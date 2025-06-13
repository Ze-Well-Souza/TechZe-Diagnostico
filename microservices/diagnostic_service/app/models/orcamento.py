"""
Modelos para sistema de orçamentos - TechZe Diagnóstico
Implementa orçamentação completa para loja de manutenção
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any, Union, Annotated
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class StatusOrcamento(str, Enum):
    """Status possíveis do orçamento"""
    RASCUNHO = "rascunho"
    PENDENTE = "pendente"
    ENVIADO = "enviado"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    CANCELADO = "cancelado"
    EXPIRADO = "expirado"


# Alias para compatibilidade com testes e APIs antigas
OrcamentoStatus = StatusOrcamento


class TipoServico(str, Enum):
    """Tipos de serviços oferecidos"""
    DIAGNOSTICO = "diagnostico"
    REPARO_HARDWARE = "reparo_hardware"
    REPARO_SOFTWARE = "reparo_software"
    MANUTENCAO = "manutencao"
    INSTALACAO = "instalacao"
    CONFIGURACAO = "configuracao"
    RECUPERACAO_DADOS = "recuperacao_dados"
    LIMPEZA = "limpeza"
    UPGRADE = "upgrade"
    CONSULTORIA = "consultoria"
    # Compatibilidade com suíte de testes legacy
    SERVICO = "servico"


class TipoPeca(str, Enum):
    """Tipos de peças para orçamento"""
    HARDWARE = "hardware"
    SOFTWARE = "software"
    ACESSORIO = "acessorio"
    CONSUMIVEL = "consumivel"


class PrioridadeOrcamento(str, Enum):
    """Prioridade do orçamento"""
    BAIXA = "baixa"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"


# ==========================================
# MODELOS DE DADOS
# ==========================================

class ItemOrcamento(BaseModel):
    """Item individual do orçamento"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    descricao: str = Field(..., min_length=3, max_length=500)
    tipo: TipoServico
    quantidade: int = Field(default=1, ge=1, le=1000)
    valor_unitario: Annotated[Decimal, Field(ge=0)]
    valor_total: Annotated[Decimal, Field(default=Decimal('0.00'), ge=0)]
    tempo_estimado_horas: Optional[float] = Field(None, ge=0, le=10000, alias="tempo_estimado")
    observacoes: Optional[str] = Field(None, max_length=1000)
    codigo_interno: Optional[str] = Field(None, max_length=50)
    garantia_dias: Optional[int] = Field(None, ge=0, le=365)
    
    @model_validator(mode='after')
    def calcular_valor_total(self):
        """Calcula automaticamente o valor total"""
        if self.quantidade and self.valor_unitario:
            self.valor_total = Decimal(str(self.quantidade)) * self.valor_unitario
        return self

    class Config:
        allow_population_by_field_name = True


