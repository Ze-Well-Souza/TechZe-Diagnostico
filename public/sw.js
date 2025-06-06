// Service Worker Avançado para TechZe Diagnóstico PWA
// Implementa estratégias de cache, sincronização em background e funcionalidades offline

const CACHE_NAME = 'techze-diagnostico-v2';
const STATIC_CACHE = 'techze-static-v2';
const DYNAMIC_CACHE = 'techze-dynamic-v2';
const API_CACHE = 'techze-api-v2';
const IMAGE_CACHE = 'techze-images-v2';

// URLs para cache estático (recursos críticos)
const STATIC_URLS = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  '/offline.html', // Página offline personalizada
  '/icons/icon-192x192.png.svg',
  '/icons/icon-512x512.png.svg'
];

// URLs da API para cache
const API_URLS = [
  '/api/v1/auth/me',
  '/api/v1/diagnostic/history',
  '/api/v1/devices'
];

// Configurações de cache por tipo de recurso
const CACHE_STRATEGIES = {
  static: 'CacheFirst',
  api: 'NetworkFirst',
  images: 'CacheFirst',
  dynamic: 'StaleWhileRevalidate'
};

// Configurações de expiração
const CACHE_EXPIRATION = {
  static: 30 * 24 * 60 * 60 * 1000, // 30 dias
  api: 7 * 24 * 60 * 60 * 1000,     // 7 dias
  images: 30 * 24 * 60 * 60 * 1000, // 30 dias
  dynamic: 24 * 60 * 60 * 1000      // 1 dia
};

// Fila de sincronização para operações offline
let syncQueue = [];

// ============================================================================
// INSTALAÇÃO DO SERVICE WORKER
// ============================================================================
self.addEventListener('install', (event) => {
  console.log('[SW] Instalando Service Worker v2...');
  
  event.waitUntil(
    Promise.all([
      // Cache recursos estáticos
      caches.open(STATIC_CACHE).then(cache => {
        console.log('[SW] Cacheando recursos estáticos');
        return cache.addAll(STATIC_URLS);
      }),
      
      // Pré-cache recursos da API críticos
      caches.open(API_CACHE).then(cache => {
        console.log('[SW] Pré-cacheando dados da API');
        return Promise.allSettled(
          API_URLS.map(url => 
            fetch(url)
              .then(response => response.ok ? cache.put(url, response) : null)
              .catch(() => null) // Ignora erros de pré-cache
          )
        );
      })
    ]).then(() => {
      console.log('[SW] Service Worker instalado com sucesso');
      // Força a ativação imediata
      return self.skipWaiting();
    })
  );
});

// ============================================================================
// ATIVAÇÃO DO SERVICE WORKER
// ============================================================================
self.addEventListener('activate', (event) => {
  console.log('[SW] Ativando Service Worker v2...');
  
  event.waitUntil(
    Promise.all([
      // Limpa caches antigos
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (![
              CACHE_NAME, STATIC_CACHE, DYNAMIC_CACHE, 
              API_CACHE, IMAGE_CACHE
            ].includes(cacheName)) {
              console.log('[SW] Removendo cache antigo:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Assume controle de todas as abas
      self.clients.claim()
    ]).then(() => {
      console.log('[SW] Service Worker ativado e assumiu controle');
    })
  );
});

// ============================================================================
// INTERCEPTAÇÃO DE REQUISIÇÕES
// ============================================================================
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Ignora requisições não-HTTP
  if (!request.url.startsWith('http')) return;
  
  // Estratégia baseada no tipo de recurso
  if (isStaticResource(url)) {
    event.respondWith(handleStaticResource(request));
  } else if (isAPIRequest(url)) {
    event.respondWith(handleAPIRequest(request));
  } else if (isImageRequest(url)) {
    event.respondWith(handleImageRequest(request));
  } else {
    event.respondWith(handleDynamicResource(request));
  }
});

// ============================================================================
// ESTRATÉGIAS DE CACHE
// ============================================================================

// Cache First - Para recursos estáticos
async function handleStaticResource(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse && !isExpired(cachedResponse, CACHE_EXPIRATION.static)) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(STATIC_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('[SW] Erro ao buscar recurso estático:', error);
    return caches.match(request) || caches.match('/offline.html');
  }
}

