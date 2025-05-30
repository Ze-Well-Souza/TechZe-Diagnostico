from fastapi import APIRouter
from app.api.endpoints import diagnostics

api_router = APIRouter()

# Incluir rotas de diagnósticos
api_router.include_router(
    diagnostics.router,
    prefix="/diagnostics",
    tags=["diagnostics"]
)

# Rota de saúde da API
@api_router.get("/health", tags=["health"])
async def api_health():
    """Verificação de saúde da API."""
    return {
        "status": "ok",
        "message": "API de Diagnóstico funcionando corretamente"
    }