
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Activity, 
  HardDrive, 
  MemoryStick, 
  Wifi,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Clock
} from "lucide-react";

interface DiagnosticProgressProps {
  isRunning: boolean;
  progress?: number;
  currentStep?: string;
  status?: 'pending' | 'running' | 'completed' | 'failed';
}

export const DiagnosticProgress = ({ 
  isRunning, 
  progress = 0, 
  currentStep = "Iniciando...",
  status = 'pending'
}: DiagnosticProgressProps) => {
  
  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'running':
        return <Activity className="w-5 h-5 text-orange-500 animate-pulse" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusBadge = () => {
    const variants = {
      pending: 'secondary',
      running: 'default',
      completed: 'default',
      failed: 'destructive'
    } as const;

    const labels = {
      pending: 'Pendente',
      running: 'Executando',
      completed: 'Concluído',
      failed: 'Falhou'
    };

    return (
      <Badge variant={variants[status]} className="ml-2">
        {labels[status]}
      </Badge>
    );
  };

  const diagnosticSteps = [
    { icon: Activity, label: "CPU", key: "cpu" },
    { icon: MemoryStick, label: "Memória", key: "memory" },
    { icon: HardDrive, label: "Disco", key: "disk" },
    { icon: Wifi, label: "Rede", key: "network" }
  ];

  return (
    <Card className="bg-black/40 backdrop-blur-md border-white/20">
      <CardHeader>
        <CardTitle className="text-white flex items-center">
          {getStatusIcon()}
          <span className="ml-2">Diagnóstico em Andamento</span>
          {getStatusBadge()}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-gray-300">{currentStep}</span>
            <span className="text-orange-400">{Math.round(progress)}%</span>
          </div>
          <Progress 
            value={progress} 
            className="h-2 bg-white/10"
          />
        </div>

        {/* Diagnostic Steps */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {diagnosticSteps.map((step, index) => {
            const Icon = step.icon;
            const isActive = isRunning && progress > (index * 25);
            const isCompleted = progress > ((index + 1) * 25);
            
            return (
              <div 
                key={step.key}
                className={`flex flex-col items-center p-3 rounded-lg border transition-all ${
                  isCompleted 
                    ? 'bg-green-500/20 border-green-500/50 text-green-400'
                    : isActive 
                      ? 'bg-orange-500/20 border-orange-500/50 text-orange-400 animate-pulse'
                      : 'bg-white/5 border-white/20 text-gray-500'
                }`}
              >
                <Icon className="w-6 h-6 mb-2" />
                <span className="text-xs font-medium">{step.label}</span>
                {isCompleted && (
                  <CheckCircle className="w-4 h-4 mt-1 text-green-500" />
                )}
              </div>
            );
          })}
        </div>

        {/* Status Message */}
        {status === 'failed' && (
          <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg">
            <div className="flex items-center text-red-400">
              <AlertTriangle className="w-4 h-4 mr-2" />
              <span className="text-sm">Erro durante o diagnóstico. Tente novamente.</span>
            </div>
          </div>
        )}

        {status === 'completed' && (
          <div className="p-3 bg-green-500/20 border border-green-500/50 rounded-lg">
            <div className="flex items-center text-green-400">
              <CheckCircle className="w-4 h-4 mr-2" />
              <span className="text-sm">Diagnóstico concluído com sucesso!</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
