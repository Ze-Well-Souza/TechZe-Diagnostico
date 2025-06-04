import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Device, DiagnosticResult } from '@/types/diagnostic';
import { 
  Monitor, 
  Smartphone, 
  Laptop, 
  Server,
  Calendar,
  Activity,
  AlertTriangle,
  CheckCircle,
  XCircle,
  MoreVertical
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface DeviceCardProps {
  device: Device;
  lastDiagnostic?: DiagnosticResult;
  onRunDiagnostic?: (deviceId: string) => void;
  onViewDiagnostics?: (deviceId: string) => void;
  onEditDevice?: (device: Device) => void;
  onDeleteDevice?: (deviceId: string) => void;
  isRunningDiagnostic?: boolean;
}

const getDeviceIcon = (type: string) => {
  switch (type.toLowerCase()) {
    case 'desktop':
      return <Monitor className="h-5 w-5" />;
    case 'laptop':
      return <Laptop className="h-5 w-5" />;
    case 'mobile':
    case 'smartphone':
      return <Smartphone className="h-5 w-5" />;
    case 'server':
      return <Server className="h-5 w-5" />;
    default:
      return <Monitor className="h-5 w-5" />;
  }
};

const getHealthStatusIcon = (score: number | undefined) => {
  if (!score) return <Activity className="h-4 w-4 text-gray-400" />;
  if (score >= 80) return <CheckCircle className="h-4 w-4 text-green-500" />;
  if (score >= 60) return <AlertTriangle className="h-4 w-4 text-yellow-500" />;
  return <XCircle className="h-4 w-4 text-red-500" />;
};

const getHealthStatusColor = (score: number | undefined) => {
  if (!score) return 'bg-gray-100 text-gray-800 border-gray-200';
  if (score >= 80) return 'bg-green-100 text-green-800 border-green-200';
  if (score >= 60) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
  return 'bg-red-100 text-red-800 border-red-200';
};

const getHealthStatusText = (score: number | undefined) => {
  if (!score) return 'Sem dados';
  if (score >= 80) return 'Saudável';
  if (score >= 60) return 'Atenção';
  return 'Crítico';
};

const DeviceCard: React.FC<DeviceCardProps> = ({
  device,
  lastDiagnostic,
  onRunDiagnostic,
  onViewDiagnostics,
  onEditDevice,
  onDeleteDevice,
  isRunningDiagnostic = false
}) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const healthScore = lastDiagnostic?.health_score;

  return (
    <Card className="w-full hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              {getDeviceIcon(device.type)}
            </div>
            <div>
              <CardTitle className="text-lg">{device.name}</CardTitle>
              <CardDescription className="capitalize">
                {device.type} • {device.os || 'Sistema não informado'}
              </CardDescription>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Badge 
              variant="outline" 
              className={getHealthStatusColor(healthScore)}
            >
              <div className="flex items-center space-x-1">
                {getHealthStatusIcon(healthScore)}
                <span>{getHealthStatusText(healthScore)}</span>
              </div>
            </Badge>
            
            {(onEditDevice || onDeleteDevice) && (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  {onEditDevice && (
                    <DropdownMenuItem onClick={() => onEditDevice(device)}>
                      Editar
                    </DropdownMenuItem>
                  )}
                  {onDeleteDevice && (
                    <DropdownMenuItem 
                      onClick={() => onDeleteDevice(device.id)}
                      className="text-red-600"
                    >
                      Excluir
                    </DropdownMenuItem>
                  )}
                </DropdownMenuContent>
              </DropdownMenu>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Especificações do Dispositivo */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          {device.processor && (
            <div>
              <span className="text-gray-500">Processador:</span>
              <p className="font-medium truncate" title={device.processor}>
                {device.processor}
              </p>
            </div>
          )}
          
          {device.ram && (
            <div>
              <span className="text-gray-500">Memória:</span>
              <p className="font-medium">{device.ram}</p>
            </div>
          )}
          
          {device.storage && (
            <div>
              <span className="text-gray-500">Armazenamento:</span>
              <p className="font-medium">{device.storage}</p>
            </div>
          )}
          
          {device.os_version && (
            <div>
              <span className="text-gray-500">Versão SO:</span>
              <p className="font-medium">{device.os_version}</p>
            </div>
          )}
        </div>

        {/* Health Score */}
        {healthScore !== undefined && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Health Score</span>
              <span className={`text-lg font-bold ${
                healthScore >= 80 ? 'text-green-600' :
                healthScore >= 60 ? 'text-yellow-600' : 'text-red-600'
              }`}>
                {healthScore.toFixed(1)}%
              </span>
            </div>
          </div>
        )}

        {/* Último Diagnóstico */}
        {lastDiagnostic && (
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <Calendar className="h-4 w-4" />
            <span>Último diagnóstico: {formatDate(lastDiagnostic.created_at)}</span>
          </div>
        )}

        {/* Actions */}
        <div className="flex space-x-2 pt-2">
          {onRunDiagnostic && (
            <Button 
              size="sm" 
              onClick={() => onRunDiagnostic(device.id)}
              disabled={isRunningDiagnostic}
              className="flex-1"
            >
              {isRunningDiagnostic ? 'Executando...' : 'Executar Diagnóstico'}
            </Button>
          )}
          
          {onViewDiagnostics && (
            <Button 
              variant="outline" 
              size="sm" 
              onClick={() => onViewDiagnostics(device.id)}
              className="flex-1"
            >
              Ver Histórico
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default DeviceCard;