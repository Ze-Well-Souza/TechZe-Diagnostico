import React, { useState, useEffect } from 'react';
import { Bell, X, Check, Trash2, Settings, Filter } from 'lucide-react';
import { useNotifications, Notification } from '@/hooks/useNotifications';
import { notificationService } from '@/services/notificationAPI';
import { useAuth } from '@/contexts/AuthContext';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface NotificationCenterProps {
  isOpen: boolean;
  onClose: () => void;
  className?: string;
}

type FilterType = 'all' | 'unread' | 'success' | 'error' | 'warning' | 'info';

const NotificationCenter: React.FC<NotificationCenterProps> = ({
  isOpen,
  onClose,
  className,
}) => {
  const { user } = useAuth();
  const {
    notifications,
    removeNotification,
    clearAllNotifications,
    markAsRead,
    unreadCount,
  } = useNotifications();
  
  const [filter, setFilter] = useState<FilterType>('all');
  const [isLoading, setIsLoading] = useState(false);

  // Carregar notificações do servidor quando abrir
  useEffect(() => {
    if (isOpen && user) {
      loadServerNotifications();
    }
  }, [isOpen, user]);

  const loadServerNotifications = async () => {
    if (!user) return;
    
    setIsLoading(true);
    try {
      const serverNotifications = await notificationService.getUserNotifications(user.id);
      // Aqui você pode mesclar com as notificações locais se necessário
    } catch (error) {
      console.error('Erro ao carregar notificações:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Filtrar notificações
  const filteredNotifications = notifications.filter(notification => {
    switch (filter) {
      case 'unread':
        return true; // Implementar lógica de não lidas
      case 'success':
      case 'error':
      case 'warning':
      case 'info':
        return notification.type === filter;
      default:
        return true;
    }
  });

  const handleMarkAsRead = async (notification: Notification) => {
    markAsRead(notification.id);
    if (user) {
      await notificationService.markNotificationAsRead(notification.id);
    }
  };

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success':
        return <Check className="h-4 w-4 text-green-500" />;
      case 'error':
        return <X className="h-4 w-4 text-red-500" />;
      case 'warning':
        return <Filter className="h-4 w-4 text-yellow-500" />;
      case 'info':
      default:
        return <Bell className="h-4 w-4 text-blue-500" />;
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40"
        onClick={onClose}
      />
      
      {/* Panel */}
      <div
        className={cn(
          'fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out',
          isOpen ? 'translate-x-0' : 'translate-x-full',
          className
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-gray-600" />
            <h2 className="text-lg font-semibold text-gray-900">
              Notificações
            </h2>
            {unreadCount > 0 && (
              <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full">
                {unreadCount}
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => {/* Abrir configurações */}}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Configurações de notificação"
            >
              <Settings className="h-4 w-4 text-gray-600" />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <X className="h-4 w-4 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Filtros */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex gap-2 flex-wrap">
            {[
              { key: 'all', label: 'Todas' },
              { key: 'unread', label: 'Não lidas' },
              { key: 'success', label: 'Sucesso' },
              { key: 'error', label: 'Erro' },
              { key: 'warning', label: 'Aviso' },
              { key: 'info', label: 'Info' },
            ].map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setFilter(key as FilterType)}
                className={cn(
                  'px-3 py-1 text-xs rounded-full transition-colors',
                  filter === key
                    ? 'bg-blue-100 text-blue-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                )}
              >
                {label}
              </button>
            ))}
          </div>
        </div>

        {/* Actions */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex gap-2">
            <button
              onClick={clearAllNotifications}
              className="flex items-center gap-2 px-3 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Trash2 className="h-4 w-4" />
              Limpar todas
            </button>
          </div>
        </div>

        {/* Lista de notificações */}
        <div className="flex-1 overflow-y-auto">
          {isLoading ? (
            <div className="flex items-center justify-center p-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : filteredNotifications.length === 0 ? (
            <div className="flex flex-col items-center justify-center p-8 text-gray-500">
              <Bell className="h-12 w-12 mb-4 text-gray-300" />
              <p className="text-sm text-center">
                {filter === 'all' ? 'Nenhuma notificação' : `Nenhuma notificação do tipo "${filter}"`}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredNotifications.map((notification) => (
                <div
                  key={notification.id}
                  className="p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => handleMarkAsRead(notification)}
                >
                  <div className="flex items-start gap-3">
                    <div className="flex-shrink-0 mt-1">
                      {getNotificationIcon(notification.type)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <h4 className="text-sm font-medium text-gray-900 mb-1">
                        {notification.title}
                      </h4>
                      {notification.message && (
                        <p className="text-sm text-gray-600 mb-2">
                          {notification.message}
                        </p>
                      )}
                      <p className="text-xs text-gray-400">
                        {format(notification.createdAt, 'dd/MM/yyyy HH:mm', {
                          locale: ptBR,
                        })}
                      </p>
                      
                      {notification.action && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            notification.action!.onClick();
                          }}
                          className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-500"
                        >
                          {notification.action.label}
                        </button>
                      )}
                    </div>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        removeNotification(notification.id);
                      }}
                      className="flex-shrink-0 p-1 hover:bg-gray-200 rounded transition-colors"
                    >
                      <X className="h-4 w-4 text-gray-400" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default NotificationCenter;