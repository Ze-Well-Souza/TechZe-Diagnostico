"""
API Endpoints para Ordem de Serviço
Endpoints: CRUD, workflow, anotações, fotos, relatórios
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, status, File, UploadFile
from datetime import datetime

from ...models.ordem_servico import (
    OrdemServicoCreate, OrdemServicoUpdate, OrdemServicoResponse,
    StatusOS, PrioridadeOS, TipoServico, StatusPagamento,
    ServicoPrestado, PecaUtilizada, AnotacaoOS, FotoOS, OSFiltros
)
from ...services.ordem_servico_service import OrdemServicoService
from ...core.auth import get_current_user
from ...core.rbac import require_permission

router = APIRouter(prefix="/ordens-servico", tags=["Ordens de Serviço"])

# Dependências
def get_os_service() -> OrdemServicoService:
    return OrdemServicoService()

# --- CRUD BÁSICO ---

@router.post("/", response_model=OrdemServicoResponse, status_code=status.HTTP_201_CREATED)
async def criar_ordem_servico(
    os_data: OrdemServicoCreate,
    orcamento_id: Optional[str] = Query(None),
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:create"))
):
    """
    Cria uma nova ordem de serviço
    
    **Permissões:** os:create
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Número único automático
    - Vinculação com orçamento (opcional)
    - Cálculo automático de valores
    - Anotação inicial automática
    """
    try:
        os_data.criado_por = current_user["id"]
        result = await service.criar_ordem_servico(os_data, orcamento_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{os_id}", response_model=OrdemServicoResponse)
async def buscar_ordem_servico(
    os_id: str,
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:read"))
):
    """
    Busca uma ordem de serviço por ID
    
    **Permissões:** os:read
    **Roles:** Técnico, Gerente, Admin, Cliente (próprias OSs)
    **Inclui:** Anotações e fotos vinculadas
    """
    try:
        result = await service.buscar_ordem_servico(os_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de serviço não encontrada"
            )
        
        # Verificar se cliente pode ver apenas suas OSs
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

@router.get("/numero/{numero}", response_model=OrdemServicoResponse)
async def buscar_por_numero(
    numero: str,
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:read"))
):
    """
    Busca uma ordem de serviço por número
    
    **Permissões:** os:read
    **Roles:** Técnico, Gerente, Admin
    """
    try:
        result = await service.buscar_por_numero(numero)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de serviço não encontrada"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/", response_model=List[OrdemServicoResponse])
async def listar_ordens_servico(
    status_filter: Optional[List[StatusOS]] = Query(None, alias="status"),
    cliente_nome: Optional[str] = Query(None),
    tecnico_responsavel: Optional[str] = Query(None),
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    prioridade: Optional[List[PrioridadeOS]] = Query(None),
    tipo_servico: Optional[List[TipoServico]] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:list"))
):
    """
    Lista ordens de serviço com filtros opcionais
    
    **Permissões:** os:list
    **Roles:** Técnico, Gerente, Admin
    **Filtros disponíveis:**
    - status: Lista de status para filtrar
    - cliente_nome: Nome do cliente (busca parcial)
    - tecnico_responsavel: ID do técnico responsável
    - data_inicio/data_fim: Período de criação
    - prioridade: Lista de prioridades
    - tipo_servico: Lista de tipos de serviço
    - limit/offset: Paginação
    """
    try:
        filtros = OSFiltros(
            status=status_filter,
            cliente_nome=cliente_nome,
            tecnico_responsavel=tecnico_responsavel,
            data_inicio=data_inicio,
            data_fim=data_fim,
            prioridade=prioridade,
            tipo_servico=tipo_servico
        )
        
        result = await service.listar_ordens_servico(filtros, limit, offset)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# --- WORKFLOW DE STATUS ---

@router.patch("/{os_id}/status", response_model=OrdemServicoResponse)
async def atualizar_status(
    os_id: str,
    novo_status: StatusOS,
    observacoes: str = "",
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:update_status"))
):
    """
    Atualiza status da ordem de serviço
    
    **Permissões:** os:update_status
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Validação de transições de status
    - Ações automáticas por status
    - Baixa automática no estoque (quando concluída)
    - Registro de anotação automática
    """
    try:
        result = await service.atualizar_status(
            os_id, novo_status, observacoes, current_user["id"]
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de serviço não encontrada"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{os_id}/iniciar", response_model=OrdemServicoResponse)
async def iniciar_atendimento(
    os_id: str,
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:update_status"))
):
    """
    Inicia atendimento da OS (muda status para EM_ANDAMENTO)
    
    **Permissões:** os:update_status
    **Roles:** Técnico, Gerente, Admin
    """
    try:
        result = await service.atualizar_status(
            os_id, StatusOS.EM_ANDAMENTO, "Atendimento iniciado", current_user["id"]
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de serviço não encontrada"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{os_id}/concluir", response_model=OrdemServicoResponse)
async def concluir_servico(
    os_id: str,
    observacoes: str = "",
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:update_status"))
):
    """
    Conclui o serviço (muda status para CONCLUIDA)
    
    **Permissões:** os:update_status
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Baixa automática das peças no estoque
    - Registro de data de conclusão
    """
    try:
        result = await service.atualizar_status(
            os_id, StatusOS.CONCLUIDA, observacoes or "Serviço concluído", current_user["id"]
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de serviço não encontrada"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{os_id}/entregar", response_model=OrdemServicoResponse)
async def entregar_equipamento(
    os_id: str,
    observacoes: str = "",
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:update_status"))
):
    """
    Registra entrega do equipamento (muda status para ENTREGUE)
    
    **Permissões:** os:update_status
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Marca pagamento como realizado
    - Registro de data de entrega
    """
    try:
        result = await service.atualizar_status(
            os_id, StatusOS.ENTREGUE, observacoes or "Equipamento entregue", current_user["id"]
        )
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de serviço não encontrada"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# --- SERVIÇOS E PEÇAS ---

@router.post("/{os_id}/servicos", response_model=OrdemServicoResponse)
async def adicionar_servico(
    os_id: str,
    servico: ServicoPrestado,
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:add_items"))
):
    """
    Adiciona um serviço à ordem de serviço
    
    **Permissões:** os:add_items
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Recálculo automático do valor total
    - Registro de anotação automática
    """
    try:
        result = await service.adicionar_servico(os_id, servico, current_user["id"])
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de serviço não encontrada"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{os_id}/pecas", response_model=OrdemServicoResponse)
async def adicionar_peca(
    os_id: str,
    peca: PecaUtilizada,
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:add_items"))
):
    """
    Adiciona uma peça à ordem de serviço
    
    **Permissões:** os:add_items
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Verificação de disponibilidade no estoque
    - Recálculo automático do valor total
    - Registro de anotação automática
    """
    try:
        result = await service.adicionar_peca(os_id, peca, current_user["id"])
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ordem de serviço não encontrada"
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# --- ANOTAÇÕES ---

@router.post("/{os_id}/anotacoes", response_model=AnotacaoOS)
async def adicionar_anotacao(
    os_id: str,
    titulo: str,
    conteudo: str,
    visivel_cliente: bool = True,
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:add_notes"))
):
    """
    Adiciona uma anotação à ordem de serviço
    
    **Permissões:** os:add_notes
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Controle de visibilidade para cliente
    - Timestamp automático
    - Identificação do autor
    """
    try:
        result = await service.adicionar_anotacao(
            os_id, titulo, conteudo, current_user["id"], visivel_cliente
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# --- FOTOS ---

@router.post("/{os_id}/fotos", response_model=FotoOS)
async def adicionar_foto(
    os_id: str,
    foto: FotoOS,
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:add_photos"))
):
    """
    Adiciona uma foto à ordem de serviço
    
    **Permissões:** os:add_photos
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Categorização automática
    - Controle de visibilidade para cliente
    - Timestamp e autor automáticos
    """
    try:
        result = await service.adicionar_foto(os_id, foto, current_user["id"])
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/{os_id}/upload-foto")
async def upload_foto(
    os_id: str,
    file: UploadFile = File(...),
    categoria: str = "diagnostico",
    descricao: str = "",
    visivel_cliente: bool = True,
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:add_photos"))
):
    """
    Upload de foto para ordem de serviço
    
    **Permissões:** os:add_photos
    **Roles:** Técnico, Gerente, Admin
    **Funcionalidades:**
    - Upload direto de arquivo
    - Validação de tipo de arquivo
    - Processamento automático
    """
    try:
        # Validar tipo de arquivo
        if not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Arquivo deve ser uma imagem"
            )
        
        # TODO: Implementar upload para storage (Supabase Storage, AWS S3, etc.)
        # Por enquanto, retornar estrutura simulada
        
        # Simular URL de upload
        file_url = f"https://storage.exemplo.com/os-fotos/{os_id}/{file.filename}"
        
        # Criar objeto foto
        from ...models.ordem_servico import CategoriaFoto
        foto = FotoOS(
            categoria=CategoriaFoto(categoria),
            url=file_url,
            descricao=descricao,
            visivel_cliente=visivel_cliente
        )
        
        result = await service.adicionar_foto(os_id, foto, current_user["id"])
        
        return {
            "message": "Foto adicionada com sucesso",
            "foto": result,
            "file_info": {
                "filename": file.filename,
                "size": file.size,
                "content_type": file.content_type
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# --- RELATÓRIOS ---

@router.get("/relatorios/estatisticas")
async def relatorio_ordens_servico(
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    tecnico_responsavel: Optional[str] = Query(None),
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:reports"))
):
    """
    Gera relatório estatístico de ordens de serviço
    
    **Permissões:** os:reports
    **Roles:** Gerente, Admin
    **Retorna:**
    - Total de OSs por período
    - Distribuição por status
    - Tempo médio de resolução
    - Ticket médio
    - Performance por técnico
    """
    try:
        filtros = OSFiltros(
            data_inicio=data_inicio,
            data_fim=data_fim,
            tecnico_responsavel=tecnico_responsavel
        )
        
        result = await service.gerar_relatorio_os(filtros)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/dashboard/tecnico/{tecnico_id}")
async def dashboard_tecnico(
    tecnico_id: str,
    service: OrdemServicoService = Depends(get_os_service),
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:dashboard"))
):
    """
    Dashboard específico para técnico
    
    **Permissões:** os:dashboard
    **Roles:** Técnico (próprio dashboard), Gerente, Admin
    **Retorna:**
    - OSs em andamento
    - OSs pendentes
    - Performance do técnico
    - Próximos prazos
    """
    try:
        # Verificar se técnico pode ver apenas seu próprio dashboard
        if current_user.get("role") == "tecnico":
            if current_user["id"] != tecnico_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Acesso negado"
                )
        
        # Buscar OSs do técnico no período atual (30 dias)
        data_inicio = datetime.now().replace(day=1)  # Início do mês
        filtros = OSFiltros(
            tecnico_responsavel=tecnico_id,
            data_inicio=data_inicio
        )
        
        todas_os = await service.listar_ordens_servico(filtros, limit=1000)
        
        # Separar por status
        abertas = [os for os in todas_os if os.status == StatusOS.ABERTA]
        em_andamento = [os for os in todas_os if os.status == StatusOS.EM_ANDAMENTO]
        concluidas = [os for os in todas_os if os.status == StatusOS.CONCLUIDA]
        entregues = [os for os in todas_os if os.status == StatusOS.ENTREGUE]
        
        # Calcular métricas
        total_os = len(todas_os)
        valor_total = sum(os.valor_total for os in todas_os)
        ticket_medio = valor_total / total_os if total_os > 0 else 0
        
        # OSs próximas ao prazo (próximos 3 dias)
        from datetime import timedelta
        limite_prazo = datetime.now() + timedelta(days=3)
        proximas_prazo = [
            os for os in em_andamento 
            if os.prazo_estimado and os.prazo_estimado <= limite_prazo
        ]
        
        return {
            "tecnico_id": tecnico_id,
            "periodo": data_inicio.isoformat(),
            "resumo": {
                "total_os": total_os,
                "valor_total": valor_total,
                "ticket_medio": ticket_medio
            },
            "status_distribuicao": {
                "abertas": len(abertas),
                "em_andamento": len(em_andamento),
                "concluidas": len(concluidas),
                "entregues": len(entregues)
            },
            "alertas": {
                "proximas_prazo": len(proximas_prazo),
                "os_proximas_prazo": [
                    {
                        "id": os.id,
                        "numero": os.numero,
                        "cliente": os.cliente.nome,
                        "prazo": os.prazo_estimado.isoformat() if os.prazo_estimado else None
                    }
                    for os in proximas_prazo
                ]
            },
            "os_em_andamento": [
                {
                    "id": os.id,
                    "numero": os.numero,
                    "cliente": os.cliente.nome,
                    "equipamento": f"{os.equipamento.marca} {os.equipamento.modelo}",
                    "valor": os.valor_total,
                    "prazo": os.prazo_estimado.isoformat() if os.prazo_estimado else None
                }
                for os in em_andamento[:10]  # Limitar a 10 mais recentes
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# --- ENDPOINTS AUXILIARES ---

@router.get("/status-opcoes")
async def listar_status_opcoes(
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:read"))
):
    """
    Lista todas as opções de status disponíveis
    
    **Permissões:** os:read
    **Roles:** Técnico, Gerente, Admin
    """
    return [{"value": status.value, "label": status.value.replace("_", " ").title()} 
            for status in StatusOS]

@router.get("/tipos-servico")
async def listar_tipos_servico(
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("os:read"))
):
    """
    Lista todos os tipos de serviço disponíveis
    
    **Permissões:** os:read
    **Roles:** Técnico, Gerente, Admin
    """
    return [{"value": tipo.value, "label": tipo.value.replace("_", " ").title()} 
            for tipo in TipoServico]

# VERSÕES TEMPORÁRIAS SEM AUTH PARA TESTES  
@router.get("/test/list")
async def listar_ordens_servico_test():
    """
    ENDPOINT TEMPORÁRIO - Lista OS sem autenticação para testes
    """
    return {
        "total": 4,
        "items": [
            {
                "id": "os-1",
                "numero": "OS-001",
                "status": "aguardando",
                "cliente": {"nome": "João Silva"},
                "equipamento": {"tipo": "smartphone", "marca": "Samsung"},
                "tecnico_responsavel": "Técnico 1",
                "prioridade": "normal",
                "created_at": "2025-01-08T10:00:00Z"
            },
            {
                "id": "os-2",
                "numero": "OS-002", 
                "status": "em_andamento",
                "cliente": {"nome": "Maria Santos"},
                "equipamento": {"tipo": "notebook", "marca": "Dell"},
                "tecnico_responsavel": "Técnico 2",
                "prioridade": "alta",
                "created_at": "2025-01-08T11:00:00Z"
            },
            {
                "id": "os-3",
                "numero": "OS-003",
                "status": "concluida",
                "cliente": {"nome": "Pedro Costa"},
                "equipamento": {"tipo": "tablet", "marca": "Apple"},
                "tecnico_responsavel": "Técnico 1",
                "prioridade": "normal",
                "created_at": "2025-01-08T12:00:00Z"
            },
            {
                "id": "os-4",
                "numero": "OS-004",
                "status": "aguardando_peca",
                "cliente": {"nome": "Ana Oliveira"},
                "equipamento": {"tipo": "smartphone", "marca": "iPhone"},
                "tecnico_responsavel": "Técnico 3",
                "prioridade": "baixa",
                "created_at": "2025-01-08T13:00:00Z"
            }
        ]
    }

@router.post("/test")
async def criar_ordem_servico_test(os_data: dict):
    """
    ENDPOINT TEMPORÁRIO - Cria OS sem autenticação para testes
    """
    return {
        "id": f"os-{hash(str(os_data)) % 1000}",
        "numero": f"OS-{hash(str(os_data)) % 10000:04d}",
        "status": "aguardando",
        "cliente": os_data.get("cliente", {"nome": "Cliente Teste"}),
        "equipamento": os_data.get("equipamento", {"tipo": "smartphone", "marca": "Teste"}),
        "tecnico_responsavel": "Técnico Teste",
        "prioridade": os_data.get("prioridade", "normal"),
        "valor_total": os_data.get("valor_total", 100.00),
        "created_at": datetime.now().isoformat(),
        "message": "Ordem de serviço criada com sucesso (teste)"
    } 