/**
 * Runner Automatizado de Testes - Semana 3
 * Agente TRAE testando Backend do CURSOR
 * Data: 09/01/2025
 */

import { RealTestExecutor, TestSession, runWeek3Tests } from './realTestExecutor';
import { TestConfig } from '../config/testConfig';

export interface AutomationConfig {
  runContinuous: boolean;
  intervalMinutes: number;
  maxRuns: number;
  emailNotifications: boolean;
  slackNotifications: boolean;
  generateDashboard: boolean;
  autoRetryFailed: boolean;
}

export interface AutomationSession {
  automationId: string;
  startTime: Date;
  endTime?: Date;
  totalRuns: number;
  successfulRuns: number;
  failedRuns: number;
  testSessions: TestSession[];
  config: AutomationConfig;
  status: 'running' | 'completed' | 'failed' | 'stopped';
}

export class AutomatedTestRunner {
  private automationSession: AutomationSession;
  private isRunning: boolean = false;
  private intervalId?: NodeJS.Timeout;

  constructor(config: AutomationConfig) {
    this.automationSession = {
      automationId: `auto-${Date.now()}`,
      startTime: new Date(),
      totalRuns: 0,
      successfulRuns: 0,
      failedRuns: 0,
      testSessions: [],
      config,
      status: 'running'
    };
  }

  // Iniciar automação
  async startAutomation(): Promise<void> {
    console.log('🤖 Iniciando Automação de Testes - Semana 3');
    console.log(`📋 Configuração:`);
    console.log(`   - Execução contínua: ${this.automationSession.config.runContinuous}`);
    console.log(`   - Intervalo: ${this.automationSession.config.intervalMinutes} minutos`);
    console.log(`   - Máximo de execuções: ${this.automationSession.config.maxRuns}`);
    console.log(`   - Retry automático: ${this.automationSession.config.autoRetryFailed}`);

    this.isRunning = true;

    try {
      // Primeira execução
      await this.runSingleTestCycle();

      // Se configurado para execução contínua
      if (this.automationSession.config.runContinuous) {
        this.scheduleNextRun();
      } else {
        this.completeAutomation();
      }

    } catch (error) {
      console.error('❌ Erro na automação:', error);
      this.automationSession.status = 'failed';
      await this.sendNotification('error', `Automação falhou: ${error.message}`);
    }
  }

  // Executar um ciclo de testes
  private async runSingleTestCycle(): Promise<void> {
    const cycleNumber = this.automationSession.totalRuns + 1;
    console.log(`\n🔄 Iniciando Ciclo ${cycleNumber}`);
    
    try {
      // Executar testes
      const testSession = await runWeek3Tests();
      
      // Registrar resultado
      this.automationSession.testSessions.push(testSession);
      this.automationSession.totalRuns++;
      
      if (testSession.summary.overallStatus === 'passed' || testSession.summary.overallStatus === 'partial') {
        this.automationSession.successfulRuns++;
        console.log(`✅ Ciclo ${cycleNumber} concluído com sucesso`);
        
        // Notificar sucesso se configurado
        if (testSession.summary.passRate === 100) {
          await this.sendNotification('success', `Ciclo ${cycleNumber}: 100% de sucesso!`);
        }
      } else {
        this.automationSession.failedRuns++;
        console.log(`❌ Ciclo ${cycleNumber} falhou`);
        
        // Notificar falha
        await this.sendNotification('warning', 
          `Ciclo ${cycleNumber} falhou. Taxa de sucesso: ${testSession.summary.passRate.toFixed(2)}%`);
        
        // Retry automático se configurado
        if (this.automationSession.config.autoRetryFailed) {
          console.log('🔄 Executando retry automático...');
          await this.delay(30000); // Aguardar 30 segundos
          await this.runSingleTestCycle();
        }
      }
      
      // Gerar relatório do ciclo
      await this.generateCycleReport(testSession, cycleNumber);
      
      // Atualizar dashboard se configurado
      if (this.automationSession.config.generateDashboard) {
        await this.updateDashboard();
      }
      
    } catch (error) {
      console.error(`❌ Erro no ciclo ${cycleNumber}:`, error);
      this.automationSession.failedRuns++;
      await this.sendNotification('error', `Ciclo ${cycleNumber} com erro: ${error.message}`);
    }
  }

  // Agendar próxima execução
  private scheduleNextRun(): void {
    if (!this.isRunning || this.automationSession.totalRuns >= this.automationSession.config.maxRuns) {
      this.completeAutomation();
      return;
    }

    const intervalMs = this.automationSession.config.intervalMinutes * 60 * 1000;
    console.log(`⏰ Próxima execução em ${this.automationSession.config.intervalMinutes} minutos`);
    
    this.intervalId = setTimeout(async () => {
      if (this.isRunning) {
        await this.runSingleTestCycle();
        this.scheduleNextRun();
      }
    }, intervalMs);
  }

