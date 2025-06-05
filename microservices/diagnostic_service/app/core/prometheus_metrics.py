"""Configuração de métricas Prometheus para monitoramento APM"""
import time
from typing import Callable, Dict, List, Optional, Any
from functools import wraps
import logging

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Gauge, Histogram, Summary
from prometheus_client import CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.multiprocess import MultiProcessCollector

logger = logging.getLogger(__name__)

# Registro de métricas customizado
registry = CollectorRegistry()

# Métricas HTTP
HTTP_REQUEST_COUNT = Counter(
    'http_request_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'status_code'],
    registry=registry
)

HTTP_REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'Duração das requisições HTTP em segundos',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf')),
    registry=registry
)

# Métricas de banco de dados
DB_QUERY_COUNT = Counter(
    'db_query_total',
    'Total de queries executadas',
    ['operation', 'success'],
    registry=registry
)

DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Duração das queries em segundos',
    ['operation'],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, float('inf')),
    registry=registry
)

DB_CONNECTION_POOL = Gauge(
    'db_connection_pool',
    'Estatísticas do pool de conexões',
    ['state'],  # active, idle, total
    registry=registry
)

# Métricas de cache
CACHE_HIT_COUNT = Counter(
    'cache_hit_total',
    'Total de cache hits',
    ['cache_type'],
    registry=registry
)

CACHE_MISS_COUNT = Counter(
    'cache_miss_total',
    'Total de cache misses',
    ['cache_type'],
    registry=registry
)

CACHE_OPERATION_DURATION = Histogram(
    'cache_operation_duration_seconds',
    'Duração das operações de cache em segundos',
    ['operation', 'cache_type'],
    buckets=(0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, float('inf')),
    registry=registry
)

# Métricas de diagnóstico
DIAGNOSTIC_COUNT = Counter(
    'diagnostic_total',
    'Total de diagnósticos',
    ['status', 'device_type'],
    registry=registry
)

DIAGNOSTIC_PROCESSING_TIME = Histogram(
    'diagnostic_processing_time_seconds',
    'Tempo de processamento de diagnósticos em segundos',
    ['device_type', 'complexity'],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, float('inf')),
    registry=registry
)

# Métricas de IA
AI_PREDICTION_COUNT = Counter(
    'ai_prediction_total',
    'Total de predições de IA',
    ['model', 'success'],
    registry=registry
)

AI_PREDICTION_DURATION = Histogram(
    'ai_prediction_duration_seconds',
    'Duração das predições de IA em segundos',
    ['model'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, float('inf')),
    registry=registry
)

AI_CONFIDENCE_SCORE = Histogram(
    'ai_confidence_score',
    'Pontuação de confiança das predições de IA',
    ['model', 'prediction_type'],
    buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
    registry=registry
)

# Métricas de sistema
SYSTEM_RESOURCE_USAGE = Gauge(
    'system_resource_usage',
    'Uso de recursos do sistema',
    ['resource_type'],  # cpu, memory, disk
    registry=registry
)

# Métricas de connection pool avançado
ADVANCED_POOL_CONNECTIONS = Gauge(
    'advanced_pool_connections',
    'Conexões no pool avançado',
    ['node_id', 'state'],  # active, idle, total
    registry=registry
)

ADVANCED_POOL_OPERATIONS = Counter(
    'advanced_pool_operations_total',
    'Operações no pool avançado',
    ['node_id', 'operation', 'success'],  # get_connection, execute_query, etc.
    registry=registry
)

ADVANCED_POOL_LATENCY = Histogram(
    'advanced_pool_latency_seconds',
    'Latência das operações no pool avançado',
    ['node_id', 'operation'],
    buckets=(0.0001, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, float('inf')),
    registry=registry
)

ADVANCED_POOL_CIRCUIT_BREAKER = Gauge(
    'advanced_pool_circuit_breaker',
    'Estado do circuit breaker no pool avançado',
    ['node_id'],  # 0 = fechado (normal), 1 = aberto (falha)
    registry=registry
)

