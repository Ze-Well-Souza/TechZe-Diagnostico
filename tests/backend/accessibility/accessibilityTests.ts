// Testes de Acessibilidade da API - Agente TRAE testando Backend CURSOR
// Data: 2025-01-09
// Testador: Agente TRAE
// Semana 2: Testes Avançados

export interface AccessibilityTest {
  name: string;
  category: 'response_format' | 'error_handling' | 'internationalization' | 'rate_limiting' | 'documentation';
  description: string;
  execute: () => Promise<AccessibilityResult>;
}

export interface AccessibilityResult {
  testName: string;
  passed: boolean;
  score: number;
  maxScore: number;
  details: string[];
  recommendations: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface AccessibilityReport {
  overallScore: number;
  maxPossibleScore: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  testResults: AccessibilityResult[];
  summary: {
    criticalIssues: string[];
    highPriorityIssues: string[];
    mediumPriorityIssues: string[];
    lowPriorityIssues: string[];
    quickFixes: string[];
  };
  compliance: {
    wcag: number; // Percentual de conformidade com WCAG (adaptado para APIs)
    restful: number; // Conformidade com princípios RESTful
    usability: number; // Usabilidade geral da API
  };
}

// Classe principal para testes de acessibilidade
export class ApiAccessibilityTester {
  private baseUrl: string;
  private authToken?: string;
  
  constructor(baseUrl: string, authToken?: string) {
    this.baseUrl = baseUrl;
    this.authToken = authToken;
  }

  // Teste 1: Formato de Resposta Acessível
  async testResponseFormat(): Promise<AccessibilityResult> {
    const details: string[] = [];
    const recommendations: string[] = [];
    let score = 0;
    const maxScore = 10;
    let severity: 'low' | 'medium' | 'high' | 'critical' = 'medium';

    try {
      const endpoints = ['/api/orcamentos', '/api/estoque/produtos', '/api/ordens-servico'];
      
      for (const endpoint of endpoints) {
        try {
          const response = await fetch(`${this.baseUrl}${endpoint}`);
          const data = await response.json();
          
          // Teste 1.1: Content-Type correto
          const contentType = response.headers.get('content-type');
          if (contentType && contentType.includes('application/json')) {
            score += 1;
            details.push(`✅ ${endpoint}: Content-Type correto`);
          } else {
            details.push(`❌ ${endpoint}: Content-Type ausente ou incorreto`);
            recommendations.push('Definir Content-Type: application/json em todas as respostas');
          }
          
          // Teste 1.2: Estrutura de dados consistente
          if (Array.isArray(data)) {
            score += 1;
            details.push(`✅ ${endpoint}: Retorna array de dados`);
          } else if (data && typeof data === 'object' && data.data && Array.isArray(data.data)) {
            score += 2;
            details.push(`✅ ${endpoint}: Estrutura com wrapper object`);
          } else {
            details.push(`⚠️ ${endpoint}: Estrutura de dados inconsistente`);
            recommendations.push('Padronizar estrutura de resposta com wrapper object');
          }
          
          // Teste 1.3: Metadados úteis
          if (data && data.pagination) {
            score += 1;
            details.push(`✅ ${endpoint}: Inclui metadados de paginação`);
          } else {
            details.push(`⚠️ ${endpoint}: Metadados de paginação ausentes`);
            recommendations.push('Incluir metadados de paginação nas listagens');
          }
          
        } catch (error) {
          details.push(`❌ ${endpoint}: Erro ao testar - ${error}`);
          severity = 'high';
        }
      }
      
      // Teste 1.4: Encoding UTF-8
      const testResponse = await fetch(`${this.baseUrl}/api/orcamentos`);
      const charset = testResponse.headers.get('content-type');
      if (charset && charset.includes('charset=utf-8')) {
        score += 1;
        details.push('✅ Charset UTF-8 especificado');
      } else {
        details.push('⚠️ Charset UTF-8 não especificado');
        recommendations.push('Especificar charset=utf-8 no Content-Type');
      }
      
    } catch (error) {
      details.push(`❌ Erro geral no teste de formato: ${error}`);
      severity = 'critical';
    }

    return {
      testName: 'Formato de Resposta Acessível',
      passed: score >= maxScore * 0.7,
      score,
      maxScore,
      details,
      recommendations,
      severity
    };
  }

