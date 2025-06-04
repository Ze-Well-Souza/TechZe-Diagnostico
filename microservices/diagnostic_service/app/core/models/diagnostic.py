from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from app.models.diagnostic import DiagnosticStatus


class DiagnosticBase(BaseModel):
    """Atributos compartilhados para criação e leitura."""
    user_id: Optional[str] = None
    device_id: Optional[str] = None


class DiagnosticCreate(DiagnosticBase):
    """Atributos para criar um novo diagnóstico."""
    pass


class DiagnosticUpdate(BaseModel):
    """Atributos que podem ser atualizados."""
    status: Optional[DiagnosticStatus] = None
    cpu_status: Optional[str] = None
    memory_status: Optional[str] = None
    disk_status: Optional[str] = None
    network_status: Optional[str] = None
    cpu_usage: Optional[float] = None
    cpu_temperature: Optional[float] = None
    memory_usage: Optional[float] = None
    memory_available: Optional[float] = None
    disk_usage: Optional[float] = None
    disk_available: Optional[float] = None
    network_speed: Optional[float] = None
    overall_health: Optional[int] = Field(None, ge=0, le=100)
    raw_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None


class DiagnosticInDB(DiagnosticBase):
    """Atributos retornados ao ler um diagnóstico do banco de dados."""
    id: str
    status: DiagnosticStatus
    created_at: datetime
    updated_at: datetime
    cpu_status: Optional[str] = None
    memory_status: Optional[str] = None
    disk_status: Optional[str] = None
    network_status: Optional[str] = None
    cpu_usage: Optional[float] = None
    cpu_temperature: Optional[float] = None
    memory_usage: Optional[float] = None
    memory_available: Optional[float] = None
    disk_usage: Optional[float] = None
    disk_available: Optional[float] = None
    network_speed: Optional[float] = None
    overall_health: Optional[int] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    
    class Config:
        orm_mode = True


class DiagnosticResponse(DiagnosticInDB):
    """Schema para resposta da API."""
    pass


class DiagnosticListResponse(BaseModel):
    """Schema para resposta de lista de diagnósticos."""
    total: int
    items: List[DiagnosticResponse]
    page: int
    limit: int
    pages: int