# -*- coding: utf-8 -*-
"""
Sistema de Chatbot TÃ©cnico e Interface Conversacional
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
    """Comandos de voz disponÃ­veis"""
    START_DIAGNOSTIC = "iniciar diagnÃ³stico"
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
    """Chatbot tÃ©cnico especializado em diagnÃ³sticos"""
    
    def __init__(self):
        self.conversation_history = {}
        self.user_contexts = {}
        self.knowledge_base = self._load_knowledge_base()
        self.response_templates = self._load_response_templates()
        self.diagnostic_patterns = self._load_diagnostic_patterns()
        
    async def process_message(self, message: ChatMessage) -> ChatResponse:
        """Processa mensagem do usuÃ¡rio e gera resposta"""
        try:
            # Atualizar contexto do usuÃ¡rio
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
            
            # Armazenar no histÃ³rico
            self._store_conversation(message, response)
            
            logger.info(f"Resposta gerada para usuÃ¡rio {message.user_id}")
            return response
            
        except Exception as e:
            logger.error(f"Erro no processamento da mensagem: {e}")
            return self._create_error_response(str(e))
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Carrega base de conhecimento tÃ©cnico"""
        return {
            "hardware_issues": {
                "cpu_overheating": {
                    "symptoms": ["alta temperatura", "lentidÃ£o", "travamentos"],
                    "solutions": ["verificar ventilaÃ§Ã£o", "limpar cooler", "trocar pasta tÃ©rmica"],
                    "urgency": "alta"
                },
                "memory_problems": {
                    "symptoms": ["erro de memÃ³ria", "tela azul", "travamentos aleatÃ³rios"],
                    "solutions": ["testar memÃ³ria", "verificar slots", "substituir mÃ³dulos"],
                    "urgency": "mÃ©dia"
                },
                "disk_failure": {
                    "symptoms": ["ruÃ­dos estranhos", "lentidÃ£o", "erros de leitura"],
                    "solutions": ["backup imediato", "verificar saÃºde do disco", "substituir HD"],
                    "urgency": "crÃ­tica"
                }
            },
            "software_issues": {
                "slow_performance": {
                    "symptoms": ["sistema lento", "demora para abrir programas"],
                    "solutions": ["limpeza de disco", "desfragmentaÃ§Ã£o", "otimizaÃ§Ã£o"],
                    "urgency": "baixa"
                },
                "virus_malware": {
                    "symptoms": ["comportamento estranho", "pop-ups", "lentidÃ£o"],
                    "solutions": ["scan antivÃ­rus", "modo seguro", "limpeza profunda"],
                    "urgency": "alta"
                }
            },
            "network_issues": {
                "connection_problems": {
                    "symptoms": ["sem internet", "conexÃ£o instÃ¡vel", "lentidÃ£o"],
                    "solutions": ["reiniciar modem", "verificar cabos", "atualizar drivers"],
                    "urgency": "mÃ©dia"
                }
            }
        }
    
    def _load_response_templates(self) -> Dict[str, str]:
        """Carrega templates de resposta"""
        return {
            "greeting": "OlÃ¡! Sou o assistente tÃ©cnico do TechZe. Como posso ajudÃ¡-lo hoje?",
            "diagnostic_start": "Vou iniciar um diagnÃ³stico do seu sistema. Isso pode levar alguns minutos...",
            "help_offer": "Posso ajudÃ¡-lo com diagnÃ³sticos, troubleshooting e otimizaÃ§Ã£o do sistema. O que vocÃª gostaria de fazer?",
            "clarification": "Poderia fornecer mais detalhes sobre o problema que estÃ¡ enfrentando?",
            "solution_found": "Encontrei uma possÃ­vel soluÃ§Ã£o para seu problema:",
            "no_solution": "NÃ£o consegui encontrar uma soluÃ§Ã£o especÃ­fica, mas posso sugerir algumas verificaÃ§Ãµes gerais.",
            "action_confirmation": "Gostaria que eu execute esta aÃ§Ã£o automaticamente?",
            "tutorial_offer": "Posso criar um tutorial passo-a-passo para resolver este problema. Interessado?"
        }
    
    def _load_diagnostic_patterns(self) -> Dict[str, List[str]]:
        """Carrega padrÃµes para identificar problemas"""
        return {
            "performance": [
                r"lento|lentidÃ£o|devagar|demorado",
                r"travando|trava|freeze|congelando",
                r"performance|desempenho|velocidade"
            ],
            "hardware": [
                r"temperatura|quente|superaquecimento",
                r"ruÃ­do|barulho|ventilador",
                r"memÃ³ria|ram|disco|hd|ssd"
            ],
            "network": [
                r"internet|rede|conexÃ£o|wifi",
                r"lento para navegar|pÃ¡ginas nÃ£o carregam",
                r"desconectando|instÃ¡vel"
            ],
            "software": [
                r"programa|aplicativo|software",
                r"erro|falha|crash|fechando",
                r"vÃ­rus|malware|antivÃ­rus"
            ]
        }
    
    def _update_user_context(self, message: ChatMessage):
        """Atualiza contexto do usuÃ¡rio"""
        user_id = message.user_id
        
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = {
                'first_interaction': datetime.now(),
                'message_count': 0,
                'topics_discussed': [],
                'current_issue': None,
                'preferred_language': message.language,
                'technical_level': 'beginner'  # SerÃ¡ inferido
            }
        
        context = self.user_contexts[user_id]
        context['message_count'] += 1
        context['last_interaction'] = datetime.now()
        
        # Inferir nÃ­vel tÃ©cnico baseado no vocabulÃ¡rio
        technical_terms = ['driver', 'registry', 'bios', 'kernel', 'api', 'tcp', 'dns']
        if any(term in message.content.lower() for term in technical_terms):
            context['technical_level'] = 'advanced'
        elif context['message_count'] > 5:
            context['technical_level'] = 'intermediate'
    
    def _classify_message(self, content: str) -> MessageType:
        """Classifica o tipo de mensagem"""
        content_lower = content.lower()
        
        # PadrÃµes para classificaÃ§Ã£o
        diagnostic_patterns = [
            r"diagnÃ³stico|diagnosticar|verificar|analisar",
            r"problema|erro|falha|nÃ£o funciona",
            r"o que estÃ¡ errado|qual o problema"
        ]
        
        help_patterns = [
            r"ajuda|help|socorro|nÃ£o sei",
            r"como fazer|como resolver|tutorial",
            r"preciso de ajuda"
        ]
        
        command_patterns = [
            r"execute|executar|fazer|iniciar",
            r"otimizar|limpar|corrigir|consertar",
            r"reiniciar|parar|cancelar"
        ]
        
        troubleshooting_patterns = [
            r"meu computador|minha mÃ¡quina|sistema",
            r"estÃ¡ lento|nÃ£o liga|travando|congelando",
            r"internet nÃ£o funciona|sem conexÃ£o"
        ]
        
        # Verificar padrÃµes
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
        """Trata solicitaÃ§Ãµes de diagnÃ³stico"""
        response_content = self.response_templates["diagnostic_start"]
        
        # Simular diagnÃ³stico
        diagnostic_results = {
            "cpu_usage": 75,
            "memory_usage": 68,
            "disk_health": 92,
            "network_status": "ok",
            "issues_found": ["Alto uso de CPU", "FragmentaÃ§Ã£o de disco"]
        }
        
        response_content += f"\n\nResultados do diagnÃ³stico:\n"
        response_content += f"â€¢ CPU: {diagnostic_results['cpu_usage']}% de uso\n"
        response_content += f"â€¢ MemÃ³ria: {diagnostic_results['memory_usage']}% de uso\n"
        response_content += f"â€¢ SaÃºde do disco: {diagnostic_results['disk_health']}%\n"
        
        if diagnostic_results['issues_found']:
            response_content += f"\nProblemas encontrados:\n"
            for issue in diagnostic_results['issues_found']:
                response_content += f"â€¢ {issue}\n"
        
        suggested_actions = [
            "Otimizar sistema automaticamente",
            "Ver tutorial de otimizaÃ§Ã£o manual",
            "Agendar manutenÃ§Ã£o preventiva"
        ]
        
        follow_up_questions = [
            "Gostaria que eu otimize o sistema automaticamente?",
            "Quer ver um tutorial detalhado de como resolver estes problemas?",
            "Precisa de mais informaÃ§Ãµes sobre algum problema especÃ­fico?"
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
        """Trata solicitaÃ§Ãµes de troubleshooting"""
        content = message.content.lower()
        
        # Identificar categoria do problema
        problem_category = None
        for category, patterns in self.diagnostic_patterns.items():
            if any(re.search(pattern, content) for pattern in patterns):
                problem_category = category
                break
        
        if problem_category and problem_category in self.knowledge_base:
            # Encontrar problema especÃ­fico
            category_issues = self.knowledge_base[problem_category]
            
            for issue_name, issue_data in category_issues.items():
                symptoms = issue_data["symptoms"]
                if any(symptom in content for symptom in symptoms):
                    solutions = issue_data["solutions"]
                    urgency = issue_data["urgency"]
                    
                    response_content = f"Identifiquei que vocÃª pode estar enfrentando: **{issue_name.replace('_', ' ').title()}**\n\n"
                    response_content += f"UrgÃªncia: {urgency.upper()}\n\n"
                    response_content += "SoluÃ§Ãµes recomendadas:\n"
                    
                    for i, solution in enumerate(solutions, 1):
                        response_content += f"{i}. {solution}\n"
                    
                    suggested_actions = [
                        "Executar correÃ§Ã£o automÃ¡tica",
                        "Ver tutorial detalhado",
                        "Agendar suporte tÃ©cnico"
                    ]
                    
                    return ChatResponse(
                        response_id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        content=response_content,
                        response_type=ResponseType.ANSWER,
                        confidence=0.8,
                        suggested_actions=suggested_actions,
                        follow_up_questions=["Gostaria que eu execute alguma dessas soluÃ§Ãµes?"],
                        timestamp=datetime.now(),
                        metadata={"problem_category": problem_category, "issue": issue_name}
                    )
        
        # Resposta genÃ©rica se nÃ£o encontrou problema especÃ­fico
        response_content = self.response_templates["clarification"]
        response_content += "\n\nPara ajudÃ¡-lo melhor, poderia me contar:\n"
        response_content += "â€¢ Quando o problema comeÃ§ou?\n"
        response_content += "â€¢ O que vocÃª estava fazendo quando aconteceu?\n"
        response_content += "â€¢ HÃ¡ alguma mensagem de erro especÃ­fica?\n"
        
        return ChatResponse(
            response_id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=response_content,
            response_type=ResponseType.CLARIFICATION_REQUEST,
            confidence=0.6,
            suggested_actions=["Executar diagnÃ³stico completo"],
            follow_up_questions=["Gostaria que eu execute um diagnÃ³stico completo?"],
            timestamp=datetime.now(),
            metadata={}
        )
    
    async def _handle_help_request(self, message: ChatMessage) -> ChatResponse:
        """Trata solicitaÃ§Ãµes de ajuda"""
        user_context = self.user_contexts.get(message.user_id, {})
        technical_level = user_context.get('technical_level', 'beginner')
        
        if technical_level == 'beginner':
            response_content = "Vou ajudÃ¡-lo de forma simples e clara!\n\n"
            response_content += "Posso ajudar com:\n"
            response_content += "â€¢ **DiagnÃ³stico automÃ¡tico** - Verifico seu sistema e encontro problemas\n"
            response_content += "â€¢ **Tutoriais passo-a-passo** - Ensino como resolver problemas\n"
            response_content += "â€¢ **OtimizaÃ§Ã£o automÃ¡tica** - Melhoro a performance do seu computador\n"
            response_content += "â€¢ **Suporte em tempo real** - Respondo suas dÃºvidas tÃ©cnicas\n"
        else:
            response_content = "Como tÃ©cnico experiente, posso oferecer:\n\n"
            response_content += "â€¢ **AnÃ¡lise avanÃ§ada de sistema** - MÃ©tricas detalhadas e logs\n"
            response_content += "â€¢ **AutomaÃ§Ã£o de correÃ§Ãµes** - Scripts e workflows personalizados\n"
            response_content += "â€¢ **Monitoramento preditivo** - Alertas antes dos problemas acontecerem\n"
            response_content += "â€¢ **IntegraÃ§Ã£o com ferramentas** - APIs e integraÃ§Ãµes avanÃ§adas\n"
        
        suggested_actions = [
            "Iniciar diagnÃ³stico do sistema",
            "Ver tutoriais disponÃ­veis",
            "Configurar monitoramento automÃ¡tico",
            "Acessar documentaÃ§Ã£o tÃ©cnica"
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
        """Trata comandos do usuÃ¡rio"""
        content = message.content.lower()
        
        if "otimizar" in content or "otimizaÃ§Ã£o" in content:
            response_content = "Iniciando otimizaÃ§Ã£o automÃ¡tica do sistema...\n\n"
            response_content += "AÃ§Ãµes que serÃ£o executadas:\n"
            response_content += "â€¢ Limpeza de arquivos temporÃ¡rios\n"
            response_content += "â€¢ OtimizaÃ§Ã£o de memÃ³ria\n"
            response_content += "â€¢ DesfragmentaÃ§Ã£o de disco\n"
            response_content += "â€¢ AtualizaÃ§Ã£o de drivers\n\n"
            response_content += "Tempo estimado: 5-10 minutos"
            
            return ChatResponse(
                response_id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content=response_content,
                response_type=ResponseType.ACTION_CONFIRMATION,
                confidence=0.9,
                suggested_actions=["Confirmar otimizaÃ§Ã£o", "Cancelar", "Ver detalhes"],
                follow_up_questions=["Posso prosseguir com a otimizaÃ§Ã£o?"],
                timestamp=datetime.now(),
                metadata={"command": "optimize", "estimated_time": 600}
            )
        
        elif "diagnÃ³stico" in content or "verificar" in content:
            return await self._handle_diagnostic_request(message)
        
        else:
            response_content = "Comando nÃ£o reconhecido. Comandos disponÃ­veis:\n\n"
            response_content += "â€¢ **otimizar sistema** - Melhora performance\n"
            response_content += "â€¢ **executar diagnÃ³stico** - Verifica problemas\n"
            response_content += "â€¢ **limpar disco** - Remove arquivos desnecessÃ¡rios\n"
            response_content += "â€¢ **verificar atualizaÃ§Ãµes** - Busca updates\n"
            
            return ChatResponse(
                response_id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                content=response_content,
                response_type=ResponseType.ANSWER,
                confidence=0.7,
                suggested_actions=["Ver todos os comandos", "Executar diagnÃ³stico"],
                follow_up_questions=["Qual comando gostaria de executar?"],
                timestamp=datetime.now(),
                metadata={"command": "unknown"}
            )
    
    async def _handle_general_chat(self, message: ChatMessage) -> ChatResponse:
        """Trata conversas gerais"""
        content = message.content.lower()
        
        # SaudaÃ§Ãµes
        if any(greeting in content for greeting in ["oi", "olÃ¡", "hello", "bom dia", "boa tarde", "boa noite"]):
            response_content = self.response_templates["greeting"]
            response_content += "\n\n" + self.response_templates["help_offer"]
        
        # Agradecimentos
        elif any(thanks in content for thanks in ["obrigado", "obrigada", "valeu", "thanks"]):
            response_content = "Fico feliz em ajudar! ğŸ˜Š\n\n"
            response_content += "Se precisar de mais alguma coisa, estarei aqui. "
            response_content += "Posso continuar monitorando seu sistema ou ajudar com outros problemas."
        
        # Despedidas
        elif any(bye in content for bye in ["tchau", "atÃ© logo", "bye", "adeus"]):
            response_content = "AtÃ© logo! Foi um prazer ajudÃ¡-lo. ğŸ‘‹\n\n"
            response_content += "Lembre-se: estou sempre disponÃ­vel para diagnÃ³sticos e suporte tÃ©cnico. "
            response_content += "Tenha um Ã³timo dia!"
        
        else:
            response_content = "Entendo que vocÃª quer conversar, mas sou especializado em suporte tÃ©cnico! ğŸ¤–\n\n"
            response_content += "Posso ajudÃ¡-lo com:\n"
            response_content += "â€¢ Problemas de computador\n"
            response_content += "â€¢ OtimizaÃ§Ã£o de sistema\n"
            response_content += "â€¢ DiagnÃ³sticos tÃ©cnicos\n"
            response_content += "â€¢ Tutoriais e dicas\n\n"
            response_content += "Sobre o que gostaria de conversar?"
        
        return ChatResponse(
            response_id=f"resp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            content=response_content,
            response_type=ResponseType.ANSWER,
            confidence=0.8,
            suggested_actions=["Executar diagnÃ³stico", "Ver tutoriais", "Otimizar sistema"],
            follow_up_questions=["Como posso ajudÃ¡-lo tecnicamente hoje?"],
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
            follow_up_questions=["Posso ajudÃ¡-lo de outra forma?"],
            timestamp=datetime.now(),
            metadata={"error": error_message}
        )
    
    def _store_conversation(self, message: ChatMessage, response: ChatResponse):
        """Armazena conversa no histÃ³rico"""
        user_id = message.user_id
        
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            'message': message,
            'response': response,
            'timestamp': datetime.now()
        })
        
        # Manter apenas Ãºltimas 50 mensagens por usuÃ¡rio
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id] = self.conversation_history[user_id][-50:]

