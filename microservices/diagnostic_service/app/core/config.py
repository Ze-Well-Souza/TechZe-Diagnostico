import os
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from enum import Enum


class Environment(str, Enum):
    """Ambientes disponíveis"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Níveis de log"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Configurações consolidadas da aplicação."""
    
    # Configurações básicas
    PROJECT_NAME: str = "TechZe Diagnostic API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    APP_NAME: str = "TechZe Diagnostico API Core"
    
    # Configurações de ambiente
    ENVIRONMENT: Environment = Field(default=Environment.PRODUCTION, env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: LogLevel = Field(default=LogLevel.INFO, env="LOG_LEVEL")
    
    @field_validator('LOG_LEVEL', mode='before')
    @classmethod
    def parse_log_level(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v
    
    # Configurações de servidor
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default_factory=lambda: int(os.getenv("PORT", 8000)), env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    RELOAD: bool = Field(default=False, env="RELOAD")
    
    # Configurações do Supabase
    SUPABASE_URL: Optional[str] = Field(default=None, env="SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = Field(default=None, env="SUPABASE_KEY")
    SUPABASE_SERVICE_KEY: Optional[str] = Field(default=None, env="SUPABASE_SERVICE_ROLE_KEY")
    SUPABASE_JWT_SECRET: Optional[str] = Field(default=None, env="SUPABASE_JWT_SECRET")
    
    # Configurações de banco de dados
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    SQLALCHEMY_DATABASE_URI: Optional[str] = Field(default=None, env="SQLALCHEMY_DATABASE_URI")
    DB_HOST: str = Field(default="localhost", env="DB_HOST")
    DB_PORT: int = Field(default=5432, env="DB_PORT")
    DB_NAME: str = Field(default="techze_diagnostico", env="DB_NAME")
    DB_USER: str = Field(default="postgres", env="DB_USER")
    DB_PASSWORD: str = Field(default="", env="DB_PASSWORD")
    DB_POOL_SIZE: int = Field(default=10, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=20, env="DB_MAX_OVERFLOW")
    DB_POOL_TIMEOUT: int = Field(default=30, env="DB_POOL_TIMEOUT")
    DB_POOL_RECYCLE: int = Field(default=3600, env="DB_POOL_RECYCLE")
    
    # Configurações de armazenamento
    REPORT_STORAGE_PATH: str = Field(default="/tmp/reports", env="REPORT_STORAGE_PATH")
    
    # Configurações de segurança
    SECRET_KEY: str = Field(default="your-secret-key-here", env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    PASSWORD_MIN_LENGTH: int = Field(default=8, env="PASSWORD_MIN_LENGTH")
    MAX_LOGIN_ATTEMPTS: int = Field(default=5, env="MAX_LOGIN_ATTEMPTS")
    LOCKOUT_DURATION_MINUTES: int = Field(default=15, env="LOCKOUT_DURATION_MINUTES")
    
    # Rate Limiting e Redis
    REDIS_URL: Optional[str] = Field(default=None, env="REDIS_URL")
    REDIS_HOST: str = Field(default="localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(default=6379, env="REDIS_PORT")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    REDIS_MAX_CONNECTIONS: int = Field(default=10, env="REDIS_MAX_CONNECTIONS")
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    
    # Monitoramento
    PROMETHEUS_ENABLED: bool = Field(default=True, env="PROMETHEUS_ENABLED")
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=8001, env="METRICS_PORT")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    @field_validator('HEALTH_CHECK_INTERVAL', mode='before')
    @classmethod
    def parse_health_check_interval(cls, v):
        """Converte string com sufixo (30s) para inteiro"""
        if isinstance(v, str):
            if v.endswith('s'):
                return int(v[:-1])
            return int(v)
        return v
    ALERT_WEBHOOK_URL: Optional[str] = Field(default=None, env="ALERT_WEBHOOK_URL")
    LOG_RETENTION_DAYS: int = Field(default=30, env="LOG_RETENTION_DAYS")
    ENABLE_PERFORMANCE_PROFILING: bool = Field(default=False, env="ENABLE_PERFORMANCE_PROFILING")
    
    # Auditoria
    AUDIT_LOG_FILE: str = Field(default="/tmp/audit.log", env="AUDIT_LOG_FILE")
    AUDIT_LOG_TO_FILE: bool = Field(default=True, env="AUDIT_LOG_TO_FILE")
    AUDIT_LOG_TO_SUPABASE: bool = Field(default=True, env="AUDIT_LOG_TO_SUPABASE")
    
    # IA e ML
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    AI_MODEL_NAME: str = Field(default="gpt-3.5-turbo", env="AI_MODEL_NAME")
    AI_MAX_TOKENS: int = Field(default=1000, env="AI_MAX_TOKENS")
    AI_TEMPERATURE: float = Field(default=0.7, env="AI_TEMPERATURE")
    ENABLE_ML_TRAINING: bool = Field(default=True, env="ENABLE_ML_TRAINING")
    MODEL_STORAGE_PATH: str = Field(default="./models", env="MODEL_STORAGE_PATH")
    TRAINING_DATA_RETENTION_DAYS: int = Field(default=90, env="TRAINING_DATA_RETENTION_DAYS")
    
    # Chat e WebSocket
    ENABLE_WEBSOCKET: bool = Field(default=True, env="ENABLE_WEBSOCKET")
    MAX_MESSAGE_LENGTH: int = Field(default=4000, env="MAX_MESSAGE_LENGTH")
    SESSION_TIMEOUT_MINUTES: int = Field(default=60, env="SESSION_TIMEOUT_MINUTES")
    MAX_SESSIONS_PER_USER: int = Field(default=5, env="MAX_SESSIONS_PER_USER")
    ENABLE_MESSAGE_HISTORY: bool = Field(default=True, env="ENABLE_MESSAGE_HISTORY")
    HISTORY_RETENTION_DAYS: int = Field(default=30, env="HISTORY_RETENTION_DAYS")
    
    # Automação
    ENABLE_WORKFLOWS: bool = Field(default=True, env="ENABLE_WORKFLOWS")
    MAX_CONCURRENT_TASKS: int = Field(default=10, env="MAX_CONCURRENT_TASKS")
    TASK_TIMEOUT_MINUTES: int = Field(default=30, env="TASK_TIMEOUT_MINUTES")
    ENABLE_SCHEDULING: bool = Field(default=True, env="ENABLE_SCHEDULING")
    SCHEDULER_CHECK_INTERVAL: int = Field(default=60, env="SCHEDULER_CHECK_INTERVAL")
    
    # Analytics
    ENABLE_REAL_TIME_METRICS: bool = Field(default=True, env="ENABLE_REAL_TIME_METRICS")
    METRICS_AGGREGATION_INTERVAL: int = Field(default=300, env="METRICS_AGGREGATION_INTERVAL")
    MAX_DASHBOARD_WIDGETS: int = Field(default=20, env="MAX_DASHBOARD_WIDGETS")
    REPORT_CACHE_TTL: int = Field(default=3600, env="REPORT_CACHE_TTL")
    ENABLE_TREND_ANALYSIS: bool = Field(default=True, env="ENABLE_TREND_ANALYSIS")
    ANALYTICS_RETENTION_DAYS: int = Field(default=90, env="ANALYTICS_RETENTION_DAYS")
    METRICS_COLLECTION_INTERVAL: int = Field(default=60, env="METRICS_COLLECTION_INTERVAL")
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    QUERY_TIMEOUT: int = Field(default=30, env="QUERY_TIMEOUT")
    
    # Performance
    ENABLE_QUERY_OPTIMIZATION: bool = Field(default=True, env="ENABLE_QUERY_OPTIMIZATION")
    SLOW_QUERY_THRESHOLD: float = Field(default=1.0, env="SLOW_QUERY_THRESHOLD")
    ENABLE_CACHING: bool = Field(default=True, env="ENABLE_CACHING")
    CACHE_TTL_SECONDS: int = Field(default=300, env="CACHE_TTL_SECONDS")
    ENABLE_COMPRESSION: bool = Field(default=True, env="ENABLE_COMPRESSION")
    MAX_REQUEST_SIZE_MB: int = Field(default=10, env="MAX_REQUEST_SIZE_MB")
    CONNECTION_TIMEOUT: int = Field(default=30, env="CONNECTION_TIMEOUT")
    REQUEST_TIMEOUT: int = Field(default=60, env="REQUEST_TIMEOUT")
    
    # Integração
    ENABLE_WEBHOOKS: bool = Field(default=True, env="ENABLE_WEBHOOKS")
    WEBHOOK_TIMEOUT: int = Field(default=30, env="WEBHOOK_TIMEOUT")
    MAX_RETRY_ATTEMPTS: int = Field(default=3, env="MAX_RETRY_ATTEMPTS")
    RETRY_DELAY_SECONDS: int = Field(default=5, env="RETRY_DELAY_SECONDS")
    ENABLE_DATA_SYNC: bool = Field(default=True, env="ENABLE_DATA_SYNC")
    SYNC_BATCH_SIZE: int = Field(default=1000, env="SYNC_BATCH_SIZE")
    AUDIT_LOG_TO_CONSOLE: bool = True
    
    # Configurações de CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:8081",
        "http://localhost:5173",
        "https://techze-diagnostic-frontend.onrender.com",
        "https://tecnoreparo.ulytech.com.br"
    ]
    CORS_ORIGINS: str = Field(default="*", env="CORS_ORIGINS")
    CORS_METHODS: str = Field(default="*", env="CORS_METHODS")
    CORS_HEADERS: str = Field(default="*", env="CORS_HEADERS")
    
    # Configurações adicionais do diagnóstico
    SERVER_NAME: Optional[str] = Field(default=None, env="SERVER_NAME")
    SERVER_HOST: Optional[str] = Field(default=None, env="SERVER_HOST")
    MAX_CONCURRENT_DIAGNOSTICS: int = Field(default=5, env="MAX_CONCURRENT_DIAGNOSTICS")
    DIAGNOSTIC_TIMEOUT_SECONDS: int = Field(default=300, env="DIAGNOSTIC_TIMEOUT_SECONDS")
    DIAGNOSTIC_MAX_HISTORY: int = Field(default=100, env="DIAGNOSTIC_MAX_HISTORY")
    REPORT_FORMATS: str = Field(default='["pdf","json"]', env="REPORT_FORMATS")
    REPORT_PUBLIC_URL_BASE: Optional[str] = Field(default=None, env="REPORT_PUBLIC_URL_BASE")
    
    def get_cors_origins(self) -> List[str]:
        """Converte CORS origins string para lista"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def redis_url_computed(self) -> str:
        """URL de conexão do Redis"""
        if self.REDIS_URL:
            return self.REDIS_URL
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def database_url_computed(self) -> str:
        """URL de conexão do banco"""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Configura SQLAlchemy URI se DATABASE_URL estiver disponível
        if self.DATABASE_URL:
            self.SQLALCHEMY_DATABASE_URI = self.DATABASE_URL
        else:
            self.SQLALCHEMY_DATABASE_URI = self.database_url_computed
    
    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "allow"  # Permite configurações extras
    }


# Instância global das configurações
settings = Settings()


def get_settings() -> Settings:
    """
    Retorna a instância global das configurações.
    Função de conveniência para compatibilidade.
    """
    return settings
