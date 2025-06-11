// Interface para testes da API de Orçamentos - Agente TRAE testando Backend CURSOR
// Data: 2025-01-09
// Testador: Agente TRAE

export interface OrcamentoCreateRequest {
  cliente_id: number;
  descricao: string;
  valor_total: number;
  status: 'PENDENTE' | 'APROVADO' | 'REJEITADO' | 'EXPIRADO';
  data_validade: string;
  itens: OrcamentoItem[];
}

export interface OrcamentoItem {
  produto_id: number;
  quantidade: number;
  preco_unitario: number;
  descricao?: string;
}

export interface OrcamentoResponse {
  id: number;
  cliente_id: number;
  descricao: string;
  valor_total: number;
  status: string;
  data_criacao: string;
  data_validade: string;
  itens: OrcamentoItem[];
}

export interface OrcamentosApiTest {
  // Endpoints identificados para teste
  createOrcamento: (data: OrcamentoCreateRequest) => Promise<OrcamentoResponse>;
  getOrcamento: (id: number) => Promise<OrcamentoResponse>;
  updateOrcamento: (id: number, data: Partial<OrcamentoCreateRequest>) => Promise<OrcamentoResponse>;
  deleteOrcamento: (id: number) => Promise<void>;
  listOrcamentos: (filters?: any) => Promise<OrcamentoResponse[]>;
  approveOrcamento: (id: number) => Promise<OrcamentoResponse>;
  rejectOrcamento: (id: number) => Promise<OrcamentoResponse>;
  getOrcamentosByCliente: (clienteId: number) => Promise<OrcamentoResponse[]>;
  generatePdfOrcamento: (id: number) => Promise<Blob>;
}

// Métricas de teste para Orçamentos API
export interface OrcamentosTestMetrics {
  endpointsTested: number;
  endpointsWorking: number;
  averageResponseTime: number;
  usabilityScore: number;
  documentationScore: number;
  criticalIssues: string[];
  performanceIssues: string[];
  usabilityIssues: string[];
}

// Casos de teste padrão
export const orcamentosTestCases = {
  validOrcamento: {
    cliente_id: 1,
    descricao: "Orçamento teste para validação",
    valor_total: 1500.00,
    status: 'PENDENTE' as const,
    data_validade: "2025-02-09",
    itens: [
      {
        produto_id: 1,
        quantidade: 2,
        preco_unitario: 750.00,
        descricao: "Produto teste"
      }
    ]
  },
  invalidOrcamento: {
    cliente_id: -1,
    descricao: "",
    valor_total: -100,
    status: 'INVALID' as any,
    data_validade: "invalid-date",
    itens: []
  }
};