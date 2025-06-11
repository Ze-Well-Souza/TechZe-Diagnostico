// Componente de Medição de Performance - Agente TRAE testando Backend CURSOR
// Data: 2025-01-09
// Testador: Agente TRAE

import React, { useState, useEffect } from 'react';

interface PerformanceMetric {
  endpoint: string;
  method: string;
  averageResponseTime: number;
  minResponseTime: number;
  maxResponseTime: number;
  successRate: number;
  errorRate: number;
  throughput: number; // requests per second
  memoryUsage?: number;
  cpuUsage?: number;
  status: 'excellent' | 'good' | 'acceptable' | 'poor' | 'critical';
}

interface LoadTestResult {
  concurrentUsers: number;
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  requestsPerSecond: number;
  errors: string[];
}

interface PerformanceMeterProps {
  baseUrl: string;
  authToken?: string;
}

const PerformanceMeter: React.FC<PerformanceMeterProps> = ({ baseUrl, authToken }) => {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [loadTestResults, setLoadTestResults] = useState<LoadTestResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentTest, setCurrentTest] = useState<string>('');
  const [testProgress, setTestProgress] = useState<number>(0);

  // Configuração base para requisições
  const apiConfig = {
    headers: {
      'Content-Type': 'application/json',
      ...(authToken && { 'Authorization': `Bearer ${authToken}` })
    }
  };

  // Endpoints para teste de performance
  const testEndpoints = [
    { url: '/api/orcamentos', method: 'GET', name: 'Listar Orçamentos' },
    { url: '/api/orcamentos', method: 'POST', name: 'Criar Orçamento' },
    { url: '/api/estoque/produtos', method: 'GET', name: 'Listar Produtos' },
    { url: '/api/estoque/produtos', method: 'POST', name: 'Criar Produto' },
    { url: '/api/ordens-servico', method: 'GET', name: 'Listar Ordens de Serviço' },
    { url: '/api/ordens-servico', method: 'POST', name: 'Criar Ordem de Serviço' }
  ];

  // Dados de teste para requisições POST
  const testData = {
    orcamento: {
      cliente_id: 1,
      descricao: "Orçamento teste performance",
      valor_total: 1000.00,
      status: 'PENDENTE',
      data_validade: "2025-02-09",
      itens: [{
        produto_id: 1,
        quantidade: 1,
        preco_unitario: 1000.00
      }]
    },
    produto: {
      nome: "Produto Teste Performance",
      categoria_id: 1,
      preco_venda: 100.00,
      preco_custo: 60.00,
      unidade_medida: "UN",
      estoque_minimo: 10,
      estoque_atual: 50,
      ativo: true
    },
    ordemServico: {
      cliente_id: 1,
      equipamento: "Equipamento Teste",
      problema_relatado: "Problema teste performance",
      prioridade: 'MEDIA'
    }
  };

  // Função para executar uma única requisição e medir performance
  const measureSingleRequest = async (endpoint: any): Promise<{
    responseTime: number;
    success: boolean;
    error?: string;
  }> => {
    const startTime = performance.now();
    
    try {
      let requestConfig = { ...apiConfig };
      
      if (endpoint.method === 'POST') {
        requestConfig = {
          ...requestConfig,
          method: 'POST',
          body: JSON.stringify(
            endpoint.url.includes('orcamentos') ? testData.orcamento :
            endpoint.url.includes('produtos') ? testData.produto :
            testData.ordemServico
          )
        };
      }
      
      const response = await fetch(`${baseUrl}${endpoint.url}`, requestConfig);
      const endTime = performance.now();
      
      return {
        responseTime: endTime - startTime,
        success: response.ok,
        error: response.ok ? undefined : `HTTP ${response.status}: ${response.statusText}`
      };
      
    } catch (error) {
      const endTime = performance.now();
      return {
        responseTime: endTime - startTime,
        success: false,
        error: `Network error: ${error}`
      };
    }
  };

  // Função para executar múltiplas requisições e calcular métricas
  const measureEndpointPerformance = async (endpoint: any, iterations: number = 10): Promise<PerformanceMetric> => {
    const results: { responseTime: number; success: boolean; error?: string }[] = [];
    
    setCurrentTest(`Testando ${endpoint.name} (${iterations} requisições)...`);
    
    for (let i = 0; i < iterations; i++) {
      const result = await measureSingleRequest(endpoint);
      results.push(result);
      setTestProgress(((i + 1) / iterations) * 100);
      
      // Pequena pausa entre requisições para não sobrecarregar
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    const responseTimes = results.map(r => r.responseTime);
    const successfulRequests = results.filter(r => r.success).length;
    const failedRequests = results.length - successfulRequests;
    
    const averageResponseTime = responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length;
    const minResponseTime = Math.min(...responseTimes);
    const maxResponseTime = Math.max(...responseTimes);
    const successRate = (successfulRequests / results.length) * 100;
    const errorRate = (failedRequests / results.length) * 100;
    
    // Calcular throughput (requisições por segundo)
    const totalTime = responseTimes.reduce((sum, time) => sum + time, 0) / 1000; // converter para segundos
    const throughput = results.length / totalTime;
    
    // Determinar status baseado na performance
    let status: PerformanceMetric['status'];
    if (averageResponseTime < 200 && successRate >= 99) {
      status = 'excellent';
    } else if (averageResponseTime < 500 && successRate >= 95) {
      status = 'good';
    } else if (averageResponseTime < 1000 && successRate >= 90) {
      status = 'acceptable';
    } else if (averageResponseTime < 2000 && successRate >= 80) {
      status = 'poor';
    } else {
      status = 'critical';
    }
    
    return {
      endpoint: endpoint.url,
      method: endpoint.method,
      averageResponseTime,
      minResponseTime,
      maxResponseTime,
      successRate,
      errorRate,
      throughput,
      status
    };
  };

  // Teste de carga com usuários concorrentes
  const runLoadTest = async (concurrentUsers: number, requestsPerUser: number): Promise<LoadTestResult> => {
    setCurrentTest(`Teste de carga: ${concurrentUsers} usuários, ${requestsPerUser} req/usuário`);
    
    const startTime = Date.now();
    const promises: Promise<any>[] = [];
    const errors: string[] = [];
    
    // Criar promessas para usuários concorrentes
    for (let user = 0; user < concurrentUsers; user++) {
      for (let req = 0; req < requestsPerUser; req++) {
        const randomEndpoint = testEndpoints[Math.floor(Math.random() * testEndpoints.length)];
        
        const promise = measureSingleRequest(randomEndpoint)
          .then(result => {
            if (!result.success && result.error) {
              errors.push(result.error);
            }
            return result;
          })
          .catch(error => {
            errors.push(`User ${user}, Request ${req}: ${error}`);
            return { responseTime: 0, success: false, error: error.toString() };
          });
          
        promises.push(promise);
      }
    }
    
    const results = await Promise.all(promises);
    const endTime = Date.now();
    
    const totalRequests = results.length;
    const successfulRequests = results.filter(r => r.success).length;
    const failedRequests = totalRequests - successfulRequests;
    
    const responseTimes = results.filter(r => r.success).map(r => r.responseTime);
    const averageResponseTime = responseTimes.length > 0 
      ? responseTimes.reduce((sum, time) => sum + time, 0) / responseTimes.length 
      : 0;
    
    const totalTimeSeconds = (endTime - startTime) / 1000;
    const requestsPerSecond = totalRequests / totalTimeSeconds;
    
    return {
      concurrentUsers,
      totalRequests,
      successfulRequests,
      failedRequests,
      averageResponseTime,
      requestsPerSecond,
      errors: [...new Set(errors)].slice(0, 10) // Limitar a 10 erros únicos
    };
  };

  // Função principal para executar todos os testes de performance
  const runPerformanceTests = async () => {
    setIsRunning(true);
    setMetrics([]);
    setLoadTestResults([]);
    setTestProgress(0);
    
    try {
      // Teste de performance individual dos endpoints
      const endpointMetrics: PerformanceMetric[] = [];
      
      for (const endpoint of testEndpoints) {
        const metric = await measureEndpointPerformance(endpoint, 10);
        endpointMetrics.push(metric);
        setMetrics(prev => [...prev, metric]);
      }
      
      // Testes de carga progressivos
      const loadTests = [
        { users: 5, requests: 5 },
        { users: 10, requests: 5 },
        { users: 20, requests: 3 },
        { users: 50, requests: 2 }
      ];
      
      for (const loadTest of loadTests) {
        const result = await runLoadTest(loadTest.users, loadTest.requests);
        setLoadTestResults(prev => [...prev, result]);
      }
      
    } catch (error) {
      console.error('Erro durante testes de performance:', error);
    } finally {
      setIsRunning(false);
      setCurrentTest('');
      setTestProgress(0);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return '#2ecc71';
      case 'good': return '#3498db';
      case 'acceptable': return '#f39c12';
      case 'poor': return '#e67e22';
      case 'critical': return '#e74c3c';
      default: return '#95a5a6';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent': return '🚀';
      case 'good': return '✅';
      case 'acceptable': return '⚠️';
      case 'poor': return '🐌';
      case 'critical': return '🚨';
      default: return '❓';
    }
  };

  return (
    <div className="performance-meter">
      <h2>⚡ Medição de Performance - Agente TRAE</h2>
      
      <div className="meter-controls">
        <button 
          onClick={runPerformanceTests} 
          disabled={isRunning}
          className="btn btn-primary"
        >
          {isRunning ? 'Executando Testes...' : 'Iniciar Testes de Performance'}
        </button>
        
        {currentTest && (
          <div className="current-test">
            <span>🔄 {currentTest}</span>
            {testProgress > 0 && (
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${testProgress}%` }}
                ></div>
              </div>
            )}
          </div>
        )}
      </div>

      {metrics.length > 0 && (
        <div className="performance-results">
          <h3>📊 Métricas de Performance por Endpoint</h3>
          
          <div className="metrics-grid">
            {metrics.map((metric, index) => (
              <div key={index} className="metric-card">
                <div className="metric-header">
                  <span className="status-icon">{getStatusIcon(metric.status)}</span>
                  <h4>{metric.method} {metric.endpoint}</h4>
                  <span 
                    className="status-badge"
                    style={{ backgroundColor: getStatusColor(metric.status) }}
                  >
                    {metric.status}
                  </span>
                </div>
                
                <div className="metric-details">
                  <div className="metric-row">
                    <span>Tempo Médio:</span>
                    <span>{metric.averageResponseTime.toFixed(2)}ms</span>
                  </div>
                  <div className="metric-row">
                    <span>Min/Max:</span>
                    <span>{metric.minResponseTime.toFixed(2)}ms / {metric.maxResponseTime.toFixed(2)}ms</span>
                  </div>
                  <div className="metric-row">
                    <span>Taxa de Sucesso:</span>
                    <span>{metric.successRate.toFixed(1)}%</span>
                  </div>
                  <div className="metric-row">
                    <span>Throughput:</span>
                    <span>{metric.throughput.toFixed(2)} req/s</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {loadTestResults.length > 0 && (
        <div className="load-test-results">
          <h3>🏋️ Resultados dos Testes de Carga</h3>
          
          <table className="load-test-table">
            <thead>
              <tr>
                <th>Usuários</th>
                <th>Total Req.</th>
                <th>Sucessos</th>
                <th>Falhas</th>
                <th>Tempo Médio</th>
                <th>Req/s</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loadTestResults.map((result, index) => {
                const successRate = (result.successfulRequests / result.totalRequests) * 100;
                const status = successRate >= 95 ? 'excellent' : 
                              successRate >= 90 ? 'good' : 
                              successRate >= 80 ? 'acceptable' : 'poor';
                
                return (
                  <tr key={index}>
                    <td>{result.concurrentUsers}</td>
                    <td>{result.totalRequests}</td>
                    <td>{result.successfulRequests}</td>
                    <td>{result.failedRequests}</td>
                    <td>{result.averageResponseTime.toFixed(2)}ms</td>
                    <td>{result.requestsPerSecond.toFixed(2)}</td>
                    <td>
                      <span style={{ color: getStatusColor(status) }}>
                        {getStatusIcon(status)} {status}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          
          {loadTestResults.some(r => r.errors.length > 0) && (
            <div className="load-test-errors">
              <h4>🚨 Erros Encontrados:</h4>
              {loadTestResults.map((result, index) => 
                result.errors.length > 0 && (
                  <div key={index}>
                    <h5>{result.concurrentUsers} usuários:</h5>
                    <ul>
                      {result.errors.map((error, i) => (
                        <li key={i}>{error}</li>
                      ))}
                    </ul>
                  </div>
                )
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PerformanceMeter;