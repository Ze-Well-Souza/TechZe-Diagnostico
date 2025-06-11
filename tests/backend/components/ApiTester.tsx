// Componente de Teste de APIs - Agente TRAE testando Backend CURSOR
// Data: 2025-01-09
// Testador: Agente TRAE

import React, { useState, useEffect } from 'react';
import { OrcamentosApiTest, OrcamentosTestMetrics, orcamentosTestCases } from '../interfaces/orcamentosApi.interface';
import { EstoqueApiTest, EstoqueTestMetrics, estoqueTestCases } from '../interfaces/estoqueApi.interface';
import { OrdemServicoApiTest, OrdemServicoTestMetrics, ordemServicoTestCases } from '../interfaces/ordemServicoApi.interface';

interface ApiTestResult {
  endpoint: string;
  status: 'success' | 'error' | 'pending';
  responseTime: number;
  errorMessage?: string;
  usabilityScore: number;
  documentationScore: number;
}

interface ApiTesterProps {
  baseUrl: string;
  authToken?: string;
}

const ApiTester: React.FC<ApiTesterProps> = ({ baseUrl, authToken }) => {
  const [testResults, setTestResults] = useState<ApiTestResult[]>([]);
  const [currentTest, setCurrentTest] = useState<string>('');
  const [isRunning, setIsRunning] = useState(false);
  const [metrics, setMetrics] = useState<{
    orcamentos: OrcamentosTestMetrics;
    estoque: EstoqueTestMetrics;
    ordemServico: OrdemServicoTestMetrics;
  } | null>(null);

  // Configuração base para requisições
  const apiConfig = {
    headers: {
      'Content-Type': 'application/json',
      ...(authToken && { 'Authorization': `Bearer ${authToken}` })
    }
  };

  // Função para medir tempo de resposta
  const measureResponseTime = async (apiCall: () => Promise<any>): Promise<{ result: any; time: number }> => {
    const startTime = performance.now();
    try {
      const result = await apiCall();
      const endTime = performance.now();
      return { result, time: endTime - startTime };
    } catch (error) {
      const endTime = performance.now();
      throw { error, time: endTime - startTime };
    }
  };

  // Teste de usabilidade da API (facilidade de uso)
  const evaluateUsability = (endpoint: string, request: any, response: any): number => {
    let score = 10;
    
    // Verifica se a resposta tem estrutura consistente
    if (!response || typeof response !== 'object') score -= 2;
    
    // Verifica se campos obrigatórios estão presentes
    if (response && !response.id && endpoint.includes('create')) score -= 1;
    
    // Verifica se mensagens de erro são claras
    if (response && response.error && !response.message) score -= 1;
    
    // Verifica se a resposta inclui timestamps
    if (response && !response.data_criacao && !response.created_at) score -= 0.5;
    
    return Math.max(0, score);
  };

  // Teste de documentação (baseado na resposta da API)
  const evaluateDocumentation = (endpoint: string, response: any): number => {
    let score = 10;
    
    // Verifica se a API retorna códigos de status apropriados
    if (!response || response.status === undefined) score -= 2;
    
    // Verifica se há validação de entrada adequada
    if (response && response.error && !response.details) score -= 1;
    
    // Verifica se há metadados úteis na resposta
    if (response && !response.meta && !response.pagination) score -= 0.5;
    
    return Math.max(0, score);
  };

  // Testes da API de Orçamentos
  const testOrcamentosApi = async (): Promise<OrcamentosTestMetrics> => {
    const results: ApiTestResult[] = [];
    let totalResponseTime = 0;
    let workingEndpoints = 0;
    const criticalIssues: string[] = [];
    const performanceIssues: string[] = [];
    const usabilityIssues: string[] = [];

    setCurrentTest('Testando API de Orçamentos...');

    // Teste 1: Criar Orçamento
    try {
      const { result, time } = await measureResponseTime(async () => {
        const response = await fetch(`${baseUrl}/api/orcamentos`, {
          method: 'POST',
          ...apiConfig,
          body: JSON.stringify(orcamentosTestCases.validOrcamento)
        });
        return await response.json();
      });
      
      const usabilityScore = evaluateUsability('create', orcamentosTestCases.validOrcamento, result);
      const documentationScore = evaluateDocumentation('create', result);
      
      results.push({
        endpoint: 'POST /api/orcamentos',
        status: 'success',
        responseTime: time,
        usabilityScore,
        documentationScore
      });
      
      workingEndpoints++;
      totalResponseTime += time;
      
      if (time > 500) performanceIssues.push(`POST /api/orcamentos: ${time.toFixed(2)}ms`);
      if (usabilityScore < 8) usabilityIssues.push(`POST /api/orcamentos: Score ${usabilityScore}/10`);
      
    } catch (error: any) {
      results.push({
        endpoint: 'POST /api/orcamentos',
        status: 'error',
        responseTime: error.time || 0,
        errorMessage: error.message,
        usabilityScore: 0,
        documentationScore: 0
      });
      criticalIssues.push(`POST /api/orcamentos: ${error.message}`);
    }

    // Teste 2: Listar Orçamentos
    try {
      const { result, time } = await measureResponseTime(async () => {
        const response = await fetch(`${baseUrl}/api/orcamentos`, {
          method: 'GET',
          ...apiConfig
        });
        return await response.json();
      });
      
      const usabilityScore = evaluateUsability('list', {}, result);
      const documentationScore = evaluateDocumentation('list', result);
      
      results.push({
        endpoint: 'GET /api/orcamentos',
        status: 'success',
        responseTime: time,
        usabilityScore,
        documentationScore
      });
      
      workingEndpoints++;
      totalResponseTime += time;
      
      if (time > 500) performanceIssues.push(`GET /api/orcamentos: ${time.toFixed(2)}ms`);
      if (usabilityScore < 8) usabilityIssues.push(`GET /api/orcamentos: Score ${usabilityScore}/10`);
      
    } catch (error: any) {
      results.push({
        endpoint: 'GET /api/orcamentos',
        status: 'error',
        responseTime: error.time || 0,
        errorMessage: error.message,
        usabilityScore: 0,
        documentationScore: 0
      });
      criticalIssues.push(`GET /api/orcamentos: ${error.message}`);
    }

    // Adicionar mais testes para outros endpoints...
    // (Por brevidade, incluindo apenas 2 testes principais)

    setTestResults(prev => [...prev, ...results]);

    return {
      endpointsTested: results.length,
      endpointsWorking: workingEndpoints,
      averageResponseTime: totalResponseTime / results.length,
      usabilityScore: results.reduce((sum, r) => sum + r.usabilityScore, 0) / results.length,
      documentationScore: results.reduce((sum, r) => sum + r.documentationScore, 0) / results.length,
      criticalIssues,
      performanceIssues,
      usabilityIssues
    };
  };

  // Função principal para executar todos os testes
  const runAllTests = async () => {
    setIsRunning(true);
    setTestResults([]);
    
    try {
      const orcamentosMetrics = await testOrcamentosApi();
      // const estoqueMetrics = await testEstoqueApi();
      // const ordemServicoMetrics = await testOrdemServicoApi();
      
      setMetrics({
        orcamentos: orcamentosMetrics,
        estoque: {
          endpointsTested: 0,
          endpointsWorking: 0,
          averageResponseTime: 0,
          usabilityScore: 0,
          documentationScore: 0,
          criticalIssues: [],
          performanceIssues: [],
          usabilityIssues: [],
          dataConsistencyIssues: []
        },
        ordemServico: {
          endpointsTested: 0,
          endpointsWorking: 0,
          averageResponseTime: 0,
          usabilityScore: 0,
          documentationScore: 0,
          criticalIssues: [],
          performanceIssues: [],
          usabilityIssues: [],
          workflowIssues: [],
          businessLogicIssues: []
        }
      });
      
    } catch (error) {
      console.error('Erro durante execução dos testes:', error);
    } finally {
      setIsRunning(false);
      setCurrentTest('');
    }
  };

  return (
    <div className="api-tester">
      <h2>🧪 Teste de APIs Backend - Agente TRAE</h2>
      
      <div className="test-controls">
        <button 
          onClick={runAllTests} 
          disabled={isRunning}
          className="btn btn-primary"
        >
          {isRunning ? 'Executando Testes...' : 'Iniciar Testes Completos'}
        </button>
        
        {currentTest && (
          <div className="current-test">
            <span>🔄 {currentTest}</span>
          </div>
        )}
      </div>

      {testResults.length > 0 && (
        <div className="test-results">
          <h3>📊 Resultados dos Testes</h3>
          
          <table className="results-table">
            <thead>
              <tr>
                <th>Endpoint</th>
                <th>Status</th>
                <th>Tempo (ms)</th>
                <th>Usabilidade</th>
                <th>Documentação</th>
                <th>Erro</th>
              </tr>
            </thead>
            <tbody>
              {testResults.map((result, index) => (
                <tr key={index} className={`status-${result.status}`}>
                  <td>{result.endpoint}</td>
                  <td>
                    {result.status === 'success' ? '✅' : '❌'}
                    {result.status}
                  </td>
                  <td>{result.responseTime.toFixed(2)}</td>
                  <td>{result.usabilityScore.toFixed(1)}/10</td>
                  <td>{result.documentationScore.toFixed(1)}/10</td>
                  <td>{result.errorMessage || '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {metrics && (
        <div className="metrics-summary">
          <h3>📈 Resumo das Métricas</h3>
          
          <div className="metrics-grid">
            <div className="metric-card">
              <h4>Orçamentos API</h4>
              <p>Endpoints: {metrics.orcamentos.endpointsWorking}/{metrics.orcamentos.endpointsTested}</p>
              <p>Tempo médio: {metrics.orcamentos.averageResponseTime.toFixed(2)}ms</p>
              <p>Usabilidade: {metrics.orcamentos.usabilityScore.toFixed(1)}/10</p>
              <p>Documentação: {metrics.orcamentos.documentationScore.toFixed(1)}/10</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApiTester;