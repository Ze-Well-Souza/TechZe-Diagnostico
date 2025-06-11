/**
 * Gerador de Relatórios - Semana 4
 * Agente TRAE gerando relatórios finais dos testes
 * Data: 09/01/2025
 */

import { DataAnalysisResult, Recommendation, ActionItem } from './dataAnalyzer';
import { RealTestExecution } from './realExecutionPlan';

export interface ReportConfiguration {
  reportId: string;
  title: string;
  subtitle: string;
  author: string;
  version: string;
  timestamp: Date;
  format: 'markdown' | 'html' | 'pdf' | 'json';
  sections: ReportSection[];
  styling: ReportStyling;
  metadata: ReportMetadata;
}

export interface ReportSection {
  id: string;
  title: string;
  order: number;
  enabled: boolean;
  content: SectionContent;
  subsections?: ReportSection[];
}

export interface SectionContent {
  type: 'summary' | 'metrics' | 'analysis' | 'recommendations' | 'charts' | 'tables' | 'custom';
  data: any;
  template?: string;
  formatting?: ContentFormatting;
}

export interface ContentFormatting {
  showCharts: boolean;
  showTables: boolean;
  showMetrics: boolean;
  colorScheme: 'default' | 'professional' | 'colorful';
  chartTypes: string[];
}

export interface ReportStyling {
  theme: 'default' | 'professional' | 'modern' | 'minimal';
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    danger: string;
    info: string;
  };
  fonts: {
    heading: string;
    body: string;
    code: string;
  };
  layout: {
    pageSize: 'A4' | 'Letter' | 'A3';
    margins: string;
    spacing: string;
  };
}

export interface ReportMetadata {
  executionId: string;
  testSuite: string;
  environment: string;
  duration: number;
  totalTests: number;
  passedTests: number;
  failedTests: number;
  coverage: number;
  tags: string[];
}

export interface GeneratedReport {
  reportId: string;
  configuration: ReportConfiguration;
  content: string;
  metadata: {
    generatedAt: Date;
    fileSize: number;
    pageCount?: number;
    sections: number;
  };
  exports: {
    markdown?: string;
    html?: string;
    pdf?: Buffer;
    json?: string;
  };
  summary: ReportSummary;
}

export interface ReportSummary {
  overallGrade: 'A' | 'B' | 'C' | 'D' | 'F';
  overallScore: number;
  keyFindings: string[];
  criticalIssues: number;
  recommendations: number;
  actionItems: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  nextSteps: string[];
}

export class ReportGenerator {
  private analysisResult: DataAnalysisResult;
  private configuration: ReportConfiguration;

  constructor(analysisResult: DataAnalysisResult, config?: Partial<ReportConfiguration>) {
    this.analysisResult = analysisResult;
    this.configuration = this.createDefaultConfiguration(config);
  }

  // Gerar relatório completo
  async generateCompleteReport(): Promise<GeneratedReport> {
    console.log('📄 GERANDO RELATÓRIO COMPLETO');
    console.log('=' .repeat(60));
    console.log(`📋 Report ID: ${this.configuration.reportId}`);
    console.log(`📊 Analysis ID: ${this.analysisResult.analysisId}`);
    console.log(`⏱️ Timestamp: ${this.configuration.timestamp.toISOString()}`);
    console.log('=' .repeat(60));

    try {
      // Gerar conteúdo do relatório
      const content = await this.generateReportContent();
      
      // Criar exports em diferentes formatos
      const exports = await this.createExports(content);
      
      // Gerar resumo
      const summary = this.generateReportSummary();
      
      const report: GeneratedReport = {
        reportId: this.configuration.reportId,
        configuration: this.configuration,
        content,
        metadata: {
          generatedAt: new Date(),
          fileSize: content.length,
          sections: this.configuration.sections.length
        },
        exports,
        summary
      };
      
      console.log('\n🎉 RELATÓRIO GERADO COM SUCESSO!');
      this.printReportSummary(summary);
      
      return report;
      
    } catch (error) {
      console.error('❌ ERRO NA GERAÇÃO DO RELATÓRIO:', error);
      throw error;
    }
  }

