import React from 'react';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { DiagnosticResult, Device } from '@/types/diagnostic';
import { 
  Activity, 
  HardDrive, 
  Cpu, 
  MemoryStick, 
  Wifi, 
  Shield, 
  Settings,
  Calendar,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Download,
  FileText,
  DollarSign,
  RefreshCw,
  Lightbulb,
  Clock,
  Info
} from 'lucide-react';

interface DiagnosticDetailsProps {
  diagnostic: DiagnosticResult;
  device?: Device;
  isOpen: boolean;
  onClose: () => void;
  onRunNewDiagnostic?: (deviceId: string) => void;
}

const DiagnosticDetails: React.FC<DiagnosticDetailsProps> = ({
  diagnostic,
  device,
  isOpen,
  onClose,
  onRunNewDiagnostic
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusIcon = (status: 'good' | 'warning' | 'critical' | undefined) => {
    switch (status) {
      case 'good':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
      case 'critical':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: 'good' | 'warning' | 'critical' | undefined) => {
    switch (status) {
      case 'good':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getHealthScoreColor = (score: number | undefined) => {
    if (!score) return 'text-gray-500';
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getOverallStatus = () => {
    const statuses = [
      diagnostic.cpu_status,
      diagnostic.memory_status,
      diagnostic.disk_status,
      diagnostic.network_status,
      diagnostic.antivirus_status,
      diagnostic.driver_status
    ].filter(Boolean);

    if (statuses.includes('critical')) return 'critical';
    if (statuses.includes('warning')) return 'warning';
    if (statuses.includes('good')) return 'good';
    return undefined;
  };

  const overallStatus = getOverallStatus();

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl flex items-center gap-2">
            {getStatusIcon(overallStatus)}
            Detalhes do Diagnóstico
          </DialogTitle>
          <DialogDescription>
            {device?.name || `Dispositivo ${diagnostic.device_id.slice(0, 8)}`} • 
            {formatDate(diagnostic.created_at)}
          </DialogDescription>
        </DialogHeader>

        {/* Resumo do Diagnóstico */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Informações Gerais</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">ID:</span>
                <span className="text-sm font-medium">{diagnostic.id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Dispositivo:</span>
                <span className="text-sm font-medium">{device?.name || diagnostic.device_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Status:</span>
                <Badge 
                  variant="outline" 
                  className={getStatusColor(overallStatus)}
                >
                  {diagnostic.status === 'completed' ? 'Concluído' : 
                  diagnostic.status === 'running' ? 'Executando' :
                  diagnostic.status === 'failed' ? 'Falhou' : 'Pendente'}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Data:</span>
                <span className="text-sm font-medium">{formatDate(diagnostic.created_at)}</span>
              </div>
              {diagnostic.execution_time && (
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Tempo de Execução:</span>
                  <span className="text-sm font-medium">{diagnostic.execution_time.toFixed(1)}s</span>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base">Health Score</CardTitle>
            </CardHeader>
            <CardContent>
              {diagnostic.health_score !== undefined ? (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Pontuação Geral</span>
                    <span className={`text-2xl font-bold ${getHealthScoreColor(diagnostic.health_score)}`}>
                      {diagnostic.health_score.toFixed(1)}%
                    </span>
                  </div>
                  <Progress 
                    value={diagnostic.health_score} 
                    className="h-2"
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center h-16 text-muted-foreground">
                  Pontuação não disponível
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Componentes Status */}
        <Card className="mb-4">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Status dos Componentes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* CPU */}
              <div className="border rounded-md p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-blue-500" />
                    <span className="font-medium">CPU</span>
                  </div>
                  {getStatusIcon(diagnostic.cpu_status)}
                </div>
                {diagnostic.cpu_metrics && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Uso:</span>
                      <span>{diagnostic.cpu_metrics.usage_percent.toFixed(1)}%</span>
                    </div>
                    {diagnostic.cpu_metrics.temperature_celsius && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Temperatura:</span>
                        <span>{diagnostic.cpu_metrics.temperature_celsius.toFixed(1)}°C</span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Memória */}
              <div className="border rounded-md p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <MemoryStick className="h-4 w-4 text-purple-500" />
                    <span className="font-medium">RAM</span>
                  </div>
                  {getStatusIcon(diagnostic.memory_status)}
                </div>
                {diagnostic.memory_metrics && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Uso:</span>
                      <span>{diagnostic.memory_metrics.usage_percent.toFixed(1)}%</span>
                    </div>
                    {diagnostic.memory_metrics.available_gb && diagnostic.memory_metrics.total_gb && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Disponível:</span>
                        <span>{diagnostic.memory_metrics.available_gb.toFixed(1)} GB / {diagnostic.memory_metrics.total_gb.toFixed(1)} GB</span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Disco */}
              <div className="border rounded-md p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <HardDrive className="h-4 w-4 text-green-500" />
                    <span className="font-medium">Disco</span>
                  </div>
                  {getStatusIcon(diagnostic.disk_status)}
                </div>
                {diagnostic.disk_metrics && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Uso:</span>
                      <span>{diagnostic.disk_metrics.usage_percent.toFixed(1)}%</span>
                    </div>
                    {diagnostic.disk_metrics.available_gb && diagnostic.disk_metrics.total_gb && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Disponível:</span>
                        <span>{diagnostic.disk_metrics.available_gb.toFixed(1)} GB / {diagnostic.disk_metrics.total_gb.toFixed(1)} GB</span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Rede */}
              <div className="border rounded-md p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Wifi className="h-4 w-4 text-cyan-500" />
                    <span className="font-medium">Rede</span>
                  </div>
                  {getStatusIcon(diagnostic.network_status)}
                </div>
                {diagnostic.network_metrics && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Latência:</span>
                      <span>{diagnostic.network_metrics.latency_ms.toFixed(0)} ms</span>
                    </div>
                    {diagnostic.network_metrics.download_speed_mbps && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Download:</span>
                        <span>{diagnostic.network_metrics.download_speed_mbps.toFixed(1)} Mbps</span>
                      </div>
                    )}
                    {diagnostic.network_metrics.upload_speed_mbps && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Upload:</span>
                        <span>{diagnostic.network_metrics.upload_speed_mbps.toFixed(1)} Mbps</span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Antivírus */}
              <div className="border rounded-md p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4 text-red-500" />
                    <span className="font-medium">Segurança</span>
                  </div>
                  {getStatusIcon(diagnostic.antivirus_status)}
                </div>
                {diagnostic.antivirus_metrics && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Proteção:</span>
                      <span>{diagnostic.antivirus_metrics.protection_enabled ? 'Ativa' : 'Inativa'}</span>
                    </div>
                    {diagnostic.antivirus_metrics.last_scan_date && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Última Verificação:</span>
                        <span>{new Date(diagnostic.antivirus_metrics.last_scan_date).toLocaleDateString('pt-BR')}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Drivers */}
              <div className="border rounded-md p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Settings className="h-4 w-4 text-orange-500" />
                    <span className="font-medium">Drivers</span>
                  </div>
                  {getStatusIcon(diagnostic.driver_status)}
                </div>
                {diagnostic.driver_metrics && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Total:</span>
                      <span>{diagnostic.driver_metrics.total_drivers}</span>
                    </div>
                    {diagnostic.driver_metrics.problematic_drivers > 0 && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Problemáticos:</span>
                        <span className="text-red-500">{diagnostic.driver_metrics.problematic_drivers}</span>
                      </div>
                    )}
                    {diagnostic.driver_metrics.outdated_drivers > 0 && (
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Desatualizados:</span>
                        <span className="text-yellow-500">{diagnostic.driver_metrics.outdated_drivers}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Problemas e Recomendações */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          {/* Problemas Encontrados */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-red-500" />
                Problemas Encontrados
              </CardTitle>
            </CardHeader>
            <CardContent>
              {diagnostic.issues_found && diagnostic.issues_found.length > 0 ? (
                <div className="space-y-3">
                  {diagnostic.issues_found.map((issue, index) => (
                    <div key={index} className="border-b pb-2 last:border-0 last:pb-0">
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-medium">{issue.description}</span>
                        <Badge className={getSeverityColor(issue.severity)}>
                          {issue.severity}
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Categoria: {issue.category}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="flex items-center justify-center h-16 text-muted-foreground">
                  Nenhum problema encontrado
                </div>
              )}
            </CardContent>
          </Card>

          {/* Recomendações */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-yellow-500" />
                Recomendações
              </CardTitle>
            </CardHeader>
            <CardContent>
              {diagnostic.recommendations && diagnostic.recommendations.length > 0 ? (
                <ul className="space-y-2">
                  {diagnostic.recommendations.map((recommendation, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <div className="mt-1 text-green-500">
                        <CheckCircle className="h-4 w-4" />
                      </div>
                      <span>{recommendation}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="flex items-center justify-center h-16 text-muted-foreground">
                  Nenhuma recomendação disponível
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Mensagem de Erro */}
        {diagnostic.error_message && (
          <Card className="mb-4 border-red-200">
            <CardHeader className="pb-2 bg-red-50">
              <CardTitle className="text-base text-red-700 flex items-center gap-2">
                <XCircle className="h-4 w-4" />
                Erro no Diagnóstico
              </CardTitle>
            </CardHeader>
            <CardContent className="bg-red-50">
              <p className="text-red-700">{diagnostic.error_message}</p>
            </CardContent>
          </Card>
        )}

        {/* Ações */}
        <div className="flex flex-wrap gap-2 justify-end">
          {onRunNewDiagnostic && (
            <Button 
              variant="outline" 
              onClick={() => onRunNewDiagnostic(diagnostic.device_id)}
              className="flex items-center gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Novo Diagnóstico
            </Button>
          )}
          <Button 
            variant="outline" 
            className="flex items-center gap-2"
          >
            <FileText className="h-4 w-4" />
            Relatório Completo
          </Button>
          <Button 
            variant="outline" 
            className="flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Exportar PDF
          </Button>
          <Button 
            variant="default" 
            className="flex items-center gap-2"
          >
            <DollarSign className="h-4 w-4" />
            Gerar Orçamento
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default DiagnosticDetails;