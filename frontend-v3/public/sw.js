// Service Worker para TechZe Diagnóstico PWA

const CACHE_NAME = 'techze-diagnostico-v1';

// Arquivos para cache inicial
const urlsToCache = [
  '/',
  '/index.html',
  '/src/main.tsx',
  '/src/App.tsx',
  '/src/index.css',
  '/src/App.css',
  '/favicon.ico',
  '/manifest.json',
  '/icons/icon-72x72.png.svg',
  '/icons/icon-96x96.png.svg',
  '/icons/icon-128x128.png.svg',
  '/icons/icon-144x144.png.svg',
  '/icons/icon-152x152.png.svg',
  '/icons/icon-192x192.png.svg',
  '/icons/icon-384x384.png.svg',
  '/icons/icon-512x512.png.svg',
  '/icons/maskable-icon-512x512.png.svg'
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
  );
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Estratégia de cache: Cache First, falling back to network
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Cache hit - retorna a resposta do cache
        if (response) {
          return response;
        }

        // Clone da requisição
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest).then(
          (response) => {
            // Verifica se recebemos uma resposta válida
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clone da resposta
            const responseToCache = response.clone();

            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });

            return response;
          }
        );
      })
  );
});

// Sincronização em segundo plano
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-diagnosticos') {
    event.waitUntil(syncDiagnosticos());
  }
});

// Função para sincronizar diagnósticos quando online
async function syncDiagnosticos() {
  try {
    const db = await openDB();
    const pendingDiagnosticos = await db.getAll('pendingDiagnosticos');
    
    for (const diagnostico of pendingDiagnosticos) {
      try {
        // Tenta enviar para o servidor
        const response = await fetch('/api/diagnosticos', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(diagnostico)
        });
        
        if (response.ok) {
          // Se sucesso, remove do IndexedDB
          await db.delete('pendingDiagnosticos', diagnostico.id);
        }
      } catch (error) {
        console.error('Erro ao sincronizar diagnóstico:', error);
      }
    }
  } catch (error) {
    console.error('Erro ao acessar IndexedDB:', error);
  }
}

// Função para abrir o IndexedDB
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open('TechZeDiagnosticoDB', 1);
    
    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);
    
    request.onupgradeneeded = (event) => {
      const db = event.target.result;
      if (!db.objectStoreNames.contains('pendingDiagnosticos')) {
        db.createObjectStore('pendingDiagnosticos', { keyPath: 'id' });
      }
    };
  });
}

// Notificações push
self.addEventListener('push', (event) => {
  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/icons/icon-192x192.png.svg',
    badge: '/icons/icon-72x72.png.svg',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      { action: 'explore', title: 'Ver detalhes' },
      { action: 'close', title: 'Fechar' }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Clique em notificação
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.action === 'explore') {
    clients.openWindow('/diagnosticos');
  }
});