// Componente de Validação de Usabilidade - Agente TRAE testando Backend CURSOR
// Data: 2025-01-09
// Testador: Agente TRAE

import React, { useState, useEffect } from 'react';

interface UsabilityTest {
  id: string;
  name: string;
  description: string;
  category: 'api_design' | 'error_handling' | 'data_consistency' | 'performance' | 'documentation';
  status: 'pending' | 'passed' | 'failed' | 'warning';
  score: number;
  details: string[];
  recommendations: string[];
}

interface UsabilityValidatorProps {
  baseUrl: string;
  authToken?: string;
}

const UsabilityValidator: React.FC<UsabilityValidatorProps> = ({ baseUrl, authToken }) => {
  const [tests, setTests] = useState<UsabilityTest[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [overallScore, setOverallScore] = useState<number>(0);
  const [currentCategory, setCurrentCategory] = useState<string>('');

  // Configuração base para requisições
  const apiConfig = {
    headers: {
      'Content-Type': 'application/json',
      ...(authToken && { 'Authorization': `Bearer ${authToken}` })
    }
  };

  // Testes de Design da API
  const testApiDesign = async (): Promise<UsabilityTest[]> => {
    const designTests: UsabilityTest[] = [];

    // Teste 1: Consistência de nomenclatura
    try {
      const response = await fetch(`${baseUrl}/api/orcamentos`, { ...apiConfig });
      const data = await response.json();
      
      let score = 10;
      const details: string[] = [];
      const recommendations: string[] = [];
      
      // Verifica se usa snake_case ou camelCase consistentemente
      if (data && Array.isArray(data) && data.length > 0) {
        const firstItem = data[0];
        const hasSnakeCase = Object.keys(firstItem).some(key => key.includes('_'));
        const hasCamelCase = Object.keys(firstItem).some(key => /[a-z][A-Z]/.test(key));
        
        if (hasSnakeCase && hasCamelCase) {
          score -= 3;
          details.push('Inconsistência entre snake_case e camelCase');
          recommendations.push('Padronizar nomenclatura para snake_case ou camelCase');
        } else {
          details.push('Nomenclatura consistente detectada');
        }
      }
      
      designTests.push({
        id: 'api_design_naming',
        name: 'Consistência de Nomenclatura',
        description: 'Verifica se a API usa nomenclatura consistente',
        category: 'api_design',
        status: score >= 8 ? 'passed' : score >= 6 ? 'warning' : 'failed',
        score,
        details,
        recommendations
      });
      
    } catch (error) {
      designTests.push({
        id: 'api_design_naming',
        name: 'Consistência de Nomenclatura',
        description: 'Verifica se a API usa nomenclatura consistente',
        category: 'api_design',
        status: 'failed',
        score: 0,
        details: [`Erro ao testar: ${error}`],
        recommendations: ['Verificar conectividade com a API']
      });
    }

    // Teste 2: Estrutura de resposta padronizada
    try {
      const endpoints = [
        '/api/orcamentos',
        '/api/estoque/produtos',
        '/api/ordens-servico'
      ];
      
      let score = 10;
      const details: string[] = [];
      const recommendations: string[] = [];
      
      for (const endpoint of endpoints) {
        try {
          const response = await fetch(`${baseUrl}${endpoint}`, { ...apiConfig });
          const data = await response.json();
          
          // Verifica se tem estrutura consistente
          if (!data || typeof data !== 'object') {
            score -= 2;
            details.push(`${endpoint}: Estrutura de resposta inconsistente`);
          } else {
            details.push(`${endpoint}: Estrutura OK`);
          }
        } catch (error) {
          score -= 1;
          details.push(`${endpoint}: Erro de conectividade`);
        }
      }
      
      if (score < 8) {
        recommendations.push('Padronizar estrutura de resposta entre endpoints');
        recommendations.push('Implementar wrapper de resposta consistente');
      }
      
      designTests.push({
        id: 'api_design_structure',
        name: 'Estrutura de Resposta',
        description: 'Verifica consistência na estrutura das respostas',
        category: 'api_design',
        status: score >= 8 ? 'passed' : score >= 6 ? 'warning' : 'failed',
        score,
        details,
        recommendations
      });
      
    } catch (error) {
      designTests.push({
        id: 'api_design_structure',
        name: 'Estrutura de Resposta',
        description: 'Verifica consistência na estrutura das respostas',
        category: 'api_design',
        status: 'failed',
        score: 0,
        details: [`Erro geral: ${error}`],
        recommendations: ['Verificar configuração da API']
      });
    }

    return designTests;
  };

  // Testes de Tratamento de Erros
  const testErrorHandling = async (): Promise<UsabilityTest[]> => {
    const errorTests: UsabilityTest[] = [];

    // Teste 1: Códigos de status HTTP apropriados
    try {
      let score = 10;
      const details: string[] = [];
      const recommendations: string[] = [];
      
      // Teste com dados inválidos
      const invalidData = {
        cliente_id: -1,
        descricao: "",
        valor_total: -100
      };
      
      const response = await fetch(`${baseUrl}/api/orcamentos`, {
        method: 'POST',
        ...apiConfig,
        body: JSON.stringify(invalidData)
      });
      
      if (response.status === 400 || response.status === 422) {
        details.push('Código de status apropriado para dados inválidos');
      } else {
        score -= 3;
        details.push(`Status inadequado: ${response.status} (esperado: 400 ou 422)`);
        recommendations.push('Implementar códigos de status HTTP apropriados');
      }
      
      const errorData = await response.json();
      
      // Verifica se a mensagem de erro é clara
      if (errorData && errorData.message) {
        details.push('Mensagem de erro presente');
      } else {
        score -= 2;
        details.push('Mensagem de erro ausente ou pouco clara');
        recommendations.push('Incluir mensagens de erro descritivas');
      }
      
      // Verifica se há detalhes dos campos com erro
      if (errorData && errorData.details) {
        details.push('Detalhes de validação presentes');
      } else {
        score -= 1;
        details.push('Detalhes de validação ausentes');
        recommendations.push('Incluir detalhes específicos dos campos com erro');
      }
      
      errorTests.push({
        id: 'error_handling_status',
        name: 'Códigos de Status HTTP',
        description: 'Verifica se a API retorna códigos de status apropriados',
        category: 'error_handling',
        status: score >= 8 ? 'passed' : score >= 6 ? 'warning' : 'failed',
        score,
        details,
        recommendations
      });
      
    } catch (error) {
      errorTests.push({
        id: 'error_handling_status',
        name: 'Códigos de Status HTTP',
        description: 'Verifica se a API retorna códigos de status apropriados',
        category: 'error_handling',
        status: 'failed',
        score: 0,
        details: [`Erro ao testar: ${error}`],
        recommendations: ['Verificar implementação de tratamento de erros']
      });
    }

    return errorTests;
  };

  // Testes de Performance
  const testPerformance = async (): Promise<UsabilityTest[]> => {
    const performanceTests: UsabilityTest[] = [];

    // Teste 1: Tempo de resposta
    try {
      let score = 10;
      const details: string[] = [];
      const recommendations: string[] = [];
      
      const endpoints = [
        { url: '/api/orcamentos', name: 'Orçamentos' },
        { url: '/api/estoque/produtos', name: 'Produtos' },
        { url: '/api/ordens-servico', name: 'Ordens de Serviço' }
      ];
      
      for (const endpoint of endpoints) {
        const startTime = performance.now();
        
        try {
          const response = await fetch(`${baseUrl}${endpoint.url}`, { ...apiConfig });
          const endTime = performance.now();
          const responseTime = endTime - startTime;
          
          if (responseTime < 200) {
            details.push(`${endpoint.name}: Excelente (${responseTime.toFixed(2)}ms)`);
          } else if (responseTime < 500) {
            details.push(`${endpoint.name}: Bom (${responseTime.toFixed(2)}ms)`);
          } else if (responseTime < 1000) {
            score -= 1;
            details.push(`${endpoint.name}: Aceitável (${responseTime.toFixed(2)}ms)`);
            recommendations.push(`Otimizar performance do endpoint ${endpoint.name}`);
          } else {
            score -= 3;
            details.push(`${endpoint.name}: Lento (${responseTime.toFixed(2)}ms)`);
            recommendations.push(`Urgente: Otimizar performance do endpoint ${endpoint.name}`);
          }
        } catch (error) {
          score -= 2;
          details.push(`${endpoint.name}: Erro de conectividade`);
        }
      }
      
      performanceTests.push({
        id: 'performance_response_time',
        name: 'Tempo de Resposta',
        description: 'Verifica se os endpoints respondem dentro do tempo aceitável',
        category: 'performance',
        status: score >= 8 ? 'passed' : score >= 6 ? 'warning' : 'failed',
        score,
        details,
        recommendations
      });
      
    } catch (error) {
      performanceTests.push({
        id: 'performance_response_time',
        name: 'Tempo de Resposta',
        description: 'Verifica se os endpoints respondem dentro do tempo aceitável',
        category: 'performance',
        status: 'failed',
        score: 0,
        details: [`Erro ao testar: ${error}`],
        recommendations: ['Verificar conectividade e configuração da API']
      });
    }

    return performanceTests;
  };

  // Função principal para executar todos os testes de usabilidade
  const runUsabilityTests = async () => {
    setIsRunning(true);
    setTests([]);
    
    try {
      setCurrentCategory('Testando Design da API...');
      const designTests = await testApiDesign();
      setTests(prev => [...prev, ...designTests]);
      
      setCurrentCategory('Testando Tratamento de Erros...');
      const errorTests = await testErrorHandling();
      setTests(prev => [...prev, ...errorTests]);
      
      setCurrentCategory('Testando Performance...');
      const performanceTests = await testPerformance();
      setTests(prev => [...prev, ...performanceTests]);
      
      // Calcular score geral
      const allTests = [...designTests, ...errorTests, ...performanceTests];
      const totalScore = allTests.reduce((sum, test) => sum + test.score, 0);
      const avgScore = totalScore / allTests.length;
      setOverallScore(avgScore);
      
    } catch (error) {
      console.error('Erro durante testes de usabilidade:', error);
    } finally {
      setIsRunning(false);
      setCurrentCategory('');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'passed': return '✅';
      case 'warning': return '⚠️';
      case 'failed': return '❌';
      default: return '⏳';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'api_design': return '#3498db';
      case 'error_handling': return '#e74c3c';
      case 'performance': return '#f39c12';
      case 'data_consistency': return '#9b59b6';
      case 'documentation': return '#2ecc71';
      default: return '#95a5a6';
    }
  };

  return (
    <div className="usability-validator">
      <h2>🎯 Validação de Usabilidade - Agente TRAE</h2>
      
      <div className="validator-controls">
        <button 
          onClick={runUsabilityTests} 
          disabled={isRunning}
          className="btn btn-primary"
        >
          {isRunning ? 'Executando Validação...' : 'Iniciar Validação de Usabilidade'}
        </button>
        
        {currentCategory && (
          <div className="current-category">
            <span>🔄 {currentCategory}</span>
          </div>
        )}
      </div>

      {overallScore > 0 && (
        <div className="overall-score">
          <h3>📊 Score Geral de Usabilidade: {overallScore.toFixed(1)}/10</h3>
          <div className="score-bar">
            <div 
              className="score-fill" 
              style={{ 
                width: `${(overallScore / 10) * 100}%`,
                backgroundColor: overallScore >= 8 ? '#2ecc71' : overallScore >= 6 ? '#f39c12' : '#e74c3c'
              }}
            ></div>
          </div>
        </div>
      )}

      {tests.length > 0 && (
        <div className="usability-results">
          <h3>🧪 Resultados da Validação</h3>
          
          {tests.map((test, index) => (
            <div key={index} className="test-card">
              <div className="test-header">
                <span className="test-status">{getStatusIcon(test.status)}</span>
                <h4>{test.name}</h4>
                <span 
                  className="test-category"
                  style={{ backgroundColor: getCategoryColor(test.category) }}
                >
                  {test.category.replace('_', ' ')}
                </span>
                <span className="test-score">{test.score.toFixed(1)}/10</span>
              </div>
              
              <p className="test-description">{test.description}</p>
              
              <div className="test-details">
                <h5>📋 Detalhes:</h5>
                <ul>
                  {test.details.map((detail, i) => (
                    <li key={i}>{detail}</li>
                  ))}
                </ul>
              </div>
              
              {test.recommendations.length > 0 && (
                <div className="test-recommendations">
                  <h5>💡 Recomendações:</h5>
                  <ul>
                    {test.recommendations.map((rec, i) => (
                      <li key={i}>{rec}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UsabilityValidator;