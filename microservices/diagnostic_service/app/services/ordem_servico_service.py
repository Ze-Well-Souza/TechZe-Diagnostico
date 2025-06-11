"""
Serviço de Ordem de Serviço - Lógica de negócio para gestão de OS
Responsável por: CRUD, workflow, integrações, notificações
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid
from decimal import Decimal

from ..models.ordem_servico import (
    OrdemServico, OrdemServicoCreate, OrdemServicoUpdate, OrdemServicoResponse,
    StatusOS, PrioridadeOS, TipoServico, StatusPagamento,
    ServicoPrestado, PecaUtilizada, AnotacaoOS, FotoOS, OSFiltros
)
from ..models.orcamento import Orcamento
from ..core.config import get_settings
from ..core.supabase import get_supabase_client
from .estoque_service import EstoqueService

settings = get_settings()

class OrdemServicoService:
    """Service para gestão de ordens de serviço"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.estoque_service = EstoqueService()
        self.table_name = "ordens_servico"
        self.table_anotacoes = "os_anotacoes"
        self.table_fotos = "os_fotos"
        
    async def criar_ordem_servico(
        self, 
        dados: OrdemServicoCreate,
        orcamento_id: Optional[str] = None
    ) -> OrdemServicoResponse:
        """
        Cria uma nova ordem de serviço
        """
        try:
            # Gerar número único da OS
            numero_os = await self._gerar_numero_os()
            
            # Calcular valores iniciais
            valor_total = self._calcular_valor_total(dados.servicos, dados.pecas)
            
            # Preparar dados para inserção
            os_data = {
                "id": str(uuid.uuid4()),
                "numero": numero_os,
                "orcamento_id": orcamento_id,
                "cliente": dados.cliente.model_dump(),
                "equipamento": dados.equipamento.model_dump(),
                "problema_relatado": dados.problema_relatado,
                "diagnostico_inicial": dados.diagnostico_inicial,
                "servicos": [servico.model_dump() for servico in dados.servicos],
                "pecas": [peca.model_dump() for peca in dados.pecas],
                "prioridade": dados.prioridade.value,
                "tipo_servico": dados.tipo_servico.value,
                "tecnico_responsavel": dados.tecnico_responsavel,
                "valor_total": float(valor_total),
                "prazo_estimado": dados.prazo_estimado.isoformat() if dados.prazo_estimado else None,
                "observacoes": dados.observacoes,
                "status": StatusOS.ABERTA.value,
                "status_pagamento": StatusPagamento.PENDENTE.value,
                "criado_em": datetime.now().isoformat(),
                "criado_por": dados.criado_por
            }
            
            # Inserir no banco
            result = self.supabase.table(self.table_name).insert(os_data).execute()
            
            if result.data:
                os_id = result.data[0]["id"]
                
                # Registrar anotação inicial
                await self._adicionar_anotacao(
                    os_id, 
                    "OS criada", 
                    f"Ordem de serviço {numero_os} criada com sucesso",
                    dados.criado_por,
                    visivel_cliente=False
                )
                
                return OrdemServicoResponse.model_validate(result.data[0])
            else:
                raise Exception("Erro ao criar ordem de serviço")
                
        except Exception as e:
            raise Exception(f"Erro ao criar OS: {str(e)}")
    
    async def buscar_ordem_servico(self, os_id: str) -> Optional[OrdemServicoResponse]:
        """Busca uma OS por ID"""
        try:
            result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("id", os_id)\
                .execute()
            
            if result.data:
                os_data = result.data[0]
                
                # Buscar anotações
                anotacoes_result = self.supabase.table(self.table_anotacoes)\
                    .select("*")\
                    .eq("os_id", os_id)\
                    .order("criado_em")\
                    .execute()
                
                # Buscar fotos
                fotos_result = self.supabase.table(self.table_fotos)\
                    .select("*")\
                    .eq("os_id", os_id)\
                    .order("criado_em")\
                    .execute()
                
                os_data["anotacoes"] = anotacoes_result.data
                os_data["fotos"] = fotos_result.data
                
                return OrdemServicoResponse.model_validate(os_data)
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar OS: {str(e)}")
    
    async def buscar_por_numero(self, numero: str) -> Optional[OrdemServicoResponse]:
        """Busca uma OS por número"""
        try:
            result = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("numero", numero)\
                .execute()
            
            if result.data:
                return await self.buscar_ordem_servico(result.data[0]["id"])
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar OS por número: {str(e)}")
    
    async def listar_ordens_servico(
        self, 
        filtros: Optional[OSFiltros] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[OrdemServicoResponse]:
        """Lista OSs com filtros opcionais"""
        try:
            query = self.supabase.table(self.table_name).select("*")
            
            if filtros:
                if filtros.status:
                    query = query.in_("status", [s.value for s in filtros.status])
                
                if filtros.cliente_nome:
                    query = query.ilike("cliente->>nome", f"%{filtros.cliente_nome}%")
                
                if filtros.tecnico_responsavel:
                    query = query.eq("tecnico_responsavel", filtros.tecnico_responsavel)
                
                if filtros.data_inicio:
                    query = query.gte("criado_em", filtros.data_inicio.isoformat())
                
                if filtros.data_fim:
                    query = query.lte("criado_em", filtros.data_fim.isoformat())
                
                if filtros.prioridade:
                    query = query.in_("prioridade", [p.value for p in filtros.prioridade])
                
                if filtros.tipo_servico:
                    query = query.in_("tipo_servico", [t.value for t in filtros.tipo_servico])
            
            query = query.order("criado_em", desc=True)\
                        .range(offset, offset + limit - 1)
            
            result = query.execute()
            return [OrdemServicoResponse.model_validate(item) for item in result.data]
            
        except Exception as e:
            raise Exception(f"Erro ao listar OSs: {str(e)}")
    
    # --- WORKFLOW DE STATUS ---
    
    async def atualizar_status(
        self, 
        os_id: str, 
        novo_status: StatusOS,
        observacoes: str = "",
        usuario: str = ""
    ) -> Optional[OrdemServicoResponse]:
        """Atualiza status da OS com validações de workflow"""
        try:
            # Buscar OS atual
            os_atual = await self.buscar_ordem_servico(os_id)
            if not os_atual:
                return None
            
            # Validar transição de status
            if not self._validar_transicao_status(StatusOS(os_atual.status), novo_status):
                raise Exception(f"Transição de status inválida: {os_atual.status} -> {novo_status.value}")
            
            # Preparar dados de atualização
            update_data = {
                "status": novo_status.value,
                "atualizado_em": datetime.now().isoformat()
            }
            
            # Ações específicas por status
            if novo_status == StatusOS.EM_ANDAMENTO:
                update_data["iniciado_em"] = datetime.now().isoformat()
            
            elif novo_status == StatusOS.AGUARDANDO_PECA:
                # Verificar se há peças em falta
                await self._verificar_disponibilidade_pecas(os_atual.pecas)
            
            elif novo_status == StatusOS.CONCLUIDA:
                update_data["concluido_em"] = datetime.now().isoformat()
                # Dar baixa nas peças utilizadas
                await self._processar_baixa_pecas(os_id, os_atual.pecas, usuario)
            
            elif novo_status == StatusOS.ENTREGUE:
                update_data["entregue_em"] = datetime.now().isoformat()
                update_data["status_pagamento"] = StatusPagamento.PAGO.value
            
            # Atualizar no banco
            result = self.supabase.table(self.table_name)\
                .update(update_data)\
                .eq("id", os_id)\
                .execute()
            
            if result.data:
                # Registrar anotação de mudança de status
                await self._adicionar_anotacao(
                    os_id,
                    f"Status alterado para {novo_status.value}",
                    observacoes or f"Status da OS alterado para {novo_status.value}",
                    usuario,
                    visivel_cliente=True
                )
                
                return OrdemServicoResponse.model_validate(result.data[0])
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao atualizar status: {str(e)}")
    
    async def adicionar_servico(
        self, 
        os_id: str, 
        servico: ServicoPrestado,
        usuario: str = ""
    ) -> Optional[OrdemServicoResponse]:
        """Adiciona um serviço à OS"""
        try:
            os_atual = await self.buscar_ordem_servico(os_id)
            if not os_atual:
                return None
            
            # Adicionar serviço à lista
            servicos_atuais = os_atual.servicos.copy()
            servicos_atuais.append(servico)
            
            # Recalcular valor total
            valor_total = self._calcular_valor_total(servicos_atuais, os_atual.pecas)
            
            update_data = {
                "servicos": [s.model_dump() for s in servicos_atuais],
                "valor_total": float(valor_total),
                "atualizado_em": datetime.now().isoformat()
            }
            
            result = self.supabase.table(self.table_name)\
                .update(update_data)\
                .eq("id", os_id)\
                .execute()
            
            if result.data:
                # Registrar anotação
                await self._adicionar_anotacao(
                    os_id,
                    "Serviço adicionado",
                    f"Serviço '{servico.descricao}' adicionado à OS",
                    usuario,
                    visivel_cliente=False
                )
                
                return OrdemServicoResponse.model_validate(result.data[0])
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao adicionar serviço: {str(e)}")
    
    async def adicionar_peca(
        self, 
        os_id: str, 
        peca: PecaUtilizada,
        usuario: str = ""
    ) -> Optional[OrdemServicoResponse]:
        """Adiciona uma peça à OS"""
        try:
            os_atual = await self.buscar_ordem_servico(os_id)
            if not os_atual:
                return None
            
            # Verificar disponibilidade no estoque
            item_estoque = await self.estoque_service.buscar_item(peca.item_estoque_id)
            if not item_estoque:
                raise Exception("Item não encontrado no estoque")
            
            if item_estoque.quantidade_atual < peca.quantidade:
                raise Exception(f"Quantidade insuficiente no estoque. Disponível: {item_estoque.quantidade_atual}")
            
            # Adicionar peça à lista
            pecas_atuais = os_atual.pecas.copy()
            pecas_atuais.append(peca)
            
            # Recalcular valor total
            valor_total = self._calcular_valor_total(os_atual.servicos, pecas_atuais)
            
            update_data = {
                "pecas": [p.model_dump() for p in pecas_atuais],
                "valor_total": float(valor_total),
                "atualizado_em": datetime.now().isoformat()
            }
            
            result = self.supabase.table(self.table_name)\
                .update(update_data)\
                .eq("id", os_id)\
                .execute()
            
            if result.data:
                # Registrar anotação
                await self._adicionar_anotacao(
                    os_id,
                    "Peça adicionada",
                    f"Peça '{item_estoque.nome}' (Qtd: {peca.quantidade}) adicionada à OS",
                    usuario,
                    visivel_cliente=False
                )
                
                return OrdemServicoResponse.model_validate(result.data[0])
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao adicionar peça: {str(e)}")
    
    # --- ANOTAÇÕES E FOTOS ---
    
    async def adicionar_anotacao(
        self, 
        os_id: str, 
        titulo: str,
        conteudo: str,
        usuario: str,
        visivel_cliente: bool = True
    ) -> AnotacaoOS:
        """Adiciona uma anotação à OS"""
        return await self._adicionar_anotacao(os_id, titulo, conteudo, usuario, visivel_cliente)
    
    async def adicionar_foto(
        self, 
        os_id: str, 
        foto: FotoOS,
        usuario: str
    ) -> FotoOS:
        """Adiciona uma foto à OS"""
        try:
            foto_data = {
                "id": str(uuid.uuid4()),
                "os_id": os_id,
                "categoria": foto.categoria.value,
                "url": foto.url,
                "descricao": foto.descricao,
                "visivel_cliente": foto.visivel_cliente,
                "criado_em": datetime.now().isoformat(),
                "criado_por": usuario
            }
            
            result = self.supabase.table(self.table_fotos).insert(foto_data).execute()
            
            if result.data:
                return FotoOS.model_validate(result.data[0])
            else:
                raise Exception("Erro ao adicionar foto")
                
        except Exception as e:
            raise Exception(f"Erro ao adicionar foto: {str(e)}")
    
    # --- RELATÓRIOS ---
    
    async def gerar_relatorio_os(
        self, 
        filtros: Optional[OSFiltros] = None
    ) -> Dict[str, Any]:
        """Gera relatório estatístico de OSs"""
        try:
            query = self.supabase.table(self.table_name).select("*")
            
            if filtros:
                if filtros.data_inicio:
                    query = query.gte("criado_em", filtros.data_inicio.isoformat())
                if filtros.data_fim:
                    query = query.lte("criado_em", filtros.data_fim.isoformat())
            
            result = query.execute()
            ordens = result.data
            
            total_os = len(ordens)
            
            if total_os == 0:
                return {
                    "total_os": 0,
                    "valor_total": 0,
                    "ticket_medio": 0,
                    "status_distribuicao": {},
                    "tempo_medio_resolucao": 0
                }
            
            # Estatísticas básicas
            status_count = {}
            valor_total = 0
            tempos_resolucao = []
            
            for os in ordens:
                status = os["status"]
                status_count[status] = status_count.get(status, 0) + 1
                valor_total += os["valor_total"]
                
                # Calcular tempo de resolução para OSs concluídas
                if os["concluido_em"]:
                    criado = datetime.fromisoformat(os["criado_em"])
                    concluido = datetime.fromisoformat(os["concluido_em"])
                    tempo_resolucao = (concluido - criado).total_seconds() / 3600  # em horas
                    tempos_resolucao.append(tempo_resolucao)
            
            ticket_medio = valor_total / total_os
            tempo_medio = sum(tempos_resolucao) / len(tempos_resolucao) if tempos_resolucao else 0
            
            return {
                "total_os": total_os,
                "valor_total": valor_total,
                "ticket_medio": ticket_medio,
                "status_distribuicao": status_count,
                "tempo_medio_resolucao": tempo_medio,
                "os_concluidas": len(tempos_resolucao),
                "periodo": {
                    "inicio": filtros.data_inicio.isoformat() if filtros and filtros.data_inicio else None,
                    "fim": filtros.data_fim.isoformat() if filtros and filtros.data_fim else None
                }
            }
            
        except Exception as e:
            raise Exception(f"Erro ao gerar relatório: {str(e)}")
    
    # --- MÉTODOS AUXILIARES ---
    
    async def _gerar_numero_os(self) -> str:
        """Gera número único para a OS"""
        ano_atual = datetime.now().year
        
        result = self.supabase.table(self.table_name)\
            .select("numero")\
            .ilike("numero", f"OS{ano_atual}%")\
            .order("numero", desc=True)\
            .limit(1)\
            .execute()
        
        if result.data:
            ultimo_numero = result.data[0]["numero"]
            sequencial = int(ultimo_numero.split("-")[-1]) + 1
        else:
            sequencial = 1
        
        return f"OS{ano_atual}-{sequencial:06d}"
    
    def _calcular_valor_total(self, servicos: List, pecas: List) -> Decimal:
        """Calcula valor total da OS"""
        total = Decimal("0")
        
        for servico in servicos:
            if hasattr(servico, 'valor_total'):
                total += Decimal(str(servico.valor_total))
        
        for peca in pecas:
            if hasattr(peca, 'preco_venda') and hasattr(peca, 'quantidade'):
                total += Decimal(str(peca.preco_venda)) * Decimal(str(peca.quantidade))
        
        return total
    
    def _validar_transicao_status(self, status_atual: StatusOS, novo_status: StatusOS) -> bool:
        """Valida se a transição de status é permitida"""
        transicoes_validas = {
            StatusOS.ABERTA: [StatusOS.EM_ANDAMENTO, StatusOS.CANCELADA],
            StatusOS.EM_ANDAMENTO: [StatusOS.AGUARDANDO_PECA, StatusOS.AGUARDANDO_CLIENTE, StatusOS.CONCLUIDA, StatusOS.CANCELADA],
            StatusOS.AGUARDANDO_PECA: [StatusOS.EM_ANDAMENTO, StatusOS.CANCELADA],
            StatusOS.AGUARDANDO_CLIENTE: [StatusOS.EM_ANDAMENTO, StatusOS.CANCELADA],
            StatusOS.CONCLUIDA: [StatusOS.ENTREGUE],
            StatusOS.ENTREGUE: [],  # Status final
            StatusOS.CANCELADA: []  # Status final
        }
        
        return novo_status in transicoes_validas.get(status_atual, [])
    
    async def _verificar_disponibilidade_pecas(self, pecas: List[PecaUtilizada]) -> None:
        """Verifica se há peças suficientes no estoque"""
        for peca in pecas:
            item = await self.estoque_service.buscar_item(peca.item_estoque_id)
            if not item or item.quantidade_atual < peca.quantidade:
                raise Exception(f"Peça {peca.item_estoque_id} indisponível no estoque")
    
    async def _processar_baixa_pecas(self, os_id: str, pecas: List[PecaUtilizada], usuario: str) -> None:
        """Processa baixa das peças utilizadas no estoque"""
        for peca in pecas:
            await self.estoque_service.saida_estoque(
                item_id=peca.item_estoque_id,
                quantidade=peca.quantidade,
                observacoes=f"Utilizada na OS {os_id}",
                usuario=usuario,
                ordem_servico_id=os_id
            )
    
    async def _adicionar_anotacao(
        self, 
        os_id: str, 
        titulo: str,
        conteudo: str,
        usuario: str,
        visivel_cliente: bool = True
    ) -> AnotacaoOS:
        """Método interno para adicionar anotação"""
        try:
            anotacao_data = {
                "id": str(uuid.uuid4()),
                "os_id": os_id,
                "titulo": titulo,
                "conteudo": conteudo,
                "visivel_cliente": visivel_cliente,
                "criado_em": datetime.now().isoformat(),
                "criado_por": usuario
            }
            
            result = self.supabase.table(self.table_anotacoes).insert(anotacao_data).execute()
            
            if result.data:
                return AnotacaoOS.model_validate(result.data[0])
            else:
                raise Exception("Erro ao adicionar anotação")
                
        except Exception as e:
            raise Exception(f"Erro ao adicionar anotação: {str(e)}") 