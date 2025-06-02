from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
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

# Import condicional do router para evitar erros em caso de dependências faltantes
try:
    from app.api.router import api_router
    API_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API router not available: {e}")
    API_ROUTER_AVAILABLE = False

# Import dos analisadores para funcionalidade básica
try:
    from app.services.analyzers import CPUAnalyzer, MemoryAnalyzer, DiskAnalyzer, NetworkAnalyzer
    from app.services.system_info_service import SystemInfoService
    ANALYZERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Analyzers not available: {e}")
    ANALYZERS_AVAILABLE = False

# Inicialização da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para diagnóstico completo de hardware e software",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas da API se disponíveis
if API_ROUTER_AVAILABLE:
    app.include_router(api_router, prefix=settings.API_V1_STR)
else:
    logger.warning("API routes not loaded - running in minimal mode")

# Rotas básicas
@app.get("/", tags=["Root"])
async def root():
    """Rota raiz do serviço de diagnóstico."""
    return {
        "message": "Bem-vindo ao Serviço de Diagnóstico do TechZe",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else "disabled",
        "api": settings.API_V1_STR,
        "status": "running"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Verificação de saúde do serviço."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": datetime.now().isoformat(),
        "service": "diagnostic-service",
        "environment": settings.ENVIRONMENT,
        "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_KEY),
        "api_router_available": API_ROUTER_AVAILABLE,
        "analyzers_available": ANALYZERS_AVAILABLE
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
        "api_prefix": settings.API_V1_STR,
        "cors_origins": settings.BACKEND_CORS_ORIGINS,
        "features": {
            "api_router": API_ROUTER_AVAILABLE,
            "analyzers": ANALYZERS_AVAILABLE,
            "supabase": bool(settings.SUPABASE_URL),
            "docs": settings.DEBUG
        }
    }

# Endpoint básico de diagnóstico que funciona sem SQLAlchemy
@app.post("/api/v1/diagnostic/quick", tags=["Diagnostic"])
async def quick_diagnostic():
    """Executa um diagnóstico rápido do sistema."""
    if not ANALYZERS_AVAILABLE:
        return {
            "status": "error",
            "message": "Analyzers not available",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Inicializa os analisadores
        cpu_analyzer = CPUAnalyzer()
        memory_analyzer = MemoryAnalyzer()
        disk_analyzer = DiskAnalyzer()
        network_analyzer = NetworkAnalyzer()
        system_info_service = SystemInfoService()
        
        # Executa análises
        cpu_result = cpu_analyzer.analyze()
        memory_result = memory_analyzer.analyze()
        disk_result = disk_analyzer.analyze()
        network_result = network_analyzer.analyze()
        system_info = system_info_service.collect_system_info()
        
        # Calcula health score
        scores = []
        for result in [cpu_result, memory_result, disk_result, network_result]:
            status = result.get("status", "error")
            if status == "healthy":
                scores.append(100)
            elif status == "warning":
                scores.append(70)
            elif status == "critical":
                scores.append(30)
            else:
                scores.append(50)
        
        health_score = int(sum(scores) / len(scores)) if scores else 50
        
        return {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "results": {
                "cpu": cpu_result,
                "memory": memory_result,
                "disk": disk_result,
                "network": network_result
            },
            "system_info": system_info
        }
        
    except Exception as e:
        logger.exception(f"Error in quick diagnostic: {str(e)}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Manipulação de exceções
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "service": "diagnostic-service"
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "service": "diagnostic-service"
        },
    )

# Função principal para execução local
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
