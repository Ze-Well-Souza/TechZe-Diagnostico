import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { PWAProvider } from './contexts/PWAContext'
import PWANotification from './components/PWANotification'

// Register service worker
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
        
        // Listen for service worker updates
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;
          if (newWorker) {
            newWorker.addEventListener('statechange', () => {
              if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                // Nova versão disponível
                console.log('Nova versão do service worker disponível');
              }
            });
          }
        });
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}

// Handle service worker messages
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'BACKGROUND_SYNC_SUCCESS') {
      console.log('Background sync completed:', event.data.payload);
    }
  });
}

// Prevenir zoom em iOS
document.addEventListener('gesturestart', function (e) {
  e.preventDefault();
});

// Adicionar classes para detecção de dispositivo
const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
const isTablet = /iPad|Android/i.test(navigator.userAgent) && window.innerWidth >= 768;
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);

if (isMobile) {
  document.documentElement.classList.add('is-mobile');
}
if (isTablet) {
  document.documentElement.classList.add('is-tablet');
}
if (isIOS) {
  document.documentElement.classList.add('is-ios');
}

// Configurar viewport height para mobile
function setVh() {
  const vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty('--vh', `${vh}px`);
}

setVh();
window.addEventListener('resize', setVh);
window.addEventListener('orientationchange', setVh);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <PWAProvider>
      <App />
      <PWANotification />
    </PWAProvider>
  </React.StrictMode>,
)
