import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useDiagnostics } from './useDiagnostics';
import { diagnosticApiService } from '@/services/diagnosticApiService';
import { useToast } from '@/hooks/use-toast';
import React from 'react';

// Mock do diagnosticApiService
jest.mock('@/services/diagnosticApiService', () => ({
  diagnosticApiService: {
    getDiagnostics: jest.fn(),
    getDevices: jest.fn(),
    getDiagnostic: jest.fn(),
    executeFullDiagnostic: jest.fn(),
    createDevice: jest.fn(),
    deleteDevice: jest.fn(),
  },
}));

// Mock do useToast
jest.mock('@/hooks/use-toast', () => ({
  useToast: jest.fn(),
}));

const mockToast = jest.fn();
const mockDiagnosticApiService = diagnosticApiService as jest.Mocked<typeof diagnosticApiService>;

// Dados de teste
const mockDiagnostics = [
  {
    id: 'diag-1',
    device_id: 'device-1',
    user_id: 'user-1',
    status: 'completed',
    health_score: 85,
    cpu_status: 'good',
    memory_status: 'good',
    disk_status: 'good',
    network_status: 'good',
    antivirus_status: 'good',
    driver_status: 'good',
    created_at: '2024-01-15T10:30:00Z',
    updated_at: '2024-01-15T10:35:00Z',
  },
  {
    id: 'diag-2',
    device_id: 'device-2',
    user_id: 'user-1',
    status: 'completed',
    health_score: 45,
    cpu_status: 'warning',
    memory_status: 'critical',
    disk_status: 'good',
    network_status: 'good',
    antivirus_status: 'warning',
    driver_status: 'good',
    created_at: '2024-01-14T10:30:00Z',
    updated_at: '2024-01-14T10:35:00Z',
  },
];

const mockDevices = [
  {
    id: 'device-1',
    user_id: 'user-1',
    name: 'Computador Principal',
    type: 'desktop',
    os: 'Windows 11',
    created_at: '2024-01-10T10:30:00Z',
    updated_at: '2024-01-15T10:35:00Z',
  },
  {
    id: 'device-2',
    user_id: 'user-1',
    name: 'Laptop Trabalho',
    type: 'laptop',
    os: 'Windows 10',
    created_at: '2024-01-05T10:30:00Z',
    updated_at: '2024-01-14T10:35:00Z',
  },
];

