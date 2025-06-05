
import { supabase } from '@/integrations/supabase/client';

export class MultiTenantService {
  private static instance: MultiTenantService;
  private currentTenant: string | null = null;

  static getInstance(): MultiTenantService {
    if (!MultiTenantService.instance) {
      MultiTenantService.instance = new MultiTenantService();
    }
    return MultiTenantService.instance;
  }

  async initializeTenant(companyId: string): Promise<void> {
    this.currentTenant = companyId;
    
    // Configure Supabase RLS context
    await supabase.rpc('set_current_company', { company_id: companyId });
    
    console.log(`Tenant inicializado: ${companyId}`);
  }

  getCurrentTenant(): string | null {
    return this.currentTenant;
  }

  async switchTenant(companyId: string): Promise<void> {
    await this.initializeTenant(companyId);
  }

  clearTenant(): void {
    this.currentTenant = null;
  }
}

export const multiTenantService = MultiTenantService.getInstance();
