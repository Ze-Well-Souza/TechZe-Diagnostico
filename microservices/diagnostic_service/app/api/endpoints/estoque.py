"""
API Endpoints para Estoque
Endpoints: CRUD, movimentações, alertas, relatórios
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from datetime import datetime
from decimal import Decimal

from ...models.estoque import (
    ItemEstoqueCreate, ItemEstoqueUpdate, ItemEstoqueResponse,
    MovimentacaoCreate, MovimentacaoEstoque, 
    EstoqueFiltros, CategoriaItem, StatusAlerta, TipoMovimentacao
)
from ...services.estoque_service import EstoqueService
from ...core.auth import get_current_user
from ...core.rbac import require_permission

router = APIRouter(prefix="/estoque", tags=["Estoque"])

# Dependências
def get_estoque_service() -> EstoqueService:
    return EstoqueService()

# --- GESTÃO DE ITENS ---

@router.post("/itens", response_model=ItemEstoqueResponse, status_code=status.HTTP_201_CREATED)
async def criar_item(
    item_data: ItemEstoqueCreate,
    service: EstoqueService = Depends(get_estoque_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:create"))
):
    """
    Cria um novo item no estoque
    
    **Permissões:** estoque:create
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Código único automático (se não fornecido)
    - Cálculo automático de margem de lucro
    - Registro de movimentação inicial
    """
    try:
        item_data.criado_por = current_user["id"]
        result = await service.criar_item(item_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/itens/{item_id}", response_model=ItemEstoqueResponse)
async def buscar_item(
    item_id: str,
    service: EstoqueService = Depends(get_estoque_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:read"))
):
    """
    Busca um item do estoque por ID
    
    **Permissões:** estoque:read
    **Roles:** Técnico, Gerente, Admin
    """
    try:
        result = await service.buscar_item(item_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrado"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/itens/codigo/{codigo}", response_model=ItemEstoqueResponse)
async def buscar_item_por_codigo(
    codigo: str,
    service: EstoqueService = Depends(get_estoque_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:read"))
):
    """
    Busca um item do estoque por código
    
    **Permissões:** estoque:read
    **Roles:** Técnico, Gerente, Admin
    """
    try:
        result = await service.buscar_por_codigo(codigo)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrado"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/itens", response_model=List[ItemEstoqueResponse])
async def listar_itens(
    categoria: Optional[List[CategoriaItem]] = Query(None),
    nome: Optional[str] = Query(None),
    codigo: Optional[str] = Query(None),
    fornecedor_id: Optional[str] = Query(None),
    status_alerta: Optional[List[StatusAlerta]] = Query(None),
    preco_minimo: Optional[float] = Query(None),
    preco_maximo: Optional[float] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    service: EstoqueService = Depends(get_estoque_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:list"))
):
    """
    Lista itens do estoque com filtros opcionais
    
    **Permissões:** estoque:list
    **Roles:** Técnico, Gerente, Admin
    **Filtros disponíveis:**
    - categoria: Lista de categorias
    - nome: Nome do item (busca parcial)
    - codigo: Código do item (busca parcial)
    - fornecedor_id: ID do fornecedor
    - status_alerta: Alertas (estoque baixo, vencido, etc.)
    - preco_minimo/preco_maximo: Faixa de preços
    - limit/offset: Paginação
    """
    try:
        filtros = EstoqueFiltros(
            categoria=categoria,
            nome=nome,
            codigo=codigo,
            fornecedor_id=fornecedor_id,
            status_alerta=status_alerta,
            preco_minimo=preco_minimo,
            preco_maximo=preco_maximo
        )
        
        result = await service.listar_itens(filtros, limit, offset)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/itens/{item_id}", response_model=ItemEstoqueResponse)
async def atualizar_item(
    item_id: str,
    item_data: ItemEstoqueUpdate,
    service: EstoqueService = Depends(get_estoque_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:update"))
):
    """
    Atualiza um item do estoque
    
    **Permissões:** estoque:update
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Recálculo automático de margem de lucro
    - Validações de negócio
    """
    try:
        result = await service.atualizar_item(item_id, item_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrado"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# --- MOVIMENTAÇÕES ---

@router.post("/itens/{item_id}/entrada", response_model=ItemEstoqueResponse)
async def entrada_estoque(
    item_id: str,
    quantidade: int = Query(..., gt=0),
    preco_custo: Optional[float] = Query(None),
    observacoes: str = Query(""),
    service: EstoqueService = Depends(get_estoque_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:movimentacao"))
):
    """
    Registra entrada de estoque
    
    **Permissões:** estoque:movimentacao
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Atualização automática de quantidade
    - Atualização de preço de custo (opcional)
    - Registro de movimentação no histórico
    """
    try:
        preco_decimal = Decimal(str(preco_custo)) if preco_custo else None
        
        result = await service.entrada_estoque(
            item_id=item_id,
            quantidade=quantidade,
            preco_custo=preco_decimal,
            observacoes=observacoes,
            usuario=current_user["id"]
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrado"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/itens/{item_id}/saida", response_model=ItemEstoqueResponse)
async def saida_estoque(
    item_id: str,
    quantidade: int = Query(..., gt=0),
    observacoes: str = Query(""),
    ordem_servico_id: Optional[str] = Query(None),
    service: EstoqueService = Depends(get_estoque_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:movimentacao"))
):
    """
    Registra saída de estoque
    
    **Permissões:** estoque:movimentacao
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Validação de quantidade disponível
    - Atualização automática de quantidade
    - Registro de movimentação no histórico
    - Vinculação com ordem de serviço (opcional)
    """
    try:
        result = await service.saida_estoque(
            item_id=item_id,
            quantidade=quantidade,
            observacoes=observacoes,
            usuario=current_user["id"],
            ordem_servico_id=ordem_servico_id
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Item não encontrado"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/movimentacoes", response_model=List[MovimentacaoEstoque])
async def listar_movimentacoes(
    item_id: Optional[str] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    tipo: Optional[TipoMovimentacao] = Query(None),
    limit: int = Query(50, le=100),
    service: EstoqueService = Depends(get_estoque_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:movimentacoes"))
):
    """
    Lista movimentações de estoque
    
    **Permissões:** estoque:movimentacoes
    **Roles:** Técnico, Gerente, Admin
    **Filtros disponíveis:**
    - item_id: Movimentações de um item específico
    - data_inicio/data_fim: Período de movimentação
    - tipo: Tipo de movimentação (entrada/saída)
    - limit: Limite de resultados
    """
    try:
        result = await service.listar_movimentacoes(
            item_id=item_id,
            data_inicio=data_inicio,
            data_fim=data_fim,
            limit=limit
        )
        
        # Aplicar filtro de tipo se fornecido
        if tipo:
            result = [mov for mov in result if mov.tipo == tipo]
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# --- ALERTAS E RELATÓRIOS ---

@router.get("/alertas")
async def verificar_alertas(
    service: EstoqueService = Depends(get_estoque_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:alertas"))
):
    """
    Verifica alertas de estoque
    
    **Permissões:** estoque:alertas
    **Roles:** Técnico, Gerente, Admin
    **Retorna:**
    - Itens com estoque baixo
    - Produtos vencidos
    - Produtos próximos ao vencimento
    """
    try:
        result = await service.verificar_alertas()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/relatorios/geral")
async def relatorio_estoque(
    categoria: Optional[CategoriaItem] = Query(None),
    service: EstoqueService = Depends(get_estoque_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:reports"))
):
    """
    Gera relatório geral do estoque
    
    **Permissões:** estoque:reports
    **Roles:** Gerente, Admin
    **Retorna:**
    - Resumo estatístico
    - Distribuição por categorias
    - Alertas resumidos
    - Valor total do estoque
    """
    try:
        result = await service.gerar_relatorio_estoque(categoria)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/relatorios/movimentacoes")
async def relatorio_movimentacoes(
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    categoria: Optional[CategoriaItem] = Query(None),
    service: EstoqueService = Depends(get_estoque_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:reports"))
):
    """
    Gera relatório de movimentações
    
    **Permissões:** estoque:reports
    **Roles:** Gerente, Admin
    **Filtros:**
    - data_inicio/data_fim: Período
    - categoria: Categoria específica
    """
    try:
        # Buscar movimentações no período
        movimentacoes = await service.listar_movimentacoes(
            data_inicio=data_inicio,
            data_fim=data_fim,
            limit=1000  # Limite alto para relatório
        )
        
        # Filtrar por categoria se fornecida
        if categoria:
            # TODO: Implementar filtro por categoria nas movimentações
            pass
        
        # Calcular estatísticas
        entradas = [m for m in movimentacoes if m.tipo == TipoMovimentacao.ENTRADA]
        saidas = [m for m in movimentacoes if m.tipo == TipoMovimentacao.SAIDA]
        
        total_entradas = sum(m.quantidade for m in entradas)
        total_saidas = sum(m.quantidade for m in saidas)
        
        valor_entradas = sum(m.valor_total or 0 for m in entradas)
        valor_saidas = sum(m.valor_total or 0 for m in saidas)
        
        return {
            "periodo": {
                "inicio": data_inicio.isoformat() if data_inicio else None,
                "fim": data_fim.isoformat() if data_fim else None
            },
            "total_movimentacoes": len(movimentacoes),
            "entradas": {
                "quantidade": total_entradas,
                "valor": valor_entradas,
                "count": len(entradas)
            },
            "saidas": {
                "quantidade": total_saidas,
                "valor": valor_saidas,
                "count": len(saidas)
            },
            "saldo": {
                "quantidade": total_entradas - total_saidas,
                "valor": valor_entradas - valor_saidas
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# --- ENDPOINTS AUXILIARES ---

@router.get("/categorias")
async def listar_categorias(
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:read"))
):
    """
    Lista todas as categorias disponíveis
    
    **Permissões:** estoque:read
    **Roles:** Técnico, Gerente, Admin
    """
    return [{"value": cat.value, "label": cat.value.replace("_", " ").title()} 
            for cat in CategoriaItem]

@router.get("/itens/busca/{termo}")
async def buscar_itens_rapida(
    termo: str,
    limit: int = Query(10, le=20),
    service: EstoqueService = Depends(get_estoque_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("estoque:read"))
):
    """
    Busca rápida de itens por nome ou código
    
    **Permissões:** estoque:read
    **Roles:** Técnico, Gerente, Admin
    **Uso:** Para autocomplete em formulários
    """
    try:
        # Buscar por nome
        filtros_nome = EstoqueFiltros(nome=termo)
        resultados_nome = await service.listar_itens(filtros_nome, limit // 2, 0)
        
        # Buscar por código
        filtros_codigo = EstoqueFiltros(codigo=termo)
        resultados_codigo = await service.listar_itens(filtros_codigo, limit // 2, 0)
        
        # Combinar e remover duplicatas
        todos_resultados = resultados_nome + resultados_codigo
        resultados_unicos = []
        ids_vistos = set()
        
        for item in todos_resultados:
            if item.id not in ids_vistos:
                resultados_unicos.append(item)
                ids_vistos.add(item.id)
        
        return resultados_unicos[:limit]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 