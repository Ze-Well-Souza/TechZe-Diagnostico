"""Endpoints de Chat - API Core

Consolida todas as funcionalidades de chat, assistente virtual e conversação.
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])

# Modelos de dados
class ChatMessage(BaseModel):
    id: Optional[str] = None
    session_id: str
    user_id: str
    message: str
    message_type: str = "user"  # "user", "assistant", "system"
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    id: str
    session_id: str
    message: str
    message_type: str = "assistant"
    timestamp: datetime
    suggestions: Optional[List[str]] = None
    actions: Optional[List[Dict[str, Any]]] = None

class ChatSession(BaseModel):
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    status: str = "active"  # "active", "archived", "deleted"
    message_count: int = 0
    metadata: Optional[Dict[str, Any]] = None

class ChatContext(BaseModel):
    session_id: str
    context_type: str  # "diagnostic", "system", "general"
    context_data: Dict[str, Any]
    expires_at: Optional[datetime] = None

class AssistantCapability(BaseModel):
    name: str
    description: str
    category: str
    enabled: bool = True
    parameters: Optional[Dict[str, Any]] = None

# Gerenciador de conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(json.dumps(message))
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.values():
            await connection.send_text(json.dumps(message))

manager = ConnectionManager()

# Endpoints de Sessões de Chat
@router.post("/sessions")
async def create_chat_session(user_id: str, title: Optional[str] = None):
    """Cria uma nova sessão de chat"""
    try:
        import uuid
        
        session_id = str(uuid.uuid4())
        session = {
            "id": session_id,
            "user_id": user_id,
            "title": title or f"Chat Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "active",
            "message_count": 0,
            "metadata": {}
        }
        
        return {
            "message": "Chat session created successfully",
            "session": session
        }
        
    except Exception as e:
        logger.error(f"Failed to create chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create chat session")

@router.get("/sessions")
async def get_chat_sessions(user_id: str, status: Optional[str] = None, limit: int = 20):
    """Lista sessões de chat do usuário"""
    try:
        # Simular sessões de chat
        sessions = [
            {
                "id": "session_1",
                "user_id": user_id,
                "title": "Diagnóstico do Sistema",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active",
                "message_count": 15,
                "last_message": "Como posso otimizar a performance?"
            },
            {
                "id": "session_2",
                "user_id": user_id,
                "title": "Configuração de Alertas",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "status": "active",
                "message_count": 8,
                "last_message": "Configurar alerta para CPU alta"
            }
        ]
        
        # Filtrar por status se especificado
        if status:
            sessions = [s for s in sessions if s["status"] == status]
        
        return {
            "sessions": sessions[:limit],
            "total_count": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Failed to get chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat sessions")

@router.get("/sessions/{session_id}")
async def get_chat_session(session_id: str):
    """Obtém detalhes de uma sessão específica"""
    try:
        # Simular sessão específica
        session = {
            "id": session_id,
            "user_id": "user_123",
            "title": "Diagnóstico do Sistema",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "active",
            "message_count": 15,
            "metadata": {
                "context_type": "diagnostic",
                "system_info": "Windows 11"
            }
        }
        
        return {"session": session}
        
    except Exception as e:
        logger.error(f"Failed to get chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat session")

@router.put("/sessions/{session_id}")
async def update_chat_session(session_id: str, title: Optional[str] = None, status: Optional[str] = None):
    """Atualiza uma sessão de chat"""
    try:
        updates = {}
        if title:
            updates["title"] = title
        if status:
            updates["status"] = status
        
        updates["updated_at"] = datetime.utcnow().isoformat()
        
        return {
            "message": "Chat session updated successfully",
            "session_id": session_id,
            "updates": updates
        }
        
    except Exception as e:
        logger.error(f"Failed to update chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to update chat session")

@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Remove uma sessão de chat"""
    try:
        return {
            "message": "Chat session deleted successfully",
            "session_id": session_id,
            "deleted_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to delete chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat session")

