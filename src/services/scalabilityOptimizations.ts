
import { supabase } from '@/integrations/supabase/client';
import { cacheService } from './cacheService';

// Otimizações de queries para grandes volumes
export class QueryOptimizer {
  
  // Paginação otimizada com cursor
  static async getPaginatedDiagnostics(
    companyId: string,
    limit = 20,
    cursor?: string
  ) {
    let query = supabase
      .from('diagnostics')
      .select(`
        id,
        status,
        health_score,
        created_at,
        device:devices(name, type)
      `)
      .eq('user_id', companyId)
      .order('created_at', { ascending: false })
      .limit(limit);

    if (cursor) {
      query = query.lt('created_at', cursor);
    }

    return query;
  }

  // Agregações otimizadas
  static async getDashboardStats(companyId: string) {
    const cacheKey = `dashboard_stats_${companyId}`;
    
    return cacheService.get(cacheKey) || await cacheService.set(
      cacheKey,
      await this.calculateDashboardStats(companyId),
      300 // 5 minutos
    );
  }

  private static async calculateDashboardStats(companyId: string) {
    const { data, error } = await supabase
      .rpc('get_dashboard_stats', { company_id: companyId });

    if (error) throw error;
    return data;
  }

  // Busca otimizada com índices
  static async searchDiagnostics(
    companyId: string,
    searchTerm: string,
    filters: Record<string, any> = {}
  ) {
    let query = supabase
      .from('diagnostics')
      .select(`
        id,
        status,
        health_score,
        created_at,
        device:devices!inner(name, type)
      `)
      .eq('user_id', companyId);

    // Aplicar filtros dinamicamente
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== '') {
        query = query.eq(key, value);
      }
    });

    // Busca textual otimizada
    if (searchTerm) {
      query = query.or(`device.name.ilike.%${searchTerm}%,device.type.ilike.%${searchTerm}%`);
    }

    return query.order('created_at', { ascending: false });
  }
}

// Gerenciamento de estado distribuído
export class StateManager {
  private static instance: StateManager;
  private subscribers = new Map<string, Set<(data: any) => void>>();

  static getInstance() {
    if (!StateManager.instance) {
      StateManager.instance = new StateManager();
    }
    return StateManager.instance;
  }

  // Pub/Sub para sincronização entre abas
  subscribe(channel: string, callback: (data: any) => void) {
    if (!this.subscribers.has(channel)) {
      this.subscribers.set(channel, new Set());
    }
    this.subscribers.get(channel)!.add(callback);

    // Escutar mudanças do localStorage para sincronizar entre abas
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === `state_${channel}` && e.newValue) {
        callback(JSON.parse(e.newValue));
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      this.subscribers.get(channel)?.delete(callback);
      window.removeEventListener('storage', handleStorageChange);
    };
  }

  publish(channel: string, data: any) {
    // Notificar subscribers locais
    this.subscribers.get(channel)?.forEach(callback => callback(data));

    // Sincronizar com outras abas
    localStorage.setItem(`state_${channel}`, JSON.stringify(data));

    // Limpar após propagação
    setTimeout(() => {
      localStorage.removeItem(`state_${channel}`);
    }, 100);
  }
}

// Otimização de recursos
export class ResourceOptimizer {
  private static imageCache = new Map<string, string>();

  // Lazy loading de imagens com cache
  static async loadImage(src: string): Promise<string> {
    if (this.imageCache.has(src)) {
      return this.imageCache.get(src)!;
    }

    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        this.imageCache.set(src, src);
        resolve(src);
      };
      img.onerror = reject;
      img.src = src;
    });
  }

  // Prefetch de rotas críticas
  static prefetchRoute(route: string) {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = route;
    document.head.appendChild(link);
  }

  // Cleanup de recursos não utilizados
  static cleanup() {
    // Limpar cache de imagens antigas
    if (this.imageCache.size > 100) {
      const entries = Array.from(this.imageCache.entries());
      entries.slice(0, 50).forEach(([key]) => {
        this.imageCache.delete(key);
      });
    }

    // Forçar garbage collection se disponível
    if ('gc' in window) {
      (window as any).gc();
    }
  }
}

export const stateManager = StateManager.getInstance();