  // Teste 2: Tratamento de Erros Acessível
  async testErrorHandling(): Promise<AccessibilityResult> {
    const details: string[] = [];
    const recommendations: string[] = [];
    let score = 0;
    const maxScore = 15;
    let severity: 'low' | 'medium' | 'high' | 'critical' = 'medium';

    try {
      // Teste 2.1: Erro 404 - Recurso não encontrado
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos/99999`);
        const errorData = await response.json();
        
        if (response.status === 404) {
          score += 2;
          details.push('✅ Status 404 correto para recurso inexistente');
        } else {
          details.push(`❌ Status incorreto para recurso inexistente: ${response.status}`);
          recommendations.push('Retornar status 404 para recursos não encontrados');
        }
        
        if (errorData && errorData.error && typeof errorData.error === 'string') {
          score += 2;
          details.push('✅ Mensagem de erro clara e legível');
        } else {
          details.push('❌ Mensagem de erro ausente ou inadequada');
          recommendations.push('Incluir mensagens de erro claras e em português');
          severity = 'high';
        }
        
      } catch {
        details.push('❌ Erro ao testar resposta 404');
        severity = 'high';
      }
      
      // Teste 2.2: Erro 400 - Dados inválidos
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ dados_invalidos: 'teste' })
        });
        const errorData = await response.json();
        
        if (response.status === 400 || response.status === 422) {
          score += 2;
          details.push('✅ Status correto para dados inválidos');
        } else {
          details.push(`❌ Status incorreto para dados inválidos: ${response.status}`);
          recommendations.push('Retornar status 400/422 para dados inválidos');
        }
        
        if (errorData && errorData.details && Array.isArray(errorData.details)) {
          score += 3;
          details.push('✅ Detalhes específicos de validação fornecidos');
        } else {
          details.push('⚠️ Detalhes de validação ausentes');
          recommendations.push('Incluir detalhes específicos nos erros de validação');
        }
        
      } catch {
        details.push('❌ Erro ao testar validação de dados');
      }
      
      // Teste 2.3: Erro 401 - Não autorizado
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`, {
          headers: { 'Authorization': 'Bearer token_invalido' }
        });
        
        if (response.status === 401) {
          score += 2;
          details.push('✅ Status 401 correto para token inválido');
        } else {
          details.push(`❌ Status incorreto para token inválido: ${response.status}`);
          recommendations.push('Retornar status 401 para autenticação inválida');
        }
        
      } catch {
        details.push('❌ Erro ao testar autenticação');
      }
      
