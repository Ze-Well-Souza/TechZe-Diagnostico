"""Integração do connection pooling avançado com métricas Prometheus"""

import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Callable
from functools import wraps

from .prometheus_metrics import (
    ADVANCED_POOL_CONNECTIONS,
    ADVANCED_POOL_OPERATIONS,
    ADVANCED_POOL_LATENCY,
    ADVANCED_POOL_CIRCUIT_BREAKER,
    update_advanced_pool_metrics
)

logger = logging.getLogger(__name__)

class MetricsEnabledConnectionPool:
    """Wrapper para adicionar métricas ao AdvancedConnectionPool"""
    
    def __init__(self, pool, node_id: str):
        """Inicializa o wrapper de métricas para o pool
        
        Args:
            pool: Instância do AdvancedConnectionPool
            node_id: Identificador do nó de banco de dados
        """
        self._pool = pool
        self.node_id = node_id
        self._last_metrics_update = 0
        self._metrics_update_interval = 5  # segundos
        
        # Inicializar métricas
        self._update_metrics()
    
    def _update_metrics(self) -> None:
        """Atualiza métricas do pool"""
        current_time = time.time()
        
        # Limitar frequência de atualização
        if current_time - self._last_metrics_update < self._metrics_update_interval:
            return
            
        try:
            stats = self._pool.get_stats()
            
            # Atualizar métricas do Prometheus
            update_advanced_pool_metrics(self.node_id, {
                "active_connections": stats.get("active_connections", 0),
                "idle_connections": stats.get("idle_connections", 0),
                "total_connections": stats.get("total_connections", 0),
                "circuit_breaker_open": stats.get("circuit_breaker_open", False)
            })
            
            self._last_metrics_update = current_time
        except Exception as e:
            logger.error(f"Erro ao atualizar métricas do pool {self.node_id}: {str(e)}")
    
    async def get_connection(self, *args, **kwargs):
        """Obtém uma conexão do pool com métricas"""
        start_time = time.time()
        success = False
        
        try:
            connection = await self._pool.get_connection(*args, **kwargs)
            success = True
            return connection
        finally:
            duration = time.time() - start_time
            ADVANCED_POOL_OPERATIONS.labels(
                node_id=self.node_id,
                operation="get_connection",
                success="true" if success else "false"
            ).inc()
            ADVANCED_POOL_LATENCY.labels(
                node_id=self.node_id,
                operation="get_connection"
            ).observe(duration)
            self._update_metrics()
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None, *args, **kwargs):
        """Executa uma query com métricas"""
        start_time = time.time()
        success = False
        
        try:
            result = await self._pool.execute_query(query, params, *args, **kwargs)
            success = True
            return result
        finally:
            duration = time.time() - start_time
            ADVANCED_POOL_OPERATIONS.labels(
                node_id=self.node_id,
                operation="execute_query",
                success="true" if success else "false"
            ).inc()
            ADVANCED_POOL_LATENCY.labels(
                node_id=self.node_id,
                operation="execute_query"
            ).observe(duration)
            self._update_metrics()
    
    async def execute_many(self, query: str, params_list: List[Dict[str, Any]], *args, **kwargs):
        """Executa múltiplas queries com métricas"""
        start_time = time.time()
        success = False
        
        try:
            result = await self._pool.execute_many(query, params_list, *args, **kwargs)
            success = True
            return result
        finally:
            duration = time.time() - start_time
            ADVANCED_POOL_OPERATIONS.labels(
                node_id=self.node_id,
                operation="execute_many",
                success="true" if success else "false"
            ).inc()
            ADVANCED_POOL_LATENCY.labels(
                node_id=self.node_id,
                operation="execute_many"
            ).observe(duration)
            self._update_metrics()
    
    async def begin_transaction(self, *args, **kwargs):
        """Inicia uma transação com métricas"""
        start_time = time.time()
        success = False
        
        try:
            transaction = await self._pool.begin_transaction(*args, **kwargs)
            success = True
            return MetricsEnabledTransaction(transaction, self.node_id)
        finally:
            duration = time.time() - start_time
            ADVANCED_POOL_OPERATIONS.labels(
                node_id=self.node_id,
                operation="begin_transaction",
                success="true" if success else "false"
            ).inc()
            ADVANCED_POOL_LATENCY.labels(
                node_id=self.node_id,
                operation="begin_transaction"
            ).observe(duration)
            self._update_metrics()
    
    async def health_check(self, *args, **kwargs):
        """Executa health check com métricas"""
        start_time = time.time()
        success = False
        
        try:
            result = await self._pool.health_check(*args, **kwargs)
            success = True
            return result
        finally:
            duration = time.time() - start_time
            ADVANCED_POOL_OPERATIONS.labels(
                node_id=self.node_id,
                operation="health_check",
                success="true" if success else "false"
            ).inc()
            ADVANCED_POOL_LATENCY.labels(
                node_id=self.node_id,
                operation="health_check"
            ).observe(duration)
            self._update_metrics()
    
    def get_stats(self, *args, **kwargs):
        """Obtém estatísticas do pool"""
        stats = self._pool.get_stats(*args, **kwargs)
        self._update_metrics()
        return stats
    
    # Delegar outros métodos ao pool subjacente
    def __getattr__(self, name):
        return getattr(self._pool, name)