class VoiceController:
    """Controlador de comandos por voz"""
    
    def __init__(self):
        self.voice_commands = self._load_voice_commands()
        self.command_history = []
        
    def _load_voice_commands(self) -> Dict[str, VoiceCommand]:
        """Carrega comandos de voz disponÃ­veis"""
        return {
            "iniciar diagnÃ³stico": VoiceCommand.START_DIAGNOSTIC,
            "comeÃ§ar diagnÃ³stico": VoiceCommand.START_DIAGNOSTIC,
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
            
            # Encontrar comando mais prÃ³ximo
            best_match = None
            best_confidence = 0.0
            
            for command_text, command_enum in self.voice_commands.items():
                # VerificaÃ§Ã£o exata
                if command_text == voice_text_clean:
                    best_match = command_enum
                    best_confidence = 1.0
                    break
                
                # VerificaÃ§Ã£o parcial
                elif command_text in voice_text_clean or voice_text_clean in command_text:
                    confidence = len(command_text) / max(len(voice_text_clean), len(command_text))
                    if confidence > best_confidence:
                        best_match = command_enum
                        best_confidence = confidence
            
            if best_match and best_confidence > 0.6:
                # Executar comando
                result = await self._execute_voice_command(best_match, voice_text_clean)
                result.confidence = best_confidence
                
                # Armazenar no histÃ³rico
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
                    response_text="Comando nÃ£o reconhecido. Diga 'ajuda' para ver comandos disponÃ­veis."
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
                confidence=0.0,  # SerÃ¡ definido depois
                parameters={"diagnostic_type": "full"},
                action_taken=True,
                response_text="Iniciando diagnÃ³stico completo do sistema. Aguarde alguns minutos..."
            )
        
        elif command == VoiceCommand.SHOW_STATUS:
            return VoiceCommandResult(
                command=command,
                confidence=0.0,
                parameters={},
                action_taken=True,
                response_text="Sistema funcionando normalmente. CPU: 45%, MemÃ³ria: 62%, Disco: 78% livre."
            )
        
        elif command == VoiceCommand.OPTIMIZE_SYSTEM:
            return VoiceCommandResult(
                command=command,
                confidence=0.0,
                parameters={"optimization_level": "standard"},
                action_taken=True,
                response_text="Iniciando otimizaÃ§Ã£o automÃ¡tica. Isso pode levar alguns minutos..."
            )
        
        elif command == VoiceCommand.HELP:
            help_text = "Comandos disponÃ­veis:\n"
            help_text += "â€¢ 'Iniciar diagnÃ³stico' - Verifica o sistema\n"
            help_text += "â€¢ 'Mostrar status' - Exibe status atual\n"
            help_text += "â€¢ 'Otimizar sistema' - Melhora performance\n"
            help_text += "â€¢ 'Parar' - Cancela operaÃ§Ã£o atual\n"
            help_text += "â€¢ 'Repetir' - Repete Ãºltimo comando"
            
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
                response_text="OperaÃ§Ã£o cancelada."
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
                response_text="Comando nÃ£o implementado."
            )

