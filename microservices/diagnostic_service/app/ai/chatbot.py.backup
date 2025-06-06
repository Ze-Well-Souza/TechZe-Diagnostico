"""
Sistema de Chatbot Técnico e Interface Conversacional
Implementa assistente IA, controle por voz e processamento de linguagem natural
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Tipos de mensagem do chatbot"""
    QUESTION = "question"
    COMMAND = "command"
    HELP_REQUEST = "help_request"
    DIAGNOSTIC_REQUEST = "diagnostic_request"
    TROUBLESHOOTING = "troubleshooting"
    GENERAL_CHAT = "general_chat"

class ResponseType(Enum):
    """Tipos de resposta do chatbot"""
    ANSWER = "answer"
    ACTION_CONFIRMATION = "action_confirmation"
    TUTORIAL_STEP = "tutorial_step"
    DIAGNOSTIC_RESULT = "diagnostic_result"
    ERROR_MESSAGE = "error_message"
    CLARIFICATION_REQUEST = "clarification_request"

class VoiceCommand(Enum):
    """Comandos de voz disponíveis"""
    START_DIAGNOSTIC = "iniciar diagnóstico"
    SHOW_STATUS = "mostrar status"
    OPTIMIZE_SYSTEM = "otimizar sistema"
    HELP = "ajuda"
    STOP = "parar"
    REPEAT = "repetir"

@dataclass
class ChatMessage:
    """Mensagem do chat"""
    message_id: str
    user_id: str
    content: str
    message_type: MessageType
    timestamp: datetime
    context: Dict[str, Any]
    language: str = "pt-BR"

@dataclass
class ChatResponse:
    """Resposta do chatbot"""
    response_id: str
    content: str
    response_type: ResponseType
    confidence: float
    suggested_actions: List[str]
    follow_up_questions: List[str]
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class Tutorial:
    """Tutorial interativo"""
    tutorial_id: str
    title: str
    description: str
    difficulty_level: str
    estimated_time: int
    steps: List[Dict[str, Any]]
    prerequisites: List[str]
    category: str

@dataclass
class VoiceCommandResult:
    """Resultado de comando de voz"""
    command: VoiceCommand
    confidence: float
    parameters: Dict[str, Any]
    action_taken: bool
    response_text: str

