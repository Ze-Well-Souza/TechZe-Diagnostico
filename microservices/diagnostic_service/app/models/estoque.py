"""
Modelos para sistema de estoque - TechZe Diagnóstico
Implementa controle completo de estoque para loja de manutenção
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid


class TipoItem(str, Enum):
    """Tipos de itens do estoque"""
    PECA_HARDWARE = "peca_hardware"
    SOFTWARE = "software"
    ACESSORIO = "acessorio"
    CONSUMIVEL = "consumivel"
    FERRAMENTA = "ferramenta"
    CABO = "cabo"
    ADAPTADOR = "adaptador"
    OUTRO = "outro"


class CategoriaItem(str, Enum):
    """Categorias de itens"""
    PROCESSADOR = "processador"
    MEMORIA_RAM = "memoria_ram"
    DISCO_RIGIDO = "disco_rigido"
    SSD = "ssd"
    PLACA_MAE = "placa_mae"
    PLACA_VIDEO = "placa_video"
    FONTE = "fonte"
    COOLER = "cooler"
    GABINETE = "gabinete"
    MONITOR = "monitor"
    TECLADO = "teclado"
    MOUSE = "mouse"
    IMPRESSORA = "impressora"
    ROTEADOR = "roteador"
    SWITCH = "switch"
    ANTIVIRUS = "antivirus"
    SISTEMA_OPERACIONAL = "sistema_operacional"
    APLICATIVO = "aplicativo"


class StatusItem(str, Enum):
    """Status do item no estoque"""
    ATIVO = "ativo"
    INATIVO = "inativo"
    DESCONTINUADO = "descontinuado"
    BLOQUEADO = "bloqueado"


class TipoMovimentacao(str, Enum):
    """Tipos de movimentação de estoque"""
    ENTRADA = "entrada"
    SAIDA = "saida"
    AJUSTE = "ajuste"
    TRANSFERENCIA = "transferencia"
    PERDA = "perda"
    DEVOLUCAO = "devolucao"


class StatusAlerta(str, Enum):
    """Status dos alertas de estoque"""
    ATIVO = "ativo"
    RESOLVIDO = "resolvido"
    IGNORADO = "ignorado"


# ==========================================
# MODELOS DE DADOS
# ==========================================

class Fornecedor(BaseModel):
    """Dados do fornecedor"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nome: str = Field(..., min_length=3, max_length=100)
    cnpj: Optional[str] = Field(None, min_length=14, max_length=18)
    telefone: Optional[str] = Field(None, min_length=10, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    endereco: Optional[str] = Field(None, max_length=300)
    contato_vendas: Optional[str] = Field(None, max_length=100)
    prazo_entrega_dias: Optional[int] = Field(None, ge=0, le=365)
    condicoes_pagamento: Optional[str] = Field(None, max_length=200)
    observacoes: Optional[str] = Field(None, max_length=500)
    ativo: bool = Field(default=True)


class ItemEstoque(BaseModel):
    """Item do estoque"""
    
    # Identificação
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    codigo: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=3, max_length=200)
    descricao: Optional[str] = Field(None, max_length=500)
    
    # Categorização
    tipo: TipoItem
    categoria: CategoriaItem
    subcategoria: Optional[str] = Field(None, max_length=100)
    marca: Optional[str] = Field(None, max_length=50)
    modelo: Optional[str] = Field(None, max_length=100)
    
    # Identificação física
    codigo_barras: Optional[str] = Field(None, max_length=100)
    numero_serie: Optional[str] = Field(None, max_length=100)
    numero_parte: Optional[str] = Field(None, max_length=100)
    
    # Quantidades
    quantidade_atual: int = Field(default=0, ge=0)
    quantidade_minima: int = Field(default=5, ge=0)
    quantidade_maxima: Optional[int] = Field(None, ge=0)
    quantidade_reservada: int = Field(default=0, ge=0)
    quantidade_disponivel: int = Field(default=0, ge=0)
    
    # Preços
    preco_custo: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    preco_venda: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    margem_lucro: Decimal = Field(default=Decimal('0.00'), ge=0, max_digits=5, decimal_places=2)
    
    # Localização
    localizacao: Optional[str] = Field(None, max_length=100)
    corredor: Optional[str] = Field(None, max_length=20)
    prateleira: Optional[str] = Field(None, max_length=20)
    posicao: Optional[str] = Field(None, max_length=20)
    
    # Fornecedor
    fornecedor_principal: Optional[str] = None  # ID do fornecedor
    fornecedores_alternativos: Optional[List[str]] = Field(default_factory=list)
    
    # Datas
    data_cadastro: datetime = Field(default_factory=datetime.now)
    data_atualizacao: datetime = Field(default_factory=datetime.now)
    data_ultima_entrada: Optional[datetime] = None
    data_ultima_saida: Optional[datetime] = None
    data_validade: Optional[date] = None
    
    # Status e controle
    status: StatusItem = Field(default=StatusItem.ATIVO)
    requer_serie: bool = Field(default=False)
    controlado: bool = Field(default=False)
    peso_kg: Optional[Decimal] = Field(None, ge=0, max_digits=8, decimal_places=3)
    dimensoes: Optional[str] = Field(None, max_length=100)
    
    # Informações técnicas
    especificacoes: Optional[Dict[str, Any]] = Field(default_factory=dict)
    compatibilidade: Optional[List[str]] = Field(default_factory=list)
    garantia_fornecedor_dias: Optional[int] = Field(None, ge=0, le=1095)
    
    # Controle interno
    observacoes: Optional[str] = Field(None, max_length=1000)
    tags: Optional[List[str]] = Field(default_factory=list)
    ativo: bool = Field(default=True)
    
    @model_validator(mode='after')
    def atualizar_dados_automaticos(self):
        """Atualiza automaticamente dados calculados"""
        # Atualizar data de modificação
        self.data_atualizacao = datetime.now()
        
        # Calcular quantidade disponível
        self.quantidade_disponivel = self.quantidade_atual - self.quantidade_reservada
        
        # Calcular margem de lucro
        if self.preco_custo > 0:
            self.margem_lucro = ((self.preco_venda - self.preco_custo) / self.preco_custo) * Decimal('100')
        else:
            self.margem_lucro = Decimal('0.00')
            
        return self
    
    def verificar_estoque_baixo(self) -> bool:
        """Verifica se o item está com estoque baixo"""
        return self.quantidade_disponivel <= self.quantidade_minima
    
    def verificar_validade_proxima(self, dias: int = 30) -> bool:
        """Verifica se o item está próximo do vencimento"""
        if self.data_validade:
            return (self.data_validade - date.today()).days <= dias
        return False


