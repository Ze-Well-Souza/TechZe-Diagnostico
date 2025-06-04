import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
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
  XCircle
} from 'lucide-react';

interface DiagnosticCardProps {
  diagnostic: DiagnosticResult;
  device?: Device;
  onViewDetails?: (diagnostic: DiagnosticResult) => void;
  onRunNewDiagnostic?: (deviceId: string) => void;
}

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

const DiagnosticCard: React.FC<DiagnosticCardProps> = ({
  diagnostic,
  device,
  onViewDetails,
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

  return (
    <Card className="w-full hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {getStatusIcon(overallStatus)}
            <CardTitle className="text-lg">
              {device?.name || `Dispositivo ${diagnostic.device_id.slice(0, 8)}`}
            </CardTitle>
          </div>
          <Badge 
            variant="outline" 
            className={getStatusColor(overallStatus)}
          >
            {diagnostic.status === 'completed' ? 'Concluído' : 
             diagnostic.status === 'running' ? 'Executando' :
             diagnostic.status === 'failed' ? 'Falhou' : 'Pendente'}
          </Badge>
        </div>
        
        <CardDescription className="flex items-center space-x-2">
          <Calendar className="h-4 w-4" />
          <span>Executado em {formatDate(diagnostic.created_at)}</span>
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Health Score */}
        {diagnostic.health_score !== undefined && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Health Score</span>
              <span className={`text-lg font-bold ${getHealthScoreColor(diagnostic.health_score)}`}>
                {diagnostic.health_score.toFixed(1)}%
              </span>
            </div>
            <Progress 
              value={diagnostic.health_score} 
              className="h-2"
            />
          </div>
        )}

        {/* Componentes Status */}
        <div className="grid grid-cols-2 gap-3">
          {/* CPU */}
          <div className="flex items-center space-x-2">
            <Cpu className="h-4 w-4 text-blue-500" />
            <span className="text-sm">CPU</span>
            {getStatusIcon(diagnostic.cpu_status)}
            {diagnostic.cpu_metrics && (
              <span className="text-xs text-gray-500">
                {diagnostic.cpu_metrics.usage_percent.toFixed(1)}%
              </span>
            )}
          </div>

          {/* Memória */}
          <div className="flex items-center space-x-2">
            <MemoryStick className="h-4 w-4 text-purple-500" />
            <span className="text-sm">RAM</span>
            {getStatusIcon(diagnostic.memory_status)}
            {diagnostic.memory_metrics && (
              <span className="text-xs text-gray-500">
                {diagnostic.memory_metrics.usage_percent.toFixed(1)}%
              </span>
            )}
          </div>

          {/* Disco */}
          <div className="flex items-center space-x-2">
            <HardDrive className="h-4 w-4 text-green-500" />
            <span className="text-sm">Disco</span>
            {getStatusIcon(diagnostic.disk_status)}
            {diagnostic.disk_metrics && (
              <span className="text-xs text-gray-500">
                {diagnostic.disk_metrics.usage_percent.toFixed(1)}%
              </span>
            )}
          </div>

          {/* Rede */}
          <div className="flex items-center space-x-2">
            <Wifi className="h-4 w-4 text-cyan-500" />
            <span className="text-sm">Rede</span>
            {getStatusIcon(diagnostic.network_status)}
            {diagnostic.network_metrics && (
              <span className="text-xs text-gray-500">
                {diagnostic.network_metrics.latency_ms.toFixed(0)}ms
              </span>
            )}
          </div>

          {/* Antivírus */}
          <div className="flex items-center space-x-2">
            <Shield className="h-4 w-4 text-red-500" />
            <span className="text-sm">Segurança</span>
            {getStatusIcon(diagnostic.antivirus_status)}
          </div>

          {/* Drivers */}
          <div className="flex items-center space-x-2">
            <Settings className="h-4 w-4 text-orange-500" />
            <span className="text-sm">Drivers</span>
            {getStatusIcon(diagnostic.driver_status)}
          </div>
        </div>

        {/* Error Message */}
        {diagnostic.error_message && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-700">{diagnostic.error_message}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex space-x-2 pt-2">
          {onViewDetails && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => onViewDetails(diagnostic)}
              className="flex-1"
            >
              Ver Detalhes
            </Button>
          )}
          {onRunNewDiagnostic && (
            <Button 
              size="sm" 
              onClick={() => onRunNewDiagnostic(diagnostic.device_id)}
              className="flex-1"
            >
              Novo Diagnóstico
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default DiagnosticCard;