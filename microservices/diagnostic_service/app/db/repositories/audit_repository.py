"""
Repositório específico para logs de auditoria
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
from pydantic import BaseModel
import uuid

from app.db.repositories.supabase_repository import SupabaseRepository
from app.core.audit import AuditEventType, AuditSeverity


class AuditLogModel(BaseModel):
    """Modelo Pydantic para logs de auditoria"""
    id: str
    timestamp: datetime
    event_type: str
    severity: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    action: str
    details: Dict[str, Any] = {}
    success: bool = True
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    
    class Config:
        from_attributes = True


class AuditRepository(SupabaseRepository[AuditLogModel]):
    """Repositório para operações com logs de auditoria"""
    
    def __init__(self):
        super().__init__(table_name="audit_logs", model_class=AuditLogModel)
    
    async def search_logs(self,
                         user_id: Optional[str] = None,
                         event_type: Optional[AuditEventType] = None,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         resource_type: Optional[str] = None,
                         success: Optional[bool] = None,
                         severity: Optional[AuditSeverity] = None,
                         limit: int = 100,
                         offset: int = 0) -> List[AuditLogModel]:
        """
        Busca avançada em logs de auditoria usando a função SQL otimizada
        
        Args:
            user_id: ID do usuário
            event_type: Tipo de evento
            start_date: Data inicial
            end_date: Data final
            resource_type: Tipo de recurso
            success: Status de sucesso
            severity: Nível de severidade
            limit: Limite de registros
            offset: Deslocamento para paginação
            
        Returns:
            Lista de logs de auditoria
        """
        # Prepara parâmetros para a função SQL
        params = self._prepare_search_params(
            user_id, event_type, start_date, end_date, 
            resource_type, success, severity, limit, offset
        )
        
        # Tenta usar a função SQL search_audit_logs
        try:
            result = await self.supabase_client.rpc("search_audit_logs", params).execute()
            
            if hasattr(result, 'error') and result.error:
                # Fallback para o método tradicional se a função falhar
                return await self._search_logs_fallback(
                    user_id, event_type, start_date, end_date, 
                    resource_type, success, severity, limit, offset
                )
            
            logs = result.data if hasattr(result, 'data') else []
            return [self._to_model(log) for log in logs]
            
        except Exception as e:
            # Fallback para o método tradicional
            return await self._search_logs_fallback(
                user_id, event_type, start_date, end_date, 
                resource_type, success, severity, limit, offset
            )
    
    def _prepare_search_params(
        self, user_id: Optional[str], event_type: Optional[AuditEventType], 
        start_date: Optional[datetime], end_date: Optional[datetime],
        resource_type: Optional[str], success: Optional[bool], 
        severity: Optional[AuditSeverity], limit: int, offset: int
    ) -> Dict[str, Any]:
        """Prepara parâmetros para a função search_audit_logs"""
        params = {}
        
        # Valida e converte user_id para UUID
        if user_id:
            try:
                uuid.UUID(user_id)
                params["p_user_id"] = user_id
            except (ValueError, TypeError):
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
    
    async def _search_logs_fallback(self,
                               user_id: Optional[str] = None,
                               event_type: Optional[AuditEventType] = None,
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None,
                               resource_type: Optional[str] = None,
                               success: Optional[bool] = None,
                               severity: Optional[AuditSeverity] = None,
                               limit: int = 100,
                               offset: int = 0) -> List[AuditLogModel]:
        """Fallback para quando a função SQL search_audit_logs falha"""
        filters = {}
        
        if user_id:
            try:
                uuid.UUID(user_id)
                filters["user_id"] = user_id
            except (ValueError, TypeError):
                pass
        
        if event_type:
            if isinstance(event_type, AuditEventType):
                filters["event_type"] = event_type.value
            else:
                filters["event_type"] = event_type
        
        if resource_type:
            filters["resource_type"] = resource_type
            
        if success is not None:
            filters["success"] = success
            
        if severity:
            if isinstance(severity, AuditSeverity):
                filters["severity"] = severity.value
            else:
                filters["severity"] = severity
        
        # Datas precisam ser tratadas de forma especial
        query = self.supabase_client.table(self.table_name).select("*")
        
        # Aplica filtros
        for field, value in filters.items():
            query = query.eq(field, value)
        
        # Filtros de data
        if start_date:
            query = query.gte("timestamp", start_date.isoformat())
        
        if end_date:
            query = query.lte("timestamp", end_date.isoformat())
        
        # Ordenação e paginação
        query = query.order("timestamp", desc=True).range(offset, offset + limit - 1)
        
        # Executa consulta
        try:
            result = query.execute()
            
            if hasattr(result, 'error') and result.error:
                return []
            
            logs = result.data if hasattr(result, 'data') else []
            
            return [self._to_model(log) for log in logs]
        except Exception as e:
            return []

    async def get_events_by_timeframe(self, 
                                  timeframe: str = "daily",
                                  days: int = 30) -> Dict[str, int]:
        """
        Obtém contagem de eventos agrupados por período de tempo
        
        Args:
            timeframe: Período de agrupamento (daily, weekly, monthly)
            days: Número de dias para analisar
            
        Returns:
            Dicionário com contagem por período
        """
        time_format = ""
        if timeframe == "daily":
            time_format = "YYYY-MM-DD"
        elif timeframe == "weekly":
            time_format = "YYYY-WW"
        elif timeframe == "monthly":
            time_format = "YYYY-MM"
        else:
            time_format = "YYYY-MM-DD"
        
        sql_query = f"""
        SELECT 
            to_char(timestamp, '{time_format}') as time_period,
            COUNT(*) as count
        FROM audit_logs
        WHERE timestamp >= NOW() - INTERVAL '{days} days'
        GROUP BY time_period
        ORDER BY time_period ASC
        """
        
        try:
            results = await self.execute_raw_query(sql_query)
            
            # Converte resultado para o formato esperado
            counts = {}
            for item in results:
                if "time_period" in item and "count" in item:
                    counts[item["time_period"]] = item["count"]
            
            return counts
        except Exception as e:
            return {}
    
    async def get_audit_summary(self) -> Dict[str, Any]:
        """
        Obtém um resumo estatístico dos logs de auditoria
        
        Returns:
            Dicionário com estatísticas resumidas
        """
        sql_query = """
        SELECT 
            COUNT(*) as total_events,
            COUNT(CASE WHEN event_type LIKE 'security.%' THEN 1 END) as security_events,
            COUNT(CASE WHEN success = false THEN 1 END) as failed_events,
            COUNT(CASE WHEN severity = 'high' OR severity = 'critical' THEN 1 END) as high_severity_events,
            MIN(timestamp) as oldest_event,
            MAX(timestamp) as newest_event,
            COUNT(DISTINCT user_id) as unique_users,
            COUNT(DISTINCT ip_address) as unique_ips
        FROM audit_logs
        WHERE timestamp >= NOW() - INTERVAL '30 days'
        """
        
        try:
            results = await self.execute_raw_query(sql_query)
            
            if not results or len(results) == 0:
                return {
                    "total_events": 0,
                    "security_events": 0,
                    "failed_events": 0,
                    "high_severity_events": 0,
                    "unique_users": 0,
                    "unique_ips": 0
                }
            
            return results[0]
        except Exception as e:
            return {
                "total_events": 0,
                "security_events": 0,
                "failed_events": 0,
                "high_severity_events": 0,
                "unique_users": 0,
                "unique_ips": 0,
                "error": str(e)
            }

    async def get_event_counts_by_type(self, 
                                     start_date: Optional[datetime] = None,
                                     end_date: Optional[datetime] = None) -> Dict[str, int]:
        """
        Obtém contagem de eventos por tipo
        
        Args:
            start_date: Data inicial
            end_date: Data final
            
        Returns:
            Dicionário com contagem por tipo de evento
        """
        sql_query = """
        SELECT event_type, COUNT(*) as count
        FROM audit_logs
        WHERE 1=1
        """
        
        params = {}
        
        if start_date:
            sql_query += " AND timestamp >= :start_date"
            params["start_date"] = start_date.isoformat()
        
        if end_date:
            sql_query += " AND timestamp <= :end_date"
            params["end_date"] = end_date.isoformat()
        
        sql_query += " GROUP BY event_type ORDER BY count DESC"
        
        try:
            results = await self.execute_raw_query(sql_query, params)
            
            # Converte resultado para o formato esperado
            counts = {}
            for item in results:
                if "event_type" in item and "count" in item:
                    counts[item["event_type"]] = item["count"]
            
            return counts
        except Exception as e:
            return {}
    
    async def get_security_events(self, 
                               limit: int = 100,
                               offset: int = 0) -> List[AuditLogModel]:
        """
        Obtém eventos de segurança (para monitoramento)
        
        Args:
            limit: Limite de registros
            offset: Deslocamento para paginação
            
        Returns:
            Lista de eventos de segurança
        """
        # Filtra eventos de segurança (começam com "security.")
        filters = {
            "resource_type": "security"
        }
        
        return await self.list(
            filters=filters,
            limit=limit,
            offset=offset,
            order_by="timestamp",
            order_desc=True
        )


# Instância global do repositório
audit_repository = AuditRepository() 