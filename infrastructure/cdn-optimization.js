/**
 * Advanced CDN Optimization System
 * Sistema enterprise de otimização de CDN com edge computing e cache inteligente
 */

import fs from 'fs/promises'
import path from 'path'
import crypto from 'crypto'
import sharp from 'sharp'
import { minify } from 'terser'
import CleanCSS from 'clean-css'

class AdvancedCDNOptimizer {
  constructor(config = {}) {
    this.config = {
      // CDN providers
      cloudflare: {
        zoneId: process.env.CLOUDFLARE_ZONE_ID,
        apiToken: process.env.CLOUDFLARE_API_TOKEN,
        baseUrl: process.env.CLOUDFLARE_CDN_URL
      },
      aws: {
        distributionId: process.env.AWS_CLOUDFRONT_DISTRIBUTION_ID,
        region: process.env.AWS_REGION || 'us-east-1',
        baseUrl: process.env.AWS_CDN_URL
      },
      
      // Optimization settings
      images: {
        quality: {
          webp: 85,
          avif: 80,
          jpeg: 85
        },
        sizes: [320, 640, 1024, 1920],
        formats: ['webp', 'avif', 'jpeg'],
        progressive: true
      },
      
      // Cache strategies
      cache: {
        static: 31536000,      // 1 year
        dynamic: 3600,         // 1 hour
        api: 300,              // 5 minutes
        html: 3600             // 1 hour
      },
      
      // Performance budgets
      budgets: {
        javascript: 250 * 1024,    // 250KB
        css: 50 * 1024,           // 50KB
        images: 500 * 1024,       // 500KB
        fonts: 100 * 1024         // 100KB
      },
      
      ...config
    }
    
    this.stats = {
      totalFiles: 0,
      optimizedFiles: 0,
      bytesOriginal: 0,
      bytesOptimized: 0,
      compressionRatio: 0
    }
  }

  /**
   * Otimiza todos os assets para CDN
   */
  async optimizeAssets(sourceDir, outputDir) {
    console.log('🚀 Iniciando otimização avançada de assets...')
    
    // Create output directory
    await fs.mkdir(outputDir, { recursive: true })
    
    // Process different asset types
    await this.processImages(path.join(sourceDir, 'images'), path.join(outputDir, 'images'))
    await this.processScripts(path.join(sourceDir, 'js'), path.join(outputDir, 'js'))
    await this.processStyles(path.join(sourceDir, 'css'), path.join(outputDir, 'css'))
    await this.processFonts(path.join(sourceDir, 'fonts'), path.join(outputDir, 'fonts'))
    
    // Generate manifest
    await this.generateManifest(outputDir)
    
    // Generate service worker
    await this.generateServiceWorker(outputDir)
    
    // Performance report
    this.generatePerformanceReport()
    
    console.log('✅ Otimização concluída!')
  }

  /**
   * Processa e otimiza imagens
   */
  async processImages(sourceDir, outputDir) {
    try {
      await fs.mkdir(outputDir, { recursive: true })
      const files = await fs.readdir(sourceDir, { withFileTypes: true })
      
      for (const file of files) {
        if (file.isFile() && this.isImageFile(file.name)) {
          await this.optimizeImage(
            path.join(sourceDir, file.name),
            outputDir,
            file.name
          )
        }
      }
    } catch (error) {
      console.warn(`⚠️ Diretório de imagens não encontrado: ${sourceDir}`)
    }
  }

