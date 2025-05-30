import os
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configurações do aplicativo."""
    
    # Configurações básicas
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutos * 24 horas * 8 dias = 8 dias
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    SERVER_NAME: str = "diagnostic-service"
    SERVER_HOST: AnyHttpUrl = "http://localhost:8000"
    DESCRIPTION: str = "Microserviço para diagnóstico de sistemas e geração de relatórios"
    VERSION: str = "0.1.0"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost",
        "http://localhost:8080",
        "http://localhost:3000",
        "https://tecnoreparo.ulytech.com.br",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "TecnoReparo - Serviço de Diagnóstico"
    
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "diagnostic_service")
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("SQLALCHEMY_DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> Any:
        if isinstance(v, str):
            return v
        # Para desenvolvimento local, usar configuração padrão
        return str(PostgresDsn.build(
            scheme="postgresql",
            username=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "postgres"),
            host=os.getenv("POSTGRES_SERVER", "localhost"),
            path=f"/{os.getenv('POSTGRES_DB', 'diagnostic_service')}"
        ))

    # Configurações de segurança
    ALGORITHM: str = "HS256"
    AUTH_REQUIRED: bool = os.getenv("AUTH_REQUIRED", "1") == "1"
    AUTH_SERVICE_URL: Optional[str] = os.getenv("AUTH_SERVICE_URL")
    
    # Configurações de logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Configurações de diagnóstico
    MAX_CONCURRENT_DIAGNOSTICS: int = int(os.getenv("MAX_CONCURRENT_DIAGNOSTICS", "5"))
    DIAGNOSTIC_TIMEOUT_SECONDS: int = int(os.getenv("DIAGNOSTIC_TIMEOUT_SECONDS", "300"))
    DIAGNOSTIC_MAX_HISTORY: int = int(os.getenv("DIAGNOSTIC_MAX_HISTORY", "100"))  # registros
    
    # Configurações de relatório
    REPORT_STORAGE_PATH: str = os.getenv("REPORT_STORAGE_PATH", "/tmp/reports")
    REPORT_FORMATS: List[str] = ["pdf", "html", "json"]
    REPORT_DEFAULT_FORMAT: str = "pdf"
    REPORT_PUBLIC_URL_BASE: str = os.getenv("REPORT_PUBLIC_URL_BASE", "http://localhost:8000/reports")
    
    # Configurações de armazenamento de arquivos
    STORAGE_TYPE: str = os.getenv("STORAGE_TYPE", "local")  # local, s3, azure
    STORAGE_LOCAL_PATH: str = os.getenv("STORAGE_LOCAL_PATH", "./storage")
    STORAGE_S3_BUCKET: str = os.getenv("STORAGE_S3_BUCKET", "")
    STORAGE_S3_REGION: str = os.getenv("STORAGE_S3_REGION", "")
    STORAGE_AZURE_CONTAINER: str = os.getenv("STORAGE_AZURE_CONTAINER", "")
    
    # Configurações do Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_JWT_SECRET: str = os.getenv("SUPABASE_JWT_SECRET", "")
    
    # Configurações de integração
    NOTIFICATION_SERVICE_URL: Optional[AnyHttpUrl] = None
    USER_SERVICE_URL: Optional[AnyHttpUrl] = None
    DEVICE_SERVICE_URL: Optional[str] = os.getenv("DEVICE_SERVICE_URL")
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env"
    }


settings = Settings()