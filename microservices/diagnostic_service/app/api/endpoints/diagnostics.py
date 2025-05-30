
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse

from app.core.auth import get_current_user
from app.schemas.diagnostic import DiagnosticCreate, DiagnosticUpdate, DiagnosticInDB
# Temporariamente comentado devido a incompatibilidade de versão do Supabase
# from app.services.supabase_diagnostic_service import SupabaseDiagnosticService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Mock service for development
class MockDiagnosticService:
    def __init__(self):
        self.diagnostics = []
    
    async def create_diagnostic(self, diagnostic_data, user_id):
        mock_diagnostic = {
            "id": f"diag_{len(self.diagnostics) + 1}",
            "device_id": diagnostic_data.device_id,
            "user_id": user_id,
            "status": "pending",
            "health_score": None,
            "created_at": "2024-01-28T10:00:00Z",
            "updated_at": "2024-01-28T10:00:00Z"
        }
        self.diagnostics.append(mock_diagnostic)
        return mock_diagnostic
    
    async def get_diagnostic(self, diagnostic_id, user_id):
        for diag in self.diagnostics:
            if diag["id"] == diagnostic_id and diag["user_id"] == user_id:
                return diag
        return None
    
    async def get_user_diagnostics(self, user_id, limit, offset):
        user_diagnostics = [d for d in self.diagnostics if d["user_id"] == user_id]
        return user_diagnostics[offset:offset+limit]
    
    async def update_diagnostic(self, diagnostic_id, diagnostic_update, user_id):
        for diag in self.diagnostics:
            if diag["id"] == diagnostic_id and diag["user_id"] == user_id:
                diag.update(diagnostic_update.dict(exclude_unset=True))
                diag["updated_at"] = "2024-01-28T10:30:00Z"
                return diag
        return None
    
    async def delete_diagnostic(self, diagnostic_id, user_id):
        for i, diag in enumerate(self.diagnostics):
            if diag["id"] == diagnostic_id and diag["user_id"] == user_id:
                del self.diagnostics[i]
                return True
        return False
    
    async def run_diagnostic(self, diagnostic_id, user_id):
        for diag in self.diagnostics:
            if diag["id"] == diagnostic_id and diag["user_id"] == user_id:
                diag["status"] = "completed"
                diag["health_score"] = 78
                diag["updated_at"] = "2024-01-28T10:45:00Z"
                return diag
        return None

# Instância do serviço
diagnostic_service = MockDiagnosticService()


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_diagnostic(
    diagnostic: DiagnosticCreate,
    user_id: str = Depends(get_current_user)
):
    """
    Cria um novo diagnóstico para o usuário autenticado.
    
    - **device_id**: ID do dispositivo a ser diagnosticado
    - **user_id**: Extraído automaticamente do token JWT
    """
    try:
        result = await diagnostic_service.create_diagnostic(diagnostic, user_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Falha ao criar diagnóstico"
            )
        
        return {
            "message": "Diagnóstico criado com sucesso",
            "diagnostic": result
        }
        
    except Exception as e:
        logger.error(f"Erro ao criar diagnóstico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{diagnostic_id}", response_model=dict)
async def get_diagnostic(
    diagnostic_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Obtém um diagnóstico específico do usuário autenticado.
    
    - **diagnostic_id**: ID único do diagnóstico
    """
    try:
        result = await diagnostic_service.get_diagnostic(diagnostic_id, user_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diagnóstico não encontrado"
            )
        
        return {
            "diagnostic": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar diagnóstico {diagnostic_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/", response_model=dict)
async def get_user_diagnostics(
    user_id: str = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros"),
    offset: int = Query(0, ge=0, description="Deslocamento para paginação")
):
    """
    Obtém todos os diagnósticos do usuário autenticado.
    
    - **limit**: Número máximo de registros (1-100)
    - **offset**: Deslocamento para paginação
    """
    try:
        diagnostics = await diagnostic_service.get_user_diagnostics(user_id, limit, offset)
        
        return {
            "diagnostics": diagnostics,
            "count": len(diagnostics),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar diagnósticos do usuário {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.patch("/{diagnostic_id}", response_model=dict)
async def update_diagnostic(
    diagnostic_id: str,
    diagnostic_update: DiagnosticUpdate,
    user_id: str = Depends(get_current_user)
):
    """
    Atualiza um diagnóstico específico do usuário autenticado.
    
    - **diagnostic_id**: ID único do diagnóstico
    - **diagnostic_update**: Dados para atualização
    """
    try:
        result = await diagnostic_service.update_diagnostic(
            diagnostic_id, diagnostic_update, user_id
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diagnóstico não encontrado ou atualização falhou"
            )
        
        return {
            "message": "Diagnóstico atualizado com sucesso",
            "diagnostic": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar diagnóstico {diagnostic_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.delete("/{diagnostic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diagnostic(
    diagnostic_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Exclui um diagnóstico específico do usuário autenticado.
    
    - **diagnostic_id**: ID único do diagnóstico
    """
    try:
        success = await diagnostic_service.delete_diagnostic(diagnostic_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diagnóstico não encontrado"
            )
        
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir diagnóstico {diagnostic_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.post("/{diagnostic_id}/run", response_model=dict)
async def run_diagnostic(
    diagnostic_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Executa um diagnóstico completo do sistema.
    
    - **diagnostic_id**: ID único do diagnóstico
    """
    try:
        result = await diagnostic_service.run_diagnostic(diagnostic_id, user_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diagnóstico não encontrado"
            )
        
        return {
            "message": "Diagnóstico executado com sucesso",
            "diagnostic": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao executar diagnóstico {diagnostic_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )


@router.get("/{diagnostic_id}/status", response_model=dict)
async def get_diagnostic_status(
    diagnostic_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Obtém apenas o status de um diagnóstico específico.
    
    - **diagnostic_id**: ID único do diagnóstico
    """
    try:
        result = await diagnostic_service.get_diagnostic(diagnostic_id, user_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diagnóstico não encontrado"
            )
        
        return {
            "diagnostic_id": result["id"],
            "status": result["status"],
            "health_score": result.get("health_score"),
            "created_at": result["created_at"],
            "updated_at": result["updated_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar status do diagnóstico {diagnostic_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )
