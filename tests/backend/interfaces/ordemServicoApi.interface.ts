// Interface para testes da API de Ordem de Serviço - Agente TRAE testando Backend CURSOR
// Data: 2025-01-09
// Testador: Agente TRAE

export interface OrdemServicoCreateRequest {
  cliente_id: number;
  equipamento: string;
  problema_relatado: string;
  observacoes?: string;
  prioridade: 'BAIXA' | 'MEDIA' | 'ALTA' | 'URGENTE';
  tecnico_id?: number;
  data_agendamento?: string;
}

export interface OrdemServicoResponse {
  id: number;
  numero_os: string;
  cliente_id: number;
  equipamento: string;
  problema_relatado: string;
  diagnostico?: string;
  solucao?: string;
  observacoes?: string;
  status: 'ABERTA' | 'EM_ANDAMENTO' | 'AGUARDANDO_PECA' | 'CONCLUIDA' | 'CANCELADA';
  prioridade: string;
  tecnico_id?: number;
  data_abertura: string;
  data_agendamento?: string;
  data_inicio?: string;
  data_conclusao?: string;
  valor_servico?: number;
  valor_pecas?: number;
  valor_total?: number;
}

export interface ServicoItem {
  id?: number;
  ordem_servico_id: number;
  descricao: string;
  quantidade: number;
  valor_unitario: number;
  valor_total: number;
}

export interface PecaItem {
  id?: number;
  ordem_servico_id: number;
  produto_id: number;
  quantidade: number;
  valor_unitario: number;
  valor_total: number;
}

export interface OrdemServicoApiTest {
  // Endpoints identificados para teste (17 endpoints)
  createOrdemServico: (data: OrdemServicoCreateRequest) => Promise<OrdemServicoResponse>;
  getOrdemServico: (id: number) => Promise<OrdemServicoResponse>;
  updateOrdemServico: (id: number, data: Partial<OrdemServicoCreateRequest>) => Promise<OrdemServicoResponse>;
  deleteOrdemServico: (id: number) => Promise<void>;
  listOrdensServico: (filters?: any) => Promise<OrdemServicoResponse[]>;
  getOrdensByCliente: (clienteId: number) => Promise<OrdemServicoResponse[]>;
  getOrdensByTecnico: (tecnicoId: number) => Promise<OrdemServicoResponse[]>;
  getOrdensByStatus: (status: string) => Promise<OrdemServicoResponse[]>;
  iniciarOrdemServico: (id: number, tecnicoId: number) => Promise<OrdemServicoResponse>;
  pausarOrdemServico: (id: number) => Promise<OrdemServicoResponse>;
  concluirOrdemServico: (id: number, diagnostico: string, solucao: string) => Promise<OrdemServicoResponse>;
  cancelarOrdemServico: (id: number, motivo: string) => Promise<OrdemServicoResponse>;
  addServicoItem: (ordemId: number, item: ServicoItem) => Promise<ServicoItem>;
  addPecaItem: (ordemId: number, item: PecaItem) => Promise<PecaItem>;
  removeServicoItem: (ordemId: number, itemId: number) => Promise<void>;
  removePecaItem: (ordemId: number, itemId: number) => Promise<void>;
  generateRelatorioOS: (dataInicio: string, dataFim: string) => Promise<any>;
}

// Métricas de teste para Ordem de Serviço API
export interface OrdemServicoTestMetrics {
  endpointsTested: number;
  endpointsWorking: number;
  averageResponseTime: number;
  usabilityScore: number;
  documentationScore: number;
  criticalIssues: string[];
  performanceIssues: string[];
  usabilityIssues: string[];
  workflowIssues: string[];
  businessLogicIssues: string[];
}

// Casos de teste padrão
export const ordemServicoTestCases = {
  validOrdemServico: {
    cliente_id: 1,
    equipamento: "Notebook Dell Inspiron 15",
    problema_relatado: "Tela não liga, apenas LED de energia aceso",
    observacoes: "Cliente relatou que problema começou após queda",
    prioridade: 'MEDIA' as const,
    tecnico_id: 1,
    data_agendamento: "2025-01-10T09:00:00Z"
  },
  invalidOrdemServico: {
    cliente_id: -1,
    equipamento: "",
    problema_relatado: "",
    prioridade: 'INVALID' as any,
    tecnico_id: -1
  },
  servicoItem: {
    ordem_servico_id: 1,
    descricao: "Diagnóstico e reparo de tela",
    quantidade: 1,
    valor_unitario: 150.00,
    valor_total: 150.00
  },
  pecaItem: {
    ordem_servico_id: 1,
    produto_id: 1,
    quantidade: 1,
    valor_unitario: 300.00,
    valor_total: 300.00
  },
  fluxoCompleto: {
    abertura: {
      cliente_id: 1,
      equipamento: "Smartphone Samsung Galaxy",
      problema_relatado: "Não carrega bateria",
      prioridade: 'ALTA' as const
    },
    inicio: {
      tecnico_id: 1
    },
    conclusao: {
      diagnostico: "Conector de carga danificado",
      solucao: "Substituição do conector de carga"
    }
  }
};