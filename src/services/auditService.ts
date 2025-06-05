
import { supabase } from '@/integrations/supabase/client';

export interface AuditLog {
  id: string;
  user_id: string;
  company_id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  details: any;
  ip_address: string;
  user_agent: string;
  created_at: string;
}

export class AuditService {
  static async logAction(
    action: string,
    resourceType: string,
    resourceId: string,
    details: any = {}
  ): Promise<void> {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      const { data: profile } = await supabase
        .from('profiles')
        .select('current_company_id')
        .eq('id', user.id)
        .single();

      await supabase.from('audit_logs').insert({
        user_id: user.id,
        company_id: profile?.current_company_id,
        action,
        resource_type: resourceType,
        resource_id: resourceId,
        details,
        ip_address: await this.getClientIP(),
        user_agent: navigator.userAgent
      });

      console.log(`Audit log: ${action} on ${resourceType}:${resourceId}`);
    } catch (error) {
      console.error('Erro ao registrar log de auditoria:', error);
    }
  }

  private static async getClientIP(): Promise<string> {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return data.ip;
    } catch {
      return 'unknown';
    }
  }

  static async getAuditLogs(filters: {
    startDate?: string;
    endDate?: string;
    userId?: string;
    action?: string;
    resourceType?: string;
  } = {}): Promise<AuditLog[]> {
    let query = supabase
      .from('audit_logs')
      .select('*')
      .order('created_at', { ascending: false });

    if (filters.startDate) {
      query = query.gte('created_at', filters.startDate);
    }

    if (filters.endDate) {
      query = query.lte('created_at', filters.endDate);
    }

    if (filters.userId) {
      query = query.eq('user_id', filters.userId);
    }

    if (filters.action) {
      query = query.eq('action', filters.action);
    }

    if (filters.resourceType) {
      query = query.eq('resource_type', filters.resourceType);
    }

    const { data, error } = await query;

    if (error) {
      console.error('Erro ao buscar logs de auditoria:', error);
      throw error;
    }

    return data || [];
  }
}
