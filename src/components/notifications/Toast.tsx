import React, { useEffect, useState } from 'react';
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react';
import { Notification } from '@/hooks/useNotifications';
import { cn } from '@/lib/utils';

interface ToastProps {
  notification: Notification;
  onRemove: (id: string) => void;
  className?: string;
}

const Toast: React.FC<ToastProps> = ({ notification, onRemove, className }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);

  useEffect(() => {
    // Animação de entrada
    const timer = setTimeout(() => setIsVisible(true), 100);
    return () => clearTimeout(timer);
  }, []);

  const handleRemove = () => {
    setIsLeaving(true);
    setTimeout(() => onRemove(notification.id), 300);
  };

  const getIcon = () => {
    switch (notification.type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'info':
      default:
        return <Info className="h-5 w-5 text-blue-500" />;
    }
  };

  const getBackgroundColor = () => {
    switch (notification.type) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      case 'warning':
        return 'bg-yellow-50 border-yellow-200';
      case 'info':
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  return (
    <div
      className={cn(
        'relative flex items-start gap-3 p-4 rounded-lg border shadow-lg transition-all duration-300 ease-in-out max-w-sm',
        getBackgroundColor(),
        isVisible && !isLeaving
          ? 'transform translate-x-0 opacity-100'
          : 'transform translate-x-full opacity-0',
        isLeaving && 'transform translate-x-full opacity-0',
        className
      )}
    >
      {/* Ícone */}
      <div className="flex-shrink-0 mt-0.5">
        {getIcon()}
      </div>

      {/* Conteúdo */}
      <div className="flex-1 min-w-0">
        <h4 className="text-sm font-semibold text-gray-900 mb-1">
          {notification.title}
        </h4>
        {notification.message && (
          <p className="text-sm text-gray-600 leading-relaxed">
            {notification.message}
          </p>
        )}
        
        {/* Ação personalizada */}
        {notification.action && (
          <button
            onClick={notification.action.onClick}
            className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-500 transition-colors"
          >
            {notification.action.label}
          </button>
        )}
      </div>

      {/* Botão de fechar */}
      <button
        onClick={handleRemove}
        className="flex-shrink-0 ml-2 p-1 rounded-md hover:bg-gray-100 transition-colors"
        aria-label="Fechar notificação"
      >
        <X className="h-4 w-4 text-gray-400" />
      </button>

      {/* Barra de progresso para notificações temporárias */}
      {!notification.persistent && notification.duration && (
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-gray-200 rounded-b-lg overflow-hidden">
          <div
            className="h-full bg-current opacity-30 transition-all ease-linear"
            style={{
              animation: `toast-progress ${notification.duration}ms linear forwards`,
            }}
          />
        </div>
      )}
    </div>
  );
};

export default Toast;