from enum import Enum as PyEnum
from typing import Dict, Any, Optional

from sqlalchemy import String, Integer, Float, JSON, ForeignKey, Enum, Boolean, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base_class import Base


class DiagnosticStatus(str, PyEnum):
    """Enum para o status do diagnóstico."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Diagnostic(Base):
    """Modelo para armazenar informações de diagnóstico."""
    
    # Informações básicas
    user_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)  # Pode ser nulo para diagnósticos anônimos
    device_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)  # Identificador do dispositivo
    status: Mapped[DiagnosticStatus] = mapped_column(Enum(DiagnosticStatus), default=DiagnosticStatus.PENDING, index=True)
    
    # Resultados do diagnóstico
    cpu_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    memory_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    disk_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    network_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Métricas detalhadas
    cpu_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    cpu_temperature: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    memory_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    memory_available: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Em MB
    disk_usage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Porcentagem
    disk_available: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Em MB
    network_speed: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # Em Mbps
    
    # Score de saúde geral (0-100)
    overall_health: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Dados brutos do diagnóstico
    raw_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Mensagem de erro (se houver)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Tempo de execução em segundos
    execution_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Relacionamentos
    system_info_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("systeminfo.id"), nullable=True)
    system_info = relationship("SystemInfo", back_populates="diagnostics")
    
    reports = relationship("Report", back_populates="diagnostic")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para um dicionário.
        
        Returns:
            Dicionário com os dados do diagnóstico
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "device_id": self.device_id,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "cpu_status": self.cpu_status,
            "memory_status": self.memory_status,
            "disk_status": self.disk_status,
            "network_status": self.network_status,
            "cpu_usage": self.cpu_usage,
            "cpu_temperature": self.cpu_temperature,
            "memory_usage": self.memory_usage,
            "memory_available": self.memory_available,
            "disk_usage": self.disk_usage,
            "disk_available": self.disk_available,
            "network_speed": self.network_speed,
            "overall_health": self.overall_health,
            "error_message": self.error_message,
            "execution_time": self.execution_time,
        }