import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { realDiagnosticService } from '@/services/realDiagnosticService';
import { diagnosticApiService } from '@/services/diagnosticApiService';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Loader2, 
  Cpu, 
  HardDrive, 
  Wifi, 
  Battery, 
  Monitor, 
  Zap,
  CheckCircle2,
  AlertTriangle,
  User,
  Printer,
  FileText,
  ArrowLeft,
  Play,
  RotateCcw
} from 'lucide-react';

interface DiagnosticStep {
  id: string;
  name: string;
  description: string;
  icon: React.ReactNode;
  status: 'pending' | 'running' | 'completed' | 'error';
  result?: any;
  duration?: number;
}

export default function Diagnostic() {
  const { user, company } = useAuth();
  const navigate = useNavigate();
  const [deviceName, setDeviceName] = useState('');
  const [clientName, setClientName] = useState('');
  const [clientPhone, setClientPhone] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [diagnosticResult, setDiagnosticResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [startTime, setStartTime] = useState<Date | null>(null);

  const [steps, setSteps] = useState<DiagnosticStep[]>([
    {
      id: 'system',
      name: 'Sistema Operacional',
      description: 'Verificando informações básicas do Windows/macOS',
      icon: <Monitor className="h-5 w-5" />,
      status: 'pending'
    },
    {
      id: 'cpu',
      name: 'Processador',
      description: 'Testando performance e temperatura da CPU',
      icon: <Cpu className="h-5 w-5" />,
      status: 'pending'
    },
    {
      id: 'memory',
      name: 'Memória RAM',
      description: 'Analisando uso e velocidade da memória',
      icon: <HardDrive className="h-5 w-5" />,
      status: 'pending'
    },
    {
      id: 'network',
      name: 'Internet',
      description: 'Testando velocidade e estabilidade da conexão',
      icon: <Wifi className="h-5 w-5" />,
      status: 'pending'
    },
    {
      id: 'battery',
      name: 'Bateria (Notebooks)',
      description: 'Verificando saúde e capacidade da bateria',
      icon: <Battery className="h-5 w-5" />,
      status: 'pending'
    }
  ]);

  const updateStepStatus = (stepId: string, status: DiagnosticStep['status'], result?: any) => {
    setSteps(prev => prev.map(step => 
      step.id === stepId 
        ? { ...step, status, result, duration: status === 'completed' ? 2 : undefined }
        : step
    ));
  };

  const runDiagnostic = async () => {
    if (!deviceName.trim()) {
      setError('Por favor, informe o nome/modelo do dispositivo');
      return;
    }
    if (!clientName.trim()) {
      setError('Por favor, informe o nome do cliente');
      return;
    }

    setIsRunning(true);
    setError('');
    setCurrentStep(0);
    setStartTime(new Date());

    try {
      // Reset all steps
      setSteps(prev => prev.map(step => ({ ...step, status: 'pending' as const })));

      // Step 1: System Info
      setCurrentStep(1);
      updateStepStatus('system', 'running');
      const systemInfo = await realDiagnosticService.getSystemInfo();
      updateStepStatus('system', 'completed', systemInfo);
      await delay(1500);

      // Step 2: CPU
      setCurrentStep(2);
      updateStepStatus('cpu', 'running');
      const hardwareMetrics = await realDiagnosticService.getHardwareMetrics();
      updateStepStatus('cpu', 'completed', hardwareMetrics.cpu);
      await delay(1500);

      // Step 3: Memory
      setCurrentStep(3);
      updateStepStatus('memory', 'running');
      updateStepStatus('memory', 'completed', hardwareMetrics.memory);
      await delay(1500);

      // Step 4: Network
      setCurrentStep(4);
      updateStepStatus('network', 'running');
      updateStepStatus('network', 'completed', hardwareMetrics.network);
      await delay(1500);

      // Step 5: Battery
      setCurrentStep(5);
      updateStepStatus('battery', 'running');
      updateStepStatus('battery', 'completed', hardwareMetrics.battery);
      await delay(1500);

      // Salvar no Supabase
      const fullDiagnostic = await realDiagnosticService.runFullDiagnostic(deviceName);
      
      // Criar device se não existir
      const device = await diagnosticApiService.createDevice({
        name: deviceName,
        type: 'Desktop/Laptop',
        os: systemInfo.os,
        os_version: systemInfo.os_version,
        processor: systemInfo.processor,
        ram: systemInfo.ram,
        storage: systemInfo.storage || 'Unknown'
      });

      // Salvar diagnóstico
      const savedDiagnostic = await diagnosticApiService.saveDiagnostic({
        device_id: device.id,
        status: 'completed',
        cpu_status: hardwareMetrics.cpu.usage_percentage < 80 ? 'normal' : 'warning',
        cpu_metrics: hardwareMetrics.cpu,
        memory_status: hardwareMetrics.memory.usage_percentage < 85 ? 'normal' : 'warning',
        memory_metrics: hardwareMetrics.memory,
        disk_status: hardwareMetrics.disk.usage_percentage < 90 ? 'normal' : 'warning',
        disk_metrics: hardwareMetrics.disk,
        network_status: hardwareMetrics.network.connection_type !== 'Unknown' ? 'normal' : 'warning',
        network_metrics: hardwareMetrics.network,
        health_score: calculateHealthScore(hardwareMetrics),
        raw_data: fullDiagnostic,
        client_name: clientName,
        client_phone: clientPhone
      });

      setDiagnosticResult(savedDiagnostic);
      setCurrentStep(0);

    } catch (err) {
      console.error('Erro durante diagnóstico:', err);
      setError('Erro durante o diagnóstico. Verifique a conexão e tente novamente.');
      updateStepStatus(steps[currentStep - 1]?.id, 'error');
    } finally {
      setIsRunning(false);
    }
  };

  const calculateHealthScore = (metrics: any): number => {
    let score = 100;
    
    if (metrics.cpu.usage_percentage > 80) score -= 20;
    if (metrics.memory.usage_percentage > 85) score -= 25;
    if (metrics.disk.usage_percentage > 90) score -= 30;
    if (metrics.network.connection_type === 'Unknown') score -= 15;
    
    return Math.max(0, score);
  };

  const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  const getStatusIcon = (status: DiagnosticStep['status']) => {
    switch (status) {
      case 'running':
        return <Loader2 className="h-4 w-4 animate-spin text-electric" />;
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-400" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-400" />;
      default:
        return null;
    }
  };

  const resetDiagnostic = () => {
    setDiagnosticResult(null);
    setDeviceName('');
    setClientName('');
    setClientPhone('');
    setError('');
    setCurrentStep(0);
    setSteps(prev => prev.map(step => ({ ...step, status: 'pending' as const })));
  };

  const printReport = () => {
    window.print();
  };

  // Tela de resultado do diagnóstico
  if (diagnosticResult) {
    const healthScore = diagnosticResult.health_score || 0;
    const getHealthStatus = (score: number) => {
      if (score >= 80) return { text: 'EXCELENTE', color: 'text-green-400', bgColor: 'bg-green-400/20' };
      if (score >= 60) return { text: 'BOM', color: 'text-yellow-400', bgColor: 'bg-yellow-400/20' };
      if (score >= 40) return { text: 'REGULAR', color: 'text-orange-400', bgColor: 'bg-orange-400/20' };
      return { text: 'CRÍTICO', color: 'text-red-400', bgColor: 'bg-red-400/20' };
    };

    const status = getHealthStatus(healthScore);

    return (
      <div className="min-h-screen bg-gradient-to-br from-tech-darker to-tech-dark print:bg-white">
        <div className="container-responsive py-8 print:py-4">
          {/* Header com ações */}
          <div className="flex justify-between items-center mb-6 print:hidden">
            <Button
              variant="outline"
              onClick={() => navigate('/dashboard')}
              className="electric-border"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Voltar ao Dashboard
            </Button>
            
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={resetDiagnostic}
                className="electric-border"
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Novo Diagnóstico
              </Button>
              <Button
                onClick={printReport}
                className="btn-electric"
              >
                <Printer className="h-4 w-4 mr-2" />
                Imprimir Relatório
              </Button>
            </div>
          </div>

          {/* Cabeçalho do relatório */}
          <Card className="card-electric mb-6">
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-2xl tech-font mb-2">
                    🔧 RELATÓRIO DE DIAGNÓSTICO
                  </CardTitle>
                  <CardDescription className="text-base">
                    <strong>Cliente:</strong> {clientName} {clientPhone && `- ${clientPhone}`}<br/>
                    <strong>Equipamento:</strong> {deviceName}<br/>
                    <strong>Data:</strong> {new Date().toLocaleDateString('pt-BR')} às {new Date().toLocaleTimeString('pt-BR')}<br/>
                    <strong>Técnico:</strong> {user?.email} ({company?.name})
                  </CardDescription>
                </div>
                <div className={`px-4 py-2 rounded-lg ${status.bgColor} border`}>
                  <div className="text-center">
                    <div className={`text-3xl font-bold ${status.color}`}>{healthScore}%</div>
                    <div className={`text-sm font-medium ${status.color}`}>{status.text}</div>
                  </div>
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Resumo executivo */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
            <Card className="card-electric">
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <Cpu className="h-5 w-5 mr-2 text-electric" />
                  Processador
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Uso atual:</span>
                    <span className={diagnosticResult.cpu_metrics?.usage_percentage > 80 ? 'text-red-400' : 'text-green-400'}>
                      {diagnosticResult.cpu_metrics?.usage_percentage || 0}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <span className={diagnosticResult.cpu_status === 'normal' ? 'text-green-400' : 'text-yellow-400'}>
                      {diagnosticResult.cpu_status === 'normal' ? 'Normal' : 'Atenção'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="card-electric">
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <HardDrive className="h-5 w-5 mr-2 text-electric" />
                  Memória RAM
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Uso atual:</span>
                    <span className={diagnosticResult.memory_metrics?.usage_percentage > 85 ? 'text-red-400' : 'text-green-400'}>
                      {diagnosticResult.memory_metrics?.usage_percentage || 0}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <span className={diagnosticResult.memory_status === 'normal' ? 'text-green-400' : 'text-yellow-400'}>
                      {diagnosticResult.memory_status === 'normal' ? 'Normal' : 'Atenção'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="card-electric">
              <CardHeader>
                <CardTitle className="flex items-center text-lg">
                  <Wifi className="h-5 w-5 mr-2 text-electric" />
                  Conectividade
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Conexão:</span>
                    <span className="text-green-400">
                      {diagnosticResult.network_metrics?.connection_type || 'Ethernet'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <span className={diagnosticResult.network_status === 'normal' ? 'text-green-400' : 'text-yellow-400'}>
                      {diagnosticResult.network_status === 'normal' ? 'Normal' : 'Verificar'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recomendações */}
          <Card className="card-electric">
            <CardHeader>
              <CardTitle className="flex items-center">
                <FileText className="h-5 w-5 mr-2 text-electric" />
                Recomendações do Técnico
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {healthScore < 60 && (
                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      <strong>⚠️ Atenção necessária:</strong> O equipamento apresenta problemas que podem afetar o desempenho.
                    </AlertDescription>
                  </Alert>
                )}
                
                <div className="bg-muted/10 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2">📋 Checklist de Manutenção:</h4>
                  <ul className="space-y-1 text-sm">
                    <li>✅ Limpeza interna e externa realizada</li>
                    <li>✅ Teste de hardware completo executado</li>
                    <li>✅ Verificação de drivers e atualizações</li>
                    <li>✅ Teste de estresse dos componentes</li>
                  </ul>
                </div>

                {healthScore >= 80 ? (
                  <div className="bg-green-400/10 p-4 rounded-lg border border-green-400/20">
                    <p className="text-green-400 font-medium">✅ Equipamento em excelente estado!</p>
                    <p className="text-sm text-muted-foreground">Mantenha as atualizações em dia e realize limpeza periódica.</p>
                  </div>
                ) : healthScore >= 60 ? (
                  <div className="bg-yellow-400/10 p-4 rounded-lg border border-yellow-400/20">
                    <p className="text-yellow-400 font-medium">⚠️ Equipamento precisa de atenção</p>
                    <p className="text-sm text-muted-foreground">Recomendamos limpeza e otimização do sistema.</p>
                  </div>
                ) : (
                  <div className="bg-red-400/10 p-4 rounded-lg border border-red-400/20">
                    <p className="text-red-400 font-medium">🚨 Equipamento precisa de reparo</p>
                    <p className="text-sm text-muted-foreground">Problemas identificados que requerem intervenção técnica.</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Rodapé do relatório */}
          <div className="mt-8 text-center text-sm text-muted-foreground print:block">
            <p>Relatório gerado automaticamente pelo Sistema TechZe Diagnóstico</p>
            <p>Para suporte técnico, entre em contato conosco</p>
          </div>
        </div>
      </div>
    );
  }

  // Tela principal de diagnóstico
  return (
    <div className="min-h-screen bg-gradient-to-br from-tech-darker to-tech-dark">
      <div className="container-responsive py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <Button
            variant="outline"
            onClick={() => navigate('/dashboard')}
            className="electric-border"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Dashboard
          </Button>
          
          <h1 className="text-2xl font-bold tech-font neon-text">
            🔧 Diagnóstico Técnico
          </h1>
          
          <div className="text-sm text-muted-foreground text-right">
            <p><strong>{company?.name}</strong></p>
            <p>Técnico: {user?.email?.split('@')[0]}</p>
          </div>
        </div>

        {error && (
          <Alert className="mb-6 bg-red-900/20 border-red-900/50">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {/* Formulário de dados */}
          <Card className="card-electric">
            <CardHeader>
              <CardTitle className="flex items-center">
                <User className="h-5 w-5 mr-2 text-electric" />
                Dados do Cliente e Equipamento
              </CardTitle>
              <CardDescription>
                Preencha as informações antes de iniciar o diagnóstico
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="clientName" className="text-sm font-medium">
                  Nome do Cliente *
                </Label>
                <Input
                  id="clientName"
                  placeholder="Ex: João Silva"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  className="electric-border"
                  disabled={isRunning}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="clientPhone" className="text-sm font-medium">
                  Telefone (opcional)
                </Label>
                <Input
                  id="clientPhone"
                  placeholder="Ex: (11) 99999-9999"
                  value={clientPhone}
                  onChange={(e) => setClientPhone(e.target.value)}
                  className="electric-border"
                  disabled={isRunning}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="deviceName" className="text-sm font-medium">
                  Modelo/Marca do Equipamento *
                </Label>
                <Input
                  id="deviceName"
                  placeholder="Ex: Dell Inspiron 15 3000, MacBook Pro M1"
                  value={deviceName}
                  onChange={(e) => setDeviceName(e.target.value)}
                  className="electric-border"
                  disabled={isRunning}
                />
              </div>

              <Button
                onClick={runDiagnostic}
                disabled={isRunning || !deviceName.trim() || !clientName.trim()}
                className="w-full btn-electric tech-font font-semibold"
                size="lg"
              >
                {isRunning ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Executando Diagnóstico...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-5 w-5" />
                    Iniciar Diagnóstico Completo
                  </>
                )}
              </Button>
            </CardContent>
          </Card>

          {/* Progress do diagnóstico */}
          <Card className="card-electric">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Zap className="h-5 w-5 mr-2 text-electric" />
                Progresso do Diagnóstico
              </CardTitle>
              <CardDescription>
                {isRunning ? 'Analisando o equipamento...' : 'Aguardando início do teste'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {steps.map((step, index) => (
                  <div
                    key={step.id}
                    className={`flex items-center space-x-3 p-3 rounded-lg border transition-all ${
                      step.status === 'running' 
                        ? 'bg-electric/10 border-electric/30 electric-glow'
                        : step.status === 'completed'
                        ? 'bg-green-400/10 border-green-400/30'
                        : step.status === 'error'
                        ? 'bg-red-400/10 border-red-400/30'
                        : 'bg-muted/5 border-muted/10'
                    }`}
                  >
                    <div className="flex-shrink-0">
                      {step.status === 'pending' ? (
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted/20">
                          {step.icon}
                        </div>
                      ) : (
                        <div className="flex items-center justify-center w-8 h-8 rounded-full">
                          {getStatusIcon(step.status)}
                        </div>
                      )}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium truncate">
                          {step.name}
                        </p>
                        {step.duration && (
                          <span className="text-xs text-muted-foreground">
                            {step.duration}s
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {step.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {isRunning && startTime && (
                <div className="mt-4 pt-4 border-t border-muted/20">
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>Tempo decorrido:</span>
                    <span>{Math.floor((Date.now() - startTime.getTime()) / 1000)}s</span>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
