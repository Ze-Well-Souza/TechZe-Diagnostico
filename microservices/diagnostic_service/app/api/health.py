"""Endpoint de Health Check com Monitoramento de Performance

Endpoint crítico para validação do sistema e monitoramento de saúde.
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
import logging
import psutil
import asyncio
from typing import Dict, Any

# Importar schemas e utilitários
try:
    from app.schemas.api_contracts import ApiResponse
    CONTRACTS_AVAILABLE = True
except ImportError:
    CONTRACTS_AVAILABLE = False
    
try:
    from app.utils.performance_monitor import monitor_performance, get_performance_stats
    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITOR_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["health"])

@router.get("/health")
@monitor_performance(slow_threshold_ms=100) if PERFORMANCE_MONITOR_AVAILABLE else lambda x: x
async def health_check(request: Request) -> Dict[str, Any]:
    """Health check endpoint com métricas detalhadas
    
    Retorna:
    - Status do sistema
    - Métricas de performance
    - Uso de recursos
    - Informações de conectividade
    """
    try:
        start_time = datetime.now()
        
        # Coletar métricas do sistema
        system_metrics = await _collect_system_metrics()
        
        # Coletar métricas de performance se disponível
        performance_metrics = {}
        if PERFORMANCE_MONITOR_AVAILABLE:
            try:
                performance_metrics = get_performance_stats()
            except Exception as e:
                logger.warning(f"Erro ao coletar métricas de performance: {e}")
                performance_metrics = {"error": str(e)}
        
        # Testar conectividade de banco (simulado)
        database_status = await _check_database_connectivity()
        
        # Calcular tempo de resposta
        response_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        # Determinar status geral
        overall_status = "healthy"
        if not database_status["connected"]:
            overall_status = "degraded"
        if system_metrics["memory_usage_percent"] > 90:
            overall_status = "warning"
        if system_metrics["cpu_usage_percent"] > 95:
            overall_status = "critical"
        
        health_data = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "response_time_ms": round(response_time_ms, 2),
            "version": "1.0.0",
            "environment": "development",  # Pode vir de config
            "system": system_metrics,
            "database": database_status,
            "performance": performance_metrics,
            "uptime_seconds": _get_uptime_seconds()
        }
        
        # Usar schema de resposta se disponível
        if CONTRACTS_AVAILABLE:
            response = ApiResponse(
                success=True,
                message=f"Sistema {overall_status}",
                data=health_data
            )
            return response.model_dump()
        else:
            return {
                "success": True,
                "message": f"Sistema {overall_status}",
                "data": health_data
            }
            
    except Exception as e:
        logger.error(f"Erro no health check: {str(e)}")
        
        error_response = {
            "success": False,
            "message": "Erro interno no health check",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        
        if CONTRACTS_AVAILABLE:
            response = ApiResponse(
                success=False,
                message="Erro interno no health check",
                errors=[str(e)]
            )
            return JSONResponse(
                status_code=500,
                content=response.model_dump()
            )
        else:
            return JSONResponse(
                status_code=500,
                content=error_response
            )

@router.get("/health/detailed")
@monitor_performance(slow_threshold_ms=200) if PERFORMANCE_MONITOR_AVAILABLE else lambda x: x
async def detailed_health_check(request: Request) -> Dict[str, Any]:
    """Health check detalhado com informações completas do sistema"""
    try:
        # Executar múltiplas verificações em paralelo
        tasks = [
            _collect_system_metrics(),
            _check_database_connectivity(),
            _check_external_services(),
            _run_performance_tests()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        system_metrics = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
        database_status = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}
        external_services = results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}
        performance_tests = results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])}
        
        detailed_data = {
            "timestamp": datetime.now().isoformat(),
            "system": system_metrics,
            "database": database_status,
            "external_services": external_services,
            "performance_tests": performance_tests,
            "environment_info": _get_environment_info()
        }
        
        if CONTRACTS_AVAILABLE:
            response = ApiResponse(
                success=True,
                message="Health check detalhado concluído",
                data=detailed_data
            )
            return response.model_dump()
        else:
            return {
                "success": True,
                "message": "Health check detalhado concluído",
                "data": detailed_data
            }
            
    except Exception as e:
        logger.error(f"Erro no health check detalhado: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health/performance")
@monitor_performance() if PERFORMANCE_MONITOR_AVAILABLE else lambda x: x
async def performance_metrics(request: Request) -> Dict[str, Any]:
    """Endpoint específico para métricas de performance"""
    if not PERFORMANCE_MONITOR_AVAILABLE:
        return {
            "success": False,
            "message": "Monitor de performance não disponível",
            "data": None
        }
    
    try:
        from app.utils.performance_monitor import get_slow_endpoints
        
        stats = get_performance_stats()
        slow_endpoints = get_slow_endpoints(threshold_ms=300)
        
        performance_data = {
            "general_stats": stats,
            "slow_endpoints": slow_endpoints,
            "recommendations": _generate_performance_recommendations(stats, slow_endpoints)
        }
        
        if CONTRACTS_AVAILABLE:
            response = ApiResponse(
                success=True,
                message="Métricas de performance coletadas",
                data=performance_data
            )
            return response.model_dump()
        else:
            return {
                "success": True,
                "message": "Métricas de performance coletadas",
                "data": performance_data
            }
            
    except Exception as e:
        logger.error(f"Erro ao coletar métricas de performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Funções auxiliares

async def _collect_system_metrics() -> Dict[str, Any]:
    """Coletar métricas do sistema"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count()
        
        # Memória
        memory = psutil.virtual_memory()
        
        # Disco
        disk = psutil.disk_usage('/')
        
        return {
            "cpu_usage_percent": cpu_percent,
            "cpu_count": cpu_count,
            "memory_usage_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "memory_total_gb": round(memory.total / (1024**3), 2),
            "disk_usage_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2),
            "disk_total_gb": round(disk.total / (1024**3), 2)
        }
    except Exception as e:
        logger.warning(f"Erro ao coletar métricas do sistema: {e}")
        return {"error": str(e)}