def setup_prometheus(app: FastAPI) -> None:
    """Configura métricas Prometheus na aplicação FastAPI"""
    
    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next) -> Response:
        # Ignorar endpoint de métricas para evitar recursão
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Extrair método e endpoint
        method = request.method
        endpoint = request.url.path
        
        # Iniciar timer
        start_time = time.time()
        
        # Processar requisição
        response = await call_next(request)
        
        # Registrar métricas
        duration = time.time() - start_time
        status_code = str(response.status_code)
        
        HTTP_REQUEST_COUNT.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
        HTTP_REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        
        return response
    
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        """Endpoint para expor métricas Prometheus"""
        return Response(content=generate_latest(registry), media_type=CONTENT_TYPE_LATEST)
    
    logger.info("Métricas Prometheus configuradas")

def track_db_query(operation: str):
    """Decorator para rastrear queries de banco de dados"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                DB_QUERY_COUNT.labels(operation=operation, success="true").inc()
                return result
            except Exception as e:
                DB_QUERY_COUNT.labels(operation=operation, success="false").inc()
                raise
            finally:
                duration = time.time() - start_time
                DB_QUERY_DURATION.labels(operation=operation).observe(duration)
        return wrapper
    return decorator

def track_cache_operation(operation: str, cache_type: str):
    """Decorator para rastrear operações de cache"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                # Registrar hit/miss baseado no resultado
                if operation == "get" and result is None:
                    CACHE_MISS_COUNT.labels(cache_type=cache_type).inc()
                elif operation == "get" and result is not None:
                    CACHE_HIT_COUNT.labels(cache_type=cache_type).inc()
                return result
            finally:
                duration = time.time() - start_time
                CACHE_OPERATION_DURATION.labels(operation=operation, cache_type=cache_type).observe(duration)
        return wrapper
    return decorator

def track_ai_prediction(model: str):
    """Decorator para rastrear predições de IA"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                AI_PREDICTION_COUNT.labels(model=model, success="true").inc()
                
                # Registrar pontuação de confiança se disponível
                if isinstance(result, dict) and "confidence" in result:
                    prediction_type = result.get("prediction_type", "unknown")
                    AI_CONFIDENCE_SCORE.labels(model=model, prediction_type=prediction_type).observe(result["confidence"])
                
                return result
            except Exception as e:
                AI_PREDICTION_COUNT.labels(model=model, success="false").inc()
                raise
            finally:
                duration = time.time() - start_time
                AI_PREDICTION_DURATION.labels(model=model).observe(duration)
        return wrapper
    return decorator

def update_pool_metrics(pool_stats: Dict[str, Any]) -> None:
    """Atualiza métricas do pool de conexões"""
    DB_CONNECTION_POOL.labels(state="active").set(pool_stats.get("active_connections", 0))
    DB_CONNECTION_POOL.labels(state="idle").set(pool_stats.get("idle_connections", 0))
    DB_CONNECTION_POOL.labels(state="total").set(pool_stats.get("total_connections", 0))

def update_advanced_pool_metrics(node_id: str, stats: Dict[str, Any]) -> None:
    """Atualiza métricas do pool de conexões avançado"""
    ADVANCED_POOL_CONNECTIONS.labels(node_id=node_id, state="active").set(stats.get("active_connections", 0))
    ADVANCED_POOL_CONNECTIONS.labels(node_id=node_id, state="idle").set(stats.get("idle_connections", 0))
    ADVANCED_POOL_CONNECTIONS.labels(node_id=node_id, state="total").set(stats.get("total_connections", 0))
    
    # Atualizar estado do circuit breaker (0 = fechado/normal, 1 = aberto/falha)
    circuit_breaker_state = 1 if stats.get("circuit_breaker_open", False) else 0
    ADVANCED_POOL_CIRCUIT_BREAKER.labels(node_id=node_id).set(circuit_breaker_state)

def update_system_metrics(metrics: Dict[str, float]) -> None:
    """Atualiza métricas de recursos do sistema"""
    for resource_type, value in metrics.items():
        SYSTEM_RESOURCE_USAGE.labels(resource_type=resource_type).set(value)

def track_diagnostic_creation(status: str, device_type: str) -> None:
    """Registra criação de diagnóstico"""
    DIAGNOSTIC_COUNT.labels(status=status, device_type=device_type).inc()

def track_diagnostic_processing(device_type: str, complexity: str, duration: float) -> None:
    """Registra tempo de processamento de diagnóstico"""
    DIAGNOSTIC_PROCESSING_TIME.labels(device_type=device_type, complexity=complexity).observe(duration)