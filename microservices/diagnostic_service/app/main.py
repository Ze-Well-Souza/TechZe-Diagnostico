from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional, Dict, Any
import uvicorn
import os
import logging
from datetime import datetime, timedelta

# Imports para Supabase
from app.core.supabase import initialize_supabase
from app.api.router import api_router
from app.core.config import settings

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Inicialização da aplicação FastAPI
app = FastAPI(
    title="TecnoReparo - Serviço de Diagnóstico",
    description="API para diagnóstico completo de hardware e software com integração Supabase",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Inicializar Supabase na inicialização da aplicação
@app.on_event("startup")
async def startup_event():
    """Eventos de inicialização da aplicação."""
    try:
        # Temporariamente comentado devido a incompatibilidade de versão
        # initialize_supabase()
        logger.info("Aplicação iniciada com sucesso")
    except Exception as e:
        logger.error(f"Erro na inicialização: {e}")
        raise

# Configuração de CORS
origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "https://tecnoreparo.ulytech.com.br",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas da API
app.include_router(api_router, prefix=settings.API_V1_STR)

# Rotas básicas
@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """Rota raiz do serviço de diagnóstico."""
    return {
        "message": "Bem-vindo ao Serviço de Diagnóstico do TecnoReparo",
        "version": "0.1.0",
        "docs": "/docs",
        "api": settings.API_V1_STR
    }

@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Verificação de saúde do serviço."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": datetime.now().isoformat(),
        "service": "diagnostic-service",
        "supabase_configured": bool(settings.SUPABASE_URL and settings.SUPABASE_KEY)
    }


# Manipulação de exceções
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Função principal para execução local
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )