// Tipos compartilhados entre frontend e backend
// Mantido por ambos agentes TRAE e CURSOR

export type OSStatus = 
  | 'aguardando_diagnostico'
  | 'diagnostico_em_andamento'
  | 'aguardando_orcamento'
  | 'orcamento_enviado'
  | 'aguardando_aprovacao'
  | 'aprovado'
  | 'em_reparo'
  | 'aguardando_pecas'
  | 'teste_qualidade'
  | 'pronto_entrega'
  | 'entregue'
  | 'cancelado'
  | 'rejeitado';

export type OrcamentoStatus = 'pendente' | 'aprovado' | 'rejeitado' | 'expirado';

export type TipoEquipamento = 'desktop' | 'notebook' | 'smartphone' | 'tablet' | 'servidor' | 'outro';

export type TipoPeca = 'processador' | 'memoria' | 'hd' | 'ssd' | 'placa_mae' | 'fonte' | 'placa_video' | 'cooler' | 'cabo' | 'outro';

export interface Cliente {
  id: string;
  nome: string;
  email: string;
  telefone: string;
  cpf?: string;
  cnpj?: string;
  endereco?: {
    rua: string;
    numero: string;
    complemento?: string;
    bairro: string;
    cidade: string;
    estado: string;
    cep: string;
  };
  criadoEm: Date;
  atualizadoEm: Date;
}

export interface Equipamento {
  id: string;
  clienteId: string;
  tipo: TipoEquipamento;
  marca: string;
  modelo: string;
  numeroSerie?: string;
  descricaoProblema: string;
  observacoes?: string;
  fotos?: string[];
  criadoEm: Date;
  atualizadoEm: Date;
}

export interface Peca {
  id: string;
  nome: string;
  tipo: TipoPeca;
  marca?: string;
  modelo?: string;
  descricao?: string;
  preco: number;
  quantidadeEstoque: number;
  estoqueMinimo: number;
  fornecedor?: string;
  codigoFornecedor?: string;
  ativa: boolean;
  criadaEm: Date;
  atualizadaEm: Date;
}

export interface OrcamentoItem {
  id: string;
  orcamentoId: string;
  tipo: 'peca' | 'servico';
  pecaId?: string;
  descricao: string;
  quantidade: number;
  valorUnitario: number;
  valorTotal: number;
  observacoes?: string;
}

export interface Orcamento {
  id: string;
  numero: string;
  clienteId: string;
  equipamentoId: string;
  ordemServicoId?: string;
  itens: OrcamentoItem[];
  valorPecas: number;
  valorServicos: number;
  valorDesconto: number;
  valorTotal: number;
  status: OrcamentoStatus;
  observacoes?: string;
  validadeAte: Date;
  aprovadoEm?: Date;
  rejeitadoEm?: Date;
  motivoRejeicao?: string;
  criadoEm: Date;
  atualizadoEm: Date;
  criadoPor: string; // ID do usuário
}

export interface Diagnostico {
  id: string;
  equipamentoId: string;
  tecnicoId: string;
  problemas: string[];
  solucoes: string[];
  pecasNecessarias: {
    pecaId: string;
    quantidade: number;
    obrigatoria: boolean;
  }[];
  tempoEstimado: number; // em horas
  observacoes?: string;
  fotos?: string[];
  criadoEm: Date;
  atualizadoEm: Date;
}

export interface OrdemServico {
  id: string;
  numero: string;
  clienteId: string;
  equipamentoId: string;
  status: OSStatus;
  prioridade: 'baixa' | 'normal' | 'alta' | 'urgente';
  diagnostico?: Diagnostico;
  orcamento?: Orcamento;
  tecnicoId?: string;
  dataEntrada: Date;
  dataPrevisao?: Date;
  dataEntrega?: Date;
  observacoes: string[];
  historico: {
    data: Date;
    status: OSStatus;
    observacao?: string;
    usuarioId: string;
  }[];
  criadaEm: Date;
  atualizadaEm: Date;
}

export interface Tecnico {
  id: string;
  nome: string;
  email: string;
  telefone: string;
  especialidades: string[];
  ativo: boolean;
  comissao: number; // percentual
  criadoEm: Date;
  atualizadoEm: Date;
}

export interface EstoqueItem {
  id: string;
  pecaId: string;
  quantidade: number;
  quantidadeReservada: number;
  quantidadeDisponivel: number;
  localizacao?: string;
  lote?: string;
  dataValidade?: Date;
  atualizadoEm: Date;
}

export interface EstoqueFiltros {
  tipo?: TipoPeca;
  marca?: string;
  estoqueMinimo?: boolean;
  ativo?: boolean;
  busca?: string;
}

export interface EstoqueAlerta {
  id: string;
  pecaId: string;
  tipo: 'estoque_baixo' | 'estoque_zerado' | 'validade_proxima';
  mensagem: string;
  criadoEm: Date;
}

export interface Notificacao {
  id: string;
  usuarioId: string;
  tipo: 'orcamento' | 'ordem_servico' | 'estoque' | 'sistema';
  titulo: string;
  mensagem: string;
  lida: boolean;
  dadosAdicionais?: any;
  criadaEm: Date;
}

export interface Agendamento {
  id: string;
  clienteId: string;
  equipamentoId?: string;
  tecnicoId?: string;
  dataHora: Date;
  duracao: number; // em minutos
  tipo: 'diagnostico' | 'entrega' | 'coleta' | 'manutencao';
  status: 'agendado' | 'confirmado' | 'em_andamento' | 'concluido' | 'cancelado';
  observacoes?: string;
  criadoEm: Date;
  atualizadoEm: Date;
}

// Interfaces para APIs
export interface OrcamentoInput {
  clienteId: string;
  equipamentoId: string;
  ordemServicoId?: string;
  itens: Omit<OrcamentoItem, 'id' | 'orcamentoId' | 'valorTotal'>[];
  valorDesconto?: number;
  observacoes?: string;
  validadeAte?: Date;
}

export interface OrcamentoAPI {
  criar: (dados: OrcamentoInput) => Promise<Orcamento>;
  buscarPorId: (id: string) => Promise<Orcamento>;
  listar: (filtros?: { clienteId?: string; status?: OrcamentoStatus }) => Promise<Orcamento[]>;
  aprovar: (id: string) => Promise<void>;
  rejeitar: (id: string, motivo: string) => Promise<void>;
  exportar: (id: string, formato: 'pdf' | 'whatsapp') => Promise<string>;
  atualizar: (id: string, dados: Partial<OrcamentoInput>) => Promise<Orcamento>;
  excluir: (id: string) => Promise<void>;
}

export interface EstoqueAPI {
  listar: (filtros?: EstoqueFiltros) => Promise<EstoqueItem[]>;
  buscarPorId: (id: string) => Promise<EstoqueItem>;
  atualizar: (id: string, quantidade: number) => Promise<void>;
  reservar: (pecaId: string, quantidade: number) => Promise<void>;
  liberar: (pecaId: string, quantidade: number) => Promise<void>;
  alertas: () => Promise<EstoqueAlerta[]>;
  entrada: (pecaId: string, quantidade: number, observacoes?: string) => Promise<void>;
  saida: (pecaId: string, quantidade: number, observacoes?: string) => Promise<void>;
}

export interface OrdemServicoAPI {
  criar: (dados: Omit<OrdemServico, 'id' | 'numero' | 'criadaEm' | 'atualizadaEm' | 'historico'>) => Promise<OrdemServico>;
  buscarPorId: (id: string) => Promise<OrdemServico>;
  listar: (filtros?: { status?: OSStatus; tecnicoId?: string; clienteId?: string }) => Promise<OrdemServico[]>;
  atualizarStatus: (id: string, status: OSStatus, observacao?: string) => Promise<void>;
  atribuirTecnico: (id: string, tecnicoId: string) => Promise<void>;
  adicionarObservacao: (id: string, observacao: string) => Promise<void>;
}

export interface AgendamentoAPI {
  criar: (dados: Omit<Agendamento, 'id' | 'criadoEm' | 'atualizadoEm'>) => Promise<Agendamento>;
  buscarPorId: (id: string) => Promise<Agendamento>;
  listar: (filtros?: { data?: Date; tecnicoId?: string; status?: string }) => Promise<Agendamento[]>;
  atualizar: (id: string, dados: Partial<Agendamento>) => Promise<Agendamento>;
  cancelar: (id: string, motivo: string) => Promise<void>;
  confirmar: (id: string) => Promise<void>;
  verificarDisponibilidade: (tecnicoId: string, dataHora: Date, duracao: number) => Promise<boolean>;
}

// Tipos para formulários
export interface FormularioOrcamento {
  clienteId: string;
  equipamentoId: string;
  itens: {
    tipo: 'peca' | 'servico';
    pecaId?: string;
    descricao: string;
    quantidade: number;
    valorUnitario: number;
  }[];
  valorDesconto: number;
  observacoes: string;
  validadeAte: string; // ISO string
}

export interface FormularioAgendamento {
  clienteId: string;
  equipamentoId?: string;
  tecnicoId?: string;
  data: string; // ISO date
  hora: string; // HH:mm
  duracao: number;
  tipo: 'diagnostico' | 'entrega' | 'coleta' | 'manutencao';
  observacoes?: string;
}

// Tipos para relatórios
export interface RelatorioFinanceiro {
  periodo: {
    inicio: Date;
    fim: Date;
  };
  orcamentos: {
    total: number;
    aprovados: number;
    rejeitados: number;
    pendentes: number;
    valorTotal: number;
    valorAprovado: number;
  };
  ordensServico: {
    total: number;
    concluidas: number;
    emAndamento: number;
    canceladas: number;
  };
  faturamento: {
    pecas: number;
    servicos: number;
    total: number;
  };
}

export interface RelatorioEstoque {
  totalItens: number;
  valorTotal: number;
  alertas: EstoqueAlerta[];
  movimentacoes: {
    entradas: number;
    saidas: number;
    periodo: { inicio: Date; fim: Date };
  };
  itensCriticos: EstoqueItem[];
}

// ===== TIPOS ESPECÍFICOS PARA PORTAL DO CLIENTE =====
export interface OrdemServicoPortal extends OrdemServico {
  podeAvaliar: boolean;
  avaliacaoId?: string;
  mensagensNaoLidas: number;
}

export interface AvaliacaoServico {
  id: string;
  ordemServicoId: string;
  clienteId: string;
  nota: number; // 1-5
  comentario?: string;
  aspectos: {
    atendimento: number;
    qualidade: number;
    prazo: number;
    preco: number;
  };
  criadoEm: Date;
}

export interface MensagemPortal {
  id: string;
  ordemServicoId: string;
  remetente: 'cliente' | 'tecnico' | 'sistema';
  remetenteId: string;
  remetenteNome: string;
  conteudo: string;
  anexos?: string[];
  lida: boolean;
  criadoEm: Date;
}

// ===== TIPOS ESPECÍFICOS PARA AGENDAMENTO =====
export interface DisponibilidadeHorario {
  horario: string;
  disponivel: boolean;
  tecnicoId?: string;
  tecnicoNome?: string;
}

export interface DisponibilidadeData {
  data: string;
  horarios: DisponibilidadeHorario[];
  totalDisponivel: number;
}

export interface AgendamentoCompleto extends Agendamento {
  cliente: Cliente;
  tecnico?: Tecnico;
  equipamento?: Equipamento;
}

// ===== TIPOS ESPECÍFICOS PARA ESTOQUE =====
export interface ItemEstoqueCompleto {
  id: string;
  nome: string;
  descricao?: string;
  categoria: string;
  codigo: string;
  preco_custo: number;
  preco_venda: number;
  quantidade_atual: number;
  quantidade_minima: number;
  fornecedor?: string;
  localizacao?: string;
  status: 'disponivel' | 'baixo_estoque' | 'esgotado' | 'descontinuado';
  criadoEm: Date;
  atualizadoEm: Date;
}

export interface MovimentacaoEstoque {
  id: string;
  item_id: string;
  tipo: 'entrada' | 'saida';
  quantidade: number;
  quantidade_anterior: number;
  quantidade_nova: number;
  motivo: string;
  observacoes?: string;
  usuario_id: string;
  usuarioNome?: string;
  itemNome?: string;
  itemCodigo?: string;
  criadoEm: Date;
}

export interface EstatisticasEstoque {
  totalItens: number;
  itensAtivos: number;
  valorTotal: number;
  itensBaixoEstoque: number;
  itensEsgotados: number;
  movimentacoesMes: number;
  valorMovimentacoesMes: number;
}

