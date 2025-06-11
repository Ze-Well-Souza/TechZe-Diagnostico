"""
Advanced Monitoring and Alerts API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta, timezone
import asyncio
import logging
from pydantic import BaseModel

from ...core.database_advanced import get_advanced_pool
from ...core.cache import get_cache_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

class AlertRule(BaseModel):
    name: str
    metric: str
    operator: str
    threshold: float
    severity: str
    enabled: bool = True

class AlertResponse(BaseModel):
    id: str
    rule_name: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False

@router.get("/health/advanced")
async def advanced_health_check():
    """Advanced health check with detailed system status"""
    try:
        pool = await get_advanced_pool()
        cache = await get_cache_client()
        
        # Check database
        db_stats = pool.get_stats()
        db_healthy = db_stats['error_count'] < 10
        
        # Check cache
        cache_healthy = True
        try:
            await cache.ping()
        except:
            cache_healthy = False
        
        # System metrics
        import psutil
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
        
        overall_healthy = db_healthy and cache_healthy and system_metrics['cpu_percent'] < 90
        
        return {
            "status": "healthy" if overall_healthy else "degraded",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {
                "database": {
                    "status": "healthy" if db_healthy else "unhealthy",
                    "stats": db_stats
                },
                "cache": {
                    "status": "healthy" if cache_healthy else "unhealthy"
                },
                "system": {
                    "status": "healthy" if system_metrics['cpu_percent'] < 90 else "unhealthy",
                    "metrics": system_metrics
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.get("/metrics/database")
async def get_database_metrics():
    """Get detailed database metrics"""
    try:
        pool = await get_advanced_pool()
        stats = pool.get_stats()
        
        # Add query performance metrics
        stats.update({
            "slow_queries": 0,  # Would be calculated from query stats
            "cache_hit_ratio": 0.85,  # Would be calculated from cache stats
            "connection_utilization": stats['active_connections'] / stats['total_connections'] if stats['total_connections'] > 0 else 0
        })
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": stats
        }
        
    except Exception as e:
        logger.error(f"Failed to get database metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

@router.get("/metrics/system")
async def get_system_metrics():
    """Get system resource metrics"""
    import psutil
    
    try:
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
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

@router.get("/performance/slow-queries")
async def get_slow_queries(limit: int = 10):
    """Get slow query analysis"""
    try:
        # This would integrate with the query optimizer
        # For now, return mock data
        slow_queries = [
            {
                "query": "SELECT * FROM diagnostics WHERE...",
                "avg_duration": 2.5,
                "execution_count": 150,
                "table_names": ["diagnostics", "devices"],
                "suggestions": [
                    "Add index on device_id column",
                    "Avoid SELECT *, specify required columns"
                ]
            }
        ]
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "slow_queries": slow_queries[:limit],
            "total_count": len(slow_queries)
        }
        
    except Exception as e:
        logger.error(f"Failed to get slow queries: {e}")
        raise HTTPException(status_code=500, detail="Failed to get slow queries")

@router.post("/alerts/rules")
async def create_alert_rule(rule: AlertRule):
    """Create a new alert rule"""
    try:
        cache = await get_cache_client()
        
        # Store alert rule in cache
        rule_data = rule.dict()
        rule_data['created_at'] = datetime.now(timezone.utc).isoformat()
        
        await cache.hset("alert_rules", rule.name, str(rule_data))
        
        return {
            "message": "Alert rule created successfully",
            "rule": rule_data
        }
        
    except Exception as e:
        logger.error(f"Failed to create alert rule: {e}")
        raise HTTPException(status_code=500, detail="Failed to create alert rule")

@router.get("/alerts/rules")
async def get_alert_rules():
    """Get all alert rules"""
    try:
        cache = await get_cache_client()
        
        # Get alert rules from cache
        rules_data = await cache.hgetall("alert_rules")
        
        rules = []
        for name, data in rules_data.items():
            try:
                import json
                rule = json.loads(data)
                rules.append(rule)
            except:
                continue
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "rules": rules,
            "total_count": len(rules)
        }
        
    except Exception as e:
        logger.error(f"Failed to get alert rules: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alert rules")

@router.get("/alerts/active")
async def get_active_alerts():
    """Get active alerts"""
    try:
        cache = await get_cache_client()
        
        # Get active alerts from cache
        alerts_data = await cache.hgetall("active_alerts")
        
        alerts = []
        for alert_id, data in alerts_data.items():
            try:
                import json
                alert = json.loads(data)
                if not alert.get('resolved', False):
                    alerts.append(alert)
            except:
                continue
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "alerts": alerts,
            "total_count": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Failed to get active alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active alerts")

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an active alert"""
    try:
        cache = await get_cache_client()
        
        # Get alert from cache
        alert_data = await cache.hget("active_alerts", alert_id)
        if not alert_data:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        import json
        alert = json.loads(alert_data)
        alert['resolved'] = True
        alert['resolved_at'] = datetime.now(timezone.utc).isoformat()
        
        # Update alert in cache
        await cache.hset("active_alerts", alert_id, json.dumps(alert))
        
        return {
            "message": "Alert resolved successfully",
            "alert_id": alert_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to resolve alert")

@router.get("/performance/recommendations")
async def get_performance_recommendations():
    """Get performance optimization recommendations"""
    try:
        pool = await get_advanced_pool()
        stats = pool.get_stats()
        
        recommendations = []
        
        # Analyze connection usage
        if stats['active_connections'] / stats['total_connections'] > 0.8:
            recommendations.append({
                "type": "database",
                "priority": "high",
                "message": "High database connection usage detected",
                "suggestion": "Consider increasing connection pool size or optimizing queries"
            })
        
        # Analyze query performance
        if stats['avg_response_time'] > 1.0:
            recommendations.append({
                "type": "performance",
                "priority": "medium",
                "message": "Slow average query response time",
                "suggestion": "Review and optimize slow queries, consider adding indexes"
            })
        
        # System resource recommendations
        import psutil
        if psutil.virtual_memory().percent > 80:
            recommendations.append({
                "type": "system",
                "priority": "high",
                "message": "High memory usage detected",
                "suggestion": "Consider scaling up server resources or optimizing memory usage"
            })
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "recommendations": recommendations,
            "total_count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"Failed to get recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@router.get("/dashboard")
async def get_monitoring_dashboard():
    """Get comprehensive monitoring dashboard data"""
    try:
        # Gather all monitoring data
        pool = await get_advanced_pool()
        db_stats = pool.get_stats()
        
        import psutil
        system_stats = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
        
        # Calculate health scores
        db_health = min(100, max(0, 100 - (db_stats['error_count'] * 10)))
        system_health = min(100, max(0, 100 - system_stats['cpu_percent']))
        overall_health = (db_health + system_health) / 2
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "health_scores": {
                "overall": overall_health,
                "database": db_health,
                "system": system_health
            },
            "database_stats": db_stats,
            "system_stats": system_stats,
            "active_alerts_count": 0,  # Would get from alert manager
            "slow_queries_count": 0    # Would get from query optimizer
        }
        
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard data") 