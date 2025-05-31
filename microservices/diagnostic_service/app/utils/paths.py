
"""
Utilitários para configuração de caminhos e diretórios.
"""
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def ensure_directory_exists(path: str) -> str:
    """Garante que um diretório existe, criando-o se necessário.
    
    Args:
        path: Caminho do diretório
        
    Returns:
        Caminho do diretório criado
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ensured: {path}")
        return path
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        # Fallback para diretório temporário
        fallback_path = "/tmp"
        logger.warning(f"Using fallback directory: {fallback_path}")
        return fallback_path


def get_report_storage_path() -> str:
    """Obtém o caminho para armazenamento de relatórios.
    
    Returns:
        Caminho para armazenamento de relatórios
    """
    # Primeiro tenta usar a variável de ambiente
    storage_path = os.getenv("REPORT_STORAGE_PATH", "/tmp/reports")
    
    # Garante que o diretório existe
    return ensure_directory_exists(storage_path)


def get_temp_path() -> str:
    """Obtém o caminho temporário do sistema.
    
    Returns:
        Caminho temporário
    """
    return os.getenv("TEMP_PATH", "/tmp")
