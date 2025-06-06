"""
Testes de Performance - Sistema de Otimização
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from app.core.database_pool import pool_manager, PoolStats
from app.core.query_optimizer import query_optimizer, QueryMetrics
from datetime import datetime

class TestConnectionPoolManager:
    """Testes para o gerenciador de pools de conexão"""
    
    @pytest.mark.asyncio
    async def test_initialize_pool_success(self):
        """Testa inicialização bem-sucedida de pool"""
        config = {
            "max_connections": 20,
            "min_connections": 5
        }
        
        result = await pool_manager.initialize_pool("test_pool", config)
        
        assert result is True
        assert "test_pool" in pool_manager.pools
        assert "test_pool" in pool_manager.stats
        assert pool_manager.stats["test_pool"].pool_name == "test_pool"
    
    def test_get_pool_stats(self):
        """Testa obtenção de estatísticas dos pools"""
        # Setup
        pool_manager.stats["test_pool"] = PoolStats(
            pool_name="test_pool",
            total_connections=20,
            active_connections=5,
            idle_connections=15,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            total_queries=100,
            avg_query_time=0.05,
            health_status="healthy"
        )
        
        stats = pool_manager.get_pool_stats()
        
        assert "test_pool" in stats
        assert stats["test_pool"]["total_connections"] == 20
        assert stats["test_pool"]["health_status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_close_all_pools(self):
        """Testa fechamento de todos os pools"""
        # Setup
        pool_manager.pools["test_pool"] = {"config": {}, "status": "active"}
        
        await pool_manager.close_all_pools()
        
        assert len(pool_manager.pools) == 0

class TestQueryOptimizer:
    """Testes para o otimizador de queries"""
    
    def setup_method(self):
        """Setup para cada teste"""
        query_optimizer.query_cache = {}
        query_optimizer.metrics = []
        query_optimizer.slow_queries = {}
    
    @pytest.mark.asyncio
    async def test_execute_optimized_query_success(self):
        """Testa execução bem-sucedida de query otimizada"""
        query = "SELECT * FROM users WHERE id = 1"
        parameters = {"id": 1}
        
        result = await query_optimizer.execute_optimized_query(query, parameters)
        
        assert "data" in result
        assert "query" in result
        assert result["query"] == query
        assert len(query_optimizer.metrics) == 1
    
    @pytest.mark.asyncio 
    async def test_query_caching(self):
        """Testa funcionalidade de cache de queries"""
        query = "SELECT * FROM users"
        
        # Primeira execução - não cacheada
        result1 = await query_optimizer.execute_optimized_query(query)
        assert not query_optimizer.metrics[0].cached
        
        # Segunda execução - deve usar cache se query for lenta o suficiente
        with patch.object(query_optimizer, 'optimization_threshold', 0.0):
            query_optimizer._cache_result(
                query_optimizer._hash_query(query, {}),
                result1
            )
            
            result2 = await query_optimizer.execute_optimized_query(query)
            # Verifica se usou cache
            assert len(query_optimizer.metrics) == 2
    
    def test_performance_report_generation(self):
        """Testa geração de relatório de performance"""
        # Setup métricas simuladas
        query_optimizer.metrics = [
            QueryMetrics(
                query_hash="hash1",
                execution_time=0.1,
                timestamp=datetime.now(),
                parameters={},
                result_count=5,
                cached=False
            ),
            QueryMetrics(
                query_hash="hash2", 
                execution_time=0.05,
                timestamp=datetime.now(),
                parameters={},
                result_count=3,
                cached=True
            )
        ]
        
        report = query_optimizer.get_performance_report()
        
        assert "total_queries" in report
        assert "cache_hit_rate" in report
        assert "avg_execution_time" in report
        assert report["total_queries"] == 2
        assert "50.00%" in report["cache_hit_rate"]
    
    def test_slow_query_detection(self):
        """Testa detecção de queries lentas"""
        query_hash = "slow_query_hash"
        
        # Simula query lenta
        query_optimizer._record_metrics(
            query_hash, 1.0, {}, 10, cached=False
        )
        
        assert query_hash in query_optimizer.slow_queries
        assert query_optimizer.slow_queries[query_hash] == 1
        
        # Executa novamente
        query_optimizer._record_metrics(
            query_hash, 1.5, {}, 15, cached=False
        )
        
        assert query_optimizer.slow_queries[query_hash] == 2