#!/usr/bin/env python3
"""
Script simples para iniciar o servidor TechZe
"""

import uvicorn
import logging
from app.main import app

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def start_server():
    """Inicia o servidor FastAPI"""
    logger.info("🚀 INICIANDO SERVIDOR TECHZE DIAGNÓSTICO")
    logger.info("=" * 50)
    logger.info(f"📱 App: {app.title}")
    logger.info(f"🔗 URL: http://localhost:8000")
    logger.info(f"📚 Docs: http://localhost:8000/docs")
    logger.info(f"🔄 API Core: http://localhost:8000/api/core/")
    logger.info("=" * 50)
    
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            reload=False,  # Desabilitando reload para teste
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"💥 Erro ao iniciar servidor: {e}")

if __name__ == "__main__":
    start_server() 