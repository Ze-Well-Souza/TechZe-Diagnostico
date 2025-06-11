// Métricas de Usabilidade - Agente TRAE testando Backend CURSOR
// Data: 2025-01-09
// Testador: Agente TRAE

export interface UsabilityMetric {
  name: string;
  score: number;
  maxScore: number;
  weight: number;
  details: string[];
  recommendations: string[];
}

export interface UsabilityReport {
  overallScore: number;
  maxPossibleScore: number;
  weightedScore: number;
  grade: 'A' | 'B' | 'C' | 'D' | 'F';
  metrics: UsabilityMetric[];
  summary: {
    strengths: string[];
    weaknesses: string[];
    criticalIssues: string[];
    quickWins: string[];
  };
}

export interface ApiUsabilityTest {
  endpoint: string;
  method: string;
  testName: string;
  category: 'discoverability' | 'learnability' | 'efficiency' | 'memorability' | 'error_prevention' | 'satisfaction';
  execute: () => Promise<UsabilityMetric>;
}

// Classe principal para métricas de usabilidade
export class UsabilityMetrics {
  private baseUrl: string;
  private authToken?: string;
  
  constructor(baseUrl: string, authToken?: string) {
    this.baseUrl = baseUrl;
    this.authToken = authToken;
  }

  // Métrica 1: Descobribilidade (Discoverability)
  async measureDiscoverability(): Promise<UsabilityMetric> {
    const details: string[] = [];
    const recommendations: string[] = [];
    let score = 0;
    const maxScore = 10;

    try {
      // Teste 1: Endpoint de documentação existe?
      try {
        const docsResponse = await fetch(`${this.baseUrl}/docs`);
        if (docsResponse.ok) {
          score += 2;
          details.push('✅ Documentação acessível em /docs');
        } else {
          details.push('❌ Documentação não encontrada em /docs');
          recommendations.push('Implementar endpoint de documentação em /docs');
        }
      } catch {
        details.push('❌ Endpoint /docs não responde');
        recommendations.push('Configurar endpoint de documentação');
      }

      // Teste 2: Endpoint de health check existe?
      try {
        const healthResponse = await fetch(`${this.baseUrl}/health`);
        if (healthResponse.ok) {
          score += 1;
          details.push('✅ Health check disponível');
        } else {
          details.push('❌ Health check não encontrado');
          recommendations.push('Implementar endpoint de health check');
        }
      } catch {
        details.push('❌ Health check não responde');
        recommendations.push('Configurar health check');
      }

      // Teste 3: Estrutura de URLs é intuitiva?
      const endpoints = [
        '/api/orcamentos',
        '/api/estoque/produtos', 
        '/api/ordens-servico'
      ];
      
      let intuitiveUrls = 0;
      for (const endpoint of endpoints) {
        // URLs RESTful são mais intuitivas
        if (endpoint.includes('/api/') && !endpoint.includes('_')) {
          intuitiveUrls++;
        }
      }
      
      const urlScore = (intuitiveUrls / endpoints.length) * 3;
      score += urlScore;
      
      if (urlScore >= 2.5) {
        details.push('✅ URLs seguem padrões RESTful');
      } else {
        details.push('⚠️ URLs poderiam ser mais intuitivas');
        recommendations.push('Adotar padrões RESTful para URLs');
      }

      // Teste 4: Métodos HTTP apropriados?
      const methodTests = [
        { url: '/api/orcamentos', method: 'GET', expected: true },
        { url: '/api/orcamentos', method: 'POST', expected: true },
        { url: '/api/orcamentos/1', method: 'PUT', expected: true },
        { url: '/api/orcamentos/1', method: 'DELETE', expected: true }
      ];
      
      let correctMethods = 0;
      for (const test of methodTests) {
        try {
          const response = await fetch(`${this.baseUrl}${test.url}`, {
            method: test.method,
            headers: this.authToken ? { 'Authorization': `Bearer ${this.authToken}` } : {}
          });
          
          // 405 = Method Not Allowed (método não implementado)
          // 401/403 = Auth required (método existe mas precisa auth)
          // 200-299 = Success
          // 400-499 = Client error (método existe)
          if (response.status !== 405) {
            correctMethods++;
          }
        } catch {
          // Erro de rede não conta como método não implementado
          correctMethods++;
        }
      }
      
      const methodScore = (correctMethods / methodTests.length) * 2;
      score += methodScore;
      
      if (methodScore >= 1.5) {
        details.push('✅ Métodos HTTP implementados adequadamente');
      } else {
        details.push('⚠️ Alguns métodos HTTP não implementados');
        recommendations.push('Implementar todos os métodos CRUD necessários');
      }

      // Teste 5: Versionamento da API?
      if (this.baseUrl.includes('/v1') || this.baseUrl.includes('/api/v1')) {
        score += 2;
        details.push('✅ API versionada');
      } else {
        details.push('⚠️ Versionamento da API não detectado');
        recommendations.push('Implementar versionamento da API');
      }

    } catch (error) {
      details.push(`❌ Erro durante teste de descobribilidade: ${error}`);
      recommendations.push('Verificar conectividade com a API');
    }

    return {
      name: 'Descobribilidade',
      score,
      maxScore,
      weight: 0.2,
      details,
      recommendations
    };
  }

