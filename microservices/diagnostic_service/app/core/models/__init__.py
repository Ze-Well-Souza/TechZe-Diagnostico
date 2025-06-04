# Modelos de dados para a aplicação
from app.core.models.user import User
from app.core.models.diagnostic import (
    DiagnosticBase, 
    DiagnosticCreate, 
    DiagnosticUpdate, 
    DiagnosticInDB, 
    DiagnosticResponse, 
    DiagnosticListResponse
)

__all__ = [
    "User",
    "DiagnosticBase",
    "DiagnosticCreate",
    "DiagnosticUpdate",
    "DiagnosticInDB",
    "DiagnosticResponse",
    "DiagnosticListResponse"
]