#!/usr/bin/env python3
"""
Script para iniciar o servidor FastAPI em modo desenvolvimento
"""

import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def start_server():
    """Inicia o servidor em modo desenvolvimento"""
    try:
        logger.info("🚀 Iniciando servidor FastAPI...")
        
        # Teste de imports críticos
        logger.info("🔍 Testando imports...")
        
        from app.core.config import get_settings
        settings = get_settings()
        logger.info("✅ Configurações carregadas")
        
        from app.main import app
        logger.info("✅ Aplicação FastAPI carregada")
        
        # Iniciar o servidor
        import uvicorn
        
        logger.info(f"🌐 Servidor iniciando em http://{settings.HOST}:{settings.PORT}")
        logger.info(f"📖 Documentação em: http://{settings.HOST}:{settings.PORT}/docs")
        
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=True,
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        logger.error(f"❌ Erro de import: {e}")
        logger.error("💡 Verifique se todas as dependências estão instaladas")
        return False
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        return False

if __name__ == "__main__":
    start_server() 