  // Métrica 2: Facilidade de Aprendizado (Learnability)
  async measureLearnability(): Promise<UsabilityMetric> {
    const details: string[] = [];
    const recommendations: string[] = [];
    let score = 0;
    const maxScore = 10;

    try {
      // Teste 1: Consistência de nomenclatura
      const endpoints = ['/api/orcamentos', '/api/estoque/produtos', '/api/ordens-servico'];
      let consistentNaming = true;
      
      for (const endpoint of endpoints) {
        try {
          const response = await fetch(`${this.baseUrl}${endpoint}`);
          const data = await response.json();
          
          if (Array.isArray(data) && data.length > 0) {
            const firstItem = data[0];
            const keys = Object.keys(firstItem);
            
            // Verifica se usa snake_case ou camelCase consistentemente
            const hasSnakeCase = keys.some(key => key.includes('_'));
            const hasCamelCase = keys.some(key => /[a-z][A-Z]/.test(key));
            
            if (hasSnakeCase && hasCamelCase) {
              consistentNaming = false;
              break;
            }
          }
        } catch {
          // Ignora erros de conectividade para este teste
        }
      }
      
      if (consistentNaming) {
        score += 3;
        details.push('✅ Nomenclatura consistente entre endpoints');
      } else {
        details.push('❌ Nomenclatura inconsistente detectada');
        recommendations.push('Padronizar nomenclatura (snake_case ou camelCase)');
      }

      // Teste 2: Estrutura de resposta padronizada
      let standardResponse = true;
      const responseStructures: any[] = [];
      
      for (const endpoint of endpoints) {
        try {
          const response = await fetch(`${this.baseUrl}${endpoint}`);
          const data = await response.json();
          
          responseStructures.push({
            endpoint,
            isArray: Array.isArray(data),
            hasMetadata: data && typeof data === 'object' && ('meta' in data || 'pagination' in data),
            structure: typeof data
          });
        } catch {
          // Ignora erros para este teste
        }
      }
      
      // Verifica se todas as respostas seguem o mesmo padrão
      if (responseStructures.length > 1) {
        const firstStructure = responseStructures[0];
        standardResponse = responseStructures.every(struct => 
          struct.isArray === firstStructure.isArray &&
          struct.structure === firstStructure.structure
        );
      }
      
      if (standardResponse) {
        score += 2;
        details.push('✅ Estrutura de resposta padronizada');
      } else {
        details.push('⚠️ Estruturas de resposta inconsistentes');
        recommendations.push('Padronizar estrutura de resposta entre endpoints');
      }

      // Teste 3: Códigos de erro claros
      try {
        const invalidData = { invalid: 'data' };
        const response = await fetch(`${this.baseUrl}/api/orcamentos`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(invalidData)
        });
        
        const errorData = await response.json();
        
        if (errorData && errorData.message) {
          score += 2;
          details.push('✅ Mensagens de erro descritivas');
        } else {
          details.push('⚠️ Mensagens de erro pouco claras');
          recommendations.push('Implementar mensagens de erro mais descritivas');
        }
        
        if (errorData && errorData.details) {
          score += 1;
          details.push('✅ Detalhes de validação presentes');
        } else {
          details.push('⚠️ Detalhes de validação ausentes');
          recommendations.push('Incluir detalhes específicos nos erros de validação');
        }
        
      } catch {
        details.push('⚠️ Não foi possível testar tratamento de erros');
        recommendations.push('Verificar implementação de tratamento de erros');
      }

      // Teste 4: Documentação inline (headers, etc.)
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`);
        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('application/json')) {
          score += 1;
          details.push('✅ Content-Type apropriado');
        } else {
          details.push('⚠️ Content-Type não especificado ou inadequado');
          recommendations.push('Especificar Content-Type adequado nas respostas');
        }
        
        // Verifica se há headers informativos
        const apiVersion = response.headers.get('api-version') || response.headers.get('x-api-version');
        if (apiVersion) {
          score += 1;
          details.push('✅ Versão da API informada nos headers');
        } else {
          details.push('⚠️ Versão da API não informada nos headers');
          recommendations.push('Incluir versão da API nos headers de resposta');
        }
        
      } catch {
        details.push('⚠️ Não foi possível verificar headers de resposta');
      }

    } catch (error) {
      details.push(`❌ Erro durante teste de facilidade de aprendizado: ${error}`);
      recommendations.push('Verificar implementação da API');
    }

    return {
      name: 'Facilidade de Aprendizado',
      score,
      maxScore,
      weight: 0.25,
      details,
      recommendations
    };
  }

  // Métrica 3: Eficiência (Efficiency)
  async measureEfficiency(): Promise<UsabilityMetric> {
    const details: string[] = [];
    const recommendations: string[] = [];
    let score = 0;
    const maxScore = 10;

    try {
      // Teste 1: Tempo de resposta
      const endpoints = ['/api/orcamentos', '/api/estoque/produtos', '/api/ordens-servico'];
      let totalResponseTime = 0;
      let successfulTests = 0;
      
      for (const endpoint of endpoints) {
        try {
          const startTime = performance.now();
          const response = await fetch(`${this.baseUrl}${endpoint}`);
          const endTime = performance.now();
          const responseTime = endTime - startTime;
          
          totalResponseTime += responseTime;
          successfulTests++;
          
          if (responseTime < 200) {
            details.push(`✅ ${endpoint}: Excelente (${responseTime.toFixed(2)}ms)`);
          } else if (responseTime < 500) {
            details.push(`✅ ${endpoint}: Bom (${responseTime.toFixed(2)}ms)`);
          } else {
            details.push(`⚠️ ${endpoint}: Lento (${responseTime.toFixed(2)}ms)`);
          }
        } catch {
          details.push(`❌ ${endpoint}: Erro de conectividade`);
        }
      }
      
      if (successfulTests > 0) {
        const avgResponseTime = totalResponseTime / successfulTests;
        
        if (avgResponseTime < 200) {
          score += 4;
        } else if (avgResponseTime < 500) {
          score += 3;
        } else if (avgResponseTime < 1000) {
          score += 2;
        } else {
          score += 1;
          recommendations.push('Otimizar performance dos endpoints');
        }
      }

      // Teste 2: Paginação eficiente
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos?page=1&limit=10`);
        const data = await response.json();
        
