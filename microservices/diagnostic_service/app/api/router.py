from fastapi import APIRouter
from app.api.endpoints import diagnostics

# Importar novos endpoints
try:
    from app.api.endpoints import orcamentos, estoque, ordem_servico
    ENDPOINTS_DISPONIVEIS = True
except ImportError as e:
    print(f"Aviso: Novos endpoints não disponíveis: {e}")
    ENDPOINTS_DISPONIVEIS = False

# Importar endpoints v1 opcionais
try:
    from app.api.v1.endpoints import auth, full_diagnostic, history
    V1_ENDPOINTS_DISPONIVEIS = True
except ImportError as e:
    print(f"Aviso: Endpoints v1 não disponíveis: {e}")
    V1_ENDPOINTS_DISPONIVEIS = False

api_router = APIRouter()

# Incluir rotas de diagnósticos
api_router.include_router(
    diagnostics.router,
    prefix="/diagnostics",
    tags=["diagnostics"]
)

# Incluir novos endpoints de negócio
if ENDPOINTS_DISPONIVEIS:
    try:
        api_router.include_router(
            orcamentos.router,
            prefix="/api/v1",
            tags=["orcamentos"]
        )
        print("✅ Rotas de orçamentos carregadas com sucesso")
    except Exception as e:
        print(f"❌ Erro ao carregar rotas de orçamentos: {e}")

    try:
        api_router.include_router(
            estoque.router,
            prefix="/api/v1",
            tags=["estoque"]
        )
        print("✅ Rotas de estoque carregadas com sucesso")
    except Exception as e:
        print(f"❌ Erro ao carregar rotas de estoque: {e}")

    try:
        api_router.include_router(
            ordem_servico.router,
            prefix="/api/v1",
            tags=["ordem-servico"]
        )
        print("✅ Rotas de ordem de serviço carregadas com sucesso")
    except Exception as e:
        print(f"❌ Erro ao carregar rotas de ordem de serviço: {e}")

# Incluir rotas v1 se disponíveis
if V1_ENDPOINTS_DISPONIVEIS:
    try:
        api_router.include_router(
            auth.router,
            prefix="/v1/auth",
            tags=["authentication"]
        )
        print("✅ Rotas de autenticação v1 carregadas")
    except Exception as e:
        print(f"❌ Erro ao carregar rotas de auth: {e}")

    try:
        api_router.include_router(
            full_diagnostic.router,
            prefix="/v1/diagnostic",
            tags=["diagnostic-v1"]
        )
        print("✅ Rotas de diagnóstico v1 carregadas")
    except Exception as e:
        print(f"❌ Erro ao carregar rotas de diagnóstico: {e}")

    try:
        api_router.include_router(
            history.router,
            prefix="/v1/history",
            tags=["history-v1"]
        )
        print("✅ Rotas de histórico v1 carregadas")
    except Exception as e:
        print(f"❌ Erro ao carregar rotas de histórico: {e}")
else:
    print("⚠️ Endpoints v1 não disponíveis - pulando importação")

# Rota de saúde da API
@api_router.get("/health", tags=["health"])
async def api_health():
    """Verificação de saúde da API."""
    return {
        "status": "ok",
        "message": "API de Diagnóstico funcionando corretamente"
    }