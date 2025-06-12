"""
Modelos para sistema de Ordem de Serviço - TechZe Diagnóstico
Implementa controle completo do fluxo de trabalho de manutenção
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class StatusOS(str, Enum):
    """Status possíveis da ordem de serviço"""
    ABERTA = "aberta"
    AGUARDANDO_DIAGNOSTICO = "aguardando_diagnostico"
    DIAGNOSTICADA = "diagnosticada"
    AGUARDANDO_APROVACAO = "aguardando_aprovacao"
    APROVADA = "aprovada"
    REJEITADA = "rejeitada"
    EM_ANDAMENTO = "em_andamento"
    AGUARDANDO_PECAS = "aguardando_pecas"
    PAUSADA = "pausada"
    CONCLUIDA = "concluida"
    ENTREGUE = "entregue"
    CANCELADA = "cancelada"


# Alias para compatibilidade com testes e APIs antigas
OSStatus = StatusOS


class PrioridadeOS(str, Enum):
    """Prioridade da ordem de serviço"""
    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"
    CRITICA = "critica"


class TipoServico(str, Enum):
    """Tipos de serviços realizados"""
    DIAGNOSTICO = "diagnostico"
    REPARO = "reparo"
    MANUTENCAO = "manutencao"
    INSTALACAO = "instalacao"
    CONFIGURACAO = "configuracao"
    LIMPEZA = "limpeza"
    UPGRADE = "upgrade"
    RECUPERACAO_DADOS = "recuperacao_dados"
    CONSULTORIA = "consultoria"
    GARANTIA = "garantia"


class StatusPagamento(str, Enum):
    """Status do pagamento"""
    PENDENTE = "pendente"
    PAGO = "pago"
    PARCIAL = "parcial"
    CANCELADO = "cancelado"
    ESTORNADO = "estornado"


class TipoEquipamento(str, Enum):
    """Tipos de equipamentos"""
    DESKTOP = "desktop"
    NOTEBOOK = "notebook"
    TABLET = "tablet"
    SMARTPHONE = "smartphone"
    IMPRESSORA = "impressora"
    MONITOR = "monitor"
    ROTEADOR = "roteador"
    SERVIDOR = "servidor"
    OUTRO = "outro"


# ==========================================
# MODELOS DE DADOS
# ==========================================

class ClienteOS(BaseModel):
    """Dados do cliente para a OS"""
    id: Optional[str] = None
    nome: str = Field(..., min_length=3, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    telefone: str = Field(..., min_length=10, max_length=20)
    whatsapp: Optional[str] = Field(None, min_length=10, max_length=20)
    cpf_cnpj: Optional[str] = Field(None, min_length=11, max_length=18)
    endereco: Optional[str] = Field(None, max_length=300)
    observacoes: Optional[str] = Field(None, max_length=500)


class EquipamentoOS(BaseModel):
    """Dados do equipamento para a OS"""
    id: Optional[str] = None
    tipo: TipoEquipamento
    marca: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=100)
    numero_serie: Optional[str] = Field(None, max_length=100)
    problema_relatado: str = Field(..., min_length=10, max_length=1000)
    estado_fisico: Optional[str] = Field(None, max_length=500)
    acessorios: Optional[List[str]] = Field(default_factory=list)
    senha_acesso: Optional[str] = Field(None, max_length=100)
    backup_necessario: bool = Field(default=False)
    observacoes: Optional[str] = Field(None, max_length=500)


class ServicoPrestado(BaseModel):
    """Serviço prestado na OS"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    descricao: str = Field(..., min_length=3, max_length=500)
    tipo: TipoServico
    tempo_gasto_horas: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=8, decimal_places=2)
    valor_servico: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    data_inicio: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None
    tecnico_responsavel: Optional[str] = None
    observacoes: Optional[str] = Field(None, max_length=1000)
    concluido: bool = Field(default=False)


class PecaUtilizada(BaseModel):
    """Peça utilizada na OS"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item_estoque_id: str
    codigo: str = Field(..., min_length=1, max_length=100)
    nome: str = Field(..., min_length=3, max_length=200)
    quantidade: int = Field(..., ge=1, le=1000)
    valor_unitario: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    valor_total: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    numero_serie: Optional[str] = Field(None, max_length=100)
    garantia_dias: Optional[int] = Field(None, ge=0, le=365)
    
    @model_validator(mode='after')
    def calcular_valor_total(self):
        """Calcula automaticamente o valor total"""
        if self.quantidade and self.valor_unitario:
            self.valor_total = Decimal(str(self.quantidade)) * self.valor_unitario
        return self


class AnotacaoOS(BaseModel):
    """Anotação/observação na OS"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    data: datetime = Field(default_factory=datetime.now)
    usuario: str = Field(..., min_length=3, max_length=100)
    tipo: str = Field(default="observacao")  # observacao, diagnostico, solucao, problema
    titulo: Optional[str] = Field(None, max_length=200)
    conteudo: str = Field(..., min_length=3, max_length=2000)
    anexos: Optional[List[str]] = Field(default_factory=list)  # URLs dos anexos
    visivel_cliente: bool = Field(default=False)


class FotoOS(BaseModel):
    """Foto anexada à OS"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome_arquivo: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., min_length=1, max_length=500)
    tipo: str = Field(default="antes")  # antes, durante, depois, problema, solucao
    descricao: Optional[str] = Field(None, max_length=500)
    data_upload: datetime = Field(default_factory=datetime.now)
    usuario: str = Field(..., min_length=3, max_length=100)


class OrdemServico(BaseModel):
    """Modelo principal da Ordem de Serviço"""
    
    # Identificação
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    numero: str = Field(..., min_length=1, max_length=20)
    numero_sequencial: Optional[int] = None
    
    # Status e controle
    status: StatusOS = Field(default=StatusOS.ABERTA)
    prioridade: PrioridadeOS = Field(default=PrioridadeOS.NORMAL)
    
    # Datas importantes
    data_abertura: datetime = Field(default_factory=datetime.now)
    data_atualizacao: datetime = Field(default_factory=datetime.now)
    data_diagnostico: Optional[datetime] = None
    data_aprovacao_orcamento: Optional[datetime] = None
    data_inicio_servico: Optional[datetime] = None
    data_conclusao: Optional[datetime] = None
    data_entrega: Optional[datetime] = None
    data_prevista_entrega: Optional[datetime] = None
    
    # Relacionamentos
    cliente: ClienteOS
    equipamento: EquipamentoOS
    diagnostico_id: Optional[str] = None
    orcamento_id: Optional[str] = None
    
    # Técnicos e responsáveis
    tecnico_responsavel: Optional[str] = None
    tecnico_diagnostico: Optional[str] = None
    atendente: Optional[str] = None
    usuario_abertura: str = Field(..., min_length=3, max_length=100)
    
    # Serviços e peças
    servicos: List[ServicoPrestado] = Field(default_factory=list)
    pecas: List[PecaUtilizada] = Field(default_factory=list)
    
    # Valores
    valor_servicos: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    valor_pecas: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    desconto: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    valor_total: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    
    # Pagamento
    status_pagamento: StatusPagamento = Field(default=StatusPagamento.PENDENTE)
    valor_pago: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    valor_pendente: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    forma_pagamento: Optional[str] = Field(None, max_length=100)
    
    # Diagnóstico e solução
    diagnostico: Optional[str] = Field(None, max_length=2000)
    solucao_aplicada: Optional[str] = Field(None, max_length=2000)
    tempo_total_horas: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=8, decimal_places=2)
    
    # Garantia
    garantia_dias: int = Field(default=90, ge=0, le=365)
    data_vencimento_garantia: Optional[date] = None
    
    # Observações e anotações
    observacoes_internas: Optional[str] = Field(None, max_length=2000)
    observacoes_cliente: Optional[str] = Field(None, max_length=2000)
    anotacoes: List[AnotacaoOS] = Field(default_factory=list)
    fotos: List[FotoOS] = Field(default_factory=list)
    
    # Avaliação do cliente
    avaliacao_cliente: Optional[int] = Field(None, ge=1, le=5)
    comentario_avaliacao: Optional[str] = Field(None, max_length=1000)
    
    # Controle interno
    ativa: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def atualizar_dados_automaticos(self):
        """Atualiza automaticamente dados calculados"""
        # Atualizar data
        self.data_atualizacao = datetime.now()
        
        # Calcular valor total
        if hasattr(self, 'valor_servicos') and hasattr(self, 'valor_pecas') and hasattr(self, 'desconto'):
            self.valor_total = self.valor_servicos + self.valor_pecas - self.desconto
            
        # Calcular valor pendente
        if hasattr(self, 'valor_total') and hasattr(self, 'valor_pago'):
            self.valor_pendente = self.valor_total - self.valor_pago
            
        return self
    
    def calcular_totais(self):
        """Calcula os totais de serviços e peças"""
        self.valor_servicos = sum(servico.valor_servico for servico in self.servicos)
        self.valor_pecas = sum(peca.valor_total for peca in self.pecas)
        self.tempo_total_horas = sum(servico.tempo_gasto_horas for servico in self.servicos)
    
    def adicionar_anotacao(self, usuario: str, conteudo: str, tipo: str = "observacao", 
                          titulo: Optional[str] = None, visivel_cliente: bool = False):
        """Adiciona uma anotação à OS"""
        anotacao = AnotacaoOS(
            usuario=usuario,
            tipo=tipo,
            titulo=titulo,
            conteudo=conteudo,
            visivel_cliente=visivel_cliente
        )
        self.anotacoes.append(anotacao)


# ==========================================
# SCHEMAS PARA API
# ==========================================

class OrdemServicoCreate(BaseModel):
    """Schema para criação de OS"""
    cliente: ClienteOS
    equipamento: EquipamentoOS
    prioridade: PrioridadeOS = Field(default=PrioridadeOS.NORMAL)
    observacoes_internas: Optional[str] = None
    data_prevista_entrega: Optional[datetime] = None


class OrdemServicoUpdate(BaseModel):
    """Schema para atualização de OS"""
    status: Optional[StatusOS] = None
    prioridade: Optional[PrioridadeOS] = None
    tecnico_responsavel: Optional[str] = None
    diagnostico: Optional[str] = None
    solucao_aplicada: Optional[str] = None
    data_prevista_entrega: Optional[datetime] = None
    observacoes_internas: Optional[str] = None
    observacoes_cliente: Optional[str] = None
    valor_servicos: Optional[Decimal] = None
    valor_pecas: Optional[Decimal] = None
    desconto: Optional[Decimal] = None
    forma_pagamento: Optional[str] = None
    status_pagamento: Optional[StatusPagamento] = None
    avaliacao_cliente: Optional[int] = Field(None, ge=1, le=5)
    comentario_avaliacao: Optional[str] = None
    ativa: Optional[bool] = None


class OrdemServicoResponse(BaseModel):
    """Schema para resposta da API"""
    id: str
    numero: str
    status: StatusOS
    prioridade: PrioridadeOS
    data_abertura: datetime
    data_atualizacao: datetime
    cliente: ClienteOS
    equipamento: EquipamentoOS
    valor_total: Decimal
    status_pagamento: StatusPagamento
    tecnico_responsavel: Optional[str]
    data_prevista_entrega: Optional[datetime]


class OSFiltros(BaseModel):
    """Schema para filtros de busca"""
    status: Optional[StatusOS] = None
    prioridade: Optional[PrioridadeOS] = None
    cliente_nome: Optional[str] = None
    cliente_telefone: Optional[str] = None
    tecnico_responsavel: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    valor_minimo: Optional[Decimal] = None
    valor_maximo: Optional[Decimal] = None
    status_pagamento: Optional[StatusPagamento] = None
    garantia_ativa: Optional[bool] = None
    ativa: bool = True
