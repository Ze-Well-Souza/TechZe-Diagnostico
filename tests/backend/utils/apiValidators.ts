// Utilitários de Validação de APIs - Agente TRAE testando Backend CURSOR
// Data: 2025-01-09
// Testador: Agente TRAE

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
  warnings: string[];
  score: number;
}

export interface ApiResponse {
  status: number;
  data: any;
  headers: Headers;
  responseTime: number;
}

// Validador de estrutura de resposta
export class ResponseStructureValidator {
  static validateOrcamentoResponse(response: any): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let score = 10;

    // Campos obrigatórios
    const requiredFields = ['id', 'cliente_id', 'descricao', 'valor_total', 'status'];
    
    for (const field of requiredFields) {
      if (!(field in response)) {
        errors.push(`Campo obrigatório ausente: ${field}`);
        score -= 2;
      }
    }

    // Validação de tipos
    if (response.id && typeof response.id !== 'number') {
      errors.push('Campo id deve ser numérico');
      score -= 1;
    }

    if (response.valor_total && typeof response.valor_total !== 'number') {
      errors.push('Campo valor_total deve ser numérico');
      score -= 1;
    }

    // Validação de status
    const validStatuses = ['PENDENTE', 'APROVADO', 'REJEITADO', 'EXPIRADO'];
    if (response.status && !validStatuses.includes(response.status)) {
      warnings.push(`Status '${response.status}' não está na lista de valores válidos`);
      score -= 0.5;
    }

    // Validação de datas
    if (response.data_criacao && !this.isValidDate(response.data_criacao)) {
      warnings.push('Formato de data_criacao pode estar incorreto');
      score -= 0.5;
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      score: Math.max(0, score)
    };
  }

  static validateProdutoResponse(response: any): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let score = 10;

    // Campos obrigatórios
    const requiredFields = ['id', 'nome', 'preco_venda', 'preco_custo', 'estoque_atual'];
    
    for (const field of requiredFields) {
      if (!(field in response)) {
        errors.push(`Campo obrigatório ausente: ${field}`);
        score -= 2;
      }
    }

    // Validação de preços
    if (response.preco_venda && response.preco_custo) {
      if (response.preco_venda < response.preco_custo) {
        warnings.push('Preço de venda menor que preço de custo');
        score -= 0.5;
      }
    }

    // Validação de estoque
    if (response.estoque_atual && response.estoque_atual < 0) {
      errors.push('Estoque atual não pode ser negativo');
      score -= 1;
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      score: Math.max(0, score)
    };
  }

  static validateOrdemServicoResponse(response: any): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let score = 10;

    // Campos obrigatórios
    const requiredFields = ['id', 'numero_os', 'cliente_id', 'equipamento', 'status'];
    
    for (const field of requiredFields) {
      if (!(field in response)) {
        errors.push(`Campo obrigatório ausente: ${field}`);
        score -= 2;
      }
    }

    // Validação de status
    const validStatuses = ['ABERTA', 'EM_ANDAMENTO', 'AGUARDANDO_PECA', 'CONCLUIDA', 'CANCELADA'];
    if (response.status && !validStatuses.includes(response.status)) {
      warnings.push(`Status '${response.status}' não está na lista de valores válidos`);
      score -= 0.5;
    }

    // Validação de prioridade
    const validPriorities = ['BAIXA', 'MEDIA', 'ALTA', 'URGENTE'];
    if (response.prioridade && !validPriorities.includes(response.prioridade)) {
      warnings.push(`Prioridade '${response.prioridade}' não está na lista de valores válidos`);
      score -= 0.5;
    }

    // Validação de lógica de negócio
    if (response.status === 'CONCLUIDA' && !response.data_conclusao) {
      warnings.push('Ordem concluída deveria ter data_conclusao');
      score -= 0.5;
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      score: Math.max(0, score)
    };
  }

  private static isValidDate(dateString: string): boolean {
    const date = new Date(dateString);
    return date instanceof Date && !isNaN(date.getTime());
  }
}

// Validador de códigos de status HTTP
export class HttpStatusValidator {
  static validateStatusCode(status: number, expectedStatus: number | number[]): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let score = 10;

    const expected = Array.isArray(expectedStatus) ? expectedStatus : [expectedStatus];
    
