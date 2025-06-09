# -*- coding: utf-8 -*-
"""
Configuração da API Core - Versão Consolidada

Este arquivo herda da configuração principal e adiciona configurações específicas da API Core.
"""

from app.core.config import Settings as BaseSettings, Environment, LogLevel
from pydantic import Field
from typing import List, Optional


class CoreAPISettings(BaseSettings):
    """
    Configurações específicas da API Core que herdam da configuração principal.
    
    Esta classe estende as configurações base com funcionalidades específicas
    da API Core consolidada.
    """
    
    # Sobrescrever configurações específicas da API Core se necessário
    APP_NAME: str = Field(default="TechZe Diagnostico API Core", env="APP_NAME")
    
    # Configurações específicas da API Core
    API_CORE_PREFIX: str = Field(default="/api/core", env="API_CORE_PREFIX")
    ENABLE_API_DOCS: bool = Field(default=True, env="ENABLE_API_DOCS")
    DOCS_URL: str = Field(default="/docs", env="DOCS_URL")
    REDOC_URL: str = Field(default="/redoc", env="REDOC_URL")
    OPENAPI_URL: str = Field(default="/openapi.json", env="OPENAPI_URL")
    
    # Configurações de middleware
    ENABLE_TRUSTED_HOST: bool = Field(default=True, env="ENABLE_TRUSTED_HOST")
    TRUSTED_HOSTS: List[str] = Field(default=["*"], env="TRUSTED_HOSTS")
    
    # Configurações de rate limiting específicas da API Core
    API_CORE_RATE_LIMIT: str = Field(default="100/minute", env="API_CORE_RATE_LIMIT")
    
    # Configurações de timeout específicas
    API_CORE_TIMEOUT: int = Field(default=30, env="API_CORE_TIMEOUT")
    
    def get_trusted_hosts(self) -> List[str]:
        """Converte trusted hosts string para lista"""
        if isinstance(self.TRUSTED_HOSTS, str):
            if self.TRUSTED_HOSTS == "*":
                return ["*"]
            return [host.strip() for host in self.TRUSTED_HOSTS.split(",")]
        return self.TRUSTED_HOSTS
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"


# Função para validar ambiente
def validate_environment():
    """Valida se o ambiente está configurado corretamente"""
    settings = CoreAPISettings()
    
    required_vars = [
        "SECRET_KEY",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var, None):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"Variáveis de ambiente obrigatórias não configuradas: {missing_vars}")
    
    return True


def apply_environment_config():
    """Aplica configurações específicas do ambiente"""
    settings = CoreAPISettings()
    
    if settings.ENVIRONMENT == Environment.DEVELOPMENT:
        # Configurações para desenvolvimento
        settings.DEBUG = True
        settings.LOG_LEVEL = LogLevel.DEBUG
        settings.RELOAD = True
    elif settings.ENVIRONMENT == Environment.PRODUCTION:
        # Configurações para produção
        settings.DEBUG = False
        settings.LOG_LEVEL = LogLevel.INFO
        settings.RELOAD = False
        settings.ENABLE_PERFORMANCE_PROFILING = False
    
    return settings


# Instância global das configurações
settings = CoreAPISettings()