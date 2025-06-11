"""
Serviço de Orçamentos - Lógica de negócio para gestão de orçamentos
Responsável por: CRUD, validações, cálculos automáticos, aprovações
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
import uuid
from decimal import Decimal
import logging

from ..models.orcamento import (
    Orcamento, OrcamentoCreate, OrcamentoUpdate, OrcamentoResponse,
    OrcamentoDetalhado, OrcamentoAprovacao, OrcamentoFiltros,
    StatusOrcamento, PrioridadeOrcamento, ItemOrcamento, PecaOrcamento,
    DadosCliente, DadosEquipamento, CondicoesPagamento
)
from ..core.config import get_settings
from ..db.repositories.orcamento_repository import OrcamentoRepository

logger = logging.getLogger(__name__)
settings = get_settings()

class OrcamentoService:
    """Service para gestão de orçamentos"""
    
    def __init__(self):
        self.repository = OrcamentoRepository()
        
    async def criar_orcamento(
        self, 
        dados: OrcamentoCreate,
        diagnostic_id: Optional[str] = None
    ) -> OrcamentoResponse:
        """
        Cria um novo orçamento com validações e cálculos automáticos
        """
        try:
            logger.info(f"Iniciando criação de orçamento para cliente: {dados.cliente.nome}")
            
            # Gerar número único do orçamento
            numero_orcamento = await self.repository.gerar_proximo_numero()
            
            # Calcular valores automáticos
            subtotal_servicos = self._calcular_subtotal_servicos(dados.servicos)
            subtotal_pecas = self._calcular_subtotal_pecas(dados.pecas)
            valor_total = subtotal_servicos + subtotal_pecas
            
            # Aplicar desconto se houver
            desconto_valor = Decimal('0.00')
            if dados.condicoes_pagamento and dados.condicoes_pagamento.desconto_porcentagem:
                desconto_valor = (valor_total * dados.condicoes_pagamento.desconto_porcentagem) / 100
            
            valor_final = valor_total - desconto_valor
            
            # Criar instância do orçamento
            orcamento = Orcamento(
                numero=numero_orcamento,
                cliente=dados.cliente,
                equipamento=dados.equipamento,
                servicos=dados.servicos or [],
                pecas=dados.pecas or [],
                subtotal_servicos=subtotal_servicos,
                subtotal_pecas=subtotal_pecas,
                desconto_total=desconto_valor,
                valor_total=valor_final,
                condicoes_pagamento=dados.condicoes_pagamento or CondicoesPagamento(),
                observacoes=dados.observacoes,
                prazo_execucao_dias=dados.prazo_execucao_dias,
                garantia_dias=dados.garantia_dias,
                data_validade=dados.data_validade,
                diagnostico_id=diagnostic_id,
                status=StatusOrcamento.RASCUNHO
            )
            
            # Preparar dados para inserção no banco
            orcamento_data = {
                "id": orcamento.id,
                "numero": orcamento.numero,
                "status": orcamento.status.value,
                "prioridade": orcamento.prioridade.value,
                "dados_cliente": orcamento.cliente.model_dump(),
                "dados_equipamento": orcamento.equipamento.model_dump(),
                "observacoes": orcamento.observacoes,
                "valor_pecas": float(orcamento.subtotal_pecas),
                "valor_servicos": float(orcamento.subtotal_servicos),
                "valor_desconto": float(orcamento.desconto_total),
                "valor_total": float(orcamento.valor_total),
                "data_validade": orcamento.data_validade.isoformat() if orcamento.data_validade else None,
                "condicoes_pagamento": orcamento.condicoes_pagamento.model_dump(),
                "tempo_estimado": orcamento.prazo_execucao_dias * 8,  # 8h por dia
                "garantia_dias": orcamento.garantia_dias,
                "diagnostico_id": diagnostic_id
            }
            
            # Inserir no banco via repository
            result = await self.repository.create(orcamento_data)
            
            if result:
                logger.info(f"Orçamento criado com sucesso: {numero_orcamento}")
                return OrcamentoResponse(
                    id=result.id,
                    numero=result.numero,
                    status=StatusOrcamento(result.status),
                    prioridade=PrioridadeOrcamento(result.prioridade),
                    data_criacao=result.data_criacao,
                    data_atualizacao=result.data_atualizacao,
                    cliente=result.cliente,
                    equipamento=result.equipamento,
                    valor_total=result.valor_total,
                    prazo_execucao_dias=result.prazo_execucao_dias,
                    garantia_dias=result.garantia_dias,
                    data_validade=result.data_validade,
                    ativo=result.ativo
                )
            else:
                raise Exception("Falha ao inserir orçamento no banco de dados")
                
        except Exception as e:
            logger.error(f"Erro ao criar orçamento: {str(e)}")
            raise Exception(f"Erro ao criar orçamento: {str(e)}")
    
    async def buscar_orcamento(self, orcamento_id: str) -> Optional[OrcamentoDetalhado]:
        """
        Busca um orçamento por ID
        """
        try:
            result = await self.repository.get_by_id(orcamento_id)
            
            if result:
                # Converter para OrcamentoDetalhado se necessário
                return OrcamentoDetalhado.model_validate(result.model_dump())
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar orçamento {orcamento_id}: {str(e)}")
            raise Exception(f"Erro ao buscar orçamento: {str(e)}")
    
    async def listar_orcamentos(
        self, 
        filtros: Optional[OrcamentoFiltros] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[OrcamentoResponse]:
        """
        Lista orçamentos com filtros opcionais
        """
        try:
            # Se há filtros específicos, usar método especializado do repository
            if filtros:
                result = await self.repository.listar_com_filtros(filtros)
            else:
                # Listar todos com paginação simples
                result = await self.repository.list_all(limit=limit, offset=offset)
            
            # Converter para OrcamentoResponse
            return [
                OrcamentoResponse(
                    id=item.id,
                    numero=item.numero,
                    status=StatusOrcamento(item.status),
                    prioridade=PrioridadeOrcamento(item.prioridade),
                    data_criacao=item.data_criacao,
                    data_atualizacao=item.data_atualizacao,
                    cliente=item.cliente,
                    equipamento=item.equipamento,
                    valor_total=item.valor_total,
                    prazo_execucao_dias=item.prazo_execucao_dias,
                    garantia_dias=item.garantia_dias,
                    data_validade=item.data_validade,
                    ativo=item.ativo
                ) for item in result
            ]
            
        except Exception as e:
            logger.error(f"Erro ao listar orçamentos: {str(e)}")
            raise Exception(f"Erro ao listar orçamentos: {str(e)}")
    
    async def atualizar_orcamento(
        self, 
        orcamento_id: str, 
        dados: OrcamentoUpdate
    ) -> Optional[OrcamentoResponse]:
        """
        Atualiza um orçamento existente
        """
        try:
            # Buscar orçamento atual
            orcamento_atual = await self.buscar_orcamento(orcamento_id)
            if not orcamento_atual:
                return None
            
            # Verificar se pode ser editado
            if orcamento_atual.status in [StatusOrcamento.APROVADO, StatusOrcamento.REJEITADO]:
                raise Exception("Orçamento já aprovado/rejeitado não pode ser editado")
            
            # Preparar dados para atualização
            update_data = {}
            
            if dados.itens is not None:
                update_data["itens"] = [item.model_dump() for item in dados.itens]
            
            if dados.pecas is not None:
                update_data["pecas"] = [peca.model_dump() for peca in dados.pecas]
            
            if dados.condicoes_pagamento is not None:
                update_data["condicoes_pagamento"] = dados.condicoes_pagamento.model_dump()
            
            if dados.observacoes is not None:
                update_data["observacoes"] = dados.observacoes
            
            if dados.prioridade is not None:
                update_data["prioridade"] = dados.prioridade.value
            
            # Recalcular valores se itens/peças foram alterados
            if dados.itens is not None or dados.pecas is not None:
                itens = dados.itens if dados.itens is not None else orcamento_atual.itens
                pecas = dados.pecas if dados.pecas is not None else orcamento_atual.pecas
                
                valor_total = self._calcular_valor_total(itens + pecas)
                desconto = dados.condicoes_pagamento.desconto_percentual if dados.condicoes_pagamento else orcamento_atual.condicoes_pagamento.desconto_percentual
                valor_desconto = self._aplicar_desconto(valor_total, desconto)
                valor_final = valor_total - valor_desconto
                
                update_data.update({
                    "valor_total": float(valor_total),
                    "valor_desconto": float(valor_desconto),
                    "valor_final": float(valor_final)
                })
            
            update_data["atualizado_em"] = datetime.now().isoformat()
            
            # Atualizar no banco via repository
            result = await self.repository.update(orcamento_id, update_data)
            
            if result:
                return OrcamentoResponse(
                    id=result.id,
                    numero=result.numero,
                    status=StatusOrcamento(result.status),
                    prioridade=PrioridadeOrcamento(result.prioridade),
                    data_criacao=result.data_criacao,
                    data_atualizacao=result.data_atualizacao,
                    cliente=result.cliente,
                    equipamento=result.equipamento,
                    valor_total=result.valor_total,
                    prazo_execucao_dias=result.prazo_execucao_dias,
                    garantia_dias=result.garantia_dias,
                    data_validade=result.data_validade,
                    ativo=result.ativo
                )
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao atualizar orçamento: {str(e)}")
    
    async def aprovar_orcamento(
        self, 
        orcamento_id: str, 
        aprovacao: OrcamentoAprovacao
    ) -> Optional[OrcamentoResponse]:
        """
        Aprova um orçamento
        """
        try:
            update_data = {
                "status": StatusOrcamento.APROVADO.value,
                "aprovado_em": datetime.now().isoformat(),
                "aprovado_por": aprovacao.aprovado_por,
                "observacoes_aprovacao": aprovacao.observacoes,
                "assinatura_digital": aprovacao.assinatura_digital
            }
            
            # Usar método específico do repository para aprovação
            success = await self.repository.aprovar_orcamento(
                orcamento_id=orcamento_id,
                assinatura_digital=aprovacao.assinatura_digital or "",
                ip_aprovacao=aprovacao.ip_aprovacao or ""
            )
            
            if success:
                # Buscar orçamento atualizado
                orcamento_atualizado = await self.repository.get_by_id(orcamento_id)
                if orcamento_atualizado:
                    # Aqui poderia disparar notificações, criar OS automática, etc.
                    await self._processar_aprovacao(orcamento_atualizado.model_dump())
                    return OrcamentoResponse(
                        id=orcamento_atualizado.id,
                        numero=orcamento_atualizado.numero,
                        status=StatusOrcamento(orcamento_atualizado.status),
                        prioridade=PrioridadeOrcamento(orcamento_atualizado.prioridade),
                        data_criacao=orcamento_atualizado.data_criacao,
                        data_atualizacao=orcamento_atualizado.data_atualizacao,
                        cliente=orcamento_atualizado.cliente,
                        equipamento=orcamento_atualizado.equipamento,
                        valor_total=orcamento_atualizado.valor_total,
                        prazo_execucao_dias=orcamento_atualizado.prazo_execucao_dias,
                        garantia_dias=orcamento_atualizado.garantia_dias,
                        data_validade=orcamento_atualizado.data_validade,
                        ativo=orcamento_atualizado.ativo
                    )
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao aprovar orçamento: {str(e)}")
    
    async def rejeitar_orcamento(
        self, 
        orcamento_id: str, 
        motivo: str,
        rejeitado_por: str
    ) -> Optional[OrcamentoResponse]:
        """
        Rejeita um orçamento
        """
        try:
            update_data = {
                "status": StatusOrcamento.REJEITADO.value,
                "rejeitado_em": datetime.now().isoformat(),
                "rejeitado_por": rejeitado_por,
                "motivo_rejeicao": motivo
            }
            
            # Usar método específico do repository para rejeição
            success = await self.repository.rejeitar_orcamento(orcamento_id)
            
            if success:
                # Buscar orçamento atualizado
                orcamento_atualizado = await self.repository.get_by_id(orcamento_id)
                if orcamento_atualizado:
                    return OrcamentoResponse(
                        id=orcamento_atualizado.id,
                        numero=orcamento_atualizado.numero,
                        status=StatusOrcamento(orcamento_atualizado.status),
                        prioridade=PrioridadeOrcamento(orcamento_atualizado.prioridade),
                        data_criacao=orcamento_atualizado.data_criacao,
                        data_atualizacao=orcamento_atualizado.data_atualizacao,
                        cliente=orcamento_atualizado.cliente,
                        equipamento=orcamento_atualizado.equipamento,
                        valor_total=orcamento_atualizado.valor_total,
                        prazo_execucao_dias=orcamento_atualizado.prazo_execucao_dias,
                        garantia_dias=orcamento_atualizado.garantia_dias,
                        data_validade=orcamento_atualizado.data_validade,
                        ativo=orcamento_atualizado.ativo
                    )
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao rejeitar orçamento: {str(e)}")
    
    async def gerar_relatorio_orcamentos(
        self, 
        filtros: Optional[OrcamentoFiltros] = None
    ) -> Dict[str, Any]:
        """
        Gera relatório estatístico de orçamentos
        """
        try:
            # Base query
            query = self.supabase.table(self.table_name).select("*")
            
            # Aplicar filtros se fornecidos
            if filtros:
                if filtros.data_inicio:
                    query = query.gte("criado_em", filtros.data_inicio.isoformat())
                if filtros.data_fim:
                    query = query.lte("criado_em", filtros.data_fim.isoformat())
            
            result = query.execute()
            orcamentos = result.data
            
            # Calcular estatísticas
            total_orcamentos = len(orcamentos)
            
            if total_orcamentos == 0:
                return {
                    "total_orcamentos": 0,
                    "valor_total": 0,
                    "valor_medio": 0,
                    "status_distribuicao": {},
                    "taxa_aprovacao": 0
                }
            
            # Distribuição por status
            status_count = {}
            valor_total = 0
            aprovados = 0
            
            for orcamento in orcamentos:
                status = orcamento["status"]
                status_count[status] = status_count.get(status, 0) + 1
                valor_total += orcamento["valor_final"]
                
                if status == StatusOrcamento.APROVADO.value:
                    aprovados += 1
            
            valor_medio = valor_total / total_orcamentos
            taxa_aprovacao = (aprovados / total_orcamentos) * 100
            
            return {
                "total_orcamentos": total_orcamentos,
                "valor_total": valor_total,
                "valor_medio": valor_medio,
                "status_distribuicao": status_count,
                "taxa_aprovacao": taxa_aprovacao,
                "orcamentos_aprovados": aprovados,
                "periodo": {
                    "inicio": filtros.data_inicio.isoformat() if filtros and filtros.data_inicio else None,
                    "fim": filtros.data_fim.isoformat() if filtros and filtros.data_fim else None
                }
            }
            
        except Exception as e:
            raise Exception(f"Erro ao gerar relatório: {str(e)}")
    
    # Métodos auxiliares privados
    
    async def _gerar_numero_orcamento(self) -> str:
        """Gera número único para o orçamento"""
        ano_atual = datetime.now().year
        
        # Buscar último número do ano
        result = self.supabase.table(self.table_name)\
            .select("numero")\
            .ilike("numero", f"ORC{ano_atual}%")\
            .order("numero", desc=True)\
            .limit(1)\
            .execute()
        
        if result.data:
            ultimo_numero = result.data[0]["numero"]
            sequencial = int(ultimo_numero.split("-")[-1]) + 1
        else:
            sequencial = 1
        
        return f"ORC{ano_atual}-{sequencial:06d}"
    
    def _calcular_subtotal_servicos(self, servicos: List[ItemOrcamento]) -> Decimal:
        """Calcula o subtotal dos serviços"""
        if not servicos:
            return Decimal('0.00')
        
        total = Decimal('0.00')
        for servico in servicos:
            total += servico.valor_total
        return total
    
    def _calcular_subtotal_pecas(self, pecas: List[PecaOrcamento]) -> Decimal:
        """Calcula o subtotal das peças"""
        if not pecas:
            return Decimal('0.00')
        
        total = Decimal('0.00')
        for peca in pecas:
            total += peca.valor_total
        return total
    
    def _calcular_valor_total(self, itens: List) -> Decimal:
        """Calcula valor total dos itens (método legacy)"""
        total = Decimal("0")
        for item in itens:
            if hasattr(item, 'valor_total'):
                total += Decimal(str(item.valor_total))
            elif hasattr(item, 'preco_venda') and hasattr(item, 'quantidade'):
                total += Decimal(str(item.preco_venda)) * Decimal(str(item.quantidade))
        return total
    
    def _aplicar_desconto(self, valor: Decimal, desconto_percentual: float) -> Decimal:
        """Aplica desconto percentual"""
        if desconto_percentual > 0:
            return valor * (Decimal(str(desconto_percentual)) / Decimal("100"))
        return Decimal("0")
    
    async def _processar_aprovacao(self, orcamento_data: Dict[str, Any]) -> None:
        """Processa pós-aprovação do orçamento"""
        try:
            # Aqui poderiam ser implementadas ações como:
            # - Criar ordem de serviço automaticamente
            # - Enviar notificações
            # - Reservar peças no estoque
            # - Enviar por WhatsApp/Email
            pass
        except Exception as e:
            # Log do erro mas não falha a aprovação
            print(f"Erro no pós-processamento da aprovação: {str(e)}") 