// ===== CONSTANTES E ENUMS =====
export const TIPOS_SERVICO_AGENDAMENTO = [
  'Diagnóstico',
  'Reparo',
  'Manutenção Preventiva',
  'Instalação',
  'Configuração',
  'Limpeza',
  'Atualização',
  'Outros'
] as const;

export const CATEGORIAS_ESTOQUE_COMPLETAS = [
  'Peças de Reposição',
  'Ferramentas',
  'Acessórios',
  'Componentes Eletrônicos',
  'Materiais de Limpeza',
  'Outros'
] as const;

export const STATUS_AGENDAMENTO_CONFIG = {
  agendado: {
    label: 'Agendado',
    color: 'bg-blue-500',
    variant: 'default' as const
  },
  confirmado: {
    label: 'Confirmado',
    color: 'bg-green-500',
    variant: 'default' as const
  },
  em_andamento: {
    label: 'Em Andamento',
    color: 'bg-yellow-500',
    variant: 'secondary' as const
  },
  concluido: {
    label: 'Concluído',
    color: 'bg-green-600',
    variant: 'default' as const
  },
  cancelado: {
    label: 'Cancelado',
    color: 'bg-red-500',
    variant: 'destructive' as const
  }
} as const;

export const STATUS_ESTOQUE_CONFIG = {
  disponivel: {
    label: 'Disponível',
    color: 'bg-green-500',
    variant: 'default' as const
  },
  baixo_estoque: {
    label: 'Baixo Estoque',
    color: 'bg-yellow-500',
    variant: 'secondary' as const
  },
  esgotado: {
    label: 'Esgotado',
    color: 'bg-red-500',
    variant: 'destructive' as const
  },
  descontinuado: {
    label: 'Descontinuado',
    color: 'bg-gray-500',
    variant: 'outline' as const
  }
} as const;

// ===== APIS ESPECÍFICAS =====
export interface PortalClienteAPI {
  obterOrdensServico: (clienteId: string) => Promise<OrdemServicoPortal[]>;
  obterHistorico: (clienteId: string) => Promise<OrdemServicoPortal[]>;
  obterDetalhesOrdem: (ordemId: string) => Promise<OrdemServicoPortal>;
  avaliarServico: (dados: Omit<AvaliacaoServico, 'id' | 'criadoEm'>) => Promise<AvaliacaoServico>;
  baixarOrcamento: (orcamentoId: string) => Promise<Blob>;
  aprovarOrcamento: (orcamentoId: string) => Promise<void>;
  rejeitarOrcamento: (orcamentoId: string, motivo: string) => Promise<void>;
  enviarMensagem: (ordemServicoId: string, conteudo: string, anexos?: File[]) => Promise<MensagemPortal>;
  obterMensagens: (ordemServicoId: string) => Promise<MensagemPortal[]>;
  marcarMensagensComoLidas: (ordemServicoId: string) => Promise<void>;
  atualizarPerfil: (dados: Partial<Cliente>) => Promise<Cliente>;
}

export interface AgendamentoAPICompleta extends AgendamentoAPI {
  obterDisponibilidade: (dataInicio: Date, dataFim: Date) => Promise<DisponibilidadeData[]>;
  reagendar: (agendamentoId: string, novaData: Date, novoHorario: string) => Promise<void>;
}

export interface EstoqueAPICompleta {
  listarItens: () => Promise<ItemEstoqueCompleto[]>;
  buscarPorCodigo: (codigo: string) => Promise<ItemEstoqueCompleto | null>;
  obterDetalhes: (itemId: string) => Promise<ItemEstoqueCompleto>;
  criar: (dados: Omit<ItemEstoqueCompleto, 'id' | 'criadoEm' | 'atualizadoEm' | 'status'>) => Promise<ItemEstoqueCompleto>;
  atualizar: (itemId: string, dados: Partial<ItemEstoqueCompleto>) => Promise<void>;
  excluir: (itemId: string) => Promise<void>;
  ajustarEstoque: (
    itemId: string,
    tipo: 'entrada' | 'saida',
    quantidade: number,
    motivo: string,
    observacoes?: string
  ) => Promise<MovimentacaoEstoque>;
  listarMovimentacoes: (itemId?: string) => Promise<MovimentacaoEstoque[]>;
  listarBaixoEstoque: () => Promise<ItemEstoqueCompleto[]>;
  obterEstatisticas: () => Promise<EstatisticasEstoque>;
  exportarItens: () => Promise<Blob>;
}