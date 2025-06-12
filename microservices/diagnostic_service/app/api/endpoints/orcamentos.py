"""
API Endpoints para Orçamentos
Endpoints: CRUD, aprovação, rejeição, relatórios
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status
from datetime import datetime

from ...models.orcamento import (
    OrcamentoCreate, OrcamentoUpdate, OrcamentoResponse, 
    OrcamentoDetalhado, OrcamentoAprovacao, OrcamentoFiltros,
    StatusOrcamento, PrioridadeOrcamento
)
from ...services.orcamento_service import OrcamentoService
from ...core.auth import get_current_user
from ...core.rbac import require_permission

router = APIRouter(tags=["Orçamentos"])

# Dependências
def get_orcamento_service() -> OrcamentoService:
    return OrcamentoService()

@router.post("/", response_model=OrcamentoResponse, status_code=status.HTTP_201_CREATED)
async def criar_orcamento(
    orcamento_data: OrcamentoCreate,
    service: OrcamentoService = Depends(get_orcamento_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("orcamentos:create"))
):
    """
    Cria um novo orçamento
    
    **Permissões:** orcamentos:create
    **Roles:** Técnico, Gerente, Admin
    """
    try:
        # Adicionar usuário criador
        orcamento_data.criado_por = current_user["id"]
        
        result = await service.criar_orcamento(orcamento_data)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{orcamento_id}", response_model=OrcamentoDetalhado)
async def buscar_orcamento(
    orcamento_id: str,
    service: OrcamentoService = Depends(get_orcamento_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("orcamentos:read"))
):
    """
    Busca um orçamento por ID
    
    **Permissões:** orcamentos:read
    **Roles:** Técnico, Gerente, Admin, Cliente (próprios orçamentos)
    """
    try:
        result = await service.buscar_orcamento(orcamento_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado"
            )
        
        # Verificar se cliente pode ver apenas seus orçamentos
        if current_user.get("role") == "cliente":
            if result.cliente.email != current_user.get("email"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Acesso negado"
                )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[OrcamentoResponse])
async def listar_orcamentos(
    status_filter: Optional[List[StatusOrcamento]] = Query(None, alias="status"),
    cliente_nome: Optional[str] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    valor_minimo: Optional[float] = Query(None),
    valor_maximo: Optional[float] = Query(None),
    prioridade: Optional[List[PrioridadeOrcamento]] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    service: OrcamentoService = Depends(get_orcamento_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("orcamentos:list"))
):
    """
    Lista orçamentos com filtros opcionais
    
    **Permissões:** orcamentos:list
    **Roles:** Técnico, Gerente, Admin
    **Filtros disponíveis:**
    - status: Lista de status para filtrar
    - cliente_nome: Nome do cliente (busca parcial)
    - data_inicio/data_fim: Período de criação
    - valor_minimo/valor_maximo: Faixa de valores
    - prioridade: Lista de prioridades
    - limit/offset: Paginação
    """
    try:
        filtros = OrcamentoFiltros(
            status=status_filter,
            cliente_nome=cliente_nome,
            data_inicio=data_inicio,
            data_fim=data_fim,
            valor_minimo=valor_minimo,
            valor_maximo=valor_maximo,
            prioridade=prioridade
        )
        
        result = await service.listar_orcamentos(filtros, limit, offset)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/{orcamento_id}", response_model=OrcamentoResponse)
async def atualizar_orcamento(
    orcamento_id: str,
    orcamento_data: OrcamentoUpdate,
    service: OrcamentoService = Depends(get_orcamento_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("orcamentos:update"))
):
    """
    Atualiza um orçamento existente
    
    **Permissões:** orcamentos:update
    **Roles:** Técnico, Gerente, Admin
    **Restrições:** 
    - Não pode editar orçamentos aprovados/rejeitados
    - Valores são recalculados automaticamente
    """
    try:
        result = await service.atualizar_orcamento(orcamento_id, orcamento_data)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado ou não pode ser editado"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{orcamento_id}/aprovar", response_model=OrcamentoResponse)
async def aprovar_orcamento(
    orcamento_id: str,
    aprovacao: OrcamentoAprovacao,
    service: OrcamentoService = Depends(get_orcamento_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("orcamentos:approve"))
):
    """
    Aprova um orçamento
    
    **Permissões:** orcamentos:approve
    **Roles:** Gerente, Admin, Cliente (próprios orçamentos)
    **Funcionalidades:**
    - Validação de assinatura digital
    - Criação automática de OS (se configurado)
    - Notificações automáticas
    """
    try:
        # Adicionar usuário que aprovou
        aprovacao.aprovado_por = current_user["id"]
        
        result = await service.aprovar_orcamento(orcamento_id, aprovacao)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado ou já processado"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{orcamento_id}/rejeitar", response_model=OrcamentoResponse)
async def rejeitar_orcamento(
    orcamento_id: str,
    motivo: str,
    service: OrcamentoService = Depends(get_orcamento_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("orcamentos:reject"))
):
    """
    Rejeita um orçamento
    
    **Permissões:** orcamentos:reject
    **Roles:** Gerente, Admin, Cliente (próprios orçamentos)
    """
    try:
        result = await service.rejeitar_orcamento(
            orcamento_id, motivo, current_user["id"]
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado ou já processado"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/relatorios/estatisticas")
async def relatorio_orcamentos(
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    service: OrcamentoService = Depends(get_orcamento_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("orcamentos:reports"))
):
    """
    Gera relatório estatístico de orçamentos
    
    **Permissões:** orcamentos:reports
    **Roles:** Gerente, Admin
    **Retorna:**
    - Total de orçamentos
    - Valor total e médio
    - Distribuição por status
    - Taxa de aprovação
    """
    try:
        filtros = OrcamentoFiltros(
            data_inicio=data_inicio,
            data_fim=data_fim
        )
        
        result = await service.gerar_relatorio_orcamentos(filtros)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{orcamento_id}/pdf")
async def exportar_orcamento_pdf(
    orcamento_id: str,
    service: OrcamentoService = Depends(get_orcamento_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("orcamentos:export"))
):
    """
    Exporta orçamento em PDF
    
    **Permissões:** orcamentos:export
    **Roles:** Técnico, Gerente, Admin
    """
    try:
        # Buscar orçamento
        orcamento = await service.buscar_orcamento(orcamento_id)
        if not orcamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado"
            )
        
        # TODO: Implementar geração de PDF
        # Por enquanto retorna os dados para download
        return {
            "message": "Funcionalidade de PDF em desenvolvimento",
            "orcamento": orcamento
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{orcamento_id}/whatsapp")
async def compartilhar_whatsapp(
    orcamento_id: str,
    service: OrcamentoService = Depends(get_orcamento_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("orcamentos:share"))
):
    """
    Gera link para compartilhar orçamento via WhatsApp
    
    **Permissões:** orcamentos:share
    **Roles:** Técnico, Gerente, Admin
    """
    try:
        # Buscar orçamento
        orcamento = await service.buscar_orcamento(orcamento_id)
        if not orcamento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Orçamento não encontrado"
            )
        
        # Gerar mensagem para WhatsApp
        telefone = orcamento.cliente.telefone.replace("+", "").replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        
        mensagem = f"""
