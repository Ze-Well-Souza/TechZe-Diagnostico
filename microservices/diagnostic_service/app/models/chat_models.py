"""
Modelos de dados para funcionalidades de Chat e Assistente IA
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    """Tipos de mensagem"""
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    FILE = "file"
    COMMAND = "command"
    SYSTEM = "system"

class MessageRole(str, Enum):
    """Papel da mensagem"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatSessionStatus(str, Enum):
    """Status da sessão de chat"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ENDED = "ended"
    PAUSED = "paused"

class VoiceCommandType(str, Enum):
    """Tipos de comando de voz"""
    DIAGNOSTIC = "diagnostic"
    OPTIMIZATION = "optimization"
    QUERY = "query"
    NAVIGATION = "navigation"
    CONTROL = "control"

class TutorialType(str, Enum):
    """Tipos de tutorial"""
    BASIC = "basic"
    ADVANCED = "advanced"
    TROUBLESHOOTING = "troubleshooting"
    FEATURE_GUIDE = "feature_guide"
    BEST_PRACTICES = "best_practices"

class ChatMessage(BaseModel):
    """Mensagem de chat"""
    message_id: str
    session_id: str
    role: MessageRole
    message_type: MessageType
    content: str
    metadata: Optional[Dict[str, Any]] = None
    attachments: List[str] = []
    timestamp: datetime
    processed: bool = False
    response_time: Optional[float] = None

class ChatSession(BaseModel):
    """Sessão de chat"""
    session_id: str
    user_id: str
    status: ChatSessionStatus
    started_at: datetime
    last_activity: datetime
    ended_at: Optional[datetime] = None
    message_count: int = 0
    context: Dict[str, Any] = {}
    preferences: Dict[str, Any] = {}
    language: str = "pt-BR"

class ChatResponse(BaseModel):
    """Resposta do chat"""
    response_id: str
    message_id: str
    content: str
    response_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    suggestions: List[str] = []
    actions: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}
    generated_at: datetime
    processing_time: float

class VoiceCommand(BaseModel):
    """Comando de voz"""
    command_id: str
    session_id: str
    audio_data: Optional[str] = None  # Base64 encoded
    transcribed_text: str
    command_type: VoiceCommandType
    confidence: float
    intent: str
    entities: Dict[str, Any] = {}
    processed_at: datetime
    execution_result: Optional[Dict[str, Any]] = None

class VoiceResponse(BaseModel):
    """Resposta de voz"""
    response_id: str
    command_id: str
    text_response: str
    audio_response: Optional[str] = None  # Base64 encoded
    voice_settings: Dict[str, Any] = {}
    generated_at: datetime
    duration: Optional[float] = None

class NLPAnalysis(BaseModel):
    """Análise de processamento de linguagem natural"""
    analysis_id: str
    text: str
    language: str
    intent: str
    confidence: float
    entities: List[Dict[str, Any]]
    sentiment: Dict[str, float]
    keywords: List[str]
    topics: List[str]
    complexity_score: float
    processed_at: datetime

class ChatIntent(BaseModel):
    """Intenção do chat"""
    intent_name: str
    description: str
    examples: List[str]
    parameters: List[Dict[str, Any]]
    responses: List[str]
    actions: List[Dict[str, Any]]
    confidence_threshold: float = 0.7
    enabled: bool = True

class ChatEntity(BaseModel):
    """Entidade do chat"""
    entity_name: str
    entity_type: str
    values: List[str]
    synonyms: Dict[str, List[str]] = {}
    patterns: List[str] = []
    case_sensitive: bool = False
    enabled: bool = True

class Tutorial(BaseModel):
    """Tutorial interativo"""
    tutorial_id: str
    title: str
    description: str
    tutorial_type: TutorialType
    difficulty_level: str = Field(pattern="^(beginner|intermediate|advanced)$")
    estimated_duration: int  # minutes
    steps: List[Dict[str, Any]]
    prerequisites: List[str] = []
    learning_objectives: List[str]
    completion_criteria: Dict[str, Any]
    created_at: datetime

class TutorialProgress(BaseModel):
    """Progresso do tutorial"""
    progress_id: str
    tutorial_id: str
    user_id: str
    session_id: str
    current_step: int
    completed_steps: List[int]
    started_at: datetime
    last_activity: datetime
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    feedback: Optional[str] = None

class ChatContext(BaseModel):
    """Contexto do chat"""
    context_id: str
    session_id: str
    current_topic: str
    conversation_history: List[str]
    user_preferences: Dict[str, Any]
    system_state: Dict[str, Any]
    active_tasks: List[str]
    last_updated: datetime

class ChatAnalytics(BaseModel):
    """Analytics do chat"""
    session_id: str
    total_messages: int
    user_messages: int
    assistant_messages: int
    average_response_time: float
    user_satisfaction: Optional[float] = None
    topics_discussed: List[str]
    intents_triggered: List[str]
    errors_encountered: int
    session_duration: int  # seconds

class ChatFeedback(BaseModel):
    """Feedback do chat"""
    feedback_id: str
    session_id: str
    message_id: Optional[str] = None
    rating: int = Field(ge=1, le=5)
    feedback_text: Optional[str] = None
    feedback_type: str = Field(pattern="^(helpful|not_helpful|incorrect|other)$")
    user_id: str
    submitted_at: datetime

class ChatKnowledgeBase(BaseModel):
    """Base de conhecimento do chat"""
    kb_id: str
    title: str
    content: str
    category: str
    tags: List[str]
    keywords: List[str]
    confidence_score: float
    usage_count: int = 0
    last_updated: datetime
    created_by: str
    approved: bool = False

class ChatTemplate(BaseModel):
    """Template de resposta do chat"""
    template_id: str
    template_name: str
    intent: str
    template_text: str
    variables: List[str] = []
    conditions: Dict[str, Any] = {}
    priority: int = Field(default=5, ge=1, le=10)
    enabled: bool = True
    usage_count: int = 0

class ChatWorkflow(BaseModel):
    """Workflow do chat"""
    workflow_id: str
    workflow_name: str
    description: str
    trigger_intents: List[str]
    steps: List[Dict[str, Any]]
    conditions: Dict[str, Any] = {}
    enabled: bool = True
    created_at: datetime

class ChatIntegration(BaseModel):
    """Integração do chat"""
    integration_id: str
    integration_name: str
    integration_type: str  # api, webhook, database, etc.
    endpoint_url: str
    authentication: Dict[str, Any]
    configuration: Dict[str, Any]
    enabled: bool = True
    last_sync: Optional[datetime] = None

class ChatBot(BaseModel):
    """Configuração do chatbot"""
    bot_id: str
    bot_name: str
    description: str
    personality: Dict[str, Any]
    capabilities: List[str]
    language_models: List[str]
    knowledge_bases: List[str]
    integrations: List[str]
    settings: Dict[str, Any]
    created_at: datetime
    last_updated: datetime

class ChatMetrics(BaseModel):
    """Métricas do chat"""
    metric_name: str
    metric_value: float
    metric_unit: str
    timestamp: datetime
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    tags: Dict[str, str] = {}

class ChatAlert(BaseModel):
    """Alerta do chat"""
    alert_id: str
    alert_type: str
    severity: str = Field(pattern="^(info|warning|error|critical)$")
    message: str
    session_id: Optional[str] = None
    triggered_at: datetime
    resolved: bool = False
    resolution_notes: Optional[str] = None

class ChatAudit(BaseModel):
    """Auditoria do chat"""
    audit_id: str
    session_id: str
    action: str
    user_id: str
    timestamp: datetime
    details: Dict[str, Any]
    ip_address: str
    user_agent: str

class ChatConfiguration(BaseModel):
    """Configuração do chat"""
    config_id: str
    component: str
    settings: Dict[str, Any]
    default_language: str = "pt-BR"
    max_session_duration: int = 3600  # seconds
    max_message_length: int = 1000
    rate_limit: Dict[str, int] = {}
    enabled_features: List[str] = []
    last_modified: datetime

class ChatPersonalization(BaseModel):
    """Personalização do chat"""
    user_id: str
    preferences: Dict[str, Any]
    conversation_style: str
    topics_of_interest: List[str]
    skill_level: str = Field(pattern="^(beginner|intermediate|advanced|expert)$")
    language: str = "pt-BR"
    notification_settings: Dict[str, bool] = {}
    last_updated: datetime

class ChatSuggestion(BaseModel):
    """Sugestão do chat"""
    suggestion_id: str
    suggestion_text: str
    suggestion_type: str
    context: Dict[str, Any]
    confidence: float
    priority: int = Field(ge=1, le=10)
    created_at: datetime
    used: bool = False

class ChatEscalation(BaseModel):
    """Escalação do chat"""
    escalation_id: str
    session_id: str
    reason: str
    escalation_type: str = Field(pattern="^(human_agent|specialist|supervisor)$")
    priority: str = Field(pattern="^(low|medium|high|urgent)$")
    created_at: datetime
    assigned_to: Optional[str] = None
    resolved: bool = False
    resolution_time: Optional[int] = None

class ChatTraining(BaseModel):
    """Treinamento do chat"""
    training_id: str
    training_type: str
    dataset: List[Dict[str, Any]]
    model_version: str
    training_parameters: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime] = None
    accuracy_score: Optional[float] = None
    status: str = Field(pattern="^(pending|running|completed|failed)$")

class ChatModel(BaseModel):
    """Modelo do chat"""
    model_id: str
    model_name: str
    model_type: str
    version: str
    accuracy: float
    training_data_size: int
    last_trained: datetime
    deployment_status: str
    performance_metrics: Dict[str, float]

class ChatExport(BaseModel):
    """Exportação do chat"""
    export_id: str
    export_type: str  # conversation, analytics, feedback
    session_ids: List[str]
    date_range: Dict[str, datetime]
    format: str = Field(pattern="^(json|csv|pdf|txt)$")
    file_path: str
    created_at: datetime
    expires_at: datetime

class ChatNotification(BaseModel):
    """Notificação do chat"""
    notification_id: str
    notification_type: str
    recipient: str
    subject: str
    message: str
    priority: str = Field(pattern="^(low|medium|high|urgent)$")
    delivery_method: str = Field(pattern="^(email|sms|push|in_app)$")
    sent_at: Optional[datetime] = None
    delivered: bool = False
    read: bool = False

class ChatSecurity(BaseModel):
    """Segurança do chat"""
    session_id: str
    security_level: str = Field(pattern="^(low|medium|high|maximum)$")
    encryption_enabled: bool = True
    data_retention_days: int = 90
    pii_detected: bool = False
    security_alerts: List[str] = []
    compliance_status: str
    last_security_check: datetime

class ChatPerformance(BaseModel):
    """Performance do chat"""
    session_id: str
    response_times: List[float]
    average_response_time: float
    max_response_time: float
    min_response_time: float
    throughput: float  # messages per second
    error_rate: float
    uptime_percentage: float
    measured_at: datetime

class ChatLanguageModel(BaseModel):
    """Modelo de linguagem do chat"""
    model_id: str
    model_name: str
    provider: str
    model_version: str
    supported_languages: List[str]
    max_tokens: int
    temperature: float = Field(ge=0.0, le=2.0)
    top_p: float = Field(ge=0.0, le=1.0)
    frequency_penalty: float = Field(ge=-2.0, le=2.0)
    presence_penalty: float = Field(ge=-2.0, le=2.0)
    cost_per_token: float
    enabled: bool = True

class ChatMemory(BaseModel):
    """Memória do chat"""
    memory_id: str
    session_id: str
    memory_type: str = Field(pattern="^(short_term|long_term|episodic|semantic)$")
    content: Dict[str, Any]
    importance_score: float = Field(ge=0.0, le=1.0)
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    expires_at: Optional[datetime] = None

class ChatEmotion(BaseModel):
    """Emoção detectada no chat"""
    emotion_id: str
    message_id: str
    emotions: Dict[str, float]  # joy, sadness, anger, fear, etc.
    dominant_emotion: str
    confidence: float
    sentiment_polarity: float = Field(ge=-1.0, le=1.0)
    sentiment_subjectivity: float = Field(ge=0.0, le=1.0)
    detected_at: datetime

class ChatRecommendation(BaseModel):
    """Recomendação do chat"""
    recommendation_id: str
    session_id: str
    recommendation_type: str
    title: str
    description: str
    confidence: float
    priority: int = Field(ge=1, le=10)
    context: Dict[str, Any]
    actions: List[Dict[str, Any]]
    generated_at: datetime
    accepted: Optional[bool] = None