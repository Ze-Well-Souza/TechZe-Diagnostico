import React, { createContext, useContext, useState, useEffect } from 'react';
import { initializePWA } from '../registerSW';

interface PWAContextType {
  isOnline: boolean;
  isInstallable: boolean;
  offlineData: any[];
  promptInstall: () => Promise<boolean>;
  saveForLater: (data: any, type?: string) => Promise<boolean>;
}

const PWAContext = createContext<PWAContextType | undefined>(undefined);

export const usePWA = () => {
  const context = useContext(PWAContext);
  if (context === undefined) {
    throw new Error('usePWA must be used within a PWAProvider');
  }
  return context;
};

interface PWAProviderProps {
  children: React.ReactNode;
}

export const PWAProvider: React.FC<PWAProviderProps> = ({ children }) => {
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [isInstallable, setIsInstallable] = useState<boolean>(false);
  const [offlineData, setOfflineData] = useState<any[]>([]);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);

  useEffect(() => {
    // Inicializa o PWA
    const { showInstallPrompt } = initializePWA();

    // Função para lidar com eventos de conexão
    const handleOnlineStatus = () => setIsOnline(true);
    const handleOfflineStatus = () => setIsOnline(false);

    // Função para lidar com o evento beforeinstallprompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
    };

    // Função para lidar com o evento appinstalled
    const handleAppInstalled = () => {
      setDeferredPrompt(null);
      setIsInstallable(false);
    };

    // Função para lidar com o evento customizado appInstallable
    const handleAppInstallable = (e: Event) => {
      const customEvent = e as CustomEvent;
      setIsInstallable(customEvent.detail);
    };

    // Função para lidar com o evento customizado connectionChange
    const handleConnectionChange = (e: Event) => {
      const customEvent = e as CustomEvent;
      if (customEvent.detail) {
        setIsOnline(customEvent.detail.isOnline);
      }
    };

    // Adiciona listeners para eventos
    window.addEventListener('online', handleOnlineStatus);
    window.addEventListener('offline', handleOfflineStatus);
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);
    document.addEventListener('appInstallable', handleAppInstallable);
    document.addEventListener('connectionChange', handleConnectionChange);

    // Carrega dados offline do IndexedDB
    const loadOfflineData = async () => {
      try {
        const db = await openDB();
        const data = await db.getAll('pendingDiagnosticos');
        setOfflineData(data);
      } catch (error) {
        console.error('Erro ao carregar dados offline:', error);
      }
    };

    loadOfflineData();

    // Cleanup function
    return () => {
      window.removeEventListener('online', handleOnlineStatus);
      window.removeEventListener('offline', handleOfflineStatus);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      document.removeEventListener('appInstallable', handleAppInstallable);
      document.removeEventListener('connectionChange', handleConnectionChange);
    };
  }, []);

  /**
   * Mostra o prompt de instalação do PWA
   */
  const promptInstall = async () => {
    if (!deferredPrompt) {
      console.log('App já está instalado ou não pode ser instalado');
      return false;
    }
    
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    setDeferredPrompt(null);
    setIsInstallable(false);
    
    return outcome === 'accepted';
  };

  /**
   * Salva dados para sincronização posterior quando estiver online
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

  const value = {
    isOnline,
    isInstallable,
    offlineData,
    promptInstall,
    saveForLater
  };

  return <PWAContext.Provider value={value}>{children}</PWAContext.Provider>;
};