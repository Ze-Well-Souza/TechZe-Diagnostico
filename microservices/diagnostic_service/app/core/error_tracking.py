"""
Error Tracking e Alertas com Sentry
"""
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
import logging
from typing import Optional, Dict, Any
from fastapi import Request
import os

logger = logging.getLogger(__name__)


class ErrorTracker:
    """Gerenciador de error tracking"""
    
    def __init__(self, dsn: Optional[str] = None, environment: str = "development"):
        self.dsn = dsn
        self.environment = environment
        self.initialized = False
        
        if dsn:
            self.initialize_sentry()
    
    def initialize_sentry(self):
        """Inicializa Sentry para error tracking"""
        try:
            # Configuração de logging para Sentry
            sentry_logging = LoggingIntegration(
                level=logging.INFO,        # Captura logs de INFO e acima
                event_level=logging.ERROR  # Envia eventos para ERROR e acima
            )
            
            sentry_sdk.init(
                dsn=self.dsn,
                environment=self.environment,
                integrations=[
                    FastApiIntegration(auto_enable=True),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                    sentry_logging,
                ],
                # Performance monitoring
                traces_sample_rate=0.1,  # 10% das transações
                profiles_sample_rate=0.1,  # 10% dos profiles
                
                # Release tracking
                release=os.getenv("APP_VERSION", "1.0.0"),
                
                # Configurações adicionais
                attach_stacktrace=True,
                send_default_pii=False,  # Não enviar informações pessoais
                max_breadcrumbs=50,
                
                # Filtros de erro
                before_send=self._before_send_filter,
                before_send_transaction=self._before_send_transaction_filter,
            )
            
            self.initialized = True
            logger.info("Sentry inicializado para error tracking")
            
        except Exception as e:
            logger.error(f"Falha ao inicializar Sentry: {e}")
            self.initialized = False
    
    def _before_send_filter(self, event, hint):
        """Filtra eventos antes de enviar para Sentry"""
        # Não enviar erros de rate limiting (são esperados)
        if 'exc_info' in hint:
            exc_type, exc_value, tb = hint['exc_info']
            if 'rate limit' in str(exc_value).lower():
                return None
        
        # Não enviar erros de health check
        if event.get('request', {}).get('url', '').endswith('/health'):
            return None
        
        return event
    
    def _before_send_transaction_filter(self, event, hint):
        """Filtra transações antes de enviar para Sentry"""
        # Não rastrear health checks
        transaction_name = event.get('transaction', '')
        if 'health' in transaction_name.lower():
            return None
        
        return event
    
    def capture_exception(self, 
                         exception: Exception, 
                         request: Optional[Request] = None,
                         user_id: Optional[str] = None,
                         extra_context: Optional[Dict[str, Any]] = None):
        """Captura exceção com contexto adicional"""
        if not self.initialized:
            logger.error(f"Error tracking não inicializado: {exception}")
            return
        
        with sentry_sdk.push_scope() as scope:
            # Adiciona contexto do usuário
            if user_id:
                scope.user = {"id": user_id}
            
            # Adiciona contexto da requisição
            if request:
                scope.set_context("request", {
                    "url": str(request.url),
                    "method": request.method,
                    "headers": dict(request.headers),
                    "query_params": dict(request.query_params)
                })
            
            # Adiciona contexto extra
            if extra_context:
                for key, value in extra_context.items():
                    scope.set_context(key, value)
            
            # Adiciona tags
            scope.set_tag("service", "diagnostic-service")
            scope.set_tag("environment", self.environment)
            
            sentry_sdk.capture_exception(exception)
    
    def capture_message(self, 
                       message: str, 
                       level: str = "info",
                       request: Optional[Request] = None,
                       user_id: Optional[str] = None,
                       extra_context: Optional[Dict[str, Any]] = None):
        """Captura mensagem com contexto"""
        if not self.initialized:
            logger.log(getattr(logging, level.upper(), logging.INFO), message)
            return
        
        with sentry_sdk.push_scope() as scope:
            # Adiciona contexto do usuário
            if user_id:
                scope.user = {"id": user_id}
            
            # Adiciona contexto da requisição
            if request:
                scope.set_context("request", {
                    "url": str(request.url),
                    "method": request.method,
                    "headers": dict(request.headers)
                })
            
            # Adiciona contexto extra
            if extra_context:
                for key, value in extra_context.items():
                    scope.set_context(key, value)
            
            sentry_sdk.capture_message(message, level)
    
    def add_breadcrumb(self, 
                      message: str, 
                      category: str = "custom",
                      level: str = "info",
                      data: Optional[Dict[str, Any]] = None):
        """Adiciona breadcrumb para rastreamento"""
        if not self.initialized:
            return
        
        sentry_sdk.add_breadcrumb(
            message=message,
            category=category,
            level=level,
            data=data or {}
        )
    
    def set_user_context(self, user_id: str, email: Optional[str] = None):
        """Define contexto do usuário"""
        if not self.initialized:
            return
        
        sentry_sdk.set_user({
            "id": user_id,
            "email": email
        })
    
    def set_extra_context(self, key: str, value: Any):
        """Define contexto extra"""
        if not self.initialized:
            return
        
        sentry_sdk.set_context(key, value)


