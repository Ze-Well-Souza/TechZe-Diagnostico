"""Monitor de Performance para APIs

Decorador para monitorar e otimizar performance de endpoints,
resolvendo problemas críticos de lentidão identificados (309% acima da meta).
"""

import time
import asyncio
import logging
from functools import wraps
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
import json
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class PerformanceLevel(Enum):
    """Níveis de performance"""
    EXCELLENT = "excellent"  # < 100ms
    GOOD = "good"           # 100-300ms
    ACCEPTABLE = "acceptable" # 300-500ms
    SLOW = "slow"           # 500-1000ms
    CRITICAL = "critical"   # > 1000ms

@dataclass
class PerformanceMetric:
    """Métrica de performance"""
    endpoint: str
    method: str
    duration_ms: float
    timestamp: datetime
    status_code: int
    level: PerformanceLevel
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    error: Optional[str] = None

class PerformanceMonitor:
    """Monitor de performance singleton"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.metrics: deque = deque(maxlen=1000)  # Últimas 1000 métricas
            self.endpoint_stats: Dict[str, Dict] = defaultdict(lambda: {
                'count': 0,
                'total_time': 0,
                'avg_time': 0,
                'min_time': float('inf'),
                'max_time': 0,
                'slow_requests': 0,
                'error_count': 0
            })
            self.alerts: deque = deque(maxlen=100)
            self._initialized = True
    
    def get_performance_level(self, duration_ms: float) -> PerformanceLevel:
        """Determinar nível de performance baseado na duração"""
        if duration_ms < 100:
            return PerformanceLevel.EXCELLENT
        elif duration_ms < 300:
            return PerformanceLevel.GOOD
        elif duration_ms < 500:
            return PerformanceLevel.ACCEPTABLE
        elif duration_ms < 1000:
            return PerformanceLevel.SLOW
        else:
            return PerformanceLevel.CRITICAL
    
    def add_metric(self, metric: PerformanceMetric):
        """Adicionar métrica de performance"""
        self.metrics.append(metric)
        
        # Atualizar estatísticas do endpoint
        key = f"{metric.method} {metric.endpoint}"
        stats = self.endpoint_stats[key]
        
        stats['count'] += 1
        stats['total_time'] += metric.duration_ms
        stats['avg_time'] = stats['total_time'] / stats['count']
        stats['min_time'] = min(stats['min_time'], metric.duration_ms)
        stats['max_time'] = max(stats['max_time'], metric.duration_ms)
        
        if metric.duration_ms > 500:  # Meta: < 500ms
            stats['slow_requests'] += 1
        
        if metric.error:
            stats['error_count'] += 1
        
        # Gerar alertas para performance crítica
        if metric.level in [PerformanceLevel.SLOW, PerformanceLevel.CRITICAL]:
            self._generate_alert(metric)
    
    def _generate_alert(self, metric: PerformanceMetric):
        """Gerar alerta de performance"""
        alert = {
            'timestamp': metric.timestamp,
            'type': 'performance_alert',
            'level': metric.level.value,
            'endpoint': f"{metric.method} {metric.endpoint}",
            'duration_ms': metric.duration_ms,
            'message': f"Endpoint lento detectado: {metric.duration_ms:.1f}ms"
        }
        
        self.alerts.append(alert)
        logger.warning(
            f"🐌 Performance Alert: {metric.method} {metric.endpoint} "
            f"took {metric.duration_ms:.1f}ms (level: {metric.level.value})"
        )
    
    def get_stats(self, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Obter estatísticas de performance"""
        if endpoint:
            return dict(self.endpoint_stats.get(endpoint, {}))
        
        # Estatísticas gerais
        total_requests = sum(stats['count'] for stats in self.endpoint_stats.values())
        total_slow = sum(stats['slow_requests'] for stats in self.endpoint_stats.values())
        total_errors = sum(stats['error_count'] for stats in self.endpoint_stats.values())
        
        if total_requests == 0:
            return {'message': 'Nenhuma métrica disponível'}
        
        avg_response_time = sum(
            stats['avg_time'] * stats['count'] for stats in self.endpoint_stats.values()
        ) / total_requests
        
        return {
            'total_requests': total_requests,
            'average_response_time_ms': round(avg_response_time, 2),
            'slow_requests': total_slow,
            'slow_request_percentage': round((total_slow / total_requests) * 100, 2),
            'error_count': total_errors,
            'error_percentage': round((total_errors / total_requests) * 100, 2),
            'endpoints': dict(self.endpoint_stats),
            'recent_alerts': list(self.alerts)[-10:]  # Últimos 10 alertas
        }
    
    def get_slow_endpoints(self, threshold_ms: float = 500) -> List[Dict[str, Any]]:
        """Obter endpoints mais lentos"""
        slow_endpoints = []
        
        for endpoint, stats in self.endpoint_stats.items():
            if stats['avg_time'] > threshold_ms:
                slow_endpoints.append({
                    'endpoint': endpoint,
                    'avg_time_ms': round(stats['avg_time'], 2),
                    'max_time_ms': round(stats['max_time'], 2),
                    'slow_requests': stats['slow_requests'],
                    'total_requests': stats['count'],
                    'slow_percentage': round((stats['slow_requests'] / stats['count']) * 100, 2)
                })
        
        return sorted(slow_endpoints, key=lambda x: x['avg_time_ms'], reverse=True)
    
    def reset_stats(self):
        """Resetar todas as estatísticas"""
        self.metrics.clear()
        self.endpoint_stats.clear()
        self.alerts.clear()
        logger.info("📊 Performance stats reset")

