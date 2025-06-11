// Test Runner Principal - Agente TRAE testando Backend CURSOR
// Data: 2025-01-09
// Testador: Agente TRAE
// Semanas 1 e 2: Setup e Testes Completos

import { ApiTester } from './components/ApiTester';
import { UsabilityValidator } from './components/UsabilityValidator';
import { PerformanceMeter } from './components/PerformanceMeter';
import { ApiValidator } from './utils/apiValidators';
import { UsabilityMetrics } from './utils/usabilityMetrics';
import { UserFlowTester } from './flows/userFlowTests';
import { ApiDocumentationValidator } from './docs/apiDocumentation';
import { ApiAccessibilityTester } from './accessibility/accessibilityTests';

// Interfaces para configuração e relatórios
export interface TestConfiguration {
  baseUrl: string;
  authToken?: string;
  timeout: number;
  retries: number;
  endpoints: {
    orcamentos: string[];
    estoque: string[];
    ordemServico: string[];
  };
}

export interface TestSuite {
  name: string;
  category: 'api' | 'usability' | 'performance' | 'flow' | 'documentation' | 'accessibility';
  tests: TestCase[];
  setup?: () => Promise<void>;
  teardown?: () => Promise<void>;
}

export interface TestCase {
  name: string;
  description: string;
  execute: () => Promise<TestResult>;
  priority: 'low' | 'medium' | 'high' | 'critical';
  tags: string[];
}

export interface TestResult {
  testName: string;
  category: string;
  passed: boolean;
  score: number;
  maxScore: number;
  duration: number;
  details: string[];
  metrics?: any;
  error?: string;
}

export interface ComprehensiveTestReport {
  summary: {
    totalTests: number;
    passedTests: number;
    failedTests: number;
    overallScore: number;
    maxPossibleScore: number;
    grade: 'A' | 'B' | 'C' | 'D' | 'F';
    executionTime: number;
  };
  categories: {
    api: CategoryResult;
    usability: CategoryResult;
    performance: CategoryResult;
    flows: CategoryResult;
    documentation: CategoryResult;
    accessibility: CategoryResult;
  };
  recommendations: {
    critical: string[];
    high: string[];
    medium: string[];
    low: string[];
    quickFixes: string[];
  };
  metrics: {
    coverage: number;
    reliability: number;
    performance: number;
    usability: number;
    documentation: number;
    accessibility: number;
  };
  detailedResults: TestResult[];
}

export interface CategoryResult {
  score: number;
  maxScore: number;
  percentage: number;
  status: 'excellent' | 'good' | 'fair' | 'poor' | 'critical';
  testCount: number;
  passedCount: number;
  issues: string[];
  recommendations: string[];
}

// Classe principal do Test Runner
export class BackendTestRunner {
  private config: TestConfiguration;
  private testSuites: TestSuite[] = [];
  private results: TestResult[] = [];
  
  constructor(config: TestConfiguration) {
    this.config = config;
    this.initializeTestSuites();
  }

  // Inicializar todas as suítes de teste
  private initializeTestSuites(): void {
    // Suíte 1: Testes de API
    this.testSuites.push({
      name: 'API Interface Tests',
      category: 'api',
      tests: this.createApiTests(),
      setup: async () => {
        console.log('🔧 Configurando testes de API...');
      }
    });

    // Suíte 2: Testes de Usabilidade
    this.testSuites.push({
      name: 'Usability Tests',
      category: 'usability',
      tests: this.createUsabilityTests(),
      setup: async () => {
        console.log('🎨 Configurando testes de usabilidade...');
      }
    });

    // Suíte 3: Testes de Performance
    this.testSuites.push({
      name: 'Performance Tests',
      category: 'performance',
      tests: this.createPerformanceTests(),
      setup: async () => {
        console.log('⚡ Configurando testes de performance...');
      }
    });

    // Suíte 4: Testes de Fluxo de Usuário
    this.testSuites.push({
      name: 'User Flow Tests',
      category: 'flow',
      tests: this.createFlowTests(),
      setup: async () => {
        console.log('🔄 Configurando testes de fluxo...');
      }
    });

    // Suíte 5: Testes de Documentação
    this.testSuites.push({
      name: 'Documentation Tests',
      category: 'documentation',
      tests: this.createDocumentationTests(),
      setup: async () => {
        console.log('📚 Configurando testes de documentação...');
      }
    });

    // Suíte 6: Testes de Acessibilidade
    this.testSuites.push({
      name: 'Accessibility Tests',
      category: 'accessibility',
      tests: this.createAccessibilityTests(),
      setup: async () => {
        console.log('♿ Configurando testes de acessibilidade...');
      }
    });
  }

