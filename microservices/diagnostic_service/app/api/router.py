from fastapi import APIRouter
from app.api.endpoints import diagnostics
from app.api.v1.endpoints import auth, full_diagnostic, history

api_router = APIRouter()

# Incluir rotas de diagnósticos
api_router.include_router(
    diagnostics.router,
    prefix="/diagnostics",
    tags=["diagnostics"]
)

# Incluir rotas básicas de autenticação (sem dependências problemáticas)
try:
    api_router.include_router(
        auth.router,
        prefix="/v1/auth",
        tags=["authentication"]
    )
except Exception as e:
    print(f"Aviso: Não foi possível carregar rotas de auth: {e}")

# Incluir rotas v1 (sem dependências problemáticas)
try:
    api_router.include_router(
        full_diagnostic.router,
        prefix="/v1/diagnostic",
        tags=["diagnostic-v1"]
    )
except Exception as e:
    print(f"Aviso: Não foi possível carregar rotas de diagnóstico: {e}")

try:
    api_router.include_router(
        history.router,
        prefix="/v1/history",
        tags=["history-v1"]
    )
except Exception as e:
    print(f"Aviso: Não foi possível carregar rotas de histórico: {e}")

# Rota de saúde da API
@api_router.get("/health", tags=["health"])
async def api_health():
    """Verificação de saúde da API."""
    return {
        "status": "ok",
        "message": "API de Diagnóstico funcionando corretamente"
    }