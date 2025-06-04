from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Cria o engine do SQLAlchemy apenas se a URI estiver configurada
engine = None
if settings.SQLALCHEMY_DATABASE_URI:
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

# Cria uma fábrica de sessões apenas se o engine estiver disponível
SessionLocal = None
if engine:
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos declarativos
Base = declarative_base()


def get_db() -> Generator:
    """Fornece uma sessão de banco de dados para as operações.
    
    Yields:
        Sessão do SQLAlchemy
    """
    if not SessionLocal:
        raise RuntimeError("Database not configured. Please set SQLALCHEMY_DATABASE_URI.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()