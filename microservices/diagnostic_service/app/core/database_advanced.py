"""
Advanced PostgreSQL Connection Pool System
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import asyncpg
from asyncpg import Pool
import psutil

logger = logging.getLogger(__name__)

@dataclass
class PoolMetrics:
    active_connections: int
    idle_connections: int
    total_connections: int
    query_count: int
    error_count: int
    avg_response_time: float
    last_health_check: datetime

class AdvancedConnectionPool:
    def __init__(self, database_url: str, min_size: int = 5, max_size: int = 20):
        self.database_url = database_url
        self.min_size = min_size
        self.max_size = max_size
        self.pool: Optional[Pool] = None
        self.metrics = PoolMetrics(
            active_connections=0,
            idle_connections=0,
            total_connections=0,
            query_count=0,
            error_count=0,
            avg_response_time=0.0,
            last_health_check=datetime.utcnow()
        )
        
    async def initialize(self):
        """Initialize the connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=self.min_size,
                max_size=self.max_size,
                command_timeout=60,
                server_settings={
                    'application_name': 'techze_diagnostic_advanced',
                    'tcp_keepalives_idle': '600',
                    'tcp_keepalives_interval': '30',
                    'tcp_keepalives_count': '3'
                }
            )
            
            # Start health check task
            asyncio.create_task(self._health_check_loop())
            logger.info("Advanced connection pool initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize pool: {e}")
            raise
    
    async def close(self):
        """Close the connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Connection pool closed")
    
    async def execute_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute query with monitoring"""
        import time
        start_time = time.time()
        
        try:
            async with self.pool.acquire() as conn:
                self.metrics.active_connections += 1
                
                result = await conn.fetch(query, *args)
                result_list = [dict(row) for row in result]
                
                # Update metrics
                execution_time = time.time() - start_time
                self.metrics.query_count += 1
                self._update_avg_response_time(execution_time)
                
                return result_list
                
        except Exception as e:
            self.metrics.error_count += 1
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            self.metrics.active_connections -= 1
    
    def _update_avg_response_time(self, execution_time: float):
        """Update average response time"""
        current_avg = self.metrics.avg_response_time
        count = self.metrics.query_count
        self.metrics.avg_response_time = (
            (current_avg * (count - 1) + execution_time) / count
        )
    
    async def _health_check_loop(self):
        """Background health check"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self._perform_health_check()
            except Exception as e:
                logger.error(f"Health check error: {e}")
    
    async def _perform_health_check(self):
        """Perform health check"""
        if self.pool:
            try:
                async with self.pool.acquire() as conn:
                    await conn.fetchrow("SELECT 1")
                
                # Update metrics
                self.metrics.total_connections = self.pool.get_size()
                self.metrics.idle_connections = self.pool.get_idle_size()
                self.metrics.last_health_check = datetime.utcnow()
                
            except Exception as e:
                logger.warning(f"Health check failed: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        return {
            "total_connections": self.metrics.total_connections,
            "active_connections": self.metrics.active_connections,
            "idle_connections": self.metrics.idle_connections,
            "query_count": self.metrics.query_count,
            "error_count": self.metrics.error_count,
            "avg_response_time": self.metrics.avg_response_time,
            "last_health_check": self.metrics.last_health_check.isoformat(),
            "system_memory": psutil.virtual_memory().percent,
            "system_cpu": psutil.cpu_percent()
        }

# Global instance
advanced_pool: Optional[AdvancedConnectionPool] = None

async def get_advanced_pool() -> AdvancedConnectionPool:
    """Get the global advanced pool instance"""
    if not advanced_pool:
        raise Exception("Advanced pool not initialized")
    return advanced_pool

async def initialize_advanced_pool(database_url: str):
    """Initialize the global advanced pool"""
    global advanced_pool
    advanced_pool = AdvancedConnectionPool(database_url)
    await advanced_pool.initialize() 