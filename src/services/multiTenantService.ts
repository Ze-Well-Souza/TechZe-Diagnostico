
import { supabase } from '@/integrations/supabase/client';
import { getCachedData, cacheService } from './cacheService';

export interface TenantContext {
  companyId: string;
  companyName: string;
  features: string[];
  limits: {
    maxUsers: number;
    maxDiagnostics: number;
    storageLimit: number;
  };
  theme: {
    primaryColor: string;
    logoUrl?: string;
  };
}

class MultiTenantService {
  private currentTenant: TenantContext | null = null;

  async initializeTenant(companyId: string): Promise<TenantContext> {
    const cacheKey = `tenant_${companyId}`;
    
    const tenantData = await getCachedData(
      cacheKey,
      async () => {
        const { data, error } = await supabase
          .from('companies')
          .select(`
            id,
            name,
            primary_color,
            logo_url,
            code
          `)
          .eq('id', companyId)
          .single();

        if (error) throw error;

        // Buscar limites e features da empresa
        const features = await this.getCompanyFeatures(companyId);
        const limits = await this.getCompanyLimits(companyId);

        return {
          companyId: data.id,
          companyName: data.name,
          features,
          limits,
          theme: {
            primaryColor: data.primary_color || '#f97316',
            logoUrl: data.logo_url
          }
        };
      },
      3600 // Cache por 1 hora
    );

    this.currentTenant = tenantData;
    return tenantData;
  }

  private async getCompanyFeatures(companyId: string): Promise<string[]> {
    // Por enquanto, features baseadas no código da empresa
    const { data } = await supabase
      .from('companies')
      .select('code')
      .eq('id', companyId)
      .single();

    const featureMap: Record<string, string[]> = {
      'ulytech': ['diagnostics', 'reports', 'marketplace', 'whatsapp'],
      'utilimix': ['diagnostics', 'reports', 'whatsapp'],
      'useprint': ['diagnostics', 'reports', 'file-conversion']
    };

    return featureMap[data?.code?.toLowerCase()] || ['diagnostics', 'reports'];
  }

  private async getCompanyLimits(companyId: string): Promise<TenantContext['limits']> {
    // Limites baseados no plano da empresa
    return {
      maxUsers: 50,
      maxDiagnostics: 1000,
      storageLimit: 5 * 1024 * 1024 * 1024 // 5GB
    };
  }

  getCurrentTenant(): TenantContext | null {
    return this.currentTenant;
  }

  hasFeature(feature: string): boolean {
    return this.currentTenant?.features.includes(feature) || false;
  }

  async switchTenant(companyId: string): Promise<void> {
    // Limpar cache do tenant anterior
    if (this.currentTenant) {
      await cacheService.invalidatePattern(`*${this.currentTenant.companyId}*`);
    }

    // Inicializar novo tenant
    await this.initializeTenant(companyId);

    // Atualizar tema da aplicação
    this.applyTenantTheme();
  }

  private applyTenantTheme(): void {
    if (!this.currentTenant) return;

    const root = document.documentElement;
    root.style.setProperty('--primary-color', this.currentTenant.theme.primaryColor);
    
    // Atualizar favicon se houver logo personalizada
    if (this.currentTenant.theme.logoUrl) {
      const favicon = document.querySelector('link[rel="icon"]') as HTMLLinkElement;
      if (favicon) {
        favicon.href = this.currentTenant.theme.logoUrl;
      }
    }
  }

  // Middleware para queries específicas do tenant
  async executeWithTenantContext<T>(
    operation: (tenantId: string) => Promise<T>
  ): Promise<T> {
    if (!this.currentTenant) {
      throw new Error('Nenhum tenant ativo. Faça login primeiro.');
    }

    return operation(this.currentTenant.companyId);
  }
}

export const multiTenantService = new MultiTenantService();

// Hook para usar o contexto do tenant
export const useTenantContext = () => {
  return multiTenantService.getCurrentTenant();
};

// Hook para verificar features
export const useFeatureFlag = (feature: string) => {
  return multiTenantService.hasFeature(feature);
};
