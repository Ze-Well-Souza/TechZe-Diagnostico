import React from 'react';
import { useInstallPWA } from '../../hooks/useInstallPWA';

/**
 * Componente que exibe um banner para instalar o PWA
 */
export function InstallPWABanner() {
  const { isInstallable, promptInstall } = useInstallPWA();

  if (!isInstallable) {
    return null;
  }

  const handleInstallClick = async () => {
    const installed = await promptInstall();
    if (installed) {
      console.log('Aplicativo instalado com sucesso!');
    } else {
      console.log('Instalação recusada ou cancelada');
    }
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 p-4 bg-indigo-600 text-white flex justify-between items-center z-50">
      <div>
        <h3 className="font-bold">Instale o TechZe Diagnóstico</h3>
        <p className="text-sm">Acesse o app mesmo offline e tenha uma experiência melhor</p>
      </div>
      <div className="flex gap-2">
        <button 
          onClick={handleInstallClick}
          className="px-4 py-2 bg-white text-indigo-600 font-medium rounded-md hover:bg-indigo-50 transition-colors"
        >
          Instalar
        </button>
        <button 
          onClick={() => document.dispatchEvent(new CustomEvent('appInstallable', { detail: false }))}
          className="px-2 py-2 text-white hover:bg-indigo-700 rounded-md transition-colors"
        >
          Agora não
        </button>
      </div>
    </div>
  );
}