class MovimentacaoEstoque(BaseModel):
    """Movimentação de estoque"""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item_id: str
    tipo: TipoMovimentacao
    quantidade: int = Field(..., ge=1)
    quantidade_anterior: int = Field(..., ge=0)
    quantidade_posterior: int = Field(..., ge=0)
    
    # Preços
    preco_unitario: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    valor_total: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    
    # Referências
    documento: Optional[str] = Field(None, max_length=100)
    ordem_servico_id: Optional[str] = None
    orcamento_id: Optional[str] = None
    fornecedor_id: Optional[str] = None
    
    # Informações adicionais
    motivo: str = Field(..., min_length=3, max_length=500)
    observacoes: Optional[str] = Field(None, max_length=1000)
    usuario: str = Field(..., min_length=3, max_length=100)
    
    # Controle
    data_movimentacao: datetime = Field(default_factory=datetime.now)
    aprovado_por: Optional[str] = None
    data_aprovacao: Optional[datetime] = None
    
    @model_validator(mode='after')
    def calcular_valor_total(self):
        """Calcula automaticamente o valor total"""
        quantidade = self.quantidade
        preco_unitario = self.preco_unitario
        self.valor_total = Decimal(str(quantidade)) * preco_unitario
        return self


# ==========================================
# SCHEMAS PARA API
# ==========================================

class ItemEstoqueCreate(BaseModel):
    """Schema para criação de item"""
    codigo: str = Field(..., min_length=1, max_length=50)
    nome: str = Field(..., min_length=3, max_length=200)
    descricao: Optional[str] = None
    tipo: TipoItem
    categoria: CategoriaItem
    subcategoria: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    quantidade_minima: int = Field(default=5, ge=0)
    quantidade_maxima: Optional[int] = None
    preco_custo: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    preco_venda: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    localizacao: Optional[str] = None
    fornecedor_principal: Optional[str] = None
    data_validade: Optional[date] = None
    observacoes: Optional[str] = None


class ItemEstoqueUpdate(BaseModel):
    """Schema para atualização de item"""
    nome: Optional[str] = Field(None, min_length=3, max_length=200)
    descricao: Optional[str] = None
    categoria: Optional[CategoriaItem] = None
    subcategoria: Optional[str] = None
    marca: Optional[str] = None
    modelo: Optional[str] = None
    quantidade_minima: Optional[int] = Field(None, ge=0)
    quantidade_maxima: Optional[int] = None
    preco_custo: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    preco_venda: Optional[Decimal] = Field(None, ge=0, max_digits=10, decimal_places=2)
    localizacao: Optional[str] = None
    fornecedor_principal: Optional[str] = None
    data_validade: Optional[date] = None
    observacoes: Optional[str] = None
    status: Optional[StatusItem] = None
    ativo: Optional[bool] = None


class ItemEstoqueResponse(BaseModel):
    """Schema para resposta da API"""
    id: str
    codigo: str
    nome: str
    tipo: TipoItem
    categoria: CategoriaItem
    quantidade_atual: int
    quantidade_disponivel: int
    preco_custo: Decimal
    preco_venda: Decimal
    status: StatusItem
    data_cadastro: datetime
    ativo: bool


class MovimentacaoCreate(BaseModel):
    """Schema para criação de movimentação"""
    item_id: str
    tipo: TipoMovimentacao
    quantidade: int = Field(..., ge=1)
    preco_unitario: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)
    motivo: str = Field(..., min_length=3, max_length=500)
    documento: Optional[str] = None
    ordem_servico_id: Optional[str] = None
    orcamento_id: Optional[str] = None
    fornecedor_id: Optional[str] = None
    observacoes: Optional[str] = None


class EstoqueFiltros(BaseModel):
    """Schema para filtros de busca"""
    tipo: Optional[TipoItem] = None
    categoria: Optional[CategoriaItem] = None
    marca: Optional[str] = None
    status: Optional[StatusItem] = None
    estoque_baixo: Optional[bool] = None
    sem_estoque: Optional[bool] = None
    validade_proxima: Optional[bool] = None
    fornecedor_id: Optional[str] = None
    ativo: bool = True


class EstoqueRelatorio(BaseModel):
    """Schema para relatórios de estoque"""
    total_itens: int
    valor_total_estoque: Decimal
    itens_estoque_baixo: int
    itens_sem_estoque: int
    itens_vencimento_proximo: int
    itens_por_categoria: Dict[str, int]
    valor_por_categoria: Dict[str, Decimal]
    giro_estoque: Optional[Decimal]


# ==========================================
# ALIASES PARA COMPATIBILIDADE
# ==========================================

# Alias para compatibilidade com testes e APIs antigas
EstoqueItem = ItemEstoque
EstoqueMovimentacao = MovimentacaoEstoque
