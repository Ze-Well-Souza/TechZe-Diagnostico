
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
import { useDiagnostics } from "@/hooks/useDiagnostics";
import { DiagnosticResult } from "@/types/diagnostic";
import { DeviceSelector } from "@/components/diagnostic/DeviceSelector";
import { DiagnosticProgress } from "@/components/diagnostic/DiagnosticProgress";

const Diagnostic = () => {
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>("");
  const [currentDiagnostic, setCurrentDiagnostic] = useState<DiagnosticResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);

  const { 
    executeFullDiagnostic, 
    isRunningDiagnostic,
    getDiagnostic 
  } = useDiagnostics();

  const startDiagnostic = async () => {
    if (!selectedDeviceId) return;
    
    setIsRunning(true);
    setProgress(0);
    
    try {
      const diagnostic = await executeFullDiagnostic(selectedDeviceId);
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
      const statusInterval = setInterval(async () => {
        if (diagnostic?.id) {
          const updated = await getDiagnostic(diagnostic.id);
          if (updated) {
            setCurrentDiagnostic(updated);
            if (updated.status === 'completed') {
              clearInterval(statusInterval);
              setProgress(100);
              setIsRunning(false);
            }
          }
        }
      }, 1000);
      
    } catch (error) {
      console.error("Erro ao executar diagnóstico:", error);
      setIsRunning(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return <Badge className="bg-green-500/20 text-green-300"><CheckCircle className="w-4 h-4 mr-1" />Concluído</Badge>;
      case 'running':
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

        {/* Device Selection */}
        <DeviceSelector 
          onDeviceSelect={setSelectedDeviceId}
          selectedDeviceId={selectedDeviceId}
        />

        {/* Start Diagnostic */}
        {selectedDeviceId && (
          <Card className="bg-black/40 backdrop-blur-md border-white/20">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Play className="w-6 h-6 text-orange-500" />
                Executar Diagnóstico
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Button 
                onClick={startDiagnostic}
                disabled={isRunningDiagnostic || isRunning}
                className="w-full btn-tecno"
              >
                {isRunning ? "Executando Diagnóstico..." : "Iniciar Diagnóstico"}
              </Button>
            </CardContent>
          </Card>
        )}

        {/* Diagnostic Progress */}
        {(isRunning || currentDiagnostic) && (
          <DiagnosticProgress 
            isRunning={isRunning}
            progress={progress}
            currentStep={isRunning ? "Analisando sistema..." : "Concluído"}
            status={currentDiagnostic?.status || 'pending'}
          />
        )}

        {/* Diagnostic Results */}
        {currentDiagnostic && currentDiagnostic.status === 'completed' && currentDiagnostic.health_score && (
          <div className="space-y-6">
            {/* Health Score */}
            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardContent className="p-6">
                <div className="text-center">
                  <h3 className="text-white text-lg mb-2">Score de Saúde do Sistema</h3>
                  <div className={`text-6xl font-bold ${getHealthScoreColor(currentDiagnostic.health_score)}`}>
                    {currentDiagnostic.health_score.toFixed(1)}%
                  </div>
                  <p className="text-gray-300 mt-2">
                    {currentDiagnostic.health_score >= 80 ? "Sistema em bom estado" :
                     currentDiagnostic.health_score >= 60 ? "Sistema necessita atenção" :
                     "Sistema crítico - ação imediata necessária"}
                  </p>
                </div>
              </CardContent>
            </Card>

            {/* Component Status */}
            <Card className="bg-black/40 backdrop-blur-md border-white/20">
              <CardHeader>
                <CardTitle className="text-white">Status dos Componentes</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* CPU */}
                  {currentDiagnostic.cpu_status && (
                    <div className="bg-black/20 p-4 rounded-lg border border-white/10">
                      <div className="flex items-center gap-3 mb-2">
                        <Cpu className={`w-5 h-5 ${
                          currentDiagnostic.cpu_status === 'good' ? 'text-green-400' :
                          currentDiagnostic.cpu_status === 'warning' ? 'text-yellow-400' : 'text-red-400'
                        }`} />
                        <h4 className="text-white font-medium">CPU</h4>
                      </div>
                      <div className={`text-lg font-bold ${
                        currentDiagnostic.cpu_status === 'good' ? 'text-green-400' :
                        currentDiagnostic.cpu_status === 'warning' ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {currentDiagnostic.cpu_metrics?.usage_percent 
                          ? `${currentDiagnostic.cpu_metrics.usage_percent.toFixed(1)}%` 
                          : 'N/A'}
                      </div>
                      <p className="text-gray-300 text-sm mt-1">
                        {currentDiagnostic.cpu_status === 'good' ? 'Funcionando bem' :
                         currentDiagnostic.cpu_status === 'warning' ? 'Atenção necessária' : 'Estado crítico'}
                      </p>
                    </div>
                  )}

                  {/* Memory */}
                  {currentDiagnostic.memory_status && (
                    <div className="bg-black/20 p-4 rounded-lg border border-white/10">
                      <div className="flex items-center gap-3 mb-2">
                        <MemoryStick className={`w-5 h-5 ${
                          currentDiagnostic.memory_status === 'good' ? 'text-green-400' :
                          currentDiagnostic.memory_status === 'warning' ? 'text-yellow-400' : 'text-red-400'
                        }`} />
                        <h4 className="text-white font-medium">Memória</h4>
                      </div>
                      <div className={`text-lg font-bold ${
                        currentDiagnostic.memory_status === 'good' ? 'text-green-400' :
                        currentDiagnostic.memory_status === 'warning' ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {currentDiagnostic.memory_metrics?.usage_percent 
                          ? `${currentDiagnostic.memory_metrics.usage_percent.toFixed(1)}%` 
                          : 'N/A'}
                      </div>
                      <p className="text-gray-300 text-sm mt-1">
                        {currentDiagnostic.memory_status === 'good' ? 'Funcionando bem' :
                         currentDiagnostic.memory_status === 'warning' ? 'Atenção necessária' : 'Estado crítico'}
                      </p>
                    </div>
                  )}

                  {/* Disk */}
                  {currentDiagnostic.disk_status && (
                    <div className="bg-black/20 p-4 rounded-lg border border-white/10">
                      <div className="flex items-center gap-3 mb-2">
                        <HardDrive className={`w-5 h-5 ${
                          currentDiagnostic.disk_status === 'good' ? 'text-green-400' :
                          currentDiagnostic.disk_status === 'warning' ? 'text-yellow-400' : 'text-red-400'
                        }`} />
                        <h4 className="text-white font-medium">Disco</h4>
                      </div>
                      <div className={`text-lg font-bold ${
                        currentDiagnostic.disk_status === 'good' ? 'text-green-400' :
                        currentDiagnostic.disk_status === 'warning' ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {currentDiagnostic.disk_metrics?.usage_percent 
                          ? `${currentDiagnostic.disk_metrics.usage_percent.toFixed(1)}%` 
                          : 'N/A'}
                      </div>
                      <p className="text-gray-300 text-sm mt-1">
                        {currentDiagnostic.disk_status === 'good' ? 'Funcionando bem' :
                         currentDiagnostic.disk_status === 'warning' ? 'Atenção necessária' : 'Estado crítico'}
                      </p>
                    </div>
                  )}

                  {/* Network */}
                  {currentDiagnostic.network_status && (
                    <div className="bg-black/20 p-4 rounded-lg border border-white/10">
                      <div className="flex items-center gap-3 mb-2">
                        <CircuitBoard className={`w-5 h-5 ${
                          currentDiagnostic.network_status === 'good' ? 'text-green-400' :
                          currentDiagnostic.network_status === 'warning' ? 'text-yellow-400' : 'text-red-400'
                        }`} />
                        <h4 className="text-white font-medium">Rede</h4>
                      </div>
                      <div className={`text-lg font-bold ${
                        currentDiagnostic.network_status === 'good' ? 'text-green-400' :
                        currentDiagnostic.network_status === 'warning' ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {currentDiagnostic.network_metrics?.download_speed_mbps 
                          ? `${currentDiagnostic.network_metrics.download_speed_mbps.toFixed(1)} Mbps` 
                          : 'N/A'}
                      </div>
                      <p className="text-gray-300 text-sm mt-1">
                        {currentDiagnostic.network_status === 'good' ? 'Funcionando bem' :
                         currentDiagnostic.network_status === 'warning' ? 'Atenção necessária' : 'Estado crítico'}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default Diagnostic;
