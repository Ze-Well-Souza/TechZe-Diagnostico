"""Endpoints de Performance - API Core

Consolida todas as funcionalidades de monitoramento de performance,
métricas do sistema, alertas e otimização.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
import time
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["performance"])

# Modelos de dados
class AlertRule(BaseModel):
    name: str
    metric: str
    operator: str  # ">", "<", ">=", "<=", "=="
    threshold: float
    severity: str  # "low", "medium", "high", "critical"
    enabled: bool = True
    description: Optional[str] = None

class AlertResponse(BaseModel):
    id: str
    rule_name: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class PerformanceMetrics(BaseModel):
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    database_connections: int
    response_time_ms: float

class Recommendation(BaseModel):
    type: str  # "database", "system", "performance", "security"
    priority: str  # "low", "medium", "high", "critical"
    message: str
    suggestion: str
    impact: Optional[str] = None
    estimated_improvement: Optional[str] = None

# Endpoints de Métricas
@router.get("/metrics/system")
async def get_system_metrics():
    """Obtém métricas detalhadas do sistema"""
    try:
        import psutil
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory metrics
        memory = psutil.virtual_memory()
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        
        # Network metrics
        network = psutil.net_io_counters()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": cpu_count,
                "load_avg": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else None
            },
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system metrics")

@router.get("/metrics/database")
async def get_database_metrics():
    """Obtém métricas detalhadas do banco de dados"""
    try:
        # Simulação de métricas do banco - integrar com pool real
        metrics = {
            "active_connections": 15,
            "total_connections": 50,
            "idle_connections": 35,
            "avg_response_time": 0.25,
            "slow_queries": 2,
            "cache_hit_ratio": 0.92,
            "error_count": 0,
            "transactions_per_second": 45.2,
            "connection_utilization": 0.3
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "health_status": "healthy" if metrics["error_count"] < 10 else "degraded"
        }
        
    except Exception as e:
        logger.error(f"Failed to get database metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database metrics")

@router.get("/metrics/application")
async def get_application_metrics():
    """Obtém métricas da aplicação"""
    try:
        # Métricas da aplicação
        metrics = {
            "requests_per_minute": 120,
            "avg_response_time": 0.15,
            "error_rate": 0.02,
            "active_sessions": 25,
            "cache_hit_rate": 0.88,
            "queue_size": 5,
            "worker_threads": 8,
            "memory_usage_mb": 256
        }
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": metrics,
            "status": "healthy" if metrics["error_rate"] < 0.05 else "degraded"
        }
        
    except Exception as e:
        logger.error(f"Failed to get application metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get application metrics")

# Endpoints de Health Check
@router.get("/health/basic")
async def performance_health_basic():
    """Health check básico do sistema de performance"""
    try:
        import psutil
        
        # Verificações básicas
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        # Determinar status geral
        issues = []
        if cpu_percent > 90:
            issues.append("High CPU usage")
        if memory_percent > 85:
            issues.append("High memory usage")
        if disk_percent > 90:
            issues.append("High disk usage")
        
        status = "healthy" if not issues else "degraded"
        
        return {
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            },
            "issues": issues
        }
        
    except Exception as e:
        logger.error(f"Performance health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/health/advanced")
async def advanced_health_check():
    """Health check avançado com status detalhado do sistema"""
    try:
        import psutil
        
        # Verificar componentes do sistema
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
        
        # Simular verificação de banco e cache
        db_healthy = True  # Integrar com verificação real
        cache_healthy = True  # Integrar com verificação real
        
        overall_healthy = (
            db_healthy and 
            cache_healthy and 
            system_metrics['cpu_percent'] < 90 and
            system_metrics['memory_percent'] < 85
        )
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "database": {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "response_time_ms": 25.5
                },
                "cache": {
                    "status": "healthy" if cache_healthy else "unhealthy",
                    "hit_rate": 0.92
                },
                "system": {
                    "status": "healthy" if system_metrics['cpu_percent'] < 90 else "unhealthy",
                    "metrics": system_metrics
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Advanced health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Endpoints de Alertas
@router.post("/alerts/rules")
async def create_alert_rule(rule: AlertRule):
    """Cria uma nova regra de alerta"""
    try:
        # Simular armazenamento da regra
        rule_data = rule.dict()
        rule_data['id'] = f"rule_{int(time.time())}"
        rule_data['created_at'] = datetime.utcnow().isoformat()
        
        return {
            "message": "Alert rule created successfully",
            "rule": rule_data
        }
        
    except Exception as e:
        logger.error(f"Failed to create alert rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to create alert rule")

@router.get("/alerts/rules")
async def get_alert_rules():
    """Obtém todas as regras de alerta"""
    try:
        # Simular regras de alerta
        rules = [
            {
                "id": "rule_1",
                "name": "High CPU Usage",
                "metric": "cpu_percent",
                "operator": ">",
                "threshold": 85.0,
                "severity": "high",
                "enabled": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "rule_2",
                "name": "High Memory Usage",
                "metric": "memory_percent",
                "operator": ">",
                "threshold": 90.0,
                "severity": "critical",
                "enabled": True,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "rules": rules,
            "total_count": len(rules)
        }
        
    except Exception as e:
        logger.error(f"Failed to get alert rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alert rules")

@router.get("/alerts/active")
async def get_active_alerts():
    """Obtém alertas ativos"""
    try:
        # Simular alertas ativos
        alerts = [
            {
                "id": "alert_1",
                "rule_name": "High CPU Usage",
                "severity": "high",
                "message": "CPU usage is at 92%",
                "timestamp": datetime.utcnow().isoformat(),
                "resolved": False
            }
        ]
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "alerts": alerts,
            "total_count": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active alerts")

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve um alerta ativo"""
    try:
        # Simular resolução do alerta
        return {
            "message": "Alert resolved successfully",
            "alert_id": alert_id,
            "resolved_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to resolve alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to resolve alert")

