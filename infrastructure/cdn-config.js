/**
 * Advanced CDN Configuration
 * Sistema enterprise de configuração de CDN
 */

// Cloudflare CDN Configuration
export const cloudflareConfig = {
  // Zone settings
  zoneId: process.env.CLOUDFLARE_ZONE_ID,
  apiToken: process.env.CLOUDFLARE_API_TOKEN,
  
  // Cache rules
  cacheRules: {
    static: {
      match: '*.{css,js,png,jpg,jpeg,gif,svg,ico,woff,woff2}',
      ttl: 31536000, // 1 year
      browserTtl: 86400 // 1 day
    },
    dynamic: {
      match: '/api/*',
      ttl: 300, // 5 minutes
      browserTtl: 0
    },
    html: {
      match: '*.html',
      ttl: 3600, // 1 hour
      browserTtl: 1800 // 30 minutes
    }
  },
  
  // Security settings
  security: {
    minify: {
      css: true,
      js: true,
      html: true
    },
    compression: 'gzip',
    ssl: 'strict',
    firewall: {
      enabled: true,
      rules: ['block-malicious-ips', 'rate-limit']
    }
  },
  
  // Performance optimizations
  performance: {
    polish: 'lossy',
    mirage: true,
    rocketLoader: true,
    autoMinify: true
  }
}

// AWS CloudFront Configuration
export const cloudFrontConfig = {
  distributionId: process.env.AWS_CLOUDFRONT_DISTRIBUTION_ID,
  region: process.env.AWS_REGION || 'us-east-1',
  
  // Cache behaviors
  cacheBehaviors: [
    {
      pathPattern: '/static/*',
      targetOrigin: 'origin-static',
      viewerProtocolPolicy: 'redirect-to-https',
      cachePolicyId: 'static-assets',
      ttl: {
        default: 86400,
        max: 31536000,
        min: 0
      }
    },
    {
      pathPattern: '/api/*',
      targetOrigin: 'origin-api',
      viewerProtocolPolicy: 'https-only',
      cachePolicyId: 'api-cache',
      ttl: {
        default: 300,
        max: 3600,
        min: 0
      }
    }
  ],
  
  // Origins
  origins: [
    {
      id: 'origin-static',
      domainName: 's3-bucket.amazonaws.com',
      s3OriginConfig: {
        originAccessIdentity: process.env.AWS_OAI
      }
    },
    {
      id: 'origin-api',
      domainName: 'api.techreparo.com',
      customOriginConfig: {
        httpPort: 80,
        httpsPort: 443,
        originProtocolPolicy: 'https-only'
      }
    }
  ],
  
  // Error pages
  errorPages: [
    {
      errorCode: 404,
      responseCode: 404,
      responsePage: '/error/404.html',
      ttl: 300
    },
    {
      errorCode: 500,
      responseCode: 500,
      responsePage: '/error/500.html',
      ttl: 0
    }
  ]
}

// CDN Optimization Functions
export class CDNOptimizer {
  constructor(provider = 'cloudflare') {
    this.provider = provider
    this.config = provider === 'cloudflare' ? cloudflareConfig : cloudFrontConfig
  }
  
  /**
   * Generate optimized URLs for assets
   */
  getOptimizedUrl(assetPath, options = {}) {
    const baseUrl = this.getBaseUrl()
    const params = this.buildOptimizationParams(options)
    
    return `${baseUrl}${assetPath}${params ? '?' + params : ''}`
  }
  
  /**
   * Get CDN base URL
   */
  getBaseUrl() {
    if (this.provider === 'cloudflare') {
      return process.env.CLOUDFLARE_CDN_URL || 'https://cdn.techreparo.com'
    } else {
      return process.env.AWS_CDN_URL || 'https://d1234567890.cloudfront.net'
    }
  }
  
  /**
   * Build optimization parameters
   */
  buildOptimizationParams(options) {
    const params = new URLSearchParams()
    
    if (options.width) params.append('w', options.width)
    if (options.height) params.append('h', options.height)
    if (options.quality) params.append('q', options.quality)
    if (options.format) params.append('f', options.format)
    if (options.dpr) params.append('dpr', options.dpr)
    
    return params.toString()
  }
  
  /**
   * Purge cache for specific URLs
   */
  async purgeCache(urls) {
    if (this.provider === 'cloudflare') {
      return this.purgeCloudflareCache(urls)
    } else {
      return this.purgeCloudFrontCache(urls)
    }
  }
  
  async purgeCloudflareCache(urls) {
    const response = await fetch(
      `https://api.cloudflare.com/client/v4/zones/${this.config.zoneId}/purge_cache`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.config.apiToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ files: urls })
      }
    )
    
    return response.json()
  }
  
  async purgeCloudFrontCache(urls) {
    // AWS SDK implementation would go here
    console.log('Purging CloudFront cache for:', urls)
    return { success: true }
  }
}

// Asset optimization configuration
export const assetOptimization = {
  images: {
    formats: ['webp', 'avif', 'jpeg'],
    quality: {
      webp: 85,
      avif: 80,
      jpeg: 85
    },
    sizes: [320, 640, 1024, 1920],
    progressive: true
  },
  
  fonts: {
    preload: ['Inter-Regular.woff2', 'Inter-Bold.woff2'],
    display: 'swap',
    formats: ['woff2', 'woff']
  },
  
  scripts: {
    minify: true,
    sourceMaps: process.env.NODE_ENV === 'development',
    splitting: true,
    treeshaking: true
  },
  
  styles: {
    minify: true,
    autoprefixer: true,
    purgeCss: true,
    criticalCss: true
  }
}

// Performance budgets
export const performanceBudgets = {
  javascript: 250 * 1024, // 250KB
  css: 50 * 1024,         // 50KB
  images: 500 * 1024,     // 500KB
  fonts: 100 * 1024,      // 100KB
  total: 1024 * 1024      // 1MB
}

// Cache headers configuration
export const cacheHeaders = {
  static: {
    'Cache-Control': 'public, max-age=31536000, immutable',
    'Expires': new Date(Date.now() + 31536000000).toUTCString()
  },
  dynamic: {
    'Cache-Control': 'public, max-age=300, s-maxage=300',
    'Vary': 'Accept-Encoding'
  },
  api: {
    'Cache-Control': 'public, max-age=300, stale-while-revalidate=60',
    'Vary': 'Accept, Accept-Encoding'
  },
  noCache: {
    'Cache-Control': 'no-cache, no-store, must-revalidate',
    'Pragma': 'no-cache',
    'Expires': '0'
  }
}

export default {
  cloudflareConfig,
  cloudFrontConfig,
  CDNOptimizer,
  assetOptimization,
  performanceBudgets,
  cacheHeaders
} 