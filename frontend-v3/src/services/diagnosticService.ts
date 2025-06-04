import diagnosticApiService from './diagnosticApiService';
import { DiagnosticResult, Device, CreateDeviceRequest } from '../types/diagnostic';

/**
 * Este serviço mantém compatibilidade com o código legado enquanto
 * redireciona todas as chamadas para o diagnosticApiService consolidado.
 */
class DiagnosticService {
  // Métodos para diagnósticos
  async getDiagnostics(): Promise<DiagnosticResult[]> {
    return diagnosticApiService.getDiagnostics();
  }

  async getDiagnostic(id: string): Promise<DiagnosticResult | null> {
    return diagnosticApiService.getDiagnostic(id);
  }

  async createDiagnostic(data: any): Promise<DiagnosticResult> {
    return diagnosticApiService.runDiagnostic(data);
  }

  async runFullDiagnostic(data: any): Promise<DiagnosticResult> {
    return diagnosticApiService.executeFullDiagnostic(data.device_id || 'default-device');
  }

  async getDiagnosticHistory(params?: any): Promise<{ data: DiagnosticResult[]; total: number; page: number; limit: number; pages: number }> {
    return diagnosticApiService.getDiagnosticHistory(params);
  }

  // Métodos para dispositivos
  async getDevices(): Promise<Device[]> {
    return diagnosticApiService.getDevices();
  }

  async getDevice(id: string): Promise<Device | null> {
    return diagnosticApiService.getDevice(id);
  }

  async createDevice(data: CreateDeviceRequest): Promise<Device> {
    return diagnosticApiService.createDevice(data);
  }

  async updateDevice(id: string, data: Partial<CreateDeviceRequest>): Promise<Device> {
    return diagnosticApiService.updateDevice(id, data);
  }

  async deleteDevice(id: string): Promise<{ success: boolean }> {
    return diagnosticApiService.deleteDevice(id);
  }

  // Método para verificar saúde da API
  async checkHealth(): Promise<{ status: string; message: string }> {
    return diagnosticApiService.checkHealth();
  }
}

export const diagnosticService = new DiagnosticService();
export default diagnosticService;