        if (data && (data.pagination || data.meta)) {
          score += 2;
          details.push('✅ Paginação implementada');
        } else {
          details.push('⚠️ Paginação não detectada');
          recommendations.push('Implementar paginação para listas grandes');
        }
      } catch {
        details.push('⚠️ Não foi possível testar paginação');
      }

      // Teste 3: Filtros e busca
      try {
        const searchResponse = await fetch(`${this.baseUrl}/api/estoque/produtos?search=teste`);
        if (searchResponse.ok) {
          score += 2;
          details.push('✅ Funcionalidade de busca disponível');
        } else {
          details.push('⚠️ Busca não implementada');
          recommendations.push('Implementar funcionalidade de busca');
        }
      } catch {
        details.push('⚠️ Não foi possível testar busca');
      }

      // Teste 4: Compressão de resposta
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`, {
          headers: { 'Accept-Encoding': 'gzip, deflate' }
        });
        
        const contentEncoding = response.headers.get('content-encoding');
        if (contentEncoding && (contentEncoding.includes('gzip') || contentEncoding.includes('deflate'))) {
          score += 1;
          details.push('✅ Compressão de resposta ativa');
        } else {
          details.push('⚠️ Compressão de resposta não detectada');
          recommendations.push('Implementar compressão de resposta (gzip)');
        }
      } catch {
        details.push('⚠️ Não foi possível testar compressão');
      }

      // Teste 5: Cache headers
      try {
        const response = await fetch(`${this.baseUrl}/api/orcamentos`);
        const cacheControl = response.headers.get('cache-control');
        const etag = response.headers.get('etag');
        
        if (cacheControl || etag) {
          score += 1;
          details.push('✅ Headers de cache presentes');
        } else {
          details.push('⚠️ Headers de cache ausentes');
          recommendations.push('Implementar headers de cache apropriados');
        }
      } catch {
        details.push('⚠️ Não foi possível verificar cache headers');
      }

    } catch (error) {
      details.push(`❌ Erro durante teste de eficiência: ${error}`);
      recommendations.push('Verificar configuração de performance da API');
    }

    return {
      name: 'Eficiência',
      score,
      maxScore,
      weight: 0.3,
      details,
      recommendations
    };
  }

  // Função principal para gerar relatório completo
  async generateUsabilityReport(): Promise<UsabilityReport> {
    const metrics: UsabilityMetric[] = [];
    
    // Executar todas as métricas
    metrics.push(await this.measureDiscoverability());
    metrics.push(await this.measureLearnability());
    metrics.push(await this.measureEfficiency());
    
    // Calcular scores
    const totalScore = metrics.reduce((sum, metric) => sum + metric.score, 0);
    const maxPossibleScore = metrics.reduce((sum, metric) => sum + metric.maxScore, 0);
    const weightedScore = metrics.reduce((sum, metric) => sum + (metric.score * metric.weight), 0);
    const maxWeightedScore = metrics.reduce((sum, metric) => sum + (metric.maxScore * metric.weight), 0);
    
    const overallScore = (totalScore / maxPossibleScore) * 100;
    
    // Determinar grade
    let grade: 'A' | 'B' | 'C' | 'D' | 'F';
    if (overallScore >= 90) grade = 'A';
    else if (overallScore >= 80) grade = 'B';
    else if (overallScore >= 70) grade = 'C';
    else if (overallScore >= 60) grade = 'D';
    else grade = 'F';
    
    // Analisar pontos fortes e fracos
    const strengths: string[] = [];
    const weaknesses: string[] = [];
    const criticalIssues: string[] = [];
    const quickWins: string[] = [];
    
    metrics.forEach(metric => {
      const percentage = (metric.score / metric.maxScore) * 100;
      
      if (percentage >= 80) {
        strengths.push(`${metric.name}: ${percentage.toFixed(1)}%`);
      } else if (percentage < 50) {
        weaknesses.push(`${metric.name}: ${percentage.toFixed(1)}%`);
        
        if (percentage < 30) {
          criticalIssues.push(`${metric.name} precisa de atenção urgente`);
        }
      }
      
      // Quick wins são recomendações fáceis de implementar
      metric.recommendations.forEach(rec => {
        if (rec.includes('header') || rec.includes('Content-Type') || rec.includes('versionamento')) {
          quickWins.push(rec);
        }
      });
    });
    
    return {
      overallScore,
      maxPossibleScore,
      weightedScore: (weightedScore / maxWeightedScore) * 100,
      grade,
      metrics,
      summary: {
        strengths,
        weaknesses,
        criticalIssues,
        quickWins: [...new Set(quickWins)] // Remove duplicatas
      }
    };
  }
}

// Função utilitária para formatar relatório
export function formatUsabilityReport(report: UsabilityReport): string {
  let output = `
