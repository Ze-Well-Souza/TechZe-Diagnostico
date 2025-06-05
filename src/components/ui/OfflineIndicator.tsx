
import React from 'react';
import { useOfflineStatus } from '@/hooks/useOfflineStatus';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertTriangle } from 'lucide-react';

export function OfflineIndicator() {
  const { isOnline } = useOfflineStatus();

  if (isOnline) {
    return null;
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 p-4">
      <Alert className="bg-yellow-50 border-yellow-200">
        <AlertTriangle className="h-4 w-4 text-yellow-600" />
        <AlertDescription className="text-yellow-800">
          Você está offline. Algumas funcionalidades podem estar limitadas.
        </AlertDescription>
      </Alert>
    </div>
  );
}