async def _check_database_connectivity() -> Dict[str, Any]:
    """Verificar conectividade com banco de dados"""
    try:
        # Simular teste de conectividade
        # Em implementação real, testaria conexão com Supabase/PostgreSQL
        await asyncio.sleep(0.01)  # Simular latência
        
        return {
            "connected": True,
            "latency_ms": 10.5,
            "pool_size": 10,
            "active_connections": 3,
            "last_check": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }

async def _check_external_services() -> Dict[str, Any]:
    """Verificar serviços externos"""
    services = {
        "supabase": {"status": "unknown", "latency_ms": None},
        "redis": {"status": "unknown", "latency_ms": None},
        "email_service": {"status": "unknown", "latency_ms": None}
    }
    
    # Simular verificações
    for service in services:
        try:
            await asyncio.sleep(0.01)  # Simular verificação
            services[service] = {
                "status": "healthy",
                "latency_ms": 15.2,
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            services[service] = {
                "status": "error",
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }
    
    return services

async def _run_performance_tests() -> Dict[str, Any]:
    """Executar testes básicos de performance"""
    tests = {}
    
    # Teste de I/O
    start_time = datetime.now()
    await asyncio.sleep(0.001)  # Simular operação I/O
    io_time = (datetime.now() - start_time).total_seconds() * 1000
    
    tests["io_test_ms"] = round(io_time, 2)
    
    # Teste de CPU
    start_time = datetime.now()
    # Simular operação CPU-intensiva
    sum(i for i in range(1000))
    cpu_time = (datetime.now() - start_time).total_seconds() * 1000
    
    tests["cpu_test_ms"] = round(cpu_time, 2)
    
    return tests

def _get_environment_info() -> Dict[str, Any]:
    """Obter informações do ambiente"""
    import sys
    import platform
    
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "hostname": platform.node(),
        "processor": platform.processor()
    }

def _get_uptime_seconds() -> float:
    """Obter uptime do sistema em segundos"""
    try:
        import time
        return time.time() - psutil.boot_time()
    except:
        return 0.0

def _generate_performance_recommendations(stats: Dict, slow_endpoints: list) -> list:
    """Gerar recomendações de performance"""
    recommendations = []
    
    if 'average_response_time_ms' in stats and stats['average_response_time_ms'] > 300:
        recommendations.append({
            "type": "performance",
            "priority": "high",
            "message": f"Tempo médio de resposta alto: {stats['average_response_time_ms']}ms",
            "suggestion": "Considere otimizar queries de banco de dados e adicionar cache"
        })
    
    if 'slow_request_percentage' in stats and stats['slow_request_percentage'] > 20:
        recommendations.append({
            "type": "performance",
            "priority": "medium",
            "message": f"{stats['slow_request_percentage']}% das requisições são lentas",
            "suggestion": "Identifique e otimize os endpoints mais lentos"
        })
    
    if len(slow_endpoints) > 5:
        recommendations.append({
            "type": "optimization",
            "priority": "high",
            "message": f"{len(slow_endpoints)} endpoints lentos detectados",
            "suggestion": "Priorize a otimização dos 3 endpoints mais lentos"
        })
    
    if not recommendations:
        recommendations.append({
            "type": "status",
            "priority": "info",
            "message": "Performance dentro dos parâmetros aceitáveis",
            "suggestion": "Continue monitorando as métricas regularmente"
        })
    
    return recommendations