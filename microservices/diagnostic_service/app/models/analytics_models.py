"""
Modelos de dados para funcionalidades de Analytics Avançado
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class ReportType(str, Enum):
    """Tipos de relatório disponíveis"""
    PERFORMANCE = "performance"
    USAGE = "usage"
    TRENDS = "trends"
    PREDICTIVE = "predictive"
    CUSTOM = "custom"
    SECURITY = "security"
    COMPLIANCE = "compliance"

class MetricType(str, Enum):
    """Tipos de métrica"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class AggregationType(str, Enum):
    """Tipos de agregação"""
    SUM = "sum"
    AVG = "avg"
    MIN = "min"
    MAX = "max"
    COUNT = "count"
    PERCENTILE = "percentile"

class AnalyticsRequest(BaseModel):
    """Solicitação de análise"""
    analysis_type: str
    data_sources: List[str]
    time_range: Dict[str, datetime]
    filters: Optional[Dict[str, Any]] = None
    aggregation: AggregationType = AggregationType.AVG
    granularity: str = Field(default="hour", regex="^(minute|hour|day|week|month)$")
    include_predictions: bool = False

class AnalyticsResponse(BaseModel):
    """Resposta de análise"""
    analysis_id: str
    analysis_type: str
    results: Dict[str, Any]
    insights: List[str]
    recommendations: List[str]
    confidence_score: float
    data_quality_score: float
    processing_time: int
    generated_at: datetime

class ReportRequest(BaseModel):
    """Solicitação de relatório"""
    report_type: ReportType
    report_name: str
    start_date: datetime
    end_date: datetime
    components: List[str] = []
    metrics: List[str] = []
    custom_parameters: Optional[Dict[str, Any]] = None
    format: str = Field(default="json", regex="^(json|pdf|excel|csv)$")
    email_delivery: bool = False
    email_recipients: List[str] = []
    schedule: Optional[str] = None  # Cron expression

class ReportResponse(BaseModel):
    """Resposta de relatório"""
    report_id: str
    report_type: ReportType
    status: str
    data: Dict[str, Any]
    summary: str
    insights: List[str]
    recommendations: List[str]
    generated_at: datetime
    file_url: Optional[str] = None
    expires_at: Optional[datetime] = None

class MetricsQuery(BaseModel):
    """Consulta de métricas"""
    metric_names: List[str]
    start_time: datetime
    end_time: datetime
    step: str = "1m"  # Prometheus-style step
    filters: Dict[str, str] = {}
    aggregation: AggregationType = AggregationType.AVG

class MetricsResponse(BaseModel):
    """Resposta de métricas"""
    metrics: Dict[str, Any]
    statistics: Dict[str, Any]
    period: Dict[str, Any]
    metadata: Dict[str, Any]

class TrendAnalysis(BaseModel):
    """Análise de tendências"""
    metric_name: str
    period_analyzed: int
    trend_direction: str  # increasing, decreasing, stable
    trend_strength: float
    slope: float
    r_squared: float
    seasonal_patterns: List[Dict[str, Any]]
    anomalies_detected: List[Dict[str, Any]]
    forecast_next_7_days: List[float]
    comparison_with_previous: Optional[Dict[str, Any]] = None
    insights: List[str]
    confidence_level: float
    analyzed_at: datetime

class PerformanceReport(BaseModel):
    """Relatório de performance"""
    component: str
    period_hours: int
    overall_score: float
    cpu_score: float
    memory_score: float
    disk_score: float
    network_score: float
    response_time_avg: float
    response_time_p95: float
    error_rate: float
    throughput: float
    availability: float
    bottlenecks: List[Dict[str, Any]]
    recommendations: List[str]
    trend_indicators: Dict[str, Any]
    generated_at: datetime

class UsageStatistics(BaseModel):
    """Estatísticas de uso"""
    period_days: int
    total_sessions: int
    unique_users: int
    total_api_calls: int
    average_session_duration: int
    peak_concurrent_users: int
    most_used_features: List[str]
    usage_by_time: Dict[str, Any]
    geographic_distribution: Dict[str, Any]
    device_types: Dict[str, Any]
    user_retention_rate: float
    new_vs_returning_users: Dict[str, Any]
    feature_adoption_rates: Dict[str, float]
    usage_trends: Dict[str, Any]
    generated_at: datetime

