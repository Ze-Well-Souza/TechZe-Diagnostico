import logging
import sys
import json
import uuid
from typing import Any, Dict, List, Optional
from contextvars import ContextVar
from datetime import datetime, timezone

from loguru import logger
from pydantic_settings import BaseSettings

from app.core.config import settings

# Context variables para rastreamento de requests
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')
session_id_var: ContextVar[str] = ContextVar('session_id', default='')

class LoggingSettings(BaseSettings):
    LOGGING_LEVEL: str = settings.LOG_LEVEL
    LOGGING_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    JSON_LOGS: bool = True  # Habilitado por padrão para logging estruturado
    LOG_FILE_PATH: str = "/tmp/techze_logs/app.log"
    AUDIT_LOG_PATH: str = "/tmp/techze_logs/audit.log"
    ERROR_LOG_PATH: str = "/tmp/techze_logs/error.log"


class InterceptHandler(logging.Handler):
    """Manipulador para interceptar logs padrão do Python e redirecioná-los para o Loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        # Obtém o logger correspondente do loguru
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


def structured_log_formatter(record: Dict[str, Any]) -> str:
    """Formatter para logs estruturados em JSON"""
    
    # Dados básicos do log
    log_data = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "logger": record["name"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
        "process_id": record["process"].id,
        "thread_id": record["thread"].id,
    }
    
    # Adiciona contexto de request se disponível
    try:
        request_id = request_id_var.get()
        user_id = user_id_var.get()
        session_id = session_id_var.get()
        
        if request_id:
            log_data["request_id"] = request_id
        if user_id:
            log_data["user_id"] = user_id
        if session_id:
            log_data["session_id"] = session_id
    except Exception:
        pass  # Ignorar erros de contexto
    
    # Adiciona dados extras se disponíveis
    if "extra" in record and record["extra"]:
        for key, value in record["extra"].items():
            if key not in log_data:  # Não sobrescrever campos básicos
                try:
                    log_data[key] = value
                except Exception:
                    log_data[key] = str(value)  # Fallback para string
    
    # Adiciona informações de exceção se disponível
    if record["exception"]:
        try:
            log_data["exception"] = {
                "type": record["exception"].type.__name__ if record["exception"].type else None,
                "value": str(record["exception"].value) if record["exception"].value else None,
                "traceback": record["exception"].traceback.format() if record["exception"].traceback else None
            }
        except Exception:
            log_data["exception"] = "Error formatting exception"
    
    try:
        return json.dumps(log_data, ensure_ascii=False, default=str)
    except Exception as e:
        # Fallback para formato simples se JSON falhar
        return f'{{"timestamp":"{record["time"].isoformat()}","level":"{record["level"].name}","message":"{record["message"]}","error":"JSON formatting failed: {str(e)}"}}'


def set_request_context(request_id: str = None, user_id: str = None, session_id: str = None):
    """Define o contexto de request para logging"""
    if request_id:
        request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)
    if session_id:
        session_id_var.set(session_id)


def generate_request_id() -> str:
    """Gera um ID único para request"""
    return str(uuid.uuid4())


def clear_request_context():
    """Limpa o contexto de request"""
    request_id_var.set('')
    user_id_var.set('')
    session_id_var.set('')


def setup_logging(
    logging_settings: Optional[LoggingSettings] = None,
) -> None:
    """Configura o sistema de logging estruturado usando Loguru.
    
    Args:
        logging_settings: Configurações de logging
    """
    if logging_settings is None:
        logging_settings = LoggingSettings()

    # Configurar Loguru
    logger.remove()  # Remove handlers padrão
    
    # Criar diretórios se não existirem
    import os
    from pathlib import Path
    
    log_dir = Path(logging_settings.LOG_FILE_PATH).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    audit_dir = Path(logging_settings.AUDIT_LOG_PATH).parent
    audit_dir.mkdir(parents=True, exist_ok=True)
    
    error_dir = Path(logging_settings.ERROR_LOG_PATH).parent
    error_dir.mkdir(parents=True, exist_ok=True)
    
    # Formato para console
    if logging_settings.JSON_LOGS:
        console_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message} | {extra}"
    else:
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
    
    # Handler para console
    logger.add(
        sys.stdout,
        format=console_format,
        level=logging_settings.LOGGING_LEVEL,
        colorize=not logging_settings.JSON_LOGS,
        serialize=logging_settings.JSON_LOGS
    )
    
    # Formato para arquivos
    file_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {message} | {extra}"
    
    # Handler para arquivo de aplicação (com rotação)
    logger.add(
        logging_settings.LOG_FILE_PATH,
        format=file_format,
        level=logging_settings.LOGGING_LEVEL,
        rotation="100 MB",
        retention="30 days",
        compression="gz",
        serialize=logging_settings.JSON_LOGS
    )
    
    # Handler para arquivo de erros
    logger.add(
        logging_settings.ERROR_LOG_PATH,
        format=file_format,
        level="ERROR",
        rotation="50 MB",
        retention="90 days",
        compression="gz",
        serialize=logging_settings.JSON_LOGS
    )
    
    # Handler para arquivo de auditoria
    logger.add(
        logging_settings.AUDIT_LOG_PATH,
        format=file_format,
        level="INFO",
        rotation="200 MB",
        retention="365 days",
        compression="gz",
        filter=lambda record: record["extra"].get("category") == "audit",
        serialize=logging_settings.JSON_LOGS
    )

    # Intercepta os logs padrão do Python
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Configura os loggers específicos
    loggers = [
        "uvicorn",
        "uvicorn.error",
        "uvicorn.access",
        "fastapi",
        "sqlalchemy",
        "alembic",
        "httpx",
        "requests",
    ]
    for logger_name in loggers:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    # Log de inicialização com contexto estruturado
    logger.bind(category="system", component="logging").info(
        "Sistema de logging estruturado inicializado",
        extra={
            "json_logs": logging_settings.JSON_LOGS,
            "log_level": logging_settings.LOGGING_LEVEL,
            "log_files": {
                "app": logging_settings.LOG_FILE_PATH,
                "error": logging_settings.ERROR_LOG_PATH,
                "audit": logging_settings.AUDIT_LOG_PATH
            }
        }
    )


def get_logger(name: str, component: str = None) -> logger:
    """Obtém um logger configurado para um módulo específico.
    
    Args:
        name: Nome do módulo
        component: Componente do sistema (opcional)
        
    Returns:
        Logger configurado com contexto
    """
    context = {"module": name}
    if component:
        context["component"] = component
    return logger.bind(**context)


def log_request(method: str, path: str, status_code: int, duration: float, 
               user_id: str = None, request_id: str = None, **kwargs):
    """Log estruturado para requisições HTTP"""
    log_data = {
        "category": "http_request",
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": round(duration * 1000, 2),
        **kwargs
    }
    
    if user_id:
        log_data["user_id"] = user_id
    if request_id:
        log_data["request_id"] = request_id
    
    level = "ERROR" if status_code >= 500 else "WARNING" if status_code >= 400 else "INFO"
    logger.bind(**log_data).log(level, f"{method} {path} - {status_code} ({duration*1000:.2f}ms)")


def log_database_operation(operation: str, table: str, duration: float, 
                          rows_affected: int = None, error: str = None, **kwargs):
    """Log estruturado para operações de banco de dados"""
    log_data = {
        "category": "database",
        "operation": operation,
        "table": table,
        "duration_ms": round(duration * 1000, 2),
        **kwargs
    }
    
    if rows_affected is not None:
        log_data["rows_affected"] = rows_affected
    
    if error:
        log_data["error"] = error
        logger.bind(**log_data).error(f"Database {operation} failed on {table}: {error}")
    else:
        logger.bind(**log_data).info(f"Database {operation} on {table} completed")


def log_security_event(event_type: str, user_id: str = None, ip_address: str = None, 
                      details: Dict[str, Any] = None, severity: str = "INFO"):
    """Log estruturado para eventos de segurança"""
    log_data = {
        "category": "security",
        "event_type": event_type,
        "severity": severity
    }
    
    if user_id:
        log_data["user_id"] = user_id
    if ip_address:
        log_data["ip_address"] = ip_address
    if details:
        log_data["details"] = details
    
    logger.bind(**log_data).log(severity, f"Security event: {event_type}")


def log_business_event(event_type: str, entity_type: str, entity_id: str = None,
                      user_id: str = None, details: Dict[str, Any] = None):
    """Log estruturado para eventos de negócio"""
    log_data = {
        "category": "business",
        "event_type": event_type,
        "entity_type": entity_type
    }
    
    if entity_id:
        log_data["entity_id"] = entity_id
    if user_id:
        log_data["user_id"] = user_id
    if details:
        log_data["details"] = details
    
    logger.bind(**log_data).info(f"Business event: {event_type} on {entity_type}")


def log_audit_event(action: str, resource: str, user_id: str, 
                   resource_id: str = None, changes: Dict[str, Any] = None,
                   ip_address: str = None, user_agent: str = None):
    """Log estruturado para eventos de auditoria"""
    log_data = {
        "category": "audit",
        "action": action,
        "resource": resource,
        "user_id": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if resource_id:
        log_data["resource_id"] = resource_id
    if changes:
        log_data["changes"] = changes
    if ip_address:
        log_data["ip_address"] = ip_address
    if user_agent:
        log_data["user_agent"] = user_agent
    
    logger.bind(**log_data).info(f"Audit: {action} on {resource}")


def log_performance_metric(metric_name: str, value: float, unit: str = "ms",
                          component: str = None, **kwargs):
    """Log estruturado para métricas de performance"""
    log_data = {
        "category": "performance",
        "metric_name": metric_name,
        "value": value,
        "unit": unit,
        **kwargs
    }
    
    if component:
        log_data["component"] = component
    
    logger.bind(**log_data).info(f"Performance metric: {metric_name} = {value}{unit}")