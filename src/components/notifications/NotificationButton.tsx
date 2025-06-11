import React, { useState } from 'react';
import { Bell } from 'lucide-react';
import { useNotifications } from '@/hooks/useNotifications';
import NotificationCenter from './NotificationCenter';
import { cn } from '@/lib/utils';

interface NotificationButtonProps {
  className?: string;
  showBadge?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const NotificationButton: React.FC<NotificationButtonProps> = ({
  className,
  showBadge = true,
  size = 'md',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const { unreadCount } = useNotifications();

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'p-1.5';
      case 'lg':
        return 'p-3';
      case 'md':
      default:
        return 'p-2';
    }
  };

  const getIconSize = () => {
    switch (size) {
      case 'sm':
        return 'h-4 w-4';
      case 'lg':
        return 'h-6 w-6';
      case 'md':
      default:
        return 'h-5 w-5';
    }
  };

  const getBadgeSize = () => {
    switch (size) {
      case 'sm':
        return 'h-4 w-4 text-xs';
      case 'lg':
        return 'h-6 w-6 text-sm';
      case 'md':
      default:
        return 'h-5 w-5 text-xs';
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className={cn(
          'relative inline-flex items-center justify-center rounded-lg border border-gray-300 bg-white text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors',
          getSizeClasses(),
          className
        )}
        aria-label={`Notificações${unreadCount > 0 ? ` (${unreadCount} não lidas)` : ''}`}
      >
        <Bell className={getIconSize()} />
        
        {/* Badge de notificações não lidas */}
        {showBadge && unreadCount > 0 && (
          <span
            className={cn(
              'absolute -top-1 -right-1 inline-flex items-center justify-center rounded-full bg-red-500 font-medium text-white',
              getBadgeSize()
            )}
          >
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
        
        {/* Indicador de pulse para novas notificações */}
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
          </span>
        )}
      </button>

      {/* Centro de notificações */}
      <NotificationCenter
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </>
  );
};

export default NotificationButton;