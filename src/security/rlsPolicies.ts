
/**
 * Configurações centralizadas de Row Level Security (RLS) para Multi-Tenancy
 */

export interface RLSPolicy {
  table: string;
  operation: 'SELECT' | 'INSERT' | 'UPDATE' | 'DELETE';
  policy: string;
  condition: string;
}

export const MULTI_TENANT_RLS_POLICIES: RLSPolicy[] = [
  // Políticas para dispositivos
  {
    table: 'devices',
    operation: 'SELECT',
    policy: 'Usuários podem ver apenas dispositivos da sua loja',
    condition: `
      EXISTS (
        SELECT 1 FROM public.profiles p
        WHERE p.id = auth.uid() 
        AND p.current_company_id = devices.company_id
      )
    `
  },
  {
    table: 'devices',
    operation: 'INSERT',
    policy: 'Usuários podem criar dispositivos apenas na sua loja',
    condition: `
      (SELECT current_company_id FROM public.profiles WHERE id = auth.uid()) = company_id
    `
  },
  
  // Políticas para diagnósticos
  {
    table: 'diagnostics',
    operation: 'SELECT',
    policy: 'Usuários podem ver apenas diagnósticos da sua loja',
    condition: `
      EXISTS (
        SELECT 1 FROM public.devices d, public.profiles p
        WHERE d.id = diagnostics.device_id 
        AND p.id = auth.uid()
        AND p.current_company_id = d.company_id
      )
    `
  },
  
  // Políticas para relatórios
  {
    table: 'reports',
    operation: 'SELECT',
    policy: 'Usuários podem ver apenas relatórios da sua loja',
    condition: `
      EXISTS (
        SELECT 1 FROM public.diagnostics diag, public.devices d, public.profiles p
        WHERE reports.diagnostic_id = diag.id
        AND diag.device_id = d.id
        AND p.id = auth.uid()
        AND p.current_company_id = d.company_id
      )
    `
  }
];

export const generateRLSSQL = (policies: RLSPolicy[]): string => {
  return policies.map(policy => `
-- ${policy.policy}
CREATE POLICY "${policy.policy.toLowerCase().replace(/\s+/g, '_')}"
  ON public.${policy.table}
  FOR ${policy.operation}
  USING (${policy.condition});
  `).join('\n');
};
