
import React, { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { getBackgroundSyncService } from '../services/backgroundSyncService';

interface PWAContextType {
  isOnline: boolean;
  isInstallable: boolean;
  isInstalled: boolean;
  isUpdateAvailable: boolean;
  promptInstall: () => void;
  updateApp: () => void;
  syncStatus: 'idle' | 'syncing' | 'completed' | 'error';
  pendingOperations: number;
  cacheStatus: 'loading' | 'ready' | 'error';
  networkType: string;
  isLowDataMode: boolean;
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
  children: ReactNode;
}

export const PWAProvider: React.FC<PWAProviderProps> = ({ children }) => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [isInstallable, setIsInstallable] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isUpdateAvailable, setIsUpdateAvailable] = useState(false);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);
  const [syncStatus, setSyncStatus] = useState<'idle' | 'syncing' | 'completed' | 'error'>('idle');
  const [pendingOperations, setPendingOperations] = useState(0);
  const [cacheStatus, setCacheStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [networkType, setNetworkType] = useState('unknown');
  const [isLowDataMode, setIsLowDataMode] = useState(false);
  const [serviceWorkerRegistration, setServiceWorkerRegistration] = useState<ServiceWorkerRegistration | null>(null);

  // Detectar se o app está instalado
  const checkIfInstalled = useCallback(() => {
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches;
    const isInWebAppiOS = (window.navigator as any).standalone === true;
    setIsInstalled(isStandalone || isInWebAppiOS);
  }, []);

  // Detectar tipo de rede e modo de dados baixos
  const checkNetworkInfo = useCallback(() => {
    const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
    if (connection) {
      setNetworkType(connection.effectiveType || 'unknown');
      setIsLowDataMode(connection.saveData || false);
    }
  }, []);

  // Verificar status do cache
  const checkCacheStatus = useCallback(async () => {
    try {
      if ('caches' in window) {
        const cacheNames = await caches.keys();
        setCacheStatus(cacheNames.length > 0 ? 'ready' : 'loading');
      }
    } catch (error) {
      console.error('Erro ao verificar cache:', error);
      setCacheStatus('error');
    }
  }, []);

  // Atualizar contagem de operações pendentes
  const updatePendingOperations = useCallback(async () => {
    try {
      const queueStatus = getBackgroundSyncService().getQueueStatus();
      setPendingOperations(queueStatus.total);
    } catch (error) {
      console.error('Erro ao obter operações pendentes:', error);
    }
  }, []);

  useEffect(() => {
    const handleOnline = async () => {
      setIsOnline(true);
      setSyncStatus('syncing');
      try {
        await getBackgroundSyncService().forceSync();
        setSyncStatus('completed');
        setTimeout(() => setSyncStatus('idle'), 2000);
      } catch (error) {
        console.error('Erro na sincronização:', error);
        setSyncStatus('error');
        setTimeout(() => setSyncStatus('idle'), 3000);
      }
      updatePendingOperations();
    };

    const handleOffline = () => {
      setIsOnline(false);
      setSyncStatus('idle');
    };

    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setIsInstallable(true);
    };

    const handleAppInstalled = () => {
      setDeferredPrompt(null);
      setIsInstallable(false);
      setIsInstalled(true);
    };

    const handleNetworkChange = () => {
      checkNetworkInfo();
    };

    // Service Worker events
    const handleSWUpdate = () => {
      setIsUpdateAvailable(true);
    };

    const handleSWControllerChange = () => {
      window.location.reload();
    };

    // Event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    // Network change listeners
    const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
    if (connection) {
      connection.addEventListener('change', handleNetworkChange);
    }

    // Service Worker registration
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.ready.then((registration) => {
        setServiceWorkerRegistration(registration);
        
        // Listen for updates
        registration.addEventListener('updatefound', handleSWUpdate);
        
        // Check for waiting service worker
        if (registration.waiting) {
          setIsUpdateAvailable(true);
        }
      });

      navigator.serviceWorker.addEventListener('controllerchange', handleSWControllerChange);
    }

    // Initial checks
    checkIfInstalled();
    checkNetworkInfo();
    checkCacheStatus();
    updatePendingOperations();

    // Periodic updates
    const interval = setInterval(() => {
      updatePendingOperations();
      checkCacheStatus();
    }, 30000); // A cada 30 segundos

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      
      if (connection) {
        connection.removeEventListener('change', handleNetworkChange);
      }
      
      if (serviceWorkerRegistration) {
        serviceWorkerRegistration.removeEventListener('updatefound', handleSWUpdate);
      }
      
      navigator.serviceWorker?.removeEventListener('controllerchange', handleSWControllerChange);
      
      clearInterval(interval);
    };
  }, [checkIfInstalled, checkNetworkInfo, checkCacheStatus, updatePendingOperations, serviceWorkerRegistration]);

  const promptInstall = useCallback(() => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult: any) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('Usuário aceitou a instalação');
        } else {
          console.log('Usuário recusou a instalação');
        }
        setDeferredPrompt(null);
        setIsInstallable(false);
      });
    }
  }, [deferredPrompt]);

  const updateApp = useCallback(() => {
    if (serviceWorkerRegistration?.waiting) {
      serviceWorkerRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
      setIsUpdateAvailable(false);
    }
  }, [serviceWorkerRegistration]);

  const value = {
    isOnline,
    isInstallable,
    isInstalled,
    isUpdateAvailable,
    promptInstall,
    updateApp,
    syncStatus,
    pendingOperations,
    cacheStatus,
    networkType,
    isLowDataMode
  };

  return (
    <PWAContext.Provider value={value}>
      {children}
    </PWAContext.Provider>
  );
};
