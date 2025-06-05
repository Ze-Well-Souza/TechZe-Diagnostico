"""
Advanced PostgreSQL Connection Pooling Configuration
Implementação de connection pooling avançado para otimização de performance
"""
import asyncio
import logging
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
import asyncpg
from asyncpg import Pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
import os
from functools import lru_cache

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Configuração avançada do banco de dados com connection pooling"""
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "")
        
        # Connection Pool Settings - Otimizado para produção
        self.min_connections = int(os.getenv("DB_MIN_CONNECTIONS", "5"))
        self.max_connections = int(os.getenv("DB_MAX_CONNECTIONS", "20"))
        self.max_queries = int(os.getenv("DB_MAX_QUERIES", "50000"))
        self.max_inactive_connection_lifetime = float(os.getenv("DB_MAX_INACTIVE_LIFETIME", "300.0"))
        
        # SQLAlchemy Pool Settings
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        self.pool_recycle = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        self.pool_pre_ping = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"

class AdvancedConnectionPool:
    """Gerenciador avançado de connection pool PostgreSQL"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self._pool: Optional[Pool] = None
        self._engine = None
        self._session_factory = None
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Inicializa o connection pool com configurações avançadas"""
        async with self._lock:
            if self._pool is None:
                try:
                    # AsyncPG Pool para operações de baixo nível
                    self._pool = await asyncpg.create_pool(
                        self.config.database_url,
                        min_size=self.config.min_connections,
                        max_size=self.config.max_connections,
                        max_queries=self.config.max_queries,
                        max_inactive_connection_lifetime=self.config.max_inactive_connection_lifetime,
                        command_timeout=60,
                        server_settings={
                            'jit': 'off',  # Desabilita JIT para consultas rápidas
                            'application_name': 'techze_diagnostic'
                        }
                    )
                    
                    # SQLAlchemy Engine para ORM
                    self._engine = create_async_engine(
                        self.config.database_url,
                        poolclass=NullPool,  # Usa nosso pool customizado
                        pool_size=self.config.pool_size,
                        max_overflow=self.config.max_overflow,
                        pool_timeout=self.config.pool_timeout,
                        pool_recycle=self.config.pool_recycle,
                        pool_pre_ping=self.config.pool_pre_ping,
                        echo=False  # Desabilita logs SQL em produção
                    )
                    
                    self._session_factory = async_sessionmaker(
                        bind=self._engine,
                        class_=AsyncSession,
                        expire_on_commit=False
                    )
                    
                    logger.info(f"Connection pool iniciado: {self.config.min_connections}-{self.config.max_connections} conexões")
                    
                except Exception as e:
                    logger.error(f"Erro ao inicializar connection pool: {e}")
                    raise
    
    async def close(self):
        """Fecha o connection pool de forma segura"""
        async with self._lock:
            if self._pool:
                await self._pool.close()
                self._pool = None
                logger.info("Connection pool fechado")
            
            if self._engine:
                await self._engine.dispose()
                self._engine = None
                logger.info("SQLAlchemy engine fechado")
    
    @asynccontextmanager
    async def get_connection(self):
        """Context manager para obter conexão do pool"""
        if not self._pool:
            await self.initialize()
        
        async with self._pool.acquire() as connection:
            try:
                yield connection
            except Exception as e:
                logger.error(f"Erro na conexão: {e}")
                raise
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Context manager para obter sessão SQLAlchemy"""
        if not self._session_factory:
            await self.initialize()
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Erro na sessão: {e}")
                raise
            finally:
                await session.close()
    
    async def execute_query(self, query: str, *args):
        """Executa query diretamente no pool"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def execute_one(self, query: str, *args):
        """Executa query e retorna um resultado"""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def get_pool_stats(self) -> dict:
        """Retorna estatísticas do connection pool"""
        if not self._pool:
            return {"status": "not_initialized"}
        
        return {
            "size": self._pool.get_size(),
            "min_size": self._pool.get_min_size(),
            "max_size": self._pool.get_max_size(),
            "free_connections": self._pool.get_idle_size(),
            "used_connections": self._pool.get_size() - self._pool.get_idle_size()
        }

# Instância global do connection pool
@lru_cache()
def get_db_config() -> DatabaseConfig:
    return DatabaseConfig()

# Pool global
connection_pool = AdvancedConnectionPool(get_db_config())

async def init_database():
    """Inicializa o banco de dados"""
    await connection_pool.initialize()

async def close_database():
    """Fecha conexões do banco de dados"""
    await connection_pool.close()

# Context managers para uso fácil
async def get_db_connection():
    """Obter conexão do pool"""
    async with connection_pool.get_connection() as conn:
        yield conn

async def get_db_session():
    """Obter sessão SQLAlchemy"""
    async with connection_pool.get_session() as session:
        yield session

# Health check do banco
async def health_check() -> bool:
    """Verifica saúde do connection pool"""
    try:
        async with connection_pool.get_connection() as conn:
            result = await conn.fetchrow("SELECT 1 as test")
            return result['test'] == 1
    except Exception as e:
        logger.error(f"Health check falhou: {e}")
        return False

# Middleware para estatísticas
async def get_connection_stats():
    """Retorna estatísticas detalhadas do pool"""
    stats = await connection_pool.get_pool_stats()
    stats.update({
        "health": await health_check(),
        "config": {
            "min_connections": get_db_config().min_connections,
            "max_connections": get_db_config().max_connections,
            "pool_size": get_db_config().pool_size,
            "max_overflow": get_db_config().max_overflow
        }
    })
    return stats 