from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any


class User(BaseModel):
    """Modelo para representar um usuário autenticado."""
    id: str
    email: Optional[EmailStr] = None
    is_active: bool = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        orm_mode = True