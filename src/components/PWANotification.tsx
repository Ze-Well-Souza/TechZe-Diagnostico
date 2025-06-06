import React, { useState, useEffect } from 'react';
import { usePWA } from '../contexts/PWAContext';
import { X, Download, Wifi, WifiOff, RefreshCw, CheckCircle, AlertCircle, Clock } from 'lucide-react';

interface NotificationProps {
  type: 'update' | 'install' | 'offline' | 'sync' | 'error';
  message: string;
  action?: () => void;
  actionText?: string;
  autoHide?: boolean;
  duration?: number;
}

interface InternalNotificationProps extends NotificationProps {
  key: number;
}

const Notification: React.FC<NotificationProps> = ({
  type,
  message,
  action,
  actionText,
  autoHide = true,
  duration = 5000
}) => {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (autoHide) {
      const timer = setTimeout(() => {
        setIsVisible(false);
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [autoHide, duration]);

  if (!isVisible) return null;

  const getIcon = () => {
    switch (type) {
      case 'update':
        return <RefreshCw className="w-5 h-5" />;
      case 'install':
        return <Download className="w-5 h-5" />;
      case 'offline':
        return <WifiOff className="w-5 h-5" />;
      case 'sync':
        return <CheckCircle className="w-5 h-5" />;
      case 'error':
        return <AlertCircle className="w-5 h-5" />;
      default:
        return <CheckCircle className="w-5 h-5" />;
    }
  };

  const getColorClasses = () => {
    switch (type) {
      case 'update':
        return 'bg-blue-500 border-blue-600';
      case 'install':
        return 'bg-green-500 border-green-600';
      case 'offline':
        return 'bg-orange-500 border-orange-600';
      case 'sync':
        return 'bg-emerald-500 border-emerald-600';
      case 'error':
        return 'bg-red-500 border-red-600';
      default:
        return 'bg-gray-500 border-gray-600';
    }
  };

  return (
    <div className={`fixed top-4 right-4 z-50 max-w-sm w-full ${getColorClasses()} text-white rounded-lg shadow-lg border-l-4 p-4 transform transition-all duration-300 ease-in-out`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          {getIcon()}
        </div>
        <div className="ml-3 flex-1">
          <p className="text-sm font-medium">{message}</p>
          {action && actionText && (
            <button
              onClick={action}
              className="mt-2 text-xs bg-white bg-opacity-20 hover:bg-opacity-30 px-3 py-1 rounded transition-colors duration-200"
            >
              {actionText}
            </button>
          )}
        </div>
        <div className="ml-4 flex-shrink-0">
          <button
            onClick={() => setIsVisible(false)}
            className="text-white hover:text-gray-200 transition-colors duration-200"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

const PWANotification: React.FC = () => {
  const {
    isOnline,
    isInstallable,
    isUpdateAvailable,
    promptInstall,
    updateApp,
    syncStatus,
    pendingOperations
  } = usePWA();

  const [notifications, setNotifications] = useState<InternalNotificationProps[]>([]);
  const [lastOnlineStatus, setLastOnlineStatus] = useState(isOnline);

  // Gerenciar notificações
  const addNotification = (notification: NotificationProps) => {
    const id = Date.now();
    setNotifications(prev => [...prev, { ...notification, key: id }]);
    
    // Auto-remover após duração especificada
    if (notification.autoHide !== false) {
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.key !== id));
      }, notification.duration || 5000);
    }
  };

  // Monitorar mudanças de status online/offline
  useEffect(() => {
    if (lastOnlineStatus !== isOnline) {
      if (isOnline) {
        addNotification({
          type: 'sync',
          message: 'Conexão restaurada! Sincronizando dados...',
          autoHide: true,
          duration: 3000
        });
      } else {
        addNotification({
          type: 'offline',
          message: 'Você está offline. Algumas funcionalidades podem estar limitadas.',
          autoHide: true,
          duration: 4000
        });
      }
      setLastOnlineStatus(isOnline);
    }
  }, [isOnline, lastOnlineStatus]);

  // Monitorar atualizações disponíveis
  useEffect(() => {
    if (isUpdateAvailable) {
      addNotification({
        type: 'update',
        message: 'Nova versão disponível!',
        action: updateApp,
        actionText: 'Atualizar',
        autoHide: false
      });
    }
  }, [isUpdateAvailable, updateApp]);

  // Monitorar possibilidade de instalação
  useEffect(() => {
    if (isInstallable) {
      addNotification({
        type: 'install',
        message: 'Instale o TechZe Diagnóstico para uma melhor experiência!',
        action: promptInstall,
        actionText: 'Instalar',
        autoHide: false
      });
    }
  }, [isInstallable, promptInstall]);

  // Monitorar status de sincronização
  useEffect(() => {
    if (syncStatus === 'completed' && pendingOperations === 0) {
      addNotification({
        type: 'sync',
        message: 'Sincronização concluída com sucesso!',
        autoHide: true,
        duration: 2000
      });
    } else if (syncStatus === 'error') {
      addNotification({
        type: 'error',
        message: 'Erro na sincronização. Tentando novamente...',
        autoHide: true,
        duration: 3000
      });
    }
  }, [syncStatus, pendingOperations]);

  return (
    <>
      {notifications.map((notification, index) => (
        <div key={notification.key} style={{ top: `${4 + index * 80}px` }}>
          <Notification {...notification} />
        </div>
      ))}
      
      {/* Status Bar - Mostra informações persistentes */}
      <div className="fixed bottom-4 left-4 z-40">
        {!isOnline && (
          <div className="bg-orange-500 text-white px-3 py-2 rounded-lg shadow-lg flex items-center space-x-2 text-sm">
            <WifiOff className="w-4 h-4" />
            <span>Modo Offline</span>
          </div>
        )}
        
        {pendingOperations > 0 && (
          <div className="bg-blue-500 text-white px-3 py-2 rounded-lg shadow-lg flex items-center space-x-2 text-sm mt-2">
            <Clock className="w-4 h-4" />
            <span>{pendingOperations} operação(ões) pendente(s)</span>
          </div>
        )}
        
        {syncStatus === 'syncing' && (
          <div className="bg-green-500 text-white px-3 py-2 rounded-lg shadow-lg flex items-center space-x-2 text-sm mt-2">
            <RefreshCw className="w-4 h-4 animate-spin" />
            <span>Sincronizando...</span>
          </div>
        )}
      </div>
    </>
  );
};

export default PWANotification;