import { useState, useEffect, useCallback } from 'react';
import { usePWA } from '../contexts/PWAContext';
import { getBackgroundSyncService } from '../services/backgroundSyncService';

interface OfflineOperation {
  id: string;
  type: 'diagnostic' | 'device' | 'backup' | 'report';
  data: any;
  timestamp: number;
  retries: number;
  priority: 'low' | 'medium' | 'high';
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

interface UseOfflineOperationsReturn {
  // Estado
  pendingOperations: OfflineOperation[];
  isProcessing: boolean;
  lastSyncTime: Date | null;
  syncErrors: string[];
  
  // Métodos
  addOperation: (operation: Omit<OfflineOperation, 'id' | 'timestamp' | 'retries' | 'status'>) => Promise<void>;
  removeOperation: (id: string) => Promise<void>;
  retryOperation: (id: string) => Promise<void>;
  retryAllFailed: () => Promise<void>;
  clearCompleted: () => Promise<void>;
  forceSync: () => Promise<void>;
  
  // Utilitários
  getOperationsByType: (type: OfflineOperation['type']) => OfflineOperation[];
  getFailedOperations: () => OfflineOperation[];
  getTotalSize: () => number;
}

export const useOfflineOperations = (): UseOfflineOperationsReturn => {
  const { isOnline, syncStatus } = usePWA();
  const [pendingOperations, setPendingOperations] = useState<OfflineOperation[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [lastSyncTime, setLastSyncTime] = useState<Date | null>(null);
  const [syncErrors, setSyncErrors] = useState<string[]>([]);

  // Carregar operações pendentes do localStorage
  const loadPendingOperations = useCallback(async () => {
    try {
      const queueStatus = getBackgroundSyncService().getQueueStatus();
      // Converter status da fila para array de operações
      const operations: OfflineOperation[] = [];
      // Como getQueueStatus retorna apenas estatísticas, vamos simular operações baseadas no total
      for (let i = 0; i < queueStatus.pending; i++) {
        operations.push({
          id: `pending_${i}`,
          type: 'diagnostic',
          data: {},
          timestamp: Date.now(),
          retries: 0,
          priority: 'medium',
          status: 'pending'
        });
      }
      setPendingOperations(operations);
    } catch (error) {
      console.error('Erro ao carregar operações pendentes:', error);
    }
  }, []);

  // Adicionar nova operação
  const addOperation = useCallback(async (operation: Omit<OfflineOperation, 'id' | 'timestamp' | 'retries' | 'status'>) => {
    const newOperation: OfflineOperation = {
      ...operation,
      id: `${operation.type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: Date.now(),
      retries: 0,
      status: 'pending'
    };

    try {
      // Usar o método correto baseado no tipo de operação
      let syncId: string;
      const syncService = getBackgroundSyncService();
      switch (operation.type) {
        case 'diagnostic':
          syncId = await syncService.syncDiagnostic('create', operation.data, operation.priority);
          break;
        case 'device':
          syncId = await syncService.syncDevice('create', operation.data, operation.priority);
          break;
        case 'backup':
          syncId = await syncService.syncBackup(operation.data, operation.priority);
          break;
        case 'report':
          syncId = await syncService.syncReport(operation.data, operation.priority);
          break;
        default:
          throw new Error(`Tipo de operação não suportado: ${operation.type}`);
      }
      
      newOperation.id = syncId;
      setPendingOperations(prev => [...prev, newOperation]);
      
      // Se estiver online, tentar processar imediatamente
      if (isOnline) {
        setTimeout(() => forceSync(), 1000);
      }
    } catch (error) {
      console.error('Erro ao adicionar operação:', error);
      setSyncErrors(prev => [...prev, `Erro ao adicionar operação: ${error}`]);
    }
  }, [isOnline]);

  // Remover operação
  const removeOperation = useCallback(async (id: string) => {
    try {
      await getBackgroundSyncService().removeFromQueue(id);
      setPendingOperations(prev => prev.filter(op => op.id !== id));
    } catch (error) {
      console.error('Erro ao remover operação:', error);
    }
  }, []);

  // Tentar novamente uma operação específica
  const retryOperation = useCallback(async (id: string) => {
    const operation = pendingOperations.find(op => op.id === id);
    if (!operation) return;

    try {
      setIsProcessing(true);
      setPendingOperations(prev => 
        prev.map(op => 
          op.id === id 
            ? { ...op, status: 'processing', retries: op.retries + 1 }
            : op
        )
      );

      // Usar o método correto baseado no tipo de operação
      const syncService = getBackgroundSyncService();
      switch (operation.type) {
        case 'diagnostic':
          await syncService.syncDiagnostic('update', operation.data, operation.priority);
          break;
        case 'device':
          await syncService.syncDevice('update', operation.data, operation.priority);
          break;
        case 'backup':
          await syncService.syncBackup(operation.data, operation.priority);
          break;
        case 'report':
          await syncService.syncReport(operation.data, operation.priority);
          break;
        default:
          throw new Error(`Tipo de operação não suportado: ${operation.type}`);
      }

      setPendingOperations(prev => 
        prev.map(op => 
          op.id === id 
            ? { ...op, status: 'completed' }
            : op
        )
      );
      
      setLastSyncTime(new Date());
    } catch (error) {
      console.error('Erro ao tentar novamente operação:', error);
      setPendingOperations(prev => 
        prev.map(op => 
          op.id === id 
            ? { ...op, status: 'failed' }
            : op
        )
      );
      setSyncErrors(prev => [...prev, `Erro na operação ${id}: ${error}`]);
    } finally {
      setIsProcessing(false);
    }
  }, [pendingOperations]);

  // Tentar novamente todas as operações falhadas
  const retryAllFailed = useCallback(async () => {
    const failedOperations = pendingOperations.filter(op => op.status === 'failed');
    
    for (const operation of failedOperations) {
      await retryOperation(operation.id);
    }
  }, [pendingOperations, retryOperation]);

  // Limpar operações concluídas
  const clearCompleted = useCallback(async () => {
    const completedIds = pendingOperations
      .filter(op => op.status === 'completed')
      .map(op => op.id);
    
    for (const id of completedIds) {
      await removeOperation(id);
    }
  }, [pendingOperations, removeOperation]);

  // Forçar sincronização
  const forceSync = useCallback(async () => {
    if (!isOnline || isProcessing) return;

    try {
      setIsProcessing(true);
      setSyncErrors([]);
      
      await getBackgroundSyncService().forceSync();
      await loadPendingOperations();
      
      setLastSyncTime(new Date());
    } catch (error) {
      console.error('Erro na sincronização forçada:', error);
      setSyncErrors(prev => [...prev, `Erro na sincronização: ${error}`]);
    } finally {
      setIsProcessing(false);
    }
  }, [isOnline, isProcessing, loadPendingOperations]);

  // Obter operações por tipo
  const getOperationsByType = useCallback((type: OfflineOperation['type']) => {
    return pendingOperations.filter(op => op.type === type);
  }, [pendingOperations]);

  // Obter operações falhadas
  const getFailedOperations = useCallback(() => {
    return pendingOperations.filter(op => op.status === 'failed');
  }, [pendingOperations]);

  // Calcular tamanho total das operações
  const getTotalSize = useCallback(() => {
    return pendingOperations.reduce((total, op) => {
      return total + JSON.stringify(op.data).length;
    }, 0);
  }, [pendingOperations]);

  // Efeitos
  useEffect(() => {
    loadPendingOperations();
  }, [loadPendingOperations]);

  // Auto-sincronização quando ficar online
  useEffect(() => {
    if (isOnline && pendingOperations.length > 0 && syncStatus === 'idle') {
      forceSync();
    }
  }, [isOnline, pendingOperations.length, syncStatus, forceSync]);

  // Limpeza automática de operações concluídas (a cada 5 minutos)
  useEffect(() => {
    const interval = setInterval(() => {
      const completedCount = pendingOperations.filter(op => op.status === 'completed').length;
      if (completedCount > 10) { // Limpar se houver mais de 10 operações concluídas
        clearCompleted();
      }
    }, 5 * 60 * 1000); // 5 minutos

    return () => clearInterval(interval);
  }, [pendingOperations, clearCompleted]);

  // Limpeza automática de erros antigos
  useEffect(() => {
    if (syncErrors.length > 5) {
      setSyncErrors(prev => prev.slice(-3)); // Manter apenas os 3 últimos erros
    }
  }, [syncErrors]);

  return {
    // Estado
    pendingOperations,
    isProcessing,
    lastSyncTime,
    syncErrors,
    
    // Métodos
    addOperation,
    removeOperation,
    retryOperation,
    retryAllFailed,
    clearCompleted,
    forceSync,
    
    // Utilitários
    getOperationsByType,
    getFailedOperations,
    getTotalSize
  };
};