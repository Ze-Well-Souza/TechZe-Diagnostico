"""Router principal da API Core

Consolida todos os domínios funcionais em uma estrutura unificada.
"""

from fastapi import APIRouter
from .auth.endpoints import router as auth_router
from .diagnostics.endpoints import router as diagnostics_router
from .diagnostics.simple_endpoints import simple_router as diagnostics_simple_router
from .ai.endpoints import router as ai_router
from .automation.endpoints import router as automation_router
from .analytics.endpoints import router as analytics_router
from .performance.endpoints import router as performance_router
from .chat.endpoints import router as chat_router
from .integration.endpoints import integration_router

# Router principal da API Core
api_router = APIRouter(prefix="/api/core")

# Incluir todos os routers de domínio
api_router.include_router(
    auth_router, 
    prefix="/auth", 
    tags=["Authentication"]
)

api_router.include_router(
    diagnostics_router, 
    prefix="/diagnostics", 
    tags=["Diagnostics"]
)

api_router.include_router(
    ai_router, 
    prefix="/ai", 
    tags=["Artificial Intelligence"]
)

api_router.include_router(
    automation_router, 
    prefix="/automation", 
    tags=["Automation"]
)

api_router.include_router(
    analytics_router, 
    prefix="/analytics", 
    tags=["Analytics"]
)

api_router.include_router(
    performance_router, 
    prefix="/performance", 
    tags=["Performance"]
)

api_router.include_router(
    chat_router, 
    prefix="/chat", 
    tags=["Chat"]
)

api_router.include_router(
    integration_router, 
    prefix="/integration", 
    tags=["Integration"]
)

# Incluir router simples para teste
api_router.include_router(
    diagnostics_simple_router,
    prefix="/diagnostics-simple", 
    tags=["Diagnostics Simple"]
)

# Endpoint de informações da API
@api_router.get("/info")
async def api_info():
    """Informações sobre a API Core"""
    return {
        "name": "TechZe Diagnostic Service - API Core",
        "version": "1.0.0",
        "description": "API consolidada com organização por domínios funcionais",
        "domains": [
            "auth",
            "diagnostics", 
            "ai",
            "automation",
            "analytics",
            "performance",
            "chat",
            "integration"
        ]
    }