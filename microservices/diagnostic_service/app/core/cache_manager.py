"""
Sistema de Cache Avançado - Semana 2
Implementa cache Redis inteligente com fallback para memória
"""
import asyncio
import json
import logging
import pickle
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class CacheStrategy(Enum):
    """Estratégias de cache"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    FIFO = "fifo"  # First In First Out


@dataclass
class CacheEntry:
    """Entrada do cache"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl_seconds: Optional[int] = None
    
    @property
    def is_expired(self) -> bool:
        """Verifica se a entrada expirou"""
        if self.ttl_seconds is None:
            return False
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl_seconds)
    
    @property
    def age_seconds(self) -> float:
        """Idade da entrada em segundos"""
        return (datetime.now() - self.created_at).total_seconds()


class MemoryCache:
    """Cache em memória com diferentes estratégias"""
    
    def __init__(self, max_size: int = 1000, strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.strategy = strategy
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []  # Para LRU
        
    def _update_access(self, key: str):
        """Atualiza informações de acesso"""
        if key in self.cache:
            entry = self.cache[key]
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            
            # Atualiza ordem de acesso para LRU
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
    
    def _evict_if_needed(self):
        """Remove entradas se necessário"""
        # Remove entradas expiradas primeiro
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired]
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
        
        # Se ainda excede o tamanho máximo, aplica estratégia
        while len(self.cache) >= self.max_size:
            if self.strategy == CacheStrategy.LRU:
                # Remove o menos recentemente usado
                if self.access_order:
                    key_to_remove = self.access_order.pop(0)
                    if key_to_remove in self.cache:
                        del self.cache[key_to_remove]
            
            elif self.strategy == CacheStrategy.LFU:
                # Remove o menos frequentemente usado
                if self.cache:
                    key_to_remove = min(self.cache.keys(), 
                                      key=lambda k: self.cache[k].access_count)
                    del self.cache[key_to_remove]
                    if key_to_remove in self.access_order:
                        self.access_order.remove(key_to_remove)
            
            elif self.strategy == CacheStrategy.FIFO:
                # Remove o mais antigo
                if self.cache:
                    key_to_remove = min(self.cache.keys(), 
                                      key=lambda k: self.cache[k].created_at)
                    del self.cache[key_to_remove]
                    if key_to_remove in self.access_order:
                        self.access_order.remove(key_to_remove)
            
            else:  # TTL
                # Remove o mais antigo (já removeu expirados acima)
                if self.cache:
                    key_to_remove = min(self.cache.keys(), 
                                      key=lambda k: self.cache[k].created_at)
                    del self.cache[key_to_remove]
                    if key_to_remove in self.access_order:
                        self.access_order.remove(key_to_remove)
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Verifica se expirou
        if entry.is_expired:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            return None
        
        self._update_access(key)
        return entry.value
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Define valor no cache"""
        self._evict_if_needed()
        
        now = datetime.now()
        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            last_accessed=now,
            access_count=1,
            ttl_seconds=ttl_seconds
        )
        
        self.cache[key] = entry
        if key not in self.access_order:
            self.access_order.append(key)
    
    def delete(self, key: str) -> bool:
        """Remove entrada do cache"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            return True
        return False
    
    def clear(self):
        """Limpa todo o cache"""
        self.cache.clear()
        self.access_order.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_entries = len(self.cache)
        expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired)
        
        if total_entries > 0:
            avg_age = sum(entry.age_seconds for entry in self.cache.values()) / total_entries
            avg_access_count = sum(entry.access_count for entry in self.cache.values()) / total_entries
        else:
            avg_age = 0
            avg_access_count = 0
        
        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "max_size": self.max_size,
            "utilization_percent": (total_entries / self.max_size) * 100,
            "strategy": self.strategy.value,
            "avg_age_seconds": avg_age,
            "avg_access_count": avg_access_count
        }


