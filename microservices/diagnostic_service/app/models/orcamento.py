"""
Modelos para sistema de orçamentos - TechZe Diagnóstico
Implementa orçamentação completa para loja de manutenção
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
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
    valor_unitario: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    valor_total: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    tempo_estimado_horas: Optional[float] = Field(None, ge=0, le=100)
    observacoes: Optional[str] = Field(None, max_length=1000)
    codigo_interno: Optional[str] = Field(None, max_length=50)
    garantia_dias: Optional[int] = Field(None, ge=0, le=365)
    
    @validator('valor_total', always=True)
    def calcular_valor_total(cls, v, values):
        """Calcula automaticamente o valor total"""
        quantidade = values.get('quantidade', 1)
        valor_unitario = values.get('valor_unitario', Decimal('0.00'))
        return Decimal(str(quantidade)) * valor_unitario


class PecaOrcamento(BaseModel):
    """Peça utilizada no orçamento"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    codigo: str = Field(..., min_length=1, max_length=100)
    nome: str = Field(..., min_length=3, max_length=200)
    descricao: Optional[str] = Field(None, max_length=500)
    tipo: TipoPeca
    quantidade: int = Field(..., ge=1, le=1000)
    valor_unitario: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    valor_total: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    fornecedor: Optional[str] = Field(None, max_length=100)
    tempo_entrega_dias: Optional[int] = Field(None, ge=0, le=90)
    garantia_dias: Optional[int] = Field(None, ge=0, le=365)
    
    @validator('valor_total', always=True)
    def calcular_valor_total(cls, v, values):
        """Calcula automaticamente o valor total"""
        quantidade = values.get('quantidade', 1)
        valor_unitario = values.get('valor_unitario', Decimal('0.00'))
        return Decimal(str(quantidade)) * valor_unitario


class DadosCliente(BaseModel):
    """Dados do cliente para o orçamento"""
    id: Optional[str] = None
    nome: str = Field(..., min_length=3, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    telefone: str = Field(..., min_length=10, max_length=20)
    whatsapp: Optional[str] = Field(None, min_length=10, max_length=20)
    cpf_cnpj: Optional[str] = Field(None, min_length=11, max_length=18)
    endereco: Optional[str] = Field(None, max_length=300)
    observacoes: Optional[str] = Field(None, max_length=500)


class DadosEquipamento(BaseModel):
    """Dados do equipamento para orçamento"""
    id: Optional[str] = None
    tipo: str = Field(..., min_length=3, max_length=50)
    marca: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=100)
    numero_serie: Optional[str] = Field(None, max_length=100)
    problema_relatado: str = Field(..., min_length=10, max_length=1000)
    estado_fisico: Optional[str] = Field(None, max_length=500)
    acessorios: Optional[List[str]] = Field(default_factory=list)
    observacoes: Optional[str] = Field(None, max_length=500)


class CondicoesPagamento(BaseModel):
    """Condições de pagamento do orçamento"""
    forma_pagamento: List[str] = Field(default_factory=lambda: ["dinheiro", "pix", "cartao"])
    condicoes: str = Field(default="À vista")
    desconto_porcentagem: Optional[Decimal] = Field(None, ge=0, le=100, max_digits=5, decimal_places=2)
    desconto_valor: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    entrada_valor: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    parcelas: Optional[int] = Field(None, ge=1, le=12)
    valor_parcela: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    juros_mes: Optional[Decimal] = Field(None, ge=0, le=10, max_digits=5, decimal_places=2)


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
    subtotal_servicos: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    subtotal_pecas: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    desconto_total: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    valor_total: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=10, decimal_places=2)
    
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
    
    @validator('data_atualizacao', always=True)
    def atualizar_data_modificacao(cls, v):
        """Atualiza automaticamente a data de modificação"""
        return datetime.now()
    
    @validator('valor_total', always=True)
    def calcular_valor_total(cls, v, values):
        """Calcula automaticamente o valor total do orçamento"""
        subtotal_servicos = values.get('subtotal_servicos', Decimal('0.00'))
        subtotal_pecas = values.get('subtotal_pecas', Decimal('0.00'))
        desconto_total = values.get('desconto_total', Decimal('0.00'))
        return subtotal_servicos + subtotal_pecas - desconto_total
    
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
    servicos: List[ItemOrcamento] = Field(default_factory=list)
    pecas: List[PecaOrcamento] = Field(default_factory=list)
    observacoes: Optional[str] = None
    prazo_execucao_dias: int = Field(default=7)
    garantia_dias: int = Field(default=90)
    data_validade: Optional[date] = None
    diagnostico_id: Optional[str] = None


class OrcamentoUpdate(BaseModel):
    """Schema para atualização de orçamento"""
    servicos: Optional[List[ItemOrcamento]] = None
    pecas: Optional[List[PecaOrcamento]] = None
    condicoes_pagamento: Optional[CondicoesPagamento] = None
    observacoes: Optional[str] = None
    prazo_execucao_dias: Optional[int] = None
    garantia_dias: Optional[int] = None
    data_validade: Optional[date] = None
    prioridade: Optional[PrioridadeOrcamento] = None


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