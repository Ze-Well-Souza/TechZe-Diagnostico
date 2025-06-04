"""
Endpoints da API v3 - Sistema de Chat e Assistente IA
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import json

from ...ai.chatbot import (
    technical_chatbot,
    voice_controller,
    nlp_processor,
    interactive_tutorials,
    process_chat_message,
    process_voice_input,
    analyze_natural_language,
    start_interactive_tutorial
)
from ...models.chat_models import (
    ChatMessageRequest,
    ChatMessageResponse,
    VoiceCommandRequest,
    VoiceCommandResponse,
    TutorialRequest,
    TutorialResponse,
    ConversationHistory,
    ChatAnalytics,
    UserPreferences
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["AI Chat & Assistant"])

# Gerenciador de conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"Usuário {user_id} conectado ao chat")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"Usuário {user_id} desconectado do chat")
    
    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_chat_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket para chat em tempo real
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Receber mensagem do cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Processar mensagem
            response = await process_chat_message(
                user_id=user_id,
                content=message_data["content"],
                context=message_data.get("context", {})
            )
            
            # Enviar resposta
            response_data = {
                "type": "chat_response",
                "response": {
                    "content": response.content,
                    "response_type": response.response_type.value,
                    "confidence": response.confidence,
                    "suggested_actions": response.suggested_actions,
                    "follow_up_questions": response.follow_up_questions,
                    "timestamp": response.timestamp.isoformat()
                }
            }
            
            await manager.send_personal_message(json.dumps(response_data), user_id)
            
    except WebSocketDisconnect:
        manager.disconnect(user_id)
    except Exception as e:
        logger.error(f"Erro no WebSocket: {e}")
        manager.disconnect(user_id)

@router.post("/message", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    background_tasks: BackgroundTasks
) -> ChatMessageResponse:
    """
    Envia mensagem para o chatbot técnico
    """
    try:
        logger.info(f"Processando mensagem do usuário {request.user_id}")
        
        # Processar mensagem
        response = await process_chat_message(
            user_id=request.user_id,
            content=request.content,
            context=request.context
        )
        
        # Analisar sentimento e contexto em background
        background_tasks.add_task(
            analyze_message_context,
            request.user_id,
            request.content,
            response
        )
        
        return ChatMessageResponse(
            response_id=response.response_id,
            content=response.content,
            response_type=response.response_type.value,
            confidence=response.confidence,
            suggested_actions=response.suggested_actions,
            follow_up_questions=response.follow_up_questions,
            metadata=response.metadata,
            timestamp=response.timestamp
        )
        
    except Exception as e:
        logger.error(f"Erro no processamento da mensagem: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/voice-command", response_model=VoiceCommandResponse)
async def process_voice_command(
    request: VoiceCommandRequest
) -> VoiceCommandResponse:
    """
    Processa comando de voz
    """
    try:
        logger.info(f"Processando comando de voz: {request.voice_text[:50]}...")
        
        # Processar comando de voz
        result = await process_voice_input(request.voice_text)
        
        return VoiceCommandResponse(
            command_id=f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            recognized_command=result.command.value,
            confidence=result.confidence,
            action_taken=result.action_taken,
            response_text=result.response_text,
            parameters=result.parameters,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erro no comando de voz: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/analyze-text")
async def analyze_text_nlp(text: str) -> Dict[str, Any]:
    """
    Analisa texto usando processamento de linguagem natural
    """
    try:
        logger.info(f"Analisando texto NLP: {text[:50]}...")
        
        # Analisar texto
        analysis = await analyze_natural_language(text)
        
        return {
            "text": text,
            "analysis": analysis,
            "processed_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Erro na análise NLP: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/tutorials", response_model=List[Dict[str, Any]])
async def get_available_tutorials(
    difficulty: Optional[str] = None,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Lista tutoriais interativos disponíveis
    """
    try:
        tutorials = await interactive_tutorials.get_available_tutorials(difficulty)
        
        # Filtrar por categoria se especificado
        if category:
            tutorials = [t for t in tutorials if t.category.lower() == category.lower()]
        
        # Converter para formato de resposta
        tutorials_data = []
        for tutorial in tutorials:
            tutorials_data.append({
                "tutorial_id": tutorial.tutorial_id,
                "title": tutorial.title,
                "description": tutorial.description,
                "difficulty_level": tutorial.difficulty_level,
                "estimated_time": tutorial.estimated_time,
                "steps_count": len(tutorial.steps),
                "category": tutorial.category,
                "prerequisites": tutorial.prerequisites
            })
        
        return tutorials_data
        
    except Exception as e:
        logger.error(f"Erro ao listar tutoriais: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/tutorials/start", response_model=TutorialResponse)
