// Testes de Fluxo de Usuário - Agente TRAE testando Backend CURSOR
// Data: 2025-01-09
// Testador: Agente TRAE

export interface FlowStep {
  name: string;
  endpoint: string;
  method: string;
  payload?: any;
  expectedStatus: number;
  expectedResponse?: any;
  validation: (response: any) => boolean;
  timing?: number;
}

export interface UserFlow {
  name: string;
  description: string;
  category: 'orcamento' | 'estoque' | 'ordem_servico' | 'integration';
  steps: FlowStep[];
  prerequisites?: string[];
  expectedDuration: number; // em ms
  criticalPath: boolean;
}

export interface FlowResult {
  flowName: string;
  success: boolean;
  totalTime: number;
  stepResults: {
    stepName: string;
    success: boolean;
    responseTime: number;
    statusCode: number;
    error?: string;
  }[];
  issues: string[];
  recommendations: string[];
}

// Classe principal para testes de fluxo
export class UserFlowTester {
  private baseUrl: string;
  private authToken?: string;
  
  constructor(baseUrl: string, authToken?: string) {
    this.baseUrl = baseUrl;
    this.authToken = authToken;
  }

  // Fluxo 1: Criação Completa de Orçamento
  getOrcamentoCreationFlow(): UserFlow {
    return {
      name: 'Criação Completa de Orçamento',
      description: 'Fluxo completo desde a criação até a aprovação de um orçamento',
      category: 'orcamento',
      criticalPath: true,
      expectedDuration: 2000,
      prerequisites: ['Cliente cadastrado', 'Produtos em estoque'],
      steps: [
        {
          name: 'Listar clientes disponíveis',
          endpoint: '/api/clientes',
          method: 'GET',
          expectedStatus: 200,
          validation: (response) => Array.isArray(response) && response.length > 0
        },
        {
          name: 'Buscar produtos para orçamento',
          endpoint: '/api/estoque/produtos',
          method: 'GET',
          expectedStatus: 200,
          validation: (response) => Array.isArray(response) && response.length > 0
        },
        {
          name: 'Criar novo orçamento',
          endpoint: '/api/orcamentos',
          method: 'POST',
          payload: {
            cliente_id: 1,
            descricao: 'Orçamento teste - Agente TRAE',
            itens: [
              {
                produto_id: 1,
                quantidade: 2,
                preco_unitario: 100.00
              }
            ]
          },
          expectedStatus: 201,
          validation: (response) => response && response.id && response.status === 'rascunho'
        },
        {
          name: 'Consultar orçamento criado',
          endpoint: '/api/orcamentos/{id}',
          method: 'GET',
          expectedStatus: 200,
          validation: (response) => response && response.id && response.descricao
        },
        {
          name: 'Atualizar orçamento',
          endpoint: '/api/orcamentos/{id}',
          method: 'PUT',
          payload: {
            descricao: 'Orçamento atualizado - Agente TRAE',
            observacoes: 'Teste de atualização'
          },
          expectedStatus: 200,
          validation: (response) => response && response.descricao.includes('atualizado')
        },
        {
          name: 'Aprovar orçamento',
          endpoint: '/api/orcamentos/{id}/aprovar',
          method: 'POST',
          expectedStatus: 200,
          validation: (response) => response && response.status === 'aprovado'
        }
      ]
    };
  }

