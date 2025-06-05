"""
Endpoint de monitoramento para connection pool e performance
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import asyncio
import time
from datetime import datetime
from ..core.database import get_connection_stats, health_check

router = APIRouter(prefix="/monitoring", tags=["monitoring"])

@router.get("/database/pool")
async def get_pool_status() -> Dict[str, Any]:
    """
    Retorna estatísticas detalhadas do connection pool PostgreSQL
    """
    try:
        stats = await get_connection_stats()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy" if stats.get("health") else "unhealthy",
            "pool_stats": stats,
            "performance": {
                "response_time_ms": await measure_db_response_time(),
                "last_check": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@router.get("/database/health")
async def database_health() -> Dict[str, Any]:
    """
    Health check simplificado do banco de dados
    """
    start_time = time.time()
    is_healthy = await health_check()
    response_time = (time.time() - start_time) * 1000
    
    return {
        "healthy": is_healthy,
        "response_time_ms": round(response_time, 2),
        "timestamp": datetime.utcnow().isoformat()
    }

async def measure_db_response_time() -> float:
    """Mede tempo de resposta do banco de dados"""
    start_time = time.time()
    await health_check()
    return round((time.time() - start_time) * 1000, 2) 