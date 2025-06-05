
/**
 * Sistema de coleta de métricas para monitoramento
 */

export interface Metric {
  name: string;
  value: number;
  timestamp: number;
  labels: Record<string, string>;
  type: 'counter' | 'gauge' | 'histogram';
}

export interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  active_connections: number;
  response_time: number;
  error_rate: number;
}

export class MetricsCollector {
  private metrics: Metric[] = [];
  private static instance: MetricsCollector;

  static getInstance(): MetricsCollector {
    if (!MetricsCollector.instance) {
      MetricsCollector.instance = new MetricsCollector();
    }
    return MetricsCollector.instance;
  }

  recordMetric(name: string, value: number, labels: Record<string, string> = {}, type: Metric['type'] = 'gauge') {
    const metric: Metric = {
      name,
      value,
      timestamp: Date.now(),
      labels: {
        ...labels,
        tenant: multiTenantService.getCurrentTenant()?.companyId || 'unknown'
      },
      type
    };

    this.metrics.push(metric);
    
    // Manter apenas os últimos 1000 registros
    if (this.metrics.length > 1000) {
      this.metrics.shift();
    }

    // Enviar para Prometheus se disponível
    this.sendToPrometheus(metric);
  }

  getSystemMetrics(): SystemMetrics {
    const now = Date.now();
    const recentMetrics = this.metrics.filter(m => now - m.timestamp < 60000); // Últimos 60 segundos

    return {
      cpu_usage: this.getAverageMetric(recentMetrics, 'cpu_usage'),
      memory_usage: this.getAverageMetric(recentMetrics, 'memory_usage'),
      disk_usage: this.getAverageMetric(recentMetrics, 'disk_usage'),
      active_connections: this.getLatestMetric(recentMetrics, 'active_connections'),
      response_time: this.getAverageMetric(recentMetrics, 'response_time'),
      error_rate: this.calculateErrorRate(recentMetrics)
    };
  }

  private getAverageMetric(metrics: Metric[], name: string): number {
    const filtered = metrics.filter(m => m.name === name);
    if (filtered.length === 0) return 0;
    return filtered.reduce((sum, m) => sum + m.value, 0) / filtered.length;
  }

  private getLatestMetric(metrics: Metric[], name: string): number {
    const filtered = metrics.filter(m => m.name === name);
    if (filtered.length === 0) return 0;
    return filtered[filtered.length - 1].value;
  }

  private calculateErrorRate(metrics: Metric[]): number {
    const errors = metrics.filter(m => m.name === 'http_errors').length;
    const total = metrics.filter(m => m.name === 'http_requests').length;
    return total > 0 ? (errors / total) * 100 : 0;
  }

  private async sendToPrometheus(metric: Metric) {
    if (import.meta.env.PROD && import.meta.env.VITE_PROMETHEUS_ENDPOINT) {
      try {
        await fetch(`${import.meta.env.VITE_PROMETHEUS_ENDPOINT}/metrics`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(metric)
        });
      } catch (error) {
        console.warn('Erro ao enviar métrica para Prometheus:', error);
      }
    }
  }

  exportPrometheusFormat(): string {
    const grouped = this.groupMetricsByName();
    let output = '';

    for (const [name, metrics] of grouped.entries()) {
      const latest = metrics[metrics.length - 1];
      const labelsStr = Object.entries(latest.labels)
        .map(([key, value]) => `${key}="${value}"`)
        .join(',');

      output += `# TYPE ${name} ${latest.type}\n`;
      output += `${name}{${labelsStr}} ${latest.value} ${latest.timestamp}\n`;
    }

    return output;
  }

  private groupMetricsByName(): Map<string, Metric[]> {
    const grouped = new Map<string, Metric[]>();
    
    for (const metric of this.metrics) {
      if (!grouped.has(metric.name)) {
        grouped.set(metric.name, []);
      }
      grouped.get(metric.name)!.push(metric);
    }

    return grouped;
  }

  // Métodos específicos para métricas do sistema
  recordDiagnosticCreated(companyId: string, deviceType: string) {
    this.recordMetric('diagnostics_created_total', 1, {
      company_id: companyId,
      device_type: deviceType
    }, 'counter');
  }

  recordResponseTime(endpoint: string, duration: number) {
    this.recordMetric('http_request_duration_seconds', duration, {
      endpoint
    }, 'histogram');
  }

  recordError(type: string, endpoint?: string) {
    this.recordMetric('errors_total', 1, {
      error_type: type,
      endpoint: endpoint || 'unknown'
    }, 'counter');
  }
}

export const metricsCollector = MetricsCollector.getInstance();

// Hook para coleta automática de métricas de performance
import { useEffect } from 'react';

export const useMetricsCollector = (componentName: string) => {
  useEffect(() => {
    const startTime = performance.now();
    
    return () => {
      const duration = performance.now() - startTime;
      metricsCollector.recordMetric('component_render_time', duration, {
        component: componentName
      });
    };
  }, [componentName]);
};
