from typing import Dict, Any, List

from sqlalchemy import Column, String, Integer, JSON, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class SystemInfo(Base):
    """Modelo para armazenar informações do sistema."""
    
    # Informações básicas do sistema
    hostname = Column(String(255), nullable=True)
    os_name = Column(String(100), nullable=True)
    os_version = Column(String(100), nullable=True)
    os_arch = Column(String(50), nullable=True)
    kernel_version = Column(String(100), nullable=True)
    
    # Informações de hardware
    cpu_model = Column(String(255), nullable=True)
    cpu_cores = Column(Integer, nullable=True)
    cpu_threads = Column(Integer, nullable=True)
    cpu_frequency = Column(String(50), nullable=True)  # Ex: "3.2 GHz"
    
    total_memory = Column(Integer, nullable=True)  # Em MB
    total_disk = Column(Integer, nullable=True)  # Em MB
    
    # Informações de rede
    ip_address = Column(String(50), nullable=True)
    mac_address = Column(String(50), nullable=True)
    
    # Informações de software instalado
    installed_software = Column(JSON, nullable=True)  # Lista de software instalado
    
    # Informações de hardware detalhadas
    hardware_details = Column(JSON, nullable=True)  # Detalhes adicionais de hardware
    
    # Notas adicionais
    notes = Column(Text, nullable=True)
    
    # Relacionamentos
    diagnostics = relationship("Diagnostic", back_populates="system_info")
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte o modelo para um dicionário.
        
        Returns:
            Dicionário com os dados do sistema
        """
        return {
            "id": self.id,
            "hostname": self.hostname,
            "os_name": self.os_name,
            "os_version": self.os_version,
            "os_arch": self.os_arch,
            "kernel_version": self.kernel_version,
            "cpu_model": self.cpu_model,
            "cpu_cores": self.cpu_cores,
            "cpu_threads": self.cpu_threads,
            "cpu_frequency": self.cpu_frequency,
            "total_memory": self.total_memory,
            "total_disk": self.total_disk,
            "ip_address": self.ip_address,
            "mac_address": self.mac_address,
            "installed_software": self.installed_software,
            "hardware_details": self.hardware_details,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }