
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { VitePWA } from 'vite-plugin-pwa';
import { componentTagger } from "lovable-tagger";

export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
  },
  plugins: [
    react(),
    mode === 'development' && componentTagger(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.ico', 'robots.txt', 'icons/*.svg'],
      manifest: {
        name: 'TechZe Diagnóstico',
        short_name: 'TechZe',
        description: 'Aplicativo de diagnóstico de dispositivos TechZe',
        theme_color: '#ffffff',
        background_color: '#ffffff',
        display: 'standalone',
        orientation: 'portrait',
        scope: '/',
        start_url: '/',
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
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/api\.techzediagnostico\.com\/.*$/,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 100,
                maxAgeSeconds: 60 * 60 * 24 * 7 // 1 semana
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          }
        ]
      }
    })
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
