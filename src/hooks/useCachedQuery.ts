
import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { getCachedData, cacheService } from '../services/cacheService';

interface CachedQueryOptions<T> extends Omit<UseQueryOptions<T>, 'queryFn'> {
  fetchFn: () => Promise<T>;
  cacheKey: string;
  ttl?: number;
  useMemoryCache?: boolean;
}

export const useCachedQuery = <T>({
  fetchFn,
  cacheKey,
  ttl = 3600,
  useMemoryCache = false,
  ...queryOptions
}: CachedQueryOptions<T>) => {
  return useQuery({
    ...queryOptions,
    queryFn: () => getCachedData(cacheKey, fetchFn, ttl, useMemoryCache),
    staleTime: ttl * 1000, // React Query considera fresh por TTL
    gcTime: ttl * 1000 * 2, // Manter em cache por 2x TTL
  });
};

// Hook específico para dados de diagnósticos
export const useCachedDiagnostics = (companyId: string, userId: string) => {
  return useCachedQuery({
    queryKey: ['diagnostics', companyId, userId],
    cacheKey: `diagnostics_${companyId}_${userId}`,
    fetchFn: async () => {
      // Implementar busca real dos diagnósticos
      const response = await fetch(`/api/diagnostics?company=${companyId}&user=${userId}`);
      return response.json();
    },
    ttl: 300, // 5 minutos para dados frequentes
  });
};

// Hook para invalidar cache quando dados mudam
export const useInvalidateCache = () => {
  return {
    invalidateDiagnostics: (companyId: string) => {
      cacheService.invalidatePattern(`diagnostics_${companyId}*`);
    },
    invalidateReports: (companyId: string) => {
      cacheService.invalidatePattern(`reports_${companyId}*`);
    },
    invalidateUserData: (userId: string) => {
      cacheService.invalidatePattern(`*_${userId}`);
    }
  };
};