class NLPProcessor:
    """Processador de linguagem natural"""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.entity_patterns = self._load_entity_patterns()
        
    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Carrega padrÃµes de intenÃ§Ã£o"""
        return {
            "diagnostic_intent": [
                r"verificar|checar|analisar|diagnosticar",
                r"problema|erro|falha|defeito",
                r"o que estÃ¡ errado|qual o problema"
            ],
            "optimization_intent": [
                r"otimizar|melhorar|acelerar|limpar",
                r"performance|desempenho|velocidade",
                r"mais rÃ¡pido|menos lento"
            ],
            "help_intent": [
                r"ajuda|help|socorro|nÃ£o sei",
                r"como fazer|como resolver",
                r"ensinar|tutorial|explicar"
            ],
            "status_intent": [
                r"status|estado|situaÃ§Ã£o|como estÃ¡",
                r"funcionando|rodando|operando",
                r"saÃºde|condiÃ§Ã£o"
            ]
        }
    
    def _load_entity_patterns(self) -> Dict[str, List[str]]:
        """Carrega padrÃµes de entidades"""
        return {
            "hardware_components": [
                r"cpu|processador|processor",
                r"memÃ³ria|ram|memory",
                r"disco|hd|ssd|storage",
                r"placa de vÃ­deo|gpu|graphics",
                r"fonte|power supply|psu"
            ],
            "software_components": [
                r"sistema operacional|windows|linux|macos",
                r"driver|drivers|device driver",
                r"programa|aplicativo|software|app",
                r"antivÃ­rus|firewall|security"
            ],
            "problem_types": [
                r"lento|lentidÃ£o|slow|devagar",
                r"travando|freeze|congelando|hanging",
                r"erro|error|falha|failure",
                r"ruÃ­do|barulho|noise|sound"
            ]
        }
    
    async def extract_intent_and_entities(self, text: str) -> Dict[str, Any]:
        """Extrai intenÃ§Ã£o e entidades do texto"""
        try:
            text_lower = text.lower()
            
            # Extrair intenÃ§Ã£o
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
            logger.error(f"Erro na extraÃ§Ã£o NLP: {e}")
            return {
                "intent": "unknown",
                "entities": {},
                "context": {},
                "confidence": 0.0,
                "original_text": text
            }
    
    def _extract_intent(self, text: str) -> str:
        """Extrai intenÃ§Ã£o principal do texto"""
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
        
        # UrgÃªncia
        if any(word in text for word in ["urgente", "crÃ­tico", "emergÃªncia", "agora"]):
            context["urgency"] = "high"
        elif any(word in text for word in ["quando possÃ­vel", "nÃ£o urgente", "depois"]):
            context["urgency"] = "low"
        else:
            context["urgency"] = "medium"
        
        # FrequÃªncia do problema
        if any(word in text for word in ["sempre", "toda vez", "constantemente"]):
            context["frequency"] = "always"
        elif any(word in text for word in ["Ã s vezes", "ocasionalmente", "raramente"]):
            context["frequency"] = "sometimes"
        else:
            context["frequency"] = "unknown"
        
        # DuraÃ§Ã£o
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
        """Calcula confianÃ§a da anÃ¡lise NLP"""
        confidence = 0.5  # Base
        
        # IntenÃ§Ã£o identificada
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
        """Carrega tutoriais disponÃ­veis"""
        tutorials = {}
        
        # Tutorial de otimizaÃ§Ã£o bÃ¡sica
        tutorials["basic_optimization"] = Tutorial(
            tutorial_id="basic_optimization",
            title="OtimizaÃ§Ã£o BÃ¡sica do Sistema",
            description="Aprenda a otimizar seu computador em passos simples",
            difficulty_level="Iniciante",
            estimated_time=15,
            steps=[
                {
                    "step_number": 1,
                    "title": "Limpeza de Arquivos TemporÃ¡rios",
                    "description": "Vamos limpar arquivos que nÃ£o sÃ£o mais necessÃ¡rios",
                    "instructions": [
                        "Pressione Windows + R",
                        "Digite '%temp%' e pressione Enter",
                        "Selecione todos os arquivos (Ctrl + A)",
                        "Delete os arquivos selecionados"
                    ],
                    "expected_result": "EspaÃ§o em disco liberado",
                    "troubleshooting": "Se alguns arquivos nÃ£o puderem ser deletados, pule-os"
                },
                {
                    "step_number": 2,
                    "title": "Limpeza de Disco",
                    "description": "Use a ferramenta nativa do Windows",
                    "instructions": [
                        "Abra 'Este Computador'",
                        "Clique com botÃ£o direito no disco C:",
                        "Selecione 'Propriedades'",
                        "Clique em 'Limpeza de Disco'",
                        "Marque todas as opÃ§Ãµes e clique 'OK'"
                    ],
                    "expected_result": "Mais espaÃ§o liberado",
                    "troubleshooting": "O processo pode demorar alguns minutos"
                }
            ],
            prerequisites=[],
            category="ManutenÃ§Ã£o"
        )
        
        # Tutorial de diagnÃ³stico de hardware
        tutorials["hardware_diagnostic"] = Tutorial(
            tutorial_id="hardware_diagnostic",
            title="DiagnÃ³stico de Hardware",
            description="Como verificar a saÃºde dos componentes do seu PC",
            difficulty_level="IntermediÃ¡rio",
            estimated_time=30,
            steps=[
                {
                    "step_number": 1,
                    "title": "VerificaÃ§Ã£o de Temperatura",
                    "description": "Monitore as temperaturas dos componentes",
                    "instructions": [
                        "Baixe o HWiNFO64 ou similar",
                        "Execute o programa",
                        "Observe as temperaturas de CPU e GPU",
                        "Verifique se estÃ£o abaixo de 80Â°C"
                    ],
                    "expected_result": "Temperaturas normais identificadas",
                    "troubleshooting": "Se temperaturas altas, verifique ventilaÃ§Ã£o"
                }
            ],
            prerequisites=["Conhecimento bÃ¡sico de hardware"],
            category="DiagnÃ³stico"
        )
        
        return tutorials
    
    async def start_tutorial(self, tutorial_id: str, user_id: str) -> Dict[str, Any]:
        """Inicia um tutorial para o usuÃ¡rio"""
        try:
            if tutorial_id not in self.tutorials:
                raise Exception(f"Tutorial {tutorial_id} nÃ£o encontrado")
            
            tutorial = self.tutorials[tutorial_id]
            
            # Inicializar progresso do usuÃ¡rio
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
        """AvanÃ§a para o prÃ³ximo passo do tutorial"""
        try:
            if user_id not in self.user_progress or tutorial_id not in self.user_progress[user_id]:
                raise Exception("Tutorial nÃ£o iniciado")
            
            tutorial = self.tutorials[tutorial_id]
            progress = self.user_progress[user_id][tutorial_id]
            
            # Marcar passo atual como completo
            current_step_index = progress["current_step"]
            if current_step_index not in progress["completed_steps"]:
                progress["completed_steps"].append(current_step_index)
            
            # AvanÃ§ar para prÃ³ximo passo
            next_step_index = current_step_index + 1
            
            if next_step_index >= len(tutorial.steps):
                # Tutorial completo
                progress["status"] = "completed"
                progress["completed_at"] = datetime.now()
                
                return {
                    "tutorial_completed": True,
                    "completion_time": progress["completed_at"] - progress["started_at"],
                    "message": f"ParabÃ©ns! VocÃª completou o tutorial '{tutorial.title}'"
                }
            
            # PrÃ³ximo passo
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
            logger.error(f"Erro ao avanÃ§ar tutorial: {e}")
            raise
    
    async def get_available_tutorials(self, difficulty_filter: Optional[str] = None) -> List[Tutorial]:
        """Retorna tutoriais disponÃ­veis"""
        tutorials = list(self.tutorials.values())
        
        if difficulty_filter:
            tutorials = [t for t in tutorials if t.difficulty_level.lower() == difficulty_filter.lower()]
        
        return tutorials

# InstÃ¢ncias globais
technical_chatbot = TechnicalChatbot()
voice_controller = VoiceController()
nlp_processor = NLPProcessor()
interactive_tutorials = InteractiveTutorials()

# FunÃ§Ãµes de conveniÃªncia
async def process_chat_message(user_id: str, content: str, context: Dict[str, Any] = None) -> ChatResponse:
    """FunÃ§Ã£o de conveniÃªncia para processar mensagem do chat"""
    message = ChatMessage(
        message_id=f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        user_id=user_id,
        content=content,
        message_type=MessageType.GENERAL_CHAT,  # SerÃ¡ reclassificado
        timestamp=datetime.now(),
        context=context or {}
    )
    
    return await technical_chatbot.process_message(message)

async def process_voice_input(voice_text: str) -> VoiceCommandResult:
    """FunÃ§Ã£o de conveniÃªncia para processar comando de voz"""
    return await voice_controller.process_voice_command(voice_text)

async def analyze_natural_language(text: str) -> Dict[str, Any]:
    """FunÃ§Ã£o de conveniÃªncia para anÃ¡lise NLP"""
    return await nlp_processor.extract_intent_and_entities(text)

async def start_interactive_tutorial(tutorial_id: str, user_id: str) -> Dict[str, Any]:
    """FunÃ§Ã£o de conveniÃªncia para iniciar tutorial"""
    return await interactive_tutorials.start_tutorial(tutorial_id, user_id)