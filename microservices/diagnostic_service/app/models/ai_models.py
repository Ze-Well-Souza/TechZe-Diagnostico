"""
Modelos de dados para funcionalidades de IA
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class PredictionType(str, Enum):
    """Tipos de predição disponíveis"""
    PERFORMANCE = "performance"
    RESOURCE_USAGE = "resource_usage"
    FAILURE_PREDICTION = "failure_prediction"
    CAPACITY_PLANNING = "capacity_planning"
    USER_BEHAVIOR = "user_behavior"

class ModelStatus(str, Enum):
    """Status do modelo de ML"""
    TRAINING = "training"
    READY = "ready"
    UPDATING = "updating"
    ERROR = "error"
    DEPRECATED = "deprecated"

class PredictionRequest(BaseModel):
    """Solicitação de predição"""
    prediction_type: PredictionType
    historical_data: Dict[str, Any]
    time_horizon: int = Field(default=7, description="Horizonte de predição em dias")
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    include_uncertainty: bool = True
    custom_parameters: Optional[Dict[str, Any]] = None

class PredictionResponse(BaseModel):
    """Resposta de predição"""
    prediction_id: str
    prediction_type: PredictionType
    predicted_values: Dict[str, Any]
    confidence_score: float
    time_horizon: int
    risk_factors: List[str]
    recommendations: List[str]
    uncertainty_bounds: Optional[Dict[str, Any]] = None
    model_version: str
    created_at: datetime

class AnomalyDetectionRequest(BaseModel):
    """Solicitação de detecção de anomalias"""
    metrics: Dict[str, List[float]]
    sensitivity: float = Field(default=0.95, ge=0.5, le=1.0)
    time_window: int = Field(default=60, description="Janela de tempo em minutos")
    baseline_period: int = Field(default=7, description="Período base em dias")
    detection_methods: List[str] = ["statistical", "ml_based"]

class AnomalyDetectionResponse(BaseModel):
    """Resposta de detecção de anomalias"""
    detection_id: str
    anomalies_found: List[Dict[str, Any]]
    severity_scores: Dict[str, float]
    affected_components: List[str]
    root_cause_analysis: Dict[str, Any]
    recommended_actions: List[str]
    confidence_level: float
    detection_timestamp: datetime

class PatternAnalysisRequest(BaseModel):
    """Solicitação de análise de padrões"""
    system_data: Dict[str, Any]
    analysis_period: int = Field(default=30, description="Período de análise em dias")
    pattern_types: List[str] = ["seasonal", "trend", "cyclical", "irregular"]
    granularity: str = Field(default="hour", regex="^(minute|hour|day|week)$")
    min_pattern_strength: float = Field(default=0.7, ge=0.0, le=1.0)

class PatternAnalysisResponse(BaseModel):
    """Resposta de análise de padrões"""
    analysis_id: str
    identified_patterns: List[Dict[str, Any]]
    pattern_strength: Dict[str, float]
    seasonal_trends: Dict[str, Any]
    usage_patterns: Dict[str, Any]
    performance_cycles: Dict[str, Any]
    insights: List[str]
    analysis_timestamp: datetime

class RecommendationRequest(BaseModel):
    """Solicitação de recomendações"""
    system_state: Dict[str, Any]
    user_preferences: Optional[Dict[str, Any]] = None
    context: str = Field(description="Contexto da recomendação")
    priority_level: str = Field(default="medium", regex="^(low|medium|high|critical)$")
    max_recommendations: int = Field(default=5, ge=1, le=20)

class RecommendationResponse(BaseModel):
    """Resposta de recomendações"""
    recommendation_id: str
    recommendations: List[Dict[str, Any]]
    priority_scores: Dict[str, float]
    expected_impact: Dict[str, Any]
    implementation_difficulty: Dict[str, str]
    estimated_time: Dict[str, int]
    risk_assessment: Dict[str, str]
    success_probability: Dict[str, float]
    generated_at: datetime

class MLModelInfo(BaseModel):
    """Informações do modelo de ML"""
    model_id: str
    model_name: str
    model_type: str
    version: str
    accuracy: float
    last_trained: datetime
    training_data_size: int
    features_count: int
    status: ModelStatus
    performance_metrics: Optional[Dict[str, float]] = None

class TrainingRequest(BaseModel):
    """Solicitação de treinamento de modelo"""
    model_type: str = Field(regex="^(predictive|anomaly|pattern|recommendation)$")
    training_data: List[Dict[str, Any]]
    model_parameters: Optional[Dict[str, Any]] = None
    validation_split: float = Field(default=0.2, ge=0.1, le=0.5)
    cross_validation: bool = True
    hyperparameter_tuning: bool = False
    estimated_duration: Optional[int] = None

class TrainingResponse(BaseModel):
    """Resposta de treinamento de modelo"""
    training_id: str
    model_type: str
    status: str
    estimated_duration: int
    data_size: int
    started_at: datetime
    progress_url: Optional[str] = None

class ModelPerformanceMetrics(BaseModel):
    """Métricas de performance do modelo"""
    model_id: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: Optional[float] = None
    mean_absolute_error: Optional[float] = None
    root_mean_square_error: Optional[float] = None
    training_time: int
    inference_time: float
    last_evaluated: datetime

class FeatureImportance(BaseModel):
    """Importância das features"""
    feature_name: str
    importance_score: float
    description: str
    data_type: str

class ModelExplanation(BaseModel):
    """Explicação do modelo"""
    model_id: str
    prediction_id: str
    feature_contributions: List[FeatureImportance]
    decision_path: List[str]
    confidence_factors: Dict[str, float]
    alternative_outcomes: List[Dict[str, Any]]
    explanation_text: str

class AISystemHealth(BaseModel):
    """Saúde do sistema de IA"""
    overall_status: str
    model_statuses: Dict[str, ModelStatus]
    prediction_accuracy: Dict[str, float]
    processing_latency: Dict[str, float]
    resource_usage: Dict[str, float]
    error_rates: Dict[str, float]
    last_health_check: datetime
    recommendations: List[str]

class DataQualityReport(BaseModel):
    """Relatório de qualidade dos dados"""
    dataset_id: str
    total_records: int
    missing_values: Dict[str, int]
    duplicate_records: int
    outliers_detected: int
    data_consistency_score: float
    completeness_score: float
    accuracy_score: float
    timeliness_score: float
    overall_quality_score: float
    issues_found: List[str]
    recommendations: List[str]
    generated_at: datetime

class AutoMLRequest(BaseModel):
    """Solicitação de AutoML"""
    problem_type: str = Field(regex="^(classification|regression|clustering|forecasting)$")
    target_variable: str
    dataset: Dict[str, Any]
    max_training_time: int = Field(default=3600, description="Tempo máximo em segundos")
    optimization_metric: str = "auto"
    cross_validation_folds: int = Field(default=5, ge=3, le=10)
    feature_selection: bool = True
    hyperparameter_optimization: bool = True

class AutoMLResponse(BaseModel):
    """Resposta de AutoML"""
    automl_id: str
    problem_type: str
    best_model: Dict[str, Any]
    model_performance: ModelPerformanceMetrics
    feature_importance: List[FeatureImportance]
    training_summary: Dict[str, Any]
    deployment_ready: bool
    model_explanation: str
    created_at: datetime

class PredictionExplanation(BaseModel):
    """Explicação de predição"""
    prediction_id: str
    input_features: Dict[str, Any]
    prediction_value: Union[float, str, List[Any]]
    confidence: float
    feature_contributions: List[FeatureImportance]
    similar_cases: List[Dict[str, Any]]
    counterfactual_examples: List[Dict[str, Any]]
    explanation_text: str
    visual_explanation_url: Optional[str] = None

class ModelDriftReport(BaseModel):
    """Relatório de drift do modelo"""
    model_id: str
    drift_detected: bool
    drift_score: float
    drift_type: str  # "data_drift", "concept_drift", "prediction_drift"
    affected_features: List[str]
    drift_magnitude: Dict[str, float]
    detection_method: str
    baseline_period: str
    comparison_period: str
    recommendations: List[str]
    retraining_required: bool
    detected_at: datetime

class AIInsight(BaseModel):
    """Insight gerado por IA"""
    insight_id: str
    insight_type: str
    title: str
    description: str
    confidence: float
    impact_level: str
    supporting_data: Dict[str, Any]
    recommended_actions: List[str]
    related_metrics: List[str]
    generated_by_model: str
    created_at: datetime
    expires_at: Optional[datetime] = None

class ModelComparison(BaseModel):
    """Comparação entre modelos"""
    comparison_id: str
    models_compared: List[str]
    comparison_metrics: Dict[str, Dict[str, float]]
    best_model: str
    performance_differences: Dict[str, float]
    statistical_significance: Dict[str, bool]
    recommendation: str
    comparison_summary: str
    performed_at: datetime

class AIWorkflow(BaseModel):
    """Workflow de IA"""
    workflow_id: str
    workflow_name: str
    description: str
    steps: List[Dict[str, Any]]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    execution_time: Optional[int] = None
    success_rate: Optional[float] = None
    last_execution: Optional[datetime] = None
    status: str
    created_at: datetime

class AIWorkflowExecution(BaseModel):
    """Execução de workflow de IA"""
    execution_id: str
    workflow_id: str
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]] = None
    status: str
    progress: float = Field(ge=0.0, le=1.0)
    current_step: str
    error_message: Optional[str] = None
    execution_time: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

class ModelVersioning(BaseModel):
    """Versionamento de modelo"""
    model_id: str
    version: str
    parent_version: Optional[str] = None
    changes_description: str
    performance_comparison: Optional[Dict[str, float]] = None
    deployment_status: str
    created_by: str
    created_at: datetime
    model_artifacts: Dict[str, str]
    metadata: Dict[str, Any]

class AIExperiment(BaseModel):
    """Experimento de IA"""
    experiment_id: str
    experiment_name: str
    description: str
    hypothesis: str
    methodology: str
    parameters: Dict[str, Any]
    results: Optional[Dict[str, Any]] = None
    conclusions: Optional[str] = None
    status: str
    created_by: str
    started_at: datetime
    completed_at: Optional[datetime] = None

class ModelMonitoring(BaseModel):
    """Monitoramento de modelo"""
    model_id: str
    monitoring_period: str
    predictions_count: int
    average_confidence: float
    accuracy_trend: List[float]
    latency_trend: List[float]
    error_rate: float
    data_quality_score: float
    drift_alerts: List[str]
    performance_alerts: List[str]
    last_updated: datetime

class AIResourceUsage(BaseModel):
    """Uso de recursos de IA"""
    resource_type: str
    usage_period: str
    cpu_usage: Dict[str, float]
    memory_usage: Dict[str, float]
    gpu_usage: Optional[Dict[str, float]] = None
    storage_usage: Dict[str, float]
    network_io: Dict[str, float]
    cost_breakdown: Dict[str, float]
    optimization_suggestions: List[str]
    measured_at: datetime