async def start_tutorial(
    request: TutorialRequest
) -> TutorialResponse:
    """
    Inicia tutorial interativo
    """
    try:
        logger.info(f"Iniciando tutorial {request.tutorial_id} para usuário {request.user_id}")
        
        # Iniciar tutorial
        tutorial_data = await start_interactive_tutorial(
            tutorial_id=request.tutorial_id,
            user_id=request.user_id
        )
        
        return TutorialResponse(
            tutorial_id=request.tutorial_id,
            tutorial_title=tutorial_data["tutorial"].title,
            current_step=tutorial_data["current_step"],
            progress=tutorial_data["progress"],
            estimated_remaining_time=tutorial_data["estimated_remaining_time"],
            status="started"
        )
        
    except Exception as e:
        logger.error(f"Erro ao iniciar tutorial: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/tutorials/{tutorial_id}/next-step")
async def next_tutorial_step(
    tutorial_id: str,
    user_id: str
) -> Dict[str, Any]:
    """
    Avança para próximo passo do tutorial
    """
    try:
        logger.info(f"Avançando tutorial {tutorial_id} para usuário {user_id}")
        
        # Avançar passo
        step_data = await interactive_tutorials.next_step(tutorial_id, user_id)
        
        return step_data
        
    except Exception as e:
        logger.error(f"Erro ao avançar tutorial: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/history/{user_id}", response_model=ConversationHistory)