class PredictiveInsights(BaseModel):
    """Insights preditivos"""
    forecast_period_days: int
    confidence_level: float
    resource_usage_forecast: Dict[str, List[float]]
    performance_forecast: Dict[str, List[float]]
    capacity_requirements: Dict[str, Any]
    potential_issues: List[Dict[str, Any]]
    recommended_actions: List[str]
    cost_projections: Dict[str, float]
    scaling_recommendations: Dict[str, Any]
    maintenance_windows: List[Dict[str, Any]]
    scenarios: Dict[str, str]
    model_accuracy: float
    last_updated: datetime

class DataPoint(BaseModel):
    """Ponto de dados"""
    timestamp: datetime
    value: Union[float, int, str]
    tags: Dict[str, str] = {}
    metadata: Dict[str, Any] = {}

class TimeSeries(BaseModel):
    """Série temporal"""
    metric_name: str
    data_points: List[DataPoint]
    aggregation_type: AggregationType
    resolution: str
    start_time: datetime
    end_time: datetime
    total_points: int

class Dashboard(BaseModel):
    """Dashboard"""
    dashboard_id: str
    name: str
    description: str
    widgets: List[Dict[str, Any]]
    layout: Dict[str, Any]
    refresh_interval: int = 300
    filters: Dict[str, Any] = {}
    permissions: Dict[str, List[str]] = {}
    created_by: str
    created_at: datetime
    last_modified: datetime

class Widget(BaseModel):
    """Widget do dashboard"""
    widget_id: str
    widget_type: str  # chart, table, metric, alert
    title: str
    data_source: str
    query: Dict[str, Any]
    visualization_config: Dict[str, Any]
    position: Dict[str, int]
    size: Dict[str, int]
    refresh_interval: int = 300

class Alert(BaseModel):
    """Alerta"""
    alert_id: str
    alert_name: str
    description: str
    metric_name: str
    condition: str  # >, <, ==, !=, etc.
    threshold: float
    severity: str = Field(regex="^(info|warning|critical)$")
    enabled: bool = True
    notification_channels: List[str]
    created_at: datetime
    last_triggered: Optional[datetime] = None

class AlertRule(BaseModel):
    """Regra de alerta"""
    rule_id: str
    rule_name: str
    expression: str  # PromQL-like expression
    duration: str = "5m"
    labels: Dict[str, str] = {}
    annotations: Dict[str, str] = {}
    severity: str
    enabled: bool = True

class Notification(BaseModel):
    """Notificação"""
    notification_id: str
    alert_id: str
    channel: str  # email, slack, webhook, etc.
    recipient: str
    subject: str
    message: str
    sent_at: datetime
    delivered: bool = False
    read: bool = False

class AnalyticsJob(BaseModel):
    """Job de analytics"""
    job_id: str
    job_type: str
    status: str = Field(regex="^(pending|running|completed|failed|cancelled)$")
    progress: float = Field(ge=0.0, le=1.0)
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result_location: Optional[str] = None

class DataSource(BaseModel):
    """Fonte de dados"""
    source_id: str
    source_name: str
    source_type: str  # database, api, file, stream
    connection_config: Dict[str, Any]
    schema_definition: Dict[str, Any]
    last_sync: Optional[datetime] = None
    sync_frequency: str = "hourly"
    enabled: bool = True
    health_status: str = "healthy"

class DataPipeline(BaseModel):
    """Pipeline de dados"""
    pipeline_id: str
    pipeline_name: str
    description: str
    source_id: str
    destination_id: str
    transformation_steps: List[Dict[str, Any]]
    schedule: str  # Cron expression
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    success_rate: float = 1.0

class DataQuality(BaseModel):
    """Qualidade dos dados"""
    dataset_id: str
    quality_score: float = Field(ge=0.0, le=1.0)
    completeness: float = Field(ge=0.0, le=1.0)
    accuracy: float = Field(ge=0.0, le=1.0)
    consistency: float = Field(ge=0.0, le=1.0)
    timeliness: float = Field(ge=0.0, le=1.0)
    validity: float = Field(ge=0.0, le=1.0)
    issues_found: List[str]
    recommendations: List[str]
    assessed_at: datetime

class AnalyticsModel(BaseModel):
    """Modelo de analytics"""
    model_id: str
    model_name: str
    model_type: str  # regression, classification, clustering, forecasting
    algorithm: str
    parameters: Dict[str, Any]
    training_data: str
    accuracy: float
    last_trained: datetime
    version: str
    status: str = "active"