  // Completar automação
  private completeAutomation(): void {
    this.isRunning = false;
    this.automationSession.endTime = new Date();
    this.automationSession.status = 'completed';
    
    if (this.intervalId) {
      clearTimeout(this.intervalId);
    }
    
    console.log('🏁 Automação concluída');
    console.log(`📊 Resumo:`);
    console.log(`   - Total de execuções: ${this.automationSession.totalRuns}`);
    console.log(`   - Sucessos: ${this.automationSession.successfulRuns}`);
    console.log(`   - Falhas: ${this.automationSession.failedRuns}`);
    console.log(`   - Taxa de sucesso: ${((this.automationSession.successfulRuns / this.automationSession.totalRuns) * 100).toFixed(2)}%`);
    
    // Gerar relatório final
    this.generateFinalReport();
    
    // Notificação final
    this.sendNotification('info', 
      `Automação concluída. ${this.automationSession.totalRuns} execuções realizadas.`);
  }

  // Parar automação
  async stopAutomation(): Promise<void> {
    console.log('🛑 Parando automação...');
    this.isRunning = false;
    this.automationSession.status = 'stopped';
    
    if (this.intervalId) {
      clearTimeout(this.intervalId);
    }
    
    await this.sendNotification('info', 'Automação interrompida pelo usuário');
  }

  // Gerar relatório de ciclo
  private async generateCycleReport(session: TestSession, cycleNumber: number): Promise<void> {
    const reportContent = `# Relatório Ciclo ${cycleNumber} - Semana 3
**Data:** ${new Date().toLocaleString('pt-BR')}
**Session ID:** ${session.sessionId}
**Ambiente:** ${session.environment.name}

## 📊 Resumo do Ciclo
- **Status:** ${session.summary.overallStatus.toUpperCase()}
- **Taxa de Sucesso:** ${session.summary.passRate.toFixed(2)}%
- **Testes Executados:** ${session.totalTests}
- **Tempo Médio:** ${session.summary.averageResponseTime.toFixed(2)}ms
- **Grade Performance:** ${session.summary.performanceGrade}

## 🎯 Scores por API
- **Orçamentos:** ${session.summary.apiScores.orcamentos}/100
- **Estoque:** ${session.summary.apiScores.estoque}/100
- **Ordem de Serviço:** ${session.summary.apiScores.ordemServico}/100

## ⚠️ Issues Identificados
${session.summary.criticalIssues.length > 0 ? 
  session.summary.criticalIssues.map(issue => `- ${issue}`).join('\n') : 
  'Nenhum issue crítico identificado.'}

## 💡 Recomendações
${session.summary.recommendations.length > 0 ? 
  session.summary.recommendations.map(rec => `- ${rec}`).join('\n') : 
  'Nenhuma recomendação específica.'}

---
*Relatório gerado automaticamente pelo Agente TRAE*
`;

    // Em implementação real, salvar arquivo
    console.log(`📄 Relatório do Ciclo ${cycleNumber} gerado`);
  }

  // Gerar relatório final da automação
  private async generateFinalReport(): Promise<void> {
    const duration = this.automationSession.endTime ? 
      (this.automationSession.endTime.getTime() - this.automationSession.startTime.getTime()) / 1000 / 60 : 0;
    
    const avgPassRate = this.automationSession.testSessions.length > 0 ?
      this.automationSession.testSessions.reduce((sum, session) => sum + session.summary.passRate, 0) / this.automationSession.testSessions.length : 0;
    
    const avgResponseTime = this.automationSession.testSessions.length > 0 ?
      this.automationSession.testSessions.reduce((sum, session) => sum + session.summary.averageResponseTime, 0) / this.automationSession.testSessions.length : 0;

    const reportContent = `# Relatório Final de Automação - Semana 3
**Data Início:** ${this.automationSession.startTime.toLocaleString('pt-BR')}
**Data Fim:** ${this.automationSession.endTime?.toLocaleString('pt-BR')}
**Duração Total:** ${duration.toFixed(2)} minutos
**ID da Automação:** ${this.automationSession.automationId}

## 🎯 Resumo Executivo
- **Status da Automação:** ${this.automationSession.status.toUpperCase()}
- **Total de Execuções:** ${this.automationSession.totalRuns}
- **Execuções Bem-sucedidas:** ${this.automationSession.successfulRuns}
- **Execuções Falharam:** ${this.automationSession.failedRuns}
- **Taxa de Sucesso da Automação:** ${((this.automationSession.successfulRuns / this.automationSession.totalRuns) * 100).toFixed(2)}%

## 📊 Métricas Médias
- **Taxa de Sucesso Média dos Testes:** ${avgPassRate.toFixed(2)}%
- **Tempo de Resposta Médio:** ${avgResponseTime.toFixed(2)}ms
- **Estabilidade do Sistema:** ${this.calculateSystemStability()}%

## 📈 Tendências Identificadas
${this.analyzeTrends()}

## 🔍 Análise de Qualidade
${this.generateQualityAnalysis()}

## 🎯 Conclusões e Recomendações Finais
${this.generateFinalRecommendations()}

## 📋 Próximos Passos
1. Analisar padrões de falha identificados
2. Implementar melhorias baseadas nas métricas coletadas
3. Ajustar configurações de automação se necessário
4. Planejar testes de regressão
5. Documentar lições aprendidas

---
*Relatório gerado automaticamente pelo Sistema de Automação do Agente TRAE*
*Semana 3 - Testes Cruzados Backend CURSOR*
`;

    console.log('📄 Relatório Final de Automação gerado');
  }

