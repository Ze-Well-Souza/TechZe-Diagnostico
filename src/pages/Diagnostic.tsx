import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { 
  Play, 
  Monitor, 
  User, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Cpu,
  HardDrive,
  MemoryStick,
  CircuitBoard,
  Zap
} from "lucide-react";
import { diagnosticService, DiagnosticResult } from "@/services/diagnosticService";

const Diagnostic = () => {
  const [deviceName, setDeviceName] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [currentDiagnostic, setCurrentDiagnostic] = useState<DiagnosticResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const startDiagnostic = async () => {
    if (!deviceName || !customerName) return;
    
    setIsRunning(true);
    setProgress(0);
    
    const diagnostic = await diagnosticService.startDiagnostic(deviceName, customerName);
    setCurrentDiagnostic(diagnostic);
    
    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          setIsRunning(false);
          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 500);
    
    // Update diagnostic status
    const statusInterval = setInterval(() => {
      const updated = diagnosticService.getDiagnostic(diagnostic.id);
      if (updated) {
        setCurrentDiagnostic(updated);
        if (updated.status === 'completed') {
          clearInterval(statusInterval);
          setProgress(100);
          setIsRunning(false);
        }
      }
    }, 1000);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-500/20 text-green-300"><CheckCircle className="w-4 h-4 mr-1" />Concluído</Badge>;
      case 'in_progress':
        return <Badge className="bg-yellow-500/20 text-yellow-300"><Clock className="w-4 h-4 mr-1" />Em Andamento</Badge>;
      case 'failed':
        return <Badge className="bg-red-500/20 text-red-300"><AlertTriangle className="w-4 h-4 mr-1" />Falhou</Badge>;
      default:
        return <Badge className="bg-gray-500/20 text-gray-300"><Clock className="w-4 h-4 mr-1" />Pendente</Badge>;
    }
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 80) return "text-green-400";
    if (score >= 60) return "text-yellow-400";
    return "text-red-400";
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return "text-red-400";
      case 'high': return "text-orange-400";
      case 'medium': return "text-yellow-400";
      default: return "text-blue-400";
    }
  };

  const getComponentIcon = (name: string) => {
    switch (name) {
      case 'CPU': return <Cpu className="w-5 h-5" />;
      case 'RAM': return <MemoryStick className="w-5 h-5" />;
      case 'Armazenamento': return <HardDrive className="w-5 h-5" />;
      case 'Placa Mãe': return <CircuitBoard className="w-5 h-5" />;
      case 'Fonte': return <Zap className="w-5 h-5" />;
      default: return <Monitor className="w-5 h-5" />;
    }
  };

  const getComponentStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return "text-green-400";
      case 'warning': return "text-yellow-400";
      case 'critical': return "text-red-400";
      default: return "text-gray-400";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Sistema de Diagnóstico
          </h1>
          <p className="text-gray-200">Execute diagnósticos completos de hardware e software</p>
        </div>

        {/* Formulário de Início */}
        <Card className="bg-black/40 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Play className="w-6 h-6 text-orange-500" />
              Iniciar Novo Diagnóstico
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="device" className="text-white">Nome do Dispositivo</Label>
                <div className="relative">
                  <Monitor className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="device"
                    placeholder="Ex: PC-VENDAS-01"
                    value={deviceName}
                    onChange={(e) => setDeviceName(e.target.value)}
                    className="pl-10 bg-white/10 border-white/30 text-white placeholder:text-white/50"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="customer" className="text-white">Nome do Cliente</Label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="customer"
                    placeholder="Ex: João Silva"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    className="pl-10 bg-white/10 border-white/30 text-white placeholder:text-white/50"
                  />
                </div>
              </div>
            </div>
            
            <Button 
              onClick={startDiagnostic}
              disabled={!deviceName || !customerName || isRunning}
              className="w-full btn-tecno"
            >
              {isRunning ? "Executando Diagnóstico..." : "Iniciar Diagnóstico"}
            </Button>
          </CardContent>
        </Card>

        {/* Progresso do Diagnóstico */}
        {currentDiagnostic && (
          <Card className="bg-black/40 backdrop-blur-md border-white/20">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-white">Diagnóstico em Andamento</CardTitle>
                {getStatusBadge(currentDiagnostic.status)}
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-300">Progresso</span>
                  <span className="text-white">{Math.round(progress)}%</span>
                </div>
                <Progress value={progress} className="w-full" />
              </div>
              
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-gray-300">Dispositivo: </span>
                  <span className="text-white">{currentDiagnostic.deviceName}</span>
                </div>
                <div>
                  <span className="text-gray-300">Cliente: </span>
                  <span className="text-white">{currentDiagnostic.customer}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Resultados do Diagnóstico */}
        {currentDiagnostic && currentDiagnostic.status === 'completed' && (
          <div className="space-y-6">
            {/* Score de Saúde */}
            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardContent className="p-6">
                <div className="text-center">
                  <h3 className="text-white text-lg mb-2">Score de Saúde do Sistema</h3>
                  <div className={`text-6xl font-bold ${getHealthScoreColor(currentDiagnostic.healthScore)}`}>
                    {currentDiagnostic.healthScore}%
                  </div>
                  <p className="text-gray-300 mt-2">
                    {currentDiagnostic.healthScore >= 80 ? "Sistema em bom estado" :
                     currentDiagnostic.healthScore >= 60 ? "Sistema necessita atenção" :
                     "Sistema crítico - ação imediata necessária"}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Status dos Componentes */}
            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Status dos Componentes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {currentDiagnostic.components.map((component, index) => (
                    <div key={index} className="bg-black/20 p-4 rounded-lg border border-white/10">
                      <div className="flex items-center gap-3 mb-2">
                        <div className={getComponentStatusColor(component.status)}>
                          {getComponentIcon(component.name)}
                        </div>
                        <h4 className="text-white font-medium">{component.name}</h4>
                      </div>
                      <div className={`text-2xl font-bold ${getComponentStatusColor(component.status)}`}>
                        {component.score}%
                      </div>
                      <p className="text-gray-300 text-sm mt-1">{component.details}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Problemas Detectados */}
            {currentDiagnostic.issues.length > 0 && (
              <Card className="bg-black/40 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <AlertTriangle className="w-6 h-6 text-red-400" />
                    Problemas Detectados ({currentDiagnostic.issues.length})
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {currentDiagnostic.issues.map((issue) => (
                      <div key={issue.id} className="bg-black/20 p-4 rounded-lg border border-white/10">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <h4 className="text-white font-medium">{issue.component}</h4>
                            <p className="text-gray-300">{issue.description}</p>
                          </div>
                          <Badge className={`${getSeverityColor(issue.severity)} bg-transparent border`}>
                            {issue.severity.toUpperCase()}
                          </Badge>
                        </div>
                        {issue.solution && (
                          <div className="mt-3 p-3 bg-blue-500/10 rounded border border-blue-500/20">
                            <p className="text-blue-300 text-sm">
                              <strong>Solução recomendada:</strong> {issue.solution}
                            </p>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Recomendações */}
            {currentDiagnostic.recommendations.length > 0 && (
              <Card className="bg-black/40 backdrop-blur-md border-white/20">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <CheckCircle className="w-6 h-6 text-green-400" />
                    Recomendações de Otimização
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {currentDiagnostic.recommendations.map((recommendation, index) => (
                      <div key={index} className="flex items-center gap-3 p-3 bg-green-500/10 rounded border border-green-500/20">
                        <CheckCircle className="w-4 h-4 text-green-400 flex-shrink-0" />
                        <p className="text-green-300">{recommendation}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Diagnostic;