# Relatório de Usabilidade da API - Agente TRAE

`;
  
  output += `## 📊 Resumo Geral
`;
  output += `- **Score Geral:** ${report.overallScore.toFixed(1)}% (${report.grade})
`;
  output += `- **Score Ponderado:** ${report.weightedScore.toFixed(1)}%
`;
  output += `- **Pontuação:** ${report.metrics.reduce((sum, m) => sum + m.score, 0)}/${report.maxPossibleScore}

`;
  
  output += `## 🎯 Métricas Detalhadas

`;
  report.metrics.forEach(metric => {
    const percentage = (metric.score / metric.maxScore) * 100;
    output += `### ${metric.name}
`;
    output += `- **Score:** ${metric.score}/${metric.maxScore} (${percentage.toFixed(1)}%)
`;
    output += `- **Peso:** ${(metric.weight * 100).toFixed(0)}%

`;
    
    if (metric.details.length > 0) {
      output += `**Detalhes:**
`;
      metric.details.forEach(detail => {
        output += `- ${detail}
`;
      });
      output += `
`;
    }
    
    if (metric.recommendations.length > 0) {
      output += `**Recomendações:**
`;
      metric.recommendations.forEach(rec => {
        output += `- ${rec}
`;
      });
      output += `
`;
    }
  });
  
  output += `## 📈 Análise

`;
  
  if (report.summary.strengths.length > 0) {
    output += `### ✅ Pontos Fortes
`;
    report.summary.strengths.forEach(strength => {
      output += `- ${strength}
`;
    });
    output += `
`;
  }
  
  if (report.summary.weaknesses.length > 0) {
    output += `### ⚠️ Pontos Fracos
`;
    report.summary.weaknesses.forEach(weakness => {
      output += `- ${weakness}
`;
    });
    output += `
`;
  }
  
  if (report.summary.criticalIssues.length > 0) {
    output += `### 🚨 Questões Críticas
`;
    report.summary.criticalIssues.forEach(issue => {
      output += `- ${issue}
`;
    });
    output += `
`;
  }
  
  if (report.summary.quickWins.length > 0) {
    output += `### 🚀 Quick Wins
`;
    report.summary.quickWins.forEach(win => {
      output += `- ${win}
`;
    });
    output += `
`;
  }
  
  return output;
}