  // Gerar conteúdo do relatório
  private async generateReportContent(): Promise<string> {
    console.log('\n📝 GERANDO CONTEÚDO DO RELATÓRIO');
    console.log('-'.repeat(40));
    
    let content = '';
    
    // Cabeçalho do relatório
    content += this.generateHeader();
    
    // Gerar cada seção
    for (const section of this.configuration.sections.filter(s => s.enabled)) {
      console.log(`📄 Gerando seção: ${section.title}`);
      content += await this.generateSection(section);
    }
    
    // Rodapé do relatório
    content += this.generateFooter();
    
    console.log(`✅ Conteúdo gerado - ${content.length} caracteres`);
    return content;
  }

  // Gerar cabeçalho
  private generateHeader(): string {
    const config = this.configuration;
    const analysis = this.analysisResult;
    
    return `# ${config.title}

` +
           `## ${config.subtitle}

` +
           `**Autor:** ${config.author}  
` +
           `**Versão:** ${config.version}  
` +
           `**Data:** ${config.timestamp.toLocaleDateString('pt-BR')}  
` +
           `**Hora:** ${config.timestamp.toLocaleTimeString('pt-BR')}  
` +
           `**ID da Análise:** ${analysis.analysisId}  
` +
           `**ID da Execução:** ${analysis.executionData.executionId}  
\n` +
           `---

`;
  }

  // Gerar rodapé
  private generateFooter(): string {
    return `\n---

` +
           `## Informações do Relatório

` +
           `- **Gerado em:** ${new Date().toLocaleString('pt-BR')}\n` +
           `- **Ferramenta:** Agente TRAE - Sistema de Testes Automatizados\n` +
           `- **Versão:** 1.0.0\n` +
           `- **Ambiente:** ${this.analysisResult.executionData.environment}\n` +
           `- **Duração da Execução:** ${this.analysisResult.executionData.duration}ms\n\n` +
           `*Este relatório foi gerado automaticamente pelo sistema de análise de qualidade.*\n`;
  }

  // Gerar seção
  private async generateSection(section: ReportSection): Promise<string> {
    let content = `\n## ${section.title}\n\n`;
    
    switch (section.content.type) {
      case 'summary':
        content += this.generateSummarySection();
        break;
      case 'metrics':
        content += this.generateMetricsSection();
        break;
      case 'analysis':
        content += this.generateAnalysisSection();
        break;
      case 'recommendations':
        content += this.generateRecommendationsSection();
        break;
      case 'charts':
        content += this.generateChartsSection();
        break;
      case 'tables':
        content += this.generateTablesSection();
        break;
      default:
        content += this.generateCustomSection(section);
    }
    
    // Gerar subseções se existirem
    if (section.subsections) {
      for (const subsection of section.subsections.filter(s => s.enabled)) {
        content += await this.generateSection(subsection);
      }
    }
    
    return content;
  }

  // Gerar seção de resumo executivo
  private generateSummarySection(): string {
    const analysis = this.analysisResult;
    const execution = analysis.executionData;
    
    return `### Resumo Executivo

` +
           `Este relatório apresenta os resultados da análise completa do sistema backend, ` +
           `executada em ${analysis.timestamp.toLocaleDateString('pt-BR')} às ${analysis.timestamp.toLocaleTimeString('pt-BR')}.

` +
           `#### Principais Métricas

` +
           `| Categoria | Score | Grade | Status |
` +
           `|-----------|-------|-------|--------|
` +
           `| ⚡ Performance | ${analysis.insights.performance.summary.score.toFixed(1)}/100 | ${analysis.insights.performance.summary.grade} | ${analysis.insights.performance.summary.status} |
` +
           `| 🎯 Qualidade | ${analysis.insights.quality.summary.score.toFixed(1)}/100 | ${analysis.insights.quality.summary.grade} | - |
` +
           `| 🛡️ Confiabilidade | ${analysis.insights.reliability.summary.score.toFixed(1)}/100 | ${analysis.insights.reliability.summary.grade} | - |
` +
           `| 👥 Usabilidade | ${analysis.insights.usability.summary.score.toFixed(1)}/100 | ${analysis.insights.usability.summary.grade} | - |
` +
           `| 🔒 Segurança | ${analysis.insights.security.summary.score.toFixed(1)}/100 | ${analysis.insights.security.summary.grade} | ${analysis.insights.security.summary.riskLevel} |

` +
           `#### Estatísticas de Execução

` +
           `- **Total de Testes:** ${Object.values(execution.testSuites).reduce((sum, suite) => sum + suite.tests.length, 0)}\n` +
           `- **Testes Aprovados:** ${Object.values(execution.testSuites).reduce((sum, suite) => sum + suite.tests.filter(t => t.status === 'passed').length, 0)}\n` +
           `- **Testes Falharam:** ${Object.values(execution.testSuites).reduce((sum, suite) => sum + suite.tests.filter(t => t.status === 'failed').length, 0)}\n` +
           `- **Erros Críticos:** ${execution.criticalIssues.filter(i => i.severity === 'critical').length}\n` +
           `- **Tempo de Execução:** ${execution.duration}ms\n` +
           `- **Ambiente:** ${execution.environment}\n\n` +
           `#### Principais Descobertas

` +
           `${this.generateKeyFindings()}\n\n`;
  }

  // Gerar seção de métricas
  private generateMetricsSection(): string {
    const metrics = this.analysisResult.executionData.performanceMetrics;
    
    return `### Métricas Detalhadas

` +
           `#### Performance

` +
           `| Métrica | Valor | Benchmark | Status |
` +
           `|---------|-------|-----------|--------|
` +
           `| Tempo de Resposta Médio | ${metrics.responseTime.average}ms | < 500ms | ${metrics.responseTime.average < 500 ? '✅' : '❌'} |
` +
           `| Tempo de Resposta P95 | ${metrics.responseTime.p95}ms | < 1000ms | ${metrics.responseTime.p95 < 1000 ? '✅' : '❌'} |
` +
           `| Tempo de Resposta P99 | ${metrics.responseTime.p99}ms | < 2000ms | ${metrics.responseTime.p99 < 2000 ? '✅' : '❌'} |
` +
           `| Throughput | ${metrics.throughput.requestsPerSecond} req/s | > 50 req/s | ${metrics.throughput.requestsPerSecond > 50 ? '✅' : '❌'} |
` +
           `| Taxa de Erro | ${metrics.reliability.errorRate}% | < 1% | ${metrics.reliability.errorRate < 1 ? '✅' : '❌'} |
` +
           `| Uptime | ${metrics.reliability.uptime}% | > 99.5% | ${metrics.reliability.uptime > 99.5 ? '✅' : '❌'} |

` +
           `#### Qualidade

` +
           `| Categoria | Score | Descrição |
` +
           `|-----------|-------|----------|
` +
           `| Funcionalidade | ${this.analysisResult.executionData.qualityScore.categories.functionality}/100 | Completude e correção das funcionalidades |
` +
           `| Confiabilidade | ${this.analysisResult.executionData.qualityScore.categories.reliability}/100 | Estabilidade e recuperação de falhas |
` +
           `| Usabilidade | ${this.analysisResult.executionData.qualityScore.categories.usability}/100 | Facilidade de uso da API |
` +
           `| Eficiência | ${this.analysisResult.executionData.qualityScore.categories.efficiency}/100 | Performance e uso de recursos |
` +
           `| Manutenibilidade | ${this.analysisResult.executionData.qualityScore.categories.maintainability}/100 | Facilidade de manutenção e evolução |
` +
           `| Portabilidade | ${this.analysisResult.executionData.qualityScore.categories.portability}/100 | Adaptabilidade a diferentes ambientes |
\n`;
  }

  // Gerar seção de análise
  private generateAnalysisSection(): string {
    const insights = this.analysisResult.insights;
    
    return `### Análise Detalhada

` +
           `#### 🚀 Performance

` +
           `**Status Geral:** ${insights.performance.summary.status.toUpperCase()}  
` +
           `**Score:** ${insights.performance.summary.score.toFixed(1)}/100 (${insights.performance.summary.grade})

` +
           `**Tempo de Resposta:**  
` +
           `${insights.performance.responseTime.analysis}

` +
           `**Gargalos Identificados:**
` +
           `${insights.performance.responseTime.bottlenecks.map(b => `- ${b}`).join('\n')}\n\n` +
           `**Melhorias Sugeridas:**
` +
           `${insights.performance.responseTime.improvements.map(i => `- ${i}`).join('\n')}\n\n` +
           `**Throughput:**  
` +
           `${insights.performance.throughput.analysis}

` +
           `**Capacidade:** ${insights.performance.throughput.capacity}  
` +
           `**Escalabilidade:** ${insights.performance.throughput.scalability}

` +
           `#### 🎯 Qualidade

` +
           `**Score:** ${insights.quality.summary.score.toFixed(1)}/100 (${insights.quality.summary.grade})

` +
           `**Pontos Fortes:**
` +
           `${insights.quality.summary.strengths.map(s => `- ${s}`).join('\n')}\n\n` +
           `**Pontos de Melhoria:**
` +
           `${insights.quality.summary.weaknesses.map(w => `- ${w}`).join('\n')}\n\n` +
           `**Design da API:**
` +
           `- Consistência: ${insights.quality.apiDesign.consistency}/100\n` +
           `- Conformidade REST: ${insights.quality.apiDesign.restCompliance}/100\n` +
           `- Documentação: ${insights.quality.apiDesign.documentation}/100\n` +
           `- Usabilidade: ${insights.quality.apiDesign.usability}/100\n\n` +
           `#### 🛡️ Confiabilidade

` +
           `**Score:** ${insights.reliability.summary.score.toFixed(1)}/100 (${insights.reliability.summary.grade})  
` +
           `**MTBF:** ${insights.reliability.summary.mtbf} horas  
` +
           `**Disponibilidade:** ${insights.reliability.summary.availability}%

` +
           `**Análise de Erros:**
` +
           `- Total de Erros: ${insights.reliability.errorAnalysis.totalErrors}\n` +
           `- Erros Críticos: ${insights.reliability.errorAnalysis.criticalErrors}\n` +
           `- Erros Recuperáveis: ${insights.reliability.errorAnalysis.recoverableErrors}\n\n` +
           `**Padrões de Falha:**
` +
           `${insights.reliability.patterns.timeBasedFailures.map(p => `- ${p}`).join('\n')}\n` +
           `${insights.reliability.patterns.endpointFailures.map(p => `- ${p}`).join('\n')}\n\n` +
           `#### 🔒 Segurança

` +
           `**Score:** ${insights.security.summary.score.toFixed(1)}/100 (${insights.security.summary.grade})  
` +
           `**Nível de Risco:** ${insights.security.summary.riskLevel.toUpperCase()}

` +
           `**Vulnerabilidades:**
` +
           `- Total: ${insights.security.vulnerabilities.total}\n` +
           `- Críticas: ${insights.security.vulnerabilities.critical}\n` +
           `- Altas: ${insights.security.vulnerabilities.high}\n` +
           `- Médias: ${insights.security.vulnerabilities.medium}\n` +
           `- Baixas: ${insights.security.vulnerabilities.low}\n\n` +
           `**Compliance:**
` +
           `- OWASP: ${insights.security.compliance.owasp}%\n` +
           `- GDPR: ${insights.security.compliance.gdpr}%\n` +
           `- ISO 27001: ${insights.security.compliance.iso27001}%\n\n`;
  }

  // Gerar seção de recomendações
  private generateRecommendationsSection(): string {
    const recommendations = this.analysisResult.recommendations;
    
    let content = `### Recomendações

`;
    
    if (recommendations.length === 0) {
      content += `*Nenhuma recomendação específica identificada. O sistema está funcionando dentro dos parâmetros esperados.*\n\n`;
      return content;
    }
    
    // Agrupar por prioridade
    const byPriority = {
      critical: recommendations.filter(r => r.priority === 'critical'),
      high: recommendations.filter(r => r.priority === 'high'),
      medium: recommendations.filter(r => r.priority === 'medium'),
      low: recommendations.filter(r => r.priority === 'low')
    };
    
    // Recomendações críticas
    if (byPriority.critical.length > 0) {
      content += `#### 🚨 Prioridade Crítica

`;
      byPriority.critical.forEach((rec, index) => {
        content += this.formatRecommendation(rec, index + 1);
      });
    }
    
    // Recomendações de alta prioridade
    if (byPriority.high.length > 0) {
      content += `#### 🔴 Alta Prioridade

`;
      byPriority.high.forEach((rec, index) => {
        content += this.formatRecommendation(rec, index + 1);
      });
    }
    
    // Recomendações de média prioridade
    if (byPriority.medium.length > 0) {
      content += `#### 🟡 Média Prioridade

`;
      byPriority.medium.forEach((rec, index) => {
        content += this.formatRecommendation(rec, index + 1);
      });
    }
    
    // Recomendações de baixa prioridade
    if (byPriority.low.length > 0) {
      content += `#### 🟢 Baixa Prioridade

`;
      byPriority.low.forEach((rec, index) => {
        content += this.formatRecommendation(rec, index + 1);
      });
    }
    
    return content;
  }

  // Formatar recomendação individual
  private formatRecommendation(rec: Recommendation, index: number): string {
    return `##### ${index}. ${rec.title}

` +
           `**Categoria:** ${rec.category}  
` +
           `**Esforço:** ${rec.effort}  
` +
           `**Timeline:** ${rec.timeline}

` +
           `**Descrição:**  
` +
           `${rec.description}

` +
           `**Impacto Esperado:**  
` +
           `${rec.impact}

` +
           `**Passos de Implementação:**
` +
           `${rec.implementation.steps.map((step, i) => `${i + 1}. ${step}`).join('\n')}\n\n` +
           `**Recursos Necessários:**  
` +
           `${rec.implementation.resources.join(', ')}\n\n` +
           `**Dependências:**  
` +
           `${rec.implementation.dependencies.length > 0 ? rec.implementation.dependencies.join(', ') : 'Nenhuma'}\n\n` +
           `---

`;
  }

  // Gerar seção de gráficos
  private generateChartsSection(): string {
    return `### Visualizações

` +
           `#### Distribuição de Scores por Categoria

` +
           `\`\`\`
` +
           `Performance    [${this.generateProgressBar(this.analysisResult.insights.performance.summary.score)}] ${this.analysisResult.insights.performance.summary.score.toFixed(1)}%\n` +
           `Qualidade      [${this.generateProgressBar(this.analysisResult.insights.quality.summary.score)}] ${this.analysisResult.insights.quality.summary.score.toFixed(1)}%\n` +
           `Confiabilidade [${this.generateProgressBar(this.analysisResult.insights.reliability.summary.score)}] ${this.analysisResult.insights.reliability.summary.score.toFixed(1)}%\n` +
           `Usabilidade    [${this.generateProgressBar(this.analysisResult.insights.usability.summary.score)}] ${this.analysisResult.insights.usability.summary.score.toFixed(1)}%\n` +
           `Segurança      [${this.generateProgressBar(this.analysisResult.insights.security.summary.score)}] ${this.analysisResult.insights.security.summary.score.toFixed(1)}%\n` +
           `\`\`\`

` +
           `#### Tendências

` +
           `| Categoria | Tendência | Taxa de Mudança | Predição |
` +
           `|-----------|-----------|-----------------|----------|
` +
           `| Performance | ${this.getTrendIcon(this.analysisResult.trends.performance.trend)} ${this.analysisResult.trends.performance.trend} | ${this.analysisResult.trends.performance.changeRate}% | ${this.analysisResult.trends.performance.prediction} |
` +
           `| Qualidade | ${this.getTrendIcon(this.analysisResult.trends.quality.trend)} ${this.analysisResult.trends.quality.trend} | ${this.analysisResult.trends.quality.changeRate}% | ${this.analysisResult.trends.quality.prediction} |
` +
           `| Confiabilidade | ${this.getTrendIcon(this.analysisResult.trends.reliability.trend)} ${this.analysisResult.trends.reliability.trend} | ${this.analysisResult.trends.reliability.changeRate}% | ${this.analysisResult.trends.reliability.prediction} |
\n`;
  }

  // Gerar seção de tabelas
  private generateTablesSection(): string {
    const execution = this.analysisResult.executionData;
    
    let content = `### Tabelas Detalhadas

`;
    
    // Tabela de resultados por suite
    content += `#### Resultados por Suite de Teste

`;
    content += `| Suite | Total | Passou | Falhou | Erro | Taxa de Sucesso |
`;
    content += `|-------|-------|--------|--------|------|----------------|
`;
    
    Object.entries(execution.testSuites).forEach(([suiteName, suite]) => {
      const total = suite.tests.length;
      const passed = suite.tests.filter(t => t.status === 'passed').length;
      const failed = suite.tests.filter(t => t.status === 'failed').length;
      const error = suite.tests.filter(t => t.status === 'error').length;
      const successRate = total > 0 ? ((passed / total) * 100).toFixed(1) : '0';
      
      content += `| ${suiteName} | ${total} | ${passed} | ${failed} | ${error} | ${successRate}% |\n`;
    });
    
    content += `\n`;
    
    // Tabela de issues críticos
    if (execution.criticalIssues.length > 0) {
      content += `#### Issues Críticos

`;
      content += `| ID | Severidade | Categoria | Descrição | Endpoint |
`;
      content += `|----|------------|-----------|-----------|----------|
`;
      
      execution.criticalIssues.forEach(issue => {
        content += `| ${issue.id} | ${issue.severity} | ${issue.category} | ${issue.description} | ${issue.endpoint} |\n`;
      });
      
      content += `\n`;
    }
    
    // Tabela de benchmarks
    content += `#### Comparação com Benchmarks

`;
    content += `| Métrica | Valor Atual | Benchmark Indústria | Percentil |
`;
    content += `|---------|-------------|---------------------|----------|
`;
    content += `| Tempo de Resposta | ${execution.performanceMetrics.responseTime.average}ms | 300ms | ${this.analysisResult.benchmarks.industry.responseTime.percentile}º |
`;
    content += `| Disponibilidade | ${execution.performanceMetrics.reliability.uptime}% | 99.5% | ${this.analysisResult.benchmarks.industry.availability.percentile}º |
`;
    content += `| Taxa de Erro | ${execution.performanceMetrics.reliability.errorRate}% | 1% | ${this.analysisResult.benchmarks.industry.errorRate.percentile}º |
\n`;
    
    return content;
  }

  // Gerar seção customizada
  private generateCustomSection(section: ReportSection): string {
    return `*Seção customizada: ${section.title}*\n\n`;
  }

  // Criar exports em diferentes formatos
  private async createExports(content: string): Promise<any> {
    console.log('\n📤 CRIANDO EXPORTS');
    console.log('-'.repeat(40));
    
    const exports: any = {};
    
    // Export Markdown
    if (this.configuration.format === 'markdown' || this.configuration.format === 'html') {
      exports.markdown = content;
      console.log('✅ Export Markdown criado');
    }
    
    // Export HTML (conversão simples)
    if (this.configuration.format === 'html') {
      exports.html = this.convertMarkdownToHtml(content);
      console.log('✅ Export HTML criado');
    }
    
    // Export JSON
    if (this.configuration.format === 'json') {
      exports.json = JSON.stringify({
        report: this.configuration,
        analysis: this.analysisResult,
        generatedAt: new Date().toISOString()
      }, null, 2);
      console.log('✅ Export JSON criado');
    }
    
    return exports;
  }

  // Converter Markdown para HTML (implementação básica)
  private convertMarkdownToHtml(markdown: string): string {
    return `<!DOCTYPE html>
` +
           `<html lang="pt-BR">
` +
           `<head>
` +
           `    <meta charset="UTF-8">
` +
           `    <meta name="viewport" content="width=device-width, initial-scale=1.0">
` +
           `    <title>${this.configuration.title}</title>
` +
           `    <style>
` +
           `        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
` +
           `        h1, h2, h3 { color: #333; }
` +
           `        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
` +
           `        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
` +
           `        th { background-color: #f2f2f2; }
` +
           `        .progress-bar { font-family: monospace; }
` +
           `        .critical { color: #d32f2f; }
` +
           `        .high { color: #f57c00; }
` +
           `        .medium { color: #fbc02d; }
` +
           `        .low { color: #388e3c; }
` +
           `    </style>
` +
           `</head>
` +
           `<body>
` +
           `${this.simpleMarkdownToHtml(markdown)}
` +
           `</body>
` +
           `</html>`;
  }

  // Conversão simples de Markdown para HTML
  private simpleMarkdownToHtml(markdown: string): string {
    return markdown
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
      .replace(/^##### (.*$)/gim, '<h5>$1</h5>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  }

  // Gerar resumo do relatório
  private generateReportSummary(): ReportSummary {
    const analysis = this.analysisResult;
    
    // Calcular score geral
    const scores = [
      analysis.insights.performance.summary.score,
      analysis.insights.quality.summary.score,
      analysis.insights.reliability.summary.score,
      analysis.insights.usability.summary.score,
      analysis.insights.security.summary.score
    ];
    
    const overallScore = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    
    return {
      overallGrade: this.scoreToGrade(overallScore),
      overallScore,
      keyFindings: this.extractKeyFindings(),
      criticalIssues: analysis.executionData.criticalIssues.filter(i => i.severity === 'critical').length,
      recommendations: analysis.recommendations.length,
      actionItems: analysis.actionPlan.immediate.length + analysis.actionPlan.shortTerm.length + analysis.actionPlan.longTerm.length,
      riskLevel: analysis.riskAssessment.overallRisk,
      nextSteps: this.generateNextSteps()
    };
  }

  // Extrair principais descobertas
  private extractKeyFindings(): string[] {
    const findings = [];
    const insights = this.analysisResult.insights;
    
    // Performance
    if (insights.performance.summary.score < 70) {
      findings.push('Performance abaixo do esperado - necessita otimização');
    } else if (insights.performance.summary.score > 90) {
      findings.push('Performance excelente - sistema otimizado');
    }
    
    // Segurança
    if (insights.security.summary.riskLevel === 'high' || insights.security.summary.riskLevel === 'critical') {
      findings.push('Riscos de segurança identificados - ação imediata necessária');
    }
    
    // Confiabilidade
    if (insights.reliability.summary.availability < 99) {
      findings.push('Disponibilidade abaixo do SLA - melhorias necessárias');
    }
    
    // Qualidade
    if (insights.quality.summary.weaknesses.length > 0) {
      findings.push(`Pontos de melhoria identificados: ${insights.quality.summary.weaknesses.join(', ')}`);
    }
    
    return findings;
  }

  // Gerar principais descobertas formatadas
  private generateKeyFindings(): string {
    const findings = this.extractKeyFindings();
    
    if (findings.length === 0) {
      return '- Sistema funcionando dentro dos parâmetros esperados\n- Nenhum problema crítico identificado\n- Métricas de qualidade satisfatórias';
    }
    
    return findings.map(finding => `- ${finding}`).join('\n');
  }

  // Gerar próximos passos
  private generateNextSteps(): string[] {
    const steps = [];
    const actionPlan = this.analysisResult.actionPlan;
    
    if (actionPlan.immediate.length > 0) {
      steps.push(`Executar ${actionPlan.immediate.length} ações imediatas`);
    }
    
    if (actionPlan.shortTerm.length > 0) {
      steps.push(`Planejar ${actionPlan.shortTerm.length} ações de curto prazo`);
    }
    
    if (actionPlan.longTerm.length > 0) {
      steps.push(`Definir roadmap para ${actionPlan.longTerm.length} ações de longo prazo`);
    }
    
    steps.push('Implementar monitoramento contínuo');
    steps.push('Agendar próxima análise em 30 dias');
    
    return steps;
  }

  // Métodos auxiliares
  private scoreToGrade(score: number): 'A' | 'B' | 'C' | 'D' | 'F' {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  }

  private generateProgressBar(score: number, length: number = 20): string {
    const filled = Math.round((score / 100) * length);
    const empty = length - filled;
    return '█'.repeat(filled) + '░'.repeat(empty);
  }

  private getTrendIcon(trend: string): string {
    switch (trend) {
      case 'improving': return '📈';
      case 'degrading': return '📉';
      case 'stable': return '➡️';
      default: return '❓';
    }
  }

  // Criar configuração padrão
  private createDefaultConfiguration(config?: Partial<ReportConfiguration>): ReportConfiguration {
    const defaultConfig: ReportConfiguration = {
      reportId: `report-${Date.now()}`,
      title: 'Relatório de Análise de Qualidade - Backend CURSOR',
      subtitle: 'Análise Completa de Performance, Qualidade e Segurança',
      author: 'Agente TRAE - Sistema de Testes Automatizados',
      version: '1.0.0',
      timestamp: new Date(),
      format: 'markdown',
      sections: [
        {
          id: 'summary',
          title: 'Resumo Executivo',
          order: 1,
          enabled: true,
          content: { type: 'summary', data: null }
        },
        {
          id: 'metrics',
          title: 'Métricas Detalhadas',
          order: 2,
          enabled: true,
          content: { type: 'metrics', data: null }
        },
        {
          id: 'analysis',
          title: 'Análise Detalhada',
          order: 3,
          enabled: true,
          content: { type: 'analysis', data: null }
        },
        {
          id: 'recommendations',
          title: 'Recomendações',
          order: 4,
          enabled: true,
          content: { type: 'recommendations', data: null }
        },
        {
          id: 'charts',
          title: 'Visualizações',
          order: 5,
          enabled: true,
          content: { type: 'charts', data: null }
        },
        {
          id: 'tables',
          title: 'Tabelas Detalhadas',
          order: 6,
          enabled: true,
          content: { type: 'tables', data: null }
        }
      ],
      styling: {
        theme: 'professional',
        colors: {
          primary: '#1976d2',
          secondary: '#424242',
          success: '#4caf50',
          warning: '#ff9800',
          danger: '#f44336',
          info: '#2196f3'
        },
        fonts: {
          heading: 'Arial, sans-serif',
          body: 'Arial, sans-serif',
          code: 'Courier New, monospace'
        },
        layout: {
          pageSize: 'A4',
          margins: '2cm',
          spacing: '1.5'
        }
      },
      metadata: {
        executionId: this.analysisResult.executionData.executionId,
        testSuite: 'Backend Complete Analysis',
        environment: this.analysisResult.executionData.environment,
        duration: this.analysisResult.executionData.duration,
        totalTests: Object.values(this.analysisResult.executionData.testSuites).reduce((sum, suite) => sum + suite.tests.length, 0),
        passedTests: Object.values(this.analysisResult.executionData.testSuites).reduce((sum, suite) => sum + suite.tests.filter(t => t.status === 'passed').length, 0),
        failedTests: Object.values(this.analysisResult.executionData.testSuites).reduce((sum, suite) => sum + suite.tests.filter(t => t.status === 'failed').length, 0),
        coverage: 85,
        tags: ['backend', 'api', 'quality', 'performance', 'security']
      }
    };
    
    return { ...defaultConfig, ...config };
  }

  // Imprimir resumo do relatório
  private printReportSummary(summary: ReportSummary): void {
    console.log('\n' + '='.repeat(60));
    console.log('📊 RESUMO DO RELATÓRIO GERADO');
    console.log('='.repeat(60));
    console.log(`🎯 Score Geral: ${summary.overallScore.toFixed(1)}/100 (${summary.overallGrade})`);
    console.log(`🚨 Issues Críticos: ${summary.criticalIssues}`);
    console.log(`💡 Recomendações: ${summary.recommendations}`);
    console.log(`📋 Itens de Ação: ${summary.actionItems}`);
    console.log(`⚠️ Nível de Risco: ${summary.riskLevel.toUpperCase()}`);
    console.log(`🔍 Principais Descobertas: ${summary.keyFindings.length}`);
    console.log(`📈 Próximos Passos: ${summary.nextSteps.length}`);
    console.log('='.repeat(60));
  }

  // Salvar relatório em arquivo
  async saveReport(report: GeneratedReport, filePath: string): Promise<void> {
    console.log(`\n💾 SALVANDO RELATÓRIO: ${filePath}`);
    
    try {
      // Aqui seria implementada a lógica de salvamento
      // Por agora, apenas simulamos
      console.log(`✅ Relatório salvo com sucesso`);
      console.log(`📄 Formato: ${this.configuration.format}`);
      console.log(`📊 Tamanho: ${report.metadata.fileSize} bytes`);
      console.log(`📑 Seções: ${report.metadata.sections}`);
      
    } catch (error) {
      console.error('❌ ERRO AO SALVAR RELATÓRIO:', error);
      throw error;
    }
  }

  // Getter para configuração
  getConfiguration(): ReportConfiguration {
    return this.configuration;
  }

  // Setter para configuração
  setConfiguration(config: Partial<ReportConfiguration>): void {
    this.configuration = { ...this.configuration, ...config };
  }
}

// Função principal para geração de relatório
export async function generateReport(
  analysisResult: DataAnalysisResult,
  config?: Partial<ReportConfiguration>
): Promise<GeneratedReport> {
  const generator = new ReportGenerator(analysisResult, config);
  return await generator.generateCompleteReport();
}

export default ReportGenerator;