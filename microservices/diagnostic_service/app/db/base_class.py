import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy.orm import Mapped, mapped_column


@as_declarative()
class Base:
    """Classe base para todos os modelos do SQLAlchemy.
    
    Fornece:
    - Geração automática de nome de tabela
    - Coluna ID UUID
    - Colunas de timestamp para criação e atualização
    - Método de representação string
    """
    id: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
    __name__: str
    
    # Gera o nome da tabela automaticamente
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
    
    # Coluna ID comum para todas as tabelas
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Colunas de timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self) -> str:
        """Representação string do objeto."""
        return f"<{self.__class__.__name__}(id={self.id})>"