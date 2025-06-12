"""
Repository para operações com ordens de serviço no Supabase
Especializado em workflow e controle de ordens de serviço
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import logging

from app.db.repositories.supabase_repository import SupabaseRepository
from app.models.ordem_servico import OrdemServico, OSFiltros, StatusOS
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class OrdemServicoRepository(SupabaseRepository[OrdemServico]):
    """Repository especializado para ordens de serviço"""
    
    def __init__(self):
        super().__init__(table_name="ordens_servico", model_class=OrdemServico)
    
    async def gerar_proximo_numero(self) -> str:
        """
        Gera o próximo número de ordem de serviço
        Formato: OS-YYYYMM-NNNN
        
        Returns:
            Próximo número de OS
        """
        try:
            agora = datetime.now()
            prefixo = f"OS-{agora.strftime('%Y%m')}-"
            
            # Busca o último número do mês
            result = self.supabase_client.table(self.table_name)\
                .select("numero")\
                .like("numero", f"{prefixo}%")\
                .order("numero", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                ultimo_numero = result.data[0]["numero"]
                # Extrai o número sequencial
                sequencial = int(ultimo_numero.split("-")[-1]) + 1
            else:
                sequencial = 1
            
            return f"{prefixo}{sequencial:04d}"
        except Exception as e:
            logger.error(f"Erro ao gerar número da OS: {e}")
            # Fallback: timestamp
            return f"OS-{agora.strftime('%Y%m%d%H%M%S')}"
    
    async def buscar_por_numero(self, numero: str) -> Optional[OrdemServico]:
        """
        Busca OS por número
        
        Args:
            numero: Número da OS
            
        Returns:
            OS encontrada ou None
        """
        try:
            result = self.supabase_client.table(self.table_name)\
                .select("*")\
                .eq("numero", numero)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return self._to_model(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar OS por número: {e}")
            return None
    
    async def listar_com_filtros(self, filtros: OSFiltros) -> List[OrdemServico]:
        """
        Lista OS com filtros específicos
        
        Args:
            filtros: Filtros de busca
            
        Returns:
            Lista de OS filtradas
        """
        try:
            query = self.supabase_client.table(self.table_name).select("*")
            
            # Aplica filtros
            if filtros.cliente_id:
                query = query.eq("cliente_id", filtros.cliente_id)
            
            if filtros.tecnico_id:
                query = query.eq("tecnico_id", filtros.tecnico_id)
            
            if filtros.status:
                query = query.eq("status", filtros.status.value)
            
            if filtros.prioridade:
                query = query.eq("prioridade", filtros.prioridade.value)
            
            if filtros.data_inicio:
                query = query.gte("data_entrada", filtros.data_inicio.isoformat())
            
            if filtros.data_fim:
                query = query.lte("data_entrada", filtros.data_fim.isoformat())
            
            if filtros.numero:
                query = query.ilike("numero", f"%{filtros.numero}%")
            
            # Ordenação
            if filtros.ordenar_por:
                query = query.order(filtros.ordenar_por, desc=filtros.ordem_desc)
            else:
                query = query.order("data_entrada", desc=True)
            
            # Paginação
            if filtros.limite:
                offset = (filtros.pagina - 1) * filtros.limite if filtros.pagina > 1 else 0
                query = query.range(offset, offset + filtros.limite - 1)
            
            result = query.execute()
            return [self._to_model(item) for item in result.data]
        except Exception as e:
            logger.error(f"Erro ao listar OS com filtros: {e}")
            return []
    
    async def buscar_por_cliente(self, cliente_id: str, 
                               limite: int = 10) -> List[OrdemServico]:
        """
        Busca OS de um cliente
        
        Args:
            cliente_id: ID do cliente
            limite: Número máximo de OS
            
        Returns:
            Lista de OS do cliente
        """
        try:
            result = self.supabase_client.table(self.table_name)\
                .select("*")\
                .eq("cliente_id", cliente_id)\
                .order("data_entrada", desc=True)\
                .limit(limite)\
                .execute()
            
            return [self._to_model(item) for item in result.data]
        except Exception as e:
            logger.error(f"Erro ao buscar OS do cliente: {e}")
            return []
    
    async def buscar_por_tecnico(self, tecnico_id: str, 
                               apenas_ativas: bool = True) -> List[OrdemServico]:
        """
        Busca OS de um técnico
        
        Args:
            tecnico_id: ID do técnico
            apenas_ativas: Se deve buscar apenas OS ativas
            
        Returns:
            Lista de OS do técnico
        """
        try:
            query = self.supabase_client.table(self.table_name)\
                .select("*")\
                .eq("tecnico_id", tecnico_id)
            
            if apenas_ativas:
                # Status que indicam OS ativa
                status_ativas = ["nova", "em_andamento", "aguardando_peca", "aguardando_cliente"]
                query = query.in_("status", status_ativas)
            
            query = query.order("data_entrada", desc=True)
            result = query.execute()
            
            return [self._to_model(item) for item in result.data]
        except Exception as e:
            logger.error(f"Erro ao buscar OS do técnico: {e}")
            return []
    
    async def atualizar_status(self, os_id: str, novo_status: StatusOS, 
                             observacao: str = None) -> bool:
        """
        Atualiza status de uma OS
        
        Args:
            os_id: ID da OS
            novo_status: Novo status
            observacao: Observação sobre a mudança
            
        Returns:
            True se atualização foi realizada
        """
        try:
            agora = datetime.now()
            dados_atualizacao = {
                "status": novo_status.value,
                "updated_at": agora.isoformat()
            }
            
            # Define campos específicos baseado no status
            if novo_status == StatusOS.EM_ANDAMENTO:
                dados_atualizacao["data_inicio"] = agora.isoformat()
            elif novo_status == StatusOS.FINALIZADA:
                dados_atualizacao["data_conclusao"] = agora.isoformat()
            
            # Atualiza OS
            result = self.supabase_client.table(self.table_name)\
                .update(dados_atualizacao)\
                .eq("id", os_id)\
                .execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Erro ao atualizar status da OS: {result.error}")
                return False
            
            # Registra anotação se fornecida
            if observacao:
                await self.adicionar_anotacao(os_id, "sistema", "observacao", observacao)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao atualizar status da OS: {e}")
            return False
    
    async def atribuir_tecnico(self, os_id: str, tecnico_id: str) -> bool:
        """
        Atribui técnico a uma OS
        
        Args:
            os_id: ID da OS
            tecnico_id: ID do técnico
            
        Returns:
            True se atribuição foi realizada
        """
        try:
            result = self.supabase_client.table(self.table_name)\
                .update({
                    "tecnico_id": tecnico_id,
                    "updated_at": datetime.now().isoformat()
                })\
                .eq("id", os_id)\
                .execute()
            
            return not (hasattr(result, 'error') and result.error)
        except Exception as e:
            logger.error(f"Erro ao atribuir técnico: {e}")
            return False
    
    async def adicionar_anotacao(self, os_id: str, usuario_id: str, 
                               tipo: str, conteudo: str, 
                               is_private: bool = False) -> bool:
        """
        Adiciona anotação a uma OS
        
        Args:
            os_id: ID da OS
            usuario_id: ID do usuário
            tipo: Tipo da anotação
            conteudo: Conteúdo da anotação
            is_private: Se é anotação privada
            
        Returns:
            True se anotação foi adicionada
        """
        try:
            anotacao_data = {
                "ordem_servico_id": os_id,
                "usuario_id": usuario_id,
                "tipo": tipo,
                "conteudo": conteudo,
                "is_private": is_private,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase_client.table("os_anotacoes")\
                .insert(anotacao_data)\
                .execute()
            
            return not (hasattr(result, 'error') and result.error)
        except Exception as e:
            logger.error(f"Erro ao adicionar anotação: {e}")
            return False
    
    async def buscar_anotacoes(self, os_id: str, 
                             incluir_privadas: bool = False) -> List[Dict[str, Any]]:
        """
        Busca anotações de uma OS
        
        Args:
            os_id: ID da OS
            incluir_privadas: Se deve incluir anotações privadas
            
        Returns:
            Lista de anotações
        """
        try:
            query = self.supabase_client.table("os_anotacoes")\
                .select("*")\
                .eq("ordem_servico_id", os_id)
            
            if not incluir_privadas:
                query = query.eq("is_private", False)
            
            query = query.order("created_at")
            result = query.execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Erro ao buscar anotações: {e}")
            return []
    
    async def adicionar_foto(self, os_id: str, url: str, 
                           descricao: str = None, tipo: str = "geral") -> bool:
        """
        Adiciona foto a uma OS
        
        Args:
            os_id: ID da OS
            url: URL da foto
            descricao: Descrição da foto
            tipo: Tipo da foto
            
        Returns:
            True se foto foi adicionada
        """
        try:
            foto_data = {
                "ordem_servico_id": os_id,
                "url": url,
                "descricao": descricao,
                "tipo": tipo,
                "created_at": datetime.now().isoformat()
            }
            
            result = self.supabase_client.table("os_fotos")\
                .insert(foto_data)\
                .execute()
            
            return not (hasattr(result, 'error') and result.error)
        except Exception as e:
            logger.error(f"Erro ao adicionar foto: {e}")
            return False
    
    async def buscar_fotos(self, os_id: str) -> List[Dict[str, Any]]:
        """
        Busca fotos de uma OS
        
        Args:
            os_id: ID da OS
            
        Returns:
            Lista de fotos
        """
        try:
            result = self.supabase_client.table("os_fotos")\
                .select("*")\
                .eq("ordem_servico_id", os_id)\
                .order("created_at")\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Erro ao buscar fotos: {e}")
            return []
    
    async def buscar_com_detalhes(self, os_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca OS completa com detalhes (serviços, peças, anotações, fotos)
        
        Args:
            os_id: ID da OS
            
        Returns:
            OS completa com detalhes
        """
        try:
            # Busca OS principal
            os = await self.get_by_id(os_id)
            if not os:
                return None
            
            # Busca serviços
            servicos_result = self.supabase_client.table("os_servicos")\
                .select("*")\
                .eq("ordem_servico_id", os_id)\
                .execute()
            
            # Busca peças
            pecas_result = self.supabase_client.table("os_pecas")\
                .select("*")\
                .eq("ordem_servico_id", os_id)\
                .execute()
            
            # Busca anotações
            anotacoes = await self.buscar_anotacoes(os_id, incluir_privadas=True)
            
            # Busca fotos
            fotos = await self.buscar_fotos(os_id)
            
            return {
                "ordem_servico": os.model_dump(),
                "servicos": servicos_result.data if servicos_result.data else [],
                "pecas": pecas_result.data if pecas_result.data else [],
                "anotacoes": anotacoes,
                "fotos": fotos
            }
        except Exception as e:
            logger.error(f"Erro ao buscar OS completa: {e}")
            return None
    
    async def estatisticas_tecnico(self, tecnico_id: str, 
                                 data_inicio: date = None,
                                 data_fim: date = None) -> Dict[str, Any]:
        """
        Gera estatísticas de um técnico
        
        Args:
            tecnico_id: ID do técnico
            data_inicio: Data de início (opcional)
            data_fim: Data de fim (opcional)
            
        Returns:
            Estatísticas do técnico
        """
        try:
            query = self.supabase_client.table(self.table_name)\
                .select("*")\
                .eq("tecnico_id", tecnico_id)
            
            if data_inicio:
                query = query.gte("data_entrada", data_inicio.isoformat())
            
            if data_fim:
                query = query.lte("data_entrada", data_fim.isoformat())
            
            result = query.execute()
            os_list = result.data if result.data else []
            
            # Calcula estatísticas
            total_os = len(os_list)
            finalizadas = len([os for os in os_list if os["status"] == "finalizada"])
            em_andamento = len([os for os in os_list if os["status"] == "em_andamento"])
            valor_total = sum(float(os["valor_total"]) for os in os_list if os["valor_total"])
            
            # Tempo médio de conclusão (apenas OS finalizadas)
            os_finalizadas = [os for os in os_list if os["status"] == "finalizada" and os["data_conclusao"]]
            tempo_medio = 0
            if os_finalizadas:
                tempos = []
                for os in os_finalizadas:
                    entrada = datetime.fromisoformat(os["data_entrada"].replace('Z', '+00:00'))
                    conclusao = datetime.fromisoformat(os["data_conclusao"].replace('Z', '+00:00'))
                    tempos.append((conclusao - entrada).total_seconds() / 3600)  # em horas
                tempo_medio = sum(tempos) / len(tempos)
            
            return {
                "total_os": total_os,
                "finalizadas": finalizadas,
                "em_andamento": em_andamento,
                "valor_total": valor_total,
                "tempo_medio_conclusao": round(tempo_medio, 2),
                "taxa_conclusao": round((finalizadas / total_os * 100) if total_os > 0 else 0, 2)
            }
        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas do técnico: {e}")
            return {}
    
    async def os_em_atraso(self) -> List[OrdemServico]:
        """
        Busca OS em atraso (com prazo vencido)
        
        Returns:
            Lista de OS em atraso
        """
        try:
            # Por simplicidade, considera OS em atraso as que estão há mais de 7 dias
            # sem atualização e não estão finalizadas
            data_limite = datetime.now() - datetime.timedelta(days=7)
            
            result = self.supabase_client.table(self.table_name)\
                .select("*")\
                .not_.in_("status", ["finalizada", "cancelada"])\
                .lt("updated_at", data_limite.isoformat())\
                .order("updated_at")\
                .execute()
            
            return [self._to_model(item) for item in result.data]
        except Exception as e:
            logger.error(f"Erro ao buscar OS em atraso: {e}")
            return [] 