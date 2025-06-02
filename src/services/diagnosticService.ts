
import { supabase } from "@/integrations/supabase/client";
import { diagnosticApiService } from "./diagnosticApiService";

// Re-export tudo do novo serviço para manter compatibilidade
export * from "./diagnosticApiService";

// Mantém a exportação padrão para compatibilidade
export default diagnosticApiService;

// Funções legacy que podem ser utilizadas por outros componentes
export const getDiagnostics = () => diagnosticApiService.getDiagnostics();
export const getDiagnostic = (id: string) => diagnosticApiService.getDiagnostic(id);
export const createDiagnostic = (data: any) => diagnosticApiService.saveDiagnostic(data);
export const runDiagnostic = (deviceId: string) => diagnosticApiService.executeFullDiagnostic(deviceId);
