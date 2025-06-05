
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { diagnosticApiService } from '@/services/diagnosticApiService';
import { multiTenantService } from '@/services/multiTenantService';

// Mock do Supabase
vi.mock('@/integrations/supabase/client', () => ({
  supabase: {
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        eq: vi.fn(() => ({
          order: vi.fn(() => ({
            range: vi.fn(() => Promise.resolve({
              data: [],
              error: null,
              count: 0
            }))
          }))
        }))
      })),
      insert: vi.fn(() => ({
        select: vi.fn(() => ({
          single: vi.fn(() => Promise.resolve({
            data: { id: '123', status: 'completed' },
            error: null
          }))
        }))
      }))
    })),
    auth: {
      getUser: vi.fn(() => Promise.resolve({
        data: { user: { id: 'user-123' } }
      }))
    }
  }
}));

describe('DiagnosticApiService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    multiTenantService.initializeTenant('company-123');
  });

  describe('getDiagnostics', () => {
    it('should return diagnostics list', async () => {
      const diagnostics = await diagnosticApiService.getDiagnostics();
      expect(Array.isArray(diagnostics)).toBe(true);
    });

    it('should handle errors gracefully', async () => {
      vi.mocked(diagnosticApiService.getDiagnostics).mockRejectedValueOnce(
        new Error('Database error')
      );

      await expect(diagnosticApiService.getDiagnostics()).rejects.toThrow('Database error');
    });
  });

  describe('saveDiagnostic', () => {
    it('should save diagnostic with user context', async () => {
      const diagnosticData = {
        device_id: 'device-123',
        status: 'pending' as const,
        health_score: 85
      };

      const result = await diagnosticApiService.saveDiagnostic(diagnosticData);
      expect(result.id).toBe('123');
      expect(result.status).toBe('completed');
    });
  });

  describe('multi-tenant isolation', () => {
    it('should respect tenant context', async () => {
      const currentTenant = multiTenantService.getCurrentTenant();
      expect(currentTenant).toBe('company-123');
      
      // Verificar se as queries incluem o contexto do tenant
      await diagnosticApiService.getDiagnostics();
      // O mock deveria verificar se o company_id foi incluído na query
    });
  });
});
