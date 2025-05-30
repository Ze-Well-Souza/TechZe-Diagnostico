import logging
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import engine

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Inicializa o banco de dados.
    
    Cria todas as tabelas definidas nos modelos.
    """
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


def create_initial_data(db: Session) -> None:
    """Cria dados iniciais no banco de dados.
    
    Args:
        db: Sessão do banco de dados
    """
    # Aqui você pode adicionar a criação de dados iniciais
    # Por exemplo, configurações padrão, usuários admin, etc.
    logger.info("Initial data created")