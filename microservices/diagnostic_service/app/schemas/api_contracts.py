"""Schemas de contratos de API corrigidos

Resolve incompatibilidades identificadas entre frontend (TRAE) e backend (CURSOR)
com mapeamento de campos e validação flexível.
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class TipoMovimentacao(str, Enum):
    """Tipos de movimentação de estoque"""
    ENTRADA = "entrada"
    SAIDA = "saida"
    AJUSTE = "ajuste"
    TRANSFERENCIA = "transferencia"

class StatusOrdemServico(str, Enum):
    """Status da ordem de serviço"""
    PENDENTE = "pendente"
    EM_ANDAMENTO = "em_andamento"
    AGUARDANDO_PECA = "aguardando_peca"
    FINALIZADA = "finalizada"
    CANCELADA = "cancelada"

class StatusOrcamento(str, Enum):
    """Status do orçamento"""
    RASCUNHO = "rascunho"
    ENVIADO = "enviado"
    APROVADO = "aprovado"
    REJEITADO = "rejeitado"
    EXPIRADO = "expirado"

# ============================================================================
# SCHEMAS DE ORÇAMENTO - Corrigidos para compatibilidade frontend
# ============================================================================

class EnderecoSchema(BaseModel):
    """Schema para endereço (objeto, não string)"""
    rua: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    cep: Optional[str] = None
    
    @field_validator('cep')
    @classmethod
    def validate_cep(cls, v):
        if v and len(v.replace('-', '').replace('.', '')) != 8:
            logger.warning(f"CEP inválido fornecido: {v}")
        return v

class ItemOrcamentoSchema(BaseModel):
    """Schema para itens do orçamento - compatível com frontend"""
    # Campos do frontend (TRAE)
    codigo_peca: Optional[str] = Field(None, description="Código da peça (frontend)")
    nome_peca: Optional[str] = Field(None, description="Nome da peça (frontend)")
    
    # Campos do backend (CURSOR) - mapeamento automático
    codigo: Optional[str] = Field(None, description="Código da peça (backend)")
    nome: Optional[str] = Field(None, description="Nome da peça (backend)")
    
    # Campos comuns
    descricao: Optional[str] = None
    quantidade: int = Field(gt=0, description="Quantidade deve ser maior que 0")
    valor_unitario: float = Field(ge=0, description="Valor unitário deve ser >= 0")
    valor_total: Optional[float] = Field(None, description="Calculado automaticamente")
    
    @model_validator(mode='after')
    def map_fields_and_calculate(self):
        """Mapear campos frontend->backend e calcular valor total"""
        # Mapeamento frontend -> backend
        if self.codigo_peca and not self.codigo:
            self.codigo = self.codigo_peca
        if self.nome_peca and not self.nome:
            self.nome = self.nome_peca
            
        # Mapeamento backend -> frontend (para compatibilidade)
        if self.codigo and not self.codigo_peca:
            self.codigo_peca = self.codigo
        if self.nome and not self.nome_peca:
            self.nome_peca = self.nome
            
        # Calcular valor total
        if self.quantidade and self.valor_unitario:
            self.valor_total = self.quantidade * self.valor_unitario
            
        return self

class OrcamentoCreateRequest(BaseModel):
    """Schema para criação de orçamento - compatível com frontend TRAE"""
    cliente_id: int = Field(gt=0, description="ID do cliente")
    descricao: str = Field(min_length=1, max_length=1000, description="Descrição do orçamento")
    valor_total: Optional[float] = Field(None, ge=0, description="Valor total (calculado se não fornecido)")
    
    # Campo faltante identificado na análise
    criado_por: int = Field(gt=0, description="ID do usuário que criou o orçamento")
    
    # Endereço como objeto (não string)
    endereco: Optional[Union[EnderecoSchema, Dict[str, Any], str]] = Field(
        None, 
        description="Endereço como objeto ou string (conversão automática)"
    )
    
    # Itens do orçamento
    itens: List[ItemOrcamentoSchema] = Field(
        min_length=1, 
        description="Lista de itens (mínimo 1 item)"
    )
    
    # Campos opcionais
    observacoes: Optional[str] = Field(None, max_length=2000)
    validade_dias: Optional[int] = Field(30, ge=1, le=365)
    status: Optional[StatusOrcamento] = Field(StatusOrcamento.RASCUNHO)
    
    @field_validator('endereco', mode='before')
    @classmethod
    def parse_endereco(cls, v):
        """Converter endereço string para objeto se necessário"""
        if isinstance(v, str):
            # Tentar parsear endereço string simples
            return EnderecoSchema(rua=v)
        elif isinstance(v, dict):
            return EnderecoSchema(**v)
        return v
    
    @model_validator(mode='after')
    def calculate_total_if_needed(self):
        """Calcular valor total se não fornecido"""
        if not self.valor_total and self.itens:
            self.valor_total = sum(
                item.valor_total or (item.quantidade * item.valor_unitario) 
                for item in self.itens
            )
        return self

# ============================================================================
# SCHEMAS DE ESTOQUE - Corrigidos para compatibilidade
# ============================================================================

class EstoqueMovimentacaoRequest(BaseModel):
    """Schema para movimentação de estoque - compatível com frontend"""
    item_id: int = Field(gt=0, description="ID do item")
    quantidade: int = Field(description="Quantidade (positiva para entrada, negativa para saída)")
    tipo_movimentacao: TipoMovimentacao = Field(description="Tipo de movimentação")
    
    # Campos do frontend (TRAE) - mapeamento automático
    codigo_peca: Optional[str] = Field(None, description="Código da peça (frontend)")
    nome_peca: Optional[str] = Field(None, description="Nome da peça (frontend)")
    
    # Campos do backend (CURSOR)
    codigo: Optional[str] = Field(None, description="Código da peça (backend)")
    nome: Optional[str] = Field(None, description="Nome da peça (backend)")
    
    # Campos comuns
    motivo: Optional[str] = Field(None, max_length=500, description="Motivo da movimentação")
    custo_unitario: Optional[float] = Field(None, ge=0, description="Custo unitário")
    lote: Optional[str] = Field(None, max_length=50, description="Número do lote")
    data_validade: Optional[datetime] = Field(None, description="Data de validade")
    
    @model_validator(mode='after')
    def map_fields(self):
        """Mapear campos frontend <-> backend"""
        # Frontend -> Backend
        if self.codigo_peca and not self.codigo:
            self.codigo = self.codigo_peca
        if self.nome_peca and not self.nome:
            self.nome = self.nome_peca
            
        # Backend -> Frontend
        if self.codigo and not self.codigo_peca:
            self.codigo_peca = self.codigo
        if self.nome and not self.nome_peca:
            self.nome_peca = self.nome
            
        return self

class EstoqueItemCreateRequest(BaseModel):
    """Schema para criação de item de estoque"""
    codigo: str = Field(min_length=1, max_length=50, description="Código único do item")
    nome: str = Field(min_length=1, max_length=200, description="Nome do item")
    descricao: Optional[str] = Field(None, max_length=1000)
    categoria_id: Optional[int] = Field(None, gt=0)
    fornecedor_id: Optional[int] = Field(None, gt=0)
    
    # Campos de estoque
    quantidade_atual: int = Field(0, ge=0, description="Quantidade atual em estoque")
    quantidade_minima: int = Field(0, ge=0, description="Estoque mínimo")
    quantidade_maxima: Optional[int] = Field(None, ge=0, description="Estoque máximo")
    
    # Campos financeiros
    custo_medio: Optional[float] = Field(None, ge=0, description="Custo médio")
    preco_venda: Optional[float] = Field(None, ge=0, description="Preço de venda")
    
    # Campos de controle
    ativo: bool = Field(True, description="Item ativo")
    controla_lote: bool = Field(False, description="Controla lote")
    perecivel: bool = Field(False, description="Item perecível")
    
    @field_validator('quantidade_maxima')
    @classmethod
    def validate_max_quantity(cls, v, info):
        if v is not None and 'quantidade_minima' in info.data:
            if v < info.data['quantidade_minima']:
                raise ValueError('Quantidade máxima deve ser >= quantidade mínima')
        return v

# ============================================================================
# SCHEMAS DE ORDEM DE SERVIÇO - Corrigidos
# ============================================================================

class OrdemServicoCreateRequest(BaseModel):
    """Schema para criação de ordem de serviço"""
    cliente_id: int = Field(gt=0, description="ID do cliente")
    equipamento: str = Field(min_length=1, max_length=200, description="Equipamento")
    problema_relatado: str = Field(min_length=1, max_length=1000, description="Problema relatado")
    
    # Campos opcionais
    tecnico_id: Optional[int] = Field(None, gt=0, description="ID do técnico responsável")
    prioridade: Optional[str] = Field("normal", description="Prioridade (baixa, normal, alta, urgente)")
    data_agendamento: Optional[datetime] = Field(None, description="Data de agendamento")
    observacoes: Optional[str] = Field(None, max_length=2000, description="Observações")
    
    # Status inicial
    status: Optional[StatusOrdemServico] = Field(StatusOrdemServico.PENDENTE)
    
    # Campos de controle
    criado_por: int = Field(gt=0, description="ID do usuário que criou a OS")
    
    @field_validator('prioridade')
    @classmethod
    def validate_prioridade(cls, v):
        valid_priorities = ['baixa', 'normal', 'alta', 'urgente']
        if v.lower() not in valid_priorities:
            raise ValueError(f'Prioridade deve ser uma de: {valid_priorities}')
        return v.lower()

# ============================================================================
# SCHEMAS DE RESPOSTA - Padronizados
# ============================================================================

class ApiResponse(BaseModel):
    """Schema padrão de resposta da API"""
    success: bool = Field(description="Indica se a operação foi bem-sucedida")
    message: str = Field(description="Mensagem descritiva")
    data: Optional[Any] = Field(None, description="Dados da resposta")
    errors: Optional[List[str]] = Field(None, description="Lista de erros")
    timestamp: datetime = Field(default_factory=datetime.now, description="Timestamp da resposta")
    
class PaginatedResponse(BaseModel):
    """Schema para respostas paginadas"""
    items: List[Any] = Field(description="Lista de itens")
    total: int = Field(ge=0, description="Total de itens")
    page: int = Field(ge=1, description="Página atual")
    per_page: int = Field(ge=1, description="Itens por página")
    pages: int = Field(ge=1, description="Total de páginas")
    has_next: bool = Field(description="Tem próxima página")
    has_prev: bool = Field(description="Tem página anterior")

# ============================================================================
# UTILITÁRIOS DE VALIDAÇÃO
# ============================================================================

def validate_api_contract(data: dict, schema_class: BaseModel) -> tuple[bool, Any, List[str]]:
    """Validar dados contra schema de contrato
    
    Returns:
        tuple: (is_valid, validated_data_or_none, errors_list)
    """
    try:
        validated_data = schema_class(**data)
        return True, validated_data, []
    except Exception as e:
        logger.error(f"Validation error for {schema_class.__name__}: {str(e)}")
        return False, None, [str(e)]

def log_contract_mismatch(endpoint: str, expected_fields: List[str], received_fields: List[str]):
    """Log incompatibilidades de contrato para debugging"""
    missing_fields = set(expected_fields) - set(received_fields)
    extra_fields = set(received_fields) - set(expected_fields)
    
    if missing_fields or extra_fields:
        logger.warning(
            f"Contract mismatch in {endpoint}: "
            f"missing={list(missing_fields)}, extra={list(extra_fields)}"
        )