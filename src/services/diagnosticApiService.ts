
import { apiClient } from "./apiClient";
import { supabase } from "@/integrations/supabase/client";
import { 
  DiagnosticResult, 
  Device, 
  CreateDiagnosticRequest, 
  CreateDeviceRequest 
} from "@/types/diagnostic";

export class DiagnosticApiService {
  
  // Métodos para diagnósticos via microserviço
  async runDiagnostic(request: CreateDiagnosticRequest): Promise<DiagnosticResult> {
    console.log("Iniciando diagnóstico via microserviço:", request);
    return apiClient.post<DiagnosticResult>("/api/v1/diagnostics", request);
  }

  async getDiagnosticStatus(diagnosticId: string): Promise<DiagnosticResult> {
    console.log("Consultando status do diagnóstico:", diagnosticId);
    return apiClient.get<DiagnosticResult>(`/api/v1/diagnostics/${diagnosticId}`);
  }

  // Métodos para dispositivos via Supabase
  async getDevices(): Promise<Device[]> {
    const { data, error } = await supabase
      .from('devices')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error("Erro ao buscar dispositivos:", error);
      throw new Error(error.message);
    }

    return data || [];
  }

  async getDevice(deviceId: string): Promise<Device | null> {
    const { data, error } = await supabase
      .from('devices')
      .select('*')
      .eq('id', deviceId)
      .maybeSingle();

    if (error) {
      console.error("Erro ao buscar dispositivo:", error);
      throw new Error(error.message);
    }

    return data;
  }

  async createDevice(device: CreateDeviceRequest): Promise<Device> {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error("Usuário não autenticado");
    }

    const { data, error } = await supabase
      .from('devices')
      .insert({
        ...device,
        user_id: user.id,
      })
      .select()
      .single();

    if (error) {
      console.error("Erro ao criar dispositivo:", error);
      throw new Error(error.message);
    }

    return data;
  }

  async updateDevice(deviceId: string, updates: Partial<CreateDeviceRequest>): Promise<Device> {
    const { data, error } = await supabase
      .from('devices')
      .update(updates)
      .eq('id', deviceId)
      .select()
      .single();

    if (error) {
      console.error("Erro ao atualizar dispositivo:", error);
      throw new Error(error.message);
    }

    return data;
  }

  async deleteDevice(deviceId: string): Promise<void> {
    const { error } = await supabase
      .from('devices')
      .delete()
      .eq('id', deviceId);

    if (error) {
      console.error("Erro ao excluir dispositivo:", error);
      throw new Error(error.message);
    }
  }

  // Métodos para diagnósticos via Supabase
  async getDiagnostics(): Promise<DiagnosticResult[]> {
    const { data, error } = await supabase
      .from('diagnostics')
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      console.error("Erro ao buscar diagnósticos:", error);
      throw new Error(error.message);
    }

    return data || [];
  }

  async getDiagnostic(diagnosticId: string): Promise<DiagnosticResult | null> {
    const { data, error } = await supabase
      .from('diagnostics')
      .select('*')
      .eq('id', diagnosticId)
      .maybeSingle();

    if (error) {
      console.error("Erro ao buscar diagnóstico:", error);
      throw new Error(error.message);
    }

    return data;
  }

  async saveDiagnostic(diagnostic: Partial<DiagnosticResult>): Promise<DiagnosticResult> {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) {
      throw new Error("Usuário não autenticado");
    }

    const { data, error } = await supabase
      .from('diagnostics')
      .insert({
        ...diagnostic,
        user_id: user.id,
      })
      .select()
      .single();

    if (error) {
      console.error("Erro ao salvar diagnóstico:", error);
      throw new Error(error.message);
    }

    return data;
  }

  async updateDiagnostic(diagnosticId: string, updates: Partial<DiagnosticResult>): Promise<DiagnosticResult> {
    const { data, error } = await supabase
      .from('diagnostics')
      .update(updates)
      .eq('id', diagnosticId)
      .select()
      .single();

    if (error) {
      console.error("Erro ao atualizar diagnóstico:", error);
      throw new Error(error.message);
    }

    return data;
  }

  // Método híbrido: executa diagnóstico via API e salva no Supabase
  async executeFullDiagnostic(deviceId: string): Promise<DiagnosticResult> {
    try {
      console.log("Executando diagnóstico completo para dispositivo:", deviceId);
      
      // 1. Buscar informações do dispositivo
      const device = await this.getDevice(deviceId);
      if (!device) {
        throw new Error("Dispositivo não encontrado");
      }

      // 2. Criar diagnóstico inicial no Supabase
      const initialDiagnostic = await this.saveDiagnostic({
        device_id: deviceId,
        status: 'pending',
      });

      // 3. Executar diagnóstico via microserviço
      try {
        const diagnosticResult = await this.runDiagnostic({
          device_id: deviceId,
          system_info: {
            os: device.os || 'Unknown',
            os_version: device.os_version || 'Unknown',
            processor: device.processor || 'Unknown',
            ram: device.ram || 'Unknown',
            storage: device.storage || 'Unknown',
          }
        });

        // 4. Atualizar com os resultados
        const updatedDiagnostic = await this.updateDiagnostic(initialDiagnostic.id, {
          status: diagnosticResult.status,
          cpu_status: diagnosticResult.cpu_status,
          cpu_metrics: diagnosticResult.cpu_metrics,
          memory_status: diagnosticResult.memory_status,
          memory_metrics: diagnosticResult.memory_metrics,
          disk_status: diagnosticResult.disk_status,
          disk_metrics: diagnosticResult.disk_metrics,
          network_status: diagnosticResult.network_status,
          network_metrics: diagnosticResult.network_metrics,
          health_score: diagnosticResult.health_score,
          raw_data: diagnosticResult.raw_data,
        });

        // 5. Atualizar último diagnóstico do dispositivo
        await this.updateDevice(deviceId, {});
        await supabase
          .from('devices')
          .update({ last_diagnostic_id: updatedDiagnostic.id })
          .eq('id', deviceId);

        return updatedDiagnostic;

      } catch (apiError) {
        console.error("Erro no microserviço:", apiError);
        
        // Atualizar diagnóstico com erro
        const failedDiagnostic = await this.updateDiagnostic(initialDiagnostic.id, {
          status: 'failed',
          error_message: apiError instanceof Error ? apiError.message : 'Erro desconhecido no microserviço',
        });

        return failedDiagnostic;
      }

    } catch (error) {
      console.error("Erro no diagnóstico completo:", error);
      throw error;
    }
  }
}

export const diagnosticApiService = new DiagnosticApiService();
