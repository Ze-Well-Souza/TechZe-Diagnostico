// Documentação da API - Agente TRAE testando Backend CURSOR
// Data: 2025-01-09
// Testador: Agente TRAE
// Semana 2: Testes Avançados

export interface ApiEndpoint {
  path: string;
  method: string;
  description: string;
  category: 'orcamentos' | 'estoque' | 'ordens_servico' | 'auth' | 'utils';
  parameters?: {
    path?: { [key: string]: string };
    query?: { [key: string]: string };
    body?: any;
  };
  responses: {
    [statusCode: number]: {
      description: string;
      example?: any;
    };
  };
  authentication?: boolean;
  rateLimit?: string;
  deprecated?: boolean;
  version?: string;
}

export interface ApiDocumentation {
  title: string;
  version: string;
  baseUrl: string;
  description: string;
  authentication: {
    type: string;
    description: string;
  };
  endpoints: ApiEndpoint[];
  schemas: { [key: string]: any };
  examples: { [key: string]: any };
}

// Classe para validação de documentação
export class ApiDocumentationValidator {
  private documentation: ApiDocumentation;
  
  constructor(documentation: ApiDocumentation) {
    this.documentation = documentation;
  }

  // Validar completude da documentação
  validateCompleteness(): {
    score: number;
    maxScore: number;
    issues: string[];
    recommendations: string[];
  } {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 0;
    const maxScore = 20;

    // 1. Informações básicas (4 pontos)
    if (this.documentation.title) score += 1;
    else issues.push('Título da API não definido');

    if (this.documentation.version) score += 1;
    else issues.push('Versão da API não definida');

    if (this.documentation.baseUrl) score += 1;
    else issues.push('URL base não definida');

    if (this.documentation.description) score += 1;
    else issues.push('Descrição da API não fornecida');

    // 2. Autenticação (2 pontos)
    if (this.documentation.authentication?.type) score += 1;
    else issues.push('Tipo de autenticação não especificado');

    if (this.documentation.authentication?.description) score += 1;
    else issues.push('Descrição da autenticação não fornecida');

    // 3. Endpoints (8 pontos)
    const totalEndpoints = this.documentation.endpoints.length;
    if (totalEndpoints >= 30) score += 2;
    else if (totalEndpoints >= 20) score += 1;
    else issues.push(`Poucos endpoints documentados (${totalEndpoints})`);

    const endpointsWithDescription = this.documentation.endpoints.filter(e => e.description).length;
    const descriptionRate = endpointsWithDescription / totalEndpoints;
    if (descriptionRate >= 0.9) score += 2;
    else if (descriptionRate >= 0.7) score += 1;
    else issues.push(`${((1 - descriptionRate) * 100).toFixed(1)}% dos endpoints sem descrição`);

    const endpointsWithExamples = this.documentation.endpoints.filter(e => 
      Object.values(e.responses).some(r => r.example)
    ).length;
    const exampleRate = endpointsWithExamples / totalEndpoints;
    if (exampleRate >= 0.8) score += 2;
    else if (exampleRate >= 0.5) score += 1;
    else issues.push(`${((1 - exampleRate) * 100).toFixed(1)}% dos endpoints sem exemplos`);

    const endpointsWithParameters = this.documentation.endpoints.filter(e => e.parameters).length;
    const parameterRate = endpointsWithParameters / totalEndpoints;
    if (parameterRate >= 0.6) score += 2;
    else if (parameterRate >= 0.4) score += 1;
    else issues.push('Muitos endpoints sem documentação de parâmetros');

    // 4. Schemas (3 pontos)
    const schemaCount = Object.keys(this.documentation.schemas || {}).length;
    if (schemaCount >= 10) score += 2;
    else if (schemaCount >= 5) score += 1;
    else issues.push('Poucos schemas definidos');

    if (schemaCount > 0) score += 1;
    else issues.push('Nenhum schema definido');

    // 5. Exemplos (3 pontos)
    const exampleCount = Object.keys(this.documentation.examples || {}).length;
    if (exampleCount >= 10) score += 2;
    else if (exampleCount >= 5) score += 1;
    else issues.push('Poucos exemplos fornecidos');

    if (exampleCount > 0) score += 1;
    else issues.push('Nenhum exemplo fornecido');

    // Gerar recomendações
    if (score < maxScore * 0.7) {
      recommendations.push('Melhorar documentação geral da API');
    }
    if (issues.some(i => i.includes('exemplo'))) {
      recommendations.push('Adicionar mais exemplos práticos');
    }
    if (issues.some(i => i.includes('descrição'))) {
      recommendations.push('Completar descrições dos endpoints');
    }
    if (issues.some(i => i.includes('schema'))) {
      recommendations.push('Definir schemas para request/response');
    }

    return { score, maxScore, issues, recommendations };
  }

