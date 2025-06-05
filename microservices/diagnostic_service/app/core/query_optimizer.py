"""
Advanced Query Optimizer & Automated Alerts System
Sistema enterprise de otimização de queries e alertas automáticos
"""
import asyncio
import logging
import time
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import asyncpg
from asyncpg import Pool
import aioredis
import psutil
from prometheus_client import Counter, Histogram, Gauge
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import threading

logger = logging.getLogger(__name__)

# Prometheus metrics
query_duration = Histogram('query_duration_seconds', 'Query execution time', ['query_type', 'table'])
query_counter = Counter('queries_total', 'Total queries executed', ['status', 'query_type'])
slow_query_counter = Counter('slow_queries_total', 'Slow queries detected', ['table'])
active_connections = Gauge('db_active_connections', 'Active database connections')
cache_hit_ratio = Gauge('cache_hit_ratio', 'Cache hit ratio percentage')

@dataclass
class QueryStats:
    """Estatísticas de uma query"""
    query_hash: str
    query_text: str
    execution_count: int
    total_duration: float
    min_duration: float
    max_duration: float
    avg_duration: float
    last_executed: datetime
    table_names: List[str]
    query_type: str  # SELECT, INSERT, UPDATE, DELETE
    is_slow: bool = False
    error_count: int = 0

@dataclass
class AlertRule:
    """Regra de alerta"""
    name: str
    metric: str
    operator: str  # >, <, >=, <=, ==
    threshold: float
    duration: int  # seconds
    severity: str  # critical, warning, info
    enabled: bool = True
    last_triggered: Optional[datetime] = None
    cooldown: int = 300  # 5 minutes default

@dataclass
class Alert:
    """Alerta gerado"""
    rule_name: str
    severity: str
    message: str
    value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False

