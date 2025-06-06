from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, validator

from app.models.diagnostic import DiagnosticStatus


# Schemas compartilhados
class DiagnosticBase(BaseModel):
    """Atributos compartilhados para criação e leitura."""
    user_id: Optional[str] = None
    device_id: Optional[str] = None


# Schema para criação de diagnóstico
class DiagnosticCreate(DiagnosticBase):
    """Atributos para criar um novo diagnóstico."""
    pass


# Schema para atualização de diagnóstico
class DiagnosticUpdate(BaseModel):
    """Atributos que podem ser atualizados."""
    status: Optional[DiagnosticStatus] = None
    cpu_status: Optional[str] = None
    memory_status: Optional[str] = None
    disk_status: Optional[str] = None
    network_status: Optional[str] = None
    antivirus_status: Optional[str] = None
    driver_status: Optional[str] = None
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


# Schema para leitura de diagnóstico
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
    antivirus_status: Optional[str] = None
    driver_status: Optional[str] = None
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
        from_attributes = True


# Schema para resposta de diagnóstico
class DiagnosticResponse(DiagnosticInDB):
    """Schema para resposta da API."""
    pass


# Schema para lista de diagnósticos
class DiagnosticListResponse(BaseModel):
    """Schema para resposta de lista de diagnósticos."""
    total: int
    items: List[DiagnosticResponse]


# Schema para resultados de diagnóstico
class DiagnosticResult(BaseModel):
    """Resultados detalhados de um diagnóstico."""
    cpu: Dict[str, Any] = Field(..., example={
        "status": "healthy",
        "usage": 25.5,
        "temperature": 45.2,
        "details": {
            "model": "Intel Core i7-9700K",
            "cores": 8,
            "threads": 8,
            "frequency": "3.6 GHz"
        }
    })
    memory: Dict[str, Any] = Field(..., example={
        "status": "healthy",
        "usage": 40.2,
        "available": 8192,  # MB
        "total": 16384  # MB
    })
    disk: Dict[str, Any] = Field(..., example={
        "status": "warning",
        "usage": 85.3,
        "available": 120000,  # MB
        "total": 512000,  # MB
        "read_speed": 150.5,  # MB/s
        "write_speed": 120.3  # MB/s
    })
    network: Dict[str, Any] = Field(..., example={
        "status": "healthy",
        "connectivity": "stable",
        "speed": 100.5,  # Mbps
        "latency": 15.3  # ms
    })
    antivirus: Dict[str, Any] = Field(..., example={
        "status": "healthy",
        "installed": ["Windows Defender"],
        "real_time_protection": True,
        "firewall_enabled": True,
        "recommendations": []
    })
    drivers: Dict[str, Any] = Field(..., example={
        "status": "warning",
        "total_drivers": 150,
        "problematic_drivers": 2,
        "outdated_drivers": 5,
        "recommendations": ["Atualize os drivers de vídeo"]
    })
    overall_health: int = Field(..., ge=0, le=100, example=85)
    
    @validator("overall_health")
    def validate_overall_health(cls, v):
        if v < 0 or v > 100:
            raise ValueError("overall_health must be between 0 and 100")
        return v