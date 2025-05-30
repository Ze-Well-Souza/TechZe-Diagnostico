
// Mock diagnostic service for demonstration
// In a real application, this would connect to your backend API

export interface DiagnosticResult {
  id: string;
  deviceName: string;
  customer: string;
  date: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  healthScore: number;
  issues: DiagnosticIssue[];
  recommendations: string[];
  components: ComponentStatus[];
}

export interface DiagnosticIssue {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  component: string;
  description: string;
  solution?: string;
}

export interface ComponentStatus {
  name: string;
  status: 'healthy' | 'warning' | 'critical';
  score: number;
  details: string;
}

class DiagnosticService {
  private diagnostics: DiagnosticResult[] = [];

  async startDiagnostic(deviceName: string, customerName: string): Promise<DiagnosticResult> {
    const diagnostic: DiagnosticResult = {
      id: this.generateId(),
      deviceName,
      customer: customerName,
      date: new Date().toISOString().split('T')[0],
      status: 'pending',
      healthScore: 0,
      issues: [],
      recommendations: [],
      components: []
    };

    this.diagnostics.push(diagnostic);
    
    // Simulate diagnostic process
    setTimeout(() => this.runDiagnostic(diagnostic.id), 1000);
    
    return diagnostic;
  }

  async runDiagnostic(diagnosticId: string): Promise<void> {
    const diagnostic = this.diagnostics.find(d => d.id === diagnosticId);
    if (!diagnostic) return;

    diagnostic.status = 'in_progress';

    // Simulate diagnostic phases
    await this.simulateHardwareCheck(diagnostic);
    await this.simulateSoftwareCheck(diagnostic);
    await this.simulatePerformanceCheck(diagnostic);

    diagnostic.status = 'completed';
    this.calculateHealthScore(diagnostic);
  }

  private async simulateHardwareCheck(diagnostic: DiagnosticResult): Promise<void> {
    await this.delay(2000);
    
    const components = [
      { name: 'CPU', chance: 0.1 },
      { name: 'RAM', chance: 0.15 },
      { name: 'Armazenamento', chance: 0.25 },
      { name: 'Placa Mãe', chance: 0.05 },
      { name: 'Fonte', chance: 0.1 }
    ];

    components.forEach(comp => {
      const hasIssue = Math.random() < comp.chance;
      const score = hasIssue ? 
        Math.floor(Math.random() * 50) + 30 : 
        Math.floor(Math.random() * 20) + 80;

      const status: ComponentStatus['status'] = 
        score >= 80 ? 'healthy' : 
        score >= 60 ? 'warning' : 'critical';

      diagnostic.components.push({
        name: comp.name,
        status,
        score,
        details: this.generateComponentDetails(comp.name, status)
      });

      if (hasIssue) {
        diagnostic.issues.push({
          id: this.generateId(),
          severity: score < 40 ? 'critical' : score < 60 ? 'high' : 'medium',
          component: comp.name,
          description: this.generateIssueDescription(comp.name),
          solution: this.generateSolution(comp.name)
        });
      }
    });
  }

  private async simulateSoftwareCheck(diagnostic: DiagnosticResult): Promise<void> {
    await this.delay(1500);
    
    // Add software-related issues randomly
    const softwareIssues = [
      'Sistema operacional desatualizado',
      'Drivers desatualizados',
      'Vírus ou malware detectado',
      'Registro do Windows corrompido',
      'Arquivos de sistema danificados'
    ];

    const randomIssues = softwareIssues.filter(() => Math.random() < 0.2);
    
    randomIssues.forEach(issue => {
      diagnostic.issues.push({
        id: this.generateId(),
        severity: 'medium',
        component: 'Software',
        description: issue,
        solution: this.generateSoftwareSolution(issue)
      });
    });
  }

  private async simulatePerformanceCheck(diagnostic: DiagnosticResult): Promise<void> {
    await this.delay(1000);
    
    // Add performance recommendations
    const recommendations = [
      'Limpar arquivos temporários',
      'Desfragmentar disco rígido',
      'Otimizar inicialização do sistema',
      'Atualizar drivers de vídeo',
      'Aumentar memória RAM'
    ];

    diagnostic.recommendations = recommendations
      .filter(() => Math.random() < 0.6)
      .slice(0, 3);
  }

  private calculateHealthScore(diagnostic: DiagnosticResult): void {
    if (diagnostic.components.length === 0) {
      diagnostic.healthScore = 75;
      return;
    }

    const avgScore = diagnostic.components.reduce((sum, comp) => sum + comp.score, 0) / diagnostic.components.length;
    const issuesPenalty = diagnostic.issues.length * 5;
    diagnostic.healthScore = Math.max(0, Math.min(100, Math.round(avgScore - issuesPenalty)));
  }

  getDiagnostics(): DiagnosticResult[] {
    return [...this.diagnostics];
  }

  getDiagnostic(id: string): DiagnosticResult | undefined {
    return this.diagnostics.find(d => d.id === id);
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private generateComponentDetails(component: string, status: ComponentStatus['status']): string {
    const details = {
      'CPU': {
        healthy: 'Processador funcionando dentro dos parâmetros normais',
        warning: 'Temperatura elevada detectada',
        critical: 'Processador superaquecendo ou com falhas'
      },
      'RAM': {
        healthy: 'Memória funcionando corretamente',
        warning: 'Alguns módulos com erros ocasionais',
        critical: 'Módulos de memória defeituosos detectados'
      },
      'Armazenamento': {
        healthy: 'Disco em bom estado',
        warning: 'Alguns setores com problemas',
        critical: 'Disco com muitos setores defeituosos'
      }
    };

    return details[component as keyof typeof details]?.[status] || 
           `Status ${status} para ${component}`;
  }

  private generateIssueDescription(component: string): string {
    const descriptions = {
      'CPU': 'Processador apresentando instabilidades',
      'RAM': 'Módulos de memória com erros',
      'Armazenamento': 'Disco rígido com setores defeituosos',
      'Placa Mãe': 'Capacitores danificados na placa mãe',
      'Fonte': 'Fonte de alimentação instável'
    };

    return descriptions[component as keyof typeof descriptions] || 
           `Problema detectado no componente ${component}`;
  }

  private generateSolution(component: string): string {
    const solutions = {
      'CPU': 'Verificar cooler e pasta térmica',
      'RAM': 'Substituir módulos defeituosos',
      'Armazenamento': 'Backup e substituição do disco',
      'Placa Mãe': 'Avaliação técnica especializada',
      'Fonte': 'Substituição da fonte de alimentação'
    };

    return solutions[component as keyof typeof solutions] || 
           `Consultar técnico especializado para ${component}`;
  }

  private generateSoftwareSolution(issue: string): string {
    const solutions = {
      'Sistema operacional desatualizado': 'Atualizar para a versão mais recente',
      'Drivers desatualizados': 'Baixar drivers atualizados do fabricante',
      'Vírus ou malware detectado': 'Executar antivírus completo',
      'Registro do Windows corrompido': 'Executar sfc /scannow no prompt',
      'Arquivos de sistema danificados': 'Reparar instalação do Windows'
    };

    return solutions[issue as keyof typeof solutions] || 
           'Consultar suporte técnico';
  }
}

export const diagnosticService = new DiagnosticService();
