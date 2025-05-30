from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel


# Schemas compartilhados
class SystemInfoBase(BaseModel):
    """Atributos compartilhados para criação e leitura."""
    hostname: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    os_arch: Optional[str] = None
    kernel_version: Optional[str] = None
    cpu_model: Optional[str] = None
    cpu_cores: Optional[int] = None
    cpu_threads: Optional[int] = None
    cpu_frequency: Optional[str] = None
    total_memory: Optional[int] = None
    total_disk: Optional[int] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    installed_software: Optional[List[Dict[str, Any]]] = None
    hardware_details: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


# Schema para criação de informações do sistema
class SystemInfoCreate(SystemInfoBase):
    """Atributos para criar novas informações do sistema."""
    pass


# Schema para atualização de informações do sistema
class SystemInfoUpdate(SystemInfoBase):
    """Atributos que podem ser atualizados."""
    pass


# Schema para leitura de informações do sistema
class SystemInfoInDB(SystemInfoBase):
    """Atributos retornados ao ler informações do sistema do banco de dados."""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


# Schema para resposta de informações do sistema
class SystemInfoResponse(SystemInfoInDB):
    """Schema para resposta da API."""
    pass


# Schema para lista de informações do sistema
class SystemInfoListResponse(BaseModel):
    """Schema para resposta de lista de informações do sistema."""
    total: int
    items: List[SystemInfoResponse]


# Schema para detalhes de hardware
class HardwareDetails(BaseModel):
    """Detalhes de hardware do sistema."""
    motherboard: Optional[Dict[str, Any]] = None
    graphics_card: Optional[Dict[str, Any]] = None
    storage_devices: Optional[List[Dict[str, Any]]] = None
    network_adapters: Optional[List[Dict[str, Any]]] = None
    peripherals: Optional[List[Dict[str, Any]]] = None
    bios: Optional[Dict[str, Any]] = None


# Schema para software instalado
class InstalledSoftware(BaseModel):
    """Informações sobre software instalado."""
    name: str
    version: Optional[str] = None
    publisher: Optional[str] = None
    install_date: Optional[datetime] = None
    size: Optional[int] = None  # Em MB
    location: Optional[str] = None