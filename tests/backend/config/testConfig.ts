/**
 * Configuração de Testes - Semana 3
 * Agente TRAE testando Backend do CURSOR
 * Data: 09/01/2025
 */

export interface TestEnvironment {
  name: string;
  baseUrl: string;
  timeout: number;
  retries: number;
  headers: Record<string, string>;
}

export interface TestSuite {
  name: string;
  enabled: boolean;
  priority: 'high' | 'medium' | 'low';
  endpoints: string[];
  expectedDuration: number; // em minutos
}

export interface TestMetrics {
  startTime: Date;
  endTime?: Date;
  totalTests: number;
  passedTests: number;
  failedTests: number;
  skippedTests: number;
  averageResponseTime: number;
  maxResponseTime: number;
  minResponseTime: number;
  errorRate: number;
}

export class TestConfig {
  // Ambientes de teste
  static readonly environments: Record<string, TestEnvironment> = {
    development: {
      name: 'Development',
      baseUrl: 'http://localhost:3000/api',
      timeout: 5000,
      retries: 3,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'TRAE-Test-Agent/1.0'
      }
    },
    staging: {
      name: 'Staging',
      baseUrl: 'https://staging-api.techze.com/api',
      timeout: 10000,
      retries: 2,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'TRAE-Test-Agent/1.0'
      }
    },
    production: {
      name: 'Production',
      baseUrl: 'https://api.techze.com/api',
      timeout: 15000,
      retries: 1,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'TRAE-Test-Agent/1.0'
      }
    }
  };

  // Suítes de teste da Semana 3
  static readonly testSuites: Record<string, TestSuite> = {
    orcamentos: {
      name: 'Orçamentos API Tests',
      enabled: true,
      priority: 'high',
      endpoints: [
        '/orcamentos',
        '/orcamentos/:id',
        '/orcamentos/:id/itens',
        '/orcamentos/:id/aprovar',
        '/orcamentos/:id/rejeitar',
        '/orcamentos/:id/pdf',
        '/orcamentos/cliente/:clienteId',
        '/orcamentos/status/:status',
        '/orcamentos/periodo'
      ],
      expectedDuration: 15
    },
    estoque: {
      name: 'Estoque API Tests',
      enabled: true,
      priority: 'high',
      endpoints: [
        '/estoque/produtos',
        '/estoque/produtos/:id',
        '/estoque/produtos/categoria/:categoria',
        '/estoque/produtos/buscar',
        '/estoque/movimentacoes',
        '/estoque/movimentacoes/:id',
        '/estoque/movimentacoes/produto/:produtoId',
        '/estoque/entrada',
        '/estoque/saida',
        '/estoque/transferencia',
        '/estoque/inventario',
        '/estoque/relatorio/baixo-estoque',
        '/estoque/relatorio/movimentacoes'
      ],
      expectedDuration: 20
    },
    ordemServico: {
      name: 'Ordem de Serviço API Tests',
      enabled: true,
      priority: 'high',
      endpoints: [
        '/ordem-servico',
        '/ordem-servico/:id',
        '/ordem-servico/:id/itens',
        '/ordem-servico/:id/servicos',
        '/ordem-servico/:id/pecas',
        '/ordem-servico/:id/iniciar',
        '/ordem-servico/:id/pausar',
        '/ordem-servico/:id/finalizar',
        '/ordem-servico/:id/cancelar',
        '/ordem-servico/:id/historico',
        '/ordem-servico/:id/anexos',
        '/ordem-servico/:id/comentarios',
        '/ordem-servico/cliente/:clienteId',
        '/ordem-servico/tecnico/:tecnicoId',
        '/ordem-servico/status/:status',
        '/ordem-servico/periodo',
        '/ordem-servico/relatorio'
      ],
      expectedDuration: 25
    },
    integration: {
      name: 'Integration Flow Tests',
      enabled: true,
      priority: 'medium',
      endpoints: [
        // Fluxos completos que envolvem múltiplas APIs
        'flow:orcamento-to-ordem',
        'flow:estoque-movimentacao',
        'flow:ordem-completa',
        'flow:relatorio-integrado'
      ],
      expectedDuration: 30
    },
    performance: {
      name: 'Performance & Load Tests',
      enabled: true,
      priority: 'medium',
      endpoints: [
        // Testes de carga em endpoints críticos
        'load:/orcamentos',
        'load:/estoque/produtos',
        'load:/ordem-servico',
        'stress:concurrent-users'
      ],
      expectedDuration: 45
    },
    security: {
      name: 'Security & Validation Tests',
      enabled: true,
      priority: 'low',
      endpoints: [
        // Testes de segurança e validação
        'security:authentication',
        'security:authorization',
        'security:input-validation',
        'security:sql-injection',
        'security:xss-protection'
      ],
      expectedDuration: 20
    }
  };

  // Configurações de teste
  static readonly testSettings = {
    // Performance thresholds
    performance: {
      maxResponseTime: 500, // ms
      acceptableResponseTime: 200, // ms
      maxErrorRate: 0.05, // 5%
      minThroughput: 100 // requests/second
    },
    
    // Load testing
    load: {
      concurrentUsers: [1, 5, 10, 25, 50],
      testDuration: 60, // seconds
      rampUpTime: 10 // seconds
    },
    
    // Retry logic
    retry: {
      maxAttempts: 3,
      backoffMultiplier: 2,
      initialDelay: 1000 // ms
    },
    
    // Reporting
    reporting: {
      generateHtml: true,
      generateJson: true,
      generateCsv: true,
      includeScreenshots: false,
      detailedLogs: true
    }
  };

  // Método para obter configuração do ambiente atual
  static getCurrentEnvironment(): TestEnvironment {
    const env = process.env.TEST_ENV || 'development';
    return this.environments[env] || this.environments.development;
  }

  // Método para obter suítes habilitadas
  static getEnabledTestSuites(): TestSuite[] {
    return Object.values(this.testSuites).filter(suite => suite.enabled);
  }

  // Método para calcular duração total estimada
  static getEstimatedDuration(): number {
    return this.getEnabledTestSuites()
      .reduce((total, suite) => total + suite.expectedDuration, 0);
  }

  // Método para validar configuração
  static validateConfig(): { valid: boolean; errors: string[] } {
    const errors: string[] = [];
    const env = this.getCurrentEnvironment();
    
    if (!env.baseUrl) {
      errors.push('Base URL não configurada');
    }
    
    if (env.timeout < 1000) {
      errors.push('Timeout muito baixo (mínimo 1000ms)');
    }
    
    const enabledSuites = this.getEnabledTestSuites();
    if (enabledSuites.length === 0) {
      errors.push('Nenhuma suíte de teste habilitada');
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }
}

// Configuração de logging
export const LogConfig = {
  level: process.env.LOG_LEVEL || 'info',
  format: 'json',
  timestamp: true,
  colorize: false,
  maxFiles: 5,
  maxSize: '10m'
};

// Exportar configuração padrão
export default TestConfig;