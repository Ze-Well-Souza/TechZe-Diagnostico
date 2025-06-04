import React from 'react';
import { useOfflineStatus } from '../../hooks/useOfflineStatus';

/**
 * Componente que exibe um indicador de status offline
 */
export function OfflineIndicator() {
  const { isOnline } = useOfflineStatus();

  if (isOnline) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 p-2 bg-yellow-500 text-white text-center z-50">
      <div className="flex items-center justify-center gap-2">
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          className="h-5 w-5" 
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
          />
        </svg>
        <span className="font-medium">Você está offline. Algumas funcionalidades podem estar limitadas.</span>
      </div>
    </div>
  );
}