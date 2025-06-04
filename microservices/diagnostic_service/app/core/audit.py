"""
Sistema de Auditoria Completo para TechZe Diagnóstico
"""
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
from dataclasses import dataclass, asdict
from fastapi import Request
import logging

logger = logging.getLogger(__name__)


class AuditEventType(str, Enum):
    """Tipos de eventos de auditoria"""
    # Autenticação
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILED = "auth.login.failed"
    LOGOUT = "auth.logout"
    TOKEN_REFRESH = "auth.token.refresh"
    
    # Diagnósticos
    DIAGNOSTIC_CREATED = "diagnostic.created"
    DIAGNOSTIC_STARTED = "diagnostic.started"
    DIAGNOSTIC_COMPLETED = "diagnostic.completed"
    DIAGNOSTIC_FAILED = "diagnostic.failed"
    DIAGNOSTIC_DELETED = "diagnostic.deleted"
    
    # Relatórios
    REPORT_GENERATED = "report.generated"
    REPORT_DOWNLOADED = "report.downloaded"
    REPORT_SHARED = "report.shared"
    REPORT_DELETED = "report.deleted"
    
    # Sistema
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"
    
    # Segurança
    RATE_LIMIT_EXCEEDED = "security.rate_limit.exceeded"
    UNAUTHORIZED_ACCESS = "security.unauthorized.access"
    SUSPICIOUS_ACTIVITY = "security.suspicious.activity"
    
    # Dados
    DATA_CREATED = "data.created"
    DATA_UPDATED = "data.updated"
    DATA_DELETED = "data.deleted"
    DATA_ACCESSED = "data.accessed"


class AuditSeverity(str, Enum):
    """Níveis de severidade dos eventos"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Evento de auditoria"""
    id: str
    timestamp: datetime
    event_type: AuditEventType
    severity: AuditSeverity
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    endpoint: Optional[str]
    method: Optional[str]
    resource_id: Optional[str]
    resource_type: Optional[str]
    action: str
    details: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data
    
    def to_json(self) -> str:
        """Converte para JSON"""
        return json.dumps(self.to_dict(), default=str)


