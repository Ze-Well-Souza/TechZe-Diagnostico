"""
Repository para operações com orçamentos no Supabase
Especializado em operações complexas de orçamentos
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import logging

from app.db.repositories.supabase_repository import SupabaseRepository
from app.models.orcamento import Orcamento, OrcamentoFiltros
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class OrcamentoRepository(SupabaseRepository[Orcamento]):
    """Repository especializado para orçamentos"""
    
    def __init__(self):
        super().__init__(table_name="orcamentos", model_class=Orcamento)
    
    async def gerar_proximo_numero(self) -> str:
        """
        Gera o próximo número de orçamento
        Formato: ORC-YYYYMM-NNNN
        
        Returns:
            Próximo número de orçamento
        """
        try:
            agora = datetime.now()
            prefixo = f"ORC-{agora.strftime('%Y%m')}-"
            
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
            logger.error(f"Erro ao gerar número do orçamento: {e}")
            # Fallback: timestamp
            return f"ORC-{agora.strftime('%Y%m%d%H%M%S')}"
    
    async def buscar_por_numero(self, numero: str) -> Optional[Orcamento]:
        """
        Busca orçamento por número
        
        Args:
            numero: Número do orçamento
            
        Returns:
            Orçamento encontrado ou None
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
            logger.error(f"Erro ao buscar orçamento por número: {e}")
            return None
    
    async def buscar_por_cliente(self, cliente_id: str, 
                                limite: int = 10) -> List[Orcamento]:
        """
        Busca orçamentos de um cliente
        
        Args:
            cliente_id: ID do cliente
            limite: Número máximo de orçamentos
            
        Returns:
            Lista de orçamentos do cliente
        """
        try:
            result = self.supabase_client.table(self.table_name)\
                .select("*")\
                .eq("cliente_id", cliente_id)\
                .order("created_at", desc=True)\
                .limit(limite)\
                .execute()
            
            return [self._to_model(item) for item in result.data]
        except Exception as e:
            logger.error(f"Erro ao buscar orçamentos do cliente: {e}")
            return []
    
    async def listar_com_filtros(self, filtros: OrcamentoFiltros) -> List[Orcamento]:
        """
        Lista orçamentos com filtros específicos
        
        Args:
            filtros: Filtros de busca
            
        Returns:
            Lista de orçamentos filtrados
        """
        try:
            query = self.supabase_client.table(self.table_name).select("*")
            
            # Aplica filtros
            if filtros.cliente_id:
                query = query.eq("cliente_id", filtros.cliente_id)
            
            if filtros.status:
                query = query.eq("status", filtros.status.value)
            
            if filtros.data_inicio:
                query = query.gte("created_at", filtros.data_inicio.isoformat())
            
            if filtros.data_fim:
                query = query.lte("created_at", filtros.data_fim.isoformat())
            
            if filtros.valor_minimo:
                query = query.gte("valor_total", float(filtros.valor_minimo))
            
            if filtros.valor_maximo:
                query = query.lte("valor_total", float(filtros.valor_maximo))
            
            if filtros.prioridade:
                query = query.eq("prioridade", filtros.prioridade.value)
            
            # Ordenação
            if filtros.ordenar_por:
                query = query.order(filtros.ordenar_por, desc=filtros.ordem_desc)
            else:
                query = query.order("created_at", desc=True)
            
            # Paginação
            if filtros.limite:
                offset = (filtros.pagina - 1) * filtros.limite if filtros.pagina > 1 else 0
                query = query.range(offset, offset + filtros.limite - 1)
            
            result = query.execute()
            return [self._to_model(item) for item in result.data]
        except Exception as e:
            logger.error(f"Erro ao listar orçamentos com filtros: {e}")
            return []
    
    async def aprovar_orcamento(self, orcamento_id: str, 
                              assinatura_digital: str,
                              ip_aprovacao: str) -> bool:
        """
        Aprova um orçamento
        
        Args:
            orcamento_id: ID do orçamento
            assinatura_digital: Assinatura digital
            ip_aprovacao: IP de onde veio a aprovação
            
        Returns:
            True se aprovado com sucesso
        """
        try:
            agora = datetime.now()
            
            result = self.supabase_client.table(self.table_name)\
                .update({
                    "status": "aprovado",
                    "data_aprovacao": agora.isoformat(),
                    "assinatura_digital": assinatura_digital,
                    "ip_aprovacao": ip_aprovacao,
                    "updated_at": agora.isoformat()
                })\
                .eq("id", orcamento_id)\
                .execute()
            
            return not (hasattr(result, 'error') and result.error)
        except Exception as e:
            logger.error(f"Erro ao aprovar orçamento: {e}")
            return False
    
    async def rejeitar_orcamento(self, orcamento_id: str) -> bool:
        """
        Rejeita um orçamento
        
        Args:
            orcamento_id: ID do orçamento
            
        Returns:
            True se rejeitado com sucesso
        """
        try:
            agora = datetime.now()
            
            result = self.supabase_client.table(self.table_name)\
                .update({
                    "status": "rejeitado",
                    "updated_at": agora.isoformat()
                })\
                .eq("id", orcamento_id)\
                .execute()
            
            return not (hasattr(result, 'error') and result.error)
        except Exception as e:
            logger.error(f"Erro ao rejeitar orçamento: {e}")
            return False
    
    async def buscar_vencidos(self) -> List[Orcamento]:
        """
        Busca orçamentos vencidos
        
        Returns:
            Lista de orçamentos vencidos
        """
        try:
            hoje = date.today()
            
            result = self.supabase_client.table(self.table_name)\
                .select("*")\
                .eq("status", "pendente")\
                .lt("data_validade", hoje.isoformat())\
                .execute()
            
            return [self._to_model(item) for item in result.data]
        except Exception as e:
            logger.error(f"Erro ao buscar orçamentos vencidos: {e}")
            return []
    
    async def marcar_como_vencidos(self) -> int:
        """
        Marca orçamentos pendentes como vencidos
        
        Returns:
            Número de orçamentos marcados como vencidos
        """
        try:
            hoje = date.today()
            agora = datetime.now()
            
            result = self.supabase_client.table(self.table_name)\
                .update({
                    "status": "vencido",
                    "updated_at": agora.isoformat()
                })\
                .eq("status", "pendente")\
                .lt("data_validade", hoje.isoformat())\
                .execute()
            
            return len(result.data) if result.data else 0
        except Exception as e:
            logger.error(f"Erro ao marcar orçamentos como vencidos: {e}")
            return 0
    
    async def buscar_com_itens_e_pecas(self, orcamento_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca orçamento completo com itens e peças
        
        Args:
            orcamento_id: ID do orçamento
            
        Returns:
            Orçamento completo com itens e peças
        """
        try:
            # Busca orçamento principal
            orcamento = await self.get_by_id(orcamento_id)
            if not orcamento:
                return None
            
            # Busca itens
            itens_result = self.supabase_client.table("orcamento_itens")\
                .select("*")\
                .eq("orcamento_id", orcamento_id)\
                .execute()
            
            # Busca peças
            pecas_result = self.supabase_client.table("orcamento_pecas")\
                .select("*")\
                .eq("orcamento_id", orcamento_id)\
                .execute()
            
            return {
                "orcamento": orcamento.dict(),
                "itens": itens_result.data if itens_result.data else [],
                "pecas": pecas_result.data if pecas_result.data else []
            }
        except Exception as e:
            logger.error(f"Erro ao buscar orçamento completo: {e}")
            return None
    
    async def estatisticas_periodo(self, data_inicio: date, 
                                 data_fim: date) -> Dict[str, Any]:
        """
        Gera estatísticas de orçamentos para um período
        
        Args:
            data_inicio: Data de início
            data_fim: Data de fim
            
        Returns:
            Estatísticas do período
        """
        try:
            # Busca orçamentos do período
            result = self.supabase_client.table(self.table_name)\
                .select("status, valor_total, created_at")\
                .gte("created_at", data_inicio.isoformat())\
                .lte("created_at", data_fim.isoformat())\
                .execute()
            
            if not result.data:
                return {
                    "total_orcamentos": 0,
                    "valor_total": 0,
                    "aprovados": 0,
                    "pendentes": 0,
                    "rejeitados": 0,
                    "vencidos": 0,
                    "taxa_aprovacao": 0
                }
            
            # Calcula estatísticas
            total = len(result.data)
            aprovados = len([o for o in result.data if o["status"] == "aprovado"])
            pendentes = len([o for o in result.data if o["status"] == "pendente"])
            rejeitados = len([o for o in result.data if o["status"] == "rejeitado"])
            vencidos = len([o for o in result.data if o["status"] == "vencido"])
            valor_total = sum(float(o["valor_total"]) for o in result.data)
            taxa_aprovacao = (aprovados / total * 100) if total > 0 else 0
            
            return {
                "total_orcamentos": total,
                "valor_total": valor_total,
                "aprovados": aprovados,
                "pendentes": pendentes,
                "rejeitados": rejeitados,
                "vencidos": vencidos,
                "taxa_aprovacao": round(taxa_aprovacao, 2)
            }
        except Exception as e:
            logger.error(f"Erro ao gerar estatísticas: {e}")
            return {} 