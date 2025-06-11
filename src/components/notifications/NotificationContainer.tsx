import React from 'react';
import { useNotifications } from '@/hooks/useNotifications';
import Toast from './Toast';
import { cn } from '@/lib/utils';

interface NotificationContainerProps {
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  maxNotifications?: number;
  className?: string;
}

const NotificationContainer: React.FC<NotificationContainerProps> = ({
  position = 'top-right',
  maxNotifications = 5,
  className,
}) => {
  const { notifications, removeNotification } = useNotifications();

  // Limitar o número de notificações exibidas
  const visibleNotifications = notifications.slice(0, maxNotifications);

  const getPositionClasses = () => {
    switch (position) {
      case 'top-left':
        return 'top-4 left-4';
      case 'top-center':
        return 'top-4 left-1/2 transform -translate-x-1/2';
      case 'top-right':
        return 'top-4 right-4';
      case 'bottom-left':
        return 'bottom-4 left-4';
      case 'bottom-center':
        return 'bottom-4 left-1/2 transform -translate-x-1/2';
      case 'bottom-right':
      default:
        return 'bottom-4 right-4';
    }
  };

  if (visibleNotifications.length === 0) {
    return null;
  }

  return (
    <div
      className={cn(
        'fixed z-50 flex flex-col gap-2 pointer-events-none',
        getPositionClasses(),
        className
      )}
      aria-live="polite"
      aria-label="Notificações"
    >
      {visibleNotifications.map((notification) => (
        <div key={notification.id} className="pointer-events-auto">
          <Toast
            notification={notification}
            onRemove={removeNotification}
          />
        </div>
      ))}
      
      {/* Indicador de notificações adicionais */}
      {notifications.length > maxNotifications && (
        <div className="pointer-events-auto">
          <div className="bg-gray-800 text-white text-xs px-3 py-2 rounded-lg shadow-lg text-center">
            +{notifications.length - maxNotifications} notificações adicionais
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationContainer;