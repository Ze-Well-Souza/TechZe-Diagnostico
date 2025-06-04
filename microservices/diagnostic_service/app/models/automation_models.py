"""
Modelos de dados para funcionalidades de Automação
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class AutoFixType(str, Enum):
    """Tipos de correção automática"""
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    DISK_CLEANUP = "disk_cleanup"
    MEMORY_OPTIMIZATION = "memory_optimization"
    REGISTRY_CLEANUP = "registry_cleanup"
    DRIVER_UPDATE = "driver_update"
    SERVICE_RESTART = "service_restart"
    NETWORK_RESET = "network_reset"
    SECURITY_PATCH = "security_patch"

class TaskStatus(str, Enum):
    """Status da tarefa de automação"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"
    PAUSED = "paused"

class RiskLevel(str, Enum):
    """Nível de risco da automação"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AutoFixRequest(BaseModel):
    """Solicitação de correção automática"""
    problem_type: AutoFixType
    severity: str = Field(regex="^(low|medium|high|critical)$")
    system_state: Dict[str, Any]
    parameters: Optional[Dict[str, Any]] = None
    safety_checks: bool = True
    execute_immediately: bool = False
    rollback_enabled: bool = True
    notification_settings: Optional[Dict[str, Any]] = None

class AutoFixResponse(BaseModel):
    """Resposta de correção automática"""
    fix_id: str
    problem_type: AutoFixType
    status: TaskStatus
    success: bool
    actions_taken: List[str]
    error_message: Optional[str] = None
    execution_time: int
    risk_level: RiskLevel
    rollback_available: bool
    rollback_steps: Optional[List[str]] = None
    verification_results: Optional[Dict[str, Any]] = None
    created_at: datetime

class WorkflowStep(BaseModel):
    """Passo do workflow"""
    step_id: str
    step_name: str
    step_type: str
    parameters: Dict[str, Any]
    dependencies: List[str] = []
    timeout: int = 300
    retry_count: int = 0
    on_failure: str = "stop"  # stop, continue, retry
    conditions: Optional[Dict[str, Any]] = None

class WorkflowTrigger(BaseModel):
    """Gatilho do workflow"""
    trigger_type: str  # schedule, event, manual, condition
    trigger_config: Dict[str, Any]
    enabled: bool = True

class WorkflowRequest(BaseModel):
    """Solicitação de workflow"""
    workflow_name: str
    description: str
    steps: List[WorkflowStep]
    triggers: List[WorkflowTrigger] = []
    schedule: Optional[str] = None  # Cron expression
    execute_immediately: bool = False
    notification_settings: Optional[Dict[str, Any]] = None
    timeout: int = 3600

class WorkflowResponse(BaseModel):
    """Resposta de workflow"""
    workflow_id: str
    workflow_name: str
    status: TaskStatus
    steps_count: int
    estimated_duration: int
    next_execution: Optional[datetime] = None
    triggers_active: bool
    created_at: datetime

class OptimizationRequest(BaseModel):
    """Solicitação de otimização"""
    optimization_type: str = Field(regex="^(performance|resource|cost|energy)$")
    target_resources: List[str]
    target_metrics: Dict[str, float]
    constraints: Optional[Dict[str, Any]] = None
    safety_mode: bool = True
    execute_immediately: bool = False
    optimization_level: str = Field(default="moderate", regex="^(conservative|moderate|aggressive)$")

class OptimizationResponse(BaseModel):
    """Resposta de otimização"""
    optimization_id: str
    optimization_type: str
    status: TaskStatus
    improvements_achieved: Dict[str, float]
    resources_optimized: List[str]
    performance_gain: Optional[Dict[str, float]] = None
    execution_time: int
    rollback_available: bool
    next_optimization: Optional[datetime] = None
    created_at: datetime

class AutomationTask(BaseModel):
    """Tarefa de automação"""
    task_id: str
    task_name: str
    task_type: str
    status: TaskStatus
    progress: float = Field(ge=0.0, le=1.0)
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None

class AutomationStatus(BaseModel):
    """Status detalhado da automação"""
    task_id: str
    status: TaskStatus
    progress: float
    current_step: Optional[str] = None
    steps_completed: int
    total_steps: int
    execution_time: int
    estimated_remaining: Optional[int] = None
    resource_usage: Dict[str, float]
    logs: List[str]
    last_updated: datetime

class ScheduledTask(BaseModel):
    """Tarefa agendada"""
    schedule_id: str
    task_name: str
    task_type: str
    schedule_expression: str  # Cron expression
    next_execution: datetime
    last_execution: Optional[datetime] = None
    execution_count: int
    success_count: int
    failure_count: int
    enabled: bool
    created_at: datetime

class AutomationRule(BaseModel):
    """Regra de automação"""
    rule_id: Optional[str] = None
    rule_name: str
    rule_type: str
    description: str
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    enabled: bool = True
    priority: int = Field(default=5, ge=1, le=10)
    cooldown_period: int = 300  # seconds
    max_executions_per_hour: int = 10
    created_at: Optional[datetime] = None

class WorkflowExecution(BaseModel):
    """Execução de workflow"""
    execution_id: str
    workflow_id: str
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    steps_executed: List[Dict[str, Any]]
    current_step: Optional[str] = None
    progress: float
    error_details: Optional[Dict[str, Any]] = None
    execution_context: Dict[str, Any]

class AutomationMetrics(BaseModel):
    """Métricas de automação"""
    metric_name: str
    metric_value: float
    metric_unit: str
    timestamp: datetime
    tags: Dict[str, str]
    threshold_breached: bool = False

class AutomationAlert(BaseModel):
    """Alerta de automação"""
    alert_id: str
    alert_type: str
    severity: str
    title: str
    description: str
    source_task: str
    triggered_at: datetime
    acknowledged: bool = False
    resolved: bool = False
    resolution_notes: Optional[str] = None

class ResourceOptimizationPlan(BaseModel):
    """Plano de otimização de recursos"""
    plan_id: str
    target_resources: List[str]
    current_state: Dict[str, Any]
    target_state: Dict[str, Any]
    optimization_steps: List[Dict[str, Any]]
    expected_improvements: Dict[str, float]
    risk_assessment: Dict[str, str]
    estimated_duration: int
    rollback_plan: List[Dict[str, Any]]

class AutomationPolicy(BaseModel):
    """Política de automação"""
    policy_id: str
    policy_name: str
    description: str
    scope: List[str]  # Components or systems affected
    rules: List[AutomationRule]
    enforcement_level: str = Field(regex="^(advisory|enforced|strict)$")
    exceptions: List[Dict[str, Any]] = []
    effective_from: datetime
    expires_at: Optional[datetime] = None
    created_by: str
    approved_by: Optional[str] = None

class AutomationReport(BaseModel):
    """Relatório de automação"""
    report_id: str
    report_type: str
    period_start: datetime
    period_end: datetime
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    average_execution_time: float
    resource_savings: Dict[str, float]
    error_analysis: Dict[str, Any]
    recommendations: List[str]
    generated_at: datetime

class ProcessAutomationConfig(BaseModel):
    """Configuração de automação de processo"""
    config_id: str
    process_name: str
    automation_level: str = Field(regex="^(manual|semi_auto|full_auto)$")
    trigger_conditions: Dict[str, Any]
    automation_steps: List[Dict[str, Any]]
    approval_required: bool = False
    notification_settings: Dict[str, Any]
    rollback_settings: Dict[str, Any]
    monitoring_settings: Dict[str, Any]

class AutomationTemplate(BaseModel):
    """Template de automação"""
    template_id: str
    template_name: str
    description: str
    category: str
    template_type: str
    parameters: List[Dict[str, Any]]
    default_values: Dict[str, Any]
    workflow_definition: Dict[str, Any]
    prerequisites: List[str]
    estimated_duration: int
    complexity_level: str
    created_by: str
    created_at: datetime

class AutomationAudit(BaseModel):
    """Auditoria de automação"""
    audit_id: str
    task_id: str
    action_type: str
    performed_by: str  # user or system
    timestamp: datetime
    details: Dict[str, Any]
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    success: bool
    impact_assessment: Optional[str] = None

class AutomationDashboard(BaseModel):
    """Dashboard de automação"""
    dashboard_id: str
    dashboard_name: str
    widgets: List[Dict[str, Any]]
    layout: Dict[str, Any]
    refresh_interval: int = 300
    filters: Dict[str, Any] = {}
    permissions: Dict[str, List[str]] = {}
    created_by: str
    created_at: datetime
    last_modified: datetime

class AutomationNotification(BaseModel):
    """Notificação de automação"""
    notification_id: str
    notification_type: str
    recipient: str
    subject: str
    message: str
    priority: str = Field(regex="^(low|medium|high|urgent)$")
    delivery_method: str = Field(regex="^(email|sms|webhook|in_app)$")
    sent_at: Optional[datetime] = None
    delivered: bool = False
    read: bool = False
    related_task: Optional[str] = None

class AutomationBackup(BaseModel):
    """Backup de automação"""
    backup_id: str
    backup_type: str  # full, incremental, differential
    source_system: str
    backup_size: int
    compression_ratio: float
    encryption_enabled: bool
    backup_location: str
    retention_period: int
    created_at: datetime
    verified: bool = False
    restoration_tested: bool = False

class AutomationRecovery(BaseModel):
    """Recuperação de automação"""
    recovery_id: str
    incident_id: str
    recovery_type: str
    recovery_steps: List[Dict[str, Any]]
    estimated_recovery_time: int
    actual_recovery_time: Optional[int] = None
    success_rate: float
    data_loss: bool = False
    services_affected: List[str]
    recovery_status: str
    started_at: datetime
    completed_at: Optional[datetime] = None

class AutomationCompliance(BaseModel):
    """Conformidade de automação"""
    compliance_id: str
    regulation_name: str
    compliance_status: str = Field(regex="^(compliant|non_compliant|partial|unknown)$")
    requirements: List[Dict[str, Any]]
    violations: List[Dict[str, Any]]
    remediation_actions: List[str]
    last_assessment: datetime
    next_assessment: datetime
    assessor: str
    evidence_documents: List[str]

class AutomationIntegration(BaseModel):
    """Integração de automação"""
    integration_id: str
    integration_name: str
    integration_type: str
    source_system: str
    target_system: str
    connection_status: str
    data_mapping: Dict[str, str]
    sync_frequency: str
    last_sync: Optional[datetime] = None
    error_count: int = 0
    configuration: Dict[str, Any]
    authentication: Dict[str, Any]

class AutomationCapacity(BaseModel):
    """Capacidade de automação"""
    capacity_id: str
    resource_type: str
    current_usage: float
    maximum_capacity: float
    utilization_percentage: float
    projected_usage: Dict[str, float]
    scaling_recommendations: List[str]
    bottlenecks: List[str]
    optimization_opportunities: List[str]
    measured_at: datetime

class AutomationSLA(BaseModel):
    """SLA de automação"""
    sla_id: str
    service_name: str
    availability_target: float
    performance_target: Dict[str, float]
    current_availability: float
    current_performance: Dict[str, float]
    sla_status: str = Field(regex="^(met|at_risk|breached)$")
    breach_count: int
    last_breach: Optional[datetime] = None
    remediation_time: Optional[int] = None
    penalties: List[Dict[str, Any]] = []