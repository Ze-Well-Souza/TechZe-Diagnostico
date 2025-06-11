import React, { createContext, useContext, useEffect, ReactNode } from 'react';
import { useNotifications, useToast } from '@/hooks/useNotifications';
import { notificationService } from '@/services/notificationAPI';
import { useAuth } from '@/contexts/AuthContext';

interface NotificationContextType {
  // Métodos do hook useNotifications
  notifications: ReturnType<typeof useNotifications>['notifications'];
  addNotification: ReturnType<typeof useNotifications>['addNotification'];
  removeNotification: ReturnType<typeof useNotifications>['removeNotification'];
  clearAllNotifications: ReturnType<typeof useNotifications>['clearAllNotifications'];
  markAsRead: ReturnType<typeof useNotifications>['markAsRead'];
  unreadCount: ReturnType<typeof useNotifications>['unreadCount'];
  
  // Métodos do toast
  toast: ReturnType<typeof useToast>;
  
  // Métodos específicos do sistema
  initializePushNotifications: () => Promise<void>;
  sendSystemNotification: (type: string, data: any) => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

interface NotificationProviderProps {
  children: ReactNode;
}

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const notificationHook = useNotifications();
  const toast = useToast();

  // Inicializar push notifications quando o usuário fizer login
  useEffect(() => {
    if (user) {
      initializePushNotifications();
      loadUserNotifications();
    }
  }, [user]);

  const initializePushNotifications = async () => {
    if (!user) return;
    
    try {
      // Solicitar permissão para notificações
      const hasPermission = await notificationService.requestNotificationPermission();
      
      if (hasPermission) {
        // Subscrever para push notifications
        await notificationService.subscribeToPushNotifications(user.id);
        
        // Notificar sucesso
        toast.success(
          'Notificações ativadas',
          'Você receberá notificações sobre atualizações importantes'
        );
      }
    } catch (error) {
      console.error('Erro ao inicializar push notifications:', error);
      toast.error(
        'Erro nas notificações',
        'Não foi possível ativar as notificações push'
      );
    }
  };

  const loadUserNotifications = async () => {
    if (!user) return;
    
    try {
      const serverNotifications = await notificationService.getUserNotifications(user.id);
      
      // Adicionar notificações do servidor que não estão localmente
      serverNotifications.forEach(notification => {
        const exists = notificationHook.notifications.find(n => n.id === notification.id);
        if (!exists) {
          notificationHook.addNotification({
            type: notification.type,
            title: notification.title,
            message: notification.message,
            persistent: notification.persistent,
          });
        }
      });
    } catch (error) {
      console.error('Erro ao carregar notificações:', error);
    }
  };

  const sendSystemNotification = async (type: string, data: any) => {
    try {
      await notificationService.sendSystemNotification(type as any, data);
    } catch (error) {
      console.error('Erro ao enviar notificação do sistema:', error);
    }
  };

  // Escutar eventos do sistema para notificações automáticas
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'techze_notification_event') {
        try {
          const eventData = JSON.parse(e.newValue || '{}');
          sendSystemNotification(eventData.type, eventData.data);
        } catch (error) {
          console.error('Erro ao processar evento de notificação:', error);
        }
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Escutar eventos customizados para notificações
  useEffect(() => {
    const handleCustomNotification = (event: CustomEvent) => {
      const { type, data } = event.detail;
      sendSystemNotification(type, data);
    };

    window.addEventListener('techze:notification' as any, handleCustomNotification);
    return () => window.removeEventListener('techze:notification' as any, handleCustomNotification);
  }, []);

  const contextValue: NotificationContextType = {
    ...notificationHook,
    toast,
    initializePushNotifications,
    sendSystemNotification,
  };

  return (
    <NotificationContext.Provider value={contextValue}>
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotificationContext = (): NotificationContextType => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotificationContext deve ser usado dentro de NotificationProvider');
  }
  return context;
};

// Função utilitária para disparar notificações de qualquer lugar da aplicação
export const triggerNotification = (type: string, data: any) => {
  // Disparar evento customizado
  const event = new CustomEvent('techze:notification', {
    detail: { type, data }
  });
  window.dispatchEvent(event);
  
  // Também salvar no localStorage para sincronização entre abas
  localStorage.setItem('techze_notification_event', JSON.stringify({ type, data }));
  setTimeout(() => {
    localStorage.removeItem('techze_notification_event');
  }, 1000);
};

export default NotificationContext;