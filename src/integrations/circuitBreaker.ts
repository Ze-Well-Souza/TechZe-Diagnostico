
/**
 * Implementação do padrão Circuit Breaker para integrações externas
 */

export enum CircuitState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN'
}

export interface CircuitBreakerConfig {
  failureThreshold: number;
  recoveryTimeout: number;
  monitoringPeriod: number;
  expectedErrors: string[];
}

export class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failureCount: number = 0;
  private lastFailureTime: number = 0;
  private config: CircuitBreakerConfig;

  constructor(private name: string, config: Partial<CircuitBreakerConfig> = {}) {
    this.config = {
      failureThreshold: 5,
      recoveryTimeout: 60000, // 1 minuto
      monitoringPeriod: 10000, // 10 segundos
      expectedErrors: ['TIMEOUT', 'CONNECTION_ERROR', '5XX'],
      ...config
    };
  }

  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      if (this.shouldAttemptReset()) {
        this.state = CircuitState.HALF_OPEN;
        console.log(`Circuit Breaker ${this.name}: Tentando recuperação`);
      } else {
        throw new Error(`Circuit Breaker ${this.name} está ABERTO`);
      }
    }

    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure(error);
      throw error;
    }
  }

  private onSuccess(): void {
    this.failureCount = 0;
    this.state = CircuitState.CLOSED;
    console.log(`Circuit Breaker ${this.name}: Operação bem-sucedida`);
  }

  private onFailure(error: any): void {
    const errorType = this.categorizeError(error);
    
    if (this.config.expectedErrors.includes(errorType)) {
      this.failureCount++;
      this.lastFailureTime = Date.now();

      console.log(`Circuit Breaker ${this.name}: Falha ${this.failureCount}/${this.config.failureThreshold}`);

      if (this.failureCount >= this.config.failureThreshold) {
        this.state = CircuitState.OPEN;
        console.error(`Circuit Breaker ${this.name}: ABERTO devido a muitas falhas`);
        
        // Enviar alerta
        this.sendAlert('CIRCUIT_OPEN', `Circuit Breaker ${this.name} foi aberto`);
      }
    }
  }

  private shouldAttemptReset(): boolean {
    return Date.now() - this.lastFailureTime >= this.config.recoveryTimeout;
  }

  private categorizeError(error: any): string {
    if (error.name === 'TimeoutError') return 'TIMEOUT';
    if (error.code === 'ECONNREFUSED') return 'CONNECTION_ERROR';
    if (error.status >= 500) return '5XX';
    return 'UNKNOWN';
  }

  private async sendAlert(type: string, message: string): Promise<void> {
    try {
      metricsCollector.recordError('circuit_breaker', this.name);
      
      // Enviar notificação
      await fetch('/api/alerts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type,
          message,
          circuit: this.name,
          timestamp: new Date().toISOString()
        })
      });
    } catch (alertError) {
      console.error('Erro ao enviar alerta:', alertError);
    }
  }

  getStatus() {
    return {
      name: this.name,
      state: this.state,
      failureCount: this.failureCount,
      lastFailureTime: this.lastFailureTime
    };
  }
}

// Instâncias pré-configuradas para serviços específicos
export const zendeskCircuitBreaker = new CircuitBreaker('zendesk', {
  failureThreshold: 3,
  recoveryTimeout: 30000
});

export const notasFiscaisCircuitBreaker = new CircuitBreaker('notas_fiscais', {
  failureThreshold: 5,
  recoveryTimeout: 60000
});

export const emailCircuitBreaker = new CircuitBreaker('email_service', {
  failureThreshold: 10,
  recoveryTimeout: 120000
});

// Hook para monitorar circuit breakers
export const useCircuitBreakerStatus = () => {
  const [status, setStatus] = useState<any[]>([]);

  useEffect(() => {
    const updateStatus = () => {
      setStatus([
        zendeskCircuitBreaker.getStatus(),
        notasFiscaisCircuitBreaker.getStatus(),
        emailCircuitBreaker.getStatus()
      ]);
    };

    updateStatus();
    const interval = setInterval(updateStatus, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return status;
};