  // Fluxo 2: Gestão de Estoque Completa
  getEstoqueManagementFlow(): UserFlow {
    return {
      name: 'Gestão Completa de Estoque',
      description: 'Fluxo de cadastro de produto, entrada e saída de estoque',
      category: 'estoque',
      criticalPath: true,
      expectedDuration: 3000,
      steps: [
        {
          name: 'Listar produtos existentes',
          endpoint: '/api/estoque/produtos',
          method: 'GET',
          expectedStatus: 200,
          validation: (response) => Array.isArray(response)
        },
        {
          name: 'Cadastrar novo produto',
          endpoint: '/api/estoque/produtos',
          method: 'POST',
          payload: {
            nome: 'Produto Teste TRAE',
            descricao: 'Produto criado pelo Agente TRAE para teste',
            preco: 150.00,
            categoria: 'Teste',
            estoque_minimo: 5
          },
          expectedStatus: 201,
          validation: (response) => response && response.id && response.nome
        },
        {
          name: 'Consultar produto criado',
          endpoint: '/api/estoque/produtos/{id}',
          method: 'GET',
          expectedStatus: 200,
          validation: (response) => response && response.nome === 'Produto Teste TRAE'
        },
        {
          name: 'Registrar entrada de estoque',
          endpoint: '/api/estoque/movimentacoes',
          method: 'POST',
          payload: {
            produto_id: '{produto_id}',
            tipo: 'entrada',
            quantidade: 10,
            motivo: 'Compra inicial - Teste TRAE'
          },
          expectedStatus: 201,
          validation: (response) => response && response.tipo === 'entrada'
        },
        {
          name: 'Verificar saldo atualizado',
          endpoint: '/api/estoque/produtos/{id}/saldo',
          method: 'GET',
          expectedStatus: 200,
          validation: (response) => response && response.quantidade >= 10
        },
        {
          name: 'Registrar saída de estoque',
          endpoint: '/api/estoque/movimentacoes',
          method: 'POST',
          payload: {
            produto_id: '{produto_id}',
            tipo: 'saida',
            quantidade: 3,
            motivo: 'Venda teste - TRAE'
          },
          expectedStatus: 201,
          validation: (response) => response && response.tipo === 'saida'
        },
        {
          name: 'Consultar histórico de movimentações',
          endpoint: '/api/estoque/produtos/{id}/movimentacoes',
          method: 'GET',
          expectedStatus: 200,
          validation: (response) => Array.isArray(response) && response.length >= 2
        }
      ]
    };
  }

  // Fluxo 3: Ordem de Serviço Completa
  getOrdemServicoFlow(): UserFlow {
    return {
      name: 'Ordem de Serviço Completa',
      description: 'Fluxo completo de criação, execução e finalização de ordem de serviço',
      category: 'ordem_servico',
      criticalPath: true,
      expectedDuration: 4000,
      prerequisites: ['Cliente cadastrado', 'Técnico disponível'],
      steps: [
        {
          name: 'Listar técnicos disponíveis',
          endpoint: '/api/tecnicos',
          method: 'GET',
          expectedStatus: 200,
          validation: (response) => Array.isArray(response) && response.length > 0
        },
        {
          name: 'Criar nova ordem de serviço',
          endpoint: '/api/ordens-servico',
          method: 'POST',
          payload: {
            cliente_id: 1,
            tecnico_id: 1,
            descricao: 'Manutenção teste - Agente TRAE',
            prioridade: 'media',
            tipo_servico: 'manutencao'
          },
          expectedStatus: 201,
          validation: (response) => response && response.id && response.status === 'aberta'
        },
        {
          name: 'Consultar ordem criada',
          endpoint: '/api/ordens-servico/{id}',
          method: 'GET',
          expectedStatus: 200,
          validation: (response) => response && response.descricao
        },
        {
          name: 'Iniciar execução da ordem',
          endpoint: '/api/ordens-servico/{id}/iniciar',
          method: 'POST',
          expectedStatus: 200,
          validation: (response) => response && response.status === 'em_andamento'
        },
        {
          name: 'Adicionar item de serviço',
          endpoint: '/api/ordens-servico/{id}/itens',
          method: 'POST',
          payload: {
            tipo: 'servico',
            descricao: 'Diagnóstico inicial',
            quantidade: 1,
            preco_unitario: 50.00
          },
          expectedStatus: 201,
          validation: (response) => response && response.tipo === 'servico'
        },
        {
          name: 'Adicionar item de peça',
          endpoint: '/api/ordens-servico/{id}/itens',
          method: 'POST',
          payload: {
            tipo: 'peca',
            produto_id: 1,
            quantidade: 1,
            preco_unitario: 25.00
          },
          expectedStatus: 201,
          validation: (response) => response && response.tipo === 'peca'
        },
        {
          name: 'Finalizar ordem de serviço',
          endpoint: '/api/ordens-servico/{id}/finalizar',
          method: 'POST',
          payload: {
            observacoes: 'Serviço concluído com sucesso - Teste TRAE'
          },
          expectedStatus: 200,
          validation: (response) => response && response.status === 'finalizada'
        },
        {
          name: 'Gerar relatório da ordem',
          endpoint: '/api/ordens-servico/{id}/relatorio',
          method: 'GET',
          expectedStatus: 200,
          validation: (response) => response && response.total_servicos && response.total_pecas
        }
      ]
    };
  }

