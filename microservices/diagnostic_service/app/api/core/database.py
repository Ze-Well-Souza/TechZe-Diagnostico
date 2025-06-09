# -*- coding: utf-8 -*-
"""
Database Core - Configuração e modelos do banco de dados da API Core

Configuração consolidada para conexão com banco de dados usando SQLAlchemy.
"""

from typing import Generator
from sqlalchemy import create_engine, MetaData, Column, Integer, String, DateTime, Text, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Base para modelos SQLAlchemy
Base = declarative_base()

# Metadata para reflexão de tabelas
metadata = MetaData()

# Engine do banco de dados
engine = None
SessionLocal = None

def create_database_engine():
    """
    Cria o engine do banco de dados.
    
    Returns:
        Engine: Engine SQLAlchemy configurado
    """
    global engine
    
    if engine is None:
        try:
            # Usar URL de banco da configuração
            database_url = settings.database_url_computed
            
            # Configurações do engine
            engine_kwargs = {
                "pool_pre_ping": True,
                "pool_recycle": settings.DB_POOL_RECYCLE,
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_timeout": settings.DB_POOL_TIMEOUT,
                "echo": settings.DEBUG and settings.ENVIRONMENT.value == "development"
            }
            
            # Para SQLite (desenvolvimento/testes)
            if "sqlite" in database_url:
                engine_kwargs.update({
                    "poolclass": StaticPool,
                    "connect_args": {"check_same_thread": False}
                })
            
            engine = create_engine(database_url, **engine_kwargs)
            
            logger.info(f"Engine de banco de dados criado: {settings.DB_HOST}:{settings.DB_PORT}")
            
        except Exception as e:
            logger.error(f"Erro ao criar engine do banco de dados: {e}")
            raise
    
    return engine

def create_session_factory():
    """
    Cria a factory de sessões do banco de dados.
    
    Returns:
        sessionmaker: Factory de sessões configurada
    """
    global SessionLocal
    
    if SessionLocal is None:
        engine = create_database_engine()
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        logger.info("Factory de sessões criada")
    
    return SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Dependency para obter uma sessão de banco de dados.
    
    Yields:
        Session: Sessão SQLAlchemy
    """
    SessionLocal = create_session_factory()
    db = SessionLocal()
    
    try:
        yield db
    except Exception as e:
        logger.error(f"Erro na sessão do banco de dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_database():
    """
    Inicializa o banco de dados criando todas as tabelas.
    """
    try:
        engine = create_database_engine()
        
        # Criar todas as tabelas
        Base.metadata.create_all(bind=engine)
        
        logger.info("Banco de dados inicializado com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise

def health_check() -> dict:
    """
    Verifica a saúde da conexão com o banco de dados.
    
    Returns:
        dict: Status da conexão
    """
    try:
        engine = create_database_engine()
        
        # Teste de conectividade
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            result.fetchone()
        
        return {
            "status": "healthy",
            "connected": True,
            "host": settings.DB_HOST,
            "database": settings.DB_NAME,
            "message": "Conexão com banco de dados estabelecida"
        }
        
    except Exception as e:
        logger.error(f"Erro no health check do banco de dados: {e}")
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
            "message": "Falha na conexão com banco de dados"
        }

def close_database_connections():
    """
    Fecha todas as conexões do banco de dados.
    """
    global engine, SessionLocal
    
    try:
        if engine:
            engine.dispose()
            engine = None
            
        SessionLocal = None
        
        logger.info("Conexões do banco de dados fechadas")
        
    except Exception as e:
        logger.error(f"Erro ao fechar conexões do banco de dados: {e}")

# Modelos básicos para diagnósticos
class DiagnosticResult(Base):
    """
    Modelo para resultados de diagnóstico.
    """
    __tablename__ = "diagnostic_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    diagnostic_type = Column(String, index=True)
    status = Column(String, default="pending")
    results = Column(Text)  # JSON string
    created_at = Column(DateTime)
    completed_at = Column(DateTime, nullable=True)
    is_successful = Column(Boolean, default=False)

class SystemMetric(Base):
    """
    Modelo para métricas do sistema.
    """
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True)
    metric_value = Column(Float)
    unit = Column(String)
    timestamp = Column(DateTime, index=True)
    source = Column(String)