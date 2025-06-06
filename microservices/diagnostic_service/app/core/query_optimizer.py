"""
Query Optimization System
Sistema de otimização automática de queries
"""

import asyncio
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class QueryMetrics:
    """Métricas de execução de query"""
    query_hash: str
    execution_time: float
    timestamp: datetime
    parameters: Dict[str, Any]
    result_count: int
    cached: bool = False

class QueryOptimizer:
    """Otimizador automático de queries"""
    
    def __init__(self):
        self.query_cache: Dict[str, Any] = {}
        self.metrics: List[QueryMetrics] = []
        self.slow_queries: Dict[str, int] = {}
        self.optimization_threshold = 0.5  # 500ms
        self.cache_ttl = 300  # 5 minutos
    
    async def execute_optimized_query(
        self, 
        query: str, 
        parameters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Executa query com otimização automática
        """
        start_time = time.time()
        query_hash = self._hash_query(query, parameters or {})
        
        # Verifica cache primeiro
        cached_result = self._get_cached_result(query_hash)
        if cached_result:
            execution_time = time.time() - start_time
            self._record_metrics(query_hash, execution_time, parameters or {}, 
                              len(cached_result.get('data', [])), cached=True)
            return cached_result
        
        # Executa query (simulado)
        result = await self._execute_query(query, parameters)
        execution_time = time.time() - start_time
        
        # Cache resultado se apropriado
        if self._should_cache_query(query, execution_time):
            self._cache_result(query_hash, result)
        
        # Registra métricas
        self._record_metrics(query_hash, execution_time, parameters or {}, 
                           len(result.get('data', [])))
        
        return result
    
    def _hash_query(self, query: str, parameters: Dict) -> str:
        """Gera hash único para query + parâmetros"""
        import hashlib
        content = f"{query}:{str(sorted(parameters.items()))}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_result(self, query_hash: str) -> Optional[Dict[str, Any]]:
        """Recupera resultado do cache se válido"""
        if query_hash in self.query_cache:
            cache_entry = self.query_cache[query_hash]
            if datetime.now() - cache_entry['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cache_entry['result']
            else:
                del self.query_cache[query_hash]
        return None
    
    async def _execute_query(self, query: str, parameters: Optional[Dict]) -> Dict[str, Any]:
        """Executa query real (implementação específica)"""
        # Simulação para exemplo
        await asyncio.sleep(0.1)  # Simula tempo de execução
        return {
            'data': [{'id': 1, 'name': 'Sample'}],
            'query': query,
            'parameters': parameters
        }
    
    def _should_cache_query(self, query: str, execution_time: float) -> bool:
        """Determina se query deve ser cacheada"""
        # Cache SELECT queries que demoram mais que threshold
        return ('SELECT' in query.upper() and 
                execution_time > self.optimization_threshold)
    
    def _cache_result(self, query_hash: str, result: Dict[str, Any]):
        """Armazena resultado no cache"""
        self.query_cache[query_hash] = {
            'result': result,
            'timestamp': datetime.now()
        }
    
    def _record_metrics(self, query_hash: str, execution_time: float, 
                       parameters: Dict, result_count: int, cached: bool = False):
        """Registra métricas da execução"""
        metric = QueryMetrics(
            query_hash=query_hash,
            execution_time=execution_time,
            timestamp=datetime.now(),
            parameters=parameters,
            result_count=result_count,
            cached=cached
        )
        
        self.metrics.append(metric)
        
        # Mantém apenas últimas 1000 métricas
        if len(self.metrics) > 1000:
            self.metrics.pop(0)
        
        # Identifica queries lentas
        if execution_time > self.optimization_threshold and not cached:
            self.slow_queries[query_hash] = self.slow_queries.get(query_hash, 0) + 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Gera relatório de performance das queries"""
        if not self.metrics:
            return {'message': 'Nenhuma métrica disponível'}
        
        total_queries = len(self.metrics)
        cached_queries = sum(1 for m in self.metrics if m.cached)
        avg_execution_time = sum(m.execution_time for m in self.metrics) / total_queries
        
        return {
            'total_queries': total_queries,
            'cached_queries': cached_queries,
            'cache_hit_rate': f"{(cached_queries/total_queries)*100:.2f}%",
            'avg_execution_time': f"{avg_execution_time:.3f}s",
            'slow_queries_count': len(self.slow_queries),
            'optimization_recommendations': self._get_optimization_recommendations()
        }
    
    def _get_optimization_recommendations(self) -> List[str]:
        """Gera recomendações de otimização"""
        recommendations = []
        
        if self.slow_queries:
            recommendations.append(f"Encontradas {len(self.slow_queries)} queries lentas")
        
        cache_hit_rate = 0
        if self.metrics:
            cached = sum(1 for m in self.metrics if m.cached)
            cache_hit_rate = (cached / len(self.metrics)) * 100
        
        if cache_hit_rate < 20:
            recommendations.append("Taxa de cache baixa - considere aumentar TTL")
        
        return recommendations

# Instância global do otimizador
query_optimizer = QueryOptimizer()