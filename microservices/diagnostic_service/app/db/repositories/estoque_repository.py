"""
Repository para operações com estoque no Supabase
Especializado em controle de estoque e movimentações
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, date
import logging
from decimal import Decimal

from app.db.repositories.supabase_repository import SupabaseRepository
from app.models.estoque import ItemEstoque, MovimentacaoEstoque, EstoqueFiltros, TipoMovimentacao
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)


class EstoqueRepository(SupabaseRepository[ItemEstoque]):
    """Repository especializado para controle de estoque"""
    
    def __init__(self):
        super().__init__(table_name="estoque_itens", model_class=ItemEstoque)
    
    async def buscar_por_codigo(self, codigo: str) -> Optional[ItemEstoque]:
        """
        Busca item por código
        
        Args:
            codigo: Código do item
            
        Returns:
            Item encontrado ou None
        """
        try:
            result = self.supabase_client.table(self.table_name)\
                .select("*")\
                .eq("codigo", codigo)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return self._to_model(result.data[0])
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar item por código: {e}")
            return None
    
    async def listar_com_filtros(self, filtros: EstoqueFiltros) -> List[ItemEstoque]:
        """
        Lista itens com filtros específicos
        
        Args:
            filtros: Filtros de busca
            
        Returns:
            Lista de itens filtrados
        """
        try:
            query = self.supabase_client.table(self.table_name).select("*")
            
            # Aplica filtros
            if filtros.codigo:
                query = query.ilike("codigo", f"%{filtros.codigo}%")
            
            if filtros.nome:
                query = query.ilike("nome", f"%{filtros.nome}%")
            
            if filtros.tipo:
                query = query.eq("tipo", filtros.tipo.value)
            
            if filtros.categoria:
                query = query.ilike("categoria", f"%{filtros.categoria}%")
            
            if filtros.fornecedor_id:
                query = query.eq("fornecedor_id", filtros.fornecedor_id)
            
            if filtros.status:
                query = query.eq("status", filtros.status.value)
            
            if filtros.estoque_baixo:
                # Items com estoque baixo (quantidade <= quantidade_minima)
                query = query.filter("quantidade_atual", "lte", "quantidade_minima")
            
            # Ordenação
            if filtros.ordenar_por:
                query = query.order(filtros.ordenar_por, desc=filtros.ordem_desc)
            else:
                query = query.order("nome")
            
            # Paginação
            if filtros.limite:
                offset = (filtros.pagina - 1) * filtros.limite if filtros.pagina > 1 else 0
                query = query.range(offset, offset + filtros.limite - 1)
            
            result = query.execute()
            return [self._to_model(item) for item in result.data]
        except Exception as e:
            logger.error(f"Erro ao listar itens com filtros: {e}")
            return []
    
    async def buscar_estoque_baixo(self) -> List[ItemEstoque]:
        """
        Busca itens com estoque baixo
        
        Returns:
            Lista de itens com estoque baixo
        """
        try:
            # Query para buscar itens onde quantidade_atual <= quantidade_minima
            result = self.supabase_client.table(self.table_name)\
                .select("*")\
                .filter("quantidade_atual", "lte", "quantidade_minima")\
                .eq("status", "ativo")\
                .order("quantidade_atual")\
                .execute()
            
            return [self._to_model(item) for item in result.data]
        except Exception as e:
            logger.error(f"Erro ao buscar itens com estoque baixo: {e}")
            return []
    
    async def buscar_vencimento_proximo(self, dias: int = 30) -> List[ItemEstoque]:
        """
        Busca itens com vencimento próximo
        
        Args:
            dias: Número de dias para considerar vencimento próximo
            
        Returns:
            Lista de itens com vencimento próximo
        """
        try:
            data_limite = date.today() + date.timedelta(days=dias)
            
            result = self.supabase_client.table(self.table_name)\
                .select("*")\
                .not_.is_("data_validade", "null")\
                .lte("data_validade", data_limite.isoformat())\
                .eq("status", "ativo")\
                .order("data_validade")\
                .execute()
            
            return [self._to_model(item) for item in result.data]
        except Exception as e:
            logger.error(f"Erro ao buscar itens com vencimento próximo: {e}")
            return []
    
    async def movimentar_estoque(self, movimentacao: MovimentacaoEstoque) -> bool:
        """
        Registra movimentação de estoque e atualiza quantidade
        
        Args:
            movimentacao: Dados da movimentação
            
        Returns:
            True se movimentação foi realizada com sucesso
        """
        try:
            # Busca item atual
            item = await self.get_by_id(movimentacao.item_id)
            if not item:
                logger.error(f"Item não encontrado: {movimentacao.item_id}")
                return False
            
            # Calcula nova quantidade
            if movimentacao.tipo == TipoMovimentacao.ENTRADA:
                nova_quantidade = item.quantidade_atual + movimentacao.quantidade
            elif movimentacao.tipo == TipoMovimentacao.SAIDA:
                nova_quantidade = item.quantidade_atual - movimentacao.quantidade
                if nova_quantidade < 0:
                    logger.error("Quantidade insuficiente em estoque")
                    return False
            else:  # AJUSTE
                nova_quantidade = movimentacao.quantidade
            
            # Registra movimentação
            movimentacao_data = {
                "item_id": movimentacao.item_id,
                "tipo": movimentacao.tipo.value,
                "quantidade": movimentacao.quantidade,
                "motivo": movimentacao.motivo,
                "origem": movimentacao.origem,
                "destino": movimentacao.destino,
                "documento": movimentacao.documento,
                "valor_unitario": float(movimentacao.valor_unitario) if movimentacao.valor_unitario else None,
                "valor_total": float(movimentacao.valor_total) if movimentacao.valor_total else None,
                "usuario_id": movimentacao.usuario_id,
                "observacoes": movimentacao.observacoes,
                "created_at": datetime.now().isoformat()
            }
            
            mov_result = self.supabase_client.table("estoque_movimentacoes")\
                .insert(movimentacao_data)\
                .execute()
            
            if hasattr(mov_result, 'error') and mov_result.error:
                logger.error(f"Erro ao registrar movimentação: {mov_result.error}")
                return False
            
            # Atualiza quantidade do item
            update_result = self.supabase_client.table(self.table_name)\
                .update({
                    "quantidade_atual": nova_quantidade,
                    "updated_at": datetime.now().isoformat()
                })\
                .eq("id", movimentacao.item_id)\
                .execute()
            
            if hasattr(update_result, 'error') and update_result.error:
                logger.error(f"Erro ao atualizar quantidade: {update_result.error}")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Erro ao movimentar estoque: {e}")
            return False
    
    async def historico_movimentacoes(self, item_id: str, 
                                    limite: int = 50) -> List[Dict[str, Any]]:
        """
        Busca histórico de movimentações de um item
        
        Args:
            item_id: ID do item
            limite: Número máximo de movimentações
            
        Returns:
            Lista de movimentações
        """
        try:
            result = self.supabase_client.table("estoque_movimentacoes")\
                .select("*")\
                .eq("item_id", item_id)\
                .order("created_at", desc=True)\
                .limit(limite)\
                .execute()
            
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Erro ao buscar histórico de movimentações: {e}")
            return []
    
    async def relatorio_estoque(self, data_inicio: date = None, 
                              data_fim: date = None) -> Dict[str, Any]:
        """
        Gera relatório de estoque
        
        Args:
            data_inicio: Data de início (opcional)
            data_fim: Data de fim (opcional)
            
        Returns:
            Relatório de estoque
        """
        try:
            # Estatísticas gerais
            itens_result = self.supabase_client.table(self.table_name)\
                .select("*")\
                .execute()
            
            itens = itens_result.data if itens_result.data else []
            
            # Calcula estatísticas
            total_itens = len(itens)
            itens_ativos = len([i for i in itens if i["status"] == "ativo"])
            valor_total_custo = sum(
                (i["quantidade_atual"] * i["preco_custo"]) 
                for i in itens if i["preco_custo"]
            )
            valor_total_venda = sum(
                (i["quantidade_atual"] * i["preco_venda"]) 
                for i in itens if i["preco_venda"]
            )
            
            # Itens com estoque baixo
            estoque_baixo = len([
                i for i in itens 
                if i["quantidade_atual"] <= i["quantidade_minima"]
            ])
            
            # Movimentações do período (se especificado)
            movimentacoes_periodo = []
            if data_inicio and data_fim:
                mov_result = self.supabase_client.table("estoque_movimentacoes")\
                    .select("*")\
                    .gte("created_at", data_inicio.isoformat())\
                    .lte("created_at", data_fim.isoformat())\
                    .execute()
                
                movimentacoes_periodo = mov_result.data if mov_result.data else []
            
            return {
                "total_itens": total_itens,
                "itens_ativos": itens_ativos,
                "itens_com_estoque_baixo": estoque_baixo,
                "valor_total_custo": float(valor_total_custo),
                "valor_total_venda": float(valor_total_venda),
                "movimentacoes_periodo": len(movimentacoes_periodo),
                "data_geracao": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao gerar relatório de estoque: {e}")
            return {}
    
    async def verificar_disponibilidade(self, item_id: str, 
                                      quantidade_solicitada: int) -> bool:
        """
        Verifica se há quantidade disponível em estoque
        
        Args:
            item_id: ID do item
            quantidade_solicitada: Quantidade solicitada
            
        Returns:
            True se há quantidade disponível
        """
        try:
            item = await self.get_by_id(item_id)
            if not item:
                return False
            
            return item.quantidade_atual >= quantidade_solicitada
        except Exception as e:
            logger.error(f"Erro ao verificar disponibilidade: {e}")
            return False
    
    async def reservar_item(self, item_id: str, quantidade: int, 
                          motivo: str = "Reserva para OS") -> bool:
        """
        Reserva quantidade de um item (reduz do estoque disponível)
        
        Args:
            item_id: ID do item
            quantidade: Quantidade a reservar
            motivo: Motivo da reserva
            
        Returns:
            True se reserva foi realizada
        """
        try:
            # Cria movimentação de saída
            movimentacao = MovimentacaoEstoque(
                item_id=item_id,
                tipo=TipoMovimentacao.SAIDA,
                quantidade=quantidade,
                motivo=motivo,
                origem="estoque",
                destino="reserva"
            )
            
            return await self.movimentar_estoque(movimentacao)
        except Exception as e:
            logger.error(f"Erro ao reservar item: {e}")
            return False
    
    async def liberar_reserva(self, item_id: str, quantidade: int, 
                            motivo: str = "Liberação de reserva") -> bool:
        """
        Libera reserva de um item (retorna ao estoque disponível)
        
        Args:
            item_id: ID do item
            quantidade: Quantidade a liberar
            motivo: Motivo da liberação
            
        Returns:
            True se liberação foi realizada
        """
        try:
            # Cria movimentação de entrada
            movimentacao = MovimentacaoEstoque(
                item_id=item_id,
                tipo=TipoMovimentacao.ENTRADA,
                quantidade=quantidade,
                motivo=motivo,
                origem="reserva",
                destino="estoque"
            )
            
            return await self.movimentar_estoque(movimentacao)
        except Exception as e:
            logger.error(f"Erro ao liberar reserva: {e}")
            return False 