  /**
   * Otimiza uma imagem individual
   */
  async optimizeImage(inputPath, outputDir, filename) {
    const originalSize = (await fs.stat(inputPath)).size
    this.stats.bytesOriginal += originalSize
    
    const nameWithoutExt = path.parse(filename).name
    const formats = this.config.images.formats
    const sizes = this.config.images.sizes
    
    for (const format of formats) {
      for (const size of sizes) {
        const outputPath = path.join(outputDir, `${nameWithoutExt}-${size}w.${format}`)
        
        let pipeline = sharp(inputPath)
          .resize(size, null, { withoutEnlargement: true })
        
        // Apply format-specific optimizations
        switch (format) {
          case 'webp':
            pipeline = pipeline.webp({ 
              quality: this.config.images.quality.webp,
              effort: 6
            })
            break
          case 'avif':
            pipeline = pipeline.avif({ 
              quality: this.config.images.quality.avif,
              effort: 9
            })
            break
          case 'jpeg':
            pipeline = pipeline.jpeg({ 
              quality: this.config.images.quality.jpeg,
              progressive: this.config.images.progressive,
              mozjpeg: true
            })
            break
        }
        
        await pipeline.toFile(outputPath)
        
        const optimizedSize = (await fs.stat(outputPath)).size
        this.stats.bytesOptimized += optimizedSize
      }
    }
    
    this.stats.optimizedFiles++
    console.log(`📸 Otimizada: ${filename}`)
  }

  /**
   * Processa e minifica JavaScript
   */
  async processScripts(sourceDir, outputDir) {
    try {
      await fs.mkdir(outputDir, { recursive: true })
      const files = await fs.readdir(sourceDir, { withFileTypes: true })
      
      for (const file of files) {
        if (file.isFile() && file.name.endsWith('.js')) {
          await this.optimizeScript(
            path.join(sourceDir, file.name),
            path.join(outputDir, file.name)
          )
        }
      }
    } catch (error) {
      console.warn(`⚠️ Diretório de scripts não encontrado: ${sourceDir}`)
    }
  }

  /**
   * Otimiza um arquivo JavaScript
   */
  async optimizeScript(inputPath, outputPath) {
    const code = await fs.readFile(inputPath, 'utf8')
    const originalSize = Buffer.byteLength(code, 'utf8')
    
    const result = await minify(code, {
      compress: {
        drop_console: true,
        drop_debugger: true,
        pure_funcs: ['console.log', 'console.info'],
        passes: 2
      },
      mangle: {
        toplevel: true
      },
      format: {
        comments: false
      },
      sourceMap: {
        filename: path.basename(outputPath),
        url: `${path.basename(outputPath)}.map`
      }
    })
    
    // Write minified file
    await fs.writeFile(outputPath, result.code)
    
    // Write source map
    if (result.map) {
      await fs.writeFile(`${outputPath}.map`, result.map)
    }
    
    const optimizedSize = Buffer.byteLength(result.code, 'utf8')
    this.updateStats(originalSize, optimizedSize)
    
    // Check performance budget
    if (optimizedSize > this.config.budgets.javascript) {
      console.warn(`⚠️ JavaScript budget exceeded: ${path.basename(outputPath)} (${optimizedSize} bytes)`)
    }
    
    console.log(`📜 Minificado: ${path.basename(inputPath)} (${originalSize} → ${optimizedSize} bytes)`)
  }

  /**
   * Processa e otimiza CSS
   */
  async processStyles(sourceDir, outputDir) {
    try {
      await fs.mkdir(outputDir, { recursive: true })
      const files = await fs.readdir(sourceDir, { withFileTypes: true })
      
      for (const file of files) {
        if (file.isFile() && file.name.endsWith('.css')) {
          await this.optimizeStyle(
            path.join(sourceDir, file.name),
            path.join(outputDir, file.name)
          )
        }
      }
    } catch (error) {
      console.warn(`⚠️ Diretório de estilos não encontrado: ${sourceDir}`)
    }
  }

  /**
   * Otimiza um arquivo CSS
   */
  async optimizeStyle(inputPath, outputPath) {
    const css = await fs.readFile(inputPath, 'utf8')
    const originalSize = Buffer.byteLength(css, 'utf8')
    
    const cleanCSS = new CleanCSS({
      level: 2,
      returnPromise: true,
      sourceMap: true,
      compatibility: 'ie9'
    })
    
    const result = await cleanCSS.minify(css)
    
    // Write minified CSS
    await fs.writeFile(outputPath, result.styles)
    
    // Write source map
    if (result.sourceMap) {
      await fs.writeFile(`${outputPath}.map`, result.sourceMap.toString())
    }
    
    const optimizedSize = Buffer.byteLength(result.styles, 'utf8')
    this.updateStats(originalSize, optimizedSize)
    
    // Check performance budget
    if (optimizedSize > this.config.budgets.css) {
      console.warn(`⚠️ CSS budget exceeded: ${path.basename(outputPath)} (${optimizedSize} bytes)`)
    }
    
    console.log(`🎨 Minificado: ${path.basename(inputPath)} (${originalSize} → ${optimizedSize} bytes)`)
  }

