from fastapi import APIRouter
from app.api.v1.endpoints import history, full_diagnostic

api_v1_router = APIRouter()

# Incluir rotas de histórico de diagnósticos
api_v1_router.include_router(
    history.router,
    prefix="/diagnostic/history",
    tags=["diagnostic-history"]
)

# Incluir rotas de diagnóstico completo
api_v1_router.include_router(
    full_diagnostic.router,
    prefix="/diagnostic/full",
    tags=["diagnostic-full"]
)

# Rota de saúde da API v1
@api_v1_router.get("/health", tags=["health"])
async def api_v1_health():
    """Verificação de saúde da API v1."""
    return {
        "status": "ok",
        "message": "API v1 de Diagnóstico funcionando corretamente",
        "version": "1.0"
    }