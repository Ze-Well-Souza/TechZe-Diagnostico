import logging
import sys
from typing import Any, Dict, List, Optional

from loguru import logger
from pydantic_settings import BaseSettings

from app.core.config import settings


class LoggingSettings(BaseSettings):
    LOGGING_LEVEL: str = settings.LOG_LEVEL
    LOGGING_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    JSON_LOGS: bool = False


class InterceptHandler(logging.Handler):
    """Manipulador para interceptar logs padrão do Python e redirecioná-los para o Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Obtém o logger correspondente do loguru
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


def setup_logging(
    logging_settings: Optional[LoggingSettings] = None,
) -> None:
    """Configura o sistema de logging usando Loguru.
    
    Args:
        logging_settings: Configurações de logging
    """
    if logging_settings is None:
        logging_settings = LoggingSettings()

    # Configura o formato de saída
    logging_config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "format": logging_settings.LOGGING_FORMAT,
                "level": logging_settings.LOGGING_LEVEL,
                "serialize": logging_settings.JSON_LOGS,
            },
        ],
    }

    # Configura o Loguru
    logger.configure(**logging_config)

    # Intercepta os logs padrão do Python
    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    # Configura os loggers específicos
    loggers = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "sqlalchemy",
        "alembic",
    ]
    for logger_name in loggers:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]

    # Log de inicialização
    logger.info("Logging system initialized")


def get_logger(name: str) -> logger:
    """Obtém um logger configurado para um módulo específico.
    
    Args:
        name: Nome do módulo
        
    Returns:
        Logger configurado
    """
    return logger.bind(name=name)