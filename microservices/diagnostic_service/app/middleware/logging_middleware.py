"""Middleware para logging estruturado de requisições HTTP."""

import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

from app.core.logging import (
    get_logger,
    log_request,
    set_request_context,
    clear_request_context,
    generate_request_id
)

logger = get_logger(__name__, "middleware")


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging estruturado de requisições HTTP."""
    
    def __init__(self, app, exclude_paths: list = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or ["/health", "/metrics", "/docs", "/openapi.json"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Processa a requisição e registra logs estruturados."""
        
        # Gerar ID único para a requisição
        request_id = generate_request_id()
        
        # Extrair informações da requisição
        method = request.method
        path = request.url.path
        query_params = str(request.query_params) if request.query_params else None
        user_agent = request.headers.get("user-agent")
        ip_address = self._get_client_ip(request)
        
        # Extrair user_id se disponível (assumindo que está no estado da requisição)
        user_id = getattr(request.state, "user_id", None)
        session_id = getattr(request.state, "session_id", None)
        
        # Configurar contexto da requisição
        set_request_context(request_id, user_id, session_id)
        
        # Adicionar informações ao estado da requisição
        request.state.request_id = request_id
        request.state.start_time = time.time()
        
        # Log de início da requisição (apenas para paths importantes)
        if path not in self.exclude_paths:
            logger.bind(
                request_id=request_id,
                method=method,
                path=path,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                query_params=query_params
            ).info(f"Request started: {method} {path}")
        
        try:
            # Processar a requisição
            response = await call_next(request)
            
            # Calcular duração
            duration = time.time() - request.state.start_time
            
            # Log estruturado da requisição (apenas para paths importantes)
            if path not in self.exclude_paths:
                log_request(
                    method=method,
                    path=path,
                    status_code=response.status_code,
                    duration=duration,
                    user_id=user_id,
                    request_id=request_id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    query_params=query_params,
                    response_size=self._get_response_size(response)
                )
            
            # Adicionar headers de rastreamento
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calcular duração mesmo em caso de erro
            duration = time.time() - request.state.start_time
            
            # Log de erro estruturado
            logger.bind(
                request_id=request_id,
                method=method,
                path=path,
                user_id=user_id,
                ip_address=ip_address,
                duration_ms=round(duration * 1000, 2),
                error_type=type(e).__name__,
                error_message=str(e)
            ).error(f"Request failed: {method} {path} - {type(e).__name__}: {str(e)}")
            
            raise
        
        finally:
            # Limpar contexto da requisição
            clear_request_context()
    
    def _get_client_ip(self, request: Request) -> str:
        """Extrai o IP do cliente considerando proxies."""
        # Verificar headers de proxy
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # IP direto
        if hasattr(request.client, "host"):
            return request.client.host
        
        return "unknown"
    
    def _get_response_size(self, response: Response) -> int:
        """Calcula o tamanho da resposta em bytes."""
        try:
            if hasattr(response, "body"):
                if isinstance(response.body, bytes):
                    return len(response.body)
                elif isinstance(response.body, str):
                    return len(response.body.encode('utf-8'))
            
            # Para StreamingResponse, não podemos calcular facilmente
            if isinstance(response, StreamingResponse):
                return 0
            
            # Tentar obter do header Content-Length
            content_length = response.headers.get("content-length")
            if content_length:
                return int(content_length)
            
        except Exception:
            pass
        
        return 0


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware para injetar contexto de usuário na requisição."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Injeta contexto de usuário na requisição."""
        
        # Extrair informações de autenticação (exemplo)
        # Isso deve ser adaptado conforme o sistema de autenticação usado
        authorization = request.headers.get("authorization")
        
        if authorization and authorization.startswith("Bearer "):
            try:
                # Aqui você decodificaria o token JWT e extrairia o user_id
                # Por enquanto, vamos simular
                token = authorization.split(" ")[1]
                # user_id = decode_jwt_token(token).get("user_id")
                # session_id = decode_jwt_token(token).get("session_id")
                
                # Simulação - remover quando implementar JWT real
                user_id = "user_123"  # Extrair do token real
                session_id = "session_456"  # Extrair do token real
                
                # Adicionar ao estado da requisição
                request.state.user_id = user_id
                request.state.session_id = session_id
                
            except Exception as e:
                logger.warning(f"Failed to decode authorization token: {e}")
        
        return await call_next(request)