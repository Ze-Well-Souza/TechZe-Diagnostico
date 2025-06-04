#!/usr/bin/env python3
"""
Script de inicialização segura do TechZe Diagnostic Service
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_python_version():
    """Verifica se a versão do Python é compatível"""
    if sys.version_info < (3, 8):
        logger.error("❌ Python 3.8+ é necessário")
        return False
    
    logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True


def setup_environment():
    """Configura o ambiente"""
    logger.info("🔧 Configurando ambiente...")
    
    # Variáveis de ambiente padrão
    env_vars = {
        "PYTHONPATH": str(Path.cwd()),
        "RATE_LIMIT_ENABLED": "true",
        "PROMETHEUS_ENABLED": "true",
        "AUDIT_LOG_TO_CONSOLE": "true",
        "LOG_LEVEL": "INFO"
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            logger.info(f"✅ {key} = {value}")
    
    return True


def install_minimal_deps():
    """Instala dependências mínimas necessárias"""
    logger.info("📦 Instalando dependências mínimas...")
    
    minimal_deps = [
        "fastapi",
        "uvicorn[standard]",
        "pydantic-settings",
        "python-multipart"
    ]
    
    for dep in minimal_deps:
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], check=True, capture_output=True)
            logger.info(f"✅ {dep} instalado")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Erro ao instalar {dep}: {e}")
            return False
    
    return True


def test_basic_import():
    """Testa se a aplicação pode ser importada"""
    logger.info("🧪 Testando importação básica...")
    
    try:
        from app.main import app
        logger.info("✅ Aplicação importada com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao importar aplicação: {e}")
        return False


def start_server():
    """Inicia o servidor"""
    logger.info("🚀 Iniciando servidor...")
    
    try:
        # Importa configurações
        from app.core.config import settings
        
        # Inicia o servidor
        import uvicorn
        
        logger.info(f"🌐 Servidor iniciando em http://{settings.HOST}:{settings.PORT}")
        logger.info(f"📚 Documentação disponível em http://{settings.HOST}:{settings.PORT}/docs")
        logger.info(f"🔍 Health check em http://{settings.HOST}:{settings.PORT}/health")
        
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        return False
    
    return True


def main():
    """Função principal"""
    logger.info("🚀 TechZe Diagnostic Service - Inicialização Segura")
    logger.info("=" * 60)
    
    # Verifica versão do Python
    if not check_python_version():
        return False
    
    # Configura ambiente
    if not setup_environment():
        return False
    
    # Instala dependências mínimas
    if not install_minimal_deps():
        logger.warning("⚠️ Algumas dependências falharam, tentando continuar...")
    
    # Testa importação
    if not test_basic_import():
        logger.error("❌ Falha na importação básica")
        return False
    
    # Inicia servidor
    logger.info("✅ Pré-verificações concluídas, iniciando servidor...")
    return start_server()


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Inicialização cancelada pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)