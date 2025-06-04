"""
Rate Limiting avançado para FastAPI com Redis
"""
import redis
import time
import json
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

logger = logging.getLogger(__name__)


class AdvancedRateLimiter:
    """Rate Limiter avançado com Redis backend"""
    
    def __init__(self, redis_url: Optional[str] = None):
        """
        Inicializa o rate limiter
        
        Args:
            redis_url: URL do Redis. Se None, usa rate limiting em memória
        """
        self.redis_client = None
        self.memory_store = {}
        
        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Testa a conexão
                self.redis_client.ping()
                logger.info("Redis conectado para rate limiting")
            except Exception as e:
                logger.warning(f"Falha ao conectar Redis: {e}. Usando rate limiting em memória")
                self.redis_client = None
    
    def _get_key(self, identifier: str, endpoint: str, window: str) -> str:
        """Gera chave única para o rate limit"""
        return f"rate_limit:{identifier}:{endpoint}:{window}"
    
    def _get_current_window(self, window_seconds: int) -> str:
        """Retorna a janela de tempo atual"""
        return str(int(time.time()) // window_seconds)
    
    def check_rate_limit(
        self, 
        identifier: str, 
        endpoint: str, 
        limit: int, 
        window_seconds: int = 60
    ) -> Dict[str, Any]:
        """
        Verifica se o rate limit foi excedido
        
        Args:
            identifier: Identificador único (IP, user_id, etc.)
            endpoint: Nome do endpoint
            limit: Número máximo de requests
            window_seconds: Janela de tempo em segundos
            
        Returns:
            Dict com informações do rate limit
        """
        window = self._get_current_window(window_seconds)
        key = self._get_key(identifier, endpoint, window)
        
        if self.redis_client:
            return self._check_redis_rate_limit(key, limit, window_seconds)
        else:
            return self._check_memory_rate_limit(key, limit, window_seconds)
    
    def _check_redis_rate_limit(self, key: str, limit: int, window_seconds: int) -> Dict[str, Any]:
        """Rate limiting usando Redis"""
        try:
            pipe = self.redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, window_seconds)
            results = pipe.execute()
            
            current_requests = results[0]
            
            return {
                "allowed": current_requests <= limit,
                "current_requests": current_requests,
                "limit": limit,
                "reset_time": int(time.time()) + window_seconds,
                "retry_after": window_seconds if current_requests > limit else 0
            }
        except Exception as e:
            logger.error(f"Erro no Redis rate limiting: {e}")
            # Fallback para memória
            return self._check_memory_rate_limit(key, limit, window_seconds)
    
    def _check_memory_rate_limit(self, key: str, limit: int, window_seconds: int) -> Dict[str, Any]:
        """Rate limiting usando memória local"""
        current_time = time.time()
        
        if key not in self.memory_store:
            self.memory_store[key] = {
                "count": 1,
                "reset_time": current_time + window_seconds
            }
            return {
                "allowed": True,
                "current_requests": 1,
                "limit": limit,
                "reset_time": int(current_time + window_seconds),
                "retry_after": 0
            }
        
        entry = self.memory_store[key]
        
        # Reset se a janela expirou
        if current_time >= entry["reset_time"]:
            entry["count"] = 1
            entry["reset_time"] = current_time + window_seconds
        else:
            entry["count"] += 1
        
        return {
            "allowed": entry["count"] <= limit,
            "current_requests": entry["count"],
            "limit": limit,
            "reset_time": int(entry["reset_time"]),
            "retry_after": int(entry["reset_time"] - current_time) if entry["count"] > limit else 0
        }


# Configurações de rate limiting por endpoint
RATE_LIMIT_CONFIG = {
    "default": {"limit": 100, "window": 60},  # 100 requests por minuto
    "diagnostic_quick": {"limit": 10, "window": 60},  # 10 diagnósticos rápidos por minuto
    "diagnostic_full": {"limit": 5, "window": 300},  # 5 diagnósticos completos por 5 minutos
    "auth_login": {"limit": 5, "window": 300},  # 5 tentativas de login por 5 minutos
    "auth_register": {"limit": 3, "window": 3600},  # 3 registros por hora
    "reports": {"limit": 20, "window": 60},  # 20 relatórios por minuto
}


def get_rate_limit_key(request: Request) -> str:
    """
    Gera chave para rate limiting baseada no usuário ou IP
    """
    # Tenta pegar o user_id do token JWT se disponível
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"
    
    # Fallback para IP
    return f"ip:{get_remote_address(request)}"


def create_rate_limiter(redis_url: Optional[str] = None) -> Limiter:
    """
    Cria instância do rate limiter
    """
    def key_func(request: Request):
        return get_rate_limit_key(request)
    
    return Limiter(key_func=key_func)


# Middleware personalizado para rate limiting avançado
class RateLimitMiddleware:
    """Middleware personalizado para rate limiting avançado"""
    
    def __init__(self, rate_limiter: AdvancedRateLimiter):
        self.rate_limiter = rate_limiter
    
    async def __call__(self, request: Request, call_next):
        """Processa o rate limiting"""
        # Identifica o endpoint
        endpoint = request.url.path.replace("/", "_").strip("_")
        if not endpoint:
            endpoint = "root"
        
        # Pega configuração do rate limit
        config = RATE_LIMIT_CONFIG.get(endpoint, RATE_LIMIT_CONFIG["default"])
        
        # Gera identificador
        identifier = get_rate_limit_key(request)
        
        # Verifica rate limit
        rate_limit_info = self.rate_limiter.check_rate_limit(
            identifier=identifier,
            endpoint=endpoint,
            limit=config["limit"],
            window_seconds=config["window"]
        )
        
        # Adiciona headers de rate limit
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, rate_limit_info["limit"] - rate_limit_info["current_requests"])
        )
        response.headers["X-RateLimit-Reset"] = str(rate_limit_info["reset_time"])
        
        # Bloqueia se excedeu o limite
        if not rate_limit_info["allowed"]:
            response.headers["Retry-After"] = str(rate_limit_info["retry_after"])
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": rate_limit_info["limit"],
                    "current_requests": rate_limit_info["current_requests"],
                    "reset_time": rate_limit_info["reset_time"],
                    "retry_after": rate_limit_info["retry_after"]
                }
            )
        
        return response


def setup_rate_limiting(app, redis_url: Optional[str] = None):
    """
    Configura rate limiting na aplicação FastAPI
    """
    # Rate limiter básico com slowapi
    limiter = create_rate_limiter(redis_url)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Rate limiter avançado
    advanced_limiter = AdvancedRateLimiter(redis_url)
    rate_limit_middleware = RateLimitMiddleware(advanced_limiter)
    
    # Adiciona middleware (comentado por enquanto para não quebrar)
    # app.middleware("http")(rate_limit_middleware)
    
    logger.info("Rate limiting configurado")
    return limiter, advanced_limiter