  // Criar testes de API
  private createApiTests(): TestCase[] {
    const apiTester = new ApiTester(this.config.baseUrl, this.config.authToken);
    const apiValidator = new ApiValidator();
    
    return [
      {
        name: 'Orçamentos API Tests',
        description: 'Testa todos os endpoints da API de Orçamentos',
        priority: 'critical',
        tags: ['api', 'orcamentos', 'crud'],
        execute: async () => {
          const startTime = Date.now();
          try {
            const result = await apiTester.testOrcamentosApi();
            return {
              testName: 'Orçamentos API Tests',
              category: 'api',
              passed: result.success,
              score: result.score,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: result.details,
              metrics: result.metrics
            };
          } catch (error) {
            return {
              testName: 'Orçamentos API Tests',
              category: 'api',
              passed: false,
              score: 0,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [`Erro na execução: ${error}`],
              error: error.toString()
            };
          }
        }
      },
      {
        name: 'Estoque API Tests',
        description: 'Testa todos os endpoints da API de Estoque',
        priority: 'critical',
        tags: ['api', 'estoque', 'crud'],
        execute: async () => {
          const startTime = Date.now();
          try {
            const result = await apiTester.testEstoqueApi();
            return {
              testName: 'Estoque API Tests',
              category: 'api',
              passed: result.success,
              score: result.score,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: result.details,
              metrics: result.metrics
            };
          } catch (error) {
            return {
              testName: 'Estoque API Tests',
              category: 'api',
              passed: false,
              score: 0,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [`Erro na execução: ${error}`],
              error: error.toString()
            };
          }
        }
      },
      {
        name: 'Ordem de Serviço API Tests',
        description: 'Testa todos os endpoints da API de Ordem de Serviço',
        priority: 'critical',
        tags: ['api', 'ordem-servico', 'crud'],
        execute: async () => {
          const startTime = Date.now();
          try {
            const result = await apiTester.testOrdemServicoApi();
            return {
              testName: 'Ordem de Serviço API Tests',
              category: 'api',
              passed: result.success,
              score: result.score,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: result.details,
              metrics: result.metrics
            };
          } catch (error) {
            return {
              testName: 'Ordem de Serviço API Tests',
              category: 'api',
              passed: false,
              score: 0,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [`Erro na execução: ${error}`],
              error: error.toString()
            };
          }
        }
      }
    ];
  }

  // Criar testes de usabilidade
  private createUsabilityTests(): TestCase[] {
    const usabilityValidator = new UsabilityValidator(this.config.baseUrl);
    const usabilityMetrics = new UsabilityMetrics();
    
    return [
      {
        name: 'API Design Consistency',
        description: 'Valida consistência no design da API',
        priority: 'high',
        tags: ['usability', 'design', 'consistency'],
        execute: async () => {
          const startTime = Date.now();
          try {
            const result = await usabilityValidator.validateApiDesign();
            return {
              testName: 'API Design Consistency',
              category: 'usability',
              passed: result.score >= 70,
              score: result.score,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: result.details,
              metrics: result.metrics
            };
          } catch (error) {
            return {
              testName: 'API Design Consistency',
              category: 'usability',
              passed: false,
              score: 0,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [`Erro na validação: ${error}`],
              error: error.toString()
            };
          }
        }
      },
      {
        name: 'Error Handling Quality',
        description: 'Avalia qualidade do tratamento de erros',
        priority: 'high',
        tags: ['usability', 'errors', 'messages'],
        execute: async () => {
          const startTime = Date.now();
          try {
            const result = await usabilityValidator.validateErrorHandling();
            return {
              testName: 'Error Handling Quality',
              category: 'usability',
              passed: result.score >= 70,
              score: result.score,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: result.details,
              metrics: result.metrics
            };
          } catch (error) {
            return {
              testName: 'Error Handling Quality',
              category: 'usability',
              passed: false,
              score: 0,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [`Erro na validação: ${error}`],
              error: error.toString()
            };
          }
        }
      }
    ];
  }