class TechnicalChatbot:
    """Chatbot técnico especializado em diagnósticos"""
    
    def __init__(self):
        self.conversation_history = {}
        self.user_contexts = {}
        self.knowledge_base = self._load_knowledge_base()
        self.response_templates = self._load_response_templates()
        self.diagnostic_patterns = self._load_diagnostic_patterns()
        
    async def process_message(self, message: ChatMessage) -> ChatResponse:
        """Processa mensagem do usuário e gera resposta"""
        try:
            # Atualizar contexto do usuário
            self._update_user_context(message)
            
            # Classificar tipo de mensagem
            message_type = self._classify_message(message.content)
            message.message_type = message_type
            
            # Gerar resposta baseada no tipo
            if message_type == MessageType.DIAGNOSTIC_REQUEST:
                response = await self._handle_diagnostic_request(message)
            elif message_type == MessageType.TROUBLESHOOTING:
                response = await self._handle_troubleshooting(message)
            elif message_type == MessageType.HELP_REQUEST:
                response = await self._handle_help_request(message)
            elif message_type == MessageType.COMMAND:
                response = await self._handle_command(message)
            else:
                response = await self._handle_general_chat(message)
            
            # Armazenar no histórico
            self._store_conversation(message, response)
            
            logger.info(f"Resposta gerada para usuário {message.user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro no processamento da mensagem: {e}")
            return self._create_error_response(str(e))
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Carrega base de conhecimento técnico"""
        return {
            "hardware_issues": {
                "cpu_overheating": {
                    "symptoms": ["alta temperatura", "lentidão", "travamentos"],
                    "solutions": ["verificar ventilação", "limpar cooler", "trocar pasta térmica"],
                    "urgency": "alta"
                },
                "memory_problems": {
                    "symptoms": ["erro de memória", "tela azul", "travamentos aleatórios"],
                    "solutions": ["testar memória", "verificar slots", "substituir módulos"],
                    "urgency": "média"
                },
                "disk_failure": {
                    "symptoms": ["ruídos estranhos", "lentidão", "erros de leitura"],
                    "solutions": ["backup imediato", "verificar saúde do disco", "substituir HD"],
                    "urgency": "crítica"
                }
            },
            "software_issues": {
                "slow_performance": {
                    "symptoms": ["sistema lento", "demora para abrir programas"],
                    "solutions": ["limpeza de disco", "desfragmentação", "otimização"],
                    "urgency": "baixa"
                },
                "virus_malware": {
                    "symptoms": ["comportamento estranho", "pop-ups", "lentidão"],
                    "solutions": ["scan antivírus", "modo seguro", "limpeza profunda"],
                    "urgency": "alta"
                }
            },
            "network_issues": {
                "connection_problems": {
                    "symptoms": ["sem internet", "conexão instável", "lentidão"],
                    "solutions": ["reiniciar modem", "verificar cabos", "atualizar drivers"],
                    "urgency": "média"
                }
            }
        }
    
    def _load_response_templates(self) -> Dict[str, str]:
        """Carrega templates de resposta"""
        return {
            "greeting": "Olá! Sou o assistente técnico do TechZe. Como posso ajudá-lo hoje?",
            "diagnostic_start": "Vou iniciar um diagnóstico do seu sistema. Isso pode levar alguns minutos...",
            "help_offer": "Posso ajudá-lo com diagnósticos, troubleshooting e otimização do sistema. O que você gostaria de fazer?",
            "clarification": "Poderia fornecer mais detalhes sobre o problema que está enfrentando?",
            "solution_found": "Encontrei uma possível solução para seu problema:",
            "no_solution": "Não consegui encontrar uma solução específica, mas posso sugerir algumas verificações gerais.",
            "action_confirmation": "Gostaria que eu execute esta ação automaticamente?",
            "tutorial_offer": "Posso criar um tutorial passo-a-passo para resolver este problema. Interessado?"
        }
    
    def _load_diagnostic_patterns(self) -> Dict[str, List[str]]:
        """Carrega padrões para identificar problemas"""
        return {
            "performance": [
                r"lento|lentidão|devagar|demorado",
                r"travando|trava|freeze|congelando",
                r"performance|desempenho|velocidade"
            ],
            "hardware": [
                r"temperatura|quente|superaquecimento",
                r"ruído|barulho|ventilador",
                r"memória|ram|disco|hd|ssd"
            ],
            "network": [
                r"internet|rede|conexão|wifi",
                r"lento para navegar|páginas não carregam",
                r"desconectando|instável"
            ],
            "software": [
                r"programa|aplicativo|software",
                r"erro|falha|crash|fechando",
                r"vírus|malware|antivírus"
            ]
        }
    
    def _update_user_context(self, message: ChatMessage):
        """Atualiza contexto do usuário"""
        user_id = message.user_id
        
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {
                'first_interaction': datetime.now(),
                'message_count': 0,
                'topics_discussed': [],
                'current_issue': None,
                'preferred_language': message.language,
                'technical_level': 'beginner'  # Será inferido
            }
        
        context = self.user_contexts[user_id]
        context['message_count'] += 1
        context['last_interaction'] = datetime.now()
        
        # Inferir nível técnico baseado no vocabulário
        technical_terms = ['driver', 'registry', 'bios', 'kernel', 'api', 'tcp', 'dns']
        if any(term in message.content.lower() for term in technical_terms):
            context['technical_level'] = 'advanced'
        elif context['message_count'] > 5:
            context['technical_level'] = 'intermediate'
    
    def _classify_message(self, content: str) -> MessageType:
        """Classifica o tipo de mensagem"""
        content_lower = content.lower()
        
        # Padrões para classificação
        diagnostic_patterns = [
            r"diagnóstico|diagnosticar|verificar|analisar",
            r"problema|erro|falha|não funciona",
            r"o que está errado|qual o problema"
        ]
        
        help_patterns = [
            r"ajuda|help|socorro|não sei",
            r"como fazer|como resolver|tutorial",
            r"preciso de ajuda"
        ]
        
        command_patterns = [
            r"execute|executar|fazer|iniciar",
            r"otimizar|limpar|corrigir|consertar",
            r"reiniciar|parar|cancelar"
        ]
        
        troubleshooting_patterns = [
            r"meu computador|minha máquina|sistema",
            r"está lento|não liga|travando|congelando",
            r"internet não funciona|sem conexão"
        ]
        
        # Verificar padrões
        if any(re.search(pattern, content_lower) for pattern in diagnostic_patterns):
            return MessageType.DIAGNOSTIC_REQUEST
        elif any(re.search(pattern, content_lower) for pattern in help_patterns):
            return MessageType.HELP_REQUEST
        elif any(re.search(pattern, content_lower) for pattern in command_patterns):
            return MessageType.COMMAND
        elif any(re.search(pattern, content_lower) for pattern in troubleshooting_patterns):
            return MessageType.TROUBLESHOOTING
        else:
            return MessageType.GENERAL_CHAT
    
    async def _handle_diagnostic_request(self, message: ChatMessage) -> ChatResponse:
        """Trata solicitações de diagnóstico"""
        response_content = self.response_templates["diagnostic_start"]
        
        # Simular diagnóstico
        diagnostic_results = {
            "cpu_usage": 75,
            "memory_usage": 68,
            "disk_health": 92,
            "network_status": "ok",
            "issues_found": ["Alto uso de CPU", "Fragmentação de disco"]
        }
        
        response_content += f"\n\nResultados do diagnóstico:\n"
        response_content += f"• CPU: {diagnostic_results['cpu_usage']}% de uso\n"
        response_content += f"• Memória: {diagnostic_results['memory_usage']}% de uso\n"
        response_content += f"• Saúde do disco: {diagnostic_results['disk_health']}%\n"
        
        if diagnostic_results['issues_found']:
            response_content += f"\nProblemas encontrados:\n"
            for issue in diagnostic_results['issues_found']:
                response_content += f"• {issue}\n"
        
        suggested_actions = [
            "Otimizar sistema automaticamente",
            "Ver tutorial de otimização manual",
            "Agendar manutenção preventiva"
        ]
        
        follow_up_questions = [
            "Gostaria que eu otimize o sistema automaticamente?",
            "Quer ver um tutorial detalhado de como resolver estes problemas?",
            "Precisa de mais informações sobre algum problema específico?"
        ]
        
        return ChatResponse(
            response_id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=response_content,
            response_type=ResponseType.DIAGNOSTIC_RESULT,
            confidence=0.9,
            suggested_actions=suggested_actions,
            follow_up_questions=follow_up_questions,
            timestamp=datetime.now(),
            metadata={"diagnostic_results": diagnostic_results}
        )
    
    async def _handle_troubleshooting(self, message: ChatMessage) -> ChatResponse:
        """Trata solicitações de troubleshooting"""
        content = message.content.lower()
        
        # Identificar categoria do problema
        problem_category = None
        for category, patterns in self.diagnostic_patterns.items():
            if any(re.search(pattern, content) for pattern in patterns):
                problem_category = category
                break
        
        if problem_category and problem_category in self.knowledge_base:
            # Encontrar problema específico
            category_issues = self.knowledge_base[problem_category]
            
            for issue_name, issue_data in category_issues.items():
                symptoms = issue_data["symptoms"]
                if any(symptom in content for symptom in symptoms):
                    solutions = issue_data["solutions"]
                    urgency = issue_data["urgency"]
                    
                    response_content = f"Identifiquei que você pode estar enfrentando: **{issue_name.replace('_', ' ').title()}**\n\n"
                    response_content += f"Urgência: {urgency.upper()}\n\n"
                    response_content += "Soluções recomendadas:\n"
                    
                    for i, solution in enumerate(solutions, 1):
                        response_content += f"{i}. {solution}\n"
                    
                    suggested_actions = [
                        "Executar correção automática",
                        "Ver tutorial detalhado",
                        "Agendar suporte técnico"
                    ]
                    
                    return ChatResponse(
                        response_id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        content=response_content,
                        response_type=ResponseType.ANSWER,
                        confidence=0.8,
                        suggested_actions=suggested_actions,
                        follow_up_questions=["Gostaria que eu execute alguma dessas soluções?"],
                        timestamp=datetime.now(),
                        metadata={"problem_category": problem_category, "issue": issue_name}
                    )
        
        # Resposta genérica se não encontrou problema específico
        response_content = self.response_templates["clarification"]
        response_content += "\n\nPara ajudá-lo melhor, poderia me contar:\n"
        response_content += "• Quando o problema começou?\n"
        response_content += "• O que você estava fazendo quando aconteceu?\n"
        response_content += "• Há alguma mensagem de erro específica?\n"
        
        return ChatResponse(
            response_id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=response_content,
            response_type=ResponseType.CLARIFICATION_REQUEST,
            confidence=0.6,
            suggested_actions=["Executar diagnóstico completo"],
            follow_up_questions=["Gostaria que eu execute um diagnóstico completo?"],
            timestamp=datetime.now(),
            metadata={}
        )
    
    async def _handle_help_request(self, message: ChatMessage) -> ChatResponse:
        """Trata solicitações de ajuda"""
        user_context = self.user_contexts.get(message.user_id, {})
        technical_level = user_context.get('technical_level', 'beginner')
        
        if technical_level == 'beginner':
            response_content = "Vou ajudá-lo de forma simples e clara!\n\n"
            response_content += "Posso ajudar com:\n"
            response_content += "• **Diagnóstico automático** - Verifico seu sistema e encontro problemas\n"
            response_content += "• **Tutoriais passo-a-passo** - Ensino como resolver problemas\n"
            response_content += "• **Otimização automática** - Melhoro a performance do seu computador\n"
            response_content += "• **Suporte em tempo real** - Respondo suas dúvidas técnicas\n"
        else:
            response_content = "Como técnico experiente, posso oferecer:\n\n"
            response_content += "• **Análise avançada de sistema** - Métricas detalhadas e logs\n"
            response_content += "• **Automação de correções** - Scripts e workflows personalizados\n"
            response_content += "• **Monitoramento preditivo** - Alertas antes dos problemas acontecerem\n"
            response_content += "• **Integração com ferramentas** - APIs e integrações avançadas\n"
        
        suggested_actions = [
            "Iniciar diagnóstico do sistema",
            "Ver tutoriais disponíveis",
            "Configurar monitoramento automático",
            "Acessar documentação técnica"
        ]
        
        return ChatResponse(
            response_id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=response_content,
            response_type=ResponseType.ANSWER,
            confidence=0.95,
            suggested_actions=suggested_actions,
            follow_up_questions=["O que gostaria de fazer primeiro?"],
            timestamp=datetime.now(),
            metadata={"help_type": "general", "user_level": technical_level}
        )
    
    async def _handle_command(self, message: ChatMessage) -> ChatResponse:
        """Trata comandos do usuário"""
        content = message.content.lower()
        
        if "otimizar" in content or "otimização" in content:
            response_content = "Iniciando otimização automática do sistema...\n\n"
            response_content += "Ações que serão executadas:\n"
            response_content += "• Limpeza de arquivos temporários\n"
            response_content += "• Otimização de memória\n"
            response_content += "• Desfragmentação de disco\n"
            response_content += "• Atualização de drivers\n\n"
            response_content += "Tempo estimado: 5-10 minutos"
            
            return ChatResponse(
                response_id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content=response_content,
                response_type=ResponseType.ACTION_CONFIRMATION,
                confidence=0.9,
                suggested_actions=["Confirmar otimização", "Cancelar", "Ver detalhes"],
                follow_up_questions=["Posso prosseguir com a otimização?"],
                timestamp=datetime.now(),
                metadata={"command": "optimize", "estimated_time": 600}
            )
        
        elif "diagnóstico" in content or "verificar" in content:
            return await self._handle_diagnostic_request(message)
        
        else:
            response_content = "Comando não reconhecido. Comandos disponíveis:\n\n"
            response_content += "• **otimizar sistema** - Melhora performance\n"
            response_content += "• **executar diagnóstico** - Verifica problemas\n"
            response_content += "• **limpar disco** - Remove arquivos desnecessários\n"
            response_content += "• **verificar atualizações** - Busca updates\n"
            
            return ChatResponse(
                response_id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content=response_content,
                response_type=ResponseType.ANSWER,
                confidence=0.7,
                suggested_actions=["Ver todos os comandos", "Executar diagnóstico"],
                follow_up_questions=["Qual comando gostaria de executar?"],
                timestamp=datetime.now(),
                metadata={"command": "unknown"}
            )
    
    async def _handle_general_chat(self, message: ChatMessage) -> ChatResponse:
        """Trata conversas gerais"""
        content = message.content.lower()
        
        # Saudações
        if any(greeting in content for greeting in ["oi", "olá", "hello", "bom dia", "boa tarde", "boa noite"]):
            response_content = self.response_templates["greeting"]
            response_content += "\n\n" + self.response_templates["help_offer"]
        
        # Agradecimentos
        elif any(thanks in content for thanks in ["obrigado", "obrigada", "valeu", "thanks"]):
            response_content = "Fico feliz em ajudar! 😊\n\n"
            response_content += "Se precisar de mais alguma coisa, estarei aqui. "
            response_content += "Posso continuar monitorando seu sistema ou ajudar com outros problemas."
        
        # Despedidas
        elif any(bye in content for bye in ["tchau", "até logo", "bye", "adeus"]):
            response_content = "Até logo! Foi um prazer ajudá-lo. 👋\n\n"
            response_content += "Lembre-se: estou sempre disponível para diagnósticos e suporte técnico. "
            response_content += "Tenha um ótimo dia!"
        
        else:
            response_content = "Entendo que você quer conversar, mas sou especializado em suporte técnico! 🤖\n\n"
            response_content += "Posso ajudá-lo com:\n"
            response_content += "• Problemas de computador\n"
            response_content += "• Otimização de sistema\n"
            response_content += "• Diagnósticos técnicos\n"
            response_content += "• Tutoriais e dicas\n\n"
            response_content += "Sobre o que gostaria de conversar?"
        
        return ChatResponse(
            response_id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=response_content,
            response_type=ResponseType.ANSWER,
            confidence=0.8,
            suggested_actions=["Executar diagnóstico", "Ver tutoriais", "Otimizar sistema"],
            follow_up_questions=["Como posso ajudá-lo tecnicamente hoje?"],
            timestamp=datetime.now(),
            metadata={"chat_type": "general"}
        )
    
    def _create_error_response(self, error_message: str) -> ChatResponse:
        """Cria resposta de erro"""
        return ChatResponse(
            response_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=f"Desculpe, ocorreu um erro: {error_message}\n\nPor favor, tente novamente ou reformule sua pergunta.",
            response_type=ResponseType.ERROR_MESSAGE,
            confidence=0.0,
            suggested_actions=["Tentar novamente", "Falar com suporte humano"],
            follow_up_questions=["Posso ajudá-lo de outra forma?"],
            timestamp=datetime.now(),
            metadata={"error": error_message}
        )
    
    def _store_conversation(self, message: ChatMessage, response: ChatResponse):
        """Armazena conversa no histórico"""
        user_id = message.user_id
        
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'message': message,
            'response': response,
            'timestamp': datetime.now()
        })
        
        # Manter apenas últimas 50 mensagens por usuário
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]

class VoiceController:
    """Controlador de comandos por voz"""
    
    def __init__(self):
        self.voice_commands = self._load_voice_commands()
        self.command_history = []
        
    def _load_voice_commands(self) -> Dict[str, VoiceCommand]:
        """Carrega comandos de voz disponíveis"""
        return {
            "iniciar diagnóstico": VoiceCommand.START_DIAGNOSTIC,
            "começar diagnóstico": VoiceCommand.START_DIAGNOSTIC,
            "verificar sistema": VoiceCommand.START_DIAGNOSTIC,
            "mostrar status": VoiceCommand.SHOW_STATUS,
            "ver status": VoiceCommand.SHOW_STATUS,
            "status do sistema": VoiceCommand.SHOW_STATUS,
            "otimizar sistema": VoiceCommand.OPTIMIZE_SYSTEM,
            "melhorar performance": VoiceCommand.OPTIMIZE_SYSTEM,
            "acelerar computador": VoiceCommand.OPTIMIZE_SYSTEM,
            "ajuda": VoiceCommand.HELP,
            "socorro": VoiceCommand.HELP,
            "help": VoiceCommand.HELP,
            "parar": VoiceCommand.STOP,
            "cancelar": VoiceCommand.STOP,
            "pare": VoiceCommand.STOP,
            "repetir": VoiceCommand.REPEAT,
            "repita": VoiceCommand.REPEAT,
            "de novo": VoiceCommand.REPEAT
        }
    
    async def process_voice_command(self, voice_text: str) -> VoiceCommandResult:
        """Processa comando de voz"""
        try:
            voice_text_clean = voice_text.lower().strip()
            
            # Encontrar comando mais próximo
            best_match = None
            best_confidence = 0.0
            
            for command_text, command_enum in self.voice_commands.items():
                # Verificação exata
                if command_text == voice_text_clean:
                    best_match = command_enum
                    best_confidence = 1.0
                    break
                
                # Verificação parcial
                elif command_text in voice_text_clean or voice_text_clean in command_text:
                    confidence = len(command_text) / max(len(voice_text_clean), len(command_text))
                    if confidence > best_confidence:
                        best_match = command_enum
                        best_confidence = confidence
            
            if best_match and best_confidence > 0.6:
                # Executar comando
                result = await self._execute_voice_command(best_match, voice_text_clean)
                result.confidence = best_confidence
                
                # Armazenar no histórico
                self.command_history.append({
                    'command': best_match,
                    'original_text': voice_text,
                    'confidence': best_confidence,
                    'timestamp': datetime.now(),
                    'success': result.action_taken
                })
                
                return result
            else:
                return VoiceCommandResult(
                    command=VoiceCommand.HELP,
                    confidence=0.0,
                    parameters={},
                    action_taken=False,
                    response_text="Comando não reconhecido. Diga 'ajuda' para ver comandos disponíveis."
                )
                
        except Exception as e:
            logger.error(f"Erro no processamento de voz: {e}")
            return VoiceCommandResult(
                command=VoiceCommand.HELP,
                confidence=0.0,
                parameters={},
                action_taken=False,
                response_text=f"Erro no processamento: {str(e)}"
            )
    
    async def _execute_voice_command(self, command: VoiceCommand, original_text: str) -> VoiceCommandResult:
        """Executa comando de voz"""
        if command == VoiceCommand.START_DIAGNOSTIC:
            return VoiceCommandResult(
                command=command,
                confidence=0.0,  # Será definido depois
                parameters={"diagnostic_type": "full"},
                action_taken=True,
                response_text="Iniciando diagnóstico completo do sistema. Aguarde alguns minutos..."
            )
        
        elif command == VoiceCommand.SHOW_STATUS:
            return VoiceCommandResult(
                command=command,
                confidence=0.0,
                parameters={},
                action_taken=True,
                response_text="Sistema funcionando normalmente. CPU: 45%, Memória: 62%, Disco: 78% livre."
            )
        
        elif command == VoiceCommand.OPTIMIZE_SYSTEM:
            return VoiceCommandResult(
                command=command,
                confidence=0.0,
                parameters={"optimization_level": "standard"},
                action_taken=True,
                response_text="Iniciando otimização automática. Isso pode levar alguns minutos..."
            )
        
        elif command == VoiceCommand.HELP:
            help_text = "Comandos disponíveis:\n"
            help_text += "• 'Iniciar diagnóstico' - Verifica o sistema\n"
            help_text += "• 'Mostrar status' - Exibe status atual\n"
            help_text += "• 'Otimizar sistema' - Melhora performance\n"
            help_text += "• 'Parar' - Cancela operação atual\n"
            help_text += "• 'Repetir' - Repete último comando"
            
            return VoiceCommandResult(
                command=command,
                confidence=0.0,
                parameters={},
                action_taken=True,
                response_text=help_text
            )
        
        elif command == VoiceCommand.STOP:
            return VoiceCommandResult(
                command=command,
                confidence=0.0,
                parameters={},
                action_taken=True,
                response_text="Operação cancelada."
            )
        
        elif command == VoiceCommand.REPEAT:
            if self.command_history:
                last_command = self.command_history[-1]['command']
                return await self._execute_voice_command(last_command, original_text)
            else:
                return VoiceCommandResult(
                    command=command,
                    confidence=0.0,
                    parameters={},
                    action_taken=False,
                    response_text="Nenhum comando anterior para repetir."
                )
        
        else:
            return VoiceCommandResult(
                command=command,
                confidence=0.0,
                parameters={},
                action_taken=False,
                response_text="Comando não implementado."
            )

class NLPProcessor:
    """Processador de linguagem natural"""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.entity_patterns = self._load_entity_patterns()
        
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Carrega padrões de intenção"""
        return {
            "diagnostic_intent": [
                r"verificar|checar|analisar|diagnosticar",
                r"problema|erro|falha|defeito",
                r"o que está errado|qual o problema"
            ],
            "optimization_intent": [
                r"otimizar|melhorar|acelerar|limpar",
                r"performance|desempenho|velocidade",
                r"mais rápido|menos lento"
            ],
            "help_intent": [
                r"ajuda|help|socorro|não sei",
                r"como fazer|como resolver",
                r"ensinar|tutorial|explicar"
            ],
            "status_intent": [
                r"status|estado|situação|como está",
                r"funcionando|rodando|operando",
                r"saúde|condição"
            ]
        }
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Carrega padrões de entidades"""
        return {
            "hardware_components": [
                r"cpu|processador|processor",
                r"memória|ram|memory",
                r"disco|hd|ssd|storage",
                r"placa de vídeo|gpu|graphics",
                r"fonte|power supply|psu"
            ],
            "software_components": [
                r"sistema operacional|windows|linux|macos",
                r"driver|drivers|device driver",
                r"programa|aplicativo|software|app",
                r"antivírus|firewall|security"
            ],
            "problem_types": [
                r"lento|lentidão|slow|devagar",
                r"travando|freeze|congelando|hanging",
                r"erro|error|falha|failure",
                r"ruído|barulho|noise|sound"
            ]
        }
    
    async def extract_intent_and_entities(self, text: str) -> Dict[str, Any]:
        """Extrai intenção e entidades do texto"""
        try:
            text_lower = text.lower()
            
            # Extrair intenção
            intent = self._extract_intent(text_lower)
            
            # Extrair entidades
            entities = self._extract_entities(text_lower)
            
            # Extrair contexto adicional
            context = self._extract_context(text_lower)
            
            return {
                "intent": intent,
                "entities": entities,
                "context": context,
                "confidence": self._calculate_nlp_confidence(intent, entities),
                "original_text": text
            }
            
        except Exception as e:
            logger.error(f"Erro na extração NLP: {e}")
            return {
                "intent": "unknown",
                "entities": {},
                "context": {},
                "confidence": 0.0,
                "original_text": text
            }
    
    def _extract_intent(self, text: str) -> str:
        """Extrai intenção principal do texto"""
        for intent, patterns in self.intent_patterns.items():
            if any(re.search(pattern, text) for pattern in patterns):
                return intent.replace("_intent", "")
        
        return "unknown"
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrai entidades do texto"""
        entities = {}
        
        for entity_type, patterns in self.entity_patterns.items():
            found_entities = []
            for pattern in patterns:
                matches = re.findall(pattern, text)
                found_entities.extend(matches)
            
            if found_entities:
                entities[entity_type] = list(set(found_entities))  # Remove duplicatas
        
        return entities
    
    def _extract_context(self, text: str) -> Dict[str, Any]:
        """Extrai contexto adicional"""
        context = {}
        
        # Urgência
        if any(word in text for word in ["urgente", "crítico", "emergência", "agora"]):
            context["urgency"] = "high"
        elif any(word in text for word in ["quando possível", "não urgente", "depois"]):
            context["urgency"] = "low"
        else:
            context["urgency"] = "medium"
        
        # Frequência do problema
        if any(word in text for word in ["sempre", "toda vez", "constantemente"]):
            context["frequency"] = "always"
        elif any(word in text for word in ["às vezes", "ocasionalmente", "raramente"]):
            context["frequency"] = "sometimes"
        else:
            context["frequency"] = "unknown"
        
        # Duração
        time_patterns = [
            (r"(\d+)\s*minutos?", "minutes"),
            (r"(\d+)\s*horas?", "hours"),
            (r"(\d+)\s*dias?", "days"),
            (r"(\d+)\s*semanas?", "weeks")
        ]
        
        for pattern, unit in time_patterns:
            match = re.search(pattern, text)
            if match:
                context["duration"] = {
                    "value": int(match.group(1)),
                    "unit": unit
                }
                break
        
        return context
    
    def _calculate_nlp_confidence(self, intent: str, entities: Dict[str, List[str]]) -> float:
        """Calcula confiança da análise NLP"""
        confidence = 0.5  # Base
        
        # Intenção identificada
        if intent != "unknown":
            confidence += 0.3
        
        # Entidades encontradas
        entity_count = sum(len(entity_list) for entity_list in entities.values())
        confidence += min(entity_count * 0.1, 0.2)
        
        return min(confidence, 1.0)

