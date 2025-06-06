import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { VitePWA } from 'vite-plugin-pwa';
// import { componentTagger } from "lovable-tagger"; // Removido temporariamente

export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [
    react(),
    // mode === 'development' && componentTagger(), // Removido temporariamente
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'robots.txt', 'icons/*.svg', 'offline.html'],
      manifest: {
        name: 'TechZe Diagnóstico',
        short_name: 'TechZe',
        description: 'Aplicativo de diagnóstico de dispositivos TechZe - PWA Completo',
        theme_color: '#00ffff',
        background_color: '#0a0a0a',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
        categories: ['productivity', 'utilities', 'business'],
        lang: 'pt-BR',
        icons: [
          {
            src: 'icons/icon-72x72.png.svg',
            sizes: '72x72',
            type: 'image/svg+xml'
          },
          {
            src: 'icons/icon-96x96.png.svg',
            sizes: '96x96',
            type: 'image/svg+xml'
          },
          {
            src: 'icons/icon-128x128.png.svg',
            sizes: '128x128',
            type: 'image/svg+xml'
          },
          {
            src: 'icons/icon-144x144.png.svg',
            sizes: '144x144',
            type: 'image/svg+xml'
          },
          {
            src: 'icons/icon-152x152.png.svg',
            sizes: '152x152',
            type: 'image/svg+xml'
          },
          {
            src: 'icons/icon-192x192.png.svg',
            sizes: '192x192',
            type: 'image/svg+xml'
          },
          {
            src: 'icons/icon-384x384.png.svg',
            sizes: '384x384',
            type: 'image/svg+xml'
          },
          {
            src: 'icons/icon-512x512.png.svg',
            sizes: '512x512',
            type: 'image/svg+xml'
          },
          {
            src: 'icons/maskable-icon-512x512.png.svg',
            sizes: '512x512',
            type: 'image/svg+xml',
            purpose: 'maskable'
          }
        ],
        shortcuts: [
          {
            name: 'Novo Diagnóstico',
            short_name: 'Diagnóstico',
            description: 'Executar novo diagnóstico',
            url: '/diagnostic',
            icons: [{ src: 'icons/icon-192x192.png.svg', sizes: '192x192' }]
          },
          {
            name: 'Dashboard',
            short_name: 'Dashboard',
            description: 'Ver painel de controle',
            url: '/dashboard',
            icons: [{ src: 'icons/icon-192x192.png.svg', sizes: '192x192' }]
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff,woff2,ttf}'],
        maximumFileSizeToCacheInBytes: 5000000, // 5MB
        cleanupOutdatedCaches: true,
        skipWaiting: true,
        clientsClaim: true,
        runtimeCaching: [
          // API Cache - Network First
          {
            urlPattern: /^https:\/\/api\.techzediagnostico\.com\/.*$/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache-v2',
              networkTimeoutSeconds: 10,
              expiration: {
                maxEntries: 200,
                maxAgeSeconds: 60 * 60 * 24 * 7, // 1 semana
                purgeOnQuotaError: true
              },
              cacheableResponse: {
                statuses: [0, 200]
              },
              backgroundSync: {
                name: 'api-background-sync',
                options: {
                  maxRetentionTime: 24 * 60 // 24 horas
                }
              }
            }
          },
          // Local API Cache - Network First
          {
            urlPattern: /^\/api\/.*$/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'local-api-cache-v2',
              networkTimeoutSeconds: 5,
              expiration: {
                maxEntries: 150,
                maxAgeSeconds: 60 * 60 * 24 * 3, // 3 dias
                purgeOnQuotaError: true
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          },
          // Static Assets - Cache First
          {
            urlPattern: /\.(?:js|css|html)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'static-assets-v2',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 30, // 30 dias
                purgeOnQuotaError: true
              }
            }
          },
          // Images - Cache First
          {
            urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp|ico)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'images-cache-v2',
              expiration: {
                maxEntries: 200,
                maxAgeSeconds: 60 * 60 * 24 * 30, // 30 dias
                purgeOnQuotaError: true
              }
            }
          },
          // Fonts - Cache First
          {
            urlPattern: /\.(?:woff|woff2|ttf|eot)$/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'fonts-cache-v2',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24 * 365, // 1 ano
                purgeOnQuotaError: true
              }
            }
          },
          // Google Fonts - Stale While Revalidate
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'google-fonts-stylesheets-v2'
            }
          },
          {
            urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-webfonts-v2',
              expiration: {
                maxEntries: 30,
                maxAgeSeconds: 60 * 60 * 24 * 365 // 1 ano
              }
            }
          },
          // CDN Assets - Stale While Revalidate
          {
            urlPattern: /^https:\/\/cdn\..*/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'cdn-cache-v2',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 7 // 1 semana
              }
            }
          }
        ],
        navigateFallback: '/offline.html',
        navigateFallbackDenylist: [/^\/api\//]
      },
      devOptions: {
        enabled: true,
        type: 'module'
      }
    })
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