class RedisCache:
    """Cache Redis com fallback para memória"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_client = None
        self.memory_fallback = MemoryCache(max_size=500)
        self.redis_available = False
        
        if redis_url:
            try:
                import redis
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Testa conexão
                self.redis_client.ping()
                self.redis_available = True
                logger.info("✅ Redis cache conectado")
            except Exception as e:
                logger.warning(f"⚠️ Redis não disponível, usando cache em memória: {e}")
                self.redis_available = False
    
    def _serialize_value(self, value: Any) -> str:
        """Serializa valor para armazenamento"""
        try:
            return json.dumps(value, default=str)
        except (TypeError, ValueError):
            # Fallback para pickle se JSON falhar
            return pickle.dumps(value).hex()
    
    def _deserialize_value(self, serialized: str) -> Any:
        """Deserializa valor do armazenamento"""
        try:
            return json.loads(serialized)
        except (json.JSONDecodeError, ValueError):
            # Tenta pickle se JSON falhar
            try:
                return pickle.loads(bytes.fromhex(serialized))
            except Exception:
                return serialized
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if self.redis_available and self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value is not None:
                    return self._deserialize_value(value)
            except Exception as e:
                logger.warning(f"Erro ao acessar Redis, usando fallback: {e}")
                self.redis_available = False
        
        # Fallback para memória
        return self.memory_fallback.get(key)
    
    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        """Define valor no cache"""
        serialized_value = self._serialize_value(value)
        
        if self.redis_available and self.redis_client:
            try:
                if ttl_seconds:
                    self.redis_client.setex(key, ttl_seconds, serialized_value)
                else:
                    self.redis_client.set(key, serialized_value)
                return
            except Exception as e:
                logger.warning(f"Erro ao escrever no Redis, usando fallback: {e}")
                self.redis_available = False
        
        # Fallback para memória
        self.memory_fallback.set(key, value, ttl_seconds)
    
    async def delete(self, key: str) -> bool:
        """Remove entrada do cache"""
        deleted = False
        
        if self.redis_available and self.redis_client:
            try:
                deleted = bool(self.redis_client.delete(key))
            except Exception as e:
                logger.warning(f"Erro ao deletar do Redis: {e}")
                self.redis_available = False
        
        # Também remove do fallback
        memory_deleted = self.memory_fallback.delete(key)
        
        return deleted or memory_deleted
    
    async def clear(self):
        """Limpa todo o cache"""
        if self.redis_available and self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                logger.warning(f"Erro ao limpar Redis: {e}")
        
        self.memory_fallback.clear()
    
    async def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        stats = {
            "redis_available": self.redis_available,
            "memory_fallback": self.memory_fallback.get_stats()
        }
        
        if self.redis_available and self.redis_client:
            try:
                redis_info = self.redis_client.info()
                stats["redis"] = {
                    "used_memory": redis_info.get("used_memory", 0),
                    "used_memory_human": redis_info.get("used_memory_human", "0B"),
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "total_commands_processed": redis_info.get("total_commands_processed", 0),
                    "keyspace_hits": redis_info.get("keyspace_hits", 0),
                    "keyspace_misses": redis_info.get("keyspace_misses", 0)
                }
                
                # Calcula hit rate
                hits = stats["redis"]["keyspace_hits"]
                misses = stats["redis"]["keyspace_misses"]
                total = hits + misses
                stats["redis"]["hit_rate_percent"] = (hits / total * 100) if total > 0 else 0
                
            except Exception as e:
                logger.warning(f"Erro ao obter stats do Redis: {e}")
                stats["redis"] = {"error": str(e)}
        
        return stats


class CacheManager:
    """Gerenciador principal de cache"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_cache = RedisCache(redis_url)
        self.cache_patterns = {
            "diagnostic_results": {"ttl": 3600, "prefix": "diag:"},
            "system_metrics": {"ttl": 300, "prefix": "metrics:"},
            "user_sessions": {"ttl": 1800, "prefix": "session:"},
            "api_responses": {"ttl": 600, "prefix": "api:"},
            "reports": {"ttl": 7200, "prefix": "report:"}
        }
        
        # Estatísticas
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
    
    def _get_cache_key(self, pattern: str, key: str) -> str:
        """Gera chave de cache com padrão"""
        if pattern in self.cache_patterns:
            prefix = self.cache_patterns[pattern]["prefix"]
            return f"{prefix}{key}"
        return key
    
    def _hash_key(self, data: Any) -> str:
        """Gera hash para chave complexa"""
        if isinstance(data, dict):
            # Ordena chaves para hash consistente
            sorted_data = json.dumps(data, sort_keys=True)
        else:
            sorted_data = str(data)
        
        return hashlib.md5(sorted_data.encode()).hexdigest()
    
    async def get(self, pattern: str, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        cache_key = self._get_cache_key(pattern, key)
        value = await self.redis_cache.get(cache_key)
        
        if value is not None:
            self.stats["hits"] += 1
            logger.debug(f"Cache HIT: {cache_key}")
        else:
            self.stats["misses"] += 1
            logger.debug(f"Cache MISS: {cache_key}")
        
        return value
    
    async def set(self, pattern: str, key: str, value: Any, ttl_override: Optional[int] = None):
        """Define valor no cache"""
        cache_key = self._get_cache_key(pattern, key)
        
        # Usa TTL do padrão ou override
        ttl = ttl_override
        if ttl is None and pattern in self.cache_patterns:
            ttl = self.cache_patterns[pattern]["ttl"]
        
        await self.redis_cache.set(cache_key, value, ttl)
        self.stats["sets"] += 1
        logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")
    
    async def delete(self, pattern: str, key: str) -> bool:
        """Remove entrada do cache"""
        cache_key = self._get_cache_key(pattern, key)
        deleted = await self.redis_cache.delete(cache_key)
        
        if deleted:
            self.stats["deletes"] += 1
            logger.debug(f"Cache DELETE: {cache_key}")
        
        return deleted
    
    async def get_or_set(self, pattern: str, key: str, factory_func, ttl_override: Optional[int] = None) -> Any:
        """Obtém do cache ou executa função e armazena resultado"""
        value = await self.get(pattern, key)
        
        if value is not None:
            return value
        
        # Executa função para obter valor
        if asyncio.iscoroutinefunction(factory_func):
            value = await factory_func()
        else:
            value = factory_func()
        
        # Armazena no cache
        await self.set(pattern, key, value, ttl_override)
        
        return value
    
    async def invalidate_pattern(self, pattern: str):
        """Invalida todas as entradas de um padrão"""
        if pattern in self.cache_patterns:
            prefix = self.cache_patterns[pattern]["prefix"]
            
            if self.redis_cache.redis_available and self.redis_cache.redis_client:
                try:
                    # Lista todas as chaves com o prefixo
                    keys = self.redis_cache.redis_client.keys(f"{prefix}*")
                    if keys:
                        self.redis_cache.redis_client.delete(*keys)
                        logger.info(f"Invalidadas {len(keys)} entradas do padrão {pattern}")
                except Exception as e:
                    logger.warning(f"Erro ao invalidar padrão {pattern}: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas completas do cache"""
        cache_stats = await self.redis_cache.get_stats()
        
        # Calcula hit rate
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "application_stats": {
                **self.stats,
                "hit_rate_percent": hit_rate,
                "total_requests": total_requests
            },
            "cache_backend": cache_stats,
            "patterns": {
                pattern: {
                    "ttl_seconds": config["ttl"],
                    "prefix": config["prefix"]
                }
                for pattern, config in self.cache_patterns.items()
            }
        }
    
    async def warm_up_cache(self):
        """Aquece o cache com dados frequentemente acessados"""
        logger.info("🔥 Iniciando aquecimento do cache...")
        
        try:
            # Aqui você pode implementar lógica para pré-carregar dados importantes
            # Por exemplo, métricas do sistema, configurações, etc.
            
            # Exemplo: cache de configurações
            await self.set("api_responses", "system_config", {
                "version": "1.0.0",
                "features": ["diagnostics", "monitoring", "alerts"]
            })
            
            logger.info("✅ Cache aquecido com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao aquecer cache: {e}")


# Instância global do gerenciador de cache
cache_manager = CacheManager()