// Network First - Para requisições da API
async function handleAPIRequest(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(API_CACHE);
      cache.put(request, networkResponse.clone());
      return networkResponse;
    }
    
    throw new Error('Network response not ok');
  } catch (error) {
    console.log('[SW] Falha na rede, buscando no cache:', error);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      // Adiciona header indicando que é do cache
      const response = cachedResponse.clone();
      response.headers.set('X-Served-By', 'ServiceWorker-Cache');
      return response;
    }
    
    // Se for POST/PUT/DELETE, adiciona à fila de sincronização
    if (['POST', 'PUT', 'DELETE'].includes(request.method)) {
      await queueRequest(request);
      return new Response(
        JSON.stringify({ 
          success: false, 
          message: 'Operação salva para sincronização posterior',
          queued: true 
        }),
        { 
          status: 202,
          headers: { 'Content-Type': 'application/json' }
        }
      );
    }
    
    return new Response(
      JSON.stringify({ error: 'Sem conexão e dados não disponíveis offline' }),
      { 
        status: 503,
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Cache First - Para imagens
async function handleImageRequest(request) {
  try {
    const cachedResponse = await caches.match(request);
    if (cachedResponse && !isExpired(cachedResponse, CACHE_EXPIRATION.images)) {
      return cachedResponse;
    }
    
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const cache = await caches.open(IMAGE_CACHE);
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    console.log('[SW] Erro ao buscar imagem:', error);
    return caches.match(request) || generatePlaceholderImage();
  }
}

// Stale While Revalidate - Para recursos dinâmicos
async function handleDynamicResource(request) {
  const cachedResponse = await caches.match(request);
  
  const fetchPromise = fetch(request).then(networkResponse => {
    if (networkResponse.ok) {
      const cache = caches.open(DYNAMIC_CACHE);
      cache.then(c => c.put(request, networkResponse.clone()));
    }
    return networkResponse;
  }).catch(() => cachedResponse);
  
  return cachedResponse || fetchPromise;
}

// ============================================================================
// SINCRONIZAÇÃO EM BACKGROUND
// ============================================================================
self.addEventListener('sync', (event) => {
  console.log('[SW] Evento de sincronização:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(processSyncQueue());
  } else if (event.tag.startsWith('auto-backup-')) {
    const companyId = event.tag.replace('auto-backup-', '');
    event.waitUntil(performAutoBackup(companyId));
  }
});

// Processa fila de sincronização
async function processSyncQueue() {
  console.log('[SW] Processando fila de sincronização...');
  
  const queue = await getStoredQueue();
  const processedItems = [];
  
  for (const item of queue) {
    try {
      const response = await fetch(item.request.url, {
        method: item.request.method,
        headers: item.request.headers,
        body: item.request.body
      });
      
      if (response.ok) {
        processedItems.push(item.id);
        console.log('[SW] Item sincronizado:', item.id);
        
        // Notifica o cliente sobre o sucesso
        notifyClients({
          type: 'SYNC_SUCCESS',
          data: { id: item.id, response: await response.json() }
        });
      }
    } catch (error) {
      console.log('[SW] Erro ao sincronizar item:', item.id, error);
    }
  }
  
  // Remove itens processados da fila
  if (processedItems.length > 0) {
    await removeFromQueue(processedItems);
  }
}

// Adiciona requisição à fila de sincronização
async function queueRequest(request) {
  const item = {
    id: Date.now() + Math.random(),
    request: {
      url: request.url,
      method: request.method,
      headers: Object.fromEntries(request.headers.entries()),
      body: await request.text()
    },
    timestamp: Date.now()
  };
  
  syncQueue.push(item);
  await storeQueue(syncQueue);
  
  // Registra sincronização em background
  if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
    const registration = await self.registration;
    await registration.sync.register('background-sync');
  }
}

// ============================================================================
// NOTIFICAÇÕES PUSH
// ============================================================================
self.addEventListener('push', (event) => {
  console.log('[SW] Notificação push recebida');
  
  const options = {
    body: 'Você tem novas atualizações no TechZe Diagnóstico',
    icon: '/icons/icon-192x192.png.svg',
    badge: '/icons/icon-72x72.png.svg',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Abrir App',
        icon: '/icons/icon-192x192.png.svg'
      },
      {
        action: 'close',
        title: 'Fechar',
        icon: '/icons/icon-192x192.png.svg'
      }
    ]
  };
  
  if (event.data) {
    const data = event.data.json();
    options.body = data.body || options.body;
    options.data = { ...options.data, ...data };
  }
  
  event.waitUntil(
    self.registration.showNotification('TechZe Diagnóstico', options)
  );
});