*ORÇAMENTO TechZe Diagnóstico* 📋

*Cliente:* {orcamento.cliente.nome}
*Orçamento:* {orcamento.numero}
*Equipamento:* {orcamento.equipamento.tipo} {orcamento.equipamento.marca} {orcamento.equipamento.modelo}

*Valor Total:* R$ {orcamento.valor_final:.2f}

Para aprovar ou visualizar detalhes:
{orcamento_id}  # TODO: Link para portal do cliente

_Válido até: {orcamento.valido_ate.strftime('%d/%m/%Y')}_
        """.strip()
        
        # URL do WhatsApp
        whatsapp_url = f"https://wa.me/{telefone}?text={mensagem}"
        
        return {
            "whatsapp_url": whatsapp_url,
            "telefone": telefone,
            "mensagem": mensagem
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# VERSÕES TEMPORÁRIAS SEM AUTH PARA TESTES
@router.post("/test", status_code=status.HTTP_201_CREATED)
async def criar_orcamento_test(
    orcamento_data: dict,
    service: OrcamentoService = Depends(get_orcamento_service)
):
    """
    ENDPOINT TEMPORÁRIO - Cria orçamento sem autenticação para testes
    """
    try:
        # Mock current_user para desenvolvimento
        mock_user = {"id": "test-user", "role": "admin"}
        
        # Converter dados para OrcamentoCreate (simplificado)
        from ...models.orcamento import DadosCliente, DadosEquipamento
        
        cliente_data = orcamento_data.get("cliente", {
            "nome": "Cliente Teste",
            "telefone": "11999887766",
            "email": "test@cliente.com"
        })
        
        equipamento_data = orcamento_data.get("equipamento", {
            "tipo": "smartphone",
            "marca": "Samsung",
            "modelo": "Galaxy Test",
            "problema_relatado": "Teste automatizado"
        })
        
        # Criar objetos necessários
        cliente = DadosCliente(**cliente_data)
        equipamento = DadosEquipamento(**equipamento_data)
        
        # Criar um orcamento simplificado
        from ...models.orcamento import Orcamento, StatusOrcamento
        orcamento = Orcamento(
            numero=f"TEST-{hash(str(orcamento_data)) % 10000}",
            cliente=cliente,
            equipamento=equipamento,
            status=StatusOrcamento.PENDENTE
        )
        
        # Simular criação bem-sucedida
        return {
            "id": orcamento.id,
            "numero": orcamento.numero,
            "status": orcamento.status.value,
            "cliente": cliente_data,
            "equipamento": equipamento_data,
            "created_at": orcamento.data_criacao.isoformat(),
            "message": "Orçamento criado com sucesso (teste)"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro no teste: {str(e)}"
        )

@router.get("/test/list")
async def listar_orcamentos_test():
    """
    ENDPOINT TEMPORÁRIO - Lista orçamentos sem autenticação para testes
    """
    return {
        "total": 3,
        "items": [
            {
                "id": "test-1",
                "numero": "TEST-001",
                "status": "pendente",
                "cliente": {"nome": "Cliente Test 1"},
                "valor_total": 150.00
            },
            {
                "id": "test-2", 
                "numero": "TEST-002",
                "status": "aprovado",
                "cliente": {"nome": "Cliente Test 2"},
                "valor_total": 250.00
            },
            {
                "id": "test-3",
                "numero": "TEST-003", 
                "status": "pendente",
                "cliente": {"nome": "Cliente Test 3"},
                "valor_total": 350.00
            }
        ]
    } 