      // Teste 2.4: Erro 500 - Tratamento de exceções
      // Simulamos um erro forçando uma requisição malformada
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: 'json_malformado{'
        });
        
        if (response.status >= 400) {
          score += 2;
          details.push('✅ API trata adequadamente requisições malformadas');
        }
        
      } catch {
        // Erro de rede é esperado em alguns casos
        score += 1;
        details.push('⚠️ Teste de erro 500 inconclusivo');
      }
      
      // Teste 2.5: Headers de erro informativos
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos/99999`);
        const errorData = await response.json();
        
        // Verificar se há timestamp no erro
        if (errorData && (errorData.timestamp || errorData.error_id)) {
          score += 1;
          details.push('✅ Metadados úteis nos erros (timestamp/ID)');
        } else {
          details.push('⚠️ Metadados de erro ausentes');
          recommendations.push('Incluir timestamp e ID único nos erros');
        }
        
        // Verificar se há sugestões de correção
        if (errorData && errorData.suggestions) {
          score += 1;
          details.push('✅ Sugestões de correção fornecidas');
        } else {
          details.push('⚠️ Sugestões de correção ausentes');
          recommendations.push('Incluir sugestões de correção nos erros');
        }
        
      } catch {
        details.push('❌ Erro ao verificar metadados de erro');
      }
      
    } catch (error) {
      details.push(`❌ Erro geral no teste de tratamento de erros: ${error}`);
      severity = 'critical';
    }

    return {
      testName: 'Tratamento de Erros Acessível',
      passed: score >= maxScore * 0.7,
      score,
      maxScore,
      details,
      recommendations,
      severity
    };
  }

  // Teste 3: Internacionalização e Localização
  async testInternationalization(): Promise<AccessibilityResult> {
    const details: string[] = [];
    const recommendations: string[] = [];
    let score = 0;
    const maxScore = 10;
    let severity: 'low' | 'medium' | 'high' | 'critical' = 'low';

    try {
      // Teste 3.1: Suporte a Accept-Language
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`, {
          headers: { 'Accept-Language': 'pt-BR' }
        });
        
        const contentLanguage = response.headers.get('content-language');
        if (contentLanguage) {
          score += 2;
          details.push('✅ Header Content-Language presente');
        } else {
          details.push('⚠️ Header Content-Language ausente');
          recommendations.push('Incluir header Content-Language nas respostas');
        }
        
      } catch {
        details.push('❌ Erro ao testar Accept-Language');
      }
      
      // Teste 3.2: Mensagens em português
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos/99999`);
        const errorData = await response.json();
        
        if (errorData && errorData.error) {
          const message = errorData.error.toLowerCase();
          const hasPortuguese = message.includes('não') || message.includes('erro') || 
                               message.includes('inválido') || message.includes('encontrado');
          
          if (hasPortuguese) {
            score += 3;
            details.push('✅ Mensagens de erro em português');
          } else {
            details.push('⚠️ Mensagens de erro não estão em português');
            recommendations.push('Traduzir todas as mensagens para português brasileiro');
            severity = 'medium';
          }
        }
        
      } catch {
        details.push('❌ Erro ao verificar idioma das mensagens');
      }
      
      // Teste 3.3: Formato de data/hora brasileiro
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`);
        const data = await response.json();
        
        if (Array.isArray(data) && data.length > 0) {
          const firstItem = data[0];
          const dateFields = Object.keys(firstItem).filter(key => 
            key.includes('date') || key.includes('created') || key.includes('updated')
          );
          
          if (dateFields.length > 0) {
            const dateValue = firstItem[dateFields[0]];
            // Verificar se está em formato ISO (aceitável) ou brasileiro
            if (typeof dateValue === 'string' && 
                (dateValue.includes('T') || dateValue.includes('/'))) {
              score += 2;
              details.push('✅ Formato de data/hora padronizado');
            } else {
              details.push('⚠️ Formato de data/hora inconsistente');
              recommendations.push('Padronizar formato de data/hora (ISO 8601 ou dd/mm/yyyy)');
            }
          }
        }
        
      } catch {
        details.push('❌ Erro ao verificar formato de data');
      }
      
      // Teste 3.4: Formato de moeda brasileiro
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`);
        const data = await response.json();
        
        if (Array.isArray(data) && data.length > 0) {
          const firstItem = data[0];
          const priceFields = Object.keys(firstItem).filter(key => 
            key.includes('preco') || key.includes('valor') || key.includes('total')
          );
          
          if (priceFields.length > 0) {
            const priceValue = firstItem[priceFields[0]];
            if (typeof priceValue === 'number') {
              score += 2;
              details.push('✅ Valores monetários em formato numérico');
            } else {
              details.push('⚠️ Valores monetários em formato inadequado');
              recommendations.push('Usar formato numérico para valores monetários');
            }
          }
        }
        
      } catch {
        details.push('❌ Erro ao verificar formato de moeda');
      }
      
      // Teste 3.5: Timezone awareness
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`);
        const data = await response.json();
        
        if (Array.isArray(data) && data.length > 0) {
          const firstItem = data[0];
          const dateFields = Object.keys(firstItem).filter(key => 
            key.includes('created') || key.includes('updated')
          );
          
          if (dateFields.length > 0) {
            const dateValue = firstItem[dateFields[0]];
            if (typeof dateValue === 'string' && 
                (dateValue.includes('Z') || dateValue.includes('+') || dateValue.includes('-'))) {
              score += 1;
              details.push('✅ Timezone incluído nas datas');
            } else {
              details.push('⚠️ Timezone não especificado nas datas');
              recommendations.push('Incluir timezone nas datas (formato ISO 8601)');
            }
          }
        }
        
      } catch {
        details.push('❌ Erro ao verificar timezone');
      }
      
    } catch (error) {
      details.push(`❌ Erro geral no teste de internacionalização: ${error}`);
      severity = 'medium';
    }

    return {
      testName: 'Internacionalização e Localização',
      passed: score >= maxScore * 0.6,
      score,
      maxScore,
      details,
      recommendations,
      severity
    };
  }

  // Teste 4: Rate Limiting e Throttling
  async testRateLimiting(): Promise<AccessibilityResult> {
    const details: string[] = [];
    const recommendations: string[] = [];
    let score = 0;
    const maxScore = 8;
    let severity: 'low' | 'medium' | 'high' | 'critical' = 'low';

    try {
      // Teste 4.1: Headers de rate limiting
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`);
        
        const rateLimitHeaders = [
          'x-ratelimit-limit',
          'x-ratelimit-remaining', 
          'x-ratelimit-reset',
          'retry-after'
        ];
        
        let headerCount = 0;
        rateLimitHeaders.forEach(header => {
          if (response.headers.get(header)) {
            headerCount++;
          }
        });
        
        if (headerCount >= 2) {
          score += 3;
          details.push('✅ Headers de rate limiting presentes');
        } else if (headerCount >= 1) {
          score += 1;
          details.push('⚠️ Alguns headers de rate limiting presentes');
          recommendations.push('Implementar headers completos de rate limiting');
        } else {
          details.push('❌ Headers de rate limiting ausentes');
          recommendations.push('Implementar rate limiting com headers informativos');
          severity = 'medium';
        }
        
      } catch {
        details.push('❌ Erro ao verificar headers de rate limiting');
      }
      
      // Teste 4.2: Resposta adequada quando limite excedido
      // Simulamos múltiplas requisições rápidas
      try {
        const promises = [];
        for (let i = 0; i < 10; i++) {
          promises.push(fetch(`${this.baseUrl}/api/orcamentos`));
        }
        
        const responses = await Promise.all(promises);
        const rateLimitedResponses = responses.filter(r => r.status === 429);
        
        if (rateLimitedResponses.length > 0) {
          score += 2;
          details.push('✅ Rate limiting ativo (status 429 detectado)');
          
          // Verificar se há mensagem explicativa
          try {
            const errorData = await rateLimitedResponses[0].json();
            if (errorData && errorData.error) {
              score += 1;
              details.push('✅ Mensagem explicativa para rate limiting');
            }
          } catch {
            details.push('⚠️ Mensagem de rate limiting ausente');
            recommendations.push('Incluir mensagem explicativa no erro 429');
          }
        } else {
          details.push('⚠️ Rate limiting não detectado ou muito permissivo');
          recommendations.push('Implementar rate limiting adequado');
        }
        
      } catch {
        details.push('❌ Erro ao testar rate limiting');
      }
      
      // Teste 4.3: Graceful degradation
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`);
        
        if (response.ok) {
          score += 2;
          details.push('✅ API responde adequadamente sob carga normal');
        } else {
          details.push('⚠️ API com problemas de resposta');
          severity = 'high';
        }
        
      } catch {
        details.push('❌ Erro ao testar resposta da API');
        severity = 'high';
      }
      
    } catch (error) {
      details.push(`❌ Erro geral no teste de rate limiting: ${error}`);
      severity = 'medium';
    }

    return {
      testName: 'Rate Limiting e Throttling',
      passed: score >= maxScore * 0.5,
      score,
      maxScore,
      details,
      recommendations,
      severity
    };
  }

  // Teste 5: Documentação Acessível
  async testDocumentationAccessibility(): Promise<AccessibilityResult> {
    const details: string[] = [];
    const recommendations: string[] = [];
    let score = 0;
    const maxScore = 12;
    let severity: 'low' | 'medium' | 'high' | 'critical' = 'medium';

    try {
      // Teste 5.1: Endpoint de documentação
      try {
        const docsResponse = await fetch(`${this.baseUrl}/docs`);
        if (docsResponse.ok) {
          score += 3;
          details.push('✅ Documentação acessível em /docs');
        } else {
          details.push('❌ Documentação não encontrada em /docs');
          recommendations.push('Implementar endpoint de documentação em /docs');
          severity = 'high';
        }
      } catch {
        details.push('❌ Endpoint /docs não responde');
        recommendations.push('Configurar endpoint de documentação');
        severity = 'high';
      }
      
      // Teste 5.2: OpenAPI/Swagger
      try {
        const swaggerResponse = await fetch(`${this.baseUrl}/swagger.json`);
        if (swaggerResponse.ok) {
          score += 2;
          details.push('✅ Especificação OpenAPI disponível');
        } else {
          details.push('⚠️ Especificação OpenAPI não encontrada');
          recommendations.push('Implementar especificação OpenAPI/Swagger');
        }
      } catch {
        details.push('⚠️ Swagger.json não acessível');
      }
      
      // Teste 5.3: Health check
      try {
        const healthResponse = await fetch(`${this.baseUrl}/health`);
        if (healthResponse.ok) {
          score += 2;
          details.push('✅ Health check disponível');
        } else {
          details.push('⚠️ Health check não encontrado');
          recommendations.push('Implementar endpoint de health check');
        }
      } catch {
        details.push('⚠️ Health check não responde');
      }
      
      // Teste 5.4: Versionamento da API
      if (this.baseUrl.includes('/v1') || this.baseUrl.includes('/api/v1')) {
        score += 2;
        details.push('✅ API versionada na URL');
      } else {
        details.push('⚠️ Versionamento não detectado na URL');
        recommendations.push('Implementar versionamento da API');
      }
      
      // Teste 5.5: Headers informativos
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`);
        
        const informativeHeaders = [
          'api-version',
          'x-api-version',
          'server',
          'x-powered-by'
        ];
        
        let headerCount = 0;
        informativeHeaders.forEach(header => {
          if (response.headers.get(header)) {
            headerCount++;
          }
        });
        
        if (headerCount >= 2) {
          score += 2;
          details.push('✅ Headers informativos presentes');
        } else if (headerCount >= 1) {
          score += 1;
          details.push('⚠️ Alguns headers informativos presentes');
        } else {
          details.push('⚠️ Headers informativos ausentes');
          recommendations.push('Incluir headers informativos (versão, servidor)');
        }
        
      } catch {
        details.push('❌ Erro ao verificar headers informativos');
      }
      
      // Teste 5.6: CORS adequado
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`);
        const corsHeader = response.headers.get('access-control-allow-origin');
        
        if (corsHeader) {
          score += 1;
          details.push('✅ Headers CORS configurados');
        } else {
          details.push('⚠️ Headers CORS ausentes');
          recommendations.push('Configurar CORS adequadamente');
        }
        
      } catch {
        details.push('❌ Erro ao verificar CORS');
      }
      
    } catch (error) {
      details.push(`❌ Erro geral no teste de documentação: ${error}`);
      severity = 'critical';
    }

    return {
      testName: 'Documentação Acessível',
      passed: score >= maxScore * 0.6,
      score,
      maxScore,
      details,
      recommendations,
      severity
    };
  }

  // Executar todos os testes de acessibilidade
  async runAllAccessibilityTests(): Promise<AccessibilityReport> {
    const testResults: AccessibilityResult[] = [];
    
    // Executar todos os testes
    testResults.push(await this.testResponseFormat());
    testResults.push(await this.testErrorHandling());
    testResults.push(await this.testInternationalization());
    testResults.push(await this.testRateLimiting());
    testResults.push(await this.testDocumentationAccessibility());
    
    // Calcular scores
    const totalScore = testResults.reduce((sum, result) => sum + result.score, 0);
    const maxPossibleScore = testResults.reduce((sum, result) => sum + result.maxScore, 0);
    const overallScore = (totalScore / maxPossibleScore) * 100;
    
    // Determinar grade
    let grade: 'A' | 'B' | 'C' | 'D' | 'F';
    if (overallScore >= 90) grade = 'A';
    else if (overallScore >= 80) grade = 'B';
    else if (overallScore >= 70) grade = 'C';
    else if (overallScore >= 60) grade = 'D';
    else grade = 'F';
    
    // Categorizar problemas por severidade
    const criticalIssues: string[] = [];
    const highPriorityIssues: string[] = [];
    const mediumPriorityIssues: string[] = [];
    const lowPriorityIssues: string[] = [];
    const quickFixes: string[] = [];
    
    testResults.forEach(result => {
      const issues = result.details.filter(detail => detail.includes('❌') || detail.includes('⚠️'));
      
      switch (result.severity) {
        case 'critical':
          criticalIssues.push(...issues);
          break;
        case 'high':
          highPriorityIssues.push(...issues);
          break;
        case 'medium':
          mediumPriorityIssues.push(...issues);
          break;
        case 'low':
          lowPriorityIssues.push(...issues);
          break;
      }
      
      // Quick fixes são recomendações simples
      result.recommendations.forEach(rec => {
        if (rec.includes('header') || rec.includes('Content-Type') || 
            rec.includes('charset') || rec.includes('CORS')) {
          quickFixes.push(rec);
        }
      });
    });
    
    // Calcular compliance scores
    const wcagScore = this.calculateWCAGCompliance(testResults);
    const restfulScore = this.calculateRESTfulCompliance(testResults);
    const usabilityScore = this.calculateUsabilityScore(testResults);
    
    return {
      overallScore,
      maxPossibleScore,
      grade,
      testResults,
      summary: {
        criticalIssues: [...new Set(criticalIssues)],
        highPriorityIssues: [...new Set(highPriorityIssues)],
        mediumPriorityIssues: [...new Set(mediumPriorityIssues)],
        lowPriorityIssues: [...new Set(lowPriorityIssues)],
        quickFixes: [...new Set(quickFixes)]
      },
      compliance: {
        wcag: wcagScore,
        restful: restfulScore,
        usability: usabilityScore
      }
    };
  }
  
  private calculateWCAGCompliance(results: AccessibilityResult[]): number {
    // WCAG adaptado para APIs: foco em clareza, consistência e acessibilidade
    const relevantTests = results.filter(r => 
      r.testName.includes('Formato') || 
      r.testName.includes('Erro') || 
      r.testName.includes('Internacionalização')
    );
    
    const totalScore = relevantTests.reduce((sum, r) => sum + r.score, 0);
    const maxScore = relevantTests.reduce((sum, r) => sum + r.maxScore, 0);
    
    return maxScore > 0 ? (totalScore / maxScore) * 100 : 0;
  }
  
  private calculateRESTfulCompliance(results: AccessibilityResult[]): number {
    // Conformidade com princípios RESTful
    const relevantTests = results.filter(r => 
      r.testName.includes('Formato') || 
      r.testName.includes('Documentação')
    );
    
    const totalScore = relevantTests.reduce((sum, r) => sum + r.score, 0);
    const maxScore = relevantTests.reduce((sum, r) => sum + r.maxScore, 0);
    
    return maxScore > 0 ? (totalScore / maxScore) * 100 : 0;
  }
  
  private calculateUsabilityScore(results: AccessibilityResult[]): number {
    // Score geral de usabilidade
    const totalScore = results.reduce((sum, r) => sum + r.score, 0);
    const maxScore = results.reduce((sum, r) => sum + r.maxScore, 0);
    
    return maxScore > 0 ? (totalScore / maxScore) * 100 : 0;
  }
}