// Manipula cliques em notificações
self.addEventListener('notificationclick', (event) => {
  console.log('[SW] Clique em notificação:', event.action);
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

// Verifica se é um recurso estático
function isStaticResource(url) {
  return url.pathname.match(/\.(js|css|html|ico|svg|png|jpg|jpeg|gif|woff|woff2|ttf)$/) ||
         url.pathname === '/' ||
         url.pathname === '/index.html' ||
         url.pathname === '/manifest.webmanifest';
}

// Verifica se é uma requisição da API
function isAPIRequest(url) {
  return url.pathname.startsWith('/api/') ||
         url.hostname.includes('api.techzediagnostico.com');
}

// Verifica se é uma requisição de imagem
function isImageRequest(url) {
  return url.pathname.match(/\.(png|jpg|jpeg|gif|svg|webp|ico)$/);
}

// Verifica se o cache expirou
function isExpired(response, maxAge) {
  const dateHeader = response.headers.get('date');
  if (!dateHeader) return false;
  
  const date = new Date(dateHeader);
  return (Date.now() - date.getTime()) > maxAge;
}

// Gera imagem placeholder
function generatePlaceholderImage() {
  const svg = `
    <svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
      <rect width="200" height="200" fill="#f0f0f0"/>
      <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#999">Imagem não disponível</text>
    </svg>
  `;
  
  return new Response(svg, {
    headers: {
      'Content-Type': 'image/svg+xml',
      'Cache-Control': 'no-cache'
    }
  });
}

// Armazena fila no IndexedDB
async function storeQueue(queue) {
  // Implementação simplificada usando localStorage como fallback
  try {
    localStorage.setItem('sw-sync-queue', JSON.stringify(queue));
  } catch (error) {
    console.log('[SW] Erro ao armazenar fila:', error);
  }
}

// Recupera fila do IndexedDB
async function getStoredQueue() {
  try {
    const stored = localStorage.getItem('sw-sync-queue');
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.log('[SW] Erro ao recuperar fila:', error);
    return [];
  }
}

// Remove itens da fila
async function removeFromQueue(itemIds) {
  try {
    const queue = await getStoredQueue();
    const filteredQueue = queue.filter(item => !itemIds.includes(item.id));
    await storeQueue(filteredQueue);
    syncQueue = filteredQueue;
  } catch (error) {
    console.log('[SW] Erro ao remover da fila:', error);
  }
}

// Notifica clientes
function notifyClients(message) {
  self.clients.matchAll().then(clients => {
    clients.forEach(client => {
      client.postMessage(message);
    });
  });
}

// Executa backup automático
async function performAutoBackup(companyId) {
  try {
    const response = await fetch(`/api/v1/backup/auto/${companyId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      console.log('[SW] Backup automático executado para empresa:', companyId);
      
      // Notifica sobre o backup bem-sucedido
      await self.registration.showNotification('Backup Automático', {
        body: 'Backup dos dados realizado com sucesso',
        icon: '/icons/icon-192x192.png.svg',
        tag: 'auto-backup'
      });
    }
  } catch (error) {
    console.log('[SW] Erro no backup automático:', error);
  }
}

// Manipula mensagens do cliente
self.addEventListener('message', (event) => {
  console.log('[SW] Mensagem recebida:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  } else if (event.data && event.data.type === 'GET_CACHE_STATUS') {
    event.ports[0].postMessage({
      caches: {
        static: STATIC_CACHE,
        dynamic: DYNAMIC_CACHE,
        api: API_CACHE,
        images: IMAGE_CACHE
      },
      queueSize: syncQueue.length
    });
  }
});

console.log('[SW] Service Worker TechZe v2 carregado com sucesso');