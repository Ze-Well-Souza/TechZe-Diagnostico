"""Middleware de segurança para TechZe Diagnostic API

Implementa headers de segurança obrigatórios e configurações CORS
para resolver problemas críticos identificados na análise.
"""

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para adicionar headers de segurança obrigatórios"""
    
    def __init__(self, app, enable_hsts: bool = True):
        super().__init__(app)
        self.enable_hsts = enable_hsts
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Processar requisição
        response = await call_next(request)
        
        # Adicionar headers de segurança obrigatórios
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            ),
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=()"
            )
        }
        
        # HSTS apenas em HTTPS
        if self.enable_hsts and request.url.scheme == "https":
            security_headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Aplicar headers
        for header, value in security_headers.items():
            response.headers[header] = value
            
        # Header de performance para debugging
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log de performance se exceder threshold
        if process_time > 0.5:
            logger.warning(
                f"⚠️ SLOW REQUEST: {request.method} {request.url.path} took {process_time:.3f}s"
            )
            
        return response


def setup_security_middleware(app: FastAPI, environment: str = "production") -> None:
    """Configurar todos os middlewares de segurança
    
    Args:
        app: Instância do FastAPI
        environment: Ambiente atual (development, staging, production)
    """
    
    # Configurações baseadas no ambiente
    if environment == "development":
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:3001", 
            "http://127.0.0.1:3000",
            "http://127.0.0.1:3001"
        ]
        allow_credentials = True
        enable_hsts = False
    elif environment == "staging":
        allowed_origins = [
            "https://staging.techze.com.br",
            "https://staging-app.techze.com.br"
        ]
        allow_credentials = True
        enable_hsts = True
    else:  # production
        allowed_origins = [
            "https://techze.com.br",
            "https://app.techze.com.br",
            "https://www.techze.com.br"
        ]
        allow_credentials = True
        enable_hsts = True
    
    # CORS Middleware - DEVE ser o primeiro
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-API-Key",
            "X-Client-Version",
            "Cache-Control"
        ],
        expose_headers=[
            "X-Total-Count",
            "X-Page-Count", 
            "X-Process-Time",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset"
        ],
        max_age=86400  # 24 horas
    )
    
    # Security Headers Middleware
    app.add_middleware(SecurityHeadersMiddleware, enable_hsts=enable_hsts)
    
    # Trusted Host Middleware (apenas em produção)
    if environment == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=[
                "techze.com.br",
                "app.techze.com.br", 
                "www.techze.com.br",
                "api.techze.com.br"
            ]
        )
    
    logger.info(f"✅ Security middleware configured for {environment} environment")
    logger.info(f"✅ CORS origins: {allowed_origins}")
    logger.info(f"✅ HSTS enabled: {enable_hsts}")


def get_security_headers_status() -> dict:
    """Retorna status dos headers de segurança para health check"""
    return {
        "security_headers": {
            "x_content_type_options": "implemented",
            "x_frame_options": "implemented", 
            "x_xss_protection": "implemented",
            "strict_transport_security": "conditional",
            "content_security_policy": "implemented",
            "referrer_policy": "implemented",
            "permissions_policy": "implemented"
        },
        "cors": {
            "configured": True,
            "credentials_allowed": True,
            "methods_allowed": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
        },
        "status": "active"
    }