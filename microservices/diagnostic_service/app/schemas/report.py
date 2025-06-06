from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel

from app.models.report import ReportFormat, ReportStatus


# Schemas compartilhados
class ReportBase(BaseModel):
    """Atributos compartilhados para criação e leitura."""
    title: str
    description: Optional[str] = None
    format: ReportFormat = ReportFormat.PDF


# Schema para criação de relatório
class ReportCreate(ReportBase):
    """Atributos para criar um novo relatório."""
    diagnostic_id: str


# Schema para atualização de relatório
class ReportUpdate(BaseModel):
    """Atributos que podem ser atualizados."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ReportStatus] = None
    file_path: Optional[str] = None
    public_url: Optional[str] = None
    error_message: Optional[str] = None


# Schema para leitura de relatório
class ReportInDB(ReportBase):
    """Atributos retornados ao ler um relatório do banco de dados."""
    id: str
    diagnostic_id: str
    status: ReportStatus
    file_path: Optional[str] = None
    public_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Schema para resposta de relatório
class ReportResponse(ReportInDB):
    """Schema para resposta da API."""
    pass


# Schema para lista de relatórios
class ReportListResponse(BaseModel):
    """Schema para resposta de lista de relatórios."""
    total: int
    items: List[ReportResponse]


# Schema para download de relatório
class ReportDownload(BaseModel):
    """Informações para download de relatório."""
    file_url: str
    filename: str
    mime_type: str
    expires_at: Optional[datetime] = None