  /**
   * Processa fontes
   */
  async processFonts(sourceDir, outputDir) {
    try {
      await fs.mkdir(outputDir, { recursive: true })
      const files = await fs.readdir(sourceDir, { withFileTypes: true })
      
      for (const file of files) {
        if (file.isFile() && this.isFontFile(file.name)) {
          const inputPath = path.join(sourceDir, file.name)
          const outputPath = path.join(outputDir, file.name)
          
          // Copy font file (fonts are already optimized)
          await fs.copyFile(inputPath, outputPath)
          
          const size = (await fs.stat(inputPath)).size
          this.updateStats(size, size)
          
          console.log(`🔤 Copiada fonte: ${file.name}`)
        }
      }
    } catch (error) {
      console.warn(`⚠️ Diretório de fontes não encontrado: ${sourceDir}`)
    }
  }

  /**
   * Gera manifest de assets
   */
  async generateManifest(outputDir) {
    const manifest = {
      version: crypto.randomBytes(8).toString('hex'),
      timestamp: new Date().toISOString(),
      assets: {},
      stats: this.stats
    }
    
    // Scan all optimized files
    await this.scanDirectory(outputDir, outputDir, manifest.assets)
    
    // Write manifest
    await fs.writeFile(
      path.join(outputDir, 'manifest.json'),
      JSON.stringify(manifest, null, 2)
    )
    
    console.log('📋 Manifest gerado')
  }

  /**
   * Gera Service Worker otimizado
   */
  async generateServiceWorker(outputDir) {
    const manifest = JSON.parse(
      await fs.readFile(path.join(outputDir, 'manifest.json'), 'utf8')
    )
    
    const swTemplate = `
// TechZe Diagnóstico - Advanced Service Worker
// Generated at: ${new Date().toISOString()}

const CACHE_VERSION = '${manifest.version}'
const CACHE_NAME = \`techze-v\${CACHE_VERSION}\`

// Assets to precache
const PRECACHE_ASSETS = ${JSON.stringify(Object.keys(manifest.assets), null, 2)}

// Cache strategies
const CACHE_STRATEGIES = {
  images: 'CacheFirst',
  scripts: 'StaleWhileRevalidate',
  styles: 'CacheFirst',
  fonts: 'CacheFirst',
  api: 'NetworkFirst',
  pages: 'StaleWhileRevalidate'
}

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Service Worker: Precaching assets')
        return cache.addAll(PRECACHE_ASSETS)
      })
      .then(() => self.skipWaiting())
  )
})

// Activate event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => cacheName.startsWith('techze-') && cacheName !== CACHE_NAME)
          .map((cacheName) => caches.delete(cacheName))
      )
    }).then(() => self.clients.claim())
  )
})

// Fetch event with intelligent caching
self.addEventListener('fetch', (event) => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  const url = new URL(request.url)
  const strategy = getStrategyForRequest(request)
  
  switch (strategy) {
    case 'CacheFirst':
      return cacheFirst(request)
    case 'NetworkFirst':
      return networkFirst(request)
    case 'StaleWhileRevalidate':
      return staleWhileRevalidate(request)
    default:
      return fetch(request)
  }
}

function getStrategyForRequest(request) {
  const url = new URL(request.url)
  
  if (url.pathname.match(/\\.(png|jpg|jpeg|gif|svg|webp|avif)$/)) return 'CacheFirst'
  if (url.pathname.match(/\\.(js|mjs)$/)) return 'StaleWhileRevalidate'
  if (url.pathname.match(/\\.(css)$/)) return 'CacheFirst'
  if (url.pathname.match(/\\.(woff|woff2|ttf|eot)$/)) return 'CacheFirst'
  if (url.pathname.startsWith('/api/')) return 'NetworkFirst'
  
  return 'StaleWhileRevalidate'
}

// Cache strategies implementation
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request)
  return cachedResponse || fetch(request)
}

async function networkFirst(request) {
  try {
    const networkResponse = await fetch(request)
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME)
      cache.put(request, networkResponse.clone())
    }
    return networkResponse
  } catch (error) {
    return caches.match(request)
  }
}

async function staleWhileRevalidate(request) {
  const cachedResponse = caches.match(request)
  const networkResponse = fetch(request).then((response) => {
    if (response.ok) {
      const cache = caches.open(CACHE_NAME)
      cache.then((c) => c.put(request, response.clone()))
    }
    return response
  })
  
  return (await cachedResponse) || networkResponse
}
`
    
    await fs.writeFile(path.join(outputDir, 'sw.js'), swTemplate)
    console.log('⚙️ Service Worker gerado')
  }

