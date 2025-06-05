/**
 * CDN Configuration for Static Assets
 * Configuração avançada de CDN para otimização de performance
 */

const CDN_CONFIG = {
  // CDN Providers Configuration
  providers: {
    cloudflare: {
      enabled: process.env.CLOUDFLARE_ENABLED === 'true',
      zone: process.env.CLOUDFLARE_ZONE_ID || '',
      token: process.env.CLOUDFLARE_API_TOKEN || '',
      baseUrl: process.env.CLOUDFLARE_CDN_URL || 'https://cdn.techreparo.com',
      settings: {
        caching: {
          browserTTL: 31536000, // 1 year
          edgeTTL: 2592000,     // 30 days
          cacheLevel: 'aggressive'
        },
        optimization: {
          minify: {
            css: true,
            js: true,
            html: true
          },
          compression: 'gzip',
          imageOptimization: true,
          webp: true,
          avif: true
        }
      }
    },
    aws: {
      enabled: process.env.AWS_CDN_ENABLED === 'true',
      distributionId: process.env.AWS_CLOUDFRONT_DISTRIBUTION_ID || '',
      baseUrl: process.env.AWS_CDN_URL || '',
      region: process.env.AWS_REGION || 'us-east-1'
    }
  },

  // Asset Types Configuration
  assets: {
    images: {
      extensions: ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.avif'],
      cacheTTL: 31536000, // 1 year
      optimization: {
        quality: 85,
        progressive: true,
        webp: true,
        avif: true,
        responsive: true
      }
    },
    styles: {
      extensions: ['.css'],
      cacheTTL: 31536000, // 1 year
      optimization: {
        minify: true,
        purge: true,
        critical: true
      }
    },
    scripts: {
      extensions: ['.js', '.mjs'],
      cacheTTL: 31536000, // 1 year
      optimization: {
        minify: true,
        treeshake: true,
        compression: 'gzip'
      }
    },
    fonts: {
      extensions: ['.woff', '.woff2', '.ttf', '.eot'],
      cacheTTL: 31536000, // 1 year
      preload: true
    },
    media: {
      extensions: ['.mp4', '.webm', '.mp3', '.wav'],
      cacheTTL: 2592000, // 30 days
      streaming: true
    }
  },

  // Performance Optimization
  performance: {
    preload: {
      critical: ['main.css', 'main.js'],
      fonts: ['inter-var.woff2'],
      images: ['logo.svg', 'hero-image.webp']
    },
    prefetch: {
      routes: ['/dashboard', '/diagnostics'],
      assets: ['chart-libs.js', 'icons.svg']
    },
    http2Push: true,
    serviceWorker: true,
    resourceHints: true
  },

  // Security Configuration
  security: {
    cors: {
      origins: [
        'https://techreparo.com',
        'https://www.techreparo.com',
        'https://app.techreparo.com'
      ],
      credentials: false
    },
    headers: {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Referrer-Policy': 'strict-origin-when-cross-origin'
    },
    hotlinking: false,
    geoBlocking: false
  },

  // Monitoring and Analytics
  monitoring: {
    realUserMonitoring: true,
    edgeLogs: true,
    performanceMetrics: true,
    errorTracking: true,
    bandwidthAlerts: true
  }
};

/**
 * CDN URL Builder
 * Constrói URLs otimizadas para assets via CDN
 */
class CDNManager {
  constructor(config = CDN_CONFIG) {
    this.config = config;
    this.activeProvider = this.getActiveProvider();
  }

  getActiveProvider() {
    if (this.config.providers.cloudflare.enabled) {
      return 'cloudflare';
    }
    if (this.config.providers.aws.enabled) {
      return 'aws';
    }
    return null;
  }

  buildAssetUrl(assetPath, options = {}) {
    if (!this.activeProvider) {
      return assetPath; // Fallback to local
    }

    const provider = this.config.providers[this.activeProvider];
    const baseUrl = provider.baseUrl;
    
    // Remove leading slash if present
    const cleanPath = assetPath.startsWith('/') ? assetPath.slice(1) : assetPath;
    
    // Add optimization parameters
    const params = this.buildOptimizationParams(assetPath, options);
    const paramString = params ? `?${params}` : '';
    
    return `${baseUrl}/${cleanPath}${paramString}`;
  }

  buildOptimizationParams(assetPath, options) {
    const extension = this.getFileExtension(assetPath);
    const assetType = this.getAssetType(extension);
    
    if (!assetType) return '';

    const params = new URLSearchParams();
    
    // Image optimizations
    if (assetType === 'images') {
      if (options.width) params.append('w', options.width);
      if (options.height) params.append('h', options.height);
      if (options.quality) params.append('q', options.quality);
      if (options.format) params.append('f', options.format);
      
      // Auto format detection
      if (this.config.assets.images.optimization.webp) {
        params.append('auto', 'webp');
      }
    }
    
    // Compression
    if (options.compress !== false) {
      params.append('compress', 'true');
    }
    
    return params.toString();
  }

  getFileExtension(filePath) {
    return filePath.substring(filePath.lastIndexOf('.')).toLowerCase();
  }

  getAssetType(extension) {
    for (const [type, config] of Object.entries(this.config.assets)) {
      if (config.extensions.includes(extension)) {
        return type;
      }
    }
    return null;
  }

  // Preload critical assets
  generatePreloadTags() {
    const tags = [];
    const { preload } = this.config.performance;
    
    // Critical CSS and JS
    preload.critical.forEach(asset => {
      const url = this.buildAssetUrl(asset);
      const type = asset.endsWith('.css') ? 'style' : 'script';
      tags.push(`<link rel="preload" href="${url}" as="${type}">`);
    });
    
    // Fonts
    preload.fonts.forEach(font => {
      const url = this.buildAssetUrl(`fonts/${font}`);
      tags.push(`<link rel="preload" href="${url}" as="font" type="font/woff2" crossorigin>`);
    });
    
    // Critical images
    preload.images.forEach(image => {
      const url = this.buildAssetUrl(`images/${image}`);
      tags.push(`<link rel="preload" href="${url}" as="image">`);
    });
    
    return tags.join('\n');
  }

  // Service Worker cache strategy
  generateSWCacheConfig() {
    return {
      assets: Object.entries(this.config.assets).map(([type, config]) => ({
        type,
        extensions: config.extensions,
        cacheTTL: config.cacheTTL,
        strategy: config.cacheTTL > 86400 ? 'CacheFirst' : 'StaleWhileRevalidate'
      }))
    };
  }
}

// Export configurations
module.exports = {
  CDN_CONFIG,
  CDNManager
};

// ES6 Export
export { CDN_CONFIG, CDNManager }; 