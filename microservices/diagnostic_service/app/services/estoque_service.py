"""
Serviço de Estoque - Lógica de negócio para gestão de estoque
Responsável por: CRUD, movimentações, alertas, controle de validade
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
from decimal import Decimal

from ..models.estoque import (
    ItemEstoque, ItemEstoqueCreate, ItemEstoqueUpdate, ItemEstoqueResponse,
    MovimentacaoEstoque, MovimentacaoCreate, Fornecedor,
    TipoMovimentacao, StatusAlerta, CategoriaItem, EstoqueFiltros
)
from ..core.config import get_settings
from ..core.supabase import get_supabase_client

settings = get_settings()

class EstoqueService:
    """Service para gestão de estoque"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.table_estoque = "estoque_itens"
        self.table_movimentacao = "estoque_movimentacoes"
        self.table_fornecedores = "fornecedores"
        
    # --- GESTÃO DE ITENS ---
    
    async def criar_item(self, dados: ItemEstoqueCreate) -> ItemEstoqueResponse:
        """Cria um novo item no estoque"""
        try:
            # Gerar código único se não fornecido
            codigo = dados.codigo or await self._gerar_codigo_item(dados.categoria)
            
            item_data = {
                "id": str(uuid.uuid4()),
                "codigo": codigo,
                "nome": dados.nome,
                "descricao": dados.descricao,
                "categoria": dados.categoria.value,
                "tipo": dados.tipo.value,
                "marca": dados.marca,
                "modelo": dados.modelo,
                "numero_serie": dados.numero_serie,
                "fornecedor_id": dados.fornecedor_id,
                "quantidade_atual": dados.quantidade_inicial,
                "quantidade_minima": dados.quantidade_minima,
                "quantidade_maxima": dados.quantidade_maxima,
                "localizacao": dados.localizacao,
                "preco_custo": float(dados.preco_custo),
                "preco_venda": float(dados.preco_venda),
                "margem_lucro": self._calcular_margem_lucro(dados.preco_custo, dados.preco_venda),
                "data_validade": dados.data_validade.isoformat() if dados.data_validade else None,
                "observacoes": dados.observacoes,
                "status": dados.status.value,
                "criado_em": datetime.now().isoformat(),
                "criado_por": dados.criado_por
            }
            
            result = self.supabase.table(self.table_estoque).insert(item_data).execute()
            
            if result.data:
                # Registrar movimentação inicial
                if dados.quantidade_inicial > 0:
                    await self._registrar_movimentacao(
                        item_id=result.data[0]["id"],
                        tipo=TipoMovimentacao.ENTRADA,
                        quantidade=dados.quantidade_inicial,
                        observacoes="Estoque inicial",
                        usuario=dados.criado_por
                    )
                
                return ItemEstoqueResponse.model_validate(result.data[0])
            else:
                raise Exception("Erro ao criar item")
                
        except Exception as e:
            raise Exception(f"Erro ao criar item: {str(e)}")
    
    async def buscar_item(self, item_id: str) -> Optional[ItemEstoqueResponse]:
        """Busca um item por ID"""
        try:
            result = self.supabase.table(self.table_estoque)\
                .select("*, fornecedores(*)")\
                .eq("id", item_id)\
                .execute()
            
            if result.data:
                return ItemEstoqueResponse.model_validate(result.data[0])
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar item: {str(e)}")
    
    async def buscar_por_codigo(self, codigo: str) -> Optional[ItemEstoqueResponse]:
        """Busca um item por código"""
        try:
            result = self.supabase.table(self.table_estoque)\
                .select("*, fornecedores(*)")\
                .eq("codigo", codigo)\
                .execute()
            
            if result.data:
                return ItemEstoqueResponse.model_validate(result.data[0])
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar item por código: {str(e)}")
    
    async def listar_itens(
        self, 
        filtros: Optional[EstoqueFiltros] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ItemEstoqueResponse]:
        """Lista itens com filtros opcionais"""
        try:
            query = self.supabase.table(self.table_estoque).select("*, fornecedores(*)")
            
            if filtros:
                if filtros.categoria:
                    query = query.in_("categoria", [c.value for c in filtros.categoria])
                
                if filtros.nome:
                    query = query.ilike("nome", f"%{filtros.nome}%")
                
                if filtros.codigo:
                    query = query.ilike("codigo", f"%{filtros.codigo}%")
                
                if filtros.fornecedor_id:
                    query = query.eq("fornecedor_id", filtros.fornecedor_id)
                
                if filtros.status_alerta:
                    if StatusAlerta.ESTOQUE_BAIXO in filtros.status_alerta:
                        query = query.lt("quantidade_atual", "quantidade_minima")
                    if StatusAlerta.PRODUTO_VENCIDO in filtros.status_alerta:
                        query = query.lt("data_validade", datetime.now().isoformat())
                
                if filtros.preco_minimo:
                    query = query.gte("preco_venda", filtros.preco_minimo)
                
                if filtros.preco_maximo:
                    query = query.lte("preco_venda", filtros.preco_maximo)
            
            query = query.order("nome").range(offset, offset + limit - 1)
            result = query.execute()
            
            return [ItemEstoqueResponse.model_validate(item) for item in result.data]
            
        except Exception as e:
            raise Exception(f"Erro ao listar itens: {str(e)}")
    
    async def atualizar_item(
        self, 
        item_id: str, 
        dados: ItemEstoqueUpdate
    ) -> Optional[ItemEstoqueResponse]:
        """Atualiza um item existente"""
        try:
            update_data = {}
            
            if dados.nome is not None:
                update_data["nome"] = dados.nome
            
            if dados.descricao is not None:
                update_data["descricao"] = dados.descricao
            
            if dados.quantidade_minima is not None:
                update_data["quantidade_minima"] = dados.quantidade_minima
            
            if dados.quantidade_maxima is not None:
                update_data["quantidade_maxima"] = dados.quantidade_maxima
            
            if dados.localizacao is not None:
                update_data["localizacao"] = dados.localizacao
            
            if dados.preco_custo is not None:
                update_data["preco_custo"] = float(dados.preco_custo)
                
                # Recalcular margem se preço de custo mudou
                item_atual = await self.buscar_item(item_id)
                if item_atual:
                    preco_venda = dados.preco_venda or item_atual.preco_venda
                    update_data["margem_lucro"] = self._calcular_margem_lucro(dados.preco_custo, preco_venda)
            
            if dados.preco_venda is not None:
                update_data["preco_venda"] = float(dados.preco_venda)
                
                # Recalcular margem se preço de venda mudou
                item_atual = await self.buscar_item(item_id)
                if item_atual:
                    preco_custo = dados.preco_custo or item_atual.preco_custo
                    update_data["margem_lucro"] = self._calcular_margem_lucro(preco_custo, dados.preco_venda)
            
            if dados.data_validade is not None:
                update_data["data_validade"] = dados.data_validade.isoformat()
            
            if dados.observacoes is not None:
                update_data["observacoes"] = dados.observacoes
            
            if dados.status is not None:
                update_data["status"] = dados.status.value
            
            update_data["atualizado_em"] = datetime.now().isoformat()
            
            result = self.supabase.table(self.table_estoque)\
                .update(update_data)\
                .eq("id", item_id)\
                .execute()
            
            if result.data:
                return ItemEstoqueResponse.model_validate(result.data[0])
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao atualizar item: {str(e)}")
    
    # --- MOVIMENTAÇÕES ---
    
    async def entrada_estoque(
        self, 
        item_id: str, 
        quantidade: int, 
        preco_custo: Optional[Decimal] = None,
        observacoes: str = "",
        usuario: str = ""
    ) -> Optional[ItemEstoqueResponse]:
        """Registra entrada de estoque"""
        try:
            # Buscar item atual
            item = await self.buscar_item(item_id)
            if not item:
                raise Exception("Item não encontrado")
            
            # Atualizar quantidade
            nova_quantidade = item.quantidade_atual + quantidade
            update_data = {"quantidade_atual": nova_quantidade}
            
            # Atualizar preço de custo se fornecido
            if preco_custo:
                update_data["preco_custo"] = float(preco_custo)
                update_data["margem_lucro"] = self._calcular_margem_lucro(preco_custo, item.preco_venda)
            
            # Atualizar item
            result = self.supabase.table(self.table_estoque)\
                .update(update_data)\
                .eq("id", item_id)\
                .execute()
            
            if result.data:
                # Registrar movimentação
                await self._registrar_movimentacao(
                    item_id=item_id,
                    tipo=TipoMovimentacao.ENTRADA,
                    quantidade=quantidade,
                    preco_unitario=preco_custo,
                    observacoes=observacoes,
                    usuario=usuario
                )
                
                return ItemEstoqueResponse.model_validate(result.data[0])
            return None
            
        except Exception as e:
            raise Exception(f"Erro na entrada de estoque: {str(e)}")
    
    async def saida_estoque(
        self, 
        item_id: str, 
        quantidade: int,
        observacoes: str = "",
        usuario: str = "",
        ordem_servico_id: Optional[str] = None
    ) -> Optional[ItemEstoqueResponse]:
        """Registra saída de estoque"""
        try:
            # Buscar item atual
            item = await self.buscar_item(item_id)
            if not item:
                raise Exception("Item não encontrado")
            
            # Verificar se há quantidade suficiente
            if item.quantidade_atual < quantidade:
                raise Exception(f"Quantidade insuficiente. Disponível: {item.quantidade_atual}")
            
            # Atualizar quantidade
            nova_quantidade = item.quantidade_atual - quantidade
            
            result = self.supabase.table(self.table_estoque)\
                .update({"quantidade_atual": nova_quantidade})\
                .eq("id", item_id)\
                .execute()
            
            if result.data:
                # Registrar movimentação
                await self._registrar_movimentacao(
                    item_id=item_id,
                    tipo=TipoMovimentacao.SAIDA,
                    quantidade=quantidade,
                    preco_unitario=item.preco_venda,
                    observacoes=observacoes,
                    usuario=usuario,
                    ordem_servico_id=ordem_servico_id
                )
                
                return ItemEstoqueResponse.model_validate(result.data[0])
            return None
            
        except Exception as e:
            raise Exception(f"Erro na saída de estoque: {str(e)}")
    
    async def listar_movimentacoes(
        self, 
        item_id: Optional[str] = None,
        data_inicio: Optional[datetime] = None,
        data_fim: Optional[datetime] = None,
        limit: int = 50
    ) -> List[MovimentacaoEstoque]:
        """Lista movimentações de estoque"""
        try:
            query = self.supabase.table(self.table_movimentacao)\
                .select("*, estoque_itens(nome, codigo)")
            
            if item_id:
                query = query.eq("item_id", item_id)
            
            if data_inicio:
                query = query.gte("data_movimentacao", data_inicio.isoformat())
            
            if data_fim:
                query = query.lte("data_movimentacao", data_fim.isoformat())
            
            query = query.order("data_movimentacao", desc=True).limit(limit)
            result = query.execute()
            
            return [MovimentacaoEstoque.model_validate(mov) for mov in result.data]
            
        except Exception as e:
            raise Exception(f"Erro ao listar movimentações: {str(e)}")
    
    # --- ALERTAS E RELATÓRIOS ---
    
    async def verificar_alertas(self) -> Dict[str, List[ItemEstoqueResponse]]:
        """Verifica e retorna alertas de estoque"""
        try:
            # Estoque baixo
            result_baixo = self.supabase.table(self.table_estoque)\
                .select("*")\
                .filter("quantidade_atual", "lt", "quantidade_minima")\
                .execute()
            
            # Produtos vencidos
            result_vencidos = self.supabase.table(self.table_estoque)\
                .select("*")\
                .lt("data_validade", datetime.now().isoformat())\
                .execute()
            
            # Produtos próximos ao vencimento (30 dias)
            data_limite = (datetime.now() + timedelta(days=30)).isoformat()
            result_vencimento = self.supabase.table(self.table_estoque)\
                .select("*")\
                .lte("data_validade", data_limite)\
                .gte("data_validade", datetime.now().isoformat())\
                .execute()
            
            return {
                "estoque_baixo": [ItemEstoqueResponse.model_validate(item) for item in result_baixo.data],
                "produtos_vencidos": [ItemEstoqueResponse.model_validate(item) for item in result_vencidos.data],
                "proximos_vencimento": [ItemEstoqueResponse.model_validate(item) for item in result_vencimento.data]
            }
            
        except Exception as e:
            raise Exception(f"Erro ao verificar alertas: {str(e)}")
    
    async def gerar_relatorio_estoque(
        self, 
        categoria: Optional[CategoriaItem] = None
    ) -> Dict[str, Any]:
        """Gera relatório completo do estoque"""
        try:
            query = self.supabase.table(self.table_estoque).select("*")
            
            if categoria:
                query = query.eq("categoria", categoria.value)
            
            result = query.execute()
            itens = result.data
            
            # Calcular estatísticas
            total_itens = len(itens)
            valor_total_custo = sum(item["preco_custo"] * item["quantidade_atual"] for item in itens)
            valor_total_venda = sum(item["preco_venda"] * item["quantidade_atual"] for item in itens)
            
            # Distribuição por categoria
            categorias = {}
            for item in itens:
                cat = item["categoria"]
                if cat not in categorias:
                    categorias[cat] = {"quantidade": 0, "valor": 0}
                categorias[cat]["quantidade"] += item["quantidade_atual"]
                categorias[cat]["valor"] += item["preco_venda"] * item["quantidade_atual"]
            
            # Itens com alertas
            alertas = await self.verificar_alertas()
            
            return {
                "resumo": {
                    "total_itens": total_itens,
                    "valor_total_custo": valor_total_custo,
                    "valor_total_venda": valor_total_venda,
                    "margem_lucro_media": ((valor_total_venda - valor_total_custo) / valor_total_custo * 100) if valor_total_custo > 0 else 0
                },
                "distribuicao_categorias": categorias,
                "alertas": {
                    "estoque_baixo": len(alertas["estoque_baixo"]),
                    "produtos_vencidos": len(alertas["produtos_vencidos"]),
                    "proximos_vencimento": len(alertas["proximos_vencimento"])
                },
                "data_geracao": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Erro ao gerar relatório: {str(e)}")
    
    # --- MÉTODOS AUXILIARES ---
    
    async def _gerar_codigo_item(self, categoria: CategoriaItem) -> str:
        """Gera código único para o item"""
        prefixo = categoria.value[:3].upper()
        
        # Buscar último código da categoria
        result = self.supabase.table(self.table_estoque)\
            .select("codigo")\
            .ilike("codigo", f"{prefixo}%")\
            .order("codigo", desc=True)\
            .limit(1)\
            .execute()
        
        if result.data:
            ultimo_codigo = result.data[0]["codigo"]
            numero = int(ultimo_codigo.split("-")[-1]) + 1
        else:
            numero = 1
        
        return f"{prefixo}-{numero:06d}"
    
    def _calcular_margem_lucro(self, preco_custo: Decimal, preco_venda: Decimal) -> float:
        """Calcula margem de lucro percentual"""
        if preco_custo > 0:
            return float(((preco_venda - preco_custo) / preco_custo) * 100)
        return 0.0
    
    async def _registrar_movimentacao(
        self,
        item_id: str,
        tipo: TipoMovimentacao,
        quantidade: int,
        preco_unitario: Optional[Decimal] = None,
        observacoes: str = "",
        usuario: str = "",
        ordem_servico_id: Optional[str] = None
    ) -> None:
        """Registra movimentação no histórico"""
        try:
            movimentacao_data = {
                "id": str(uuid.uuid4()),
                "item_id": item_id,
                "tipo": tipo.value,
                "quantidade": quantidade,
                "preco_unitario": float(preco_unitario) if preco_unitario else None,
                "valor_total": float(preco_unitario * quantidade) if preco_unitario else None,
                "observacoes": observacoes,
                "usuario": usuario,
                "ordem_servico_id": ordem_servico_id,
                "data_movimentacao": datetime.now().isoformat()
            }
            
            self.supabase.table(self.table_movimentacao).insert(movimentacao_data).execute()
            
        except Exception as e:
            # Log do erro mas não falha a operação principal
            print(f"Erro ao registrar movimentação: {str(e)}") 