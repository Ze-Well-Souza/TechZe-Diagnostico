"""Router principal da API Core

Consolida todos os domínios funcionais em uma estrutura unificada.
"""

from fastapi import APIRouter
import logging

logger = logging.getLogger(__name__)

# Router principal da API Core
api_router = APIRouter()

# Importações condicionais para sub-routers
routers_config = [
    {"name": "auth", "module": ".auth.endpoints", "router": "router", "tags": ["Authentication"]},
    {"name": "diagnostics", "module": ".diagnostics.endpoints", "router": "router", "tags": ["Diagnostics"]},
    {"name": "diagnostics-simple", "module": ".diagnostics.simple_endpoints", "router": "simple_router", "tags": ["Diagnostics Simple"]},
    {"name": "ai", "module": ".ai.endpoints", "router": "router", "tags": ["Artificial Intelligence"]},
    {"name": "automation", "module": ".automation.endpoints", "router": "router", "tags": ["Automation"]},
    {"name": "analytics", "module": ".analytics.endpoints", "router": "router", "tags": ["Analytics"]},
    {"name": "performance", "module": ".performance.endpoints", "router": "router", "tags": ["Performance"]},
    {"name": "chat", "module": ".chat.endpoints", "router": "router", "tags": ["Chat"]},
    {"name": "integration", "module": ".integration.endpoints", "router": "integration_router", "tags": ["Integration"]}
]

# Incluir routers disponíveis
available_domains = []
for config in routers_config:
    try:
        module = __import__(f"app.api.core{config['module']}", fromlist=[config['router']])
        router_obj = getattr(module, config['router'])
        
        if config['name'] == 'diagnostics-simple':
            api_router.include_router(
                router_obj,
                prefix="/diagnostics-simple", 
                tags=config['tags']
            )
            # diagnostics-simple não conta como domínio separado
        else:
            api_router.include_router(
                router_obj, 
                prefix=f"/{config['name']}", 
                tags=config['tags']
            )
            available_domains.append(config['name'])
        logger.info(f"✅ Router {config['name']} incluído com sucesso")
        
    except ImportError as e:
        logger.warning(f"⚠️ Router {config['name']} não disponível: {e}")
        # Criar stub router para domínios não disponíveis
        stub_router = APIRouter()
        
        @stub_router.get("/health")
        async def domain_health():
            return {
                "status": "unavailable",
                "domain": config['name'],
                "message": f"Domain {config['name']} is not available in this build"
            }
        
        api_router.include_router(
            stub_router,
            prefix=f"/{config['name']}", 
            tags=[f"{config['tags'][0]} (Stub)"]
        )
        logger.info(f"🔧 Stub router criado para {config['name']}")

# Endpoint de informações da API
@api_router.get("/info")
async def api_info():
    """Informações sobre a API Core"""
    return {
        "name": "TechZe Diagnostic Service - API Core",
        "version": "1.0.0",
        "description": "API consolidada com organização por domínios funcionais",
        "domains": available_domains,
        "available_domains": available_domains,
        "total_domains": len(routers_config),
        "coverage": f"{len(available_domains)}/{len(routers_config)} ({len(available_domains)/len(routers_config)*100:.1f}%)"
    }

# Endpoint de health check geral
@api_router.get("/health")
async def core_health():
    """Health check da API Core"""
    return {
        "status": "healthy",
        "api_core": "active",
        "available_domains": available_domains,
        "domains_count": len(available_domains)
    }