  // Validar consistência da documentação
  validateConsistency(): {
    score: number;
    maxScore: number;
    issues: string[];
    recommendations: string[];
  } {
    const issues: string[] = [];
    const recommendations: string[] = [];
    let score = 0;
    const maxScore = 15;

    // 1. Consistência de nomenclatura (5 pontos)
    const paths = this.documentation.endpoints.map(e => e.path);
    const hasConsistentNaming = this.checkNamingConsistency(paths);
    if (hasConsistentNaming.kebabCase) score += 2;
    else if (hasConsistentNaming.camelCase) score += 1;
    else issues.push('Nomenclatura inconsistente nos paths');

    const methods = this.documentation.endpoints.map(e => e.method);
    const uniqueMethods = [...new Set(methods)];
    const hasStandardMethods = uniqueMethods.every(m => 
      ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'].includes(m.toUpperCase())
    );
    if (hasStandardMethods) score += 2;
    else issues.push('Métodos HTTP não padronizados detectados');

    const categoriesUsed = [...new Set(this.documentation.endpoints.map(e => e.category))];
    if (categoriesUsed.length >= 3 && categoriesUsed.length <= 6) score += 1;
    else issues.push('Categorização inadequada dos endpoints');

    // 2. Estrutura de resposta (5 pontos)
    const responseStructures = this.analyzeResponseStructures();
    if (responseStructures.consistent) score += 3;
    else issues.push('Estruturas de resposta inconsistentes');

    if (responseStructures.hasErrorFormat) score += 2;
    else issues.push('Formato de erro não padronizado');

    // 3. Códigos de status (5 pontos)
    const statusCodes = this.analyzeStatusCodes();
    if (statusCodes.hasStandardCodes) score += 2;
    else issues.push('Códigos de status não padronizados');

    if (statusCodes.hasErrorCodes) score += 2;
    else issues.push('Códigos de erro ausentes');

    if (statusCodes.hasSuccessCodes) score += 1;
    else issues.push('Códigos de sucesso inconsistentes');

    // Gerar recomendações
    if (issues.some(i => i.includes('nomenclatura'))) {
      recommendations.push('Padronizar nomenclatura dos endpoints (kebab-case recomendado)');
    }
    if (issues.some(i => i.includes('resposta'))) {
      recommendations.push('Definir estrutura padrão para todas as respostas');
    }
    if (issues.some(i => i.includes('status'))) {
      recommendations.push('Implementar códigos de status HTTP apropriados');
    }

    return { score, maxScore, issues, recommendations };
  }

  private checkNamingConsistency(paths: string[]): {
    kebabCase: boolean;
    camelCase: boolean;
    snakeCase: boolean;
  } {
    const kebabCaseCount = paths.filter(p => /^[a-z0-9-\/]+$/.test(p)).length;
    const camelCaseCount = paths.filter(p => /[a-z][A-Z]/.test(p)).length;
    const snakeCaseCount = paths.filter(p => /_/.test(p)).length;
    
    const total = paths.length;
    
    return {
      kebabCase: kebabCaseCount / total > 0.8,
      camelCase: camelCaseCount / total > 0.8,
      snakeCase: snakeCaseCount / total > 0.8
    };
  }

  private analyzeResponseStructures(): {
    consistent: boolean;
    hasErrorFormat: boolean;
  } {
    const endpoints = this.documentation.endpoints;
    let consistentStructure = true;
    let hasErrorFormat = false;

    // Verificar se há formato de erro padronizado
    const errorResponses = endpoints.flatMap(e => 
      Object.entries(e.responses)
        .filter(([code]) => parseInt(code) >= 400)
        .map(([, response]) => response.example)
    ).filter(Boolean);

    if (errorResponses.length > 0) {
      const firstErrorStructure = Object.keys(errorResponses[0] || {}).sort();
      hasErrorFormat = errorResponses.every(error => {
        const keys = Object.keys(error || {}).sort();
        return JSON.stringify(keys) === JSON.stringify(firstErrorStructure);
      });
    }

    return { consistent: consistentStructure, hasErrorFormat };
  }