  // Fluxo 4: Integração entre Módulos
  getIntegrationFlow(): UserFlow {
    return {
      name: 'Integração entre Módulos',
      description: 'Teste de integração entre orçamento, estoque e ordem de serviço',
      category: 'integration',
      criticalPath: true,
      expectedDuration: 5000,
      steps: [
        {
          name: 'Criar orçamento com produtos',
          endpoint: '/api/orcamentos',
          method: 'POST',
          payload: {
            cliente_id: 1,
            descricao: 'Orçamento para integração - TRAE',
            itens: [{ produto_id: 1, quantidade: 2, preco_unitario: 100.00 }]
          },
          expectedStatus: 201,
          validation: (response) => response && response.id
        },
        {
          name: 'Aprovar orçamento',
          endpoint: '/api/orcamentos/{orcamento_id}/aprovar',
          method: 'POST',
          expectedStatus: 200,
          validation: (response) => response && response.status === 'aprovado'
        },
        {
          name: 'Converter orçamento em ordem de serviço',
          endpoint: '/api/orcamentos/{orcamento_id}/converter-ordem',
          method: 'POST',
          payload: {
            tecnico_id: 1,
            observacoes: 'Conversão automática - Teste TRAE'
          },
          expectedStatus: 201,
          validation: (response) => response && response.ordem_servico_id
        },
        {
          name: 'Verificar baixa automática no estoque',
          endpoint: '/api/estoque/produtos/1/saldo',
          method: 'GET',
          expectedStatus: 200,
          validation: (response) => response && typeof response.quantidade === 'number'
        },
        {
          name: 'Consultar histórico de movimentações',
          endpoint: '/api/estoque/produtos/1/movimentacoes',
          method: 'GET',
          expectedStatus: 200,
          validation: (response) => Array.isArray(response) && 
            response.some(mov => mov.motivo && mov.motivo.includes('ordem'))
        }
      ]
    };
  }

  // Executar um fluxo específico
  async executeFlow(flow: UserFlow): Promise<FlowResult> {
    const startTime = performance.now();
    const stepResults: FlowResult['stepResults'] = [];
    const issues: string[] = [];
    const recommendations: string[] = [];
    let success = true;
    
    // Variáveis para armazenar IDs criados durante o fluxo
    const createdIds: { [key: string]: any } = {};
    
    for (const step of flow.steps) {
      const stepStartTime = performance.now();
      
      try {
        // Substituir placeholders nos endpoints e payloads
        let endpoint = step.endpoint;
        let payload = step.payload;
        
        // Substituir IDs nos endpoints
        Object.keys(createdIds).forEach(key => {
          endpoint = endpoint.replace(`{${key}}`, createdIds[key]);
          if (payload) {
            payload = JSON.parse(JSON.stringify(payload).replace(`{${key}}`, createdIds[key]));
          }
        });
        
        // Fazer a requisição
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
          method: step.method,
          headers: {
            'Content-Type': 'application/json',
            ...(this.authToken ? { 'Authorization': `Bearer ${this.authToken}` } : {})
          },
          body: payload ? JSON.stringify(payload) : undefined
        });
        
        const stepEndTime = performance.now();
        const responseTime = stepEndTime - stepStartTime;
        
        let responseData;
        try {
          responseData = await response.json();
        } catch {
          responseData = null;
        }
        
        // Validar resposta
        const stepSuccess = response.status === step.expectedStatus && 
                           step.validation(responseData);
        
        if (!stepSuccess) {
          success = false;
          issues.push(`${step.name}: Status ${response.status} (esperado ${step.expectedStatus})`);
        }
        
        // Armazenar IDs criados para próximos steps
        if (responseData && responseData.id) {
          if (step.name.includes('orçamento')) {
            createdIds['orcamento_id'] = responseData.id;
            createdIds['id'] = responseData.id;
          } else if (step.name.includes('produto')) {
            createdIds['produto_id'] = responseData.id;
            createdIds['id'] = responseData.id;
          } else if (step.name.includes('ordem')) {
            createdIds['ordem_id'] = responseData.id;
            createdIds['id'] = responseData.id;
          }
        }
        
        stepResults.push({
          stepName: step.name,
          success: stepSuccess,
          responseTime,
          statusCode: response.status,
          error: stepSuccess ? undefined : `Validação falhou ou status incorreto`
        });
        
        // Verificar timing se especificado
        if (step.timing && responseTime > step.timing) {
          issues.push(`${step.name}: Tempo de resposta alto (${responseTime.toFixed(2)}ms > ${step.timing}ms)`);
          recommendations.push(`Otimizar performance do endpoint ${endpoint}`);
        }
        
      } catch (error) {
        const stepEndTime = performance.now();
        const responseTime = stepEndTime - stepStartTime;
        
        success = false;
        issues.push(`${step.name}: Erro de execução - ${error}`);
        
        stepResults.push({
          stepName: step.name,
          success: false,
          responseTime,
          statusCode: 0,
          error: `Erro de execução: ${error}`
        });
      }
    }
    
    const endTime = performance.now();
    const totalTime = endTime - startTime;
    
    // Verificar se o fluxo demorou mais que o esperado
    if (totalTime > flow.expectedDuration) {
      issues.push(`Fluxo demorou mais que o esperado (${totalTime.toFixed(2)}ms > ${flow.expectedDuration}ms)`);
      recommendations.push('Revisar performance geral do fluxo');
    }
    
    // Adicionar recomendações baseadas nos resultados
    const failedSteps = stepResults.filter(step => !step.success);
    if (failedSteps.length > 0) {
      recommendations.push('Revisar implementação dos endpoints que falharam');
      recommendations.push('Implementar testes unitários para os endpoints problemáticos');
    }
    
    const slowSteps = stepResults.filter(step => step.responseTime > 1000);
    if (slowSteps.length > 0) {
      recommendations.push('Otimizar performance dos endpoints lentos');
      recommendations.push('Considerar implementar cache para endpoints frequentemente acessados');
    }
    
    return {
      flowName: flow.name,
      success,
      totalTime,
      stepResults,
      issues,
      recommendations
    };
  }

  // Executar todos os fluxos
  async executeAllFlows(): Promise<FlowResult[]> {
    const flows = [
      this.getOrcamentoCreationFlow(),
      this.getEstoqueManagementFlow(),
      this.getOrdemServicoFlow(),
      this.getIntegrationFlow()
    ];
    
    const results: FlowResult[] = [];
    
    for (const flow of flows) {
      console.log(`Executando fluxo: ${flow.name}`);
      const result = await this.executeFlow(flow);
      results.push(result);
      
      // Pausa entre fluxos para não sobrecarregar a API
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
    
    return results;
  }
}

