import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Registrar Service Worker para PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then((registration) => {
        console.log('SW registered: ', registration);
      })
      .catch((registrationError) => {
        console.log('SW registration failed: ', registrationError);
      });
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
    <App />
  </React.StrictMode>,
)