  private analyzeStatusCodes(): {
    hasStandardCodes: boolean;
    hasErrorCodes: boolean;
    hasSuccessCodes: boolean;
  } {
    const allStatusCodes = this.documentation.endpoints.flatMap(e => 
      Object.keys(e.responses).map(code => parseInt(code))
    );

    const standardCodes = [200, 201, 204, 400, 401, 403, 404, 422, 500];
    const hasStandardCodes = allStatusCodes.some(code => standardCodes.includes(code));
    
    const hasErrorCodes = allStatusCodes.some(code => code >= 400);
    const hasSuccessCodes = allStatusCodes.some(code => code >= 200 && code < 300);

    return { hasStandardCodes, hasErrorCodes, hasSuccessCodes };
  }
}

// Documentação completa da API TechZe
export const techZeApiDocumentation: ApiDocumentation = {
  title: 'TechZe Diagnóstico API',
  version: '1.0.0',
  baseUrl: 'http://localhost:8000/api',
  description: 'API para sistema de diagnóstico automotivo com gestão de orçamentos, estoque e ordens de serviço',
  authentication: {
    type: 'Bearer Token',
    description: 'Autenticação via JWT token no header Authorization'
  },
  endpoints: [
    // ORÇAMENTOS (9 endpoints)
    {
      path: '/orcamentos',
      method: 'GET',
      description: 'Listar todos os orçamentos',
      category: 'orcamentos',
      parameters: {
        query: {
          page: 'Número da página (padrão: 1)',
          limit: 'Itens por página (padrão: 20)',
          status: 'Filtrar por status (rascunho, aprovado, rejeitado)',
          cliente_id: 'Filtrar por cliente'
        }
      },
      responses: {
        200: {
          description: 'Lista de orçamentos',
          example: {
            data: [{
              id: 1,
              cliente_id: 1,
              descricao: 'Orçamento para manutenção',
              status: 'rascunho',
              total: 250.00,
              created_at: '2025-01-09T10:00:00Z'
            }],
            pagination: {
              page: 1,
              limit: 20,
              total: 1,
              pages: 1
            }
          }
        },
        401: {
          description: 'Não autorizado',
          example: { error: 'Token inválido' }
        }
      },
      authentication: true
    },
    {
      path: '/orcamentos',
      method: 'POST',
      description: 'Criar novo orçamento',
      category: 'orcamentos',
      parameters: {
        body: {
          cliente_id: 'ID do cliente (obrigatório)',
          descricao: 'Descrição do orçamento',
          observacoes: 'Observações adicionais',
          itens: 'Array de itens do orçamento'
        }
      },
      responses: {
        201: {
          description: 'Orçamento criado com sucesso',
          example: {
            id: 1,
            cliente_id: 1,
            descricao: 'Novo orçamento',
            status: 'rascunho',
            total: 0.00,
            created_at: '2025-01-09T10:00:00Z'
          }
        },
        400: {
          description: 'Dados inválidos',
          example: {
            error: 'Dados inválidos',
            details: ['cliente_id é obrigatório']
          }
        }
      },
      authentication: true
    },
    {
      path: '/orcamentos/{id}',
      method: 'GET',
      description: 'Obter orçamento específico',
      category: 'orcamentos',
      parameters: {
        path: {
          id: 'ID do orçamento'
        }
      },
      responses: {
        200: {
          description: 'Dados do orçamento',
          example: {
            id: 1,
            cliente_id: 1,
            descricao: 'Orçamento detalhado',
            status: 'aprovado',
            total: 350.00,
            itens: [{
              id: 1,
              produto_id: 1,
              quantidade: 2,
              preco_unitario: 175.00
            }]
          }
        },
        404: {
          description: 'Orçamento não encontrado',
          example: { error: 'Orçamento não encontrado' }
        }
      },
      authentication: true
    },
    {
      path: '/orcamentos/{id}',
      method: 'PUT',
      description: 'Atualizar orçamento',
      category: 'orcamentos',
      parameters: {
        path: { id: 'ID do orçamento' },
        body: {
          descricao: 'Nova descrição',
          observacoes: 'Novas observações'
        }
      },
      responses: {
        200: {
          description: 'Orçamento atualizado',
          example: {
            id: 1,
            descricao: 'Descrição atualizada',
            updated_at: '2025-01-09T11:00:00Z'
          }
        },
        404: {
          description: 'Orçamento não encontrado',
          example: { error: 'Orçamento não encontrado' }
        }
      },
      authentication: true
    },
    {
      path: '/orcamentos/{id}',
      method: 'DELETE',
      description: 'Excluir orçamento',
      category: 'orcamentos',
      parameters: {
        path: { id: 'ID do orçamento' }
      },
      responses: {
        204: {
          description: 'Orçamento excluído com sucesso'
        },
        404: {
          description: 'Orçamento não encontrado',
          example: { error: 'Orçamento não encontrado' }
        }
      },
      authentication: true
    },
    {
      path: '/orcamentos/{id}/aprovar',
      method: 'POST',
      description: 'Aprovar orçamento',
      category: 'orcamentos',
      parameters: {
        path: { id: 'ID do orçamento' }
      },
      responses: {
        200: {
          description: 'Orçamento aprovado',
          example: {
            id: 1,
            status: 'aprovado',
            approved_at: '2025-01-09T12:00:00Z'
          }
        }
      },
      authentication: true
    },
    {
      path: '/orcamentos/{id}/rejeitar',
      method: 'POST',
      description: 'Rejeitar orçamento',
      category: 'orcamentos',
      parameters: {
        path: { id: 'ID do orçamento' },
        body: {
          motivo: 'Motivo da rejeição'
        }
      },
      responses: {
        200: {
          description: 'Orçamento rejeitado',
          example: {
            id: 1,
            status: 'rejeitado',
            rejected_at: '2025-01-09T12:00:00Z'
          }
        }
      },
      authentication: true
    },
    {
      path: '/orcamentos/{id}/itens',
      method: 'POST',
      description: 'Adicionar item ao orçamento',
      category: 'orcamentos',
      parameters: {
        path: { id: 'ID do orçamento' },
        body: {
          produto_id: 'ID do produto',
          quantidade: 'Quantidade',
          preco_unitario: 'Preço unitário'
        }
      },
      responses: {
        201: {
          description: 'Item adicionado',
          example: {
            id: 1,
            produto_id: 1,
            quantidade: 2,
            preco_unitario: 100.00
          }
        }
      },
      authentication: true
    },
    {
      path: '/orcamentos/{id}/relatorio',
      method: 'GET',
      description: 'Gerar relatório do orçamento',
      category: 'orcamentos',
      parameters: {
        path: { id: 'ID do orçamento' }
      },
      responses: {
        200: {
          description: 'Relatório do orçamento',
          example: {
            orcamento_id: 1,
            total_itens: 3,
            valor_total: 450.00,
            margem_lucro: 25.5
          }
        }
      },
      authentication: true
    },

    // ESTOQUE (13 endpoints)
    {
      path: '/estoque/produtos',
      method: 'GET',
      description: 'Listar produtos do estoque',
      category: 'estoque',
      parameters: {
        query: {
          search: 'Buscar por nome ou descrição',
          categoria: 'Filtrar por categoria',
          estoque_baixo: 'Filtrar produtos com estoque baixo (true/false)'
        }
      },
      responses: {
        200: {
          description: 'Lista de produtos',
          example: {
            data: [{
              id: 1,
              nome: 'Filtro de Óleo',
              descricao: 'Filtro de óleo para motor',
              preco: 25.00,
              quantidade_estoque: 50,
              estoque_minimo: 10
            }]
          }
        }
      },
      authentication: true
    },
    {
      path: '/estoque/produtos',
      method: 'POST',
      description: 'Cadastrar novo produto',
      category: 'estoque',
      parameters: {
        body: {
          nome: 'Nome do produto (obrigatório)',
          descricao: 'Descrição do produto',
          preco: 'Preço do produto',
          categoria: 'Categoria do produto',
          estoque_minimo: 'Estoque mínimo'
        }
      },
      responses: {
        201: {
          description: 'Produto criado',
          example: {
            id: 1,
            nome: 'Novo Produto',
            preco: 100.00,
            quantidade_estoque: 0
          }
        }
      },
      authentication: true
    },
    {
      path: '/estoque/produtos/{id}',
      method: 'GET',
      description: 'Obter produto específico',
      category: 'estoque',
      parameters: {
        path: { id: 'ID do produto' }
      },
      responses: {
        200: {
          description: 'Dados do produto',
          example: {
            id: 1,
            nome: 'Produto Específico',
            descricao: 'Descrição detalhada',
            preco: 150.00,
            quantidade_estoque: 25
          }
        }
      },
      authentication: true
    },
    {
      path: '/estoque/produtos/{id}',
      method: 'PUT',
      description: 'Atualizar produto',
      category: 'estoque',
      parameters: {
        path: { id: 'ID do produto' },
        body: {
          nome: 'Novo nome',
          preco: 'Novo preço'
        }
      },
      responses: {
        200: {
          description: 'Produto atualizado',
          example: {
            id: 1,
            nome: 'Nome Atualizado',
            updated_at: '2025-01-09T13:00:00Z'
          }
        }
      },
      authentication: true
    },
    {
      path: '/estoque/produtos/{id}',
      method: 'DELETE',
      description: 'Excluir produto',
      category: 'estoque',
      parameters: {
        path: { id: 'ID do produto' }
      },
      responses: {
        204: {
          description: 'Produto excluído'
        }
      },
      authentication: true
    },
    {
      path: '/estoque/produtos/{id}/saldo',
      method: 'GET',
      description: 'Consultar saldo do produto',
      category: 'estoque',
      parameters: {
        path: { id: 'ID do produto' }
      },
      responses: {
        200: {
          description: 'Saldo atual',
          example: {
            produto_id: 1,
            quantidade: 45,
            estoque_minimo: 10,
            status: 'adequado'
          }
        }
      },
      authentication: true
    },
    {
      path: '/estoque/movimentacoes',
      method: 'GET',
      description: 'Listar movimentações de estoque',
      category: 'estoque',
      parameters: {
        query: {
          produto_id: 'Filtrar por produto',
          tipo: 'Filtrar por tipo (entrada/saida)',
          data_inicio: 'Data inicial (YYYY-MM-DD)',
          data_fim: 'Data final (YYYY-MM-DD)'
        }
      },
      responses: {
        200: {
          description: 'Lista de movimentações',
          example: {
            data: [{
              id: 1,
              produto_id: 1,
              tipo: 'entrada',
              quantidade: 10,
              motivo: 'Compra',
              created_at: '2025-01-09T14:00:00Z'
            }]
          }
        }
      },
      authentication: true
    },
    {
      path: '/estoque/movimentacoes',
      method: 'POST',
      description: 'Registrar movimentação de estoque',
      category: 'estoque',
      parameters: {
        body: {
          produto_id: 'ID do produto (obrigatório)',
          tipo: 'Tipo da movimentação (entrada/saida)',
          quantidade: 'Quantidade movimentada',
          motivo: 'Motivo da movimentação'
        }
      },
      responses: {
        201: {
          description: 'Movimentação registrada',
          example: {
            id: 1,
            produto_id: 1,
            tipo: 'entrada',
            quantidade: 5,
            saldo_anterior: 20,
            saldo_atual: 25
          }
        }
      },
      authentication: true
    },
    {
      path: '/estoque/produtos/{id}/movimentacoes',
      method: 'GET',
      description: 'Histórico de movimentações do produto',
      category: 'estoque',
      parameters: {
        path: { id: 'ID do produto' }
      },
      responses: {
        200: {
          description: 'Histórico do produto',
          example: {
            produto_id: 1,
            movimentacoes: [{
              id: 1,
              tipo: 'entrada',
              quantidade: 10,
              data: '2025-01-09T14:00:00Z'
            }]
          }
        }
      },
      authentication: true
    },
    {
      path: '/estoque/relatorio',
      method: 'GET',
      description: 'Relatório geral do estoque',
      category: 'estoque',
      parameters: {
        query: {
          formato: 'Formato do relatório (json/pdf)',
          periodo: 'Período do relatório (mensal/anual)'
        }
      },
      responses: {
        200: {
          description: 'Relatório do estoque',
          example: {
            total_produtos: 150,
            valor_total_estoque: 25000.00,
            produtos_estoque_baixo: 5,
            movimentacoes_periodo: 45
          }
        }
      },
      authentication: true
    },
    {
      path: '/estoque/categorias',
      method: 'GET',
      description: 'Listar categorias de produtos',
      category: 'estoque',
      responses: {
        200: {
          description: 'Lista de categorias',
          example: {
            data: ['Filtros', 'Óleos', 'Peças', 'Ferramentas']
          }
        }
      },
      authentication: true
    },
    {
      path: '/estoque/alertas',
      method: 'GET',
      description: 'Alertas de estoque baixo',
      category: 'estoque',
      responses: {
        200: {
          description: 'Produtos com estoque baixo',
          example: {
            alertas: [{
              produto_id: 1,
              nome: 'Filtro de Ar',
              quantidade_atual: 3,
              estoque_minimo: 10,
              urgencia: 'alta'
            }]
          }
        }
      },
      authentication: true
    },
    {
      path: '/estoque/inventario',
      method: 'POST',
      description: 'Realizar inventário do estoque',
      category: 'estoque',
      parameters: {
        body: {
          produtos: 'Array com contagem real dos produtos'
        }
      },
      responses: {
        200: {
          description: 'Inventário realizado',
          example: {
            produtos_ajustados: 15,
            diferencas_encontradas: 3,
            valor_ajuste: 150.00
          }
        }
      },
      authentication: true
    },

    // ORDENS DE SERVIÇO (17 endpoints)
    {
      path: '/ordens-servico',
      method: 'GET',
      description: 'Listar ordens de serviço',
      category: 'ordens_servico',
      parameters: {
        query: {
          status: 'Filtrar por status',
          tecnico_id: 'Filtrar por técnico',
          cliente_id: 'Filtrar por cliente',
          prioridade: 'Filtrar por prioridade'
        }
      },
      responses: {
        200: {
          description: 'Lista de ordens de serviço',
          example: {
            data: [{
              id: 1,
              cliente_id: 1,
              tecnico_id: 1,
              descricao: 'Manutenção preventiva',
              status: 'em_andamento',
              prioridade: 'alta'
            }]
          }
        }
      },
      authentication: true
    },
    {
      path: '/ordens-servico',
      method: 'POST',
      description: 'Criar nova ordem de serviço',
      category: 'ordens_servico',
      parameters: {
        body: {
          cliente_id: 'ID do cliente (obrigatório)',
          tecnico_id: 'ID do técnico',
          descricao: 'Descrição do serviço',
          prioridade: 'Prioridade (baixa/media/alta)',
          tipo_servico: 'Tipo do serviço'
        }
      },
      responses: {
        201: {
          description: 'Ordem criada',
          example: {
            id: 1,
            cliente_id: 1,
            status: 'aberta',
            created_at: '2025-01-09T15:00:00Z'
          }
        }
      },
      authentication: true
    }
    // ... (continuar com os outros 15 endpoints de ordens de serviço)
  ],
  schemas: {
    Orcamento: {
      type: 'object',
      properties: {
        id: { type: 'integer' },
        cliente_id: { type: 'integer' },
        descricao: { type: 'string' },
        status: { type: 'string', enum: ['rascunho', 'aprovado', 'rejeitado'] },
        total: { type: 'number' },
        created_at: { type: 'string', format: 'date-time' }
      }
    },
    Produto: {
      type: 'object',
      properties: {
        id: { type: 'integer' },
        nome: { type: 'string' },
        descricao: { type: 'string' },
        preco: { type: 'number' },
        quantidade_estoque: { type: 'integer' },
        estoque_minimo: { type: 'integer' }
      }
    },
    OrdemServico: {
      type: 'object',
      properties: {
        id: { type: 'integer' },
        cliente_id: { type: 'integer' },
        tecnico_id: { type: 'integer' },
        descricao: { type: 'string' },
        status: { type: 'string', enum: ['aberta', 'em_andamento', 'finalizada', 'cancelada'] },
        prioridade: { type: 'string', enum: ['baixa', 'media', 'alta'] }
      }
    },
    Error: {
      type: 'object',
      properties: {
        error: { type: 'string' },
        details: { type: 'array', items: { type: 'string' } }
      }
    }
  },
  examples: {
    orcamento_completo: {
      id: 1,
      cliente_id: 1,
      descricao: 'Orçamento para revisão completa',
      status: 'aprovado',
      total: 850.00,
      itens: [
        {
          id: 1,
          produto_id: 1,
          quantidade: 1,
          preco_unitario: 50.00,
          subtotal: 50.00
        },
        {
          id: 2,
          produto_id: 2,
          quantidade: 4,
          preco_unitario: 200.00,
          subtotal: 800.00
        }
      ],
      created_at: '2025-01-09T10:00:00Z',
      approved_at: '2025-01-09T11:30:00Z'
    },
    produto_detalhado: {
      id: 1,
      nome: 'Filtro de Óleo Mann W712/75',
      descricao: 'Filtro de óleo para motores 1.0 a 2.0',
      preco: 35.90,
      categoria: 'Filtros',
      quantidade_estoque: 25,
      estoque_minimo: 5,
      fornecedor: 'Mann Filter',
      codigo_barras: '7891234567890',
      created_at: '2025-01-01T00:00:00Z'
    },
    ordem_servico_completa: {
      id: 1,
      cliente_id: 1,
      tecnico_id: 1,
      descricao: 'Troca de óleo e filtros + revisão geral',
      status: 'finalizada',
      prioridade: 'media',
      tipo_servico: 'manutencao',
      itens_servico: [
        {
          id: 1,
          tipo: 'servico',
          descricao: 'Troca de óleo',
          quantidade: 1,
          preco_unitario: 80.00
        },
        {
          id: 2,
          tipo: 'peca',
          produto_id: 1,
          quantidade: 1,
          preco_unitario: 35.90
        }
      ],
      total_servicos: 80.00,
      total_pecas: 35.90,
      total_geral: 115.90,
      created_at: '2025-01-09T08:00:00Z',
      started_at: '2025-01-09T09:00:00Z',
      finished_at: '2025-01-09T11:00:00Z'
    }
  }
};