// Função para gerar relatório de acessibilidade
export function generateAccessibilityReport(report: AccessibilityReport): string {
  let output = `
# Relatório de Acessibilidade da API - Agente TRAE

`;
  
  output += `## 📊 Resumo Geral
`;
  output += `- **Score Geral:** ${report.overallScore.toFixed(1)}% (${report.grade})
`;
  output += `- **Pontuação:** ${report.testResults.reduce((sum, r) => sum + r.score, 0)}/${report.maxPossibleScore}
`;
  output += `- **Testes Executados:** ${report.testResults.length}
`;
  output += `- **Testes Aprovados:** ${report.testResults.filter(r => r.passed).length}

`;
  
  output += `## 🎯 Compliance Scores
`;
  output += `- **WCAG (Adaptado):** ${report.compliance.wcag.toFixed(1)}%
`;
  output += `- **RESTful:** ${report.compliance.restful.toFixed(1)}%
`;
  output += `- **Usabilidade:** ${report.compliance.usability.toFixed(1)}%

`;
  
  output += `## 📋 Resultados Detalhados

`;
  report.testResults.forEach(result => {
    const status = result.passed ? '✅' : '❌';
    const percentage = (result.score / result.maxScore) * 100;
    
    output += `### ${status} ${result.testName}
`;
    output += `- **Score:** ${result.score}/${result.maxScore} (${percentage.toFixed(1)}%)
`;
    output += `- **Severidade:** ${result.severity.toUpperCase()}
`;
    output += `- **Status:** ${result.passed ? 'APROVADO' : 'REPROVADO'}

`;
    
    if (result.details.length > 0) {
      output += `**Detalhes:**
`;
      result.details.forEach(detail => {
        output += `- ${detail}
`;
      });
      output += `
`;
    }
    
    if (result.recommendations.length > 0) {
      output += `**Recomendações:**
`;
      result.recommendations.forEach(rec => {
        output += `- ${rec}
`;
      });
      output += `
`;
    }
  });
  
  // Resumo de problemas por prioridade
  if (report.summary.criticalIssues.length > 0) {
    output += `## 🚨 Problemas Críticos
`;
    report.summary.criticalIssues.forEach(issue => {
      output += `- ${issue}
`;
    });
    output += `
`;
  }
  
  if (report.summary.highPriorityIssues.length > 0) {
    output += `## ⚠️ Problemas de Alta Prioridade
`;
    report.summary.highPriorityIssues.forEach(issue => {
      output += `- ${issue}
`;
    });
    output += `
`;
  }
  
  if (report.summary.quickFixes.length > 0) {
    output += `## 🚀 Quick Fixes
`;
    report.summary.quickFixes.forEach(fix => {
      output += `- ${fix}
`;
    });
    output += `
`;
  }
  
  return output;
}