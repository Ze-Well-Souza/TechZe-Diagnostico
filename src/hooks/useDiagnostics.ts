
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { diagnosticApiService } from '@/services/diagnosticApiService';
import { DiagnosticResult, Device, CreateDeviceRequest } from '@/types/diagnostic';
import { useToast } from '@/hooks/use-toast';

export const useDiagnostics = () => {
  const { toast } = useToast();
  const queryClient = useQueryClient();

  // Estados para controle de loading
  const [isRunningDiagnostic, setIsRunningDiagnostic] = useState(false);

  // Query para buscar todos os diagnósticos
  const {
    data: diagnostics = [],
    isLoading: isLoadingDiagnostics,
    error: diagnosticsError,
    refetch: refetchDiagnostics,
  } = useQuery({
    queryKey: ['diagnostics'],
    queryFn: () => diagnosticApiService.getDiagnostics(),
  });

  // Query para buscar todos os dispositivos
  const {
    data: devices = [],
    isLoading: isLoadingDevices,
    error: devicesError,
    refetch: refetchDevices,
  } = useQuery({
    queryKey: ['devices'],
    queryFn: () => diagnosticApiService.getDevices(),
  });

  // Função para buscar um diagnóstico específico
  const getDiagnostic = async (diagnosticId: string): Promise<DiagnosticResult | null> => {
    return await diagnosticApiService.getDiagnostic(diagnosticId);
  };

  // Mutation para executar diagnóstico completo
  const executeFullDiagnosticMutation = useMutation({
    mutationFn: (deviceId: string) => {
      setIsRunningDiagnostic(true);
      return diagnosticApiService.executeFullDiagnostic(deviceId);
    },
    onSuccess: (result) => {
      setIsRunningDiagnostic(false);
      toast({
        title: "Diagnóstico Concluído",
        description: `Diagnóstico executado com sucesso. Health Score: ${result.health_score?.toFixed(1) || 'N/A'}%`,
      });
      // Invalidar queries para atualizar dados
      queryClient.invalidateQueries({ queryKey: ['diagnostics'] });
      queryClient.invalidateQueries({ queryKey: ['devices'] });
    },
    onError: (error) => {
      setIsRunningDiagnostic(false);
      toast({
        title: "Erro no Diagnóstico",
        description: error instanceof Error ? error.message : "Erro desconhecido ao executar diagnóstico",
        variant: "destructive",
      });
    },
  });

  // Mutation para criar dispositivo
  const createDeviceMutation = useMutation({
    mutationFn: (device: CreateDeviceRequest) => diagnosticApiService.createDevice(device),
    onSuccess: () => {
      toast({
        title: "Dispositivo Criado",
        description: "Dispositivo cadastrado com sucesso",
      });
      queryClient.invalidateQueries({ queryKey: ['devices'] });
    },
    onError: (error) => {
      toast({
        title: "Erro ao Criar Dispositivo",
        description: error instanceof Error ? error.message : "Erro desconhecido",
        variant: "destructive",
      });
    },
  });

  // Mutation para excluir dispositivo
  const deleteDeviceMutation = useMutation({
    mutationFn: (deviceId: string) => diagnosticApiService.deleteDevice(deviceId),
    onSuccess: () => {
      toast({
        title: "Dispositivo Excluído",
        description: "Dispositivo removido com sucesso",
      });
      queryClient.invalidateQueries({ queryKey: ['devices'] });
    },
    onError: (error) => {
      toast({
        title: "Erro ao Excluir Dispositivo",
        description: error instanceof Error ? error.message : "Erro desconhecido",
        variant: "destructive",
      });
    },
  });

  // Função helper para encontrar último diagnóstico de um dispositivo
  const getLastDiagnosticForDevice = (deviceId: string): DiagnosticResult | undefined => {
    return diagnostics
      .filter(d => d.device_id === deviceId)
      .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())[0];
  };

  // Função helper para obter estatísticas gerais
  const getStatistics = () => {
    const totalDevices = devices.length;
    const totalDiagnostics = diagnostics.length;
    const healthyDevices = devices.filter(device => {
      const lastDiagnostic = getLastDiagnosticForDevice(device.id);
      return lastDiagnostic?.health_score && lastDiagnostic.health_score >= 80;
    }).length;
    const criticalDevices = devices.filter(device => {
      const lastDiagnostic = getLastDiagnosticForDevice(device.id);
      return lastDiagnostic?.health_score && lastDiagnostic.health_score < 50;
    }).length;

    return {
      totalDevices,
      totalDiagnostics,
      healthyDevices,
      criticalDevices,
    };
  };

  return {
    // Dados
    diagnostics,
    devices,
    statistics: getStatistics(),
    
    // Estados de loading
    isLoadingDiagnostics,
    isLoadingDevices,
    isRunningDiagnostic: isRunningDiagnostic || executeFullDiagnosticMutation.isPending,
    
    // Erros
    diagnosticsError,
    devicesError,
    
    // Funções
    executeFullDiagnostic: executeFullDiagnosticMutation.mutate,
    createDevice: createDeviceMutation.mutate,
    deleteDevice: deleteDeviceMutation.mutate,
    getDiagnostic,
    refetchDiagnostics,
    refetchDevices,
    getLastDiagnosticForDevice,
    
    // Estados das mutations
    isCreatingDevice: createDeviceMutation.isPending,
    isDeletingDevice: deleteDeviceMutation.isPending,
  };
};