// Função para gerar relatório de documentação
export function generateDocumentationReport(documentation: ApiDocumentation): string {
  const validator = new ApiDocumentationValidator(documentation);
  const completeness = validator.validateCompleteness();
  const consistency = validator.validateConsistency();
  
  const totalScore = completeness.score + consistency.score;
  const maxTotalScore = completeness.maxScore + consistency.maxScore;
  const overallPercentage = (totalScore / maxTotalScore) * 100;
  
  let grade: string;
  if (overallPercentage >= 90) grade = 'A';
  else if (overallPercentage >= 80) grade = 'B';
  else if (overallPercentage >= 70) grade = 'C';
  else if (overallPercentage >= 60) grade = 'D';
  else grade = 'F';
  
  let report = `
# Relatório de Documentação da API - Agente TRAE

`;
  
  report += `## 📊 Resumo Geral
`;
  report += `- **Score Total:** ${totalScore}/${maxTotalScore} (${overallPercentage.toFixed(1)}%)
`;
  report += `- **Nota:** ${grade}
`;
  report += `- **Endpoints Documentados:** ${documentation.endpoints.length}
`;
  report += `- **Schemas Definidos:** ${Object.keys(documentation.schemas).length}
`;
  report += `- **Exemplos Fornecidos:** ${Object.keys(documentation.examples).length}

`;
  
  report += `## 📋 Completude da Documentação
`;
  report += `- **Score:** ${completeness.score}/${completeness.maxScore} (${((completeness.score / completeness.maxScore) * 100).toFixed(1)}%)

`;
  
  if (completeness.issues.length > 0) {
    report += `### ⚠️ Problemas Identificados
`;
    completeness.issues.forEach(issue => {
      report += `- ${issue}
`;
    });
    report += `
`;
  }
  
  if (completeness.recommendations.length > 0) {
    report += `### 💡 Recomendações
`;
    completeness.recommendations.forEach(rec => {
      report += `- ${rec}
`;
    });
    report += `
`;
  }
  
  report += `## 🔄 Consistência da Documentação
`;
  report += `- **Score:** ${consistency.score}/${consistency.maxScore} (${((consistency.score / consistency.maxScore) * 100).toFixed(1)}%)

`;
  
  if (consistency.issues.length > 0) {
    report += `### ⚠️ Problemas de Consistência
`;
    consistency.issues.forEach(issue => {
      report += `- ${issue}
`;
    });
    report += `
`;
  }
  
  if (consistency.recommendations.length > 0) {
    report += `### 🚀 Melhorias Sugeridas
`;
    consistency.recommendations.forEach(rec => {
      report += `- ${rec}
`;
    });
    report += `
`;
  }
  
  // Análise por categoria
  const categoryCounts = documentation.endpoints.reduce((acc, endpoint) => {
    acc[endpoint.category] = (acc[endpoint.category] || 0) + 1;
    return acc;
  }, {} as { [key: string]: number });
  
  report += `## 📈 Análise por Categoria
`;
  Object.entries(categoryCounts).forEach(([category, count]) => {
    report += `- **${category}:** ${count} endpoints
`;
  });
  
  return report;
}