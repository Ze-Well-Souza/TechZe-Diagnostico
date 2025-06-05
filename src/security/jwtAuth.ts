
/**
 * Sistema de autenticação JWT multi-tenant
 */

import { supabase } from '@/integrations/supabase/client';
import { multiTenantService } from '@/services/multiTenantService';

export interface JWTClaims {
  sub: string; // user_id
  email: string;
  company_id: string;
  role: string;
  store_id?: string;
  permissions: string[];
  iat: number;
  exp: number;
}

export class JWTAuthService {
  private static instance: JWTAuthService;

  static getInstance(): JWTAuthService {
    if (!JWTAuthService.instance) {
      JWTAuthService.instance = new JWTAuthService();
    }
    return JWTAuthService.instance;
  }

  async authenticateWithCompany(email: string, password: string, companyCode: string) {
    try {
      // 1. Autenticar usuário
      const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
        email,
        password
      });

      if (authError) throw authError;

      // 2. Verificar se usuário tem acesso à empresa
      const { data: companyUser, error: companyError } = await supabase
        .from('company_users')
        .select(`
          *,
          company:companies(*)
        `)
        .eq('user_id', authData.user.id)
        .eq('companies.code', companyCode)
        .eq('is_active', true)
        .single();

      if (companyError || !companyUser) {
        throw new Error('Usuário não tem acesso a esta empresa');
      }

      // 3. Inicializar contexto do tenant
      await multiTenantService.initializeTenant(companyUser.company_id);

      // 4. Atualizar empresa atual do usuário
      await supabase
        .from('profiles')
        .update({ current_company_id: companyUser.company_id })
        .eq('id', authData.user.id);

      return {
        user: authData.user,
        company: companyUser.company,
        role: companyUser.role
      };

    } catch (error) {
      console.error('Erro na autenticação multi-tenant:', error);
      throw error;
    }
  }

  async getCurrentUserClaims(): Promise<JWTClaims | null> {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return null;

      const { data: profile } = await supabase
        .from('profiles')
        .select(`
          *,
          company_users!inner(
            role,
            company:companies(*)
          )
        `)
        .eq('id', user.id)
        .eq('company_users.company_id', 'current_company_id')
        .single();

      if (!profile) return null;

      return {
        sub: user.id,
        email: user.email!,
        company_id: profile.current_company_id,
        role: profile.company_users[0]?.role || 'tecnico',
        store_id: profile.store_id,
        permissions: this.getRolePermissions(profile.company_users[0]?.role || 'tecnico'),
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60) // 24 horas
      };

    } catch (error) {
      console.error('Erro ao obter claims do usuário:', error);
      return null;
    }
  }

  private getRolePermissions(role: string): string[] {
    const permissions: Record<string, string[]> = {
      'admin': ['*'], // Todas as permissões
      'gerente': ['diagnostics:read', 'diagnostics:write', 'reports:read', 'users:read'],
      'tecnico': ['diagnostics:read', 'diagnostics:write', 'reports:read'],
      'suporte': ['diagnostics:read', 'reports:read']
    };

    return permissions[role] || ['diagnostics:read'];
  }

  hasPermission(claims: JWTClaims, permission: string): boolean {
    if (claims.permissions.includes('*')) return true;
    return claims.permissions.includes(permission);
  }
}

export const jwtAuthService = JWTAuthService.getInstance();
