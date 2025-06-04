import { useState, useEffect } from 'react';

/**
 * Hook para gerenciar a instalação do PWA
 * @returns Um objeto contendo o estado de instalação e métodos relacionados
 */
export function useInstallPWA() {
  const [isInstallable, setIsInstallable] = useState<boolean>(false);
  const [deferredPrompt, setDeferredPrompt] = useState<any>(null);

  useEffect(() => {
    // Função para lidar com o evento beforeinstallprompt
    const handleBeforeInstallPrompt = (e: Event) => {
      // Previne o comportamento padrão do navegador
      e.preventDefault();
      // Armazena o evento para uso posterior
      setDeferredPrompt(e);
      // Indica que o app pode ser instalado
      setIsInstallable(true);
    };

    // Função para lidar com o evento appinstalled
    const handleAppInstalled = () => {
      // Limpa o prompt e atualiza o estado
      setDeferredPrompt(null);
      setIsInstallable(false);
      console.log('App instalado com sucesso');
    };

    // Função para lidar com o evento customizado appInstallable
    const handleAppInstallable = (e: Event) => {
      const customEvent = e as CustomEvent;
      setIsInstallable(customEvent.detail);
    };

    // Adiciona listeners para eventos de instalação
    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);
    document.addEventListener('appInstallable', handleAppInstallable);

    // Cleanup function
    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
      document.removeEventListener('appInstallable', handleAppInstallable);
    };
  }, []);

  /**
   * Mostra o prompt de instalação do PWA
   * @returns Uma Promise que resolve com o resultado da escolha do usuário
   */
  const promptInstall = async () => {
    if (!deferredPrompt) {
      console.log('App já está instalado ou não pode ser instalado');
      return false;
    }
    
    // Mostra o prompt de instalação
    deferredPrompt.prompt();
    
    // Espera o usuário responder ao prompt
    const { outcome } = await deferredPrompt.userChoice;
    
    // Limpa a referência ao prompt
    setDeferredPrompt(null);
    setIsInstallable(false);
    
    return outcome === 'accepted';
  };

  return {
    isInstallable,
    promptInstall
  };
}