// Wrapper para fornecer o QueryClientProvider
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useDiagnostics', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Configuração padrão dos mocks
    (useToast as jest.Mock).mockReturnValue({ toast: mockToast });
    mockDiagnosticApiService.getDiagnostics.mockResolvedValue(mockDiagnostics);
    mockDiagnosticApiService.getDevices.mockResolvedValue(mockDevices);
  });

  it('deve carregar diagnósticos e dispositivos', async () => {
    const { result } = renderHook(() => useDiagnostics(), {
      wrapper: createWrapper(),
    });
    
    // Inicialmente, os dados devem estar carregando
    expect(result.current.isLoadingDiagnostics).toBe(true);
    expect(result.current.isLoadingDevices).toBe(true);
    
    // Aguarda o carregamento dos dados
    await waitFor(() => {
      expect(result.current.isLoadingDiagnostics).toBe(false);
      expect(result.current.isLoadingDevices).toBe(false);
    });
    
    // Verifica se os dados foram carregados corretamente
    expect(result.current.diagnostics).toEqual(mockDiagnostics);
    expect(result.current.devices).toEqual(mockDevices);
    
    // Verifica se as funções da API foram chamadas
    expect(mockDiagnosticApiService.getDiagnostics).toHaveBeenCalled();
    expect(mockDiagnosticApiService.getDevices).toHaveBeenCalled();
  });

  it('deve calcular estatísticas corretamente', async () => {
    const { result } = renderHook(() => useDiagnostics(), {
      wrapper: createWrapper(),
    });
    
    await waitFor(() => {
      expect(result.current.isLoadingDiagnostics).toBe(false);
      expect(result.current.isLoadingDevices).toBe(false);
    });
    
    // Verifica as estatísticas calculadas
    expect(result.current.statistics).toEqual({
      totalDevices: 2,
      totalDiagnostics: 2,
      healthyDevices: 1, // device-1 tem health_score 85
      criticalDevices: 1, // device-2 tem health_score 45
    });
  });

  it('deve executar diagnóstico completo com sucesso', async () => {
    const mockDiagnosticResult = {
      id: 'diag-3',
      device_id: 'device-1',
      user_id: 'user-1',
      status: 'completed',
      health_score: 90,
      created_at: '2024-01-16T10:30:00Z',
      updated_at: '2024-01-16T10:35:00Z',
    };
    
    mockDiagnosticApiService.executeFullDiagnostic.mockResolvedValue(mockDiagnosticResult);
    
    const { result } = renderHook(() => useDiagnostics(), {
      wrapper: createWrapper(),
    });
    
    await waitFor(() => {
      expect(result.current.isLoadingDiagnostics).toBe(false);
    });
    
    // Executa o diagnóstico
    act(() => {
      result.current.executeFullDiagnostic('device-1');
    });
    
    // Verifica se a função da API foi chamada
    expect(mockDiagnosticApiService.executeFullDiagnostic).toHaveBeenCalledWith('device-1');
    
    // Aguarda a conclusão da mutação
    await waitFor(() => {
      expect(result.current.isRunningDiagnostic).toBe(false);
    });
    
    // Verifica se o toast foi exibido
    expect(mockToast).toHaveBeenCalledWith({
      title: 'Diagnóstico Concluído',
      description: 'Diagnóstico executado com sucesso. Health Score: 90.0%',
    });
  
  });

  it('deve lidar com erro ao executar diagnóstico', async () => {
    const mockError = new Error('Falha ao conectar com o dispositivo');
    mockDiagnosticApiService.executeFullDiagnostic.mockRejectedValue(mockError);
    
    const { result } = renderHook(() => useDiagnostics(), {
      wrapper: createWrapper(),
    });
    
    await waitFor(() => {
      expect(result.current.isLoadingDiagnostics).toBe(false);
    });
    
    // Executa o diagnóstico
    act(() => {
      result.current.executeFullDiagnostic('device-1');
    });
    
    // Aguarda a conclusão da mutação
    await waitFor(() => {
      expect(result.current.isRunningDiagnostic).toBe(false);
    });
    
    // Verifica se o toast de erro foi exibido
    expect(mockToast).toHaveBeenCalledWith({
      title: 'Erro no Diagnóstico',
      description: 'Falha ao conectar com o dispositivo',
      variant: 'destructive',
    });
  
  });

  it('deve criar dispositivo com sucesso', async () => {
    const newDevice = {
      id: 'device-3',
      user_id: 'user-1',
      name: 'Novo Dispositivo',
      type: 'tablet',
      os: 'Android',
      created_at: '2024-01-16T10:30:00Z',
      updated_at: '2024-01-16T10:30:00Z',
    };
    
    const createDeviceRequest = {
      name: 'Novo Dispositivo',
      type: 'tablet',
      os: 'Android',
    };
    
    mockDiagnosticApiService.createDevice.mockResolvedValue(newDevice);
    
    const { result } = renderHook(() => useDiagnostics(), {
      wrapper: createWrapper(),
    });
    
    await waitFor(() => {
      expect(result.current.isLoadingDevices).toBe(false);
    });
    
    // Cria o dispositivo
    act(() => {
      result.current.createDevice(createDeviceRequest);
    });
    
    // Verifica se a função da API foi chamada
    expect(mockDiagnosticApiService.createDevice).toHaveBeenCalledWith(createDeviceRequest);
    
    // Aguarda a conclusão da mutação
    await waitFor(() => {
      expect(result.current.isCreatingDevice).toBe(false);
    });
    
    // Verifica se o toast foi exibido
    expect(mockToast).toHaveBeenCalledWith({
      title: 'Dispositivo Criado',
      description: 'Dispositivo cadastrado com sucesso',
    });
  
  });

  it('deve excluir dispositivo com sucesso', async () => {
    mockDiagnosticApiService.deleteDevice.mockResolvedValue({ success: true });
    
    const { result } = renderHook(() => useDiagnostics(), {
      wrapper: createWrapper(),
    });
    
    await waitFor(() => {
      expect(result.current.isLoadingDevices).toBe(false);
    });
    
    // Exclui o dispositivo
    act(() => {
      result.current.deleteDevice('device-1');
    });
    
    // Verifica se a função da API foi chamada
    expect(mockDiagnosticApiService.deleteDevice).toHaveBeenCalledWith('device-1');
    
    // Aguarda a conclusão da mutação
    await waitFor(() => {
      expect(result.current.isDeletingDevice).toBe(false);
    });
    
    // Verifica se o toast foi exibido
    expect(mockToast).toHaveBeenCalledWith({
      title: 'Dispositivo Excluído',
      description: 'Dispositivo removido com sucesso',
    });
  
  });

  it('deve obter o último diagnóstico para um dispositivo', async () => {
    const { result } = renderHook(() => useDiagnostics(), {
      wrapper: createWrapper(),
    });
    
    await waitFor(() => {
      expect(result.current.isLoadingDiagnostics).toBe(false);
    });
    
    // Obtém o último diagnóstico para o dispositivo-1
    const lastDiagnostic = result.current.getLastDiagnosticForDevice('device-1');
    
    // Verifica se o diagnóstico correto foi retornado
    expect(lastDiagnostic).toEqual(mockDiagnostics[0]);
  });

  it('deve retornar undefined para dispositivo sem diagnóstico', async () => {
    const { result } = renderHook(() => useDiagnostics(), {
      wrapper: createWrapper(),
    });
    
    await waitFor(() => {
      expect(result.current.isLoadingDiagnostics).toBe(false);
    });
    
    // Tenta obter diagnóstico para um dispositivo inexistente
    const lastDiagnostic = result.current.getLastDiagnosticForDevice('dispositivo-inexistente');
    
    // Verifica que retorna undefined
    expect(lastDiagnostic).toBeUndefined();
  });

  it('deve buscar um diagnóstico específico', async () => {
    const mockSpecificDiagnostic = {
      id: 'diag-specific',
      device_id: 'device-1',
      user_id: 'user-1',
      status: 'completed',
      health_score: 88,
      created_at: '2024-01-16T10:30:00Z',
      updated_at: '2024-01-16T10:35:00Z',
    };
    
    mockDiagnosticApiService.getDiagnostic.mockResolvedValue(mockSpecificDiagnostic);
    
    const { result } = renderHook(() => useDiagnostics(), {
      wrapper: createWrapper(),
    });
    
    // Busca um diagnóstico específico
    const diagnostic = await result.current.getDiagnostic('diag-specific');
    
    // Verifica se a função da API foi chamada
    expect(mockDiagnosticApiService.getDiagnostic).toHaveBeenCalledWith('diag-specific');
    
    // Verifica se o diagnóstico correto foi retornado
    expect(diagnostic).toEqual(mockSpecificDiagnostic);
  });
});