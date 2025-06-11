#!/usr/bin/env python3
"""
TechZe Diagnostic Service - Development Main Application
Versão simplificada para desenvolvimento local
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório do microserviço ao path
service_dir = Path(__file__).parent.parent
sys.path.insert(0, str(service_dir))

# Carregar variáveis de ambiente do arquivo .env.local
from dotenv import load_dotenv
root_dir = Path(__file__).parent.parent.parent.parent
load_dotenv(root_dir / ".env.local")

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
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
try:
    from app.core.config import settings
except ImportError:
    logger.error("Erro ao importar configurações")
    sys.exit(1)

# ==========================================
# CONFIGURAÇÃO DA APLICAÇÃO FASTAPI
# ==========================================

app = FastAPI(
    title="TechZe Diagnostic API - Development",
    description="API para diagnóstico completo de hardware e software - Versão de Desenvolvimento",
    version="1.0.0-dev",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"  # Para desenvolvimento apenas
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ROTAS BÁSICAS
# ==========================================

@app.get("/")
async def root():
    """Endpoint raiz"""
    return {
        "message": "TechZe Diagnostic API - Development Mode",
        "version": "1.0.0-dev",
        "timestamp": datetime.now().isoformat(),
        "status": "running",
        "environment": "development"
    }

@app.get("/health")
async def health_check():
    """Health check básico"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "TechZe Diagnostic API",
        "version": "1.0.0-dev",
        "environment": "development"
    }

@app.get("/api/health")
async def api_health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "api_version": "1.0.0-dev",
        "timestamp": datetime.now().isoformat(),
        "endpoints_available": [
            "/",
            "/health",
            "/api/health",
            "/docs",
            "/redoc"
        ]
    }

# ==========================================
# IMPORTAÇÃO GRADUAL DAS ROTAS
# ==========================================

# Tentar importar as rotas da API Core
try:
    from app.api.core.router import api_router as core_api_router
    app.include_router(core_api_router, prefix="/api/core")
    logger.info("✅ API Core router carregado com sucesso")
except ImportError as e:
    logger.warning(f"⚠️ API Core router não disponível: {e}")

# ==========================================
# HANDLER DE ERROS
# ==========================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handler global de exceções"""
    logger.error(f"Erro não tratado: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "Ocorreu um erro interno no servidor",
            "timestamp": datetime.now().isoformat()
        }
    )

# ==========================================
# FUNÇÃO PRINCIPAL
# ==========================================

if __name__ == "__main__":
    logger.info("🚀 Iniciando TechZe Diagnostic Service - Modo Desenvolvimento")
    
    uvicorn.run(
        "main_dev:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )