import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple, Union
from uuid import UUID

from app.core.supabase import get_supabase_client
from app.schemas.diagnostic import DiagnosticCreate, DiagnosticUpdate, DiagnosticInDB
from app.models.diagnostic import DiagnosticStatus

logger = logging.getLogger(__name__)


class SupabaseDiagnosticService:
    """Serviço para gerenciar diagnósticos de sistema usando Supabase."""
    
    def __init__(self):
        """Inicializa o serviço de diagnóstico com Supabase."""
        self.supabase = get_supabase_client()
    
    async def create_diagnostic(self, obj_in: DiagnosticCreate, user_id: str) -> Dict[str, Any]:
        """Cria um novo diagnóstico.
        
        Args:
            obj_in: Dados para criação do diagnóstico
            user_id: ID do usuário autenticado
            
        Returns:
            Dados do diagnóstico criado
        """
        try:
            # Preparar dados para inserção
            data = {
                "user_id": user_id,
                "device_id": obj_in.device_id,
                "status": DiagnosticStatus.PENDING.value,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Inserir no Supabase
            result = self.supabase.table("diagnostics").insert(data).execute()
            
            if not result.data:
                logger.error("Falha ao criar diagnóstico no Supabase")
                return None
                
            logger.info(f"Diagnóstico criado com ID: {result.data[0]['id']}")
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Erro ao criar diagnóstico: {e}")
            raise
    
    async def get_diagnostic(self, diagnostic_id: Union[str, UUID], user_id: str) -> Dict[str, Any]:
        """Obtém um diagnóstico específico.
        
        Args:
            diagnostic_id: ID do diagnóstico
            user_id: ID do usuário autenticado
            
        Returns:
            Dados do diagnóstico ou None se não encontrado
        """
        try:
            # Converter UUID para string se necessário
            if isinstance(diagnostic_id, UUID):
                diagnostic_id = str(diagnostic_id)
            
            # Buscar no Supabase
            result = self.supabase.table("diagnostics") \
                .select("*") \
                .eq("id", diagnostic_id) \
                .eq("user_id", user_id) \
                .execute()
            
            if not result.data:
                logger.warning(f"Diagnóstico não encontrado: {diagnostic_id}")
                return None
                
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Erro ao buscar diagnóstico {diagnostic_id}: {e}")
            raise
    
    async def get_user_diagnostics(self, user_id: str, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Obtém todos os diagnósticos de um usuário.
        
        Args:
            user_id: ID do usuário
            limit: Número máximo de registros
            offset: Deslocamento para paginação
            
        Returns:
            Lista de diagnósticos
        """
        try:
            result = self.supabase.table("diagnostics") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .range(offset, offset + limit - 1) \
                .execute()
            
            return result.data
            
        except Exception as e:
            logger.error(f"Erro ao buscar diagnósticos do usuário {user_id}: {e}")
            raise
    
    async def update_diagnostic(self, diagnostic_id: Union[str, UUID], obj_in: DiagnosticUpdate, user_id: str) -> Dict[str, Any]:
        """Atualiza um diagnóstico existente.
        
        Args:
            diagnostic_id: ID do diagnóstico
            obj_in: Dados para atualização
            user_id: ID do usuário autenticado
            
        Returns:
            Dados do diagnóstico atualizado ou None se não encontrado
        """
        try:
            # Converter UUID para string se necessário
            if isinstance(diagnostic_id, UUID):
                diagnostic_id = str(diagnostic_id)
            
            # Preparar dados para atualização
            update_data = obj_in.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.now().isoformat()
            
            # Atualizar no Supabase
            result = self.supabase.table("diagnostics") \
                .update(update_data) \
                .eq("id", diagnostic_id) \
                .eq("user_id", user_id) \
                .execute()
            
            if not result.data:
                logger.warning(f"Diagnóstico não encontrado ou não pertence ao usuário: {diagnostic_id}")
                return None
                
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Erro ao atualizar diagnóstico {diagnostic_id}: {e}")
            raise
    
    async def delete_diagnostic(self, diagnostic_id: Union[str, UUID], user_id: str) -> bool:
        """Exclui um diagnóstico.
        
        Args:
            diagnostic_id: ID do diagnóstico
            user_id: ID do usuário autenticado
            
        Returns:
            True se excluído com sucesso, False caso contrário
        """
        try:
            # Converter UUID para string se necessário
            if isinstance(diagnostic_id, UUID):
                diagnostic_id = str(diagnostic_id)
            
            # Excluir do Supabase
            result = self.supabase.table("diagnostics") \
                .delete() \
                .eq("id", diagnostic_id) \
                .eq("user_id", user_id) \
                .execute()
            
            # Verificar se algo foi excluído
            return len(result.data) > 0
            
        except Exception as e:
            logger.error(f"Erro ao excluir diagnóstico {diagnostic_id}: {e}")
            raise
    
    async def run_diagnostic(self, diagnostic_id: Union[str, UUID], user_id: str) -> Dict[str, Any]:
        """Executa um diagnóstico completo.
        
        Args:
            diagnostic_id: ID do diagnóstico
            user_id: ID do usuário autenticado
            
        Returns:
            Resultado do diagnóstico
        """
        try:
            # Atualizar status para EM ANDAMENTO
            await self.update_diagnostic(
                diagnostic_id,
                DiagnosticUpdate(status=DiagnosticStatus.RUNNING),
                user_id
            )
            
            start_time = time.time()
            
            # TODO: Implementar os analisadores reais
            # Por enquanto, vamos simular os resultados
            cpu_result = {"usage": 45.5, "temperature": 65.2, "cores": 8, "status": "healthy"}
            memory_result = {"total": 16.0, "used": 8.5, "available": 7.5, "status": "healthy"}
            disk_result = {"total": 512.0, "used": 350.0, "available": 162.0, "status": "warning"}
            network_result = {"download": 95.5, "upload": 35.2, "latency": 25, "status": "healthy"}
            
            # Calcular score de saúde
            health_score = self._calculate_health_score(cpu_result, memory_result, disk_result, network_result)
            
            # Preparar dados para atualização
            diagnostic_update = DiagnosticUpdate(
                status=DiagnosticStatus.COMPLETED,
                cpu_status=cpu_result["status"],
                cpu_metrics=cpu_result,
                memory_status=memory_result["status"],
                memory_metrics=memory_result,
                disk_status=disk_result["status"],
                disk_metrics=disk_result,
                network_status=network_result["status"],
                network_metrics=network_result,
                health_score=health_score,
                raw_data={
                    "cpu": cpu_result,
                    "memory": memory_result,
                    "disk": disk_result,
                    "network": network_result
                },
                execution_time=time.time() - start_time
            )
            
            # Atualizar diagnóstico com resultados
            result = await self.update_diagnostic(diagnostic_id, diagnostic_update, user_id)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao executar diagnóstico {diagnostic_id}: {e}")
            
            # Atualizar status para ERRO
            await self.update_diagnostic(
                diagnostic_id,
                DiagnosticUpdate(
                    status=DiagnosticStatus.ERROR,
                    error_message=str(e)
                ),
                user_id
            )
            
            raise
    
    def _calculate_health_score(self, cpu_data: Dict[str, Any], memory_data: Dict[str, Any], 
                              disk_data: Dict[str, Any], network_data: Dict[str, Any]) -> float:
        """Calcula o score de saúde do sistema.
        
        Args:
            cpu_data: Dados da CPU
            memory_data: Dados da memória
            disk_data: Dados do disco
            network_data: Dados da rede
            
        Returns:
            Score de saúde (0-100)
        """
        # Pesos para cada componente
        weights = {"cpu": 0.3, "memory": 0.25, "disk": 0.25, "network": 0.2}
        
        # Calcular scores individuais (simplificado)
        cpu_score = 100 - min(cpu_data["usage"], 100)
        memory_score = 100 * (memory_data["available"] / (memory_data["total"] or 1))
        
        # Para disco, quanto mais espaço livre melhor
        disk_free_percent = 100 * (disk_data["available"] / (disk_data["total"] or 1))
        disk_score = disk_free_percent
        
        # Para rede, baixa latência é melhor (assumindo latência máxima de 200ms)
        network_score = 100 - min(network_data["latency"] / 2, 100)
        
        # Calcular score ponderado
        health_score = (
            weights["cpu"] * cpu_score +
            weights["memory"] * memory_score +
            weights["disk"] * disk_score +
            weights["network"] * network_score
        )
        
        return round(health_score, 1)