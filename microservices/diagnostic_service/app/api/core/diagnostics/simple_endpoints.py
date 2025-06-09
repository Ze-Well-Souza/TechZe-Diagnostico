"""Endpoints simples do Diagnostics - SEM DEPENDÊNCIAS

Versão limpa dos endpoints /info e /health sem nenhuma dependência complexa.
"""

from fastapi import APIRouter
from datetime import datetime

# Router completamente limpo
simple_router = APIRouter()

@simple_router.get("/info")
def diagnostics_info_simple():
    """Informações do domínio diagnostics - VERSÃO LIMPA"""
    return {
        "domain": "diagnostics",
        "name": "Diagnostics Domain",
        "version": "1.0.0", 
        "description": "Diagnóstico de hardware e software",
        "features": ['System Diagnostics', 'Hardware Analysis', 'Performance Tests'],
        "status": "active"
    }

@simple_router.get("/health")
def diagnostics_health_simple():
    """Health check do domínio diagnostics - VERSÃO LIMPA"""
    return {
        "status": "healthy",
        "domain": "diagnostics",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    } 