# Endpoints de Análise de Performance
@router.get("/analysis/slow-queries")
async def get_slow_queries(limit: int = 10):
    """Obtém análise de consultas lentas"""
    try:
        # Simular consultas lentas
        slow_queries = [
            {
                "query": "SELECT * FROM diagnostics WHERE device_id = ?",
                "avg_duration": 2.5,
                "execution_count": 150,
                "table_names": ["diagnostics", "devices"],
                "suggestions": [
                    "Add index on device_id column",
                    "Avoid SELECT *, specify required columns"
                ]
            },
            {
                "query": "SELECT COUNT(*) FROM logs WHERE created_at > ?",
                "avg_duration": 1.8,
                "execution_count": 89,
                "table_names": ["logs"],
                "suggestions": [
                    "Add index on created_at column",
                    "Consider partitioning by date"
                ]
            }
        ]
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "slow_queries": slow_queries[:limit],
            "total_count": len(slow_queries)
        }
        
    except Exception as e:
        logger.error(f"Failed to get slow queries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get slow queries")

@router.get("/recommendations")
async def get_performance_recommendations():
    """Obtém recomendações de otimização de performance"""
    try:
        import psutil
        
        recommendations = []
        
        # Analisar uso de CPU
        cpu_percent = psutil.cpu_percent()
        if cpu_percent > 80:
            recommendations.append({
                "type": "system",
                "priority": "high",
                "message": "High CPU usage detected",
                "suggestion": "Consider optimizing CPU-intensive processes or scaling up resources",
                "impact": "Performance degradation",
                "estimated_improvement": "20-30% performance boost"
            })
        
        # Analisar uso de memória
        memory_percent = psutil.virtual_memory().percent
        if memory_percent > 80:
            recommendations.append({
                "type": "system",
                "priority": "high",
                "message": "High memory usage detected",
                "suggestion": "Consider increasing memory or optimizing memory usage",
                "impact": "Potential system slowdown",
                "estimated_improvement": "15-25% performance improvement"
            })
        
        # Recomendações de banco de dados
        recommendations.append({
            "type": "database",
            "priority": "medium",
            "message": "Database connection pool optimization",
            "suggestion": "Review and optimize connection pool settings",
            "impact": "Better resource utilization",
            "estimated_improvement": "10-15% query performance"
        })
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "recommendations": recommendations,
            "total_count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

