import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.diagnostic import Diagnostic

logger = logging.getLogger(__name__)


class PredictiveService:
    """Serviço para análise preditiva de falhas com base em diagnósticos."""
    
    def __init__(self, db: Session):
        """Inicializa o serviço de análise preditiva.
        
        Args:
            db: Sessão do banco de dados
        """
        self.db = db
    
    def predict_failures(
        self, device_id: str, time_window_days: int = 30
    ) -> Dict[str, Any]:
        """Prevê possíveis falhas com base no histórico de diagnósticos.
        
        Args:
            device_id: ID do dispositivo para análise
            time_window_days: Janela de tempo em dias para análise
            
        Returns:
            Dicionário com previsões de falhas
        """
        # Define o período de análise
        start_date = datetime.now(timezone.utc) - timedelta(days=time_window_days)
        
        # Obtém os diagnósticos do dispositivo no período
        diagnostics = self.db.query(Diagnostic).filter(
            Diagnostic.device_id == device_id,
            Diagnostic.created_at >= start_date
        ).order_by(Diagnostic.created_at.asc()).all()
        
        if not diagnostics:
            logger.warning(f"No diagnostics found for device {device_id} in the last {time_window_days} days")
            return {
                "device_id": device_id,
                "predictions": {},
                "risk_level": "unknown",
                "message": f"No diagnostics found in the last {time_window_days} days"
            }
        
        # Analisa tendências nos componentes
        cpu_trend = self._analyze_component_trend(diagnostics, "cpu_usage")
        memory_trend = self._analyze_component_trend(diagnostics, "memory_usage")
        disk_trend = self._analyze_component_trend(diagnostics, "disk_usage")
        health_trend = self._analyze_component_trend(diagnostics, "overall_health", inverse=True)
        
        # Calcula o risco geral
        risk_level, risk_components = self._calculate_risk_level(
            cpu_trend, memory_trend, disk_trend, health_trend
        )
        
        # Gera previsões específicas
        predictions = self._generate_predictions(
            diagnostics, cpu_trend, memory_trend, disk_trend, health_trend
        )
        
        # Compila os resultados
        result = {
            "device_id": device_id,
            "analysis_period": {
                "start_date": start_date.isoformat(),
                "end_date": datetime.now(timezone.utc).isoformat(),
                "days": time_window_days
            },
            "diagnostics_analyzed": len(diagnostics),
            "trends": {
                "cpu_usage": cpu_trend,
                "memory_usage": memory_trend,
                "disk_usage": disk_trend,
                "overall_health": health_trend
            },
            "risk_level": risk_level,
            "risk_components": risk_components,
            "predictions": predictions,
            "recommended_actions": self._get_recommended_actions(risk_level, risk_components)
        }
        
        return result
    
    def _analyze_component_trend(
        self, diagnostics: List[Diagnostic], attribute: str, inverse: bool = False
    ) -> Dict[str, Any]:
        """Analisa a tendência de um componente ao longo do tempo.
        
        Args:
            diagnostics: Lista de diagnósticos
            attribute: Nome do atributo a ser analisado
            inverse: Se True, valores mais altos são piores (ex: uso de CPU)
                     Se False, valores mais altos são melhores (ex: saúde geral)
            
        Returns:
            Dicionário com análise de tendência
        """
        values = []
        dates = []
        
        for diag in diagnostics:
            value = getattr(diag, attribute)
            if value is not None:
                values.append(value)
                dates.append(diag.created_at)
        
        if not values:
            return {"trend": "unknown", "slope": 0, "values": []}
        
        # Calcula estatísticas básicas
        avg = sum(values) / len(values)
        latest = values[-1] if values else None
        
        # Calcula a tendência (simplificada)
        if len(values) >= 2:
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            slope = second_avg - first_avg
            
            # Determina a direção da tendência
            if abs(slope) < 0.05 * avg:  # Menos de 5% de variação
                trend = "stable"
            else:
                if inverse:
                    trend = "improving" if slope < 0 else "degrading"
                else:
                    trend = "improving" if slope > 0 else "degrading"
        else:
            trend = "unknown"
            slope = 0
        
        return {
            "trend": trend,
            "slope": slope,
            "current": latest,
            "average": avg,
            "min": min(values),
            "max": max(values),
            "values": list(zip([d.isoformat() for d in dates], values))
        }
    
    def _calculate_risk_level(
        self, cpu_trend: Dict[str, Any], memory_trend: Dict[str, Any], 
        disk_trend: Dict[str, Any], health_trend: Dict[str, Any]
    ) -> tuple:
        """Calcula o nível de risco geral com base nas tendências.
        
        Args:
            cpu_trend: Tendência de uso da CPU
            memory_trend: Tendência de uso da memória
            disk_trend: Tendência de uso do disco
            health_trend: Tendência de saúde geral
            
        Returns:
            Tupla com nível de risco e componentes em risco
        """
        risk_components = []
        
        # Verifica componentes em degradação
        if cpu_trend["trend"] == "degrading" and cpu_trend["current"] > 80:
            risk_components.append("cpu")
        
        if memory_trend["trend"] == "degrading" and memory_trend["current"] > 80:
            risk_components.append("memory")
        
        if disk_trend["trend"] == "degrading" and disk_trend["current"] > 85:
            risk_components.append("disk")
        
        if health_trend["trend"] == "degrading" and health_trend["current"] < 70:
            risk_components.append("overall_health")
        
        # Determina o nível de risco
        if len(risk_components) >= 3 or (health_trend["current"] and health_trend["current"] < 50):
            risk_level = "high"
        elif len(risk_components) >= 1 or (health_trend["current"] and health_trend["current"] < 70):
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return risk_level, risk_components
    
    def _generate_predictions(
        self, diagnostics: List[Diagnostic], cpu_trend: Dict[str, Any], 
        memory_trend: Dict[str, Any], disk_trend: Dict[str, Any], 
        health_trend: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Gera previsões específicas com base nas tendências.
        
        Args:
            diagnostics: Lista de diagnósticos
            cpu_trend: Tendência de uso da CPU
            memory_trend: Tendência de uso da memória
            disk_trend: Tendência de uso do disco
            health_trend: Tendência de saúde geral
            
        Returns:
            Dicionário com previsões
        """
        predictions = {}
        
        # Previsão de espaço em disco
        if disk_trend["trend"] == "degrading" and disk_trend["slope"] > 0:
            # Estima quando o disco ficará cheio
            remaining_space = 100 - disk_trend["current"]
            days_to_full = remaining_space / (disk_trend["slope"] * 30) if disk_trend["slope"] > 0 else 999
            
            if days_to_full < 30:
                predictions["disk_full"] = {
                    "message": f"O disco pode ficar cheio em aproximadamente {int(days_to_full)} dias",
                    "estimated_date": (datetime.now(timezone.utc) + timedelta(days=days_to_full)).isoformat(),
                    "confidence": "medium"
                }
        
        # Previsão de falha de hardware
        if health_trend["trend"] == "degrading" and health_trend["slope"] < 0:
            # Estima quando a saúde cairá abaixo de um limite crítico
            current_health = health_trend["current"]
            critical_threshold = 40
            days_to_critical = (current_health - critical_threshold) / abs(health_trend["slope"] * 30) if health_trend["slope"] < 0 else 999
            
            if days_to_critical < 60:
                predictions["hardware_failure"] = {
                    "message": f"Possível falha de hardware em aproximadamente {int(days_to_critical)} dias",
                    "estimated_date": (datetime.now(timezone.utc) + timedelta(days=days_to_critical)).isoformat(),
                    "confidence": "medium",
                    "affected_components": self._identify_failing_components(diagnostics[-1])
                }
        
        # Previsão de problemas de desempenho
        if cpu_trend["trend"] == "degrading" or memory_trend["trend"] == "degrading":
            predictions["performance_issues"] = {
                "message": "Possíveis problemas de desempenho no futuro próximo",
                "confidence": "medium",
                "affected_components": []
            }
            
            if cpu_trend["trend"] == "degrading":
                predictions["performance_issues"]["affected_components"].append("cpu")
            
            if memory_trend["trend"] == "degrading":
                predictions["performance_issues"]["affected_components"].append("memory")
        
        return predictions
    
    def _identify_failing_components(self, diagnostic: Diagnostic) -> List[str]:
        """Identifica componentes com maior probabilidade de falha.
        
        Args:
            diagnostic: Diagnóstico mais recente
            
        Returns:
            Lista de componentes com maior probabilidade de falha
        """
        failing_components = []
        
        if diagnostic.cpu_status == "critical" or diagnostic.cpu_temperature and diagnostic.cpu_temperature > 80:
            failing_components.append("cpu")
        
        if diagnostic.memory_status == "critical":
            failing_components.append("memory")
        
        if diagnostic.disk_status == "critical" or diagnostic.disk_usage and diagnostic.disk_usage > 95:
            failing_components.append("disk")
        
        if diagnostic.network_status == "critical":
            failing_components.append("network")
        
        return failing_components
    
    def _get_recommended_actions(self, risk_level: str, risk_components: List[str]) -> List[str]:
        """Gera recomendações de ações com base no nível de risco e componentes afetados.
        
        Args:
            risk_level: Nível de risco (low, medium, high)
            risk_components: Lista de componentes em risco
            
        Returns:
            Lista de ações recomendadas
        """
        actions = []
        
        if risk_level == "low":
            actions.append("Continuar monitoramento regular")
            actions.append("Realizar diagnósticos completos mensalmente")
        
        if risk_level == "medium" or risk_level == "high":
            actions.append("Agendar diagnóstico completo em breve")
            
            if "disk" in risk_components:
                actions.append("Liberar espaço em disco removendo arquivos desnecessários")
                actions.append("Considerar adicionar mais armazenamento")
            
            if "cpu" in risk_components:
                actions.append("Verificar processos consumindo muita CPU")
                actions.append("Limpar sistema de refrigeração")
            
            if "memory" in risk_components:
                actions.append("Verificar aplicativos com vazamento de memória")
                actions.append("Considerar adicionar mais memória RAM")
            
            if "overall_health" in risk_components:
                actions.append("Realizar manutenção preventiva completa")
        
        if risk_level == "high":
            actions.append("Fazer backup de dados importantes imediatamente")
            actions.append("Agendar manutenção com técnico especializado")
            actions.append("Considerar substituição de componentes críticos")
        
        return actions