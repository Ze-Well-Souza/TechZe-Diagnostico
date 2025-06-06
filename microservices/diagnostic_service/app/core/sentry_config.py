"""Configuração do Sentry para monitoramento APM"""
import os
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, cast

import sentry_sdk
from fastapi import FastAPI, Request
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])

def setup_sentry(app: FastAPI) -> None:
    """Configura o Sentry para monitoramento de erros e performance"""
    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")
    release = os.getenv("RELEASE", "local")
    
    if not sentry_dsn or sentry_dsn.strip() == "" or "your-sentry-dsn" in sentry_dsn:
        logger.warning("SENTRY_DSN não configurado ou inválido. Monitoramento Sentry desativado.")
        return
    
    # Configurar integrações
    integrations = [
        LoggingIntegration(
            level=logging.INFO,        # Capturar logs de INFO e acima como breadcrumbs
            event_level=logging.ERROR  # Enviar logs de ERROR e acima como eventos
        ),
        SqlalchemyIntegration(),
        RedisIntegration(),
    ]
    
    # Inicializar Sentry SDK
    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        release=release,
        integrations=integrations,
        traces_sample_rate=0.2,  # Amostragem de 20% das transações para APM
        profiles_sample_rate=0.1,  # Amostragem de 10% para profiling
        send_default_pii=False,  # Não enviar informações de identificação pessoal por padrão
        max_breadcrumbs=50,  # Número máximo de breadcrumbs
        debug=environment == "development",
        attach_stacktrace=True,
    )
    
    # Adicionar middleware ASGI do Sentry
    app.add_middleware(SentryAsgiMiddleware)
    
    logger.info(f"Sentry configurado para ambiente: {environment}, release: {release}")

def capture_exception(func: F) -> F:
    """Decorator para capturar exceções e enviar para o Sentry"""
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Adicionar contexto adicional
            sentry_sdk.set_context("function_context", {
                "function": func.__name__,
                "module": func.__module__,
                "args_length": len(args),
                "kwargs_keys": list(kwargs.keys()),
            })
            
            # Capturar exceção com contexto
            sentry_sdk.capture_exception(e)
            
            # Re-lançar exceção para tratamento normal
            raise
    
    return cast(F, wrapper)

def start_transaction(name: str, op: str = "task"):
    """Inicia uma transação Sentry para monitoramento de performance"""
    return sentry_sdk.start_transaction(name=name, op=op)

def set_user(user_id: str, email: Optional[str] = None, username: Optional[str] = None) -> None:
    """Define informações do usuário para o contexto atual"""
    sentry_sdk.set_user({"id": user_id, "email": email, "username": username})

def set_tag(key: str, value: str) -> None:
    """Define uma tag para o escopo atual"""
    sentry_sdk.set_tag(key, value)

def set_context(name: str, data: Dict[str, Any]) -> None:
    """Adiciona contexto adicional ao escopo atual"""
    sentry_sdk.set_context(name, data)

async def track_performance(request: Request, call_next):
    """Middleware para rastrear performance de requisições HTTP"""
    with sentry_sdk.start_transaction(op="http", name=f"{request.method} {request.url.path}"):
        # Adicionar informações da requisição como tags
        sentry_sdk.set_tag("http.method", request.method)
        sentry_sdk.set_tag("http.url", str(request.url))
        
        # Adicionar headers como contexto (excluindo informações sensíveis)
        headers = dict(request.headers)
        if "authorization" in headers:
            headers["authorization"] = "[FILTERED]"
        if "cookie" in headers:
            headers["cookie"] = "[FILTERED]"
        
        sentry_sdk.set_context("request", {
            "method": request.method,
            "url": str(request.url),
            "headers": headers,
            "client": request.client.host if request.client else None,
        })
        
        # Processar a requisição
        response = await call_next(request)
        
        # Adicionar informações da resposta
        sentry_sdk.set_context("response", {
            "status_code": response.status_code,
            "headers": dict(response.headers),
        })
        
        return response