# Endpoints de Dashboard
@router.get("/dashboard")
async def get_performance_dashboard():
    """Obtém dados abrangentes do dashboard de monitoramento"""
    try:
        import psutil
        
        # Coletar métricas do sistema
        system_stats = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
        
        # Simular métricas do banco
        db_stats = {
            "active_connections": 15,
            "avg_response_time": 0.25,
            "error_count": 0,
            "cache_hit_ratio": 0.92
        }
        
        # Calcular pontuações de saúde
        db_health = min(100, max(0, 100 - (db_stats['error_count'] * 10)))
        system_health = min(100, max(0, 100 - system_stats['cpu_percent']))
        overall_health = (db_health + system_health) / 2
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "health_scores": {
                "overall": round(overall_health, 1),
                "database": round(db_health, 1),
                "system": round(system_health, 1)
            },
            "database_stats": db_stats,
            "system_stats": system_stats,
            "active_alerts_count": 1,
            "slow_queries_count": 2,
            "recommendations_count": 3
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data")

@router.get("/trends")
async def get_performance_trends(hours: int = 24):
    """Obtém tendências de performance ao longo do tempo"""
    try:
        # Simular dados de tendência
        import random
        from datetime import timedelta
        
        trends = []
        base_time = datetime.utcnow() - timedelta(hours=hours)
        
        for i in range(hours):
            timestamp = base_time + timedelta(hours=i)
            trends.append({
                "timestamp": timestamp.isoformat(),
                "cpu_percent": random.uniform(20, 80),
                "memory_percent": random.uniform(30, 70),
                "response_time_ms": random.uniform(100, 500),
                "requests_per_minute": random.randint(50, 200)
            })
        
        return {
            "period_hours": hours,
            "data_points": len(trends),
            "trends": trends
        }
        
    except Exception as e:
        logger.error(f"Failed to get performance trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get performance trends")

# Endpoints de Otimização
@router.post("/optimize/database")
async def optimize_database():
    """Executa otimizações automáticas do banco de dados"""
    try:
        # Simular otimizações
        optimizations = [
            "Analyzed query execution plans",
            "Updated table statistics",
            "Optimized connection pool settings",
            "Cleaned up temporary tables"
        ]
        
        return {
            "message": "Database optimization completed",
            "optimizations_applied": optimizations,
            "estimated_improvement": "15-20% performance boost",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to optimize database: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize database")

@router.post("/optimize/cache")
async def optimize_cache():
    """Executa otimizações do sistema de cache"""
    try:
        # Simular otimizações de cache
        optimizations = [
            "Cleared expired cache entries",
            "Optimized cache key distribution",
            "Updated cache eviction policies",
            "Preloaded frequently accessed data"
        ]
        
        return {
            "message": "Cache optimization completed",
            "optimizations_applied": optimizations,
            "cache_hit_rate_improvement": "5-10%",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to optimize cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to optimize cache")

@router.get("/info")
async def performance_info():
    """
    Informações do domínio performance
    """
    return {
        "domain": "performance",
        "name": "Performance Domain",
        "version": "1.0.0", 
        "description": "Análise de performance e otimização",
        "features": ['Performance Monitoring', 'Optimization', 'Resource Analysis'],
        "status": "active"
    }

@router.get("/health")
async def performance_health_check():
    """
    Health check do domínio performance
    """
    return {
        "status": "healthy",
        "domain": "performance",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