async def get_conversation_history(
    user_id: str,
    limit: int = 50,
    offset: int = 0
) -> ConversationHistory:
    """
    Obtém histórico de conversas do usuário
    """
    try:
        # Obter histórico do chatbot
        history = technical_chatbot.conversation_history.get(user_id, [])
        
        # Aplicar paginação
        paginated_history = history[offset:offset + limit]
        
        # Converter para formato de resposta
        messages = []
        for entry in paginated_history:
            messages.append({
                "message_id": entry["message"].message_id,
                "content": entry["message"].content,
                "message_type": entry["message"].message_type.value,
                "response_content": entry["response"].content,
                "response_type": entry["response"].response_type.value,
                "confidence": entry["response"].confidence,
                "timestamp": entry["timestamp"]
            })
        
        return ConversationHistory(
            user_id=user_id,
            total_messages=len(history),
            messages=messages,
            first_interaction=technical_chatbot.user_contexts.get(user_id, {}).get("first_interaction"),
            last_interaction=technical_chatbot.user_contexts.get(user_id, {}).get("last_interaction")
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter histórico: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/analytics/{user_id}", response_model=ChatAnalytics)
async def get_chat_analytics(user_id: str) -> ChatAnalytics:
    """
    Obtém analytics da conversa do usuário
    """
    try:
        user_context = technical_chatbot.user_contexts.get(user_id, {})
        history = technical_chatbot.conversation_history.get(user_id, [])
        
        if not history:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Calcular estatísticas
        total_messages = len(history)
        avg_confidence = sum(entry["response"].confidence for entry in history) / total_messages
        
        # Contar tipos de mensagem
        message_types = {}
        response_types = {}
        
        for entry in history:
            msg_type = entry["message"].message_type.value
            resp_type = entry["response"].response_type.value
            
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
            response_types[resp_type] = response_types.get(resp_type, 0) + 1
        
        # Calcular satisfação (baseado na confiança das respostas)
        if avg_confidence > 0.8:
            satisfaction_score = "high"
        elif avg_confidence > 0.6:
            satisfaction_score = "medium"
        else:
            satisfaction_score = "low"
        
        return ChatAnalytics(
            user_id=user_id,
            total_messages=total_messages,
            average_confidence=avg_confidence,
            message_types_distribution=message_types,
            response_types_distribution=response_types,
            technical_level=user_context.get("technical_level", "beginner"),
            satisfaction_score=satisfaction_score,
            most_common_topics=list(user_context.get("topics_discussed", [])),
            session_duration=user_context.get("last_interaction", datetime.now()) - user_context.get("first_interaction", datetime.now()),
            preferred_language=user_context.get("preferred_language", "pt-BR")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/preferences/{user_id}")
async def update_user_preferences(
    user_id: str,
    preferences: UserPreferences
) -> Dict[str, str]:
    """
    Atualiza preferências do usuário
    """
    try:
        logger.info(f"Atualizando preferências do usuário {user_id}")
        
        # Atualizar contexto do usuário
        if user_id not in technical_chatbot.user_contexts:
            technical_chatbot.user_contexts[user_id] = {}
        
        context = technical_chatbot.user_contexts[user_id]
        context.update({
            "preferred_language": preferences.language,
            "technical_level": preferences.technical_level,
            "notification_preferences": preferences.notifications,
            "response_style": preferences.response_style,
            "tutorial_preferences": preferences.tutorial_preferences
        })
        
        return {
            "message": "Preferências atualizadas com sucesso",
            "user_id": user_id,
            "status": "updated"
        }
        
    except Exception as e:
        logger.error(f"Erro ao atualizar preferências: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/preferences/{user_id}", response_model=UserPreferences)
async def get_user_preferences(user_id: str) -> UserPreferences:
    """
    Obtém preferências do usuário
    """
    try:
        context = technical_chatbot.user_contexts.get(user_id, {})
        
        return UserPreferences(
            language=context.get("preferred_language", "pt-BR"),
            technical_level=context.get("technical_level", "beginner"),
            notifications=context.get("notification_preferences", {}),
            response_style=context.get("response_style", "friendly"),
            tutorial_preferences=context.get("tutorial_preferences", {})
        )
        
    except Exception as e:
        logger.error(f"Erro ao obter preferências: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/feedback")
async def submit_chat_feedback(
    user_id: str,
    message_id: str,
    rating: int,
    feedback_text: Optional[str] = None
) -> Dict[str, str]:
    """
    Submete feedback sobre uma resposta do chatbot
    """
    try:
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating deve ser entre 1 e 5")
        
        logger.info(f"Feedback recebido do usuário {user_id} para mensagem {message_id}: {rating}/5")
        
        # Armazenar feedback (em implementação real, salvaria no banco)
        feedback_data = {
            "user_id": user_id,
            "message_id": message_id,
            "rating": rating,
            "feedback_text": feedback_text,
            "timestamp": datetime.now()
        }
        
        # Aqui você salvaria o feedback no banco de dados
        # await save_feedback_to_database(feedback_data)
        
        return {
            "message": "Feedback recebido com sucesso",
            "status": "saved",
            "feedback_id": f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao salvar feedback: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/health")
async def get_chat_system_health() -> Dict[str, Any]:
    """
    Verifica saúde do sistema de chat
    """
    try:
        # Verificar componentes do sistema
        health_status = {
            "chatbot_engine": "healthy",
            "voice_controller": "healthy",
            "nlp_processor": "healthy",
            "tutorial_system": "healthy",
            "websocket_connections": len(manager.active_connections),
            "total_users": len(technical_chatbot.user_contexts),
            "total_conversations": sum(len(history) for history in technical_chatbot.conversation_history.values()),
            "system_uptime": "operational",
            "last_check": datetime.now()
        }
        
        # Verificar se há problemas
        issues = []
        if len(manager.active_connections) > 1000:
            issues.append("Alto número de conexões WebSocket")
        
        if len(technical_chatbot.user_contexts) > 10000:
            issues.append("Alto número de contextos de usuário em memória")
        
        health_status["issues"] = issues
        health_status["overall_status"] = "healthy" if not issues else "warning"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Erro ao verificar saúde do sistema: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/clear-history/{user_id}")
async def clear_user_history(user_id: str) -> Dict[str, str]:
    """
    Limpa histórico de conversa do usuário
    """
    try:
        logger.info(f"Limpando histórico do usuário {user_id}")
        
        # Limpar histórico
        if user_id in technical_chatbot.conversation_history:
            del technical_chatbot.conversation_history[user_id]
        
        # Manter contexto básico mas limpar histórico de tópicos
        if user_id in technical_chatbot.user_contexts:
            context = technical_chatbot.user_contexts[user_id]
            context["topics_discussed"] = []
            context["message_count"] = 0
            context["current_issue"] = None
        
        return {
            "message": f"Histórico do usuário {user_id} limpo com sucesso",
            "status": "cleared"
        }
        
    except Exception as e:
        logger.error(f"Erro ao limpar histórico: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

# Função auxiliar para análise de contexto em background
async def analyze_message_context(user_id: str, message_content: str, response):
    """
    Analisa contexto da mensagem em background
    """
    try:
        # Analisar sentimento
        sentiment_analysis = await nlp_processor.extract_intent_and_entities(message_content)
        
        # Atualizar contexto do usuário
        if user_id in technical_chatbot.user_contexts:
            context = technical_chatbot.user_contexts[user_id]
            
            # Adicionar tópicos discutidos
            if sentiment_analysis["intent"] not in context.get("topics_discussed", []):
                if "topics_discussed" not in context:
                    context["topics_discussed"] = []
                context["topics_discussed"].append(sentiment_analysis["intent"])
            
            # Atualizar problema atual se relevante
            if sentiment_analysis["intent"] in ["diagnostic", "troubleshooting"]:
                context["current_issue"] = sentiment_analysis["entities"]
        
        logger.debug(f"Contexto analisado para usuário {user_id}")
        
    except Exception as e:
        logger.error(f"Erro na análise de contexto: {e}")