// Função utilitária para gerar relatório de fluxos
export function generateFlowReport(results: FlowResult[]): string {
  let report = `
# Relatório de Testes de Fluxo de Usuário - Agente TRAE

`;
  
  const totalFlows = results.length;
  const successfulFlows = results.filter(r => r.success).length;
  const successRate = (successfulFlows / totalFlows) * 100;
  
  report += `## 📊 Resumo Geral
`;
  report += `- **Total de Fluxos:** ${totalFlows}
`;
  report += `- **Fluxos Bem-sucedidos:** ${successfulFlows}
`;
  report += `- **Taxa de Sucesso:** ${successRate.toFixed(1)}%
`;
  report += `- **Tempo Total:** ${results.reduce((sum, r) => sum + r.totalTime, 0).toFixed(2)}ms

`;
  
  results.forEach(result => {
    report += `## 🔄 ${result.flowName}
`;
    report += `- **Status:** ${result.success ? '✅ Sucesso' : '❌ Falha'}
`;
    report += `- **Tempo Total:** ${result.totalTime.toFixed(2)}ms
`;
    report += `- **Steps Executados:** ${result.stepResults.length}
`;
    report += `- **Steps Bem-sucedidos:** ${result.stepResults.filter(s => s.success).length}

`;
    
    if (result.stepResults.length > 0) {
      report += `### 📋 Detalhes dos Steps
`;
      result.stepResults.forEach(step => {
        const status = step.success ? '✅' : '❌';
        report += `- ${status} **${step.stepName}** (${step.responseTime.toFixed(2)}ms) - Status: ${step.statusCode}
`;
        if (step.error) {
          report += `  - ⚠️ ${step.error}
`;
        }
      });
      report += `
`;
    }
    
    if (result.issues.length > 0) {
      report += `### 🚨 Problemas Identificados
`;
      result.issues.forEach(issue => {
        report += `- ${issue}
`;
      });
      report += `
`;
    }
    
    if (result.recommendations.length > 0) {
      report += `### 💡 Recomendações
`;
      result.recommendations.forEach(rec => {
        report += `- ${rec}
`;
      });
      report += `
`;
    }
  });
  
  // Análise geral
  const allIssues = results.flatMap(r => r.issues);
  const allRecommendations = results.flatMap(r => r.recommendations);
  
  if (allIssues.length > 0) {
    report += `## 🎯 Análise Geral

`;
    report += `### ⚠️ Principais Problemas
`;
    [...new Set(allIssues)].forEach(issue => {
      report += `- ${issue}
`;
    });
    report += `
`;
  }
  
  if (allRecommendations.length > 0) {
    report += `### 🚀 Recomendações Prioritárias
`;
    [...new Set(allRecommendations)].forEach(rec => {
      report += `- ${rec}
`;
    });
    report += `
`;
  }
  
  return report;
}