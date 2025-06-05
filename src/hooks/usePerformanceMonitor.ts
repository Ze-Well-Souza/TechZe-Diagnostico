
import { useEffect, useRef } from 'react';

interface PerformanceMetrics {
  componentName: string;
  renderTime: number;
  mountTime: number;
  updateCount: number;
}

export const usePerformanceMonitor = (componentName: string) => {
  const mountTime = useRef<number>(Date.now());
  const renderStartTime = useRef<number>(Date.now());
  const updateCount = useRef<number>(0);

  useEffect(() => {
    const mount = Date.now();
    mountTime.current = mount;

    return () => {
      const metrics: PerformanceMetrics = {
        componentName,
        renderTime: Date.now() - renderStartTime.current,
        mountTime: mount - mountTime.current,
        updateCount: updateCount.current
      };

      // Enviar métricas apenas em desenvolvimento
      if (import.meta.env.DEV) {
        console.log(`🔍 Performance [${componentName}]:`, metrics);
        
        // Alertar para componentes lentos
        if (metrics.renderTime > 100) {
          console.warn(`⚠️ Componente lento detectado: ${componentName} (${metrics.renderTime}ms)`);
        }
      }

      // Em produção, enviar para serviço de analytics
      if (import.meta.env.PROD && metrics.renderTime > 200) {
        // Implementar envio para serviço de monitoramento
        sendPerformanceMetrics(metrics);
      }
    };
  }, [componentName]);

  useEffect(() => {
    renderStartTime.current = Date.now();
    updateCount.current += 1;
  });

  return {
    markRenderStart: () => {
      renderStartTime.current = Date.now();
    },
    markRenderEnd: () => {
      const renderTime = Date.now() - renderStartTime.current;
      if (renderTime > 50) {
        console.log(`🐌 Render lento: ${componentName} (${renderTime}ms)`);
      }
    }
  };
};

const sendPerformanceMetrics = async (metrics: PerformanceMetrics) => {
  try {
    // Implementar envio para serviço de analytics
    await fetch('/api/analytics/performance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(metrics)
    });
  } catch (error) {
    console.error('Erro ao enviar métricas:', error);
  }
};

// Hook para monitorar Web Vitals
export const useWebVitals = () => {
  useEffect(() => {
    if ('web-vital' in window) {
      // Implementar monitoramento de Web Vitals
      const observer = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.entryType === 'largest-contentful-paint') {
            console.log('LCP:', entry.startTime);
          }
          if (entry.entryType === 'first-input') {
            console.log('FID:', entry.processingStart - entry.startTime);
          }
        });
      });

      observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input'] });

      return () => observer.disconnect();
    }
  }, []);
};
