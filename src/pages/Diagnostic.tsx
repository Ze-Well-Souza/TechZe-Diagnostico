
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
  AlertTriangle
} from 'lucide-react';

interface DiagnosticStep {
  id: string;
  name: string;
  icon: React.ReactNode;
  status: 'pending' | 'running' | 'completed' | 'error';
  result?: any;
}

export default function Diagnostic() {
  const { user, company } = useAuth();
  const navigate = useNavigate();
  const [deviceName, setDeviceName] = useState('Meu Computador');
  const [clientName, setClientName] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [diagnosticResult, setDiagnosticResult] = useState<any>(null);
  const [error, setError] = useState('');

  const [steps, setSteps] = useState<DiagnosticStep[]>([
    {
      id: 'system',
      name: 'Informações do Sistema',
      icon: <Monitor className="h-5 w-5" />,
      status: 'pending'
    },
    {
      id: 'cpu',
      name: 'Processador e Performance',
      icon: <Cpu className="h-5 w-5" />,
      status: 'pending'
    },
    {
      id: 'memory',
      name: 'Memória RAM',
      icon: <HardDrive className="h-5 w-5" />,
      status: 'pending'
    },
    {
      id: 'network',
      name: 'Conectividade de Rede',
      icon: <Wifi className="h-5 w-5" />,
      status: 'pending'
    },
    {
      id: 'battery',
      name: 'Estado da Bateria',
      icon: <Battery className="h-5 w-5" />,
      status: 'pending'
    }
  ]);

  const updateStepStatus = (stepId: string, status: DiagnosticStep['status'], result?: any) => {
    setSteps(prev => prev.map(step => 
      step.id === stepId 
        ? { ...step, status, result }
        : step
    ));
  };

  const runDiagnostic = async () => {
    if (!deviceName.trim()) {
      setError('Por favor, informe o nome do dispositivo');
      return;
    }

    setIsRunning(true);
    setError('');
    setCurrentStep(0);

    try {
      // Reset all steps
      setSteps(prev => prev.map(step => ({ ...step, status: 'pending' as const })));

      // Step 1: System Info
      setCurrentStep(1);
      updateStepStatus('system', 'running');
      const systemInfo = await realDiagnosticService.getSystemInfo();
      updateStepStatus('system', 'completed', systemInfo);
      await delay(1000);

      // Step 2: CPU
      setCurrentStep(2);
      updateStepStatus('cpu', 'running');
      const hardwareMetrics = await realDiagnosticService.getHardwareMetrics();
      updateStepStatus('cpu', 'completed', hardwareMetrics.cpu);
      await delay(1000);

      // Step 3: Memory
      setCurrentStep(3);
      updateStepStatus('memory', 'running');
      updateStepStatus('memory', 'completed', hardwareMetrics.memory);
      await delay(1000);

      // Step 4: Network
      setCurrentStep(4);
      updateStepStatus('network', 'running');
      updateStepStatus('network', 'completed', hardwareMetrics.network);
      await delay(1000);

      // Step 5: Battery
      setCurrentStep(5);
      updateStepStatus('battery', 'running');
      updateStepStatus('battery', 'completed', hardwareMetrics.battery);
      await delay(1000);

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
        raw_data: fullDiagnostic
      });

      setDiagnosticResult(savedDiagnostic);
      setCurrentStep(0);

    } catch (err) {
      console.error('Erro durante diagnóstico:', err);
      setError('Erro durante o diagnóstico. Tente novamente.');
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

  if (diagnosticResult) {
    return (
      <div className="container-responsive py-8">
        <Card className="card-electric max-w-4xl mx-auto">
          <CardHeader className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <CheckCircle2 className="h-8 w-8 text-green-400" />
              <CardTitle className="tech-font text-2xl neon-text">
                Diagnóstico Concluído
              </CardTitle>
            </div>
            <CardDescription>
              Resultado do diagnóstico para {deviceName}
            </CardDescription>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 rounded-lg bg-muted/20 electric-border">
                <div className="flex items-center space-x-2">
                  <Cpu className="h-5 w-5 text-electric" />
                  <span className="font-semibold">CPU</span>
                </div>
                <p className="text-2xl font-bold mt-2">{diagnosticResult.cpu_metrics?.usage_percentage}%</p>
                <p className="text-sm text-muted-foreground">Uso atual</p>
              </div>
              
              <div className="p-4 rounded-lg bg-muted/20 electric-border">
                <div className="flex items-center space-x-2">
                  <HardDrive className="h-5 w-5 text-electric" />
                  <span className="font-semibold">RAM</span>
                </div>
                <p className="text-2xl font-bold mt-2">{diagnosticResult.memory_metrics?.usage_percentage}%</p>
                <p className="text-sm text-muted-foreground">Uso atual</p>
              </div>
              
              <div className="p-4 rounded-lg bg-muted/20 electric-border">
                <div className="flex items-center space-x-2">
                  <Wifi className="h-5 w-5 text-electric" />
                  <span className="font-semibold">Rede</span>
                </div>
                <p className="text-lg font-bold mt-2">{diagnosticResult.network_metrics?.connection_type}</p>
                <p className="text-sm text-muted-foreground">Tipo de conexão</p>
              </div>
              
              <div className="p-4 rounded-lg bg-muted/20 electric-border">
                <div className="flex items-center space-x-2">
                  <Zap className="h-5 w-5 text-electric" />
                  <span className="font-semibold">Saúde</span>
                </div>
                <p className="text-2xl font-bold mt-2 text-green-400">{diagnosticResult.health_score}%</p>
                <p className="text-sm text-muted-foreground">Score geral</p>
              </div>
            </div>

            <div className="flex space-x-4">
              <Button 
                onClick={() => navigate('/dashboard')}
                className="btn-electric"
              >
                Ver Dashboard
              </Button>
              <Button 
                variant="outline"
                onClick={() => {
                  setDiagnosticResult(null);
                  setDeviceName('');
                  setClientName('');
                }}
                className="electric-border"
              >
                Novo Diagnóstico
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container-responsive py-8">
      <Card className="card-electric max-w-2xl mx-auto">
        <CardHeader className="text-center">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="p-3 rounded-lg bg-primary/10 electric-glow">
              <Zap className="h-8 w-8 text-electric" />
            </div>
          </div>
          <CardTitle className="tech-font text-2xl neon-text">
            Diagnóstico de Hardware
          </CardTitle>
          <CardDescription>
            {company?.name} - Sistema de Diagnóstico Profissional
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-6">
          {!isRunning && (
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="deviceName">Nome do Dispositivo *</Label>
                <Input
                  id="deviceName"
                  value={deviceName}
                  onChange={(e) => setDeviceName(e.target.value)}
                  placeholder="Ex: PC-001, Notebook-Cliente"
                  className="electric-border"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="clientName">Nome do Cliente (Opcional)</Label>
                <Input
                  id="clientName"
                  value={clientName}
                  onChange={(e) => setClientName(e.target.value)}
                  placeholder="Nome do cliente"
                  className="electric-border"
                />
              </div>

              {error && (
                <Alert className="border-destructive/50">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertDescription className="text-destructive">
                    {error}
                  </AlertDescription>
                </Alert>
              )}

              <Button
                onClick={runDiagnostic}
                disabled={isRunning}
                className="w-full btn-electric tech-font font-semibold"
                size="lg"
              >
                <Zap className="mr-2 h-5 w-5" />
                Iniciar Diagnóstico Real
              </Button>
            </div>
          )}

          {isRunning && (
            <div className="space-y-4">
              <div className="text-center mb-6">
                <h3 className="tech-font text-lg font-semibold text-electric mb-2">
                  Executando Diagnóstico...
                </h3>
                <p className="text-sm text-muted-foreground">
                  Analisando {deviceName}
                </p>
              </div>

              <div className="space-y-3">
                {steps.map((step, index) => (
                  <div
                    key={step.id}
                    className={`flex items-center space-x-3 p-3 rounded-lg border transition-all duration-300 ${
                      step.status === 'running' 
                        ? 'electric-border electric-glow' 
                        : step.status === 'completed'
                        ? 'border-green-400/30'
                        : step.status === 'error'
                        ? 'border-red-400/30'
                        : 'border-muted'
                    }`}
                  >
                    <div className={`p-2 rounded ${
                      step.status === 'running' ? 'bg-primary/20' :
                      step.status === 'completed' ? 'bg-green-400/20' :
                      step.status === 'error' ? 'bg-red-400/20' :
                      'bg-muted/20'
                    }`}>
                      {step.icon}
                    </div>
                    
                    <div className="flex-1">
                      <p className="font-medium">{step.name}</p>
                      {step.status === 'running' && (
                        <p className="text-sm text-electric">Analisando...</p>
                      )}
                      {step.status === 'completed' && (
                        <p className="text-sm text-green-400">Concluído</p>
                      )}
                      {step.status === 'error' && (
                        <p className="text-sm text-red-400">Erro</p>
                      )}
                    </div>
                    
                    {getStatusIcon(step.status)}
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