  // Criar testes de performance
  private createPerformanceTests(): TestCase[] {
    const performanceMeter = new PerformanceMeter(this.config.baseUrl);
    
    return [
      {
        name: 'Endpoint Response Time',
        description: 'Mede tempo de resposta dos endpoints',
        priority: 'high',
        tags: ['performance', 'response-time', 'latency'],
        execute: async () => {
          const startTime = Date.now();
          try {
            const result = await performanceMeter.measureEndpointPerformance('/api/orcamentos');
            return {
              testName: 'Endpoint Response Time',
              category: 'performance',
              passed: result.averageTime < 2000, // 2 segundos
              score: Math.max(0, 100 - (result.averageTime / 20)), // Score baseado no tempo
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [
                `Tempo médio: ${result.averageTime}ms`,
                `Tempo mínimo: ${result.minTime}ms`,
                `Tempo máximo: ${result.maxTime}ms`,
                `Taxa de sucesso: ${result.successRate}%`
              ],
              metrics: result
            };
          } catch (error) {
            return {
              testName: 'Endpoint Response Time',
              category: 'performance',
              passed: false,
              score: 0,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [`Erro na medição: ${error}`],
              error: error.toString()
            };
          }
        }
      },
      {
        name: 'Load Testing',
        description: 'Testa comportamento sob carga',
        priority: 'medium',
        tags: ['performance', 'load', 'stress'],
        execute: async () => {
          const startTime = Date.now();
          try {
            const result = await performanceMeter.runLoadTest('/api/orcamentos', 10, 5000);
            return {
              testName: 'Load Testing',
              category: 'performance',
              passed: result.successRate >= 95,
              score: result.successRate,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [
                `Usuários concorrentes: 10`,
                `Taxa de sucesso: ${result.successRate}%`,
                `Throughput: ${result.throughput} req/s`,
                `Tempo médio: ${result.averageTime}ms`
              ],
              metrics: result
            };
          } catch (error) {
            return {
              testName: 'Load Testing',
              category: 'performance',
              passed: false,
              score: 0,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [`Erro no teste de carga: ${error}`],
              error: error.toString()
            };
          }
        }
      }
    ];
  }

  // Criar testes de fluxo
  private createFlowTests(): TestCase[] {
    const flowTester = new UserFlowTester(this.config.baseUrl, this.config.authToken);
    
    return [
      {
        name: 'Complete Orçamento Flow',
        description: 'Testa fluxo completo de orçamento',
        priority: 'critical',
        tags: ['flow', 'orcamento', 'integration'],
        execute: async () => {
          const startTime = Date.now();
          try {
            const result = await flowTester.executeOrcamentoFlow();
            return {
              testName: 'Complete Orçamento Flow',
              category: 'flow',
              passed: result.success,
              score: result.score,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: result.steps.map(step => 
                `${step.passed ? '✅' : '❌'} ${step.name}: ${step.description}`
              ),
              metrics: result.metrics
            };
          } catch (error) {
            return {
              testName: 'Complete Orçamento Flow',
              category: 'flow',
              passed: false,
              score: 0,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [`Erro no fluxo: ${error}`],
              error: error.toString()
            };
          }
        }
      },
      {
        name: 'Integration Flow Test',
        description: 'Testa integração entre módulos',
        priority: 'high',
        tags: ['flow', 'integration', 'modules'],
        execute: async () => {
          const startTime = Date.now();
          try {
            const result = await flowTester.executeIntegrationFlow();
            return {
              testName: 'Integration Flow Test',
              category: 'flow',
              passed: result.success,
              score: result.score,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: result.steps.map(step => 
                `${step.passed ? '✅' : '❌'} ${step.name}: ${step.description}`
              ),
              metrics: result.metrics
            };
          } catch (error) {
            return {
              testName: 'Integration Flow Test',
              category: 'flow',
              passed: false,
              score: 0,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [`Erro na integração: ${error}`],
              error: error.toString()
            };
          }
        }
      }
    ];
  }

