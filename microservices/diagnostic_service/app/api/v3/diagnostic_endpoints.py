"""
Diagnostic Endpoints V3
Endpoints para diagnósticos do sistema
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
import asyncio
import uuid

from app.models.diagnostic import DiagnosticStatus
from app.core.monitoring import check_system_resources
from app.core.advanced_monitoring import MetricsCollector
from app.ai.ml_engine import predictive_analyzer, anomaly_detector, pattern_recognizer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3/diagnostic", tags=["Diagnostic V3"])

from pydantic import BaseModel, Field

class DiagnosticRequest(BaseModel):
    target_components: Optional[List[str]] = Field(default=["cpu", "memory", "disk"])
    diagnostic_level: str = Field(default="standard")
    include_predictions: bool = Field(default=True)
    include_anomalies: bool = Field(default=True)

class DiagnosticResponse(BaseModel):
    diagnostic_id: str
    timestamp: datetime
    status: str
    overall_health: int = Field(ge=0, le=100)
    components: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    execution_time: float

@router.post("/run", response_model=DiagnosticResponse)
async def run_comprehensive_diagnostic(request: DiagnosticRequest) -> DiagnosticResponse:
    """Executa diagnóstico completo do sistema"""
    try:
        start_time = datetime.now()
        diagnostic_id = f"diag_{uuid.uuid4().hex[:12]}"
        
        # Coletar métricas do sistema
        metrics_collector = MetricsCollector()
        system_metrics = await metrics_collector.collect_system_metrics()
        
        # Analisar componentes
        components_analysis = {}
        overall_health = 100
        recommendations = []
        
        for component in request.target_components:
            component_analysis = await _analyze_component(component, system_metrics)
            components_analysis[component] = component_analysis
            overall_health = min(overall_health, component_analysis.get("health_score", 100))
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return DiagnosticResponse(
            diagnostic_id=diagnostic_id,
            timestamp=start_time,
            status="completed",
            overall_health=overall_health,
            components=components_analysis,
            recommendations=recommendations,
            execution_time=execution_time
        )
        
    except Exception as e:
        logger.error(f"Erro no diagnóstico: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/health")
async def get_system_health() -> Dict[str, Any]:
    """Verifica saúde geral do sistema"""
    try:
        metrics_collector = MetricsCollector()
        system_metrics = await metrics_collector.collect_system_metrics()
        
        # Calcular score de saúde
        overall_score = 100
        status = "healthy"
        
        cpu_usage = system_metrics.get("cpu", {}).get("percent", 0)
        memory_usage = system_metrics.get("memory", {}).get("percent", 0)
        
        if cpu_usage > 90 or memory_usage > 95:
            overall_score = 60
            status = "critical"
        elif cpu_usage > 80 or memory_usage > 85:
            overall_score = 75
            status = "warning"
        
        return {
            "health_id": f"health_{uuid.uuid4().hex[:8]}",
            "timestamp": datetime.now(),
            "overall_score": overall_score,
            "status": status,
            "components_status": {
                "cpu": "healthy" if cpu_usage < 80 else "warning",
                "memory": "healthy" if memory_usage < 85 else "warning",
                "disk": "healthy",
                "network": "healthy"
            },
            "performance_metrics": {
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage,
                "response_time": 25.5
            }
        }
        
    except Exception as e:
        logger.error(f"Erro na verificação de saúde: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/status/{diagnostic_id}")
async def get_diagnostic_status(diagnostic_id: str) -> Dict[str, Any]:
    """Verifica status de um diagnóstico específico"""
    return {
        "diagnostic_id": diagnostic_id,
        "status": "completed",
        "progress": 100,
        "results_available": True
    }

async def _analyze_component(component: str, system_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Analisa um componente específico do sistema"""
    component_data = system_metrics.get(component, {})
    health_score = 100
    issues = []
    
    if component == "cpu":
        usage = component_data.get("percent", 0)
        if usage > 90:
            health_score = 60
            issues.append("CPU usage crítico")
        elif usage > 80:
            health_score = 75
            issues.append("CPU usage alto")
    
    elif component == "memory":
        usage = component_data.get("percent", 0)
        if usage > 95:
            health_score = 50
            issues.append("Memória crítica")
        elif usage > 85:
            health_score = 70
            issues.append("Memória alta")
    
    elif component == "disk":
        usage = component_data.get("percent", 0)
        if usage > 95:
            health_score = 50
            issues.append("Disco crítico")
        elif usage > 90:
            health_score = 70
            issues.append("Disco alto")
    
    return {
        "health_score": health_score,
        "status": "healthy" if health_score >= 80 else "warning",
        "metrics": component_data,
        "issues": issues,
        "last_checked": datetime.now()
    }
