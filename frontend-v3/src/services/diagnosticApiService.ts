import { DiagnosticResult, Device, CreateDeviceRequest } from '../types/diagnostic';
import { supabase } from "../integrations/supabase/client";
import { apiClient } from "../services/apiClient";
import { Json } from "../integrations/supabase/types";

// Configuração da API
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class DiagnosticApiService {
  // Helper function para converter tipos Supabase para nossos tipos
  private convertSupabaseToDiagnostic(data: any): DiagnosticResult {
    return {
      ...data,
      status: data.status as 'pending' | 'running' | 'completed' | 'failed',
      cpu_metrics: data.cpu_metrics as any,
      memory_metrics: data.memory_metrics as any,
      disk_metrics: data.disk_metrics as any,
      network_metrics: data.network_metrics as any,
      antivirus_metrics: data.antivirus_metrics as any,
      driver_metrics: data.driver_metrics as any,
    };
  }

  // Helper function para converter nossos tipos para Supabase
  private convertDiagnosticToSupabase(data: Partial<DiagnosticResult>): any {
    return {
      ...data,
      cpu_metrics: data.cpu_metrics ? (data.cpu_metrics as unknown as Json) : null,
      memory_metrics: data.memory_metrics ? (data.memory_metrics as unknown as Json) : null,
      disk_metrics: data.disk_metrics ? (data.disk_metrics as unknown as Json) : null,
      network_metrics: data.network_metrics ? (data.network_metrics as unknown as Json) : null,
      antivirus_metrics: data.antivirus_metrics ? (data.antivirus_metrics as unknown as Json) : null,
      driver_metrics: data.driver_metrics ? (data.driver_metrics as unknown as Json) : null,
    };
  }

  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Métodos para diagnósticos via microserviço
  async runDiagnostic(request: any): Promise<DiagnosticResult> {
    console.log("Iniciando diagnóstico via microserviço:", request);
    try {
      return await apiClient.post<DiagnosticResult>("/api/v1/diagnostics", request);
    } catch (error) {
      console.error("Erro ao executar diagnóstico via API:", error);
      throw error;
    }
  }

  async getDiagnosticStatus(diagnosticId: string): Promise<DiagnosticResult> {
    console.log("Consultando status do diagnóstico:", diagnosticId);
    try {
      return await apiClient.get<DiagnosticResult>(`/api/v1/diagnostics/${diagnosticId}`);
    } catch (error) {
      console.error("Erro ao consultar status do diagnóstico:", error);
      throw error;
    }
  }

  // Método para obter todos os diagnósticos
  async getDiagnostics(): Promise<DiagnosticResult[]> {
    try {
      // Primeiro tenta obter via API
      try {
        return await apiClient.get<DiagnosticResult[]>("/api/v1/diagnostics");
      } catch (apiError) {
        console.warn("API não disponível, usando Supabase como fallback", apiError);
        
        // Fallback para Supabase
        const { data, error } = await supabase
          .from('diagnostics')
          .select('*')
          .order('created_at', { ascending: false });

        if (error) {
          console.error("Erro ao buscar diagnósticos:", error);
          throw new Error(error.message);
        }

        return (data || []).map(this.convertSupabaseToDiagnostic);
      }
    } catch (error) {
      console.error("Erro ao obter diagnósticos:", error);
      
      // Se tudo falhar, retorna dados mockados para desenvolvimento
      return [
        {
          id: 'diag-1',
          device_id: 'device-1',
          status: 'completed',
          health_score: 85,
          issues_found: [
            { category: 'performance', severity: 'medium', description: 'CPU usage high' }
          ],
          recommendations: ['Close unnecessary programs'],
          execution_time: 45.2,
          created_at: new Date(Date.now() - 86400000).toISOString(), // 1 dia atrás
          updated_at: new Date(Date.now() - 86400000).toISOString(),
          user_id: 'user-1'
        },
        {
          id: 'diag-2',
          device_id: 'device-2',
          status: 'completed',
          health_score: 92,
          issues_found: [],
          recommendations: ['System is running optimally'],
          execution_time: 32.1,
          created_at: new Date(Date.now() - 172800000).toISOString(), // 2 dias atrás
          updated_at: new Date(Date.now() - 172800000).toISOString(),
          user_id: 'user-1'
        }
      ];
    }
  }

  // Método para obter um diagnóstico específico
  async getDiagnostic(id: string): Promise<DiagnosticResult | null> {
    try {
      // Primeiro tenta obter via API
      try {
        return await apiClient.get<DiagnosticResult>(`/api/v1/diagnostics/${id}`);
      } catch (apiError) {
        console.warn(`API não disponível para diagnóstico ${id}, usando Supabase como fallback`, apiError);
        
        // Fallback para Supabase
        const { data, error } = await supabase
          .from('diagnostics')
          .select('*')
          .eq('id', id)
          .maybeSingle();

        if (error) {
          console.error("Erro ao buscar diagnóstico:", error);
          throw new Error(error.message);
        }

        return data ? this.convertSupabaseToDiagnostic(data) : null;
      }
    } catch (error) {
      console.error(`Erro ao obter diagnóstico ${id}:`, error);
      
      // Se tudo falhar, retorna dados mockados para desenvolvimento
      return {
        id,
        device_id: 'device-1',
        status: 'completed',
        health_score: 85,
        issues_found: [
          { category: 'performance', severity: 'medium', description: 'CPU usage high' }
        ],
        recommendations: ['Close unnecessary programs'],
        execution_time: 45.2,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        user_id: 'user-1'
      };
    }
  }

  // Método para obter histórico de diagnósticos
  async getDiagnosticHistory(params?: {
    page?: number;
    limit?: number;
    device_id?: string;
    status?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<{ data: DiagnosticResult[]; total: number; page: number; limit: number; pages: number }> {
    try {
      // Primeiro tentamos obter do endpoint específico de histórico
      try {
        const searchParams = new URLSearchParams();
        
        if (params?.page) searchParams.append('page', params.page.toString());
        if (params?.limit) searchParams.append('limit', params.limit.toString());
        if (params?.device_id) searchParams.append('device_id', params.device_id);
        if (params?.status) searchParams.append('status', params.status);
        if (params?.start_date) searchParams.append('start_date', params.start_date);
        if (params?.end_date) searchParams.append('end_date', params.end_date);

        const endpoint = `/api/v1/diagnostic/history/?${searchParams.toString()}`;
        return await this.makeRequest<{ data: DiagnosticResult[]; total: number; page: number; limit: number; pages: number }>(endpoint);
      } catch (apiError) {
        console.warn("Endpoint de histórico não disponível, usando fallback para Supabase", apiError);
        
        // Fallback: Se o endpoint não estiver disponível, usamos o Supabase diretamente
        let query = supabase.from('diagnostics').select('*', { count: 'exact' });
        
        // Aplicar filtros se fornecidos
        if (params?.device_id) {
          query = query.eq('device_id', params.device_id);
        }
        
        if (params?.status) {
          query = query.eq('status', params.status);
        }
        
        if (params?.start_date) {
          query = query.gte('created_at', params.start_date);
        }
        
        if (params?.end_date) {
          query = query.lte('created_at', params.end_date);
        }
        
        // Aplicar paginação
        const page = params?.page || 1;
        const limit = params?.limit || 10;
        const start = (page - 1) * limit;
        
        query = query.order('created_at', { ascending: false })
                     .range(start, start + limit - 1);
        
        const { data, error, count } = await query;
        
        if (error) {
          console.error("Erro ao buscar histórico de diagnósticos:", error);
          throw new Error(error.message);
        }
        
        return {
          data: (data || []).map(this.convertSupabaseToDiagnostic),
          total: count || 0,
          page,
          limit,
          pages: Math.ceil((count || 0) / limit)
        };
      }
    } catch (error) {
      console.error("Erro ao obter histórico de diagnósticos:", error);
      throw error;
    }
  }

  // Método para executar diagnóstico completo
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
        // Tentar usar o endpoint /api/v1/diagnostic/full se disponível
        let diagnosticResult;
        try {
          diagnosticResult = await apiClient.post<DiagnosticResult>(`/api/v1/diagnostic/full`, {
            device_id: deviceId,
            diagnostic_id: initialDiagnostic.id,
            system_info: {
              os: device.os || 'Unknown',
              os_version: device.os_version || 'Unknown',
              processor: device.processor || 'Unknown',
              ram: device.ram || 'Unknown',
              storage: device.storage || 'Unknown',
            }
          });
        } catch (fullEndpointError) {
          console.warn("Endpoint /api/v1/diagnostic/full não disponível, usando fallback", fullEndpointError);
          // Fallback para o endpoint padrão
          diagnosticResult = await this.runDiagnostic({
            device_id: deviceId,
            system_info: {
              os: device.os || 'Unknown',
              os_version: device.os_version || 'Unknown',
              processor: device.processor || 'Unknown',
              ram: device.ram || 'Unknown',
              storage: device.storage || 'Unknown',
            }
          });
        }

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
      
      // Se tudo falhar, retorna dados mockados para desenvolvimento
      const mockResult: DiagnosticResult = {
        id: `diag-${Date.now()}`,
        device_id: deviceId,
        status: 'completed',
        health_score: Math.floor(Math.random() * 40) + 60, // Score entre 60-100
        issues_found: [
          { category: 'performance', severity: 'low', description: 'Temporary files detected' },
          { category: 'security', severity: 'medium', description: 'Windows updates pending' }
        ],
        recommendations: [
          'Clean temporary files',
          'Install pending Windows updates',
          'Run disk cleanup'
        ],
        execution_time: Math.random() * 60 + 30, // Entre 30-90 segundos
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        user_id: 'user-1'
      };

      return mockResult;
    }
  }

  // Método alternativo para compatibilidade
  async runFullDiagnostic(data: {
    device_id?: string;
    system_info?: any;
  }): Promise<DiagnosticResult> {
    return this.executeFullDiagnostic(data.device_id || 'default-device');
  }

  // Métodos para dispositivos via Supabase
  async getDevices(): Promise<Device[]> {
    try {
      const { data, error } = await supabase
        .from('devices')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) {
        console.error("Erro ao buscar dispositivos:", error);
        throw new Error(error.message);
      }

      return data || [];
    } catch (error) {
      console.error("Erro ao obter dispositivos:", error);
      
      // Dados mockados para desenvolvimento
      return [
        {
          id: 'device-1',
          name: 'Computador Principal',
          type: 'desktop',
          os: 'Windows 11',
          created_at: new Date(Date.now() - 86400000 * 7).toISOString(), // 7 dias atrás
          updated_at: new Date().toISOString(),
          user_id: 'user-1'
        },
        {
          id: 'device-2',
          name: 'Laptop Trabalho',
          type: 'laptop',
          os: 'Windows 10',
          created_at: new Date(Date.now() - 86400000 * 14).toISOString(), // 14 dias atrás
          updated_at: new Date().toISOString(),
          user_id: 'user-1'
        }
      ];
    }
  }

  async getDevice(deviceId: string): Promise<Device | null> {
    try {
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
    } catch (error) {
      console.error(`Erro ao obter dispositivo ${deviceId}:`, error);
      return null;
    }
  }

  async createDevice(device: CreateDeviceRequest): Promise<Device> {
    try {
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
    } catch (error) {
      console.error("Erro ao criar dispositivo:", error);
      
      // Simular criação de dispositivo para desenvolvimento
      const newDevice: Device = {
        id: `device-${Date.now()}`,
        name: device.name,
        type: device.type,
        os: device.os || 'Unknown',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        user_id: 'user-1'
      };

      return newDevice;
    }
  }

  async updateDevice(deviceId: string, updates: Partial<CreateDeviceRequest>): Promise<Device> {
    try {
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
    } catch (error) {
      console.error(`Erro ao atualizar dispositivo ${deviceId}:`, error);
      throw error;
    }
  }

  async deleteDevice(deviceId: string): Promise<{ success: boolean }> {
    try {
      const { error } = await supabase
        .from('devices')
        .delete()
        .eq('id', deviceId);

      if (error) {
        console.error("Erro ao excluir dispositivo:", error);
        throw new Error(error.message);
      }

      return { success: true };
    } catch (error) {
      console.error(`Erro ao excluir dispositivo ${deviceId}:`, error);
      
      // Simular deleção para desenvolvimento
      return { success: true };
    }
  }

  // Métodos para diagnósticos via Supabase
  async saveDiagnostic(diagnostic: Partial<DiagnosticResult>): Promise<DiagnosticResult> {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      
      if (!user) {
        throw new Error("Usuário não autenticado");
      }

      const supabaseData = this.convertDiagnosticToSupabase({
        ...diagnostic,
        user_id: user.id,
      });

      const { data, error } = await supabase
        .from('diagnostics')
        .insert(supabaseData)
        .select()
        .single();

      if (error) {
        console.error("Erro ao salvar diagnóstico:", error);
        throw new Error(error.message);
      }

      return this.convertSupabaseToDiagnostic(data);
    } catch (error) {
      console.error("Erro ao salvar diagnóstico:", error);
      throw error;
    }
  }

  async updateDiagnostic(diagnosticId: string, updates: Partial<DiagnosticResult>): Promise<DiagnosticResult> {
    try {
      const supabaseData = this.convertDiagnosticToSupabase(updates);

      const { data, error } = await supabase
        .from('diagnostics')
        .update(supabaseData)
        .eq('id', diagnosticId)
        .select()
        .single();

      if (error) {
        console.error("Erro ao atualizar diagnóstico:", error);
        throw new Error(error.message);
      }

      return this.convertSupabaseToDiagnostic(data);
    } catch (error) {
      console.error(`Erro ao atualizar diagnóstico ${diagnosticId}:`, error);
      throw error;
    }
  }

  // Método para verificar saúde da API
  async checkHealth(): Promise<{ status: string; message: string }> {
    try {
      return await this.makeRequest<{ status: string; message: string }>('/health');
    } catch (error) {
      console.error("Erro ao verificar saúde da API:", error);
      return { status: "error", message: "API não disponível" };
    }
  }
}

export const diagnosticApiService = new DiagnosticApiService();
export default diagnosticApiService;