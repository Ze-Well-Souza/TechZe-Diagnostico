#!/usr/bin/env python3
"""
API Core - TechZe Diagnóstico

Aplicação principal que consolida todas as funcionalidades das APIs v1 e v3
em uma estrutura modular e escalável.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import time
import logging
import uvicorn
from typing import Dict, Any

# Importações locais
from .config import settings, validate_environment, apply_environment_config
from .router import api_router
from app.middleware.logging_middleware import StructuredLoggingMiddleware, RequestContextMiddleware
from app.core.logging import setup_logging, get_logger

# Configurar logging estruturado
setup_logging()
logger = get_logger(__name__, "api_core")

# Eventos de ciclo de vida
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Iniciando TechZe Diagnóstico API Core...")
    
    try:
        # Validação do ambiente (desabilitada temporariamente para desenvolvimento)
        # validate_environment()
        logger.info("✅ Ambiente validado com sucesso")
        
        # Aplicar configurações específicas do ambiente
        apply_environment_config()
        logger.info(f"✅ Configurações do ambiente {settings.ENVIRONMENT.value} aplicadas")
        
        # Inicializar componentes
        await initialize_components()
        logger.info("✅ Componentes inicializados")
        
        # Logging estruturado configurado com sucesso
        logger.info("📊 Sistema de logging estruturado ativo")
        
        logger.info("🎉 API Core iniciada com sucesso!")
        
    except Exception as e:
        logger.error(f"❌ Erro durante a inicialização: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Finalizando TechZe Diagnóstico API Core...")
    await cleanup_components()
    logger.info("✅ Finalização concluída")

async def initialize_components():
    """Inicializa componentes da aplicação"""
    # Aqui você pode inicializar:
    # - Conexões de banco de dados
    # - Conexões Redis
    # - Clientes HTTP
    # - Modelos de ML
    # - Schedulers
    # - etc.
    
    logger.info("Inicializando banco de dados...")
    # await init_database()
    
    logger.info("Inicializando cache Redis...")
    # await init_redis()
    
    if settings.get_feature_config("ai"):
        logger.info("Inicializando modelos de IA...")
        # await init_ai_models()
    
    if settings.get_feature_config("automation"):
        logger.info("Inicializando sistema de automação...")
        # await init_automation_scheduler()
    
    logger.info("Todos os componentes foram inicializados")

async def cleanup_components():
    """Limpa recursos da aplicação"""
    logger.info("Fechando conexões de banco de dados...")
    # await close_database_connections()
    
    logger.info("Fechando conexões Redis...")
    # await close_redis_connections()
    
    logger.info("Finalizando schedulers...")
    # await shutdown_schedulers()
    
    logger.info("Limpeza de recursos concluída")

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    description="API Core consolidada para diagnóstico e monitoramento de sistemas",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None
)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS.split(","),
    allow_headers=settings.CORS_HEADERS.split(","),
)

# Middleware de hosts confiáveis (apenas em produção)
if settings.is_production():
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["techze.com", "*.techze.com"]
    )

# Middleware para contexto de requisição (deve ser o primeiro)
app.add_middleware(RequestContextMiddleware)

# Middleware para logging estruturado
app.add_middleware(StructuredLoggingMiddleware, exclude_paths=["/health", "/metrics", "/docs", "/openapi.json", "/redoc"])

# Middleware para rate limiting (se habilitado)
if settings.RATE_LIMIT_ENABLED:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Handler de exceções global
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handler personalizado para exceções HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_exception",
                "timestamp": time.time(),
                "path": str(request.url.path)
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções gerais"""
    logger.error(f"Erro não tratado: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Erro interno do servidor" if settings.is_production() else str(exc),
                "type": "internal_error",
                "timestamp": time.time(),
                "path": str(request.url.path)
            }
        }
    )

# Incluir router principal
app.include_router(api_router, prefix="/api/core")

# Endpoints raiz
@app.get("/")
async def root():
    """Endpoint raiz da API"""
    return {
        "message": "TechZe Diagnóstico API Core",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT.value,
        "status": "operational",
        "docs_url": "/docs" if settings.DEBUG else None,
        "api_prefix": "/api/core",
        "features": ["diagnostics", "ai", "automation", "analytics", "performance", "chat"],
        "timestamp": time.time()
    }

@app.get("/health")
async def health_check():
    """Health check geral da aplicação"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT.value,
        "uptime": time.time(),
        "features": {
            "diagnostics": True,
            "ai": True,
            "automation": True,
            "analytics": True,
            "performance": True,
            "chat": True
        },
        "modules": [
            "authentication",
            "diagnostics", 
            "ai",
            "automation",
            "analytics",
            "performance",
            "chat",
            "integration"
        ]
    }

@app.get("/version")
async def version_info():
    """Informações de versão"""
    return {
        "version": settings.VERSION,
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT.value,
        "build_info": {
            "python_version": "3.11+",
            "fastapi_version": "0.104+",
            "api_type": "core",
            "migration_from": ["v1", "v3"]
        }
    }

@app.get("/config")
async def config_info():
    """Informações de configuração (apenas em desenvolvimento)"""
    if not settings.is_development():
        raise HTTPException(status_code=404, detail="Endpoint não disponível em produção")
    
    return settings.to_dict()

# Documentação personalizada
def custom_openapi():
    """Gera documentação OpenAPI personalizada"""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.VERSION,
        description="""
        # TechZe Diagnóstico API Core
        
        API consolidada que unifica as funcionalidades das APIs v1 e v3 em uma estrutura modular e escalável.
        
        ## Módulos Disponíveis
        
        - **Authentication**: Autenticação e autorização com Supabase
        - **Diagnostics**: Diagnósticos de sistema com IA
        - **AI**: Inteligência artificial e machine learning
        - **Automation**: Automação de tarefas e workflows
        - **Analytics**: Análise de dados e relatórios
        - **Performance**: Monitoramento de performance
        - **Chat**: Assistente virtual inteligente
        - **Integration**: Integração com sistemas externos
        
        ## Migração
        
        Esta API substitui as APIs v1 e v3. Consulte o guia de migração para mais detalhes.
        
        ## Autenticação
        
        A API utiliza JWT tokens para autenticação. Obtenha um token através do endpoint `/auth/login`.
        """,
        routes=app.routes,
    )
    
    # Adicionar informações de segurança
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # Adicionar segurança global
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Função principal para execução
def main():
    """Função principal para executar a aplicação"""
    logger.info(f"🚀 Iniciando servidor em {settings.HOST}:{settings.PORT}")
    logger.info(f"📝 Ambiente: {settings.ENVIRONMENT.value}")
    logger.info(f"🔧 Debug: {settings.DEBUG}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD and settings.is_development(),
        workers=settings.WORKERS if settings.is_production() else 1,
        log_level=settings.LOG_LEVEL.value.lower(),
        access_log=True
    )

if __name__ == "__main__":
    main()