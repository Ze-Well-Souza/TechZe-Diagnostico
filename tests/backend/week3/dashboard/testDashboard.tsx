/**
 * Dashboard de Monitoramento de Testes - Semana 3
 * Agente TRAE testando Backend do CURSOR
 * Data: 09/01/2025
 */

import React, { useState, useEffect, useCallback } from 'react';
import { TestSession, RealTestResult } from '../realTestExecutor';
import { AutomationSession } from '../automatedTestRunner';

interface DashboardProps {
  automationSession?: AutomationSession;
  currentTestSession?: TestSession;
  refreshInterval?: number;
}

interface DashboardMetrics {
  totalTests: number;
  passedTests: number;
  failedTests: number;
  errorTests: number;
  averageResponseTime: number;
  currentPassRate: number;
  systemHealth: 'excellent' | 'good' | 'warning' | 'critical';
  apiScores: {
    orcamentos: number;
    estoque: number;
    ordemServico: number;
  };
  recentIssues: string[];
  performanceGrade: string;
}

const TestDashboard: React.FC<DashboardProps> = ({ 
  automationSession, 
  currentTestSession, 
  refreshInterval = 5000 
}) => {
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalTests: 0,
    passedTests: 0,
    failedTests: 0,
    errorTests: 0,
    averageResponseTime: 0,
    currentPassRate: 0,
    systemHealth: 'good',
    apiScores: { orcamentos: 0, estoque: 0, ordemServico: 0 },
    recentIssues: [],
    performanceGrade: 'N/A'
  });
  
  const [isLive, setIsLive] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [alerts, setAlerts] = useState<Array<{id: string, type: string, message: string, timestamp: Date}>>([]);

  // Calcular métricas baseadas nos dados atuais
  const calculateMetrics = useCallback((): DashboardMetrics => {
    if (!currentTestSession && !automationSession) {
      return metrics;
    }

    let totalTests = 0;
    let passedTests = 0;
    let failedTests = 0;
    let errorTests = 0;
    let totalResponseTime = 0;
    let validResponseCount = 0;
    let apiScores = { orcamentos: 0, estoque: 0, ordemServico: 0 };
    let recentIssues: string[] = [];
    let performanceGrade = 'N/A';

    // Se temos uma sessão de automação, usar dados agregados
    if (automationSession && automationSession.testSessions.length > 0) {
      const latestSession = automationSession.testSessions[automationSession.testSessions.length - 1];
      totalTests = latestSession.totalTests;
      passedTests = latestSession.metrics.passedTests;
      failedTests = latestSession.metrics.failedTests;
      errorTests = latestSession.metrics.skippedTests;
      totalResponseTime = latestSession.metrics.averageResponseTime * latestSession.totalTests;
      validResponseCount = latestSession.totalTests;
      apiScores = latestSession.summary.apiScores;
      recentIssues = latestSession.summary.criticalIssues.slice(0, 5);
      performanceGrade = latestSession.summary.performanceGrade;
    }
    // Senão, usar sessão atual
    else if (currentTestSession) {
      totalTests = currentTestSession.totalTests;
      passedTests = currentTestSession.metrics.passedTests;
      failedTests = currentTestSession.metrics.failedTests;
      errorTests = currentTestSession.metrics.skippedTests;
      
      // Calcular tempo médio de resposta
      const validResults = currentTestSession.results.filter(r => r.responseTime > 0);
      if (validResults.length > 0) {
        totalResponseTime = validResults.reduce((sum, r) => sum + r.responseTime, 0);
        validResponseCount = validResults.length;
      }
      
      apiScores = currentTestSession.summary.apiScores;
      recentIssues = currentTestSession.summary.criticalIssues.slice(0, 5);
      performanceGrade = currentTestSession.summary.performanceGrade;
    }

    const averageResponseTime = validResponseCount > 0 ? totalResponseTime / validResponseCount : 0;
    const currentPassRate = totalTests > 0 ? (passedTests / totalTests) * 100 : 0;
    
    // Determinar saúde do sistema
    let systemHealth: 'excellent' | 'good' | 'warning' | 'critical' = 'good';
    if (currentPassRate >= 95 && averageResponseTime < 300) {
      systemHealth = 'excellent';
    } else if (currentPassRate >= 80 && averageResponseTime < 800) {
      systemHealth = 'good';
    } else if (currentPassRate >= 60 && averageResponseTime < 1500) {
      systemHealth = 'warning';
    } else {
      systemHealth = 'critical';
    }

    return {
      totalTests,
      passedTests,
      failedTests,
      errorTests,
      averageResponseTime,
      currentPassRate,
      systemHealth,
      apiScores,
      recentIssues,
      performanceGrade
    };
  }, [currentTestSession, automationSession, metrics]);

  // Atualizar métricas periodicamente
  useEffect(() => {
    const updateMetrics = () => {
      const newMetrics = calculateMetrics();
      
      // Verificar se há alertas
      checkForAlerts(newMetrics);
      
      setMetrics(newMetrics);
      setLastUpdate(new Date());
    };

    updateMetrics();
    
    if (isLive) {
      const interval = setInterval(updateMetrics, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [calculateMetrics, isLive, refreshInterval]);

  // Verificar alertas
  const checkForAlerts = (newMetrics: DashboardMetrics) => {
    const newAlerts = [];
    
    // Alert para taxa de sucesso baixa
    if (newMetrics.currentPassRate < 80 && newMetrics.totalTests > 10) {
      newAlerts.push({
        id: `low-pass-rate-${Date.now()}`,
        type: 'warning',
        message: `Taxa de sucesso baixa: ${newMetrics.currentPassRate.toFixed(1)}%`,
        timestamp: new Date()
      });
    }
    
    // Alert para tempo de resposta alto
    if (newMetrics.averageResponseTime > 1000) {
      newAlerts.push({
        id: `high-response-time-${Date.now()}`,
        type: 'warning',
        message: `Tempo de resposta alto: ${newMetrics.averageResponseTime.toFixed(0)}ms`,
        timestamp: new Date()
      });
    }
    
    // Alert para saúde crítica
    if (newMetrics.systemHealth === 'critical') {
      newAlerts.push({
        id: `critical-health-${Date.now()}`,
        type: 'error',
        message: 'Sistema em estado crítico',
        timestamp: new Date()
      });
    }
    
    if (newAlerts.length > 0) {
      setAlerts(prev => [...newAlerts, ...prev].slice(0, 10)); // Manter apenas 10 alertas
    }
  };

  // Obter cor baseada na saúde do sistema
  const getHealthColor = (health: string): string => {
    switch (health) {
      case 'excellent': return '#10B981'; // Verde
      case 'good': return '#3B82F6'; // Azul
      case 'warning': return '#F59E0B'; // Amarelo
      case 'critical': return '#EF4444'; // Vermelho
      default: return '#6B7280'; // Cinza
    }
  };

  // Obter cor da API baseada no score
  const getApiScoreColor = (score: number): string => {
    if (score >= 90) return '#10B981';
    if (score >= 80) return '#3B82F6';
    if (score >= 70) return '#F59E0B';
    return '#EF4444';
  };

  // Formatar tempo
  const formatTime = (date: Date): string => {
    return date.toLocaleTimeString('pt-BR');
  };

  // Calcular uptime da automação
  const getAutomationUptime = (): string => {
    if (!automationSession) return 'N/A';
    
    const now = new Date();
    const start = automationSession.startTime;
    const diffMs = now.getTime() - start.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
    
    return `${diffHours}h ${diffMinutes}m`;
  };

  return (
    <div style={{ 
      fontFamily: 'Arial, sans-serif', 
      padding: '20px', 
      backgroundColor: '#F9FAFB',
      minHeight: '100vh'
    }}>
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        marginBottom: '30px',
        padding: '20px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <div>
          <h1 style={{ margin: 0, color: '#1F2937', fontSize: '28px' }}>
            🧪 Dashboard de Testes - Semana 3
          </h1>
          <p style={{ margin: '5px 0 0 0', color: '#6B7280' }}>
            Agente TRAE testando Backend do CURSOR
          </p>
        </div>
        
        <div style={{ textAlign: 'right' }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '10px',
            marginBottom: '5px'
          }}>
            <span style={{ 
              width: '12px', 
              height: '12px', 
              borderRadius: '50%', 
              backgroundColor: isLive ? '#10B981' : '#EF4444',
              display: 'inline-block'
            }}></span>
            <span style={{ color: '#374151', fontWeight: 'bold' }}>
              {isLive ? 'AO VIVO' : 'PAUSADO'}
            </span>
          </div>
          <p style={{ margin: 0, color: '#6B7280', fontSize: '14px' }}>
            Última atualização: {formatTime(lastUpdate)}
          </p>
        </div>
      </div>

      {/* Métricas Principais */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
        gap: '20px',
        marginBottom: '30px'
      }}>
        {/* Saúde do Sistema */}
        <div style={{ 
          padding: '20px', 
          backgroundColor: 'white', 
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
          borderLeft: `4px solid ${getHealthColor(metrics.systemHealth)}`
        }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#374151' }}>🏥 Saúde do Sistema</h3>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: getHealthColor(metrics.systemHealth) }}>
            {metrics.systemHealth.toUpperCase()}
          </div>
          <p style={{ margin: '5px 0 0 0', color: '#6B7280', fontSize: '14px' }}>
            Taxa de sucesso: {metrics.currentPassRate.toFixed(1)}%
          </p>
        </div>

        {/* Total de Testes */}
        <div style={{ 
          padding: '20px', 
          backgroundColor: 'white', 
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#374151' }}>📊 Total de Testes</h3>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#1F2937' }}>
            {metrics.totalTests}
          </div>
          <div style={{ display: 'flex', gap: '15px', marginTop: '10px', fontSize: '14px' }}>
            <span style={{ color: '#10B981' }}>✅ {metrics.passedTests}</span>
            <span style={{ color: '#EF4444' }}>❌ {metrics.failedTests}</span>
            <span style={{ color: '#F59E0B' }}>⚠️ {metrics.errorTests}</span>
          </div>
        </div>

        {/* Performance */}
        <div style={{ 
          padding: '20px', 
          backgroundColor: 'white', 
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 10px 0', color: '#374151' }}>⚡ Performance</h3>
          <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1F2937' }}>
            {metrics.averageResponseTime.toFixed(0)}ms
          </div>
          <div style={{ 
            marginTop: '10px',
            padding: '5px 10px',
            backgroundColor: metrics.performanceGrade === 'A' ? '#DCFCE7' : 
                           metrics.performanceGrade === 'B' ? '#DBEAFE' : 
                           metrics.performanceGrade === 'C' ? '#FEF3C7' : '#FEE2E2',
            borderRadius: '4px',
            display: 'inline-block',
            fontSize: '14px',
            fontWeight: 'bold'
          }}>
            Grade: {metrics.performanceGrade}
          </div>
        </div>

        {/* Automação Status */}
        {automationSession && (
          <div style={{ 
            padding: '20px', 
            backgroundColor: 'white', 
            borderRadius: '8px',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
          }}>
            <h3 style={{ margin: '0 0 10px 0', color: '#374151' }}>🤖 Automação</h3>
            <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#1F2937' }}>
              {automationSession.status.toUpperCase()}
            </div>
            <div style={{ fontSize: '14px', color: '#6B7280', marginTop: '5px' }}>
              Uptime: {getAutomationUptime()}
            </div>
            <div style={{ fontSize: '14px', color: '#6B7280' }}>
              Execuções: {automationSession.totalRuns}
            </div>
          </div>
        )}
      </div>

      {/* Scores das APIs */}
      <div style={{ 
        padding: '20px', 
        backgroundColor: 'white', 
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        marginBottom: '30px'
      }}>
        <h3 style={{ margin: '0 0 20px 0', color: '#374151' }}>🎯 Scores das APIs</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
          {/* Orçamentos */}
          <div style={{ textAlign: 'center' }}>
            <h4 style={{ margin: '0 0 10px 0', color: '#374151' }}>💰 Orçamentos</h4>
            <div style={{ 
              fontSize: '36px', 
              fontWeight: 'bold', 
              color: getApiScoreColor(metrics.apiScores.orcamentos)
            }}>
              {metrics.apiScores.orcamentos}/100
            </div>
            <div style={{ 
              width: '100%', 
              height: '8px', 
              backgroundColor: '#E5E7EB', 
              borderRadius: '4px',
              marginTop: '10px'
            }}>
              <div style={{ 
                width: `${metrics.apiScores.orcamentos}%`, 
                height: '100%', 
                backgroundColor: getApiScoreColor(metrics.apiScores.orcamentos),
                borderRadius: '4px'
              }}></div>
            </div>
          </div>

          {/* Estoque */}
          <div style={{ textAlign: 'center' }}>
            <h4 style={{ margin: '0 0 10px 0', color: '#374151' }}>📦 Estoque</h4>
            <div style={{ 
              fontSize: '36px', 
              fontWeight: 'bold', 
              color: getApiScoreColor(metrics.apiScores.estoque)
            }}>
              {metrics.apiScores.estoque}/100
            </div>
            <div style={{ 
              width: '100%', 
              height: '8px', 
              backgroundColor: '#E5E7EB', 
              borderRadius: '4px',
              marginTop: '10px'
            }}>
              <div style={{ 
                width: `${metrics.apiScores.estoque}%`, 
                height: '100%', 
                backgroundColor: getApiScoreColor(metrics.apiScores.estoque),
                borderRadius: '4px'
              }}></div>
            </div>
          </div>

          {/* Ordem de Serviço */}
          <div style={{ textAlign: 'center' }}>
            <h4 style={{ margin: '0 0 10px 0', color: '#374151' }}>🔧 Ordem de Serviço</h4>
            <div style={{ 
              fontSize: '36px', 
              fontWeight: 'bold', 
              color: getApiScoreColor(metrics.apiScores.ordemServico)
            }}>
              {metrics.apiScores.ordemServico}/100
            </div>
            <div style={{ 
              width: '100%', 
              height: '8px', 
              backgroundColor: '#E5E7EB', 
              borderRadius: '4px',
              marginTop: '10px'
            }}>
              <div style={{ 
                width: `${metrics.apiScores.ordemServico}%`, 
                height: '100%', 
                backgroundColor: getApiScoreColor(metrics.apiScores.ordemServico),
                borderRadius: '4px'
              }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Alertas e Issues Recentes */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        {/* Alertas */}
        <div style={{ 
          padding: '20px', 
          backgroundColor: 'white', 
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 15px 0', color: '#374151' }}>🚨 Alertas Recentes</h3>
          {alerts.length === 0 ? (
            <p style={{ color: '#6B7280', fontStyle: 'italic' }}>Nenhum alerta ativo</p>
          ) : (
            <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
              {alerts.map(alert => (
                <div key={alert.id} style={{ 
                  padding: '10px', 
                  marginBottom: '10px',
                  borderRadius: '4px',
                  backgroundColor: alert.type === 'error' ? '#FEE2E2' : '#FEF3C7',
                  borderLeft: `4px solid ${alert.type === 'error' ? '#EF4444' : '#F59E0B'}`
                }}>
                  <div style={{ fontWeight: 'bold', fontSize: '14px' }}>
                    {alert.message}
                  </div>
                  <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '5px' }}>
                    {formatTime(alert.timestamp)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Issues Recentes */}
        <div style={{ 
          padding: '20px', 
          backgroundColor: 'white', 
          borderRadius: '8px',
          boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ margin: '0 0 15px 0', color: '#374151' }}>🔍 Issues Identificados</h3>
          {metrics.recentIssues.length === 0 ? (
            <p style={{ color: '#6B7280', fontStyle: 'italic' }}>Nenhum issue crítico</p>
          ) : (
            <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
              {metrics.recentIssues.map((issue, index) => (
                <div key={index} style={{ 
                  padding: '10px', 
                  marginBottom: '10px',
                  borderRadius: '4px',
                  backgroundColor: '#FEF2F2',
                  borderLeft: '4px solid #EF4444'
                }}>
                  <div style={{ fontSize: '14px' }}>
                    {issue}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Controles */}
      <div style={{ 
        marginTop: '30px',
        padding: '20px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        textAlign: 'center'
      }}>
        <button 
          onClick={() => setIsLive(!isLive)}
          style={{
            padding: '10px 20px',
            marginRight: '10px',
            backgroundColor: isLive ? '#EF4444' : '#10B981',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          {isLive ? '⏸️ Pausar' : '▶️ Retomar'} Monitoramento
        </button>
        
        <button 
          onClick={() => setAlerts([])}
          style={{
            padding: '10px 20px',
            backgroundColor: '#6B7280',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          🗑️ Limpar Alertas
        </button>
      </div>
    </div>
  );
};

export default TestDashboard;