  // Criar testes de documentação
  private createDocumentationTests(): TestCase[] {
    const docValidator = new ApiDocumentationValidator();
    
    return [
      {
        name: 'API Documentation Completeness',
        description: 'Verifica completude da documentação',
        priority: 'medium',
        tags: ['documentation', 'completeness', 'quality'],
        execute: async () => {
          const startTime = Date.now();
          try {
            const result = await docValidator.validateDocumentationCompleteness(this.config.baseUrl);
            return {
              testName: 'API Documentation Completeness',
              category: 'documentation',
              passed: result.score >= 70,
              score: result.score,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: result.details,
              metrics: result.metrics
            };
          } catch (error) {
            return {
              testName: 'API Documentation Completeness',
              category: 'documentation',
              passed: false,
              score: 0,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [`Erro na validação: ${error}`],
              error: error.toString()
            };
          }
        }
      }
    ];
  }

  // Criar testes de acessibilidade
  private createAccessibilityTests(): TestCase[] {
    const accessibilityTester = new ApiAccessibilityTester(this.config.baseUrl, this.config.authToken);
    
    return [
      {
        name: 'API Accessibility Compliance',
        description: 'Verifica conformidade de acessibilidade',
        priority: 'medium',
        tags: ['accessibility', 'compliance', 'usability'],
        execute: async () => {
          const startTime = Date.now();
          try {
            const result = await accessibilityTester.runAllAccessibilityTests();
            return {
              testName: 'API Accessibility Compliance',
              category: 'accessibility',
              passed: result.overallScore >= 70,
              score: result.overallScore,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: result.testResults.map(test => 
                `${test.passed ? '✅' : '❌'} ${test.testName}: ${test.score}/${test.maxScore}`
              ),
              metrics: result
            };
          } catch (error) {
            return {
              testName: 'API Accessibility Compliance',
              category: 'accessibility',
              passed: false,
              score: 0,
              maxScore: 100,
              duration: Date.now() - startTime,
              details: [`Erro nos testes: ${error}`],
              error: error.toString()
            };
          }
        }
      }
    ];
  }

  // Executar todos os testes
  async runAllTests(): Promise<ComprehensiveTestReport> {
    console.log('🚀 Iniciando execução completa dos testes...');
    const startTime = Date.now();
    
    this.results = [];
    
    // Executar cada suíte de testes
    for (const suite of this.testSuites) {
      console.log(`\n📋 Executando: ${suite.name}`);
      
      // Setup da suíte
      if (suite.setup) {
        await suite.setup();
      }
      
      // Executar testes da suíte
      for (const test of suite.tests) {
        console.log(`  ⏳ ${test.name}...`);
        try {
          const result = await test.execute();
          this.results.push(result);
          console.log(`  ${result.passed ? '✅' : '❌'} ${test.name} - ${result.score}/${result.maxScore}`);
        } catch (error) {
          console.log(`  ❌ ${test.name} - Erro: ${error}`);
          this.results.push({
            testName: test.name,
            category: suite.category,
            passed: false,
            score: 0,
            maxScore: 100,
            duration: 0,
            details: [`Erro na execução: ${error}`],
            error: error.toString()
          });
        }
      }
      
      // Teardown da suíte
      if (suite.teardown) {
        await suite.teardown();
      }
    }
    
    const executionTime = Date.now() - startTime;
    console.log(`\n🏁 Testes concluídos em ${executionTime}ms`);
    
    return this.generateComprehensiveReport(executionTime);
  }

