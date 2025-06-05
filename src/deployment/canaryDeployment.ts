
/**
 * Sistema de deploy canário com feature flags e rollback automático
 */

export interface FeatureFlag {
  name: string;
  enabled: boolean;
  rollout_percentage: number;
  conditions: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface DeploymentConfig {
  version: string;
  environment: 'staging' | 'production';
  canary_percentage: number;
  health_check_url: string;
  rollback_threshold: number;
  monitoring_duration: number;
}

export class CanaryDeploymentService {
  private static instance: CanaryDeploymentService;
  private featureFlags: Map<string, FeatureFlag> = new Map();

  static getInstance(): CanaryDeploymentService {
    if (!CanaryDeploymentService.instance) {
      CanaryDeploymentService.instance = new CanaryDeploymentService();
    }
    return CanaryDeploymentService.instance;
  }

  async startCanaryDeployment(config: DeploymentConfig): Promise<boolean> {
    try {
      console.log(`Iniciando deploy canário - versão ${config.version}`);
      
      // 1. Ativar feature flag para a nova versão
      await this.createFeatureFlag(`version_${config.version}`, {
        name: `version_${config.version}`,
        enabled: true,
        rollout_percentage: config.canary_percentage,
        conditions: {
          environment: config.environment,
          user_role: ['admin', 'beta_tester']
        },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      });

      // 2. Monitorar métricas
      const isHealthy = await this.monitorCanaryHealth(config);
      
      if (isHealthy) {
        // 3. Promover para 100%
        await this.promoteCanary(config.version);
        return true;
      } else {
        // 4. Rollback automático
        await this.rollbackCanary(config.version);
        return false;
      }

    } catch (error) {
      console.error('Erro no deploy canário:', error);
      await this.rollbackCanary(config.version);
      return false;
    }
  }

  private async monitorCanaryHealth(config: DeploymentConfig): Promise<boolean> {
    const startTime = Date.now();
    const duration = config.monitoring_duration * 1000; // converter para ms
    
    while (Date.now() - startTime < duration) {
      try {
        // Verificar health check
        const healthResponse = await fetch(config.health_check_url);
        if (!healthResponse.ok) {
          console.error('Health check falhou');
          return false;
        }

        // Verificar métricas de erro
        const metrics = metricsCollector.getSystemMetrics();
        if (metrics.error_rate > config.rollback_threshold) {
          console.error(`Taxa de erro muito alta: ${metrics.error_rate}%`);
          return false;
        }

        // Aguardar antes da próxima verificação
        await new Promise(resolve => setTimeout(resolve, 30000)); // 30 segundos
        
      } catch (error) {
        console.error('Erro no monitoramento:', error);
        return false;
      }
    }

    return true;
  }

  private async promoteCanary(version: string): Promise<void> {
    console.log(`Promovendo versão ${version} para 100%`);
    
    await this.updateFeatureFlag(`version_${version}`, {
      rollout_percentage: 100,
      conditions: {} // Remover condições, aplicar para todos
    });

    // Notificar sucesso
    await this.sendNotification('success', `Deploy da versão ${version} promovido com sucesso`);
  }

  private async rollbackCanary(version: string): Promise<void> {
    console.log(`Fazendo rollback da versão ${version}`);
    
    await this.updateFeatureFlag(`version_${version}`, {
      enabled: false,
      rollout_percentage: 0
    });

    // Notificar rollback
    await this.sendNotification('error', `Rollback automático da versão ${version} executado`);
  }

  async createFeatureFlag(name: string, flag: FeatureFlag): Promise<void> {
    this.featureFlags.set(name, flag);
    
    // Salvar no Supabase se disponível
    try {
      await supabase.from('feature_flags').upsert({
        name: flag.name,
        enabled: flag.enabled,
        rollout_percentage: flag.rollout_percentage,
        conditions: flag.conditions
      });
    } catch (error) {
      console.warn('Erro ao salvar feature flag:', error);
    }
  }

  async updateFeatureFlag(name: string, updates: Partial<FeatureFlag>): Promise<void> {
    const existing = this.featureFlags.get(name);
    if (existing) {
      const updated = { ...existing, ...updates, updated_at: new Date().toISOString() };
      this.featureFlags.set(name, updated);
      
      try {
        await supabase.from('feature_flags')
          .update(updates)
          .eq('name', name);
      } catch (error) {
        console.warn('Erro ao atualizar feature flag:', error);
      }
    }
  }

  isFeatureEnabled(name: string, userContext?: any): boolean {
    const flag = this.featureFlags.get(name);
    if (!flag || !flag.enabled) return false;

    // Verificar porcentagem de rollout
    const userHash = userContext?.id ? this.hashUser(userContext.id) : Math.random();
    if (userHash > flag.rollout_percentage / 100) return false;

    // Verificar condições específicas
    if (flag.conditions.user_role && userContext?.role) {
      return flag.conditions.user_role.includes(userContext.role);
    }

    return true;
  }

  private hashUser(userId: string): number {
    let hash = 0;
    for (let i = 0; i < userId.length; i++) {
      const char = userId.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash) / 2147483647; // Normalizar para 0-1
  }

  private async sendNotification(type: 'success' | 'error', message: string): Promise<void> {
    // Implementar notificações por SMS/Email via webhook
    try {
      await fetch('/api/notifications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type, message, timestamp: new Date().toISOString() })
      });
    } catch (error) {
      console.error('Erro ao enviar notificação:', error);
    }
  }
}

export const canaryDeploymentService = CanaryDeploymentService.getInstance();

// Hook para usar feature flags em componentes React
import { useState, useEffect } from 'react';

export const useFeatureFlag = (flagName: string, userContext?: any): boolean => {
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    const checkFlag = () => {
      const isEnabled = canaryDeploymentService.isFeatureEnabled(flagName, userContext);
      setEnabled(isEnabled);
    };

    checkFlag();
    
    // Verificar periodicamente por mudanças
    const interval = setInterval(checkFlag, 60000); // 1 minuto
    
    return () => clearInterval(interval);
  }, [flagName, userContext]);

  return enabled;
};
