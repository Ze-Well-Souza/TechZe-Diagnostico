from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import time
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Imports da aplicação
from app.core.config import settings

# Imports do connection pooling avançado
try:
    from app.core.advanced_pool import AdvancedConnectionPool, initialize_advanced_pool, get_advanced_pool
    from app.core.advanced_pool_metrics import MetricsEnabledConnectionPool, create_metrics_enabled_pool
    from app.core.database_pool import pool_manager
    ADVANCED_POOL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Advanced pool modules not available: {e}")
    ADVANCED_POOL_AVAILABLE = False

# Imports dos novos módulos de segurança e monitoramento
try:
    from app.core.rate_limiter import setup_rate_limiting
    from app.core.monitoring import setup_monitoring, techze_metrics, monitor_diagnostic
    from app.core.error_tracking import setup_error_tracking, track_errors
    from app.core.audit import audit_service, AuditEventType, audit_endpoint
    from app.core.advanced_monitoring import advanced_monitoring
    from app.core.cache_manager import cache_manager
    SECURITY_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Security modules not available: {e}")
    SECURITY_MODULES_AVAILABLE = False

# Import da API Core (Consolidada) - PRIORIDADE
try:
    from app.api.core.router import api_router as core_api_router
    API_CORE_ROUTER_AVAILABLE = True
    logger.info("✅ API Core router imported successfully")
except ImportError as e:
    logger.warning(f"API Core router not available: {e}")
    API_CORE_ROUTER_AVAILABLE = False

# Import condicional dos routers legacy para compatibilidade temporária
try:
    from app.api.router import api_router
    API_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API router not available: {e}")
    API_ROUTER_AVAILABLE = False

try:
    from app.api.v1.router import api_v1_router
    API_V1_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API v1 router not available: {e}")
    API_V1_ROUTER_AVAILABLE = False

# Import da API v3 apenas se Core não estiver disponível
try:
    from app.api.v3 import ai_endpoints, automation_endpoints, analytics_endpoints, chat_endpoints
    from app.api.v3 import performance_endpoints
    API_V3_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API v3 router not available: {e}")
    API_V3_ROUTER_AVAILABLE = False

# Import dos analisadores para funcionalidade básica
try:
    from app.services.analyzers import CPUAnalyzer, MemoryAnalyzer, DiskAnalyzer, NetworkAnalyzer
    from app.services.system_info_service import SystemInfoService
    ANALYZERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Analyzers not available: {e}")
    ANALYZERS_AVAILABLE = False

# Função de ciclo de vida da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Iniciando TechZe Diagnostic Service...")
    
    # Inicializar connection pooling avançado
    if ADVANCED_POOL_AVAILABLE:
        try:
            # Configuração dos nós do banco de dados
            db_nodes = [
                {
                    "id": "primary",
                    "host": getattr(settings, 'DATABASE_HOST', 'localhost'),
                    "port": getattr(settings, 'DATABASE_PORT', 5432),
                    "database": getattr(settings, 'DATABASE_NAME', 'techze_db'),
                    "user": getattr(settings, 'DATABASE_USER', 'postgres'),
                    "password": getattr(settings, 'DATABASE_PASSWORD', ''),
                    "weight": 1.0,
                    "is_primary": True
                }
            ]
            
            # Adicionar réplicas se configuradas
            replica_hosts = getattr(settings, 'DATABASE_REPLICA_HOSTS', [])
            for i, replica_host in enumerate(replica_hosts):
                db_nodes.append({
                    "id": f"replica_{i+1}",
                    "host": replica_host,
                    "port": getattr(settings, 'DATABASE_PORT', 5432),
                    "database": getattr(settings, 'DATABASE_NAME', 'techze_db'),
                    "user": getattr(settings, 'DATABASE_USER', 'postgres'),
                    "password": getattr(settings, 'DATABASE_PASSWORD', ''),
                    "weight": 0.5,
                    "is_primary": False
                })
            
            # Configuração do pool avançado
            pool_config = {
                "nodes": db_nodes,
                "strategy": "least_connections",
                "max_connections_per_node": getattr(settings, 'DATABASE_MAX_CONNECTIONS', 20),
                "min_connections_per_node": getattr(settings, 'DATABASE_MIN_CONNECTIONS', 5),
                "connection_timeout": 30,
                "retry_attempts": 3,
                "circuit_breaker_threshold": 5,
                "circuit_breaker_timeout": 60,
                "enable_metrics": True
            }
            
            # Inicializar pool avançado
            await initialize_advanced_pool(pool_config)
            logger.info("✅ Connection pooling avançado inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar connection pooling avançado: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando TechZe Diagnostic Service...")
    
    # Fechar connection pooling avançado
    if ADVANCED_POOL_AVAILABLE:
        try:
            pool = await get_advanced_pool()
            if pool:
                await pool.close_all()
                logger.info("✅ Connection pooling avançado encerrado")
        except Exception as e:
            logger.error(f"❌ Erro ao encerrar connection pooling: {e}")

