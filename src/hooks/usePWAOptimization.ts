import { useState, useEffect, useCallback } from 'react';

interface PWAOptimizationOptions {
  prefetchAssets?: boolean;
  lazyLoadImages?: boolean;
  monitorPerformance?: boolean;
  cacheFirstStrategy?: boolean;
}

interface PerformanceMetrics {
  fcp: number | null; // First Contentful Paint
  lcp: number | null; // Largest Contentful Paint
  fid: number | null; // First Input Delay
  cls: number | null; // Cumulative Layout Shift
  ttfb: number | null; // Time to First Byte
}

/**
 * Hook para otimizar o desempenho do PWA em dispositivos móveis
 * Implementa técnicas como prefetching, lazy loading e monitoramento de métricas
 * 
 * @param options Opções de otimização
 * @returns Objeto com métricas e funções de otimização
 */
export function usePWAOptimization(options: PWAOptimizationOptions = {}) {
  const {
    prefetchAssets = true,
    lazyLoadImages = true,
    monitorPerformance = true,
    cacheFirstStrategy = true
  } = options;

  const [isLowEndDevice, setIsLowEndDevice] = useState<boolean>(false);
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fcp: null,
    lcp: null,
    fid: null,
    cls: null,
    ttfb: null
  });

  // Detecta se o dispositivo é de baixo desempenho
  useEffect(() => {
    const detectLowEndDevice = () => {
      // Verifica se o dispositivo tem recursos limitados
      const memory = (navigator as any).deviceMemory || 4; // Default para 4GB se não disponível
      const cores = navigator.hardwareConcurrency || 4; // Default para 4 cores se não disponível
      const connection = (navigator as any).connection || {};
      const connectionType = connection.effectiveType || '4g';
      
      // Considera um dispositivo de baixo desempenho se tiver menos de 4GB de RAM
      // ou menos de 4 cores, ou conexão lenta (2g/3g)
      const isLowEnd = 
        memory < 4 || 
        cores < 4 || 
        ['slow-2g', '2g', '3g'].includes(connectionType);
      
      setIsLowEndDevice(isLowEnd);
      
      // Ajusta estratégias baseado no tipo de dispositivo
      if (isLowEnd) {
        console.log('[PWA Optimization] Dispositivo de baixo desempenho detectado, ajustando estratégias');
      }
    };
    
    detectLowEndDevice();
  }, []);

  // Monitora métricas de Web Vitals
  useEffect(() => {
    if (!monitorPerformance) return;
    
    try {
      if ('PerformanceObserver' in window) {
        // Monitora First Contentful Paint (FCP)
        const fcpObserver = new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          if (entries.length > 0) {
            const fcp = entries[0].startTime;
            setMetrics(prev => ({ ...prev, fcp }));
            console.log(`[PWA Metrics] FCP: ${fcp}ms`);
          }
        });
        fcpObserver.observe({ type: 'paint', buffered: true });
        
        // Monitora Largest Contentful Paint (LCP)
        const lcpObserver = new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          if (entries.length > 0) {
            const lcp = entries[entries.length - 1].startTime;
            setMetrics(prev => ({ ...prev, lcp }));
            console.log(`[PWA Metrics] LCP: ${lcp}ms`);
          }
        });
        lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
        
        // Monitora First Input Delay (FID)
        const fidObserver = new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          if (entries.length > 0) {
            const fid = entries[0].processingStart - entries[0].startTime;
            setMetrics(prev => ({ ...prev, fid }));
            console.log(`[PWA Metrics] FID: ${fid}ms`);
          }
        });
        fidObserver.observe({ type: 'first-input', buffered: true });
        
        // Monitora Cumulative Layout Shift (CLS)
        let clsValue = 0;
        const clsObserver = new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          entries.forEach(entry => {
            if (!(entry as any).hadRecentInput) {
              clsValue += (entry as any).value;
              setMetrics(prev => ({ ...prev, cls: clsValue }));
              console.log(`[PWA Metrics] CLS: ${clsValue}`);
            }
          });
        });
        clsObserver.observe({ type: 'layout-shift', buffered: true });
        
        // Monitora Time to First Byte (TTFB)
        const ttfbObserver = new PerformanceObserver((entryList) => {
          const entries = entryList.getEntries();
          entries.forEach(entry => {
            if (entry.entryType === 'navigation') {
              const ttfb = (entry as PerformanceNavigationTiming).responseStart;
              setMetrics(prev => ({ ...prev, ttfb }));
              console.log(`[PWA Metrics] TTFB: ${ttfb}ms`);
            }
          });
        });
        ttfbObserver.observe({ type: 'navigation', buffered: true });
        
        return () => {
          fcpObserver.disconnect();
          lcpObserver.disconnect();
          fidObserver.disconnect();
          clsObserver.disconnect();
          ttfbObserver.disconnect();
        };
      }
    } catch (error) {
      console.error('[PWA Metrics] Erro ao monitorar métricas:', error);
    }
  }, [monitorPerformance]);

  // Prefetch de recursos críticos
  useEffect(() => {
    if (!prefetchAssets || isLowEndDevice) return;
    
    const prefetchCriticalAssets = async () => {
      try {
        // Lista de recursos críticos para prefetch
        const criticalAssets = [
          '/src/main.tsx',
          '/src/App.tsx',
          '/manifest.json'
        ];
        
        // Prefetch usando a API de Cache
        if ('caches' in window) {
          const cache = await caches.open('prefetch-cache');
          await Promise.all(
            criticalAssets.map(asset => 
              cache.add(new Request(asset, { cache: 'no-cache' }))
            )
          );
          console.log('[PWA Optimization] Prefetch de recursos críticos concluído');
        }
      } catch (error) {
        console.error('[PWA Optimization] Erro no prefetch:', error);
      }
    };
    
    // Executa o prefetch após o carregamento da página
    if (document.readyState === 'complete') {
      prefetchCriticalAssets();
    } else {
      window.addEventListener('load', prefetchCriticalAssets);
      return () => window.removeEventListener('load', prefetchCriticalAssets);
    }
  }, [prefetchAssets, isLowEndDevice]);

  // Implementa lazy loading para imagens
  useEffect(() => {
    if (!lazyLoadImages) return;
    
    const setupLazyLoading = () => {
      if ('IntersectionObserver' in window) {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              const img = entry.target as HTMLImageElement;
              const src = img.getAttribute('data-src');
              
              if (src) {
                img.src = src;
                img.removeAttribute('data-src');
              }
              
              imageObserver.unobserve(img);
            }
          });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
        console.log(`[PWA Optimization] Lazy loading configurado para ${lazyImages.length} imagens`);
        
        return () => imageObserver.disconnect();
      }
    };
    
    // Configura lazy loading após o carregamento do DOM
    if (document.readyState === 'complete' || document.readyState === 'interactive') {
      setupLazyLoading();
    } else {
      document.addEventListener('DOMContentLoaded', setupLazyLoading);
      return () => document.removeEventListener('DOMContentLoaded', setupLazyLoading);
    }
  }, [lazyLoadImages]);

  // Implementa estratégia de cache-first para recursos estáticos
  useEffect(() => {
    if (!cacheFirstStrategy || !('serviceWorker' in navigator)) return;
    
    const setupCacheStrategy = async () => {
      try {
        // Verifica se o Service Worker está ativo
        const registration = await navigator.serviceWorker.ready;
        
        // Envia mensagem para o Service Worker para ativar estratégia cache-first
        if (registration.active) {
          registration.active.postMessage({
            type: 'CACHE_STRATEGY',
            payload: { strategy: 'cache-first' }
          });
          console.log('[PWA Optimization] Estratégia cache-first ativada');
        }
      } catch (error) {
        console.error('[PWA Optimization] Erro ao configurar estratégia de cache:', error);
      }
    };
    
    setupCacheStrategy();
  }, [cacheFirstStrategy]);

  // Função para aplicar otimizações específicas para mobile
  const applyMobileOptimizations = useCallback(() => {
    // Otimiza eventos de touch para melhor responsividade
    document.addEventListener('touchstart', () => {}, { passive: true });
    
    // Configura viewport para melhor experiência em dispositivos móveis
    const viewportMeta = document.querySelector('meta[name="viewport"]');
    if (viewportMeta) {
      viewportMeta.setAttribute(
        'content',
        'width=device-width, initial-scale=1, maximum-scale=5, viewport-fit=cover'
      );
    }
    
    // Desativa animações complexas em dispositivos de baixo desempenho
    if (isLowEndDevice) {
      document.documentElement.classList.add('reduce-motion');
      document.documentElement.classList.add('low-end-device');
    }
    
    console.log('[PWA Optimization] Otimizações mobile aplicadas');
    
    return () => {
      document.removeEventListener('touchstart', () => {});
    };
  }, [isLowEndDevice]);

  return {
    isLowEndDevice,
    metrics,
    applyMobileOptimizations
  };
}