class InteractiveTutorials:
    """Sistema de tutoriais interativos"""
    
    def __init__(self):
        self.tutorials = self._load_tutorials()
        self.user_progress = {}
        
    def _load_tutorials(self) -> Dict[str, Tutorial]:
        """Carrega tutoriais disponíveis"""
        tutorials = {}
        
        # Tutorial de otimização básica
        tutorials["basic_optimization"] = Tutorial(
            tutorial_id="basic_optimization",
            title="Otimização Básica do Sistema",
            description="Aprenda a otimizar seu computador em passos simples",
            difficulty_level="Iniciante",
            estimated_time=15,
            steps=[
                {
                    "step_number": 1,
                    "title": "Limpeza de Arquivos Temporários",
                    "description": "Vamos limpar arquivos que não são mais necessários",
                    "instructions": [
                        "Pressione Windows + R",
                        "Digite '%temp%' e pressione Enter",
                        "Selecione todos os arquivos (Ctrl + A)",
                        "Delete os arquivos selecionados"
                    ],
                    "expected_result": "Espaço em disco liberado",
                    "troubleshooting": "Se alguns arquivos não puderem ser deletados, pule-os"
                },
                {
                    "step_number": 2,
                    "title": "Limpeza de Disco",
                    "description": "Use a ferramenta nativa do Windows",
                    "instructions": [
                        "Abra 'Este Computador'",
                        "Clique com botão direito no disco C:",
                        "Selecione 'Propriedades'",
                        "Clique em 'Limpeza de Disco'",
                        "Marque todas as opções e clique 'OK'"
                    ],
                    "expected_result": "Mais espaço liberado",
                    "troubleshooting": "O processo pode demorar alguns minutos"
                }
            ],
            prerequisites=[],
            category="Manutenção"
        )
        
        # Tutorial de diagnóstico de hardware
        tutorials["hardware_diagnostic"] = Tutorial(
            tutorial_id="hardware_diagnostic",
            title="Diagnóstico de Hardware",
            description="Como verificar a saúde dos componentes do seu PC",
            difficulty_level="Intermediário",
            estimated_time=30,
            steps=[
                {
                    "step_number": 1,
                    "title": "Verificação de Temperatura",
                    "description": "Monitore as temperaturas dos componentes",
                    "instructions": [
                        "Baixe o HWiNFO64 ou similar",
                        "Execute o programa",
                        "Observe as temperaturas de CPU e GPU",
                        "Verifique se estão abaixo de 80°C"
                    ],
                    "expected_result": "Temperaturas normais identificadas",
                    "troubleshooting": "Se temperaturas altas, verifique ventilação"
                }
            ],
            prerequisites=["Conhecimento básico de hardware"],
            category="Diagnóstico"
        )
        
        return tutorials
    
    async def start_tutorial(self, tutorial_id: str, user_id: str) -> Dict[str, Any]:
        """Inicia um tutorial para o usuário"""
        try:
            if tutorial_id not in self.tutorials:
                raise Exception(f"Tutorial {tutorial_id} não encontrado")
            
            tutorial = self.tutorials[tutorial_id]
            
            # Inicializar progresso do usuário
            if user_id not in self.user_progress:
                self.user_progress[user_id] = {}
            
            self.user_progress[user_id][tutorial_id] = {
                "current_step": 0,
                "started_at": datetime.now(),
                "completed_steps": [],
                "status": "in_progress"
            }
            
            # Retornar primeiro passo
            first_step = tutorial.steps[0]
            
            return {
                "tutorial": tutorial,
                "current_step": first_step,
                "progress": {
                    "step": 1,
                    "total_steps": len(tutorial.steps),
                    "percentage": 0
                },
                "estimated_remaining_time": tutorial.estimated_time
            }
            
        except Exception as e:
            logger.error(f"Erro ao iniciar tutorial: {e}")
            raise
    
    async def next_step(self, tutorial_id: str, user_id: str) -> Dict[str, Any]:
        """Avança para o próximo passo do tutorial"""
        try:
            if user_id not in self.user_progress or tutorial_id not in self.user_progress[user_id]:
                raise Exception("Tutorial não iniciado")
            
            tutorial = self.tutorials[tutorial_id]
            progress = self.user_progress[user_id][tutorial_id]
            
            # Marcar passo atual como completo
            current_step_index = progress["current_step"]
            if current_step_index not in progress["completed_steps"]:
                progress["completed_steps"].append(current_step_index)
            
            # Avançar para próximo passo
            next_step_index = current_step_index + 1
            
            if next_step_index >= len(tutorial.steps):
                # Tutorial completo
                progress["status"] = "completed"
                progress["completed_at"] = datetime.now()
                
                return {
                    "tutorial_completed": True,
                    "completion_time": progress["completed_at"] - progress["started_at"],
                    "message": f"Parabéns! Você completou o tutorial '{tutorial.title}'"
                }
            
            # Próximo passo
            progress["current_step"] = next_step_index
            next_step = tutorial.steps[next_step_index]
            
            completion_percentage = (next_step_index / len(tutorial.steps)) * 100
            
            return {
                "tutorial": tutorial,
                "current_step": next_step,
                "progress": {
                    "step": next_step_index + 1,
                    "total_steps": len(tutorial.steps),
                    "percentage": completion_percentage
                },
                "estimated_remaining_time": tutorial.estimated_time * (1 - completion_percentage / 100)
            }
            
        except Exception as e:
            logger.error(f"Erro ao avançar tutorial: {e}")
            raise
    
    async def get_available_tutorials(self, difficulty_filter: Optional[str] = None) -> List[Tutorial]:
        """Retorna tutoriais disponíveis"""
        tutorials = list(self.tutorials.values())
        
        if difficulty_filter:
            tutorials = [t for t in tutorials if t.difficulty_level.lower() == difficulty_filter.lower()]
        
        return tutorials

# Instâncias globais
technical_chatbot = TechnicalChatbot()
voice_controller = VoiceController()
nlp_processor = NLPProcessor()
interactive_tutorials = InteractiveTutorials()

# Funções de conveniência
async def process_chat_message(user_id: str, content: str, context: Dict[str, Any] = None) -> ChatResponse:
    """Função de conveniência para processar mensagem do chat"""
    message = ChatMessage(
        message_id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        user_id=user_id,
        content=content,
        message_type=MessageType.GENERAL_CHAT,  # Será reclassificado
        timestamp=datetime.now(),
        context=context or {}
    )
    
    return await technical_chatbot.process_message(message)

async def process_voice_input(voice_text: str) -> VoiceCommandResult:
    """Função de conveniência para processar comando de voz"""
    return await voice_controller.process_voice_command(voice_text)

async def analyze_natural_language(text: str) -> Dict[str, Any]:
    """Função de conveniência para análise NLP"""
    return await nlp_processor.extract_intent_and_entities(text)

async def start_interactive_tutorial(tutorial_id: str, user_id: str) -> Dict[str, Any]:
    """Função de conveniência para iniciar tutorial"""
    return await interactive_tutorials.start_tutorial(tutorial_id, user_id)