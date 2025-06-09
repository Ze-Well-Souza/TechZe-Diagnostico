"""
TechZe Diagnostic Service - Main Application
API Consolidada com organização por domínios funcionais
"""

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
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
    ADVANCED_POOL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Advanced pool modules not available: {e}")
    ADVANCED_POOL_AVAILABLE = False

# Imports dos módulos de segurança e monitoramento
try:
    from app.core.rate_limiter import setup_rate_limiting
    from app.core.monitoring import setup_monitoring
    from app.core.error_tracking import setup_error_tracking
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
    logger.error(f"❌ API Core router not available: {e}")
    API_CORE_ROUTER_AVAILABLE = False

# Import dos analisadores
try:
    from app.services.analyzers import CPUAnalyzer, MemoryAnalyzer, DiskAnalyzer, NetworkAnalyzer
    ANALYZERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Analyzers not available: {e}")
    ANALYZERS_AVAILABLE = False

# ==========================================
# CONFIGURAÇÃO DO CICLO DE VIDA
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Iniciando TechZe Diagnostic Service - API Consolidada...")
    
    # Inicializar connection pooling avançado
    if ADVANCED_POOL_AVAILABLE:
        try:
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
            
            await initialize_advanced_pool(pool_config)
            logger.info("✅ Connection pooling inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar connection pooling: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando TechZe Diagnostic Service...")
    
    if ADVANCED_POOL_AVAILABLE:
        try:
            pool = await get_advanced_pool()
            if pool:
                await pool.close_all()
                logger.info("✅ Connection pooling encerrado")
        except Exception as e:
            logger.error(f"❌ Erro ao encerrar connection pooling: {e}")

# ==========================================
# CONFIGURAÇÃO DA APLICAÇÃO FASTAPI
# ==========================================

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
            setup_rate_limiting(app, getattr(settings, 'REDIS_URL', None))
            logger.info("✅ Rate limiting configurado")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao configurar rate limiting: {e}")

    if getattr(settings, 'PROMETHEUS_ENABLED', True):
        try:
            setup_monitoring(app)
            logger.info("✅ Monitoramento Prometheus configurado")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao configurar monitoramento: {e}")

    if getattr(settings, 'SENTRY_DSN', None):
        try:
            setup_error_tracking(app, settings.SENTRY_DSN)
            logger.info("✅ Error tracking Sentry configurado")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao configurar error tracking: {e}")

# ==========================================
# INCLUIR ROUTERS - API CORE CONSOLIDADA
# ==========================================

if API_CORE_ROUTER_AVAILABLE:
    app.include_router(core_api_router)
    logger.info("✅ API Core routes loaded - Consolidated API available at /api/core/*")
else:
    logger.error("❌ API Core routes not loaded - service will have limited functionality")

# ==========================================
# ENDPOINTS BÁSICOS DO SISTEMA
# ==========================================

@app.get("/", tags=["Root"])
async def root():
    """Rota raiz do serviço de diagnóstico."""
    return {
        "service": "TechZe Diagnostic Service",
        "version": settings.VERSION,
        "status": "running",
        "api_consolidation": {
            "status": "active",
            "core_api": "/api/core" if API_CORE_ROUTER_AVAILABLE else "unavailable"
        },
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else "disabled",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Verificação de saúde do serviço."""
    return {
        "status": "healthy",
        "service": "diagnostic-service-consolidated",
        "version": settings.VERSION,
        "timestamp": datetime.now().isoformat(),
        "environment": settings.ENVIRONMENT,
        "api_status": {
            "core_api": "available" if API_CORE_ROUTER_AVAILABLE else "unavailable"
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
        "api_consolidation": {
            "status": "completed",
            "core_api_available": API_CORE_ROUTER_AVAILABLE,
            "core_api_endpoint": "/api/core" if API_CORE_ROUTER_AVAILABLE else None,
            "domains": [
                "auth",
                "diagnostics", 
                "ai",
                "automation",
                "analytics",
                "performance",
                "chat",
                "integration"
            ] if API_CORE_ROUTER_AVAILABLE else []
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
# ENDPOINTS DE MONITORAMENTO (LEGACY)
# ==========================================

# Mantidos para compatibilidade com sistemas de monitoramento existentes
if ADVANCED_POOL_AVAILABLE:
    @app.get("/api/v3/pool/metrics", tags=["Legacy Monitoring"])
    async def get_pool_metrics():
        """Retorna métricas do connection pool (Legacy)"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            metrics = await pool.get_metrics()
            return {
                "status": "success",
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat(),
                "note": "This is a legacy endpoint. Use /api/core/performance/stats instead."
            }
        except Exception as e:
            logger.error(f"Erro ao obter métricas do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v3/pool/health", tags=["Legacy Monitoring"])
    async def get_pool_health():
        """Retorna status de saúde do connection pool (Legacy)"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            health_status = await pool.health_check()
            return {
                "status": "healthy" if health_status["healthy"] else "unhealthy",
                "details": health_status,
                "timestamp": datetime.utcnow().isoformat(),
                "note": "This is a legacy endpoint. Use /api/core/performance/health instead."
            }
        except Exception as e:
            logger.error(f"Erro ao verificar saúde do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v3/pool/stats", tags=["Legacy Monitoring"])
    async def get_pool_stats():
        """Retorna estatísticas detalhadas do pool (Legacy)"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            stats = await pool.get_detailed_stats()
            return {
                "status": "success",
                "stats": stats,
                "timestamp": datetime.utcnow().isoformat(),
                "note": "This is a legacy endpoint. Use /api/core/performance/stats instead."
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# TRATAMENTO DE ERROS GLOBAL
# ==========================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler para exceções HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "service": "diagnostic-service-consolidated"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções gerais"""
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Erro interno do servidor",
            "status_code": 500,
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url),
            "service": "diagnostic-service-consolidated"
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
        log_level=getattr(settings, 'LOG_LEVEL', 'info').lower()
    ) 