class AlertManager:
    """Gerenciador de alertas"""
    
    def __init__(self, error_tracker: ErrorTracker):
        self.error_tracker = error_tracker
        self.alert_thresholds = {
            "error_rate": 0.05,  # 5% de taxa de erro
            "response_time": 5.0,  # 5 segundos
            "memory_usage": 0.85,  # 85% de uso de memória
            "cpu_usage": 0.80,  # 80% de uso de CPU
        }
    
    def check_error_rate(self, current_rate: float):
        """Verifica taxa de erro"""
        if current_rate > self.alert_thresholds["error_rate"]:
            self.error_tracker.capture_message(
                f"High error rate detected: {current_rate:.2%}",
                level="warning",
                extra_context={
                    "alert_type": "error_rate",
                    "current_value": current_rate,
                    "threshold": self.alert_thresholds["error_rate"]
                }
            )
    
    def check_response_time(self, avg_response_time: float):
        """Verifica tempo de resposta"""
        if avg_response_time > self.alert_thresholds["response_time"]:
            self.error_tracker.capture_message(
                f"High response time detected: {avg_response_time:.2f}s",
                level="warning",
                extra_context={
                    "alert_type": "response_time",
                    "current_value": avg_response_time,
                    "threshold": self.alert_thresholds["response_time"]
                }
            )
    
    def check_system_resources(self, cpu_usage: float, memory_usage: float):
        """Verifica recursos do sistema"""
        if cpu_usage > self.alert_thresholds["cpu_usage"]:
            self.error_tracker.capture_message(
                f"High CPU usage detected: {cpu_usage:.1%}",
                level="warning",
                extra_context={
                    "alert_type": "cpu_usage",
                    "current_value": cpu_usage,
                    "threshold": self.alert_thresholds["cpu_usage"]
                }
            )
        
        if memory_usage > self.alert_thresholds["memory_usage"]:
            self.error_tracker.capture_message(
                f"High memory usage detected: {memory_usage:.1%}",
                level="warning",
                extra_context={
                    "alert_type": "memory_usage",
                    "current_value": memory_usage,
                    "threshold": self.alert_thresholds["memory_usage"]
                }
            )


# Instância global
error_tracker = ErrorTracker(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT", "development")
)

alert_manager = AlertManager(error_tracker)


def setup_error_tracking(app, sentry_dsn: Optional[str] = None):
    """Configura error tracking na aplicação"""
    if sentry_dsn:
        error_tracker.dsn = sentry_dsn
        error_tracker.initialize_sentry()
    
    # Middleware para capturar erros automaticamente
    @app.middleware("http")
    async def error_tracking_middleware(request: Request, call_next):
        try:
            # Adiciona breadcrumb para a requisição
            error_tracker.add_breadcrumb(
                message=f"{request.method} {request.url.path}",
                category="http",
                data={
                    "method": request.method,
                    "url": str(request.url),
                    "headers": dict(request.headers)
                }
            )
            
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Captura exceção com contexto da requisição
            user_id = getattr(request.state, "user_id", None)
            error_tracker.capture_exception(
                exception=e,
                request=request,
                user_id=user_id,
                extra_context={
                    "endpoint": request.url.path,
                    "method": request.method
                }
            )
            raise
    
    logger.info("Error tracking configurado")
    return error_tracker


# Decorador para tracking automático de funções
def track_errors(operation_name: str = None):
    """Decorador para tracking automático de erros"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            operation = operation_name or func.__name__
            
            # Adiciona breadcrumb
            error_tracker.add_breadcrumb(
                message=f"Starting operation: {operation}",
                category="operation"
            )
            
            try:
                result = await func(*args, **kwargs)
                
                # Breadcrumb de sucesso
                error_tracker.add_breadcrumb(
                    message=f"Operation completed: {operation}",
                    category="operation",
                    level="info"
                )
                
                return result
                
            except Exception as e:
                # Captura erro com contexto
                error_tracker.capture_exception(
                    exception=e,
                    extra_context={
                        "operation": operation,
                        "function": func.__name__,
                        "args": str(args)[:200],  # Limita tamanho
                        "kwargs": str(kwargs)[:200]
                    }
                )
                raise
        
        return wrapper
    return decorator