    if (!expected.includes(status)) {
      errors.push(`Status code ${status} não esperado. Esperado: ${expected.join(' ou ')}`);
      score = 0;
    }

    // Verificações específicas
    if (status >= 500) {
      errors.push('Erro interno do servidor detectado');
    } else if (status >= 400 && status < 500) {
      if (!expected.includes(status)) {
        warnings.push('Erro do cliente - verificar se é intencional');
      }
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      score
    };
  }
}

// Validador de performance
export class PerformanceValidator {
  static validateResponseTime(responseTime: number, maxAcceptable: number = 500): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let score = 10;

    if (responseTime > maxAcceptable * 4) {
      errors.push(`Tempo de resposta muito alto: ${responseTime.toFixed(2)}ms (máximo aceitável: ${maxAcceptable}ms)`);
      score = 0;
    } else if (responseTime > maxAcceptable * 2) {
      warnings.push(`Tempo de resposta alto: ${responseTime.toFixed(2)}ms`);
      score = 3;
    } else if (responseTime > maxAcceptable) {
      warnings.push(`Tempo de resposta acima do ideal: ${responseTime.toFixed(2)}ms`);
      score = 6;
    } else if (responseTime > maxAcceptable * 0.5) {
      score = 8;
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      score
    };
  }

  static validateThroughput(requestsPerSecond: number, minExpected: number = 10): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let score = 10;

    if (requestsPerSecond < minExpected * 0.25) {
      errors.push(`Throughput muito baixo: ${requestsPerSecond.toFixed(2)} req/s (mínimo esperado: ${minExpected} req/s)`);
      score = 0;
    } else if (requestsPerSecond < minExpected * 0.5) {
      warnings.push(`Throughput baixo: ${requestsPerSecond.toFixed(2)} req/s`);
      score = 3;
    } else if (requestsPerSecond < minExpected) {
      warnings.push(`Throughput abaixo do esperado: ${requestsPerSecond.toFixed(2)} req/s`);
      score = 6;
    } else if (requestsPerSecond < minExpected * 2) {
      score = 8;
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      score
    };
  }
}

// Validador de segurança
export class SecurityValidator {
  static validateHeaders(headers: Headers): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let score = 10;

    // Verificar headers de segurança importantes
    const securityHeaders = {
      'x-content-type-options': 'nosniff',
      'x-frame-options': ['DENY', 'SAMEORIGIN'],
      'x-xss-protection': '1; mode=block'
    };

    for (const [header, expectedValue] of Object.entries(securityHeaders)) {
      const headerValue = headers.get(header);
      
      if (!headerValue) {
        warnings.push(`Header de segurança ausente: ${header}`);
        score -= 0.5;
      } else if (Array.isArray(expectedValue)) {
        if (!expectedValue.includes(headerValue)) {
          warnings.push(`Valor inadequado para ${header}: ${headerValue}`);
          score -= 0.3;
        }
      } else if (headerValue !== expectedValue) {
        warnings.push(`Valor inadequado para ${header}: ${headerValue}`);
        score -= 0.3;
      }
    }

    // Verificar se não há exposição de informações sensíveis
    const serverHeader = headers.get('server');
    if (serverHeader && serverHeader.includes('version')) {
      warnings.push('Header Server pode estar expondo informações de versão');
      score -= 0.5;
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      score: Math.max(0, score)
    };
  }

  static validateAuthenticationRequired(response: ApiResponse, requiresAuth: boolean): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let score = 10;

    if (requiresAuth && response.status !== 401 && response.status !== 403) {
      errors.push('Endpoint que requer autenticação não está protegido adequadamente');
      score = 0;
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      score
    };
  }
}