  // Calcular estabilidade do sistema
  private calculateSystemStability(): number {
    if (this.automationSession.testSessions.length === 0) return 0;
    
    const consistentResults = this.automationSession.testSessions.filter(session => 
      session.summary.passRate >= 80
    ).length;
    
    return Math.round((consistentResults / this.automationSession.testSessions.length) * 100);
  }

  // Analisar tendências
  private analyzeTrends(): string {
    if (this.automationSession.testSessions.length < 2) {
      return 'Dados insuficientes para análise de tendências.';
    }
    
    const sessions = this.automationSession.testSessions;
    const trends = [];
    
    // Tendência de taxa de sucesso
    const firstHalf = sessions.slice(0, Math.floor(sessions.length / 2));
    const secondHalf = sessions.slice(Math.floor(sessions.length / 2));
    
    const firstHalfAvg = firstHalf.reduce((sum, s) => sum + s.summary.passRate, 0) / firstHalf.length;
    const secondHalfAvg = secondHalf.reduce((sum, s) => sum + s.summary.passRate, 0) / secondHalf.length;
    
    if (secondHalfAvg > firstHalfAvg + 5) {
      trends.push('📈 **Melhoria na taxa de sucesso** ao longo do tempo');
    } else if (firstHalfAvg > secondHalfAvg + 5) {
      trends.push('📉 **Degradação na taxa de sucesso** ao longo do tempo');
    } else {
      trends.push('📊 **Taxa de sucesso estável** ao longo do tempo');
    }
    
    // Tendência de performance
    const firstHalfPerf = firstHalf.reduce((sum, s) => sum + s.summary.averageResponseTime, 0) / firstHalf.length;
    const secondHalfPerf = secondHalf.reduce((sum, s) => sum + s.summary.averageResponseTime, 0) / secondHalf.length;
    
    if (secondHalfPerf < firstHalfPerf - 50) {
      trends.push('⚡ **Melhoria na performance** ao longo do tempo');
    } else if (secondHalfPerf > firstHalfPerf + 50) {
      trends.push('🐌 **Degradação na performance** ao longo do tempo');
    } else {
      trends.push('⚖️ **Performance estável** ao longo do tempo');
    }
    
    return trends.join('\n');
  }

  // Gerar análise de qualidade
  private generateQualityAnalysis(): string {
    if (this.automationSession.testSessions.length === 0) {
      return 'Nenhuma sessão de teste disponível para análise.';
    }
    
    const sessions = this.automationSession.testSessions;
    const analysis = [];
    
    // Análise de APIs
    const avgOrcamentos = sessions.reduce((sum, s) => sum + s.summary.apiScores.orcamentos, 0) / sessions.length;
    const avgEstoque = sessions.reduce((sum, s) => sum + s.summary.apiScores.estoque, 0) / sessions.length;
    const avgOrdem = sessions.reduce((sum, s) => sum + s.summary.apiScores.ordemServico, 0) / sessions.length;
    
    analysis.push(`**API de Orçamentos:** ${avgOrcamentos.toFixed(1)}/100 - ${this.getQualityLevel(avgOrcamentos)}`);
    analysis.push(`**API de Estoque:** ${avgEstoque.toFixed(1)}/100 - ${this.getQualityLevel(avgEstoque)}`);
    analysis.push(`**API de Ordem de Serviço:** ${avgOrdem.toFixed(1)}/100 - ${this.getQualityLevel(avgOrdem)}`);
    
    // API com melhor performance
    const bestApi = avgOrcamentos >= avgEstoque && avgOrcamentos >= avgOrdem ? 'Orçamentos' :
                   avgEstoque >= avgOrdem ? 'Estoque' : 'Ordem de Serviço';
    analysis.push(`\n🏆 **API com melhor performance:** ${bestApi}`);
    
    // Issues mais frequentes
    const allIssues = sessions.flatMap(s => s.summary.criticalIssues);
    const issueFrequency = allIssues.reduce((acc, issue) => {
      acc[issue] = (acc[issue] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);
    
    const topIssues = Object.entries(issueFrequency)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 3);
    
    if (topIssues.length > 0) {
      analysis.push('\n🔍 **Issues mais frequentes:**');
      topIssues.forEach(([issue, count]) => {
        analysis.push(`- ${issue} (${count}x)`);
      });
    }
    
    return analysis.join('\n');
  }

  // Obter nível de qualidade
  private getQualityLevel(score: number): string {
    if (score >= 90) return '🟢 Excelente';
    if (score >= 80) return '🟡 Bom';
    if (score >= 70) return '🟠 Regular';
    return '🔴 Precisa Melhorar';
  }

  // Gerar recomendações finais
  private generateFinalRecommendations(): string {
    const recommendations = [];
    const sessions = this.automationSession.testSessions;
    
    if (sessions.length === 0) {
      return 'Nenhuma recomendação disponível - sem dados de teste.';
    }
    
    const avgPassRate = sessions.reduce((sum, s) => sum + s.summary.passRate, 0) / sessions.length;
    const avgResponseTime = sessions.reduce((sum, s) => sum + s.summary.averageResponseTime, 0) / sessions.length;
    
    // Recomendações baseadas em taxa de sucesso
    if (avgPassRate < 80) {
      recommendations.push('🔧 **Crítico:** Investigar e corrigir falhas recorrentes - taxa de sucesso abaixo do aceitável');
    } else if (avgPassRate < 95) {
      recommendations.push('⚠️ **Importante:** Melhorar estabilidade geral do sistema');
    } else {
      recommendations.push('✅ **Parabéns:** Sistema demonstra alta estabilidade');
    }
    
    // Recomendações baseadas em performance
    if (avgResponseTime > 1000) {
      recommendations.push('⚡ **Crítico:** Otimização urgente de performance necessária');
    } else if (avgResponseTime > 500) {
      recommendations.push('🚀 **Recomendado:** Implementar otimizações de performance');
    } else {
      recommendations.push('🎯 **Excelente:** Performance dentro dos padrões esperados');
    }
    
    // Recomendações baseadas em estabilidade
    const stability = this.calculateSystemStability();
    if (stability < 70) {
      recommendations.push('🔄 **Urgente:** Sistema apresenta instabilidade - revisar arquitetura');
    } else if (stability < 90) {
      recommendations.push('🔧 **Sugerido:** Implementar melhorias de estabilidade');
    }
    
    // Recomendações para automação
    if (this.automationSession.failedRuns > this.automationSession.successfulRuns * 0.2) {
      recommendations.push('🤖 **Automação:** Ajustar configurações de retry e timeout');
    }
    
    return recommendations.join('\n');
  }

  // Atualizar dashboard
  private async updateDashboard(): Promise<void> {
    // Em implementação real, atualizar dashboard web
    console.log('📊 Dashboard atualizado');
  }

  // Enviar notificação
  private async sendNotification(type: 'success' | 'warning' | 'error' | 'info', message: string): Promise<void> {
    const timestamp = new Date().toLocaleString('pt-BR');
    console.log(`🔔 [${type.toUpperCase()}] ${timestamp}: ${message}`);
    
    // Em implementação real, enviar email/slack se configurado
    if (this.automationSession.config.emailNotifications) {
      // Enviar email
    }
    
    if (this.automationSession.config.slackNotifications) {
      // Enviar para Slack
    }
  }

  // Utilitário para delay
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Getter para sessão de automação
  public getAutomationSession(): AutomationSession {
    return this.automationSession;
  }

  // Método para obter status atual
  public getStatus(): string {
    return `Status: ${this.automationSession.status} | Execuções: ${this.automationSession.totalRuns} | Sucessos: ${this.automationSession.successfulRuns} | Falhas: ${this.automationSession.failedRuns}`;
  }
}

// Função para iniciar automação com configuração padrão
export async function startDefaultAutomation(): Promise<AutomatedTestRunner> {
  const defaultConfig: AutomationConfig = {
    runContinuous: true,
    intervalMinutes: 30,
    maxRuns: 10,
    emailNotifications: false,
    slackNotifications: false,
    generateDashboard: true,
    autoRetryFailed: true
  };
  
  const runner = new AutomatedTestRunner(defaultConfig);
  await runner.startAutomation();
  return runner;
}

// Função para automação única
export async function runSingleAutomatedTest(): Promise<AutomatedTestRunner> {
  const singleRunConfig: AutomationConfig = {
    runContinuous: false,
    intervalMinutes: 0,
    maxRuns: 1,
    emailNotifications: false,
    slackNotifications: false,
    generateDashboard: true,
    autoRetryFailed: false
  };
  
  const runner = new AutomatedTestRunner(singleRunConfig);
  await runner.startAutomation();
  return runner;
}

export default AutomatedTestRunner;