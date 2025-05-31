
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # Configurações básicas
    PROJECT_NAME: str = "TechZe Diagnostic API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Configurações de ambiente
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Configurações de servidor
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Configurações do Supabase
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_KEY")
    
    # Configurações de banco de dados (para SQLAlchemy se necessário)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Configurações de armazenamento
    REPORT_STORAGE_PATH: str = os.getenv("REPORT_STORAGE_PATH", "/tmp/reports")
    
    # Configurações de segurança
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configurações de CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "https://techze-diagnostic-frontend.onrender.com",
        "https://tecnoreparo.ulytech.com.br"
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Configura SQLAlchemy URI se DATABASE_URL estiver disponível
        if self.DATABASE_URL:
            self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Instância global das configurações
settings = Settings()
