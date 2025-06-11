// Serviço de Sincronização em Background para PWA
// Gerencia operações offline e sincronização quando a conexão é restaurada

interface SyncItem {
  id: string;
  type: 'diagnostic' | 'device' | 'backup' | 'report';
  action: 'create' | 'update' | 'delete';
  data: any;
  timestamp: number;
  retries: number;
  maxRetries: number;
  priority: 'low' | 'medium' | 'high';
}

interface SyncResult {
  success: boolean;
  error?: string;
  data?: any;
}

class BackgroundSyncService {
  private static instance: BackgroundSyncService;
  private syncQueue: SyncItem[] = [];
  private isProcessing = false;
  private maxRetries = 3;
  private retryDelay = 5000; // 5 segundos

  private constructor() {
    this.loadQueue();
    this.setupEventListeners();
  }

  static getInstance(): BackgroundSyncService {
    if (!BackgroundSyncService.instance) {
      BackgroundSyncService.instance = new BackgroundSyncService();
    }
    return BackgroundSyncService.instance;
  }

  // ============================================================================
  // GERENCIAMENTO DA FILA
  // ============================================================================

  /**
   * Adiciona item à fila de sincronização
   */
  async addToQueue(
    type: SyncItem['type'],
    action: SyncItem['action'],
    data: any,
    priority: SyncItem['priority'] = 'medium'
  ): Promise<string> {
    const item: SyncItem = {
      id: this.generateId(),
      type,
      action,
      data,
      timestamp: Date.now(),
      retries: 0,
      maxRetries: this.maxRetries,
      priority
    };

    this.syncQueue.push(item);
    this.sortQueueByPriority();
    await this.saveQueue();

    console.log(`[BackgroundSync] Item adicionado à fila: ${item.id}`);

    // Tenta processar imediatamente se online
    if (navigator.onLine && !this.isProcessing) {
      this.processQueue();
    }

    // Registra background sync se suportado
    this.registerBackgroundSync();

    return item.id;
  }

  /**
   * Remove item da fila
   */
  async removeFromQueue(id: string): Promise<boolean> {
    const index = this.syncQueue.findIndex(item => item.id === id);
    if (index !== -1) {
      this.syncQueue.splice(index, 1);
      await this.saveQueue();
      console.log(`[BackgroundSync] Item removido da fila: ${id}`);
      return true;
    }
    return false;
  }

  /**
   * Obtém status da fila
   */
  getQueueStatus() {
    return {
      total: this.syncQueue.length,
      pending: this.syncQueue.filter(item => item.retries < item.maxRetries).length,
      failed: this.syncQueue.filter(item => item.retries >= item.maxRetries).length,
      isProcessing: this.isProcessing
    };
  }

  /**
   * Limpa itens falhados da fila
   */
  async clearFailedItems(): Promise<number> {
    const failedCount = this.syncQueue.filter(item => item.retries >= item.maxRetries).length;
    this.syncQueue = this.syncQueue.filter(item => item.retries < item.maxRetries);
    await this.saveQueue();
    console.log(`[BackgroundSync] ${failedCount} itens falhados removidos`);
    return failedCount;
  }

  // ============================================================================
  // PROCESSAMENTO DA FILA
  // ============================================================================

  /**
   * Processa fila de sincronização
   */
  async processQueue(): Promise<void> {
    if (this.isProcessing || !navigator.onLine || this.syncQueue.length === 0) {
      return;
    }

    this.isProcessing = true;
    console.log(`[BackgroundSync] Processando ${this.syncQueue.length} itens da fila`);

    const processedItems: string[] = [];
    const failedItems: string[] = [];

    for (const item of this.syncQueue) {
      if (item.retries >= item.maxRetries) {
        failedItems.push(item.id);
        continue;
      }

      try {
        const result = await this.processItem(item);
        
        if (result.success) {
          processedItems.push(item.id);
          console.log(`[BackgroundSync] Item sincronizado: ${item.id}`);
          
          // Notifica sucesso
          this.notifySync('success', {
            id: item.id,
            type: item.type,
            action: item.action,
            data: result.data
          });
        } else {
          item.retries++;
          console.log(`[BackgroundSync] Falha na sincronização: ${item.id} (tentativa ${item.retries}/${item.maxRetries})`);
          
          if (item.retries >= item.maxRetries) {
            failedItems.push(item.id);
            this.notifySync('failed', {
              id: item.id,
              type: item.type,
              action: item.action,
              error: result.error
            });
          }
        }
      } catch (error) {
        item.retries++;
        console.error(`[BackgroundSync] Erro ao processar item ${item.id}:`, error);
        
        if (item.retries >= item.maxRetries) {
          failedItems.push(item.id);
        }
      }

      // Delay entre processamentos para não sobrecarregar
      await this.delay(100);
    }

    // Remove itens processados
    this.syncQueue = this.syncQueue.filter(item => !processedItems.includes(item.id));
    await this.saveQueue();

    this.isProcessing = false;
    
    console.log(`[BackgroundSync] Processamento concluído. Sucesso: ${processedItems.length}, Falhas: ${failedItems.length}`);
  }