// Validador de consistência de dados
export class DataConsistencyValidator {
  static validateBusinessRules(data: any, type: 'orcamento' | 'produto' | 'ordem_servico'): ValidationResult {
    const errors: string[] = [];
    const warnings: string[] = [];
    let score = 10;

    switch (type) {
      case 'orcamento':
        // Validar se valor total bate com soma dos itens
        if (data.itens && Array.isArray(data.itens)) {
          const somaItens = data.itens.reduce((sum: number, item: any) => {
            return sum + (item.quantidade * item.preco_unitario);
          }, 0);
          
          if (Math.abs(somaItens - data.valor_total) > 0.01) {
            errors.push(`Valor total (${data.valor_total}) não confere com soma dos itens (${somaItens})`);
            score -= 3;
          }
        }
        
        // Validar data de validade
        if (data.data_validade) {
          const dataValidade = new Date(data.data_validade);
          const hoje = new Date();
          
          if (dataValidade < hoje && data.status === 'PENDENTE') {
            warnings.push('Orçamento pendente com data de validade vencida');
            score -= 1;
          }
        }
        break;

      case 'produto':
        // Validar margem de lucro
        if (data.preco_venda && data.preco_custo) {
          const margem = ((data.preco_venda - data.preco_custo) / data.preco_custo) * 100;
          
          if (margem < 0) {
            errors.push('Produto com margem negativa');
            score -= 2;
          } else if (margem < 10) {
            warnings.push(`Margem de lucro baixa: ${margem.toFixed(2)}%`);
            score -= 0.5;
          }
        }
        
        // Validar estoque mínimo
        if (data.estoque_atual < data.estoque_minimo) {
          warnings.push('Produto abaixo do estoque mínimo');
          score -= 0.5;
        }
        break;

      case 'ordem_servico':
        // Validar sequência de datas
        const datas = {
          abertura: data.data_abertura,
          agendamento: data.data_agendamento,
          inicio: data.data_inicio,
          conclusao: data.data_conclusao
        };
        
        const datasValidas = Object.entries(datas)
          .filter(([_, data]) => data)
          .map(([nome, data]) => ({ nome, data: new Date(data as string) }));
        
        for (let i = 1; i < datasValidas.length; i++) {
          if (datasValidas[i].data < datasValidas[i-1].data) {
            errors.push(`Data de ${datasValidas[i].nome} anterior à data de ${datasValidas[i-1].nome}`);
            score -= 2;
          }
        }
        break;
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings,
      score: Math.max(0, score)
    };
  }
}

// Função utilitária para executar todas as validações
export class ApiValidator {
  static async validateApiResponse(
    response: ApiResponse, 
    expectedStatus: number | number[],
    dataType: 'orcamento' | 'produto' | 'ordem_servico',
    requiresAuth: boolean = false
  ): Promise<{
    overall: ValidationResult;
    details: {
      structure: ValidationResult;
      status: ValidationResult;
      performance: ValidationResult;
      security: ValidationResult;
      businessRules: ValidationResult;
    }
  }> {
    
    // Executar todas as validações
    const structureResult = this.validateStructure(response.data, dataType);
    const statusResult = HttpStatusValidator.validateStatusCode(response.status, expectedStatus);
    const performanceResult = PerformanceValidator.validateResponseTime(response.responseTime);
    const securityResult = SecurityValidator.validateHeaders(response.headers);
    const businessRulesResult = DataConsistencyValidator.validateBusinessRules(response.data, dataType);
    
    // Calcular score geral
    const scores = [structureResult, statusResult, performanceResult, securityResult, businessRulesResult];
    const overallScore = scores.reduce((sum, result) => sum + result.score, 0) / scores.length;
    
    // Combinar erros e warnings
    const allErrors = scores.flatMap(result => result.errors);
    const allWarnings = scores.flatMap(result => result.warnings);
    
    return {
      overall: {
        isValid: allErrors.length === 0,
        errors: allErrors,
        warnings: allWarnings,
        score: overallScore
      },
      details: {
        structure: structureResult,
        status: statusResult,
        performance: performanceResult,
        security: securityResult,
        businessRules: businessRulesResult
      }
    };
  }
  
  private static validateStructure(data: any, type: 'orcamento' | 'produto' | 'ordem_servico'): ValidationResult {
    switch (type) {
      case 'orcamento':
        return ResponseStructureValidator.validateOrcamentoResponse(data);
      case 'produto':
        return ResponseStructureValidator.validateProdutoResponse(data);
      case 'ordem_servico':
        return ResponseStructureValidator.validateOrdemServicoResponse(data);
      default:
        return { isValid: false, errors: ['Tipo de dados não reconhecido'], warnings: [], score: 0 };
    }
  }
}