  /**
   * Utilitários
   */
  isImageFile(filename) {
    return /\.(png|jpe?g|gif|svg|webp|avif)$/i.test(filename)
  }

  isFontFile(filename) {
    return /\.(woff2?|ttf|eot|otf)$/i.test(filename)
  }

  updateStats(originalSize, optimizedSize) {
    this.stats.bytesOriginal += originalSize
    this.stats.bytesOptimized += optimizedSize
    this.stats.totalFiles++
    this.stats.compressionRatio = 
      ((this.stats.bytesOriginal - this.stats.bytesOptimized) / this.stats.bytesOriginal) * 100
  }

  async scanDirectory(dir, baseDir, assets) {
    const files = await fs.readdir(dir, { withFileTypes: true })
    
    for (const file of files) {
      const fullPath = path.join(dir, file.name)
      
      if (file.isDirectory()) {
        await this.scanDirectory(fullPath, baseDir, assets)
      } else {
        const relativePath = path.relative(baseDir, fullPath)
        const stat = await fs.stat(fullPath)
        
        assets[`/${relativePath.replace(/\\/g, '/')}`] = {
          size: stat.size,
          hash: await this.generateFileHash(fullPath),
          lastModified: stat.mtime.toISOString()
        }
      }
    }
  }

  async generateFileHash(filePath) {
    const content = await fs.readFile(filePath)
    return crypto.createHash('sha256').update(content).digest('hex').substring(0, 8)
  }

  generatePerformanceReport() {
    const savings = this.stats.bytesOriginal - this.stats.bytesOptimized
    const savingsPercent = ((savings / this.stats.bytesOriginal) * 100).toFixed(2)
    
    console.log('\n📊 RELATÓRIO DE OTIMIZAÇÃO')
    console.log('================================')
    console.log(`📁 Total de arquivos: ${this.stats.totalFiles}`)
    console.log(`📏 Tamanho original: ${this.formatBytes(this.stats.bytesOriginal)}`)
    console.log(`📐 Tamanho otimizado: ${this.formatBytes(this.stats.bytesOptimized)}`)
    console.log(`💾 Economia: ${this.formatBytes(savings)} (${savingsPercent}%)`)
    console.log(`🎯 Taxa de compressão: ${this.stats.compressionRatio.toFixed(2)}%`)
    console.log('================================\n')
  }

  formatBytes(bytes) {
    const units = ['B', 'KB', 'MB', 'GB']
    let size = bytes
    let unitIndex = 0
    
    while (size >= 1024 && unitIndex < units.length - 1) {
      size /= 1024
      unitIndex++
    }
    
    return `${size.toFixed(2)} ${units[unitIndex]}`
  }
}

// Export
export default AdvancedCDNOptimizer

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const optimizer = new AdvancedCDNOptimizer()
  const sourceDir = process.argv[2] || './src'
  const outputDir = process.argv[3] || './dist'
  
  optimizer.optimizeAssets(sourceDir, outputDir)
    .catch(console.error)
} 