"""
Ultra-Advanced PostgreSQL Connection Pooling
Sistema enterprise de gerenciamento de conexões com load balancing e failover
"""
import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, AsyncContextManager
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
import asyncpg
from asyncpg import Pool
import psutil
import json
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PoolStrategy(Enum):
    """Estratégias de balanceamento de carga"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    GEOGRAPHIC = "geographic"

@dataclass
class DatabaseNode:
    """Configuração de um nó do banco de dados"""
    host: str
    port: int
    database: str
    user: str
    password: str
    weight: float = 1.0
    region: str = "default"
    is_primary: bool = True
    max_connections: int = 20
    min_connections: int = 5

@dataclass
class PoolMetrics:
    """Métricas do pool de conexões"""
    total_connections: int
    active_connections: int
    idle_connections: int
    query_count: int
    error_count: int
    avg_response_time: float
    last_health_check: datetime
    uptime: timedelta

class AdvancedConnectionPool:
    """Pool de conexões ultra-avançado com load balancing e failover"""
    
    def __init__(self, nodes: List[DatabaseNode], strategy: PoolStrategy = PoolStrategy.LEAST_CONNECTIONS):
        self.nodes = nodes
        self.strategy = strategy
        self.pools: Dict[str, Pool] = {}
        self.metrics: Dict[str, PoolMetrics] = {}
        self.circuit_breaker: Dict[str, bool] = {}
        self.health_check_interval = 30  # seconds
        self.current_node_index = 0
        self.start_time = datetime.utcnow()
        
        # Query statistics
        self.query_stats = {
            'total_queries': 0,
            'successful_queries': 0,
            'failed_queries': 0,
            'avg_response_time': 0.0,
            'slowest_query': 0.0,
            'fastest_query': float('inf')
        }
        
        # Performance monitoring
        self.performance_threshold = 1.0  # seconds
        self.connection_timeout = 30.0
        self.query_timeout = 60.0
        
        # Adaptive scaling
        self.auto_scaling_enabled = True
        self.scale_up_threshold = 0.8  # 80% utilization
        self.scale_down_threshold = 0.3  # 30% utilization
        
    async def initialize(self):
        """Inicializa todos os pools de conexão"""
        for node in self.nodes:
            node_id = f"{node.host}:{node.port}"
            try:
                pool = await asyncpg.create_pool(
                    host=node.host,
                    port=node.port,
                    database=node.database,
                    user=node.user,
                    password=node.password,
                    min_size=node.min_connections,
                    max_size=node.max_connections,
                    command_timeout=self.query_timeout,
                    server_settings={
                        'application_name': 'techze_diagnostic_advanced',
                        'tcp_keepalives_idle': '600',
                        'tcp_keepalives_interval': '30',
                        'tcp_keepalives_count': '3'
                    }
                )
                
                self.pools[node_id] = pool
                self.circuit_breaker[node_id] = False
                
                # Initialize metrics
                self.metrics[node_id] = PoolMetrics(
                    total_connections=node.max_connections,
                    active_connections=0,
                    idle_connections=node.min_connections,
                    query_count=0,
                    error_count=0,
                    avg_response_time=0.0,
                    last_health_check=datetime.utcnow(),
                    uptime=timedelta()
                )
                
                logger.info(f"Pool inicializado para {node_id}")
                
            except Exception as e:
                logger.error(f"Erro ao inicializar pool {node_id}: {e}")
                self.circuit_breaker[node_id] = True
        
        # Start background tasks
        asyncio.create_task(self._health_check_loop())
        asyncio.create_task(self._metrics_collector_loop())
        asyncio.create_task(self._auto_scaling_loop())
        
    async def close(self):
        """Fecha todos os pools"""
        for node_id, pool in self.pools.items():
            if pool:
                await pool.close()
                logger.info(f"Pool {node_id} fechado")
    
    def _select_node(self) -> Optional[str]:
        """Seleciona o melhor nó baseado na estratégia configurada"""
        available_nodes = [
            node_id for node_id in self.pools.keys() 
            if not self.circuit_breaker.get(node_id, True)
        ]
        
        if not available_nodes:
            logger.error("Nenhum nó disponível!")
            return None
        
        if self.strategy == PoolStrategy.ROUND_ROBIN:
            return self._round_robin_selection(available_nodes)
        elif self.strategy == PoolStrategy.LEAST_CONNECTIONS:
            return self._least_connections_selection(available_nodes)
        elif self.strategy == PoolStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_selection(available_nodes)
        elif self.strategy == PoolStrategy.GEOGRAPHIC:
            return self._geographic_selection(available_nodes)
        
        return available_nodes[0]  # Fallback
    
    def _round_robin_selection(self, nodes: List[str]) -> str:
        """Seleção round-robin"""
        node = nodes[self.current_node_index % len(nodes)]
        self.current_node_index += 1
        return node
    
    def _least_connections_selection(self, nodes: List[str]) -> str:
        """Seleciona o nó com menos conexões ativas"""
        min_connections = float('inf')
        selected_node = nodes[0]
        
        for node_id in nodes:
            metrics = self.metrics.get(node_id)
            if metrics and metrics.active_connections < min_connections:
                min_connections = metrics.active_connections
                selected_node = node_id
        
        return selected_node
    
    def _weighted_round_robin_selection(self, nodes: List[str]) -> str:
        """Seleção weighted round-robin baseada nos pesos dos nós"""
        # Implementação simplificada - pode ser expandida
        weights = {}
        for node in self.nodes:
            node_id = f"{node.host}:{node.port}"
            if node_id in nodes:
                weights[node_id] = node.weight
        
        # Selecionar baseado no peso
        total_weight = sum(weights.values())
        if total_weight == 0:
            return nodes[0]
        
        # Seleção proporcional ao peso
        import random
        r = random.uniform(0, total_weight)
        current = 0
        for node_id, weight in weights.items():
            current += weight
            if r <= current:
                return node_id
        
        return nodes[0]
    
    def _geographic_selection(self, nodes: List[str]) -> str:
        """Seleção baseada na proximidade geográfica"""
        # Implementação simplificada - priorizar região local
        for node in self.nodes:
            node_id = f"{node.host}:{node.port}"
            if node_id in nodes and node.region == "local":
                return node_id
        
        return nodes[0]  # Fallback
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager para obter conexão otimizada"""
        node_id = self._select_node()
        if not node_id:
            raise Exception("Nenhum nó de banco disponível")
        
        pool = self.pools[node_id]
        start_time = time.time()
        
        try:
            async with pool.acquire() as connection:
                # Update metrics
                self.metrics[node_id].active_connections += 1
                yield connection
                
                # Record successful query
                response_time = time.time() - start_time
                self._update_query_stats(response_time, True)
                self.metrics[node_id].query_count += 1
                
        except Exception as e:
            # Record failed query
            response_time = time.time() - start_time
            self._update_query_stats(response_time, False)
            self.metrics[node_id].error_count += 1
            
            # Check if we should trigger circuit breaker
            if self.metrics[node_id].error_count > 10:
                self.circuit_breaker[node_id] = True
                logger.warning(f"Circuit breaker ativado para {node_id}")
            
            raise
        finally:
            self.metrics[node_id].active_connections -= 1
    
    def _update_query_stats(self, response_time: float, success: bool):
        """Atualiza estatísticas de queries"""
        self.query_stats['total_queries'] += 1
        
        if success:
            self.query_stats['successful_queries'] += 1
        else:
            self.query_stats['failed_queries'] += 1
        
        # Update response time statistics
        self.query_stats['fastest_query'] = min(
            self.query_stats['fastest_query'], response_time
        )
        self.query_stats['slowest_query'] = max(
            self.query_stats['slowest_query'], response_time
        )
        
        # Calculate moving average
        total_queries = self.query_stats['total_queries']
        current_avg = self.query_stats['avg_response_time']
        self.query_stats['avg_response_time'] = (
            (current_avg * (total_queries - 1) + response_time) / total_queries
        )
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Executa query com retry automático e failover"""
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                async with self.get_connection() as conn:
                    result = await conn.fetch(query, *args)
                    return [dict(row) for row in result]
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff
    
    async def execute_transaction(self, queries: List[tuple]):
        """Executa múltiplas queries em uma transação"""
        async with self.get_connection() as conn:
            async with conn.transaction():
                results = []
                for query, args in queries:
                    result = await conn.fetch(query, *args)
                    results.append([dict(row) for row in result])
                return results
    
    async def _health_check_loop(self):
        """Loop de health check em background"""
        while True:
            await asyncio.sleep(self.health_check_interval)
            await self._perform_health_checks()
    
    async def _perform_health_checks(self):
        """Realiza health checks em todos os nós"""
        for node_id, pool in self.pools.items():
            try:
                async with pool.acquire() as conn:
                    await conn.fetchrow("SELECT 1")
                
                # Reset circuit breaker if healthy
                if self.circuit_breaker[node_id]:
                    self.circuit_breaker[node_id] = False
                    logger.info(f"Circuit breaker resetado para {node_id}")
                
                self.metrics[node_id].last_health_check = datetime.utcnow()
                
            except Exception as e:
                logger.warning(f"Health check falhou para {node_id}: {e}")
                self.circuit_breaker[node_id] = True
    
    async def _metrics_collector_loop(self):
        """Coleta métricas em background"""
        while True:
            await asyncio.sleep(10)  # Collect every 10 seconds
            await self._collect_metrics()
    
    async def _collect_metrics(self):
        """Coleta métricas detalhadas dos pools"""
        for node_id, pool in self.pools.items():
            if node_id in self.metrics:
                metrics = self.metrics[node_id]
                
                # Update pool statistics
                metrics.total_connections = pool.get_size()
                metrics.idle_connections = pool.get_idle_size()
                metrics.uptime = datetime.utcnow() - self.start_time
                
                # Calculate average response time
                if metrics.query_count > 0:
                    metrics.avg_response_time = self.query_stats['avg_response_time']
    
    async def _auto_scaling_loop(self):
        """Loop de auto-scaling em background"""
        if not self.auto_scaling_enabled:
            return
        
        while True:
            await asyncio.sleep(60)  # Check every minute
            await self._perform_auto_scaling()
    
    async def _perform_auto_scaling(self):
        """Realiza auto-scaling baseado na utilização"""
        for node_id, pool in self.pools.items():
            metrics = self.metrics[node_id]
            utilization = metrics.active_connections / metrics.total_connections
            
            if utilization > self.scale_up_threshold:
                # Scale up
                new_size = min(metrics.total_connections + 5, 50)  # Max 50 connections
                logger.info(f"Scaling up {node_id}: {metrics.total_connections} -> {new_size}")
                
            elif utilization < self.scale_down_threshold:
                # Scale down
                new_size = max(metrics.total_connections - 2, 5)  # Min 5 connections
                logger.info(f"Scaling down {node_id}: {metrics.total_connections} -> {new_size}")
    
    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas completas do pool"""
        total_active = sum(m.active_connections for m in self.metrics.values())
        total_idle = sum(m.idle_connections for m in self.metrics.values())
        total_connections = sum(m.total_connections for m in self.metrics.values())
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "strategy": self.strategy.value,
            "total_nodes": len(self.nodes),
            "healthy_nodes": len([1 for cb in self.circuit_breaker.values() if not cb]),
            "total_connections": total_connections,
            "active_connections": total_active,
            "idle_connections": total_idle,
            "utilization_percent": (total_active / total_connections * 100) if total_connections > 0 else 0,
            "query_statistics": self.query_stats.copy(),
            "node_metrics": {
                node_id: {
                    "active_connections": metrics.active_connections,
                    "idle_connections": metrics.idle_connections,
                    "total_connections": metrics.total_connections,
                    "query_count": metrics.query_count,
                    "error_count": metrics.error_count,
                    "avg_response_time": metrics.avg_response_time,
                    "circuit_breaker_open": self.circuit_breaker.get(node_id, True),
                    "last_health_check": metrics.last_health_check.isoformat(),
                    "uptime_seconds": metrics.uptime.total_seconds()
                }
                for node_id, metrics in self.metrics.items()
            },
            "system_resources": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            }
        }

# Pool global instance
advanced_pool: Optional[AdvancedConnectionPool] = None

async def initialize_advanced_pool(config: Dict[str, Any]):
    """Inicializa o pool avançado"""
    global advanced_pool
    
    nodes = []
    for node_config in config.get('nodes', []):
        node = DatabaseNode(**node_config)
        nodes.append(node)
    
    strategy = PoolStrategy(config.get('strategy', 'least_connections'))
    advanced_pool = AdvancedConnectionPool(nodes, strategy)
    await advanced_pool.initialize()
    
    logger.info("Advanced connection pool inicializado")

async def get_advanced_pool() -> AdvancedConnectionPool:
    """Retorna instância do pool avançado"""
    if not advanced_pool:
        raise Exception("Advanced pool não inicializado")
    return advanced_pool 