class Forecast(BaseModel):
    """Previsão"""
    forecast_id: str
    metric_name: str
    forecast_horizon: int  # days
    predicted_values: List[float]
    confidence_intervals: List[Dict[str, float]]
    model_used: str
    accuracy_score: float
    created_at: datetime
    valid_until: datetime

class Anomaly(BaseModel):
    """Anomalia"""
    anomaly_id: str
    metric_name: str
    timestamp: datetime
    actual_value: float
    expected_value: float
    deviation_score: float
    severity: str = Field(regex="^(low|medium|high|critical)$")
    description: str
    root_cause: Optional[str] = None
    resolved: bool = False

class BusinessMetric(BaseModel):
    """Métrica de negócio"""
    metric_id: str
    metric_name: str
    description: str
    calculation_formula: str
    target_value: Optional[float] = None
    current_value: float
    trend: str  # up, down, stable
    impact_level: str = Field(regex="^(low|medium|high|critical)$")
    owner: str
    last_updated: datetime

class KPI(BaseModel):
    """Indicador-chave de performance"""
    kpi_id: str
    kpi_name: str
    description: str
    target: float
    current_value: float
    previous_value: float
    change_percentage: float
    status: str = Field(regex="^(on_track|at_risk|off_track)$")
    measurement_unit: str
    frequency: str  # daily, weekly, monthly
    owner: str
    last_updated: datetime

class AnalyticsExport(BaseModel):
    """Exportação de analytics"""
    export_id: str
    export_type: str  # report, dashboard, dataset
    format: str = Field(regex="^(pdf|excel|csv|json|png)$")
    file_path: str
    file_size: int
    created_at: datetime
    expires_at: datetime
    download_count: int = 0
    password_protected: bool = False

class AnalyticsConfig(BaseModel):
    """Configuração de analytics"""
    config_id: str
    component: str
    settings: Dict[str, Any]
    default_retention_days: int = 90
    max_query_duration: int = 300
    cache_enabled: bool = True
    cache_ttl: int = 3600
    rate_limit: Dict[str, int] = {}
    last_modified: datetime

class UserAnalytics(BaseModel):
    """Analytics de usuário"""
    user_id: str
    session_count: int
    total_time_spent: int  # seconds
    features_used: List[str]
    last_activity: datetime
    user_journey: List[Dict[str, Any]]
    conversion_events: List[str]
    retention_score: float
    engagement_score: float

class SystemHealth(BaseModel):
    """Saúde do sistema"""
    component: str
    status: str = Field(regex="^(healthy|warning|critical|unknown)$")
    uptime_percentage: float
    response_time_avg: float
    error_rate: float
    resource_usage: Dict[str, float]
    last_incident: Optional[datetime] = None
    health_score: float = Field(ge=0.0, le=100.0)
    checked_at: datetime

class CapacityPlanning(BaseModel):
    """Planejamento de capacidade"""
    resource_type: str
    current_capacity: float
    current_usage: float
    utilization_percentage: float
    projected_usage: Dict[str, float]  # next 30, 60, 90 days
    recommended_capacity: float
    scaling_trigger: float
    cost_implications: Dict[str, float]
    recommendations: List[str]
    analyzed_at: datetime

class PerformanceBenchmark(BaseModel):
    """Benchmark de performance"""
    benchmark_id: str
    benchmark_name: str
    component: str
    baseline_metrics: Dict[str, float]
    current_metrics: Dict[str, float]
    performance_delta: Dict[str, float]
    regression_detected: bool
    improvement_areas: List[str]
    benchmark_date: datetime

class AnalyticsInsight(BaseModel):
    """Insight de analytics"""
    insight_id: str
    insight_type: str
    title: str
    description: str
    impact_level: str = Field(regex="^(low|medium|high|critical)$")
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_data: Dict[str, Any]
    recommended_actions: List[str]
    generated_at: datetime
    expires_at: Optional[datetime] = None

class AnalyticsAudit(BaseModel):
    """Auditoria de analytics"""
    audit_id: str
    action: str
    user_id: str
    resource_type: str
    resource_id: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    success: bool
    details: Dict[str, Any]

class AnalyticsSubscription(BaseModel):
    """Assinatura de analytics"""
    subscription_id: str
    user_id: str
    report_type: str
    frequency: str  # daily, weekly, monthly
    delivery_method: str = Field(regex="^(email|webhook|dashboard)$")
    filters: Dict[str, Any] = {}
    enabled: bool = True
    last_delivery: Optional[datetime] = None
    next_delivery: Optional[datetime] = None
    created_at: datetime