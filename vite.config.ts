import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// CDN Configuration
const CDN_BASE_URL = process.env.VITE_CDN_URL || ''
const IS_PRODUCTION = process.env.NODE_ENV === 'production'
const USE_CDN = IS_PRODUCTION && CDN_BASE_URL

export default defineConfig({
  plugins: [react()],
  
  // Base URL for assets (CDN in production)
  base: USE_CDN ? CDN_BASE_URL : '/',
  
  // Build optimizations
  build: {
    // Output directory
    outDir: 'dist',
    
    // Generate manifest for asset mapping
    manifest: true,
    
    // Optimize bundle splitting
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
      },
      output: {
        // Asset naming with hash for cache busting
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.')
          const extType = info[info.length - 1]
          
          // Organize assets by type
          if (/\.(png|jpe?g|svg|gif|tiff|bmp|ico)$/i.test(assetInfo.name)) {
            return `images/[name]-[hash][extname]`
          }
          if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name)) {
            return `fonts/[name]-[hash][extname]`
          }
          if (/\.(css)$/i.test(assetInfo.name)) {
            return `styles/[name]-[hash][extname]`
          }
          
          return `assets/[name]-[hash][extname]`
        },
        
        // JS chunk naming
        chunkFileNames: 'js/[name]-[hash].js',
        entryFileNames: 'js/[name]-[hash].js',
        
        // Manual chunk splitting for better caching
        manualChunks: {
          // Vendor libraries
          vendor: ['react', 'react-dom'],
          
          // Chart libraries (if used)
          charts: ['recharts', 'chart.js'],
          
          // UI libraries
          ui: ['@headlessui/react', '@heroicons/react'],
          
          // Utilities
          utils: ['date-fns', 'lodash-es']
        }
      }
    },
    
    // Minification
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: IS_PRODUCTION,
        drop_debugger: IS_PRODUCTION,
        pure_funcs: IS_PRODUCTION ? ['console.log', 'console.info'] : []
      },
      mangle: true,
      format: {
        comments: false
      }
    },
    
    // Source maps for production debugging
    sourcemap: IS_PRODUCTION ? 'hidden' : true,
    
    // Chunk size warnings
    chunkSizeWarningLimit: 1000,
    
    // CSS code splitting
    cssCodeSplit: true,
    
    // Asset inlining threshold
    assetsInlineLimit: 4096
  },
  
  // Development server
  server: {
    port: 3000,
    host: true,
    
    // Proxy API requests in development
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  
  // Preview server (production build testing)
  preview: {
    port: 3000,
    host: true
  },
  
  // Path aliases
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components'),
      '@pages': resolve(__dirname, 'src/pages'),
      '@hooks': resolve(__dirname, 'src/hooks'),
      '@services': resolve(__dirname, 'src/services'),
      '@types': resolve(__dirname, 'src/types'),
      '@utils': resolve(__dirname, 'src/lib'),
      '@styles': resolve(__dirname, 'src/styles')
    }
  },
  
  // CSS configuration
  css: {
    modules: {
      localsConvention: 'camelCase'
    },
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    },
    postcss: {
      plugins: [
        require('tailwindcss'),
        require('autoprefixer'),
        ...(IS_PRODUCTION ? [
          require('cssnano')({
            preset: 'default'
          })
        ] : [])
      ]
    }
  },
  
  // Environment variables
  define: {
    __CDN_URL__: JSON.stringify(CDN_BASE_URL),
    __BUILD_DATE__: JSON.stringify(new Date().toISOString()),
    __VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0')
  },
  
  // Dependency optimization
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      '@supabase/supabase-js'
    ],
    exclude: ['@vite/client', '@vite/env']
  },
  
  // Asset handling
  assetsInclude: [
    '**/*.png',
    '**/*.jpg', 
    '**/*.jpeg',
    '**/*.gif',
    '**/*.svg',
    '**/*.webp',
    '**/*.avif',
    '**/*.woff',
    '**/*.woff2',
    '**/*.eot',
    '**/*.ttf',
    '**/*.otf'
  ],
  
  // Worker configuration
  worker: {
    format: 'es',
    plugins: [react()]
  }
}) 