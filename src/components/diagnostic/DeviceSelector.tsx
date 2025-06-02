
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  Monitor, 
  Smartphone, 
  Server, 
  Laptop,
  Plus,
  Play,
  Trash2
} from "lucide-react";
import { Device } from "@/types/diagnostic";
import { useDiagnostics } from "@/hooks/useDiagnostics";
import { CreateDeviceDialog } from "./CreateDeviceDialog";

interface DeviceSelectorProps {
  onDeviceSelect: (deviceId: string) => void;
  selectedDeviceId?: string;
}

export const DeviceSelector = ({ onDeviceSelect, selectedDeviceId }: DeviceSelectorProps) => {
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const { 
    devices, 
    isLoadingDevices, 
    deleteDevice, 
    isDeletingDevice,
    getLastDiagnosticForDevice,
    executeFullDiagnostic,
    isRunningDiagnostic
  } = useDiagnostics();

  const getDeviceIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'desktop':
        return Monitor;
      case 'laptop':
        return Laptop;
      case 'mobile':
        return Smartphone;
      case 'server':
        return Server;
      default:
        return Monitor;
    }
  };

  const getHealthBadge = (device: Device) => {
    const lastDiagnostic = getLastDiagnosticForDevice(device.id);
    
    if (!lastDiagnostic?.health_score) {
      return <Badge variant="secondary">Sem diagnóstico</Badge>;
    }

    const score = lastDiagnostic.health_score;
    
    if (score >= 80) {
      return <Badge className="bg-green-500/20 text-green-400 border-green-500/50">Saudável</Badge>;
    } else if (score >= 50) {
      return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/50">Atenção</Badge>;
    } else {
      return <Badge className="bg-red-500/20 text-red-400 border-red-500/50">Crítico</Badge>;
    }
  };

  if (isLoadingDevices) {
    return (
      <Card className="bg-black/40 backdrop-blur-md border-white/20">
        <CardContent className="p-6">
          <div className="text-center text-gray-400">Carregando dispositivos...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card className="bg-black/40 backdrop-blur-md border-white/20">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-white">Selecionar Dispositivo</CardTitle>
            <Button
              onClick={() => setShowCreateDialog(true)}
              size="sm"
              className="btn-tecno"
            >
              <Plus className="w-4 h-4 mr-2" />
              Adicionar
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {devices.length === 0 ? (
            <div className="text-center py-8">
              <Monitor className="w-12 h-12 text-gray-500 mx-auto mb-4" />
              <p className="text-gray-400 mb-4">Nenhum dispositivo cadastrado</p>
              <Button
                onClick={() => setShowCreateDialog(true)}
                className="btn-tecno"
              >
                <Plus className="w-4 h-4 mr-2" />
                Cadastrar Primeiro Dispositivo
              </Button>
            </div>
          ) : (
            <div className="grid gap-4">
              {devices.map((device) => {
                const Icon = getDeviceIcon(device.type);
                const isSelected = selectedDeviceId === device.id;
                const lastDiagnostic = getLastDiagnosticForDevice(device.id);
                
                return (
                  <div
                    key={device.id}
                    className={`p-4 rounded-lg border cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-orange-500/20 border-orange-500/50'
                        : 'bg-white/5 border-white/20 hover:bg-white/10 hover:border-white/30'
                    }`}
                    onClick={() => onDeviceSelect(device.id)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Icon className={`w-8 h-8 ${isSelected ? 'text-orange-400' : 'text-gray-400'}`} />
                        <div>
                          <h4 className="text-white font-medium">{device.name}</h4>
                          <p className="text-gray-400 text-sm">
                            {device.type} • {device.os || 'SO não informado'}
                          </p>
                          {device.processor && (
                            <p className="text-gray-500 text-xs">{device.processor}</p>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {getHealthBadge(device)}
                        
                        <div className="flex space-x-1">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={(e) => {
                              e.stopPropagation();
                              executeFullDiagnostic(device.id);
                            }}
                            disabled={isRunningDiagnostic}
                            className="text-green-400 hover:bg-green-500/20"
                          >
                            <Play className="w-4 h-4" />
                          </Button>
                          
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteDevice(device.id);
                            }}
                            disabled={isDeletingDevice}
                            className="text-red-400 hover:bg-red-500/20"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                    
                    {lastDiagnostic && (
                      <div className="mt-3 pt-3 border-t border-white/10">
                        <div className="flex justify-between text-xs text-gray-400">
                          <span>Último diagnóstico</span>
                          <span>{new Date(lastDiagnostic.created_at).toLocaleDateString()}</span>
                        </div>
                        {lastDiagnostic.health_score && (
                          <div className="mt-1">
                            <span className="text-xs text-gray-400">Health Score: </span>
                            <span className={`text-xs font-medium ${
                              lastDiagnostic.health_score >= 80 ? 'text-green-400' : 
                              lastDiagnostic.health_score >= 50 ? 'text-yellow-400' : 'text-red-400'
                            }`}>
                              {lastDiagnostic.health_score.toFixed(1)}%
                            </span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      <CreateDeviceDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
      />
    </>
  );
};
