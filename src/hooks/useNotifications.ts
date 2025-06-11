import { useState, useCallback, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
  createdAt: Date;
}

export interface NotificationOptions {
  type?: Notification['type'];
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
  action?: Notification['action'];
}

interface UseNotificationsReturn {
  notifications: Notification[];
  addNotification: (options: NotificationOptions) => string;
  removeNotification: (id: string) => void;
  clearAllNotifications: () => void;
  markAsRead: (id: string) => void;
  unreadCount: number;
}

const DEFAULT_DURATION = 5000; // 5 segundos

export const useNotifications = (): UseNotificationsReturn => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [readNotifications, setReadNotifications] = useState<Set<string>>(new Set());

  // Adicionar nova notificação
  const addNotification = useCallback((options: NotificationOptions): string => {
    const id = uuidv4();
    const notification: Notification = {
      id,
      type: options.type || 'info',
      title: options.title,
      message: options.message,
      duration: options.duration || DEFAULT_DURATION,
      persistent: options.persistent || false,
      action: options.action,
      createdAt: new Date(),
    };

    setNotifications(prev => [notification, ...prev]);

    // Auto-remover notificação se não for persistente
    if (!notification.persistent && notification.duration) {
      setTimeout(() => {
        removeNotification(id);
      }, notification.duration);
    }

    return id;
  }, []);

  // Remover notificação
  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
    setReadNotifications(prev => {
      const newSet = new Set(prev);
      newSet.delete(id);
      return newSet;
    });
  }, []);

  // Limpar todas as notificações
  const clearAllNotifications = useCallback(() => {
    setNotifications([]);
    setReadNotifications(new Set());
  }, []);

  // Marcar como lida
  const markAsRead = useCallback((id: string) => {
    setReadNotifications(prev => new Set([...prev, id]));
  }, []);

  // Calcular notificações não lidas
  const unreadCount = notifications.filter(
    notification => !readNotifications.has(notification.id)
  ).length;

  // Cleanup de notificações antigas (mais de 24h)
  useEffect(() => {
    const cleanup = setInterval(() => {
      const now = new Date();
      setNotifications(prev => 
        prev.filter(notification => {
          const age = now.getTime() - notification.createdAt.getTime();
          return age < 24 * 60 * 60 * 1000; // 24 horas
        })
      );
    }, 60 * 60 * 1000); // Verificar a cada hora

    return () => clearInterval(cleanup);
  }, []);

  return {
    notifications,
    addNotification,
    removeNotification,
    clearAllNotifications,
    markAsRead,
    unreadCount,
  };
};

// Hook para notificações rápidas
export const useToast = () => {
  const { addNotification } = useNotifications();

  const toast = {
    success: (title: string, message?: string) => 
      addNotification({ type: 'success', title, message }),
    error: (title: string, message?: string) => 
      addNotification({ type: 'error', title, message, persistent: true }),
    warning: (title: string, message?: string) => 
      addNotification({ type: 'warning', title, message }),
    info: (title: string, message?: string) => 
      addNotification({ type: 'info', title, message }),
  };

  return toast;
};