class MetricsEnabledTransaction:
    """Wrapper para adicionar métricas a transações do banco de dados"""
    
    def __init__(self, transaction, node_id: str):
        """Inicializa o wrapper de métricas para a transação
        
        Args:
            transaction: Objeto de transação do banco de dados
            node_id: Identificador do nó de banco de dados
        """
        self._transaction = transaction
        self.node_id = node_id
    
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None, *args, **kwargs):
        """Executa uma query na transação com métricas"""
        start_time = time.time()
        success = False
        
        try:
            result = await self._transaction.execute(query, params, *args, **kwargs)
            success = True
            return result
        finally:
            duration = time.time() - start_time
            ADVANCED_POOL_OPERATIONS.labels(
                node_id=self.node_id,
                operation="transaction_execute",
                success="true" if success else "false"
            ).inc()
            ADVANCED_POOL_LATENCY.labels(
                node_id=self.node_id,
                operation="transaction_execute"
            ).observe(duration)
    
    async def commit(self, *args, **kwargs):
        """Commit da transação com métricas"""
        start_time = time.time()
        success = False
        
        try:
            result = await self._transaction.commit(*args, **kwargs)
            success = True
            return result
        finally:
            duration = time.time() - start_time
            ADVANCED_POOL_OPERATIONS.labels(
                node_id=self.node_id,
                operation="transaction_commit",
                success="true" if success else "false"
            ).inc()
            ADVANCED_POOL_LATENCY.labels(
                node_id=self.node_id,
                operation="transaction_commit"
            ).observe(duration)
    
    async def rollback(self, *args, **kwargs):
        """Rollback da transação com métricas"""
        start_time = time.time()
        success = False
        
        try:
            result = await self._transaction.rollback(*args, **kwargs)
            success = True
            return result
        finally:
            duration = time.time() - start_time
            ADVANCED_POOL_OPERATIONS.labels(
                node_id=self.node_id,
                operation="transaction_rollback",
                success="true" if success else "false"
            ).inc()
            ADVANCED_POOL_LATENCY.labels(
                node_id=self.node_id,
                operation="transaction_rollback"
            ).observe(duration)
    
    # Delegar outros métodos à transação subjacente
    def __getattr__(self, name):
        return getattr(self._transaction, name)


def create_metrics_enabled_pool(pool_factory, node_id: str, *args, **kwargs):
    """Cria um pool com métricas habilitadas
    
    Args:
        pool_factory: Função factory para criar o pool original
        node_id: Identificador do nó de banco de dados
        *args, **kwargs: Argumentos para passar para a factory
        
    Returns:
        MetricsEnabledConnectionPool: Pool com métricas habilitadas
    """
    pool = pool_factory(*args, **kwargs)
    return MetricsEnabledConnectionPool(pool, node_id)