# Endpoints de Mensagens
@router.post("/sessions/{session_id}/messages")
async def send_message(session_id: str, message: ChatMessage):
    """Envia uma mensagem no chat"""
    try:
        import uuid
        
        # Processar mensagem do usuário
        user_message = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "user_id": message.user_id,
            "message": message.message,
            "message_type": "user",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": message.metadata or {}
        }
        
        # Gerar resposta do assistente
        assistant_response = await _generate_assistant_response(message.message, session_id)
        
        assistant_message = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "message": assistant_response["message"],
            "message_type": "assistant",
            "timestamp": datetime.utcnow().isoformat(),
            "suggestions": assistant_response.get("suggestions", []),
            "actions": assistant_response.get("actions", [])
        }
        
        # Enviar via WebSocket se conectado
        await manager.send_message(session_id, {
            "type": "new_message",
            "message": assistant_message
        })
        
        return {
            "user_message": user_message,
            "assistant_message": assistant_message
        }
        
    except Exception as e:
        logger.error(f"Failed to send message: {e}")
        raise HTTPException(status_code=500, detail="Failed to send message")

@router.get("/sessions/{session_id}/messages")
async def get_chat_messages(session_id: str, limit: int = 50, offset: int = 0):
    """Obtém mensagens de uma sessão de chat"""
    try:
        # Simular mensagens
        messages = [
            {
                "id": "msg_1",
                "session_id": session_id,
                "user_id": "user_123",
                "message": "Olá! Preciso de ajuda com o diagnóstico do sistema.",
                "message_type": "user",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "id": "msg_2",
                "session_id": session_id,
                "message": "Olá! Claro, posso ajudá-lo com o diagnóstico. Que tipo de problema você está enfrentando?",
                "message_type": "assistant",
                "timestamp": datetime.utcnow().isoformat(),
                "suggestions": [
                    "Executar diagnóstico completo",
                    "Verificar performance do sistema",
                    "Analisar logs de erro"
                ]
            },
            {
                "id": "msg_3",
                "session_id": session_id,
                "user_id": "user_123",
                "message": "O sistema está lento e quero verificar a performance.",
                "message_type": "user",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "id": "msg_4",
                "session_id": session_id,
                "message": "Entendi. Vou executar uma análise de performance para você. Isso pode levar alguns minutos.",
                "message_type": "assistant",
                "timestamp": datetime.utcnow().isoformat(),
                "actions": [
                    {
                        "type": "run_diagnostic",
                        "label": "Executar Diagnóstico de Performance",
                        "endpoint": "/api/core/diagnostics/run",
                        "parameters": {"type": "performance"}
                    }
                ]
            }
        ]
        
        # Aplicar paginação
        paginated_messages = messages[offset:offset + limit]
        
        return {
            "messages": paginated_messages,
            "total_count": len(messages),
            "has_more": offset + limit < len(messages)
        }
        
    except Exception as e:
        logger.error(f"Failed to get chat messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat messages")

