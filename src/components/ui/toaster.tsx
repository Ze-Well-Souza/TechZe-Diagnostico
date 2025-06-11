import React from 'react';
import NotificationContainer from '@/components/notifications/NotificationContainer';

interface ToasterProps {
  className?: string;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  maxNotifications?: number;
}

export const Toaster: React.FC<ToasterProps> = ({ 
  className,
  position = 'bottom-right',
  maxNotifications = 5 
}) => {
  return (
    <NotificationContainer
      position={position}
      maxNotifications={maxNotifications}
      className={className}
    />
  );
};

export default Toaster;