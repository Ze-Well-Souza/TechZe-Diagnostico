
import React from 'react';
import { useInstallPWA } from '@/hooks/useInstallPWA';
import { Button } from '@/components/ui/button';
import { Download, X } from 'lucide-react';

export function InstallPWABanner() {
  const { isInstallable, promptInstall } = useInstallPWA();
  const [dismissed, setDismissed] = React.useState(false);

  if (!isInstallable || dismissed) {
    return null;
  }

  const handleInstallClick = async () => {
    const installed = await promptInstall();
    if (!installed) {
      setDismissed(true);
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 p-4 bg-indigo-600 text-white flex justify-between items-center z-50 pwa-install-banner">
      <div className="flex items-center space-x-3">
        <Download className="h-5 w-5" />
        <div>
          <h3 className="font-bold">Instale o TechZe Diagnóstico</h3>
          <p className="text-sm opacity-90">Acesse o app mesmo offline</p>
        </div>
      </div>
      <div className="flex gap-2">
        <Button 
          onClick={handleInstallClick}
          variant="secondary"
          size="sm"
        >
          Instalar
        </Button>
        <Button 
          onClick={() => setDismissed(true)}
          variant="ghost"
          size="sm"
          className="text-white hover:bg-indigo-700"
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
}
