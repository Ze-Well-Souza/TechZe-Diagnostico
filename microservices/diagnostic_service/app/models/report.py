from enum import Enum as PyEnum
from typing import Dict, Any

from sqlalchemy import Column, String, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ReportFormat(str, PyEnum):
    """Enum para o formato do relatório."""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    CSV = "csv"


class ReportStatus(str, PyEnum):
    """Enum para o status do relatório."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class Report(Base):
    """Modelo para armazenar informações de relatórios."""
    
    # Informações básicas
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Relacionamento com o diagnóstico
    diagnostic_id = Column(String(36), ForeignKey("diagnostic.id"), nullable=False)
    diagnostic = relationship("Diagnostic", back_populates="reports")
    
    # Informações do relatório
    format = Column(Enum(ReportFormat), default=ReportFormat.PDF)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    
    # Caminho do arquivo
    file_path = Column(String(255), nullable=True)
    
    # URL pública (se disponível)
    public_url = Column(String(255), nullable=True)
    
    # Mensagem de erro (se houver)
    error_message = Column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para um dicionário.
        
        Returns:
            Dicionário com os dados do relatório
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "diagnostic_id": self.diagnostic_id,
            "format": self.format,
            "status": self.status,
            "file_path": self.file_path,
            "public_url": self.public_url,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }