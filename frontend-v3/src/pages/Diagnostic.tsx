
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { 
  Cpu, 
  HardDrive, 
  MemoryStick, 
  Monitor, 
  Shield,
  Settings,
  AlertTriangle,
  CheckCircle,
  XCircle,
  PlayCircle,
  RefreshCw,
  Download,
  FileX,
  Lightbulb,
  FileText,
  DollarSign,
  Zap
} from 'lucide-react';

export default function Diagnostic() {
  const [currentStep, setCurrentStep] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [diagnosticComplete, setDiagnosticComplete] = useState(false);

  const steps = [
    { name: 'Preparação', description: 'Inicializando sistema de diagnóstico' },
    { name: 'Hardware', description: 'Verificando componentes físicos' },
    { name: 'Software', description: 'Analisando sistema operacional e drivers' },
    { name: 'Segurança', description: 'Verificando antivírus e arquivos corrompidos' },
    { name: 'Performance', description: 'Testando desempenho geral' },
    { name: 'Relatório', description: 'Gerando relatório final' }
  ];

  const diagnosticResults = [
    {
      component: 'CPU',
      icon: <Cpu className="h-5 w-5" />,
      status: 'healthy',
      score: 92,
      details: 'Intel Core i7-12700K funcionando normalmente',
      issues: []
    },
    {
      component: 'Memória RAM',
      icon: <MemoryStick className="h-5 w-5" />,
      status: 'warning',
      score: 78,
      details: '16GB DDR4 - 2 slots ocupados',
      issues: ['Velocidade abaixo do ideal']
    },
    {
      component: 'Armazenamento',
      icon: <HardDrive className="h-5 w-5" />,
      status: 'critical',
      score: 65,
      details: 'HD 1TB - Performance baixa',
      issues: ['Fragmentação alta', 'Setores defeituosos detectados']
    },
    {
      component: 'Placa de Vídeo',
      icon: <Monitor className="h-5 w-5" />,
      status: 'warning',
      score: 75,
      details: 'NVIDIA RTX 3080 - Driver desatualizado',
      issues: ['Driver versão antiga', 'Temperatura elevada']
    },
    {
      component: 'Antivírus',
      icon: <Shield className="h-5 w-5" />,
      status: 'critical',
      score: 45,
      details: 'Windows Defender desatualizado',
      issues: ['Definições de vírus desatualizadas', 'Proteção em tempo real desabilitada']
    },
    {
      component: 'Drivers',
      icon: <Settings className="h-5 w-5" />,
      status: 'warning',
      score: 70,
      details: '3 drivers desatualizados encontrados',
      issues: ['Driver de áudio desatualizado', 'Driver de rede desatualizado', 'Driver chipset antigo']
    },
    {
      component: 'Arquivos do Sistema',
      icon: <FileX className="h-5 w-5" />,
      status: 'healthy',
      score: 88,
      details: 'Sistema íntegro',
      issues: []
    }
  ];

  const problemsIdentified = [
    {
      problem: 'Performance lenta do sistema',
      rootCause: 'HD tradicional com fragmentação alta e setores defeituosos',
      solution: 'Executar desfragmentação completa e verificar integridade do disco. Considerar substituição por SSD.'
    },
    {
      problem: 'Vulnerabilidade de segurança',
      rootCause: 'Antivírus desatualizado e proteção em tempo real desabilitada',
      solution: 'Atualizar definições do Windows Defender e reativar proteção em tempo real. Executar scan completo.'
    },
    {
      problem: 'Instabilidade em jogos e aplicações',
      rootCause: 'Driver de vídeo desatualizado e temperatura elevada',
      solution: 'Atualizar driver da NVIDIA para versão mais recente. Verificar sistema de refrigeração.'
    }
  ];

  const suggestions = [
    {
      type: 'upgrade',
      title: 'Upgrade de Armazenamento',
      description: 'Substituir HD por SSD 1TB para melhoria significativa de performance',
      impact: 'Alto',
      priority: 'Alta'
    },
    {
      type: 'maintenance',
      title: 'Limpeza e Manutenção',
      description: 'Limpeza interna completa e troca da pasta térmica do processador',
      impact: 'Médio',
      priority: 'Média'
    },
    {
      type: 'memory',
      title: 'Upgrade de Memória',
      description: 'Adicionar mais 16GB RAM para total de 32GB (trabalhos pesados)',
      impact: 'Médio',
      priority: 'Baixa'
    }
  ];

  const runDiagnostic = () => {
    setIsRunning(true);
    setProgress(0);
    setCurrentStep(0);
    setDiagnosticComplete(false);

    const interval = setInterval(() => {
      setProgress(prev => {
        const newProgress = prev + 1.5;
        
        const stepProgress = Math.floor(newProgress / (100 / steps.length));
        setCurrentStep(stepProgress);

        if (newProgress >= 100) {
          clearInterval(interval);
          setIsRunning(false);
          setDiagnosticComplete(true);
          return 100;
        }
        
        return newProgress;
      });
    }, 100);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-tech" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-400" />;
      case 'critical':
        return <XCircle className="h-5 w-5 text-red-400" />;
      default:
        return <CheckCircle className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-tech';
      case 'warning':
        return 'text-yellow-400';
      case 'critical':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-tech';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getOverallScore = () => {
    const total = diagnosticResults.reduce((sum, result) => sum + result.score, 0);
    return Math.round(total / diagnosticResults.length);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Alta':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'Média':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'Baixa':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  return (
    <div className="min-h-screen bg-black">
      <main className="pt-20 pb-10 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Diagnóstico Completo do Sistema</h1>
            <p className="text-gray-400">Análise detalhada de hardware, software e segurança</p>
          </div>

          {!diagnosticComplete ? (
            <>
              {/* Diagnostic Controls */}
              <Card className="bg-dark/50 border-white/10 mb-8">
                <CardHeader className="text-center">
                  <CardTitle className="text-white flex items-center justify-center">
                    <Zap className="mr-2 h-6 w-6 text-electric" />
                    Centro de Diagnóstico
                  </CardTitle>
                  <CardDescription className="text-gray-400">
                    Inicie um diagnóstico completo do seu sistema
                  </CardDescription>
                </CardHeader>
                <CardContent className="text-center">
                  {!isRunning ? (
                    <Button 
                      onClick={runDiagnostic}
                      size="lg"
                      className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80 text-black font-semibold px-8 py-4"
                    >
                      <PlayCircle className="mr-2 h-5 w-5" />
                      Iniciar Diagnóstico
                    </Button>
                  ) : (
                    <div className="space-y-4">
                      <div className="text-center">
                        <RefreshCw className="h-8 w-8 text-electric animate-spin mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-white mb-2">
                          Diagnóstico em Andamento
                        </h3>
                        <p className="text-gray-400">
                          {steps[currentStep]?.description || 'Finalizando...'}
                        </p>
                      </div>
                      
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-gray-400">Progresso</span>
                          <span className="text-white">{progress}%</span>
                        </div>
                        <Progress value={progress} className="h-2" />
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Progress Steps */}
              {isRunning && (
                <Card className="bg-dark/50 border-white/10 mb-8">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-center">
                      {steps.map((step, index) => (
                        <div key={index} className="flex flex-col items-center space-y-2">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold ${
                            index <= currentStep 
                              ? 'bg-gradient-to-r from-electric to-tech text-black' 
                              : 'bg-dark border border-white/20 text-gray-400'
                          }`}>
                            {index + 1}
                          </div>
                          <span className={`text-xs text-center ${
                            index <= currentStep ? 'text-white' : 'text-gray-400'
                          }`}>
                            {step.name}
                          </span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </>
          ) : (
            <>
              {/* Results Header */}
              <Card className="bg-dark/50 border-white/10 mb-8">
                <CardContent className="p-8 text-center">
                  <CheckCircle className="h-16 w-16 text-tech mx-auto mb-4" />
                  <h2 className="text-2xl font-bold text-white mb-2">
                    Diagnóstico Concluído
                  </h2>
                  <p className="text-gray-400 mb-6">
                    Análise completa do sistema finalizada com sucesso
                  </p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="text-center">
                      <div className={`text-3xl font-bold mb-1 ${getScoreColor(getOverallScore())}`}>
                        {getOverallScore()}%
                      </div>
                      <div className="text-gray-400 text-sm">Score Geral</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-white mb-1">
                        {diagnosticResults.filter(r => r.status === 'healthy').length}
                      </div>
                      <div className="text-gray-400 text-sm">Componentes OK</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-red-400 mb-1">
                        {diagnosticResults.filter(r => r.status === 'critical').length}
                      </div>
                      <div className="text-gray-400 text-sm">Críticos</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-yellow-400 mb-1">
                        {problemsIdentified.length}
                      </div>
                      <div className="text-gray-400 text-sm">Problemas</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Detailed Results */}
              <div className="grid lg:grid-cols-2 gap-8 mb-8">
                <div className="space-y-6">
                  <h3 className="text-xl font-bold text-white">Resultados por Componente</h3>
                  
                  {diagnosticResults.map((result, index) => (
                    <Card key={index} className="bg-dark/50 border-white/10">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className="text-electric">
                              {result.icon}
                            </div>
                            <div>
                              <CardTitle className="text-white text-lg">{result.component}</CardTitle>
                              <CardDescription className="text-gray-400">
                                {result.details}
                              </CardDescription>
                            </div>
                          </div>
                          <div className="flex items-center space-x-3">
                            <div className={`text-2xl font-bold ${getScoreColor(result.score)}`}>
                              {result.score}%
                            </div>
                            {getStatusIcon(result.status)}
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <Progress value={result.score} className="h-2 mb-3" />
                        
                        {result.issues.length > 0 && (
                          <div className="space-y-2">
                            <h4 className="text-sm font-semibold text-white">Problemas:</h4>
                            <div className="space-y-1">
                              {result.issues.map((issue, idx) => (
                                <div key={idx} className="flex items-center space-x-2">
                                  <AlertTriangle className="h-4 w-4 text-yellow-400" />
                                  <span className="text-sm text-gray-300">{issue}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Problems and Solutions */}
                <div className="space-y-6">
                  <h3 className="text-xl font-bold text-white">Problemas Identificados</h3>
                  
                  {problemsIdentified.map((item, index) => (
                    <Card key={index} className="bg-dark/50 border-red-500/20">
                      <CardHeader>
                        <CardTitle className="text-white flex items-center">
                          <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
                          {item.problem}
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div>
                          <h4 className="text-sm font-semibold text-yellow-400 mb-1">Causa Raiz:</h4>
                          <p className="text-gray-300 text-sm">{item.rootCause}</p>
                        </div>
                        <div>
                          <h4 className="text-sm font-semibold text-tech mb-1">Como Resolver:</h4>
                          <p className="text-gray-300 text-sm">{item.solution}</p>
                        </div>
                      </CardContent>
                    </Card>
                  ))}

                  <Separator className="bg-white/10" />

                  <h3 className="text-xl font-bold text-white">Sugestões de Melhoria</h3>
                  
                  {suggestions.map((suggestion, index) => (
                    <Card key={index} className="bg-dark/50 border-white/10">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-white flex items-center">
                            <Lightbulb className="h-5 w-5 text-electric mr-2" />
                            {suggestion.title}
                          </CardTitle>
                          <Badge className={getPriorityColor(suggestion.priority)}>
                            {suggestion.priority}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p className="text-gray-300 text-sm mb-2">{suggestion.description}</p>
                        <div className="flex items-center justify-between text-xs">
                          <span className="text-gray-400">Impacto: {suggestion.impact}</span>
                          <Badge variant="outline" className="text-electric border-electric/30">
                            {suggestion.type}
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="grid md:grid-cols-4 gap-4">
                <Button 
                  onClick={() => setDiagnosticComplete(false)}
                  variant="outline" 
                  className="border-electric/50 text-electric hover:bg-electric/10"
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Novo Diagnóstico
                </Button>
                <Button className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80 text-black">
                  <FileText className="mr-2 h-4 w-4" />
                  Relatório Completo
                </Button>
                <Button className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white">
                  <DollarSign className="mr-2 h-4 w-4" />
                  Gerar Orçamento
                </Button>
                <Button variant="outline" className="border-white/20 text-white hover:bg-white/10">
                  <Download className="mr-2 h-4 w-4" />
                  Baixar PDF
                </Button>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}
