
import { createClient } from 'redis';

interface CacheService {
  get<T>(key: string): Promise<T | null>;
  set(key: string, value: any, ttl?: number): Promise<void>;
  del(key: string): Promise<void>;
  invalidatePattern(pattern: string): Promise<void>;
}

class RedisCacheService implements CacheService {
  private client;
  private connected = false;

  constructor() {
    // Conectar apenas se Redis estiver disponível
    if (import.meta.env.VITE_REDIS_URL) {
      this.client = createClient({
        url: import.meta.env.VITE_REDIS_URL
      });
      this.connect();
    }
  }

  private async connect() {
    try {
      if (this.client && !this.connected) {
        await this.client.connect();
        this.connected = true;
        console.log('🚀 Redis cache conectado');
      }
    } catch (error) {
      console.warn('⚠️ Redis não disponível, usando cache local');
    }
  }

  async get<T>(key: string): Promise<T | null> {
    try {
      if (this.client && this.connected) {
        const value = await this.client.get(key);
        return value ? JSON.parse(value) : null;
      }
      // Fallback para localStorage
      const value = localStorage.getItem(`cache_${key}`);
      return value ? JSON.parse(value) : null;
    } catch (error) {
      console.error('Erro ao buscar cache:', error);
      return null;
    }
  }

  async set(key: string, value: any, ttl = 3600): Promise<void> {
    try {
      const serialized = JSON.stringify(value);
      
      if (this.client && this.connected) {
        await this.client.setEx(key, ttl, serialized);
      } else {
        // Fallback para localStorage com TTL simulado
        const item = {
          value: serialized,
          expiry: Date.now() + (ttl * 1000)
        };
        localStorage.setItem(`cache_${key}`, JSON.stringify(item));
      }
    } catch (error) {
      console.error('Erro ao salvar cache:', error);
    }
  }

  async del(key: string): Promise<void> {
    try {
      if (this.client && this.connected) {
        await this.client.del(key);
      } else {
        localStorage.removeItem(`cache_${key}`);
      }
    } catch (error) {
      console.error('Erro ao deletar cache:', error);
    }
  }

  async invalidatePattern(pattern: string): Promise<void> {
    try {
      if (this.client && this.connected) {
        const keys = await this.client.keys(pattern);
        if (keys.length > 0) {
          await this.client.del(keys);
        }
      } else {
        // Limpar localStorage baseado no padrão
        Object.keys(localStorage)
          .filter(key => key.startsWith(`cache_`) && key.includes(pattern.replace('*', '')))
          .forEach(key => localStorage.removeItem(key));
      }
    } catch (error) {
      console.error('Erro ao invalidar cache:', error);
    }
  }
}

// Cache em memória para dados críticos
class MemoryCacheService implements CacheService {
  private cache = new Map<string, { value: any; expiry: number }>();

  async get<T>(key: string): Promise<T | null> {
    const item = this.cache.get(key);
    if (!item) return null;
    
    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return null;
    }
    
    return item.value;
  }

  async set(key: string, value: any, ttl = 3600): Promise<void> {
    this.cache.set(key, {
      value,
      expiry: Date.now() + (ttl * 1000)
    });
  }

  async del(key: string): Promise<void> {
    this.cache.delete(key);
  }

  async invalidatePattern(pattern: string): Promise<void> {
    const regex = new RegExp(pattern.replace('*', '.*'));
    Array.from(this.cache.keys())
      .filter(key => regex.test(key))
      .forEach(key => this.cache.delete(key));
  }
}

// Instância singleton
export const cacheService = new RedisCacheService();
export const memoryCache = new MemoryCacheService();

// Helper para cache com fallback
export const getCachedData = async <T>(
  key: string,
  fetchFn: () => Promise<T>,
  ttl = 3600,
  useMemory = false
): Promise<T> => {
  const cache = useMemory ? memoryCache : cacheService;
  
  // Tentar buscar do cache
  let cached = await cache.get<T>(key);
  if (cached) return cached;
  
  // Buscar dados frescos
  const data = await fetchFn();
  
  // Salvar no cache
  await cache.set(key, data, ttl);
  
  return data;
};
