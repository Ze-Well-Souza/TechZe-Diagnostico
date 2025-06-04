from typing import List, Optional
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.models.diagnostic import DiagnosticInDB, DiagnosticResponse
from app.db.repositories.diagnostic_repository import DiagnosticRepository
from app.db.session import get_db
from app.core.security import get_current_user
from app.core.models.user import User

router = APIRouter()


@router.get("/", response_model=dict)
async def get_diagnostic_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    page: int = Query(1, ge=1, description="Página atual"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    device_id: Optional[str] = Query(None, description="Filtrar por ID do dispositivo"),
    status: Optional[str] = Query(None, description="Filtrar por status (pending, running, completed, failed)"),
    start_date: Optional[str] = Query(None, description="Data inicial (formato ISO)"),
    end_date: Optional[str] = Query(None, description="Data final (formato ISO)"),
):
    """Obter histórico de diagnósticos com paginação e filtros"""
    try:
        # Inicializar repositório
        diagnostic_repo = DiagnosticRepository(db)
        
        # Aplicar filtros
        filters = {}
        if device_id:
            filters["device_id"] = device_id
        if status:
            filters["status"] = status
        
        # Filtros de data são tratados separadamente no repositório
        
        # Obter diagnósticos paginados
        diagnostics, total = diagnostic_repo.get_diagnostics_paginated(
            user_id=current_user.id,
            page=page,
            limit=limit,
            filters=filters,
            start_date=start_date,
            end_date=end_date
        )
        
        # Converter para resposta
        diagnostic_responses = [DiagnosticResponse.from_orm(diag) for diag in diagnostics]
        
        # Retornar resposta paginada
        return {
            "data": diagnostic_responses,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit  # Cálculo do total de páginas
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter histórico de diagnósticos: {str(e)}")