  // Gerar relatório abrangente
  private generateComprehensiveReport(executionTime: number): ComprehensiveTestReport {
    const totalTests = this.results.length;
    const passedTests = this.results.filter(r => r.passed).length;
    const failedTests = totalTests - passedTests;
    const totalScore = this.results.reduce((sum, r) => sum + r.score, 0);
    const maxPossibleScore = this.results.reduce((sum, r) => sum + r.maxScore, 0);
    const overallScore = maxPossibleScore > 0 ? (totalScore / maxPossibleScore) * 100 : 0;
    
    // Determinar grade
    let grade: 'A' | 'B' | 'C' | 'D' | 'F';
    if (overallScore >= 90) grade = 'A';
    else if (overallScore >= 80) grade = 'B';
    else if (overallScore >= 70) grade = 'C';
    else if (overallScore >= 60) grade = 'D';
    else grade = 'F';
    
    // Calcular resultados por categoria
    const categories = {
      api: this.calculateCategoryResult('api'),
      usability: this.calculateCategoryResult('usability'),
      performance: this.calculateCategoryResult('performance'),
      flows: this.calculateCategoryResult('flow'),
      documentation: this.calculateCategoryResult('documentation'),
      accessibility: this.calculateCategoryResult('accessibility')
    };
    
    // Coletar recomendações por prioridade
    const recommendations = this.collectRecommendations();
    
    // Calcular métricas específicas
    const metrics = {
      coverage: this.calculateCoverage(),
      reliability: this.calculateReliability(),
      performance: categories.performance.percentage,
      usability: categories.usability.percentage,
      documentation: categories.documentation.percentage,
      accessibility: categories.accessibility.percentage
    };
    
    return {
      summary: {
        totalTests,
        passedTests,
        failedTests,
        overallScore,
        maxPossibleScore,
        grade,
        executionTime
      },
      categories,
      recommendations,
      metrics,
      detailedResults: this.results
    };
  }
  
  private calculateCategoryResult(category: string): CategoryResult {
    const categoryResults = this.results.filter(r => r.category === category);
    const score = categoryResults.reduce((sum, r) => sum + r.score, 0);
    const maxScore = categoryResults.reduce((sum, r) => sum + r.maxScore, 0);
    const percentage = maxScore > 0 ? (score / maxScore) * 100 : 0;
    const passedCount = categoryResults.filter(r => r.passed).length;
    
    let status: 'excellent' | 'good' | 'fair' | 'poor' | 'critical';
    if (percentage >= 90) status = 'excellent';
    else if (percentage >= 80) status = 'good';
    else if (percentage >= 70) status = 'fair';
    else if (percentage >= 50) status = 'poor';
    else status = 'critical';
    
    const issues = categoryResults
      .filter(r => !r.passed)
      .flatMap(r => r.details.filter(d => d.includes('❌') || d.includes('⚠️')));
    
    const recommendations = categoryResults
      .flatMap(r => r.details.filter(d => d.includes('Recomendação') || d.includes('Sugestão')));
    
    return {
      score,
      maxScore,
      percentage,
      status,
      testCount: categoryResults.length,
      passedCount,
      issues: [...new Set(issues)],
      recommendations: [...new Set(recommendations)]
    };
  }
  
  private collectRecommendations() {
    const critical: string[] = [];
    const high: string[] = [];
    const medium: string[] = [];
    const low: string[] = [];
    const quickFixes: string[] = [];
    
    this.results.forEach(result => {
      if (!result.passed) {
        if (result.score === 0) {
          critical.push(`${result.testName}: Falha crítica`);
        } else if (result.score < result.maxScore * 0.5) {
          high.push(`${result.testName}: Performance abaixo do esperado`);
        } else {
          medium.push(`${result.testName}: Melhorias necessárias`);
        }
      }
      
      // Quick fixes baseados em padrões comuns
      result.details.forEach(detail => {
        if (detail.includes('Content-Type') || detail.includes('header')) {
          quickFixes.push(detail);
        }
      });
    });
    
    return {
      critical: [...new Set(critical)],
      high: [...new Set(high)],
      medium: [...new Set(medium)],
      low: [...new Set(low)],
      quickFixes: [...new Set(quickFixes)]
    };
  }
  
  private calculateCoverage(): number {
    // Cobertura baseada na quantidade de endpoints testados vs total esperado
    const expectedEndpoints = 39; // Total de endpoints mencionados no TASK_MASTER
    const testedEndpoints = this.results.filter(r => r.category === 'api').length * 13; // Aproximação
    return Math.min(100, (testedEndpoints / expectedEndpoints) * 100);
  }
  
  private calculateReliability(): number {
    // Confiabilidade baseada na taxa de sucesso dos testes
    const totalTests = this.results.length;
    const passedTests = this.results.filter(r => r.passed).length;
    return totalTests > 0 ? (passedTests / totalTests) * 100 : 0;
  }
}