# Inicialização da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para diagnóstico completo de hardware e software - Versão Consolidada",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de segurança e monitoramento
if SECURITY_MODULES_AVAILABLE:
    if getattr(settings, 'RATE_LIMIT_ENABLED', True):
        try:
            limiter, advanced_limiter = setup_rate_limiting(app, getattr(settings, 'REDIS_URL', None))
            logger.info("Rate limiting configurado")
        except Exception as e:
            logger.warning(f"Erro ao configurar rate limiting: {e}")

    if getattr(settings, 'PROMETHEUS_ENABLED', True):
        try:
            instrumentator = setup_monitoring(app)
            logger.info("Monitoramento Prometheus configurado")
        except Exception as e:
            logger.warning(f"Erro ao configurar monitoramento: {e}")

    if getattr(settings, 'SENTRY_DSN', None):
        try:
            error_tracker = setup_error_tracking(app, settings.SENTRY_DSN)
            logger.info("Error tracking Sentry configurado")
        except Exception as e:
            logger.warning(f"Erro ao configurar error tracking: {e}")

# ==========================================
# INCLUIR ROUTERS - PRIORIDADE PARA API CORE
# ==========================================

# 1. API Core (Consolidada) - PRIORIDADE MÁXIMA
if API_CORE_ROUTER_AVAILABLE:
    app.include_router(core_api_router)
    logger.info("✅ API Core routes loaded - Consolidated API with all domains available")
    logger.info("📍 API Core endpoints available at: /api/core/*")
else:
    logger.error("❌ API Core routes not loaded - falling back to legacy APIs")

# 2. Compatibility routers (apenas se Core não estiver disponível)
if not API_CORE_ROUTER_AVAILABLE:
    logger.warning("⚠️  Loading legacy APIs for compatibility...")
    
    # Incluir rotas da API v1 como fallback
    if API_V1_ROUTER_AVAILABLE:
        app.include_router(api_v1_router, prefix=settings.API_V1_STR)
        logger.info("✅ API v1 routes loaded as fallback")
    else:
        logger.warning("API v1 routes not loaded")

    # Incluir rotas da API básica como fallback
    if API_ROUTER_AVAILABLE:
        app.include_router(api_router, prefix=settings.API_V1_STR)
        logger.info("✅ Basic API routes loaded as fallback")
    else:
        logger.warning("Basic API routes not loaded")

    # Incluir rotas da API v3 como fallback
    if API_V3_ROUTER_AVAILABLE:
        app.include_router(ai_endpoints.router, prefix="/api/v3")
        app.include_router(automation_endpoints.router, prefix="/api/v3")
        app.include_router(analytics_endpoints.router, prefix="/api/v3")
        app.include_router(chat_endpoints.router, prefix="/api/v3")
        app.include_router(performance_endpoints.router, prefix="/api/v3")
        logger.info("✅ API v3 routes loaded as fallback")
    else:
        logger.warning("API v3 routes not loaded")