# Instância global do monitor
performance_monitor = PerformanceMonitor()

def monitor_performance(
    log_slow_requests: bool = True,
    slow_threshold_ms: float = 500,
    include_memory: bool = False
):
    """Decorador para monitorar performance de funções/endpoints
    
    Args:
        log_slow_requests: Se deve logar requisições lentas
        slow_threshold_ms: Threshold para considerar requisição lenta
        include_memory: Se deve incluir métricas de memória (requer psutil)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            error = None
            status_code = 200
            
            # Tentar extrair informações da requisição
            endpoint = getattr(func, '__name__', 'unknown')
            method = 'UNKNOWN'
            
            # Se for um endpoint FastAPI, tentar extrair informações
            if hasattr(func, '__annotations__'):
                # Procurar por Request nos argumentos
                for arg in args:
                    if hasattr(arg, 'method') and hasattr(arg, 'url'):
                        method = arg.method
                        endpoint = str(arg.url.path)
                        break
            
            try:
                # Executar função
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Tentar extrair status code da resposta
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                
                return result
                
            except Exception as e:
                error = str(e)
                status_code = 500
                raise
            
            finally:
                # Calcular duração
                duration_ms = (time.time() - start_time) * 1000
                
                # Obter métricas de memória se solicitado
                memory_usage_mb = None
                if include_memory:
                    try:
                        import psutil
                        process = psutil.Process()
                        memory_usage_mb = process.memory_info().rss / 1024 / 1024
                    except ImportError:
                        pass
                
                # Criar métrica
                metric = PerformanceMetric(
                    endpoint=endpoint,
                    method=method,
                    duration_ms=duration_ms,
                    timestamp=datetime.now(),
                    status_code=status_code,
                    level=performance_monitor.get_performance_level(duration_ms),
                    memory_usage_mb=memory_usage_mb,
                    error=error
                )
                
                # Adicionar ao monitor
                performance_monitor.add_metric(metric)
                
                # Log se necessário
                if log_slow_requests and duration_ms > slow_threshold_ms:
                    logger.warning(
                        f"🐌 Slow request: {method} {endpoint} "
                        f"took {duration_ms:.1f}ms (threshold: {slow_threshold_ms}ms)"
                    )
                elif duration_ms < 100:
                    logger.debug(
                        f"⚡ Fast request: {method} {endpoint} "
                        f"took {duration_ms:.1f}ms"
                    )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Versão síncrona do wrapper
            start_time = time.time()
            error = None
            status_code = 200
            
            endpoint = getattr(func, '__name__', 'unknown')
            method = 'SYNC'
            
            try:
                result = func(*args, **kwargs)
                
                if hasattr(result, 'status_code'):
                    status_code = result.status_code
                
                return result
                
            except Exception as e:
                error = str(e)
                status_code = 500
                raise
            
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                metric = PerformanceMetric(
                    endpoint=endpoint,
                    method=method,
                    duration_ms=duration_ms,
                    timestamp=datetime.now(),
                    status_code=status_code,
                    level=performance_monitor.get_performance_level(duration_ms),
                    error=error
                )
                
                performance_monitor.add_metric(metric)
                
                if log_slow_requests and duration_ms > slow_threshold_ms:
                    logger.warning(
                        f"🐌 Slow function: {endpoint} "
                        f"took {duration_ms:.1f}ms"
                    )
        
        # Retornar wrapper apropriado
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Funções utilitárias para uso direto

def get_performance_stats() -> Dict[str, Any]:
    """Obter estatísticas de performance"""
    return performance_monitor.get_stats()

def get_slow_endpoints(threshold_ms: float = 500) -> List[Dict[str, Any]]:
    """Obter endpoints mais lentos"""
    return performance_monitor.get_slow_endpoints(threshold_ms)

def reset_performance_stats():
    """Resetar estatísticas de performance"""
    performance_monitor.reset_stats()

def log_performance_summary():
    """Logar resumo de performance"""
    stats = get_performance_stats()
    
    if 'message' in stats:
        logger.info("📊 Performance Summary: No metrics available")
        return
    
    logger.info(
        f"📊 Performance Summary: "
        f"{stats['total_requests']} requests, "
        f"avg {stats['average_response_time_ms']}ms, "
        f"{stats['slow_request_percentage']}% slow, "
        f"{stats['error_percentage']}% errors"
    )
    
    slow_endpoints = get_slow_endpoints()
    if slow_endpoints:
        logger.warning(f"🐌 {len(slow_endpoints)} slow endpoints detected:")
        for endpoint in slow_endpoints[:5]:  # Top 5
            logger.warning(
                f"   {endpoint['endpoint']}: {endpoint['avg_time_ms']}ms avg "
                f"({endpoint['slow_percentage']}% slow)"
            )

# Middleware FastAPI para monitoramento automático
class PerformanceMiddleware:
    """Middleware FastAPI para monitoramento automático de performance"""
    
    def __init__(self, app, slow_threshold_ms: float = 500):
        self.app = app
        self.slow_threshold_ms = slow_threshold_ms
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        
        # Capturar informações da requisição
        method = scope["method"]
        path = scope["path"]
        
        status_code = 200
        error = None
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            error = str(e)
            status_code = 500
            raise
        finally:
            # Registrar métrica
            duration_ms = (time.time() - start_time) * 1000
            
            metric = PerformanceMetric(
                endpoint=path,
                method=method,
                duration_ms=duration_ms,
                timestamp=datetime.now(),
                status_code=status_code,
                level=performance_monitor.get_performance_level(duration_ms),
                error=error
            )
            
            performance_monitor.add_metric(metric)

# Exemplo de uso
if __name__ == "__main__":
    # Teste do decorador
    @monitor_performance(slow_threshold_ms=100)
    async def test_endpoint():
        await asyncio.sleep(0.2)  # Simular processamento
        return {"message": "success"}
    
    async def main():
        # Executar alguns testes
        for i in range(5):
            await test_endpoint()
        
        # Mostrar estatísticas
        log_performance_summary()
        
        stats = get_performance_stats()
        print(json.dumps(stats, indent=2, default=str))
    
    asyncio.run(main())