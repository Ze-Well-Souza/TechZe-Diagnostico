"""
Sistema Avançado de Error Handling Global para TechZe Diagnostic
Captura, processa e reporta erros de forma estruturada
"""

import traceback
import logging
import time
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import asyncio

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from app.core.config import settings

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Severidade dos erros"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ErrorCategory(Enum):
    """Categorias de erro"""
    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"
    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    UNKNOWN = "unknown"

@dataclass
class ErrorEvent:
    """Evento de erro estruturado"""
    id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    message: str
    component: str
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ErrorProcessor:
    """Processador de erros"""
    
    def __init__(self):
        self.error_buffer = deque(maxlen=1000)
        self.error_counts = {}
        self.start_time = time.time()
        
    def categorize_error(self, error: Exception, context: Dict = None) -> ErrorCategory:
        """Categoriza automaticamente o erro"""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Categorização baseada no tipo
        if isinstance(error, (ConnectionError, TimeoutError)):
            return ErrorCategory.NETWORK
        elif isinstance(error, (ValueError, TypeError)):
            return ErrorCategory.VALIDATION
        elif "database" in error_message or "sql" in error_message:
            return ErrorCategory.DATABASE
        elif "auth" in error_message or "permission" in error_message:
            return ErrorCategory.AUTHENTICATION
        elif "http" in error_message or "api" in error_message:
            return ErrorCategory.EXTERNAL_SERVICE
        else:
            return ErrorCategory.UNKNOWN
    
    def determine_severity(self, error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determina a severidade do erro"""
        error_type = type(error).__name__
        
        # Erros críticos do sistema
        if error_type in ['SystemExit', 'KeyboardInterrupt', 'MemoryError']:
            return ErrorSeverity.CRITICAL
        
        # Erros de categoria crítica
        if category in [ErrorCategory.DATABASE, ErrorCategory.SYSTEM]:
            return ErrorSeverity.HIGH
        
        # Erros de rede e serviços externos
        if category in [ErrorCategory.NETWORK, ErrorCategory.EXTERNAL_SERVICE]:
            return ErrorSeverity.MEDIUM
        
        # Outros erros
        return ErrorSeverity.LOW
    
    def process_error(self, error: Exception, component: str, context: Dict = None, 
                     request: Request = None) -> ErrorEvent:
        """Processa um erro e cria evento estruturado"""
        
        # Gera ID único
        error_id = f"err_{int(time.time() * 1000)}_{id(error)}"
        
        # Categoriza e determina severidade
        category = self.categorize_error(error, context)
        severity = self.determine_severity(error, category)
        
        # Extrai informações do request se disponível
        user_id = None
        request_id = None
        if request:
            request_id = getattr(request.state, 'request_id', None)
            # user_id = getattr(request.state, 'user_id', None)  # Implementar se necessário
        
        # Cria evento de erro
        error_event = ErrorEvent(
            id=error_id,
            timestamp=datetime.now(timezone.utc),
            severity=severity,
            category=category,
            message=str(error),
            component=component,
            user_id=user_id,
            request_id=request_id,
            stack_trace=traceback.format_exc(),
            context=context or {},
            metadata={
                "error_type": type(error).__name__,
                "python_version": sys.version,
                "uptime_seconds": time.time() - self.start_time
            }
        )
        
        # Armazena no buffer
        self.error_buffer.append(error_event)
        
        # Conta erros por tipo
        error_key = f"{category.value}:{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log estruturado
        self._log_error(error_event)
        
        return error_event
    
    def _log_error(self, error_event: ErrorEvent):
        """Faz log estruturado do erro"""
        log_data = {
            "error_id": error_event.id,
            "severity": error_event.severity.value,
            "category": error_event.category.value,
            "component": error_event.component,
            "message": error_event.message,
            "timestamp": error_event.timestamp.isoformat()
        }
        
        if error_event.severity == ErrorSeverity.CRITICAL:
            logger.critical("ERRO CRÍTICO", extra=log_data)
        elif error_event.severity == ErrorSeverity.HIGH:
            logger.error("ERRO ALTO", extra=log_data)
        elif error_event.severity == ErrorSeverity.MEDIUM:
            logger.warning("ERRO MÉDIO", extra=log_data)
        else:
            logger.info("ERRO BAIXO", extra=log_data)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de erros"""
        total_errors = len(self.error_buffer)
        
        # Últimos 5 minutos
        recent_errors = [
            err for err in self.error_buffer 
            if (datetime.now(timezone.utc) - err.timestamp).seconds < 300
        ]
        
        # Por severidade
        by_severity = {}
        for severity in ErrorSeverity:
            count = len([err for err in recent_errors if err.severity == severity])
            by_severity[severity.value] = count
        
        # Por categoria
        by_category = {}
        for category in ErrorCategory:
            count = len([err for err in recent_errors if err.category == category])
            by_category[category.value] = count
        
        return {
            "total_errors": total_errors,
            "recent_errors_5min": len(recent_errors),
            "by_severity": by_severity,
            "by_category": by_category,
            "error_rate_5min": len(recent_errors) / 5,  # erros por minuto
            "top_error_types": dict(sorted(self.error_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        }

class GlobalErrorHandler:
    """Handler global de erros para FastAPI"""
    
    def __init__(self):
        self.processor = ErrorProcessor()
        self.notification_handlers = []
        
    def add_notification_handler(self, handler):
        """Adiciona handler para notificações"""
        self.notification_handlers.append(handler)
    
    async def handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """Manipula HTTPExceptions"""
        
        error_event = self.processor.process_error(
            exc, 
            "http_handler",
            context={
                "status_code": exc.status_code,
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers)
            },
            request=request
        )
        
        # Notifica handlers
        await self._notify_handlers(error_event)
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "id": error_event.id,
                    "message": exc.detail,
                    "status_code": exc.status_code,
                    "timestamp": error_event.timestamp.isoformat(),
                    "service": "techze-diagnostic"
                }
            }
        )
    
    async def handle_general_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Manipula exceções gerais"""
        
        error_event = self.processor.process_error(
            exc,
            "general_handler", 
            context={
                "url": str(request.url),
                "method": request.method,
                "user_agent": request.headers.get("user-agent", "unknown")
            },
            request=request
        )
        
        # Notifica handlers 
        await self._notify_handlers(error_event)
        
        # Resposta baseada na severidade
        if error_event.severity == ErrorSeverity.CRITICAL:
            status_code = 503  # Service Unavailable
            message = "Erro crítico do sistema. Tente novamente mais tarde."
        elif error_event.severity == ErrorSeverity.HIGH:
            status_code = 500  # Internal Server Error
            message = "Erro interno do servidor."
        else:
            status_code = 400  # Bad Request
            message = "Erro na requisição."
        
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "id": error_event.id,
                    "message": message,
                    "status_code": status_code,
                    "timestamp": error_event.timestamp.isoformat(),
                    "service": "techze-diagnostic",
                    "category": error_event.category.value,
                    "severity": error_event.severity.value
                }
            }
        )
    
    async def _notify_handlers(self, error_event: ErrorEvent):
        """Notifica handlers de erro"""
        for handler in self.notification_handlers:
            try:
                await handler(error_event)
            except Exception as e:
                logger.error(f"Erro ao notificar handler: {e}")
    
    def get_error_dashboard(self) -> Dict[str, Any]:
        """Retorna dados para dashboard de erros"""
        stats = self.processor.get_error_stats()
        
        # Últimos erros
        recent_errors = sorted(
            [err for err in self.processor.error_buffer if (datetime.now(timezone.utc) - err.timestamp).seconds < 3600],
            key=lambda x: x.timestamp,
            reverse=True
        )[:20]
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "statistics": stats,
            "recent_errors": [
                {
                    "id": err.id,
                    "timestamp": err.timestamp.isoformat(),
                    "severity": err.severity.value,
                    "category": err.category.value,
                    "message": err.message,
                    "component": err.component
                }
                for err in recent_errors
            ]
        }

# Instância global
global_error_handler = GlobalErrorHandler()

# Decorator para captura de erros
def handle_errors(component: str = "unknown"):
    """Decorator para captura automática de erros"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                global_error_handler.processor.process_error(e, component)
                raise
        
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                global_error_handler.processor.process_error(e, component)
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# Context manager para captura de erros
class ErrorCapture:
    """Context manager para captura de erros"""
    
    def __init__(self, component: str, context: Dict = None):
        self.component = component
        self.context = context or {}
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            global_error_handler.processor.process_error(
                exc_val, 
                self.component,
                self.context
            )
        return False  # Não suprime a exceção

# Funções auxiliares
async def setup_error_tracking(app, sentry_dsn: str = None):
    """Configura tracking de erros com Sentry (opcional)"""
    
    # Adiciona handlers ao FastAPI
    app.add_exception_handler(HTTPException, global_error_handler.handle_http_exception)
    app.add_exception_handler(Exception, global_error_handler.handle_general_exception)
    
    # Configura Sentry se DSN fornecido
    if sentry_dsn:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.logging import LoggingIntegration
            
            sentry_logging = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
            
            sentry_sdk.init(
                dsn=sentry_dsn,
                integrations=[
                    FastApiIntegration(auto_enabling_integrations=False),
                    sentry_logging
                ],
                traces_sample_rate=0.1,
                environment=settings.ENVIRONMENT
            )
            
            logger.info("Sentry configurado para tracking de erros")
            
        except ImportError:
            logger.warning("Sentry SDK não disponível")
        except Exception as e:
            logger.error(f"Erro ao configurar Sentry: {e}")
    
    logger.info("Sistema de error handling configurado")
    return global_error_handler

def track_errors(func):
    """Decorator simples para tracking de erros"""
    return handle_errors(func.__name__)(func) 