class QueryOptimizer:
    """Sistema avançado de otimização de queries"""
    
    def __init__(self, pool: Pool, redis_client: Optional[aioredis.Redis] = None):
        self.pool = pool
        self.redis = redis_client
        
        # Query statistics
        self.query_stats: Dict[str, QueryStats] = {}
        self.query_cache: Dict[str, Any] = {}
        self.query_history = deque(maxlen=10000)  # Last 10k queries
        
        # Performance thresholds
        self.slow_query_threshold = 1.0  # 1 second
        self.cache_ttl = 300  # 5 minutes
        self.max_cache_size = 1000
        
        # Query patterns for optimization
        self.optimization_patterns = {
            'select_star': r'SELECT \* FROM',
            'no_limit': r'SELECT .+ FROM .+ WHERE .+ ORDER BY .+ (?!LIMIT)',
            'n_plus_one': r'SELECT .+ FROM .+ WHERE .+ IN \(',
            'cartesian_join': r'FROM .+ , .+',
            'missing_index': [],  # Will be populated by analysis
        }
        
        # Background tasks
        self.running = False
        self.analysis_task = None
        self.cleanup_task = None
        
    async def initialize(self):
        """Inicializa o otimizador"""
        self.running = True
        
        # Start background tasks
        self.analysis_task = asyncio.create_task(self._analysis_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Load existing statistics
        await self._load_statistics()
        
        logger.info("Query Optimizer inicializado")
    
    async def shutdown(self):
        """Para o otimizador"""
        self.running = False
        
        if self.analysis_task:
            self.analysis_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()
        
        # Save statistics
        await self._save_statistics()
        
        logger.info("Query Optimizer finalizado")
    
    async def execute_optimized_query(
        self, 
        query: str, 
        params: tuple = (), 
        cache_key: Optional[str] = None,
        cache_ttl: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Executa query com otimizações automáticas"""
        start_time = time.time()
        query_hash = self._generate_query_hash(query)
        query_type = self._get_query_type(query)
        table_names = self._extract_table_names(query)
        
        # Check cache first
        if cache_key and self.redis:
            cached_result = await self._get_from_cache(cache_key)
            if cached_result is not None:
                cache_hit_ratio.inc()
                return cached_result
        
        # Analyze and optimize query
        optimized_query = await self._optimize_query(query, params)
        
        try:
            # Execute query
            async with self.pool.acquire() as conn:
                active_connections.inc()
                
                if query_type == 'SELECT':
                    result = await conn.fetch(optimized_query, *params)
                    result_list = [dict(row) for row in result]
                else:
                    await conn.execute(optimized_query, *params)
                    result_list = []
                
                execution_time = time.time() - start_time
                
                # Update metrics
                query_duration.labels(
                    query_type=query_type,
                    table=','.join(table_names[:3])  # Limit to first 3 tables
                ).observe(execution_time)
                
                query_counter.labels(status='success', query_type=query_type).inc()
                
                # Update statistics
                await self._update_query_stats(
                    query_hash, query, execution_time, table_names, query_type
                )
                
                # Cache result if applicable
                if cache_key and self.redis and query_type == 'SELECT':
                    await self._cache_result(
                        cache_key, result_list, cache_ttl or self.cache_ttl
                    )
                
                # Check for slow query
                if execution_time > self.slow_query_threshold:
                    slow_query_counter.labels(table=','.join(table_names[:3])).inc()
                    await self._handle_slow_query(query, execution_time, table_names)
                
                return result_list
                
        except Exception as e:
            execution_time = time.time() - start_time
            query_counter.labels(status='error', query_type=query_type).inc()
            
            # Update error statistics
            if query_hash in self.query_stats:
                self.query_stats[query_hash].error_count += 1
            
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            active_connections.dec()
    
    async def _optimize_query(self, query: str, params: tuple) -> str:
        """Aplica otimizações automáticas na query"""
        optimized = query
        
        # Remove unnecessary SELECT *
        if 'SELECT *' in optimized and 'COUNT(*)' not in optimized:
            # Suggest specific columns (would need schema analysis)
            logger.warning(f"Query usando SELECT * detectada: {query[:100]}...")
        
        # Add LIMIT if missing in paginated queries
        if ('ORDER BY' in optimized and 'LIMIT' not in optimized and 
            'SELECT' in optimized and 'UPDATE' not in optimized):
            # Could add automatic LIMIT for safety
            logger.warning(f"Query sem LIMIT detectada: {query[:100]}...")
        
        # Detect potential N+1 queries
        if 'WHERE' in optimized and 'IN (' in optimized:
            logger.warning(f"Possível N+1 query detectada: {query[:100]}...")
        
        return optimized
    
    def _generate_query_hash(self, query: str) -> str:
        """Gera hash único para a query"""
        import hashlib
        # Normalize query for hashing
        normalized = ' '.join(query.strip().split())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def _get_query_type(self, query: str) -> str:
        """Identifica o tipo da query"""
        query_upper = query.strip().upper()
        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        else:
            return 'OTHER'
    
    def _extract_table_names(self, query: str) -> List[str]:
        """Extrai nomes das tabelas da query"""
        import re
        
        # Simple table extraction (could be improved with SQL parser)
        patterns = [
            r'FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'JOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'UPDATE\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'INSERT\s+INTO\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        ]
        
        tables = set()
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            tables.update(matches)
        
        return list(tables)
    
    async def _update_query_stats(
        self, 
        query_hash: str, 
        query: str, 
        execution_time: float,
        table_names: List[str],
        query_type: str
    ):
        """Atualiza estatísticas da query"""
        now = datetime.utcnow()
        
        if query_hash in self.query_stats:
            stats = self.query_stats[query_hash]
            stats.execution_count += 1
            stats.total_duration += execution_time
            stats.min_duration = min(stats.min_duration, execution_time)
            stats.max_duration = max(stats.max_duration, execution_time)
            stats.avg_duration = stats.total_duration / stats.execution_count
            stats.last_executed = now
            stats.is_slow = execution_time > self.slow_query_threshold
        else:
            self.query_stats[query_hash] = QueryStats(
                query_hash=query_hash,
                query_text=query[:500],  # Truncate long queries
                execution_count=1,
                total_duration=execution_time,
                min_duration=execution_time,
                max_duration=execution_time,
                avg_duration=execution_time,
                last_executed=now,
                table_names=table_names,
                query_type=query_type,
                is_slow=execution_time > self.slow_query_threshold
            )
        
        # Add to history
        self.query_history.append({
            'timestamp': now,
            'query_hash': query_hash,
            'execution_time': execution_time,
            'table_names': table_names,
            'query_type': query_type
        })
    
    async def _handle_slow_query(self, query: str, execution_time: float, table_names: List[str]):
        """Processa queries lentas"""
        logger.warning(
            f"Slow query detected: {execution_time:.3f}s - "
            f"Tables: {', '.join(table_names)} - Query: {query[:100]}..."
        )
        
        # Generate optimization suggestions
        suggestions = await self._generate_optimization_suggestions(query, table_names)
        
        # Could send alert or log to special file
        slow_query_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'execution_time': execution_time,
            'query': query,
            'table_names': table_names,
            'suggestions': suggestions
        }
        
        # Log to file or send to monitoring system
        logger.warning(f"Slow query data: {json.dumps(slow_query_data, indent=2)}")
    
    async def _generate_optimization_suggestions(
        self, query: str, table_names: List[str]
    ) -> List[str]:
        """Gera sugestões de otimização"""
        suggestions = []
        
        # Check for missing indexes
        for table in table_names:
            index_suggestions = await self._check_missing_indexes(table, query)
            suggestions.extend(index_suggestions)
        
        # Check query patterns
        if 'SELECT *' in query:
            suggestions.append("Evite SELECT *, especifique apenas as colunas necessárias")
        
        if 'ORDER BY' in query and 'LIMIT' not in query:
            suggestions.append("Considere adicionar LIMIT para queries com ORDER BY")
        
        if 'WHERE' in query and 'IN (' in query:
            suggestions.append("Considere usar JOIN ao invés de WHERE IN para melhor performance")
        
        return suggestions
    
    async def _check_missing_indexes(self, table: str, query: str) -> List[str]:
        """Verifica índices ausentes"""
        suggestions = []
        
        try:
            async with self.pool.acquire() as conn:
                # Get existing indexes
                existing_indexes = await conn.fetch("""
                    SELECT indexname, indexdef 
                    FROM pg_indexes 
                    WHERE tablename = $1
                """, table)
                
                # Analyze query for potential index needs
                # This is a simplified analysis
                if 'WHERE' in query.upper():
                    suggestions.append(
                        f"Considere criar índice na tabela {table} para colunas usadas em WHERE"
                    )
                
        except Exception as e:
            logger.error(f"Error checking indexes for {table}: {e}")
        
        return suggestions
    
    async def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Obtém resultado do cache"""
        try:
            if self.redis:
                cached = await self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
        
        return None
    
    async def _cache_result(self, cache_key: str, result: Any, ttl: int):
        """Armazena resultado no cache"""
        try:
            if self.redis:
                await self.redis.setex(
                    cache_key, 
                    ttl, 
                    json.dumps(result, default=str)
                )
        except Exception as e:
            logger.warning(f"Cache write error: {e}")
    
    async def _analysis_loop(self):
        """Loop de análise em background"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                await self._perform_analysis()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Analysis loop error: {e}")
    
    async def _cleanup_loop(self):
        """Loop de limpeza em background"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Every hour
                await self._cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")
    
    async def _perform_analysis(self):
        """Realiza análise de performance"""
        # Analyze slow queries
        slow_queries = [
            stats for stats in self.query_stats.values() 
            if stats.is_slow and stats.execution_count > 5
        ]
        
        if slow_queries:
            logger.info(f"Found {len(slow_queries)} frequently slow queries")
            
            # Generate report
            report = await self._generate_performance_report(slow_queries)
            logger.info(f"Performance report: {report}")
    
    async def _cleanup_old_data(self):
        """Limpa dados antigos"""
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        # Remove old statistics
        old_queries = [
            query_hash for query_hash, stats in self.query_stats.items()
            if stats.last_executed < cutoff_date and stats.execution_count < 10
        ]
        
        for query_hash in old_queries:
            del self.query_stats[query_hash]
        
        logger.info(f"Cleaned up {len(old_queries)} old query statistics")
    
    async def _load_statistics(self):
        """Carrega estatísticas salvas"""
        try:
            if self.redis:
                data = await self.redis.get('query_optimizer:stats')
                if data:
                    stats_data = json.loads(data)
                    for query_hash, stats_dict in stats_data.items():
                        stats_dict['last_executed'] = datetime.fromisoformat(
                            stats_dict['last_executed']
                        )
                        self.query_stats[query_hash] = QueryStats(**stats_dict)
                    
                    logger.info(f"Loaded {len(self.query_stats)} query statistics")
        except Exception as e:
            logger.warning(f"Failed to load statistics: {e}")
    
    async def _save_statistics(self):
        """Salva estatísticas"""
        try:
            if self.redis:
                stats_data = {
                    query_hash: asdict(stats) 
                    for query_hash, stats in self.query_stats.items()
                }
                
                await self.redis.setex(
                    'query_optimizer:stats',
                    86400,  # 24 hours
                    json.dumps(stats_data, default=str)
                )
                
                logger.info(f"Saved {len(self.query_stats)} query statistics")
        except Exception as e:
            logger.warning(f"Failed to save statistics: {e}")
    
    async def _generate_performance_report(self, slow_queries: List[QueryStats]) -> Dict[str, Any]:
        """Gera relatório de performance"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'total_queries': len(self.query_stats),
            'slow_queries': len(slow_queries),
            'avg_execution_time': statistics.mean([
                stats.avg_duration for stats in self.query_stats.values()
            ]),
            'slowest_query': max(
                self.query_stats.values(), 
                key=lambda x: x.max_duration
            ).query_text[:100] if self.query_stats else None,
            'most_frequent_tables': self._get_most_frequent_tables()
        }
    
    def _get_most_frequent_tables(self) -> List[Tuple[str, int]]:
        """Obtém tabelas mais frequentemente consultadas"""
        table_count = defaultdict(int)
        
        for stats in self.query_stats.values():
            for table in stats.table_names:
                table_count[table] += stats.execution_count
        
        return sorted(table_count.items(), key=lambda x: x[1], reverse=True)[:10]
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """Retorna resumo das estatísticas"""
        if not self.query_stats:
            return {"message": "No statistics available"}
        
        total_queries = sum(stats.execution_count for stats in self.query_stats.values())
        slow_queries = sum(1 for stats in self.query_stats.values() if stats.is_slow)
        
        return {
            'total_unique_queries': len(self.query_stats),
            'total_executions': total_queries,
            'slow_queries': slow_queries,
            'avg_execution_time': statistics.mean([
                stats.avg_duration for stats in self.query_stats.values()
            ]),
            'most_frequent_tables': self._get_most_frequent_tables()[:5],
            'query_types': self._get_query_type_distribution()
        }
    
    def _get_query_type_distribution(self) -> Dict[str, int]:
        """Obtém distribuição de tipos de query"""
        type_count = defaultdict(int)
        
        for stats in self.query_stats.values():
            type_count[stats.query_type] += stats.execution_count
        
        return dict(type_count)


class AlertManager:
    """Sistema de alertas automáticos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules: Dict[str, AlertRule] = {}
        self.active_alerts: List[Alert] = []
        self.alert_history: deque = deque(maxlen=1000)
        self.running = False
        self.monitoring_task = None
        
        # Load default rules
        self._load_default_rules()
    
    def _load_default_rules(self):
        """Carrega regras padrão de alerta"""
        default_rules = [
            AlertRule(
                name='high_query_duration',
                metric='avg_query_duration',
                operator='>',
                threshold=2.0,  # 2 seconds
                duration=300,   # 5 minutes
                severity='warning'
            ),
            AlertRule(
                name='high_error_rate',
                metric='query_error_rate',
                operator='>',
                threshold=0.1,  # 10%
                duration=60,    # 1 minute
                severity='critical'
            ),
            AlertRule(
                name='low_cache_hit_ratio',
                metric='cache_hit_ratio',
                operator='<',
                threshold=0.8,  # 80%
                duration=600,   # 10 minutes
                severity='warning'
            ),
            AlertRule(
                name='high_connection_usage',
                metric='db_connection_usage',
                operator='>',
                threshold=0.9,  # 90%
                duration=300,   # 5 minutes
                severity='critical'
            )
        ]
        
        for rule in default_rules:
            self.rules[rule.name] = rule
    
    async def start_monitoring(self, query_optimizer: QueryOptimizer):
        """Inicia monitoramento de alertas"""
        self.running = True
        self.query_optimizer = query_optimizer
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Alert Manager iniciado")
    
    async def stop_monitoring(self):
        """Para monitoramento"""
        self.running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        logger.info("Alert Manager parado")
    
    async def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._check_all_rules()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
    
    async def _check_all_rules(self):
        """Verifica todas as regras de alerta"""
        current_metrics = await self._collect_metrics()
        
        for rule_name, rule in self.rules.items():
            if not rule.enabled:
                continue
            
            # Check cooldown
            if (rule.last_triggered and 
                datetime.utcnow() - rule.last_triggered < timedelta(seconds=rule.cooldown)):
                continue
            
            await self._check_rule(rule, current_metrics)
    
    async def _collect_metrics(self) -> Dict[str, float]:
        """Coleta métricas atuais"""
        stats = self.query_optimizer.get_statistics_summary()
        
        metrics = {
            'avg_query_duration': stats.get('avg_execution_time', 0),
            'query_error_rate': 0,  # Would calculate from error stats
            'cache_hit_ratio': 0.85,  # Would get from cache stats
            'db_connection_usage': 0.7,  # Would get from pool stats
        }
        
        # Add system metrics
        metrics.update({
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        })
        
        return metrics
    
    async def _check_rule(self, rule: AlertRule, metrics: Dict[str, float]):
        """Verifica uma regra específica"""
        if rule.metric not in metrics:
            return
        
        current_value = metrics[rule.metric]
        threshold_met = self._evaluate_condition(
            current_value, rule.operator, rule.threshold
        )
        
        if threshold_met:
            alert = Alert(
                rule_name=rule.name,
                severity=rule.severity,
                message=f"{rule.metric} is {current_value} (threshold: {rule.threshold})",
                value=current_value,
                threshold=rule.threshold,
                timestamp=datetime.utcnow()
            )
            
            await self._trigger_alert(alert, rule)
    
    def _evaluate_condition(self, value: float, operator: str, threshold: float) -> bool:
        """Avalia condição do alerta"""
        if operator == '>':
            return value > threshold
        elif operator == '<':
            return value < threshold
        elif operator == '>=':
            return value >= threshold
        elif operator == '<=':
            return value <= threshold
        elif operator == '==':
            return value == threshold
        return False
    
    async def _trigger_alert(self, alert: Alert, rule: AlertRule):
        """Dispara um alerta"""
        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        rule.last_triggered = datetime.utcnow()
        
        logger.warning(f"ALERT [{alert.severity.upper()}] {alert.rule_name}: {alert.message}")
        
        # Send notifications
        await self._send_notifications(alert)
    
    async def _send_notifications(self, alert: Alert):
        """Envia notificações"""
        # Email notification
        if self.config.get('email', {}).get('enabled'):
            await self._send_email_alert(alert)
        
        # Slack notification
        if self.config.get('slack', {}).get('enabled'):
            await self._send_slack_alert(alert)
        
        # Webhook notification
        if self.config.get('webhook', {}).get('enabled'):
            await self._send_webhook_alert(alert)
    
    async def _send_email_alert(self, alert: Alert):
        """Envia alerta por email"""
        try:
            email_config = self.config['email']
            
            msg = MIMEMultipart()
            msg['From'] = email_config['from']
            msg['To'] = email_config['to']
            msg['Subject'] = f"[TechZe] {alert.severity.upper()} Alert: {alert.rule_name}"
            
            body = f"""
            Alert Details:
            - Rule: {alert.rule_name}
            - Severity: {alert.severity}
            - Message: {alert.message}
            - Timestamp: {alert.timestamp}
            - Value: {alert.value}
            - Threshold: {alert.threshold}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_config['smtp_host'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email alert sent for {alert.rule_name}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    async def _send_slack_alert(self, alert: Alert):
        """Envia alerta para Slack"""
        try:
            slack_config = self.config['slack']
            
            payload = {
                'text': f"🚨 {alert.severity.upper()} Alert: {alert.rule_name}",
                'attachments': [{
                    'color': 'danger' if alert.severity == 'critical' else 'warning',
                    'fields': [
                        {'title': 'Message', 'value': alert.message, 'short': False},
                        {'title': 'Value', 'value': str(alert.value), 'short': True},
                        {'title': 'Threshold', 'value': str(alert.threshold), 'short': True},
                        {'title': 'Timestamp', 'value': alert.timestamp.isoformat(), 'short': False}
                    ]
                }]
            }
            
            response = requests.post(slack_config['webhook_url'], json=payload)
            response.raise_for_status()
            
            logger.info(f"Slack alert sent for {alert.rule_name}")
            
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    async def _send_webhook_alert(self, alert: Alert):
        """Envia alerta via webhook"""
        try:
            webhook_config = self.config['webhook']
            
            payload = {
                'rule_name': alert.rule_name,
                'severity': alert.severity,
                'message': alert.message,
                'value': alert.value,
                'threshold': alert.threshold,
                'timestamp': alert.timestamp.isoformat()
            }
            
            response = requests.post(webhook_config['url'], json=payload)
            response.raise_for_status()
            
            logger.info(f"Webhook alert sent for {alert.rule_name}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Retorna alertas ativos"""
        return [
            {
                'rule_name': alert.rule_name,
                'severity': alert.severity,
                'message': alert.message,
                'value': alert.value,
                'threshold': alert.threshold,
                'timestamp': alert.timestamp.isoformat(),
                'resolved': alert.resolved
            }
            for alert in self.active_alerts
            if not alert.resolved
        ]
    
    def resolve_alert(self, rule_name: str):
        """Resolve um alerta"""
        for alert in self.active_alerts:
            if alert.rule_name == rule_name and not alert.resolved:
                alert.resolved = True
                logger.info(f"Alert resolved: {rule_name}")
                break

# Global instances
query_optimizer: Optional[QueryOptimizer] = None
alert_manager: Optional[AlertManager] = None

async def initialize_optimization_system(pool: Pool, redis_client: Optional[aioredis.Redis], config: Dict[str, Any]):
    """Inicializa sistema de otimização"""
    global query_optimizer, alert_manager
    
    query_optimizer = QueryOptimizer(pool, redis_client)
    await query_optimizer.initialize()
    
    alert_manager = AlertManager(config.get('alerts', {}))
    await alert_manager.start_monitoring(query_optimizer)
    
    logger.info("Optimization system inicializado")

async def shutdown_optimization_system():
    """Finaliza sistema de otimização"""
    global query_optimizer, alert_manager
    
    if query_optimizer:
        await query_optimizer.shutdown()
    
    if alert_manager:
        await alert_manager.stop_monitoring()
    
    logger.info("Optimization system finalizado") 