# ==========================================
# ENDPOINTS BÁSICOS DO SISTEMA
# ==========================================

@app.get("/", tags=["Root"])
async def root():
    """Rota raiz do serviço de diagnóstico."""
    return {
        "message": "Bem-vindo ao TechZe Diagnostic Service - API Consolidada",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else "disabled",
        "api": {
            "core": "/api/core" if API_CORE_ROUTER_AVAILABLE else "not available",
            "legacy_v1": settings.API_V1_STR if API_V1_ROUTER_AVAILABLE else "not available",
            "legacy_v3": "/api/v3" if API_V3_ROUTER_AVAILABLE else "not available"
        },
        "status": "running",
        "consolidation_status": {
            "core_api_active": API_CORE_ROUTER_AVAILABLE,
            "legacy_apis_active": not API_CORE_ROUTER_AVAILABLE
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Verificação de saúde do serviço."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": datetime.now().isoformat(),
        "service": "diagnostic-service-consolidated",
        "environment": settings.ENVIRONMENT,
        "api_status": {
            "core_api": "available" if API_CORE_ROUTER_AVAILABLE else "unavailable",
            "legacy_v1": "available" if API_V1_ROUTER_AVAILABLE else "unavailable", 
            "legacy_v3": "available" if API_V3_ROUTER_AVAILABLE else "unavailable"
        },
        "modules": {
            "security": SECURITY_MODULES_AVAILABLE,
            "advanced_pool": ADVANCED_POOL_AVAILABLE,
            "analyzers": ANALYZERS_AVAILABLE
        }
    }

@app.get("/info", tags=["Info"])
async def service_info():
    """Informações detalhadas do serviço."""
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "debug_mode": settings.DEBUG,
        "host": settings.HOST,
        "port": settings.PORT,
        "cors_origins": settings.BACKEND_CORS_ORIGINS,
        "api_consolidation": {
            "status": "active",
            "core_api_available": API_CORE_ROUTER_AVAILABLE,
            "core_api_endpoint": "/api/core" if API_CORE_ROUTER_AVAILABLE else None,
            "legacy_endpoints": {
                "v1": settings.API_V1_STR if API_V1_ROUTER_AVAILABLE else None,
                "v3": "/api/v3" if API_V3_ROUTER_AVAILABLE else None
            }
        },
        "features": {
            "security_modules": SECURITY_MODULES_AVAILABLE,
            "advanced_pool": ADVANCED_POOL_AVAILABLE,
            "analyzers": ANALYZERS_AVAILABLE,
            "supabase": bool(getattr(settings, 'SUPABASE_URL', None)),
            "docs": settings.DEBUG
        }
    }

# ==========================================
# ENDPOINTS DE MONITORAMENTO AVANÇADO
# ==========================================

# Endpoints do connection pooling avançado (mantidos para compatibilidade)
if ADVANCED_POOL_AVAILABLE:
    @app.get("/api/v3/pool/metrics", tags=["Advanced Pool"])
    async def get_pool_metrics():
        """Retorna métricas do connection pool"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            metrics = await pool.get_metrics()
            return {
                "status": "success",
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter métricas do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v3/pool/health", tags=["Advanced Pool"])
    async def get_pool_health():
        """Retorna status de saúde do connection pool"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            health_status = await pool.health_check()
            return {
                "status": "healthy" if health_status["healthy"] else "unhealthy",
                "details": health_status,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao verificar saúde do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v3/pool/stats", tags=["Advanced Pool"])
    async def get_pool_stats():
        """Retorna estatísticas detalhadas do pool"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            stats = await pool.get_detailed_stats()
            return {
                "status": "success",
                "stats": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# TRATAMENTO DE ERROS GLOBAL
# ==========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler para exceções HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler para exceções gerais"""
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

# ==========================================
# SERVIDOR UVICORN
# ==========================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.DEBUG,
        log_level="info"
    ) 