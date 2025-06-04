"""
Machine Learning Engine para TechZe Diagnostic Service
Implementa análise preditiva, detecção de anomalias e recomendações inteligentes
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PredictionType(Enum):
    """Tipos de previsão disponíveis"""
    HARDWARE_FAILURE = "hardware_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SECURITY_BREACH = "security_breach"
    SYSTEM_OVERLOAD = "system_overload"

class AnomalyType(Enum):
    """Tipos de anomalia detectáveis"""
    CPU_SPIKE = "cpu_spike"
    MEMORY_LEAK = "memory_leak"
    DISK_UNUSUAL = "disk_unusual"
    NETWORK_ANOMALY = "network_anomaly"
    TEMPERATURE_ABNORMAL = "temperature_abnormal"

@dataclass
class PredictionResult:
    """Resultado de uma previsão"""
    prediction_type: PredictionType
    probability: float
    confidence: float
    time_to_failure: Optional[timedelta]
    recommended_actions: List[str]
    risk_level: str
    details: Dict[str, Any]

@dataclass
class AnomalyResult:
    """Resultado de detecção de anomalia"""
    anomaly_type: AnomalyType
    severity: float
    timestamp: datetime
    affected_components: List[str]
    description: str
    suggested_investigation: List[str]

@dataclass
class PatternResult:
    """Resultado de reconhecimento de padrão"""
    pattern_name: str
    frequency: int
    last_occurrence: datetime
    correlation_strength: float
    related_events: List[str]
    business_impact: str

@dataclass
class Recommendation:
    """Recomendação do sistema"""
    title: str
    description: str
    priority: str
    category: str
    estimated_impact: str
    implementation_steps: List[str]
    resources_needed: List[str]

class PredictiveAnalyzer:
    """Analisador preditivo para falhas de sistema"""
    
    def __init__(self):
        self.models = {}
        self.feature_extractors = {}
        self.prediction_history = []
        self.accuracy_metrics = {}
        
    async def predict_failure(self, system_data: Dict[str, Any]) -> PredictionResult:
        """Prevê possíveis falhas do sistema"""
        try:
            # Extração de features
            features = self._extract_features(system_data)
            
            # Análise de tendências
            trends = self._analyze_trends(features)
            
            # Previsão usando modelo ML (simulado)
            prediction_type, probability = self._predict_with_ml(features, trends)
            
            # Cálculo de confiança
            confidence = self._calculate_confidence(features, trends)
            
            # Estimativa de tempo até falha
            time_to_failure = self._estimate_time_to_failure(probability, trends)
            
            # Geração de recomendações
            recommended_actions = self._generate_recommendations(prediction_type, probability)
            
            # Determinação do nível de risco
            risk_level = self._determine_risk_level(probability, confidence)
            
            result = PredictionResult(
                prediction_type=prediction_type,
                probability=probability,
                confidence=confidence,
                time_to_failure=time_to_failure,
                recommended_actions=recommended_actions,
                risk_level=risk_level,
                details={
                    "features_analyzed": len(features),
                    "trend_indicators": trends,
                    "model_version": "v3.0",
                    "analysis_timestamp": datetime.now()
                }
            )
            
            # Armazenar para histórico
            self.prediction_history.append(result)
            
            logger.info(f"Previsão gerada: {prediction_type.value} com {probability:.2%} de probabilidade")
            return result
            
        except Exception as e:
            logger.error(f"Erro na análise preditiva: {e}")
            raise
    
    def _extract_features(self, system_data: Dict[str, Any]) -> Dict[str, float]:
        """Extrai features relevantes dos dados do sistema"""
        features = {}
        
        # CPU features
        if 'cpu' in system_data:
            cpu_data = system_data['cpu']
            features['cpu_usage_avg'] = np.mean(cpu_data.get('usage_history', [0]))
            features['cpu_usage_std'] = np.std(cpu_data.get('usage_history', [0]))
            features['cpu_temperature'] = cpu_data.get('temperature', 0)
            features['cpu_frequency'] = cpu_data.get('frequency', 0)
        
        # Memory features
        if 'memory' in system_data:
            mem_data = system_data['memory']
            features['memory_usage'] = mem_data.get('usage_percent', 0)
            features['memory_available'] = mem_data.get('available_gb', 0)
            features['swap_usage'] = mem_data.get('swap_percent', 0)
        
        # Disk features
        if 'disk' in system_data:
            disk_data = system_data['disk']
            features['disk_usage'] = disk_data.get('usage_percent', 0)
            features['disk_io_read'] = disk_data.get('io_read_mb', 0)
            features['disk_io_write'] = disk_data.get('io_write_mb', 0)
            features['disk_health'] = disk_data.get('health_score', 100)
        
        # Network features
        if 'network' in system_data:
            net_data = system_data['network']
            features['network_latency'] = net_data.get('latency_ms', 0)
            features['network_throughput'] = net_data.get('throughput_mbps', 0)
            features['packet_loss'] = net_data.get('packet_loss_percent', 0)
        
        return features
    
    def _analyze_trends(self, features: Dict[str, float]) -> Dict[str, str]:
        """Analisa tendências nos dados"""
        trends = {}
        
        # Simulação de análise de tendências
        for feature, value in features.items():
            if 'usage' in feature and value > 80:
                trends[feature] = "increasing_rapidly"
            elif 'temperature' in feature and value > 70:
                trends[feature] = "concerning_rise"
            elif 'health' in feature and value < 80:
                trends[feature] = "degrading"
            else:
                trends[feature] = "stable"
        
        return trends
    
    def _predict_with_ml(self, features: Dict[str, float], trends: Dict[str, str]) -> Tuple[PredictionType, float]:
        """Faz previsão usando modelo ML (simulado)"""
        # Simulação de modelo ML
        risk_score = 0.0
        
        # Análise de CPU
        if features.get('cpu_usage_avg', 0) > 85:
            risk_score += 0.3
        if features.get('cpu_temperature', 0) > 75:
            risk_score += 0.4
        
        # Análise de memória
        if features.get('memory_usage', 0) > 90:
            risk_score += 0.3
        
        # Análise de disco
        if features.get('disk_health', 100) < 70:
            risk_score += 0.5
        if features.get('disk_usage', 0) > 95:
            risk_score += 0.2
        
        # Análise de rede
        if features.get('packet_loss', 0) > 5:
            risk_score += 0.3
        
        # Determinar tipo de previsão baseado no maior risco
        if features.get('disk_health', 100) < 70:
            prediction_type = PredictionType.HARDWARE_FAILURE
        elif features.get('cpu_usage_avg', 0) > 90:
            prediction_type = PredictionType.SYSTEM_OVERLOAD
        elif features.get('packet_loss', 0) > 3:
            prediction_type = PredictionType.SECURITY_BREACH
        else:
            prediction_type = PredictionType.PERFORMANCE_DEGRADATION
        
        probability = min(risk_score, 0.95)  # Máximo 95%
        
        return prediction_type, probability
    
    def _calculate_confidence(self, features: Dict[str, float], trends: Dict[str, str]) -> float:
        """Calcula confiança na previsão"""
        # Simulação de cálculo de confiança
        confidence = 0.7  # Base
        
        # Mais dados = mais confiança
        confidence += min(len(features) * 0.02, 0.2)
        
        # Tendências claras = mais confiança
        concerning_trends = sum(1 for trend in trends.values() 
                              if trend in ["increasing_rapidly", "concerning_rise", "degrading"])
        confidence += concerning_trends * 0.05
        
        return min(confidence, 0.95)
    
    def _estimate_time_to_failure(self, probability: float, trends: Dict[str, str]) -> Optional[timedelta]:
        """Estima tempo até possível falha"""
        if probability < 0.3:
            return None
        
        # Simulação de estimativa
        base_days = 30
        
        if probability > 0.8:
            base_days = 3
        elif probability > 0.6:
            base_days = 7
        elif probability > 0.4:
            base_days = 14
        
        # Ajustar baseado em tendências
        rapid_trends = sum(1 for trend in trends.values() 
                          if trend in ["increasing_rapidly", "concerning_rise"])
        if rapid_trends > 2:
            base_days = max(1, base_days // 2)
        
        return timedelta(days=base_days)
    
    def _generate_recommendations(self, prediction_type: PredictionType, probability: float) -> List[str]:
        """Gera recomendações baseadas na previsão"""
        recommendations = []
        
        if prediction_type == PredictionType.HARDWARE_FAILURE:
            recommendations.extend([
                "Realizar backup completo imediatamente",
                "Verificar logs de hardware para erros",
                "Agendar manutenção preventiva",
                "Considerar substituição de componentes críticos"
            ])
        
        elif prediction_type == PredictionType.PERFORMANCE_DEGRADATION:
            recommendations.extend([
                "Otimizar processos em execução",
                "Limpar arquivos temporários",
                "Verificar fragmentação do disco",
                "Atualizar drivers de sistema"
            ])
        
        elif prediction_type == PredictionType.SECURITY_BREACH:
            recommendations.extend([
                "Verificar logs de segurança",
                "Atualizar definições de antivírus",
                "Revisar configurações de firewall",
                "Monitorar tráfego de rede suspeito"
            ])
        
        elif prediction_type == PredictionType.SYSTEM_OVERLOAD:
            recommendations.extend([
                "Redistribuir carga de trabalho",
                "Adicionar recursos de hardware",
                "Otimizar configurações de sistema",
                "Implementar balanceamento de carga"
            ])
        
        if probability > 0.7:
            recommendations.insert(0, "AÇÃO URGENTE NECESSÁRIA")
        
        return recommendations
    
    def _determine_risk_level(self, probability: float, confidence: float) -> str:
        """Determina nível de risco"""
        risk_score = probability * confidence
        
        if risk_score > 0.7:
            return "CRÍTICO"
        elif risk_score > 0.5:
            return "ALTO"
        elif risk_score > 0.3:
            return "MÉDIO"
        else:
            return "BAIXO"

class AnomalyDetector:
    """Detector de anomalias em tempo real"""
    
    def __init__(self):
        self.baseline_metrics = {}
        self.detection_models = {}
        self.anomaly_history = []
        
    async def detect_anomalies(self, current_metrics: Dict[str, Any]) -> List[AnomalyResult]:
        """Detecta anomalias nos métricas atuais"""
        try:
            anomalies = []
            
            # Detectar diferentes tipos de anomalias
            cpu_anomalies = self._detect_cpu_anomalies(current_metrics)
            memory_anomalies = self._detect_memory_anomalies(current_metrics)
            disk_anomalies = self._detect_disk_anomalies(current_metrics)
            network_anomalies = self._detect_network_anomalies(current_metrics)
            temperature_anomalies = self._detect_temperature_anomalies(current_metrics)
            
            anomalies.extend(cpu_anomalies)
            anomalies.extend(memory_anomalies)
            anomalies.extend(disk_anomalies)
            anomalies.extend(network_anomalies)
            anomalies.extend(temperature_anomalies)
            
            # Armazenar no histórico
            self.anomaly_history.extend(anomalies)
            
            if anomalies:
                logger.warning(f"Detectadas {len(anomalies)} anomalias")
            
            return anomalies
            
        except Exception as e:
            logger.error(f"Erro na detecção de anomalias: {e}")
            return []
    
    def _detect_cpu_anomalies(self, metrics: Dict[str, Any]) -> List[AnomalyResult]:
        """Detecta anomalias de CPU"""
        anomalies = []
        
        cpu_data = metrics.get('cpu', {})
        current_usage = cpu_data.get('usage_percent', 0)
        
        # Spike de CPU
        if current_usage > 95:
            anomalies.append(AnomalyResult(
                anomaly_type=AnomalyType.CPU_SPIKE,
                severity=0.9,
                timestamp=datetime.now(),
                affected_components=['CPU'],
                description=f"Uso de CPU extremamente alto: {current_usage}%",
                suggested_investigation=[
                    "Verificar processos com maior uso de CPU",
                    "Analisar se há malware ou processos suspeitos",
                    "Considerar limitação de recursos para processos específicos"
                ]
            ))
        
        return anomalies
    
    def _detect_memory_anomalies(self, metrics: Dict[str, Any]) -> List[AnomalyResult]:
        """Detecta anomalias de memória"""
        anomalies = []
        
        memory_data = metrics.get('memory', {})
        current_usage = memory_data.get('usage_percent', 0)
        
        # Possível memory leak
        if current_usage > 90:
            anomalies.append(AnomalyResult(
                anomaly_type=AnomalyType.MEMORY_LEAK,
                severity=0.8,
                timestamp=datetime.now(),
                affected_components=['RAM'],
                description=f"Uso de memória crítico: {current_usage}%",
                suggested_investigation=[
                    "Identificar processos com maior uso de memória",
                    "Verificar possíveis vazamentos de memória",
                    "Considerar reinicialização de serviços problemáticos"
                ]
            ))
        
        return anomalies
    
    def _detect_disk_anomalies(self, metrics: Dict[str, Any]) -> List[AnomalyResult]:
        """Detecta anomalias de disco"""
        anomalies = []
        
        disk_data = metrics.get('disk', {})
        io_read = disk_data.get('io_read_mb', 0)
        io_write = disk_data.get('io_write_mb', 0)
        
        # I/O anômalo
        if io_read > 1000 or io_write > 1000:
            anomalies.append(AnomalyResult(
                anomaly_type=AnomalyType.DISK_UNUSUAL,
                severity=0.6,
                timestamp=datetime.now(),
                affected_components=['Disk'],
                description=f"I/O de disco anômalo: Read {io_read}MB/s, Write {io_write}MB/s",
                suggested_investigation=[
                    "Verificar processos com alta atividade de disco",
                    "Analisar fragmentação do disco",
                    "Verificar integridade do sistema de arquivos"
                ]
            ))
        
        return anomalies
    
    def _detect_network_anomalies(self, metrics: Dict[str, Any]) -> List[AnomalyResult]:
        """Detecta anomalias de rede"""
        anomalies = []
        
        network_data = metrics.get('network', {})
        packet_loss = network_data.get('packet_loss_percent', 0)
        latency = network_data.get('latency_ms', 0)
        
        # Anomalia de rede
        if packet_loss > 5 or latency > 500:
            anomalies.append(AnomalyResult(
                anomaly_type=AnomalyType.NETWORK_ANOMALY,
                severity=0.7,
                timestamp=datetime.now(),
                affected_components=['Network'],
                description=f"Problemas de rede: {packet_loss}% perda, {latency}ms latência",
                suggested_investigation=[
                    "Verificar conectividade de rede",
                    "Analisar configurações de firewall",
                    "Verificar possível ataque DDoS"
                ]
            ))
        
        return anomalies
    
    def _detect_temperature_anomalies(self, metrics: Dict[str, Any]) -> List[AnomalyResult]:
        """Detecta anomalias de temperatura"""
        anomalies = []
        
        cpu_data = metrics.get('cpu', {})
        temperature = cpu_data.get('temperature', 0)
        
        # Temperatura anômala
        if temperature > 80:
            anomalies.append(AnomalyResult(
                anomaly_type=AnomalyType.TEMPERATURE_ABNORMAL,
                severity=0.8,
                timestamp=datetime.now(),
                affected_components=['CPU', 'Cooling System'],
                description=f"Temperatura crítica: {temperature}°C",
                suggested_investigation=[
                    "Verificar sistema de refrigeração",
                    "Limpar ventiladores e dissipadores",
                    "Verificar pasta térmica do processador"
                ]
            ))
        
        return anomalies

class PatternRecognizer:
    """Reconhecedor de padrões em dados históricos"""
    
    def __init__(self):
        self.pattern_database = {}
        self.correlation_matrix = {}
        
    async def recognize_patterns(self, historical_data: List[Dict[str, Any]]) -> List[PatternResult]:
        """Reconhece padrões nos dados históricos"""
        try:
            patterns = []
            
            # Padrões temporais
            temporal_patterns = self._find_temporal_patterns(historical_data)
            patterns.extend(temporal_patterns)
            
            # Padrões de correlação
            correlation_patterns = self._find_correlation_patterns(historical_data)
            patterns.extend(correlation_patterns)
            
            # Padrões de frequência
            frequency_patterns = self._find_frequency_patterns(historical_data)
            patterns.extend(frequency_patterns)
            
            logger.info(f"Reconhecidos {len(patterns)} padrões")
            return patterns
            
        except Exception as e:
            logger.error(f"Erro no reconhecimento de padrões: {e}")
            return []
    
    def _find_temporal_patterns(self, data: List[Dict[str, Any]]) -> List[PatternResult]:
        """Encontra padrões temporais"""
        patterns = []
        
        # Simulação de detecção de padrões temporais
        # Padrão de pico de CPU às segundas-feiras
        patterns.append(PatternResult(
            pattern_name="Pico de CPU Segunda-feira",
            frequency=4,  # 4 vezes por mês
            last_occurrence=datetime.now() - timedelta(days=7),
            correlation_strength=0.85,
            related_events=["Backup semanal", "Sincronização de dados"],
            business_impact="Lentidão no início da semana"
        ))
        
        return patterns
    
    def _find_correlation_patterns(self, data: List[Dict[str, Any]]) -> List[PatternResult]:
        """Encontra padrões de correlação"""
        patterns = []
        
        # Simulação de correlações
        patterns.append(PatternResult(
            pattern_name="Correlação Temperatura-Performance",
            frequency=10,
            last_occurrence=datetime.now() - timedelta(days=2),
            correlation_strength=0.92,
            related_events=["Alta temperatura", "Queda de performance"],
            business_impact="Degradação de performance em dias quentes"
        ))
        
        return patterns
    
    def _find_frequency_patterns(self, data: List[Dict[str, Any]]) -> List[PatternResult]:
        """Encontra padrões de frequência"""
        patterns = []
        
        # Simulação de padrões de frequência
        patterns.append(PatternResult(
            pattern_name="Reinicializações Frequentes",
            frequency=3,
            last_occurrence=datetime.now() - timedelta(days=5),
            correlation_strength=0.78,
            related_events=["Falha de memória", "Travamento de sistema"],
            business_impact="Interrupções no trabalho"
        ))
        
        return patterns

class RecommendationEngine:
    """Motor de recomendações personalizadas"""
    
    def __init__(self):
        self.user_profiles = {}
        self.recommendation_history = {}
        self.effectiveness_scores = {}
        
    async def generate_recommendations(self, 
                                     user_id: str, 
                                     system_state: Dict[str, Any],
                                     user_preferences: Dict[str, Any] = None) -> List[Recommendation]:
        """Gera recomendações personalizadas"""
        try:
            recommendations = []
            
            # Recomendações baseadas no estado do sistema
            system_recommendations = self._get_system_recommendations(system_state)
            recommendations.extend(system_recommendations)
            
            # Recomendações baseadas no perfil do usuário
            if user_id in self.user_profiles:
                profile_recommendations = self._get_profile_recommendations(user_id, system_state)
                recommendations.extend(profile_recommendations)
            
            # Recomendações baseadas em preferências
            if user_preferences:
                preference_recommendations = self._get_preference_recommendations(user_preferences, system_state)
                recommendations.extend(preference_recommendations)
            
            # Ordenar por prioridade e relevância
            recommendations = self._prioritize_recommendations(recommendations)
            
            # Armazenar no histórico
            self.recommendation_history[user_id] = recommendations
            
            logger.info(f"Geradas {len(recommendations)} recomendações para usuário {user_id}")
            return recommendations[:10]  # Top 10
            
        except Exception as e:
            logger.error(f"Erro na geração de recomendações: {e}")
            return []
    
    def _get_system_recommendations(self, system_state: Dict[str, Any]) -> List[Recommendation]:
        """Gera recomendações baseadas no estado do sistema"""
        recommendations = []
        
        # Verificar uso de CPU
        cpu_usage = system_state.get('cpu', {}).get('usage_percent', 0)
        if cpu_usage > 80:
            recommendations.append(Recommendation(
                title="Otimizar Uso de CPU",
                description="O uso de CPU está alto. Considere otimizar processos em execução.",
                priority="ALTA",
                category="Performance",
                estimated_impact="Melhoria de 20-30% na responsividade",
                implementation_steps=[
                    "Identificar processos com maior uso de CPU",
                    "Finalizar processos desnecessários",
                    "Configurar prioridades de processo",
                    "Considerar upgrade de hardware"
                ],
                resources_needed=["Tempo: 15-30 minutos", "Conhecimento: Básico"]
            ))
        
        # Verificar espaço em disco
        disk_usage = system_state.get('disk', {}).get('usage_percent', 0)
        if disk_usage > 85:
            recommendations.append(Recommendation(
                title="Liberar Espaço em Disco",
                description="O disco está quase cheio. Libere espaço para evitar problemas.",
                priority="MÉDIA",
                category="Manutenção",
                estimated_impact="Prevenção de falhas do sistema",
                implementation_steps=[
                    "Executar limpeza de disco",
                    "Remover arquivos temporários",
                    "Desinstalar programas não utilizados",
                    "Mover arquivos para armazenamento externo"
                ],
                resources_needed=["Tempo: 30-60 minutos", "Conhecimento: Básico"]
            ))
        
        return recommendations
    
    def _get_profile_recommendations(self, user_id: str, system_state: Dict[str, Any]) -> List[Recommendation]:
        """Gera recomendações baseadas no perfil do usuário"""
        recommendations = []
        
        # Simulação de recomendações baseadas em perfil
        profile = self.user_profiles.get(user_id, {})
        
        if profile.get('experience_level') == 'beginner':
            recommendations.append(Recommendation(
                title="Tutorial de Manutenção Básica",
                description="Aprenda técnicas básicas de manutenção do sistema.",
                priority="BAIXA",
                category="Educação",
                estimated_impact="Melhoria na autonomia técnica",
                implementation_steps=[
                    "Assistir tutorial de limpeza de sistema",
                    "Praticar verificação de atualizações",
                    "Aprender sobre backup de dados"
                ],
                resources_needed=["Tempo: 1-2 horas", "Conhecimento: Nenhum"]
            ))
        
        return recommendations
    
    def _get_preference_recommendations(self, preferences: Dict[str, Any], system_state: Dict[str, Any]) -> List[Recommendation]:
        """Gera recomendações baseadas em preferências"""
        recommendations = []
        
        # Simulação de recomendações baseadas em preferências
        if preferences.get('auto_optimization', False):
            recommendations.append(Recommendation(
                title="Ativar Otimização Automática",
                description="Configure otimização automática baseada em suas preferências.",
                priority="MÉDIA",
                category="Automação",
                estimated_impact="Manutenção automática contínua",
                implementation_steps=[
                    "Configurar horários de otimização",
                    "Definir parâmetros de performance",
                    "Ativar notificações de status"
                ],
                resources_needed=["Tempo: 10-15 minutos", "Conhecimento: Intermediário"]
            ))
        
        return recommendations
    
    def _prioritize_recommendations(self, recommendations: List[Recommendation]) -> List[Recommendation]:
        """Prioriza recomendações por importância"""
        priority_order = {"CRÍTICA": 4, "ALTA": 3, "MÉDIA": 2, "BAIXA": 1}
        
        return sorted(recommendations, 
                     key=lambda r: priority_order.get(r.priority, 0), 
                     reverse=True)

# Instâncias globais
predictive_analyzer = PredictiveAnalyzer()
anomaly_detector = AnomalyDetector()
pattern_recognizer = PatternRecognizer()
recommendation_engine = RecommendationEngine()

# Funções de conveniência
async def predict_system_failure(system_data: Dict[str, Any]) -> PredictionResult:
    """Função de conveniência para previsão de falhas"""
    return await predictive_analyzer.predict_failure(system_data)

async def detect_system_anomalies(metrics: Dict[str, Any]) -> List[AnomalyResult]:
    """Função de conveniência para detecção de anomalias"""
    return await anomaly_detector.detect_anomalies(metrics)

async def recognize_data_patterns(historical_data: List[Dict[str, Any]]) -> List[PatternResult]:
    """Função de conveniência para reconhecimento de padrões"""
    return await pattern_recognizer.recognize_patterns(historical_data)

async def get_personalized_recommendations(user_id: str, 
                                         system_state: Dict[str, Any],
                                         preferences: Dict[str, Any] = None) -> List[Recommendation]:
    """Função de conveniência para recomendações"""
    return await recommendation_engine.generate_recommendations(user_id, system_state, preferences)