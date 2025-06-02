import os
from typing import Optional, List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # Configurações básicas
    PROJECT_NAME: str = "TechZe Diagnostic API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Configurações de ambiente
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Configurações de servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Configurações do Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # Configurações de banco de dados (para SQLAlchemy se necessário)
    DATABASE_URL: Optional[str] = None
    SQLALCHEMY_DATABASE_URI: Optional[str] = None
    
    # Configurações de armazenamento
    REPORT_STORAGE_PATH: str = "/tmp/reports"
    
    # Configurações de segurança
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configurações de CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "https://techze-diagnostic-frontend.onrender.com",
        "https://tecnoreparo.ulytech.com.br"
    ]
    
    # Configurações adicionais opcionais
    SUPABASE_JWT_SECRET: Optional[str] = None
    SERVER_NAME: Optional[str] = None
    SERVER_HOST: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    MAX_CONCURRENT_DIAGNOSTICS: int = 5
    DIAGNOSTIC_TIMEOUT_SECONDS: int = 300
    DIAGNOSTIC_MAX_HISTORY: int = 100
    REPORT_FORMATS: str = '["pdf","json"]'
    REPORT_PUBLIC_URL_BASE: Optional[str] = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Configura SQLAlchemy URI se DATABASE_URL estiver disponível
        if self.DATABASE_URL:
            self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"  # Permite configurações extras


# Instância global das configurações
settings = Settings()
