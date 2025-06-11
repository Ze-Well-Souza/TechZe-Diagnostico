"""
Sistema Avançado de Health Checks para TechZe Diagnostic
Verifica estado detalhado de todos os componentes críticos do sistema
"""

import asyncio
import time
import psutil
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Status de saúde dos componentes"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class ComponentHealth:
    """Status de saúde de um componente específico"""
    name: str
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    last_check: datetime
    response_time_ms: float

class HealthCheckRegistry:
    """Registry para health checks customizados"""
    
    def __init__(self):
        self._checks = {}
        self._last_results = {}
        
    def register(self, name: str, check_func):
        """Registra um health check customizado"""
        self._checks[name] = check_func
        
    async def run_check(self, name: str) -> ComponentHealth:
        """Executa um health check específico"""
        if name not in self._checks:
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNKNOWN,
                message=f"Health check '{name}' não encontrado",
                details={},
                last_check=datetime.now(timezone.utc),
                response_time_ms=0.0
            )
            
        start_time = time.time()
        try:
            result = await self._checks[name]()
            response_time = (time.time() - start_time) * 1000
            
            if isinstance(result, ComponentHealth):
                result.response_time_ms = response_time
                result.last_check = datetime.now(timezone.utc)
                self._last_results[name] = result
                return result
            else:
                return ComponentHealth(
                    name=name,
                    status=HealthStatus.HEALTHY if result else HealthStatus.CRITICAL,
                    message="OK" if result else "Falha",
                    details={},
                    last_check=datetime.now(timezone.utc),
                    response_time_ms=response_time
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            logger.error(f"Erro no health check {name}: {e}")
            
            result = ComponentHealth(
                name=name,
                status=HealthStatus.CRITICAL,
                message=f"Erro: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.now(timezone.utc),
                response_time_ms=response_time
            )
            self._last_results[name] = result
            return result

# Registry global
health_registry = HealthCheckRegistry()

class AdvancedHealthChecker:
    """Sistema avançado de health checks"""
    
    def __init__(self):
        self.cache_results = {}
        self.cache_ttl = 30  # 30 segundos de cache
        
    async def check_system_resources(self) -> ComponentHealth:
        """Verifica recursos do sistema (CPU, Memória, Disco)"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memória
            memory = psutil.virtual_memory()
            
            # Disco
            disk = psutil.disk_usage('/')
            
            # Processos
            process_count = len(psutil.pids())
            
            # Determina status baseado nos recursos
            status = HealthStatus.HEALTHY
            warnings = []
            
            if cpu_percent > 80:
                status = HealthStatus.WARNING
                warnings.append(f"CPU alto: {cpu_percent}%")
            
            if memory.percent > 85:
                status = HealthStatus.WARNING if status != HealthStatus.CRITICAL else status
                warnings.append(f"Memória alta: {memory.percent}%")
                
            if disk.percent > 90:
                status = HealthStatus.CRITICAL
                warnings.append(f"Disco cheio: {disk.percent}%")
                
            if process_count > 500:
                status = HealthStatus.WARNING if status != HealthStatus.CRITICAL else status
                warnings.append(f"Muitos processos: {process_count}")
            
            return ComponentHealth(
                name="system_resources",
                status=status,
                message="OK" if not warnings else "; ".join(warnings),
                details={
                    "cpu": {
                        "percent": cpu_percent,
                        "count": cpu_count,
                        "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                    },
                    "memory": {
                        "total_gb": round(memory.total / (1024**3), 2),
                        "available_gb": round(memory.available / (1024**3), 2),
                        "percent_used": memory.percent
                    },
                    "disk": {
                        "total_gb": round(disk.total / (1024**3), 2),
                        "free_gb": round(disk.free / (1024**3), 2),
                        "percent_used": disk.percent
                    },
                    "processes": {
                        "count": process_count
                    }
                },
                last_check=datetime.now(timezone.utc),
                response_time_ms=0.0
            )
            
        except Exception as e:
            return ComponentHealth(
                name="system_resources",
                status=HealthStatus.CRITICAL,
                message=f"Erro ao verificar recursos: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.now(timezone.utc),
                response_time_ms=0.0
            )
    
    async def check_database_connection(self) -> ComponentHealth:
        """Verifica conexão com banco de dados"""
        try:
            start_time = time.time()
            
            if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
                return ComponentHealth(
                    name="database",
                    status=HealthStatus.CRITICAL,
                    message="Credenciais do Supabase não configuradas",
                    details={
                        "supabase_url_configured": bool(settings.SUPABASE_URL),
                        "supabase_key_configured": bool(settings.SUPABASE_ANON_KEY)
                    },
                    last_check=datetime.now(timezone.utc),
                    response_time_ms=0.0
                )
            
            # Verifica conectividade básica via HTTP
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(
                        f"{settings.SUPABASE_URL}/rest/v1/",
                        headers={"apikey": settings.SUPABASE_ANON_KEY},
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as response:
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status == 200:
                            return ComponentHealth(
                                name="database",
                                status=HealthStatus.HEALTHY,
                                message="Conexão OK",
                                details={
                                    "url": settings.SUPABASE_URL,
                                    "status_code": response.status,
                                    "response_time_ms": response_time
                                },
                                last_check=datetime.now(timezone.utc),
                                response_time_ms=response_time
                            )
                        else:
                            return ComponentHealth(
                                name="database",
                                status=HealthStatus.WARNING,
                                message=f"Status HTTP: {response.status}",
                                details={
                                    "url": settings.SUPABASE_URL,
                                    "status_code": response.status,
                                    "response_time_ms": response_time
                                },
                                last_check=datetime.now(timezone.utc),
                                response_time_ms=response_time
                            )
                            
                except asyncio.TimeoutError:
                    return ComponentHealth(
                        name="database",
                        status=HealthStatus.CRITICAL,
                        message="Timeout na conexão",
                        details={
                            "url": settings.SUPABASE_URL,
                            "timeout": "5s"
                        },
                        last_check=datetime.now(timezone.utc),
                        response_time_ms=5000.0
                    )
                    
        except Exception as e:
            return ComponentHealth(
                name="database",
                status=HealthStatus.CRITICAL,
                message=f"Erro na conexão: {str(e)}",
                details={"error": str(e)},
                last_check=datetime.now(timezone.utc),
                response_time_ms=0.0
            )

    async def get_comprehensive_health(self) -> Dict[str, Any]:
        """Executa todos os health checks e retorna status completo"""
        
        cache_key = "comprehensive_health"
        if cache_key in self.cache_results:
            cache_time, cached_result = self.cache_results[cache_key]
            if time.time() - cache_time < self.cache_ttl:
                return cached_result
        
        start_time = time.time()
        
        # Executa todos os checks em paralelo
        checks = await asyncio.gather(
            self.check_system_resources(),
            self.check_database_connection(),
            return_exceptions=True
        )
        
        # Processa resultados
        components = {}
        overall_status = HealthStatus.HEALTHY
        critical_count = 0
        warning_count = 0
        
        for check in checks:
            if isinstance(check, Exception):
                continue
                
            components[check.name] = asdict(check)
            
            if check.status == HealthStatus.CRITICAL:
                critical_count += 1
                overall_status = HealthStatus.CRITICAL
            elif check.status == HealthStatus.WARNING:
                warning_count += 1
                if overall_status != HealthStatus.CRITICAL:
                    overall_status = HealthStatus.WARNING
        
        total_time = (time.time() - start_time) * 1000
        
        result = {
            "status": overall_status.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "response_time_ms": total_time,
            "summary": {
                "total_components": len(components),
                "healthy_components": len([c for c in components.values() 
                                         if c["status"] == HealthStatus.HEALTHY.value]),
                "warning_components": warning_count,
                "critical_components": critical_count
            },
            "components": components,
            "metadata": {
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "uptime_seconds": time.time() - start_time
            }
        }
        
        # Cache do resultado
        self.cache_results[cache_key] = (time.time(), result)
        
        return result

# Instância global
health_checker = AdvancedHealthChecker()
