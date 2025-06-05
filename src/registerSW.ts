
export const registerServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register('/sw.js');
      console.log('Service Worker registrado com sucesso:', registration.scope);
      
      if ('sync' in registration) {
        await registration.sync.register('sync-diagnosticos');
      }
      
      if ('pushManager' in registration) {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
          console.log('Permissão para notificações concedida');
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
