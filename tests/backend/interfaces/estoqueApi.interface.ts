// Interface para testes da API de Estoque - Agente TRAE testando Backend CURSOR
// Data: 2025-01-09
// Testador: Agente TRAE

export interface ProdutoCreateRequest {
  nome: string;
  descricao?: string;
  categoria_id: number;
  preco_venda: number;
  preco_custo: number;
  codigo_barras?: string;
  unidade_medida: string;
  estoque_minimo: number;
  estoque_atual: number;
  ativo: boolean;
}

export interface ProdutoResponse {
  id: number;
  nome: string;
  descricao?: string;
  categoria_id: number;
  preco_venda: number;
  preco_custo: number;
  codigo_barras?: string;
  unidade_medida: string;
  estoque_minimo: number;
  estoque_atual: number;
  ativo: boolean;
  data_criacao: string;
  data_atualizacao: string;
}

export interface MovimentacaoEstoque {
  produto_id: number;
  tipo: 'ENTRADA' | 'SAIDA' | 'AJUSTE';
  quantidade: number;
  motivo: string;
  data_movimentacao: string;
  usuario_id: number;
}

export interface EstoqueApiTest {
  // Endpoints identificados para teste (13 endpoints)
  createProduto: (data: ProdutoCreateRequest) => Promise<ProdutoResponse>;
  getProduto: (id: number) => Promise<ProdutoResponse>;
  updateProduto: (id: number, data: Partial<ProdutoCreateRequest>) => Promise<ProdutoResponse>;
  deleteProduto: (id: number) => Promise<void>;
  listProdutos: (filters?: any) => Promise<ProdutoResponse[]>;
  searchProdutos: (query: string) => Promise<ProdutoResponse[]>;
  getProdutosByCategoria: (categoriaId: number) => Promise<ProdutoResponse[]>;
  addEstoque: (produtoId: number, quantidade: number, motivo: string) => Promise<MovimentacaoEstoque>;
  removeEstoque: (produtoId: number, quantidade: number, motivo: string) => Promise<MovimentacaoEstoque>;
  ajustarEstoque: (produtoId: number, novaQuantidade: number, motivo: string) => Promise<MovimentacaoEstoque>;
  getMovimentacoes: (produtoId?: number) => Promise<MovimentacaoEstoque[]>;
  getEstoqueBaixo: () => Promise<ProdutoResponse[]>;
  getRelatorioEstoque: (dataInicio: string, dataFim: string) => Promise<any>;
}

// Métricas de teste para Estoque API
export interface EstoqueTestMetrics {
  endpointsTested: number;
  endpointsWorking: number;
  averageResponseTime: number;
  usabilityScore: number;
  documentationScore: number;
  criticalIssues: string[];
  performanceIssues: string[];
  usabilityIssues: string[];
  dataConsistencyIssues: string[];
}

// Casos de teste padrão
export const estoqueTestCases = {
  validProduto: {
    nome: "Produto Teste",
    descricao: "Produto para validação de testes",
    categoria_id: 1,
    preco_venda: 100.00,
    preco_custo: 60.00,
    codigo_barras: "1234567890123",
    unidade_medida: "UN",
    estoque_minimo: 10,
    estoque_atual: 50,
    ativo: true
  },
  invalidProduto: {
    nome: "",
    categoria_id: -1,
    preco_venda: -10,
    preco_custo: -5,
    unidade_medida: "",
    estoque_minimo: -1,
    estoque_atual: -10,
    ativo: false
  },
  movimentacaoEntrada: {
    produto_id: 1,
    tipo: 'ENTRADA' as const,
    quantidade: 20,
    motivo: "Compra de mercadoria",
    data_movimentacao: new Date().toISOString(),
    usuario_id: 1
  },
  movimentacaoSaida: {
    produto_id: 1,
    tipo: 'SAIDA' as const,
    quantidade: 5,
    motivo: "Venda",
    data_movimentacao: new Date().toISOString(),
    usuario_id: 1
  }
};