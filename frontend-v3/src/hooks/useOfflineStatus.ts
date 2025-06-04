import { useState, useEffect } from 'react';

/**
 * Hook para gerenciar o estado de conectividade do aplicativo
 * @returns Um objeto contendo o estado atual da conexão e métodos relacionados
 */
export function useOfflineStatus() {
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [offlineData, setOfflineData] = useState<any[]>([]);

  useEffect(() => {
    // Função para atualizar o estado de conectividade
    const handleConnectionChange = (event: Event) => {
      const customEvent = event as CustomEvent;
      if (customEvent.detail) {
        setIsOnline(customEvent.detail.isOnline);
      } else {
        setIsOnline(navigator.onLine);
      }
    };

    // Função para lidar com eventos nativos de online/offline
    const handleOnlineStatus = () => setIsOnline(true);
    const handleOfflineStatus = () => setIsOnline(false);

    // Adiciona listeners para eventos de conexão
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);
    document.addEventListener('connectionChange', handleConnectionChange);

    // Carrega dados offline do IndexedDB quando necessário
    const loadOfflineData = async () => {
      if (!isOnline) {
        try {
          const db = await openDB();
          const data = await db.getAll('pendingDiagnosticos');
          setOfflineData(data);
        } catch (error) {
          console.error('Erro ao carregar dados offline:', error);
        }
      }
    };

    loadOfflineData();

    // Cleanup function
    return () => {
      window.removeEventListener('online', handleOnlineStatus);
      window.removeEventListener('offline', handleOfflineStatus);
      document.removeEventListener('connectionChange', handleConnectionChange);
    };
  }, [isOnline]);

  /**
   * Salva dados para sincronização posterior quando estiver online
   * @param data Os dados a serem salvos
   * @param type O tipo de operação (ex: 'diagnostico', 'dispositivo')
   */
  const saveForLater = async (data: any, type: string = 'diagnostico') => {
    try {
      const db = await openDB();
      const id = `${type}_${Date.now()}`;
      await db.add('pendingDiagnosticos', { ...data, id, type, timestamp: Date.now() });
      
      // Atualiza a lista de dados offline
      const updatedData = await db.getAll('pendingDiagnosticos');
      setOfflineData(updatedData);
      
      // Tenta registrar uma sincronização em segundo plano
      if ('serviceWorker' in navigator && 'sync' in navigator.serviceWorker) {
        const registration = await navigator.serviceWorker.ready;
        await registration.sync.register('sync-diagnosticos');
      }
      
      return true;
    } catch (error) {
      console.error('Erro ao salvar dados offline:', error);
      return false;
    }
  };

  /**
   * Função auxiliar para abrir o IndexedDB
   */
  const openDB = () => {
    return new Promise<IDBDatabase>((resolve, reject) => {
      const request = indexedDB.open('TechZeDiagnosticoDB', 1);
      
      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
      
      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        if (!db.objectStoreNames.contains('pendingDiagnosticos')) {
          db.createObjectStore('pendingDiagnosticos', { keyPath: 'id' });
        }
      };
    });
  };

  return {
    isOnline,
    offlineData,
    saveForLater,
  };
}