# WebSocket para Chat em Tempo Real
@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket para chat em tempo real"""
    await manager.connect(websocket, session_id)
    try:
        # Enviar mensagem de boas-vindas
        await manager.send_message(session_id, {
            "type": "connected",
            "message": "Conectado ao chat. Como posso ajudá-lo hoje?",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while True:
            # Receber mensagens do cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Processar mensagem
            if message_data.get("type") == "user_message":
                response = await _generate_assistant_response(
                    message_data.get("message", ""), 
                    session_id
                )
                
                await manager.send_message(session_id, {
                    "type": "assistant_message",
                    "message": response["message"],
                    "suggestions": response.get("suggestions", []),
                    "actions": response.get("actions", []),
                    "timestamp": datetime.utcnow().isoformat()
                })
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        manager.disconnect(session_id)

# Endpoints do Assistente Virtual
@router.get("/assistant/capabilities")
async def get_assistant_capabilities():
    """Obtém capacidades do assistente virtual"""
    try:
        capabilities = [
            {
                "name": "system_diagnostics",
                "description": "Executar diagnósticos completos do sistema",
                "category": "diagnostics",
                "enabled": True,
                "parameters": {
                    "types": ["quick", "standard", "comprehensive"]
                }
            },
            {
                "name": "performance_analysis",
                "description": "Analisar performance e otimização",
                "category": "performance",
                "enabled": True,
                "parameters": {
                    "metrics": ["cpu", "memory", "disk", "network"]
                }
            },
            {
                "name": "alert_management",
                "description": "Gerenciar alertas e notificações",
                "category": "monitoring",
                "enabled": True,
                "parameters": {
                    "actions": ["create", "update", "delete", "resolve"]
                }
            },
            {
                "name": "report_generation",
                "description": "Gerar relatórios personalizados",
                "category": "analytics",
                "enabled": True,
                "parameters": {
                    "formats": ["pdf", "excel", "json"]
                }
            },
            {
                "name": "automation_tasks",
                "description": "Executar tarefas automatizadas",
                "category": "automation",
                "enabled": True,
                "parameters": {
                    "types": ["scheduled", "triggered", "manual"]
                }
            }
        ]
        
        return {
            "capabilities": capabilities,
            "total_count": len(capabilities)
        }
        
    except Exception as e:
        logger.error(f"Failed to get assistant capabilities: {e}")
        raise HTTPException(status_code=500, detail="Failed to get assistant capabilities")

@router.post("/assistant/execute")
async def execute_assistant_action(action: str, parameters: Dict[str, Any]):
    """Executa uma ação do assistente virtual"""
    try:
        # Simular execução de ações
        result = await _execute_assistant_action(action, parameters)
        
        return {
            "action": action,
            "parameters": parameters,
            "result": result,
            "executed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to execute assistant action: {e}")
        raise HTTPException(status_code=500, detail="Failed to execute assistant action")

# Endpoints de Contexto
@router.post("/context")
async def set_chat_context(context: ChatContext):
    """Define contexto para a sessão de chat"""
    try:
        context_data = {
            "session_id": context.session_id,
            "context_type": context.context_type,
            "context_data": context.context_data,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": context.expires_at.isoformat() if context.expires_at else None
        }
        
        return {
            "message": "Chat context set successfully",
            "context": context_data
        }
        
    except Exception as e:
        logger.error(f"Failed to set chat context: {e}")
        raise HTTPException(status_code=500, detail="Failed to set chat context")

@router.get("/context/{session_id}")
async def get_chat_context(session_id: str):
    """Obtém contexto da sessão de chat"""
    try:
        # Simular contexto
        context = {
            "session_id": session_id,
            "context_type": "diagnostic",
            "context_data": {
                "system_type": "Windows 11",
                "last_diagnostic": "2024-01-15T10:30:00Z",
                "performance_issues": ["high_cpu", "memory_leak"]
            },
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": None
        }
        
        return {"context": context}
        
    except Exception as e:
        logger.error(f"Failed to get chat context: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat context")

# Health Check
@router.get("/health")
async def chat_health_check():
    """Health check do sistema de chat"""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "active_connections": len(manager.active_connections),
            "assistant_status": "online",
            "capabilities_count": 5
        }
        
    except Exception as e:
        logger.error(f"Chat health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

# Funções auxiliares
async def _generate_assistant_response(user_message: str, session_id: str) -> Dict[str, Any]:
    """Gera resposta do assistente baseada na mensagem do usuário"""
    try:
        # Análise simples da mensagem para gerar resposta contextual
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["diagnóstico", "diagnostic", "verificar", "check"]):
            return {
                "message": "Vou executar um diagnóstico do sistema para você. Que tipo de diagnóstico você gostaria: rápido, padrão ou completo?",
                "suggestions": [
                    "Diagnóstico rápido",
                    "Diagnóstico padrão",
                    "Diagnóstico completo"
                ],
                "actions": [
                    {
                        "type": "run_diagnostic",
                        "label": "Executar Diagnóstico",
                        "endpoint": "/api/core/diagnostics/run"
                    }
                ]
            }
        
        elif any(word in message_lower for word in ["performance", "lento", "slow", "otimizar"]):
            return {
                "message": "Vou analisar a performance do seu sistema. Posso verificar CPU, memória, disco e rede. O que você gostaria de analisar primeiro?",
                "suggestions": [
                    "Analisar CPU",
                    "Verificar memória",
                    "Análise completa de performance"
                ],
                "actions": [
                    {
                        "type": "performance_analysis",
                        "label": "Análise de Performance",
                        "endpoint": "/api/core/performance/metrics/system"
                    }
                ]
            }
        
        elif any(word in message_lower for word in ["alerta", "alert", "notificação", "notification"]):
            return {
                "message": "Posso ajudá-lo com alertas e notificações. Você gostaria de criar um novo alerta, verificar alertas ativos ou configurar regras?",
                "suggestions": [
                    "Criar novo alerta",
                    "Ver alertas ativos",
                    "Configurar regras"
                ],
                "actions": [
                    {
                        "type": "alert_management",
                        "label": "Gerenciar Alertas",
                        "endpoint": "/api/core/performance/alerts/active"
                    }
                ]
            }
        
        elif any(word in message_lower for word in ["relatório", "report", "análise", "analytics"]):
            return {
                "message": "Posso gerar relatórios personalizados para você. Que tipo de relatório você precisa: diagnóstico, performance, ou análise de tendências?",
                "suggestions": [
                    "Relatório de diagnóstico",
                    "Relatório de performance",
                    "Análise de tendências"
                ],
                "actions": [
                    {
                        "type": "generate_report",
                        "label": "Gerar Relatório",
                        "endpoint": "/api/core/analytics/reports"
                    }
                ]
            }
        
        else:
            return {
                "message": "Entendi. Como assistente de diagnóstico, posso ajudá-lo com análises do sistema, performance, alertas e relatórios. Em que posso ajudá-lo especificamente?",
                "suggestions": [
                    "Executar diagnóstico",
                    "Verificar performance",
                    "Configurar alertas",
                    "Gerar relatório"
                ]
            }
        
    except Exception as e:
        logger.error(f"Failed to generate assistant response: {e}")
        return {
            "message": "Desculpe, ocorreu um erro ao processar sua mensagem. Pode tentar novamente?",
            "suggestions": ["Tentar novamente"]
        }

async def _execute_assistant_action(action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Executa uma ação específica do assistente"""
    try:
        if action == "run_diagnostic":
            return {
                "status": "started",
                "diagnostic_id": "diag_123",
                "estimated_duration": "2-3 minutes",
                "message": "Diagnóstico iniciado com sucesso"
            }
        
        elif action == "performance_analysis":
            return {
                "status": "completed",
                "analysis_id": "perf_456",
                "summary": "Sistema operando normalmente",
                "recommendations": ["Otimizar cache", "Limpar arquivos temporários"]
            }
        
        elif action == "alert_management":
            return {
                "status": "success",
                "alerts_count": 3,
                "active_alerts": 1,
                "message": "Alertas verificados com sucesso"
            }
        
        elif action == "generate_report":
            return {
                "status": "generated",
                "report_id": "report_789",
                "format": parameters.get("format", "pdf"),
                "download_url": "/api/core/analytics/reports/report_789/download"
            }
        
        else:
            return {
                "status": "unknown_action",
                "message": f"Ação '{action}' não reconhecida"
            }
        
    except Exception as e:
        logger.error(f"Failed to execute assistant action {action}: {e}")
        return {
            "status": "error",
            "message": f"Erro ao executar ação: {str(e)}"
        }

@router.get("/info")
async def chat_info():
    """
    Informações do domínio chat
    """
    return {
        "domain": "chat",
        "name": "Chat Domain",
        "version": "1.0.0", 
        "description": "Chat e comunicação em tempo real",
        "features": ['Real-time Chat', 'WebSocket Support', 'Message History'],
        "status": "active"
    }

@router.get("/health")
async def chat_health_check():
    """
    Health check do domínio chat
    """
    return {
        "status": "healthy",
        "domain": "chat",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

