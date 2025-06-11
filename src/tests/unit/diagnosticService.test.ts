
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { diagnosticApiService } from '@/services/diagnosticApiService';

// Mock do apiClient
vi.mock('@/services/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}));

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

// Mock do multiTenantService
vi.mock('@/services/multiTenantService', () => ({
  multiTenantService: {
    initializeTenant: vi.fn(),
    getCurrentTenant: vi.fn(() => 'company-123')
  }
}));

describe('DiagnosticApiService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Basic functionality', () => {
    it('should be defined', () => {
      expect(diagnosticApiService).toBeDefined();
    });

    it('should have required methods', () => {
      expect(typeof diagnosticApiService.runDiagnostic).toBe('function');
      expect(typeof diagnosticApiService.getDiagnosticStatus).toBe('function');
    });
  });

  describe('runDiagnostic', () => {
    it('should call API with correct parameters', async () => {
      const mockResponse = {
        id: '123',
        status: 'completed' as const,
        device_id: 'device-123',
        health_score: 85,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const { apiClient } = await import('@/services/apiClient');
      vi.mocked(apiClient.post).mockResolvedValueOnce(mockResponse);

      const diagnosticData = {
        device_id: 'device-123',
        user_id: 'user-123'
      };

      const result = await diagnosticApiService.runDiagnostic(diagnosticData);
      expect(result.id).toBe('123');
      expect(result.status).toBe('completed');
      expect(apiClient.post).toHaveBeenCalledWith('/api/v1/diagnostics', diagnosticData);
    });
  });
});
