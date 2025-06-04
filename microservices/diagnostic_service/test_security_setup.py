#!/usr/bin/env python3
"""
Script de teste para verificar se o setup de segurança está funcionando
"""
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Testa se todos os módulos podem ser importados"""
    logger.info("🧪 Testando imports...")
    
    try:
        # Testa configuração
        from app.core.config import settings
        logger.info("✅ Config importado com sucesso")
        
        # Testa módulos de segurança
        from app.core.rate_limiter import AdvancedRateLimiter, setup_rate_limiting
        logger.info("✅ Rate limiter importado com sucesso")
        
        from app.core.monitoring import TechZeMetrics, setup_monitoring
        logger.info("✅ Monitoring importado com sucesso")
        
        from app.core.error_tracking import ErrorTracker, setup_error_tracking
        logger.info("✅ Error tracking importado com sucesso")
        
        from app.core.audit import AuditService, AuditEventType
        logger.info("✅ Audit importado com sucesso")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao importar módulos: {e}")
        return False


def test_main_app():
    """Testa se a aplicação principal pode ser inicializada"""
    logger.info("🧪 Testando aplicação principal...")
    
    try:
        from app.main import app
        logger.info("✅ Aplicação FastAPI criada com sucesso")
        
        # Verifica se as rotas básicas existem
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/info", "/api/v1/diagnostic/quick"]
        
        for route in expected_routes:
            if route in routes:
                logger.info(f"✅ Rota {route} encontrada")
            else:
                logger.warning(f"⚠️ Rota {route} não encontrada")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar aplicação: {e}")
        return False


def test_security_modules():
    """Testa se os módulos de segurança funcionam"""
    logger.info("🧪 Testando módulos de segurança...")
    
    try:
        # Testa rate limiter
        from app.core.rate_limiter import AdvancedRateLimiter
        rate_limiter = AdvancedRateLimiter()
        logger.info("✅ Rate limiter inicializado")
        
        # Testa métricas
        from app.core.monitoring import TechZeMetrics
        metrics = TechZeMetrics()
        logger.info("✅ Métricas inicializadas")
        
        # Testa error tracker
        from app.core.error_tracking import ErrorTracker
        error_tracker = ErrorTracker()
        logger.info("✅ Error tracker inicializado")
        
        # Testa audit service
        from app.core.audit import AuditService
        audit_service = AuditService()
        logger.info("✅ Audit service inicializado")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar módulos de segurança: {e}")
        return False


def test_configuration():
    """Testa se as configurações estão corretas"""
    logger.info("🧪 Testando configurações...")
    
    try:
        from app.core.config import settings
        
        # Verifica configurações básicas
        assert settings.PROJECT_NAME, "PROJECT_NAME não configurado"
        assert settings.VERSION, "VERSION não configurado"
        assert settings.API_V1_STR, "API_V1_STR não configurado"
        
        logger.info(f"✅ Projeto: {settings.PROJECT_NAME}")
        logger.info(f"✅ Versão: {settings.VERSION}")
        logger.info(f"✅ API Prefix: {settings.API_V1_STR}")
        logger.info(f"✅ Ambiente: {settings.ENVIRONMENT}")
        logger.info(f"✅ Debug: {settings.DEBUG}")
        logger.info(f"✅ Host: {settings.HOST}")
        logger.info(f"✅ Port: {settings.PORT}")
        
        # Verifica configurações de segurança
        logger.info(f"✅ Rate Limiting: {settings.RATE_LIMIT_ENABLED}")
        logger.info(f"✅ Prometheus: {settings.PROMETHEUS_ENABLED}")
        logger.info(f"✅ Redis URL: {'Configurado' if settings.REDIS_URL else 'Não configurado'}")
        logger.info(f"✅ Sentry DSN: {'Configurado' if settings.SENTRY_DSN else 'Não configurado'}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar configurações: {e}")
        return False


def main():
    """Função principal de teste"""
    logger.info("🚀 Iniciando testes de segurança...")
    
    tests = [
        ("Imports", test_imports),
        ("Configuração", test_configuration),
        ("Módulos de Segurança", test_security_modules),
        ("Aplicação Principal", test_main_app),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"🧪 Executando: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASSOU")
            else:
                logger.error(f"❌ {test_name}: FALHOU")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERRO - {e}")
            results.append((test_name, False))
    
    # Relatório final
    logger.info(f"\n{'='*50}")
    logger.info("📊 RELATÓRIO FINAL")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\n📈 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        logger.info("🎉 Todos os testes passaram! Sistema pronto para uso.")
        return True
    else:
        logger.error("⚠️ Alguns testes falharam. Verifique os logs acima.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)