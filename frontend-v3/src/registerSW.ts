// Função para registrar o Service Worker
export const registerServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      console.log('Service Worker registrado com sucesso:', registration.scope);
      
      // Configurar sincronização em segundo plano
      if ('sync' in registration) {
        // Registrar sincronização periódica
        await registration.sync.register('sync-diagnosticos');
      }
      
      // Configurar notificações push
      if ('pushManager' in registration) {
        // Solicitar permissão para notificações
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
          console.log('Permissão para notificações concedida');
          // Aqui você pode implementar a lógica para assinar o usuário em um serviço de push
        }
      }
      
      return registration;
    } catch (error) {
      console.error('Erro ao registrar Service Worker:', error);
      return null;
    }
  } else {
    console.warn('Service Worker não é suportado neste navegador');
    return null;
  }
};

// Função para verificar se o app pode ser instalado
export const checkInstallable = () => {
  let deferredPrompt: any = null;
  
  window.addEventListener('beforeinstallprompt', (e) => {
    // Previne o comportamento padrão do navegador
    e.preventDefault();
    // Armazena o evento para uso posterior
    deferredPrompt = e;
    // Atualiza a UI para mostrar o botão de instalação
    document.dispatchEvent(new CustomEvent('appInstallable', { detail: true }));
  });
  
  // Função para mostrar o prompt de instalação
  const showInstallPrompt = async () => {
    if (!deferredPrompt) {
      console.log('App já está instalado ou não pode ser instalado');
      return;
    }
    
    // Mostra o prompt de instalação
    deferredPrompt.prompt();
    // Espera o usuário responder ao prompt
    const { outcome } = await deferredPrompt.userChoice;
    console.log(`Usuário ${outcome === 'accepted' ? 'aceitou' : 'recusou'} a instalação`);
    // Limpa a referência ao prompt
    deferredPrompt = null;
    // Atualiza a UI para esconder o botão de instalação
    document.dispatchEvent(new CustomEvent('appInstallable', { detail: false }));
  };
  
  // Evento para quando o app é instalado
  window.addEventListener('appinstalled', () => {
    console.log('App instalado com sucesso');
    // Atualiza a UI para esconder o botão de instalação
    document.dispatchEvent(new CustomEvent('appInstallable', { detail: false }));
    deferredPrompt = null;
  });
  
  return { showInstallPrompt };
};

// Função para verificar o status da conexão
export const setupOfflineDetection = () => {
  const updateOnlineStatus = () => {
    const isOnline = navigator.onLine;
    document.dispatchEvent(new CustomEvent('connectionChange', { detail: { isOnline } }));
    console.log(`Aplicativo está ${isOnline ? 'online' : 'offline'}`);
  };
  
  // Adiciona listeners para eventos de conexão
  window.addEventListener('online', updateOnlineStatus);
  window.addEventListener('offline', updateOnlineStatus);
  
  // Verifica o status inicial
  updateOnlineStatus();
};

// Inicializa todas as funcionalidades PWA
export const initializePWA = () => {
  registerServiceWorker();
  const { showInstallPrompt } = checkInstallable();
  setupOfflineDetection();
  
  return { showInstallPrompt };
};