class PecaOrcamento(BaseModel):
    """Peça utilizada no orçamento"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    codigo: str = Field(..., min_length=1, max_length=100, alias="codigo_peca")
    nome: str = Field(..., min_length=3, max_length=200, alias="nome_peca")
    descricao: Optional[str] = Field(None, max_length=500)
    tipo: TipoPeca = Field(default=TipoPeca.HARDWARE)
    quantidade: int = Field(..., ge=1, le=1000)
    valor_unitario: Decimal = Field(..., ge=0)
    valor_total: Decimal = Field(default=Decimal('0.00'), ge=0)
    fornecedor: Optional[str] = Field(None, max_length=100)
    tempo_entrega_dias: Optional[int] = Field(None, ge=0, le=90)
    garantia_dias: Optional[int] = Field(None, ge=0, le=365)
    
    @model_validator(mode='after')
    def calcular_valor_total(self):
        """Calcula automaticamente o valor total"""
        if self.quantidade and self.valor_unitario:
            self.valor_total = Decimal(str(self.quantidade)) * self.valor_unitario
        return self

    class Config:
        allow_population_by_field_name = True


class DadosCliente(BaseModel):
    """Dados do cliente para o orçamento"""
    id: Optional[str] = None
    nome: str = Field(..., min_length=3, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    telefone: str = Field(..., min_length=10, max_length=20)
    whatsapp: Optional[str] = Field(None, min_length=10, max_length=20)
    cpf_cnpj: Optional[str] = Field(None, min_length=11, max_length=18)
    # Testes enviam dict, portanto aceitar Any
    endereco: Optional[Any] = Field(None, description="Endereço pode ser string ou objeto", json_schema_extra={"example": "Rua A, 123"})
    observacoes: Optional[str] = Field(None, max_length=500)


class DadosEquipamento(BaseModel):
    """Dados do equipamento para orçamento"""
    id: Optional[str] = None
    tipo: str = Field(..., min_length=3, max_length=50)
    marca: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=100)
    numero_serie: Optional[str] = Field(None, max_length=100)
    # Campo principal - reduzindo min_length de 10 para 5 para ser mais flexível
    problema_relatado: str = Field(..., min_length=5, max_length=1000)
    # Campo alias para compatibilidade com testes legacy 
    descricao_problema: Optional[str] = Field(None, min_length=5, max_length=1000)
    estado_fisico: Optional[str] = Field(None, max_length=500)
    acessorios: Optional[List[str]] = Field(default_factory=list)
    observacoes: Optional[str] = Field(None, max_length=500)

    class Config:
        allow_population_by_field_name = True
    
    def __init__(self, **data):
        # Se descricao_problema foi passado e problema_relatado não, usar descricao_problema
        if 'descricao_problema' in data and 'problema_relatado' not in data:
            data['problema_relatado'] = data['descricao_problema']
        # Se problema_relatado foi passado e descricao_problema não, usar problema_relatado  
        elif 'problema_relatado' in data and 'descricao_problema' not in data:
            data['descricao_problema'] = data['problema_relatado']
        super().__init__(**data)


class CondicoesPagamento(BaseModel):
    """Condições de pagamento do orçamento"""
    forma_pagamento: List[str] | str = Field(default_factory=lambda: ["dinheiro", "pix", "cartao"], alias="forma_pagamento")
    condicoes: str = Field(default="À vista")
    desconto_porcentagem: Annotated[Decimal | None, Field(None, ge=0, le=100)]
    desconto_valor: Annotated[Decimal | None, Field(None, ge=0)]
    prazo_dias: Optional[int] = Field(None, ge=0, alias="prazo_dias")
    entrada_valor: Annotated[Decimal | None, Field(None, ge=0)]
    parcelas: Optional[int] = Field(None, ge=1, le=12)
    valor_parcela: Annotated[Decimal | None, Field(None, ge=0)]
    juros_mes: Annotated[Decimal | None, Field(None, ge=0, le=10)]

    @field_validator('forma_pagamento', mode='before')
    @classmethod
    def ensure_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v

    class Config:
        allow_population_by_field_name = True


class Orcamento(BaseModel):
    """Modelo principal do orçamento"""
    
    # Identificação
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    numero: str = Field(..., min_length=1, max_length=20)
    
    # Status e controle
    status: StatusOrcamento = Field(default=StatusOrcamento.RASCUNHO)
    prioridade: PrioridadeOrcamento = Field(default=PrioridadeOrcamento.NORMAL)
    
    # Datas
    data_criacao: datetime = Field(default_factory=datetime.now)
    data_atualizacao: datetime = Field(default_factory=datetime.now)
    data_envio: Optional[datetime] = None
    data_validade: Optional[date] = None
    data_aprovacao: Optional[datetime] = None
    data_rejeicao: Optional[datetime] = None
    
    # Relacionamentos
    cliente: DadosCliente
    equipamento: DadosEquipamento
    diagnostico_id: Optional[str] = None
    ordem_servico_id: Optional[str] = None
    tecnico_responsavel: Optional[str] = None
    
    # Itens e peças
    servicos: List[ItemOrcamento] = Field(default_factory=list)
    pecas: List[PecaOrcamento] = Field(default_factory=list)
    
    # Valores
    subtotal_servicos: Annotated[Decimal, Field(default=Decimal('0.00'), ge=0)]
    subtotal_pecas: Annotated[Decimal, Field(default=Decimal('0.00'), ge=0)]
    desconto_total: Annotated[Decimal, Field(default=Decimal('0.00'), ge=0)]
    valor_total: Annotated[Decimal, Field(default=Decimal('0.00'), ge=0)]
    
    # Condições
    condicoes_pagamento: CondicoesPagamento = Field(default_factory=CondicoesPagamento)
    prazo_execucao_dias: int = Field(default=7, ge=1, le=90)
    garantia_dias: int = Field(default=90, ge=0, le=365)
    
    # Observações e informações adicionais
    observacoes: Optional[str] = Field(None, max_length=2000)
    condicoes_gerais: Optional[str] = Field(None, max_length=2000)
    motivo_rejeicao: Optional[str] = Field(None, max_length=500)
    
    # Dados de aprovação
    aprovado_por: Optional[str] = None
    ip_aprovacao: Optional[str] = None
    assinatura_digital: Optional[str] = None
    
    # Controle interno
    versao: int = Field(default=1)
    ativo: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def atualizar_data_modificacao_e_calcular_valor(self):
        """Atualiza automaticamente a data de modificação e calcula valor total"""
        # Atualizar data
        self.data_atualizacao = datetime.now()
        
        # Calcular valor total
        if hasattr(self, 'subtotal_servicos') and hasattr(self, 'subtotal_pecas') and hasattr(self, 'desconto_total'):
            self.valor_total = self.subtotal_servicos + self.subtotal_pecas - self.desconto_total
        
        return self
    
    def calcular_subtotais(self):
        """Calcula os subtotais de serviços e peças"""
        self.subtotal_servicos = sum(item.valor_total for item in self.servicos)
        self.subtotal_pecas = sum(peca.valor_total for peca in self.pecas)
        
    def aplicar_desconto(self, porcentagem: Optional[Decimal] = None, valor: Optional[Decimal] = None):
        """Aplica desconto ao orçamento"""
        if porcentagem:
            total_base = self.subtotal_servicos + self.subtotal_pecas
            self.desconto_total = total_base * (porcentagem / Decimal('100'))
            self.condicoes_pagamento.desconto_porcentagem = porcentagem
        elif valor:
            self.desconto_total = valor
            self.condicoes_pagamento.desconto_valor = valor
            
    def aprovar(self, aprovado_por: str, ip: Optional[str] = None, assinatura: Optional[str] = None):
        """Aprova o orçamento"""
        self.status = StatusOrcamento.APROVADO
        self.data_aprovacao = datetime.now()
        self.aprovado_por = aprovado_por
        if ip:
            self.ip_aprovacao = ip
        if assinatura:
            self.assinatura_digital = assinatura
            
    def rejeitar(self, motivo: str):
        """Rejeita o orçamento"""
        self.status = StatusOrcamento.REJEITADO
        self.data_rejeicao = datetime.now()
        self.motivo_rejeicao = motivo
        
    def enviar(self):
        """Envia o orçamento para o cliente"""
        self.status = StatusOrcamento.ENVIADO
        self.data_envio = datetime.now()
        
    def verificar_validade(self) -> bool:
        """Verifica se o orçamento ainda está válido"""
        if self.data_validade:
            return date.today() <= self.data_validade
        return True


# ==========================================
# SCHEMAS PARA API
# ==========================================

class OrcamentoCreate(BaseModel):
    """Schema para criação de orçamento"""
    cliente: DadosCliente
    equipamento: DadosEquipamento
    itens: Optional[List[ItemOrcamento]] = Field(default_factory=list, alias="itens")
    servicos: List[ItemOrcamento] = Field(default_factory=list)
    pecas: List[PecaOrcamento] = Field(default_factory=list)
    condicoes_pagamento: Optional[CondicoesPagamento] = None
    observacoes: Optional[str] = None
    prazo_execucao_dias: int = Field(default=7)
    garantia_dias: int = Field(default=90)
    data_validade: Optional[date] = None
    diagnostico_id: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class OrcamentoUpdate(BaseModel):
    """Schema para atualização de orçamento"""
    # Compatibilidade com nomenclatura antiga da suíte (itens/pecas) e nova (servicos/pecas)
    itens: Optional[List[ItemOrcamento]] = None
    servicos: Optional[List[ItemOrcamento]] = None  # alias
    pecas: Optional[List[PecaOrcamento]] = None
    condicoes_pagamento: Optional[CondicoesPagamento] = None
    observacoes: Optional[str] = None
    prazo_execucao_dias: Optional[int] = None
    garantia_dias: Optional[int] = None
    data_validade: Optional[date] = None
    prioridade: Optional[PrioridadeOrcamento] = None

    class Config:
        allow_population_by_field_name = True


class OrcamentoResponse(BaseModel):
    """Schema para resposta da API"""
    id: str
    numero: str
    status: StatusOrcamento
    prioridade: PrioridadeOrcamento
    data_criacao: datetime
    data_atualizacao: datetime
    cliente: DadosCliente
    equipamento: DadosEquipamento
    valor_total: Decimal
    prazo_execucao_dias: int
    garantia_dias: int
    data_validade: Optional[date]
    ativo: bool


class OrcamentoDetalhado(OrcamentoResponse):
    """Schema completo para detalhes do orçamento"""
    servicos: List[ItemOrcamento]
    pecas: List[PecaOrcamento]
    subtotal_servicos: Decimal
    subtotal_pecas: Decimal
    desconto_total: Decimal
    condicoes_pagamento: CondicoesPagamento
    observacoes: Optional[str]
    condicoes_gerais: Optional[str]
    diagnostico_id: Optional[str]
    ordem_servico_id: Optional[str]
    tecnico_responsavel: Optional[str]


class OrcamentoAprovacao(BaseModel):
    """Schema para aprovação de orçamento"""
    aprovado: bool
    motivo_rejeicao: Optional[str] = None
    assinatura_digital: Optional[str] = None
    ip_aprovacao: Optional[str] = None


class OrcamentoFiltros(BaseModel):
    """Schema para filtros de busca"""
    status: Optional[StatusOrcamento] = None
    prioridade: Optional[PrioridadeOrcamento] = None
    cliente_id: Optional[str] = None
    cliente_nome: Optional[str] = None
    cliente_telefone: Optional[str] = None
    tecnico_responsavel: Optional[str] = None
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    valor_minimo: Optional[Decimal] = None
    valor_maximo: Optional[Decimal] = None
    ativo: bool = True
    # Paginação
    pagina: int = Field(default=1, ge=1)
    limite: Optional[int] = Field(default=50, ge=1, le=100)
    # Ordenação
    ordenar_por: Optional[str] = Field(default="created_at")
    ordem_desc: bool = Field(default=True)


class OrcamentoRelatorio(BaseModel):
    """Schema para relatórios de orçamento"""
    total_orcamentos: int
    valor_total_geral: Decimal
    orcamentos_por_status: Dict[StatusOrcamento, int]
    orcamentos_por_prioridade: Dict[PrioridadeOrcamento, int]
    ticket_medio: Decimal
    taxa_aprovacao: float
    tempo_medio_aprovacao_horas: Optional[float]