  /**
   * Processa item individual
   */
  private async processItem(item: SyncItem): Promise<SyncResult> {
    try {
      switch (item.type) {
        case 'diagnostic':
          return await this.processDiagnosticItem(item);
        case 'device':
          return await this.processDeviceItem(item);
        case 'backup':
          return await this.processBackupItem(item);
        case 'report':
          return await this.processReportItem(item);
        default:
          throw new Error(`Tipo de item não suportado: ${item.type}`);
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Erro desconhecido'
      };
    }
  }

  // ============================================================================
  // PROCESSADORES ESPECÍFICOS
  // ============================================================================

  private async processDiagnosticItem(item: SyncItem): Promise<SyncResult> {
    const { action, data } = item;
    const baseUrl = '/api/v1/diagnostics';

    switch (action) {
      case 'create':
        const createResponse = await fetch(baseUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        
        if (!createResponse.ok) {
          throw new Error(`Erro ao criar diagnóstico: ${createResponse.statusText}`);
        }
        
        return {
          success: true,
          data: await createResponse.json()
        };

      case 'update':
        const updateResponse = await fetch(`${baseUrl}/${data.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        
        if (!updateResponse.ok) {
          throw new Error(`Erro ao atualizar diagnóstico: ${updateResponse.statusText}`);
        }
        
        return {
          success: true,
          data: await updateResponse.json()
        };

      case 'delete':
        const deleteResponse = await fetch(`${baseUrl}/${data.id}`, {
          method: 'DELETE'
        });
        
        if (!deleteResponse.ok) {
          throw new Error(`Erro ao deletar diagnóstico: ${deleteResponse.statusText}`);
        }
        
        return { success: true };

      default:
        throw new Error(`Ação não suportada para diagnóstico: ${action}`);
    }
  }

  private async processDeviceItem(item: SyncItem): Promise<SyncResult> {
    const { action, data } = item;
    const baseUrl = '/api/v1/devices';

    switch (action) {
      case 'create':
        const createResponse = await fetch(baseUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        
        if (!createResponse.ok) {
          throw new Error(`Erro ao criar dispositivo: ${createResponse.statusText}`);
        }
        
        return {
          success: true,
          data: await createResponse.json()
        };

      case 'update':
        const updateResponse = await fetch(`${baseUrl}/${data.id}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        
        if (!updateResponse.ok) {
          throw new Error(`Erro ao atualizar dispositivo: ${updateResponse.statusText}`);
        }
        
        return {
          success: true,
          data: await updateResponse.json()
        };

      case 'delete':
        const deleteResponse = await fetch(`${baseUrl}/${data.id}`, {
          method: 'DELETE'
        });
        
        if (!deleteResponse.ok) {
          throw new Error(`Erro ao deletar dispositivo: ${deleteResponse.statusText}`);
        }
        
        return { success: true };

      default:
        throw new Error(`Ação não suportada para dispositivo: ${action}`);
    }
  }

  private async processBackupItem(item: SyncItem): Promise<SyncResult> {
    const { data } = item;
    
    const response = await fetch('/api/v1/backup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`Erro ao criar backup: ${response.statusText}`);
    }
    
    return {
      success: true,
      data: await response.json()
    };
  }

  private async processReportItem(item: SyncItem): Promise<SyncResult> {
    const { data } = item;
    
    const response = await fetch('/api/v1/reports', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`Erro ao gerar relatório: ${response.statusText}`);
    }
    
    return {
      success: true,
      data: await response.json()
    };
  }

  // ============================================================================
  // UTILITÁRIOS
  // ============================================================================

  private generateId(): string {
    return `sync_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private sortQueueByPriority(): void {
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    this.syncQueue.sort((a, b) => {
      const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority];
      if (priorityDiff !== 0) return priorityDiff;
      return a.timestamp - b.timestamp; // FIFO para mesma prioridade
    });
  }

  private async saveQueue(): Promise<void> {
    try {
      localStorage.setItem('background-sync-queue', JSON.stringify(this.syncQueue));
    } catch (error) {
      console.error('[BackgroundSync] Erro ao salvar fila:', error);
    }
  }

  private loadQueue(): void {
    try {
      const stored = localStorage.getItem('background-sync-queue');
      if (stored) {
        this.syncQueue = JSON.parse(stored);
        this.sortQueueByPriority();
        console.log(`[BackgroundSync] ${this.syncQueue.length} itens carregados da fila`);
      }
    } catch (error) {
      console.error('[BackgroundSync] Erro ao carregar fila:', error);
      this.syncQueue = [];
    }
  }

  private async delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private setupEventListeners(): void {
    // Processa fila quando volta online
    window.addEventListener('online', () => {
      console.log('[BackgroundSync] Conexão restaurada, processando fila');
      setTimeout(() => this.processQueue(), 1000);
    });

    // Escuta mensagens do Service Worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data?.type === 'BACKGROUND_SYNC') {
          console.log('[BackgroundSync] Evento de sync do Service Worker');
          this.processQueue();
        }
      });
    }

    // Processa fila periodicamente
    setInterval(() => {
      if (navigator.onLine && this.syncQueue.length > 0 && !this.isProcessing) {
        this.processQueue();
      }
    }, 30000); // A cada 30 segundos
  }

  private async registerBackgroundSync(): Promise<void> {
    if (!('serviceWorker' in navigator) || !('sync' in window.ServiceWorkerRegistration.prototype)) {
      return;
    }

    try {
      const registration = await navigator.serviceWorker.ready;
      await registration.sync.register('background-sync');
      console.log('[BackgroundSync] Background sync registrado');
    } catch (error) {
      console.error('[BackgroundSync] Erro ao registrar background sync:', error);
    }
  }

  private notifySync(type: 'success' | 'failed', data: any): void {
    // Dispara evento customizado
    window.dispatchEvent(new CustomEvent('backgroundSyncUpdate', {
      detail: { type, data }
    }));

    // Notifica via Service Worker se disponível
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then(registration => {
        registration.active?.postMessage({
          type: 'SYNC_NOTIFICATION',
          payload: { type, data }
        });
      });
    }
  }

  // ============================================================================
  // API PÚBLICA
  // ============================================================================

  /**
   * Agenda diagnóstico para sincronização
   */
  async syncDiagnostic(action: 'create' | 'update' | 'delete', data: any, priority: SyncItem['priority'] = 'medium'): Promise<string> {
    return this.addToQueue('diagnostic', action, data, priority);
  }

  /**
   * Agenda dispositivo para sincronização
   */
  async syncDevice(action: 'create' | 'update' | 'delete', data: any, priority: SyncItem['priority'] = 'medium'): Promise<string> {
    return this.addToQueue('device', action, data, priority);
  }

  /**
   * Agenda backup para sincronização
   */
  async syncBackup(data: any, priority: SyncItem['priority'] = 'low'): Promise<string> {
    return this.addToQueue('backup', 'create', data, priority);
  }

  /**
   * Agenda relatório para sincronização
   */
  async syncReport(data: any, priority: SyncItem['priority'] = 'medium'): Promise<string> {
    return this.addToQueue('report', 'create', data, priority);
  }

  /**
   * Força processamento da fila
   */
  async forceSync(): Promise<void> {
    if (navigator.onLine) {
      await this.processQueue();
    } else {
      console.warn('[BackgroundSync] Não é possível sincronizar offline');
    }
  }
}

// Exporta a classe e uma função para obter a instância
export { BackgroundSyncService };
export const getBackgroundSyncService = () => BackgroundSyncService.getInstance();
export default BackgroundSyncService;