class AuditLogger:
    """Logger de auditoria com múltiplos backends"""
    
    def __init__(self, 
                 log_to_file: bool = True,
                 log_to_supabase: bool = True,
                 log_to_console: bool = True,
                 file_path: str = "/tmp/audit.log"):
        self.log_to_file = log_to_file
        self.log_to_supabase = log_to_supabase
        self.log_to_console = log_to_console
        self.file_path = file_path
        
        # Setup file logger
        if self.log_to_file:
            self.file_logger = logging.getLogger("audit_file")
            self.file_logger.setLevel(logging.INFO)
            
            # Remove handlers existentes
            for handler in self.file_logger.handlers[:]:
                self.file_logger.removeHandler(handler)
            
            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - AUDIT - %(message)s')
            )
            self.file_logger.addHandler(file_handler)
            self.file_logger.propagate = False
    
    async def log_event(self, event: AuditEvent):
        """Registra evento de auditoria"""
        try:
            # Log para console
            if self.log_to_console:
                logger.info(f"AUDIT: {event.event_type} - {event.action} - User: {event.user_id} - IP: {event.ip_address}")
            
            # Log para arquivo
            if self.log_to_file:
                self.file_logger.info(event.to_json())
            
            # Log para Supabase (implementar quando necessário)
            if self.log_to_supabase:
                await self._log_to_supabase(event)
                
        except Exception as e:
            logger.error(f"Erro ao registrar evento de auditoria: {e}")
    
    async def _log_to_supabase(self, event: AuditEvent):
        """Registra evento no Supabase"""
        try:
            # Obtém cliente do Supabase
            from app.core.supabase import get_supabase_client
            supabase_client = get_supabase_client()
            
            # Converte o evento para dicionário
            event_data = event.to_dict()
            
            # Ajusta tipos de dados para compatibilidade com Supabase
            self._prepare_event_data_for_supabase(event_data)
            
            # Tenta inserir o evento na tabela de auditoria
            result = supabase_client.table("audit_logs").insert(event_data).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Erro ao inserir log no Supabase: {result.error}")
                
                # Verifica se é um erro de esquema/tipos
                if "violates not-null constraint" in str(result.error) or "invalid input syntax" in str(result.error):
                    # Fallback 1: Tenta simplificar o evento removendo campos problemáticos
                    return await self._try_fallback_insert(supabase_client, event_data, result.error)
                else:
                    # Outros erros (conexão, permissão, etc)
                    logger.error(f"Erro de conexão/permissão ao inserir log: {result.error}")
                    return False
            else:
                logger.debug(f"Log de auditoria registrado no Supabase: {event.id}")
                return True
                
        except Exception as e:
            logger.error(f"Erro ao registrar no Supabase: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
            
    def _prepare_event_data_for_supabase(self, event_data: Dict[str, Any]) -> None:
        """Prepara os dados do evento para inserção no Supabase"""
        # Ajusta o user_id para UUID se possível
        if "user_id" in event_data and event_data["user_id"] is not None:
            try:
                # Verifica se é um UUID válido
                import uuid
                if not isinstance(event_data["user_id"], uuid.UUID):
                    try:
                        uuid.UUID(event_data["user_id"])
                    except ValueError:
                        # Se não for UUID válido, define como None
                        event_data["user_id"] = None
            except Exception:
                event_data["user_id"] = None
                
        # Garante que o timestamp esteja em formato ISO
        if "timestamp" in event_data:
            if isinstance(event_data["timestamp"], datetime):
                event_data["timestamp"] = event_data["timestamp"].isoformat()
                
        # Garante que details seja um objeto JSON válido
        if "details" in event_data:
            if not isinstance(event_data["details"], dict):
                try:
                    if isinstance(event_data["details"], str):
                        import json
                        event_data["details"] = json.loads(event_data["details"])
                    else:
                        event_data["details"] = {}
                except Exception:
                    event_data["details"] = {}
            
            # Converte valores não serializáveis em strings
            try:
                import json
                json.dumps(event_data["details"])
            except (TypeError, OverflowError):
                self._sanitize_json_object(event_data["details"])
                
    def _sanitize_json_object(self, obj: Dict[str, Any]) -> None:
        """Sanitiza um objeto JSON para garantir que seja serializável"""
        for key, value in list(obj.items()):
            if isinstance(value, dict):
                self._sanitize_json_object(value)
            elif not isinstance(value, (str, int, float, bool, type(None), list)):
                obj[key] = str(value)
            elif isinstance(value, list):
                obj[key] = [str(item) if not isinstance(item, (str, int, float, bool, type(None))) else item 
                           for item in value]
                
    async def _try_fallback_insert(self, supabase_client, event_data: Dict[str, Any], original_error) -> bool:
        """Tenta inserção com fallback para dados simplificados"""
        try:
            # Fallback 1: Versão simplificada do evento
            fallback_event = {
                "id": event_data["id"],
                "timestamp": event_data["timestamp"],
                "event_type": event_data["event_type"],
                "severity": event_data["severity"],
                "user_id": None,  # Evita problemas de tipo
                "action": event_data["action"],
                "details": json.dumps({
                    "original_event": "Evento original simplificado devido a erro de inserção",
                    "error": str(original_error),
                    "event_type": event_data["event_type"],
                    "resource_type": event_data.get("resource_type", "unknown"),
                    "resource_id": event_data.get("resource_id")
                }),
                "success": event_data["success"]
            }
            
            fallback_result = supabase_client.table("audit_logs").insert(fallback_event).execute()
            
            if hasattr(fallback_result, 'error') and fallback_result.error:
                logger.error(f"Erro no fallback de auditoria: {fallback_result.error}")
                
                # Fallback 2: Versão minimalista do evento (último recurso)
                minimal_event = {
                    "id": event_data["id"],
                    "timestamp": event_data["timestamp"],
                    "event_type": "system.error",
                    "severity": "high",
                    "action": "audit.fallback",
                    "details": json.dumps({"message": "Evento de auditoria falhou ao ser registrado"}),
                    "success": False
                }
                
                minimal_result = supabase_client.table("audit_logs").insert(minimal_event).execute()
                
                if hasattr(minimal_result, 'error') and minimal_result.error:
                    logger.error(f"Erro no fallback minimalista de auditoria: {minimal_result.error}")
                    return False
                else:
                    logger.info(f"Log de auditoria registrado via fallback minimalista: {event_data['id']}")
                    return True
            else:
                logger.info(f"Log de auditoria registrado via fallback: {event_data['id']}")
                return True
                
        except Exception as e:
            logger.error(f"Erro no mecanismo de fallback de auditoria: {e}")
            return False


class AuditService:
    """Serviço principal de auditoria"""
    
    def __init__(self):
        self.logger = AuditLogger()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extrai informações da requisição"""
        return {
            "ip_address": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "endpoint": str(request.url.path),
            "method": request.method,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers)
        }
    
    def get_user_info(self, request: Request) -> Dict[str, Any]:
        """Extrai informações do usuário da requisição"""
        return {
            "user_id": getattr(request.state, "user_id", None),
            "session_id": getattr(request.state, "session_id", None),
            "user_email": getattr(request.state, "user_email", None)
        }
    
    async def log_authentication_event(self, 
                                     request: Request,
                                     event_type: AuditEventType,
                                     user_id: Optional[str] = None,
                                     success: bool = True,
                                     error_message: Optional[str] = None,
                                     details: Optional[Dict[str, Any]] = None):
        """Registra evento de autenticação"""
        request_info = self.extract_request_info(request)
        
        event = AuditEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            severity=AuditSeverity.HIGH if not success else AuditSeverity.MEDIUM,
            user_id=user_id,
            session_id=request_info.get("session_id"),
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            endpoint=request_info["endpoint"],
            method=request_info["method"],
            resource_id=user_id,
            resource_type="user",
            action=event_type.value,
            details=details or {},
            success=success,
            error_message=error_message
        )
        
        await self.logger.log_event(event)
    
    async def log_diagnostic_event(self,
                                 request: Request,
                                 event_type: AuditEventType,
                                 diagnostic_id: Optional[str] = None,
                                 success: bool = True,
                                 error_message: Optional[str] = None,
                                 details: Optional[Dict[str, Any]] = None,
                                 duration_ms: Optional[int] = None):
        """Registra evento de diagnóstico"""
        request_info = self.extract_request_info(request)
        user_info = self.get_user_info(request)
        
        event = AuditEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            severity=AuditSeverity.MEDIUM,
            user_id=user_info["user_id"],
            session_id=user_info["session_id"],
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            endpoint=request_info["endpoint"],
            method=request_info["method"],
            resource_id=diagnostic_id,
            resource_type="diagnostic",
            action=event_type.value,
            details=details or {},
            success=success,
            error_message=error_message,
            duration_ms=duration_ms
        )
        
        await self.logger.log_event(event)
    
    async def log_security_event(self,
                               request: Request,
                               event_type: AuditEventType,
                               severity: AuditSeverity = AuditSeverity.HIGH,
                               details: Optional[Dict[str, Any]] = None,
                               error_message: Optional[str] = None):
        """Registra evento de segurança"""
        request_info = self.extract_request_info(request)
        user_info = self.get_user_info(request)
        
        event = AuditEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            severity=severity,
            user_id=user_info["user_id"],
            session_id=user_info["session_id"],
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            endpoint=request_info["endpoint"],
            method=request_info["method"],
            resource_id=None,
            resource_type="security",
            action=event_type.value,
            details=details or {},
            success=False,
            error_message=error_message
        )
        
        await self.logger.log_event(event)
    
    async def log_data_event(self,
                           request: Request,
                           event_type: AuditEventType,
                           resource_type: str,
                           resource_id: Optional[str] = None,
                           old_data: Optional[Dict[str, Any]] = None,
                           new_data: Optional[Dict[str, Any]] = None,
                           success: bool = True,
                           error_message: Optional[str] = None):
        """Registra evento de manipulação de dados"""
        request_info = self.extract_request_info(request)
        user_info = self.get_user_info(request)
        
        details = {}
        if old_data:
            details["old_data"] = old_data
        if new_data:
            details["new_data"] = new_data
        
        event = AuditEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            severity=AuditSeverity.MEDIUM,
            user_id=user_info["user_id"],
            session_id=user_info["session_id"],
            ip_address=request_info["ip_address"],
            user_agent=request_info["user_agent"],
            endpoint=request_info["endpoint"],
            method=request_info["method"],
            resource_id=resource_id,
            resource_type=resource_type,
            action=event_type.value,
            details=details,
            success=success,
            error_message=error_message
        )
        
        await self.logger.log_event(event)
    
    async def get_audit_logs(self,
                           user_id: Optional[str] = None,
                           event_type: Optional[AuditEventType] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None,
                           resource_type: Optional[str] = None,
                           success: Optional[bool] = None,
                           severity: Optional[AuditSeverity] = None,
                           limit: int = 100,
                           offset: int = 0) -> List[Dict[str, Any]]:
        """
        Recupera logs de auditoria do Supabase
        
        Args:
            user_id: Filtrar por ID de usuário
            event_type: Filtrar por tipo de evento
            start_date: Data inicial
            end_date: Data final
            resource_type: Filtrar por tipo de recurso
            success: Filtrar por status de sucesso
            severity: Filtrar por severidade
            limit: Limite de registros (máx. 100)
            offset: Deslocamento para paginação
            
        Returns:
            Lista de logs de auditoria
        """
        try:
            # Obtém cliente do Supabase
            from app.core.supabase import get_supabase_client
            supabase_client = get_supabase_client()
            
            # Prepara parâmetros para a função SQL
            params = self._prepare_audit_logs_params(
                user_id, event_type, start_date, end_date, 
                resource_type, success, severity, limit, offset
            )
            
            # Tenta usar a função SQL search_audit_logs
            try:
                logger.debug(f"Chamando função search_audit_logs com parâmetros: {params}")
                result = await supabase_client.rpc("search_audit_logs", params).execute()
                
                if hasattr(result, 'error') and result.error:
                    logger.warning(f"Erro ao usar função search_audit_logs: {result.error}. Tentando fallback.")
                    logs = await self._get_audit_logs_fallback(
                        supabase_client, user_id, event_type, start_date, end_date, 
                        resource_type, success, severity, limit, offset
                    )
                else:
                    logs = result.data if hasattr(result, 'data') else []
                    logger.debug(f"Recuperados {len(logs)} logs usando função search_audit_logs")
            except Exception as e:
                logger.warning(f"Exceção ao chamar função search_audit_logs: {e}. Tentando fallback.")
                logs = await self._get_audit_logs_fallback(
                    supabase_client, user_id, event_type, start_date, end_date, 
                    resource_type, success, severity, limit, offset
            )
            
            # Processa os logs para formato consistente
            return self._process_audit_logs(logs)
            
        except Exception as e:
            logger.error(f"Erro ao recuperar logs de auditoria: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def _prepare_audit_logs_params(
        self, user_id: Optional[str], event_type: Optional[AuditEventType], 
        start_date: Optional[datetime], end_date: Optional[datetime],
        resource_type: Optional[str], success: Optional[bool], 
        severity: Optional[AuditSeverity], limit: int, offset: int
    ) -> Dict[str, Any]:
        """Prepara parâmetros para a função search_audit_logs"""
        params = {}
        
        # Valida e converte user_id para UUID se necessário
        if user_id:
            try:
                import uuid
                uuid.UUID(user_id)
                params["p_user_id"] = user_id
            except (ValueError, TypeError):
                logger.warning(f"user_id inválido para busca de auditoria: {user_id}")
                params["p_user_id"] = None
        else:
            params["p_user_id"] = None
        
        # Converte event_type para string
        if event_type:
            if isinstance(event_type, AuditEventType):
                params["p_event_type"] = event_type.value
            else:
                params["p_event_type"] = str(event_type)
        else:
            params["p_event_type"] = None
        
        # Formata datas para ISO
        params["p_start_date"] = start_date.isoformat() if start_date else None
        params["p_end_date"] = end_date.isoformat() if end_date else None
        
        # Parâmetros restantes
        params["p_resource_type"] = resource_type
        params["p_success"] = success
        
        # Converte severity para string
        if severity:
            if isinstance(severity, AuditSeverity):
                params["p_severity"] = severity.value
            else:
                params["p_severity"] = str(severity)
        else:
            params["p_severity"] = None
        
        # Limita os resultados por questões de performance
        params["p_limit"] = min(limit, 100)
        params["p_offset"] = max(0, offset)
        
        return params
    
    async def _get_audit_logs_fallback(
        self, supabase_client, user_id: Optional[str], event_type: Optional[AuditEventType], 
        start_date: Optional[datetime], end_date: Optional[datetime],
        resource_type: Optional[str], success: Optional[bool], 
        severity: Optional[AuditSeverity], limit: int, offset: int
    ) -> List[Dict[str, Any]]:
        """Fallback para buscar logs diretamente da tabela quando a função SQL falha"""
        logger.debug("Usando fallback para busca de logs de auditoria")
        
        # Inicia a consulta selecionando todos os campos
        query = supabase_client.table("audit_logs").select("*")
        
        # Aplica filtros
        if user_id:
            try:
                import uuid
                uuid.UUID(user_id)
                query = query.eq("user_id", user_id)
            except (ValueError, TypeError):
                pass
        
        if start_date:
            query = query.gte("timestamp", start_date.isoformat())
        
        if end_date:
            query = query.lte("timestamp", end_date.isoformat())
        
        if event_type:
            event_type_str = event_type.value if isinstance(event_type, AuditEventType) else str(event_type)
            query = query.eq("event_type", event_type_str)
        
        if resource_type:
            query = query.eq("resource_type", resource_type)
        
        if success is not None:
            query = query.eq("success", success)
        
        if severity:
            severity_str = severity.value if isinstance(severity, AuditSeverity) else str(severity)
            query = query.eq("severity", severity_str)
        
        # Ordena e pagina
        query = query.order("timestamp", desc=True).limit(min(limit, 100)).offset(max(0, offset))
        
        # Executa a consulta
        try:
            result = query.execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Erro no fallback de busca de auditoria: {result.error}")
        return []
            
            return result.data if hasattr(result, 'data') else []
        except Exception as e:
            logger.error(f"Exceção no fallback de busca de auditoria: {e}")
            return []
    
    def _process_audit_logs(self, logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processa logs para formato consistente"""
        processed_logs = []
        
        for log in logs:
            try:
                # Converte timestamp para objeto datetime
                if "timestamp" in log and log["timestamp"]:
                    if isinstance(log["timestamp"], str):
                        log["timestamp"] = datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
                
                # Processa details se for string
                if "details" in log and isinstance(log["details"], str):
                    try:
                        import json
                        log["details"] = json.loads(log["details"])
                    except json.JSONDecodeError:
                        # Mantém como string se não for JSON válido
                        pass
                
                # Adiciona informações calculadas
                if "timestamp" in log and isinstance(log["timestamp"], datetime):
                    log["age_in_days"] = (datetime.now(timezone.utc) - log["timestamp"]).days
                
                processed_logs.append(log)
            except Exception as e:
                logger.warning(f"Erro ao processar log de auditoria: {e}")
                processed_logs.append(log)  # Adiciona mesmo com erro de processamento
        
        return processed_logs
            
    async def get_event_statistics(self, 
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Obtém estatísticas dos eventos de auditoria"""
        try:
            from app.db.repositories.audit_repository import audit_repository
            
            # Contagem por tipo de evento
            counts_by_type = await audit_repository.get_event_counts_by_type(
                start_date=start_date,
                end_date=end_date
            )
            
            # Contagem total de eventos
            total_events = sum(counts_by_type.values())
            
            # Contagem de eventos de segurança
            security_events = await audit_repository.count(
                filters={"resource_type": "security"}
            )
            
            # Contagem de erros
            error_events = await audit_repository.count(
                filters={"success": False}
            )
            
            return {
                "total_events": total_events,
                "events_by_type": counts_by_type,
                "security_events": security_events,
                "error_events": error_events
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas de auditoria: {e}")
            return {
                "total_events": 0,
                "events_by_type": {},
                "security_events": 0,
                "error_events": 0
            }


# Instância global do serviço de auditoria
audit_service = AuditService()


# Decorador para auditoria automática
def audit_endpoint(event_type: AuditEventType, 
                  resource_type: str = "unknown",
                  track_duration: bool = True):
    """Decorador para auditoria automática de endpoints"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            request = None
            
            # Encontra o objeto Request nos argumentos
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # Se não encontrou Request, executa função normalmente
                return await func(*args, **kwargs)
            
            start_time = time.time() if track_duration else None
            
            try:
                result = await func(*args, **kwargs)
                
                # Calcula duração
                duration_ms = None
                if start_time:
                    duration_ms = int((time.time() - start_time) * 1000)
                
                # Log de sucesso
                await audit_service.log_diagnostic_event(
                    request=request,
                    event_type=event_type,
                    success=True,
                    duration_ms=duration_ms,
                    details={"result_type": type(result).__name__}
                )
                
                return result
                
            except Exception as e:
                # Calcula duração
                duration_ms = None
                if start_time:
                    duration_ms = int((time.time() - start_time) * 1000)
                
                # Log de erro
                await audit_service.log_diagnostic_event(
                    request=request,
                    event_type=event_type,
                    success=False,
                    error_message=str(e),
                    duration_ms=duration_ms
                )
                
                raise
        
        return wrapper
    return decorator