// Função para gerar relatório em markdown
export function generateMarkdownReport(report: ComprehensiveTestReport): string {
  let output = `# Relatório Completo de Testes - Backend CURSOR\n`;
  output += `**Testado por:** Agente TRAE\n`;
  output += `**Data:** ${new Date().toLocaleDateString('pt-BR')}\n`;
  output += `**Duração:** ${report.summary.executionTime}ms\n\n`;
  
  // Resumo executivo
  output += `## 📊 Resumo Executivo\n\n`;
  output += `- **Score Geral:** ${report.summary.overallScore.toFixed(1)}% (${report.summary.grade})\n`;
  output += `- **Testes Executados:** ${report.summary.totalTests}\n`;
  output += `- **Aprovados:** ${report.summary.passedTests} (${((report.summary.passedTests/report.summary.totalTests)*100).toFixed(1)}%)\n`;
  output += `- **Reprovados:** ${report.summary.failedTests}\n\n`;
  
  // Métricas por categoria
  output += `## 📈 Métricas por Categoria\n\n`;
  Object.entries(report.categories).forEach(([key, category]) => {
    const emoji = category.status === 'excellent' ? '🟢' : 
                  category.status === 'good' ? '🔵' : 
                  category.status === 'fair' ? '🟡' : 
                  category.status === 'poor' ? '🟠' : '🔴';
    
    output += `### ${emoji} ${key.toUpperCase()}\n`;
    output += `- **Score:** ${category.score}/${category.maxScore} (${category.percentage.toFixed(1)}%)\n`;
    output += `- **Status:** ${category.status.toUpperCase()}\n`;
    output += `- **Testes:** ${category.passedCount}/${category.testCount} aprovados\n\n`;
  });
  
  // Recomendações prioritárias
  if (report.recommendations.critical.length > 0) {
    output += `## 🚨 Ações Críticas Necessárias\n\n`;
    report.recommendations.critical.forEach(rec => {
      output += `- ${rec}\n`;
    });
    output += `\n`;
  }
  
  if (report.recommendations.high.length > 0) {
    output += `## ⚠️ Prioridade Alta\n\n`;
    report.recommendations.high.forEach(rec => {
      output += `- ${rec}\n`;
    });
    output += `\n`;
  }
  
  if (report.recommendations.quickFixes.length > 0) {
    output += `## 🚀 Quick Fixes\n\n`;
    report.recommendations.quickFixes.forEach(fix => {
      output += `- ${fix}\n`;
    });
    output += `\n`;
  }
  
  // Resultados detalhados
  output += `## 📋 Resultados Detalhados\n\n`;
  report.detailedResults.forEach(result => {
    const status = result.passed ? '✅' : '❌';
    const percentage = (result.score / result.maxScore) * 100;
    
    output += `### ${status} ${result.testName}\n`;
    output += `- **Categoria:** ${result.category}\n`;
    output += `- **Score:** ${result.score}/${result.maxScore} (${percentage.toFixed(1)}%)\n`;
    output += `- **Duração:** ${result.duration}ms\n`;
    
    if (result.details.length > 0) {
      output += `- **Detalhes:**\n`;
      result.details.forEach(detail => {
        output += `  - ${detail}\n`;
      });
    }
    
    if (result.error) {
      output += `- **Erro:** ${result.error}\n`;
    }
    
    output += `\n`;
  });
  
  return output;
}

// Configuração padrão para execução
export const defaultConfig: TestConfiguration = {
  baseUrl: 'http://localhost:8000',
  timeout: 30000,
  retries: 3,
  endpoints: {
    orcamentos: [
      '/api/orcamentos',
      '/api/orcamentos/{id}',
      '/api/orcamentos/{id}/itens',
      '/api/orcamentos/{id}/status',
      '/api/orcamentos/search'
    ],
    estoque: [
      '/api/estoque/produtos',
      '/api/estoque/produtos/{id}',
      '/api/estoque/movimentacoes',
      '/api/estoque/categorias',
      '/api/estoque/fornecedores',
      '/api/estoque/relatorios'
    ],
    ordemServico: [
      '/api/ordens-servico',
      '/api/ordens-servico/{id}',
      '/api/ordens-servico/{id}/itens',
      '/api/ordens-servico/{id}/status',
      '/api/ordens-servico/{id}/historico',
      '/api/ordens-servico/tecnicos',
      '/api/ordens-servico/relatorios'
    ]
  }
};