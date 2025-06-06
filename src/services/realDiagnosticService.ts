
interface SystemInfo {
  os: string;
  os_version: string;
  processor: string;
  ram: string;
  storage: string;
  screen_resolution: string;
  user_agent: string;
}

interface HardwareMetrics {
  cpu: {
    cores: number;
    threads: number;
    usage_percentage: number;
    temperature: number | null;
  };
  memory: {
    total_gb: number;
    available_gb: number;
    usage_percentage: number;
    type: string;
  };
  disk: {
    total_gb: number;
    available_gb: number;
    usage_percentage: number;
    type: string;
    read_speed: number | null;
    write_speed: number | null;
  };
  network: {
    connection_type: string;
    download_speed: number | null;
    upload_speed: number | null;
    latency: number | null;
    ip_address: string | null;
  };
  graphics: {
    renderer: string;
    vendor: string;
    memory_mb: number | null;
  };
  battery: {
    level: number | null;
    charging: boolean | null;
    estimated_time: number | null;
  };
}

export class RealDiagnosticService {
  private static instance: RealDiagnosticService;

  static getInstance(): RealDiagnosticService {
    if (!RealDiagnosticService.instance) {
      RealDiagnosticService.instance = new RealDiagnosticService();
    }
    return RealDiagnosticService.instance;
  }

  async getSystemInfo(): Promise<SystemInfo> {
    const navigator = window.navigator;
    const screen = window.screen;
    
    // Detectar OS
    const userAgent = navigator.userAgent;
    let os = 'Unknown';
    let osVersion = 'Unknown';
    
    if (userAgent.includes('Windows NT')) {
      os = 'Windows';
      const versionMatch = userAgent.match(/Windows NT ([\d.]+)/);
      osVersion = versionMatch ? this.getWindowsVersion(versionMatch[1]) : 'Unknown';
    } else if (userAgent.includes('Mac OS X')) {
      os = 'macOS';
      const versionMatch = userAgent.match(/Mac OS X ([\d_]+)/);
      osVersion = versionMatch ? versionMatch[1].replace(/_/g, '.') : 'Unknown';
    } else if (userAgent.includes('Linux')) {
      os = 'Linux';
      osVersion = 'Unknown';
    } else if (userAgent.includes('Android')) {
      os = 'Android';
      const versionMatch = userAgent.match(/Android ([\d.]+)/);
      osVersion = versionMatch ? versionMatch[1] : 'Unknown';
    } else if (userAgent.includes('iPhone') || userAgent.includes('iPad')) {
      os = 'iOS';
      const versionMatch = userAgent.match(/OS ([\d_]+)/);
      osVersion = versionMatch ? versionMatch[1].replace(/_/g, '.') : 'Unknown';
    }

    // Estimar RAM baseado em deviceMemory (se disponível)
    const deviceMemory = (navigator as any).deviceMemory;
    const ramEstimate = deviceMemory ? `${deviceMemory} GB` : 'Unknown';

    // Detectar processador
    const hardwareConcurrency = navigator.hardwareConcurrency || 1;
    const processor = `${hardwareConcurrency} cores detected`;

    return {
      os,
      os_version: osVersion,
      processor,
      ram: ramEstimate,
      storage: 'Unknown', // Não acessível via browser
      screen_resolution: `${screen.width}x${screen.height}`,
      user_agent: userAgent
    };
  }

  async getHardwareMetrics(): Promise<HardwareMetrics> {
    const navigator = window.navigator;
    const performance = window.performance;

    // CPU Metrics
    const cores = navigator.hardwareConcurrency || 1;
    const cpuUsage = await this.estimateCPUUsage();

    // Memory Metrics (estimado)
    const memoryInfo = (performance as any).memory;
    const memoryMetrics = this.calculateMemoryMetrics(memoryInfo);

    // Storage Metrics (estimado via Persistent Storage API)
    const storageMetrics = await this.getStorageMetrics();

    // Network Metrics
    const networkMetrics = await this.getNetworkMetrics();

    // Graphics Metrics
    const graphicsMetrics = this.getGraphicsMetrics();

    // Battery Metrics
    const batteryMetrics = await this.getBatteryMetrics();

    return {
      cpu: {
        cores,
        threads: cores * 2, // Estimativa (hyperthreading)
        usage_percentage: cpuUsage,
        temperature: null // Não acessível via browser
      },
      memory: memoryMetrics,
      disk: storageMetrics,
      network: networkMetrics,
      graphics: graphicsMetrics,
      battery: batteryMetrics
    };
  }

  private async estimateCPUUsage(): Promise<number> {
    return new Promise((resolve) => {
      const startTime = performance.now();
      const iterations = 100000;
      
      // Simular carga de trabalho
      let dummy = 0;
      for (let i = 0; i < iterations; i++) {
        dummy += Math.random();
      }
      
      const endTime = performance.now();
      const executionTime = endTime - startTime;
      
      // Estimar uso baseado no tempo de execução
      const estimatedUsage = Math.min(100, Math.max(5, (executionTime / 10) * 20));
      resolve(Math.round(estimatedUsage));
    });
  }

  private calculateMemoryMetrics(memoryInfo: any) {
    if (memoryInfo) {
      const totalBytes = memoryInfo.jsHeapSizeLimit;
      const usedBytes = memoryInfo.usedJSHeapSize;
      
      const totalGB = totalBytes / (1024 * 1024 * 1024);
      const usedGB = usedBytes / (1024 * 1024 * 1024);
      const availableGB = totalGB - usedGB;
      const usagePercentage = (usedGB / totalGB) * 100;

      return {
        total_gb: Number(totalGB.toFixed(2)),
        available_gb: Number(availableGB.toFixed(2)),
        usage_percentage: Number(usagePercentage.toFixed(1)),
        type: 'JavaScript Heap'
      };
    }

    return {
      total_gb: 8, // Estimativa padrão
      available_gb: 4,
      usage_percentage: 50,
      type: 'Estimated'
    };
  }

  private async getStorageMetrics() {
    try {
      if ('storage' in navigator && 'estimate' in navigator.storage) {
        const estimate = await navigator.storage.estimate();
        const totalBytes = estimate.quota || 0;
        const usedBytes = estimate.usage || 0;
        
        const totalGB = totalBytes / (1024 * 1024 * 1024);
        const usedGB = usedBytes / (1024 * 1024 * 1024);
        const availableGB = totalGB - usedGB;
        const usagePercentage = totalGB > 0 ? (usedGB / totalGB) * 100 : 0;

        return {
          total_gb: Number(totalGB.toFixed(2)),
          available_gb: Number(availableGB.toFixed(2)),
          usage_percentage: Number(usagePercentage.toFixed(1)),
          type: 'Browser Storage',
          read_speed: null,
          write_speed: null
        };
      }
    } catch (error) {
      console.warn('Erro ao obter métricas de armazenamento:', error);
    }

    return {
      total_gb: 500,
      available_gb: 250,
      usage_percentage: 50,
      type: 'Estimated SSD',
      read_speed: null,
      write_speed: null
    };
  }

  private async getNetworkMetrics() {
    const connection = (navigator as any).connection;
    
    let connectionType = 'Unknown';
    if (connection) {
      connectionType = connection.effectiveType || connection.type || 'Unknown';
    }

    return {
      connection_type: connectionType,
      download_speed: connection?.downlink || null,
      upload_speed: null, // Não disponível via API
      latency: connection?.rtt || null,
      ip_address: null // Não acessível via browser por segurança
    };
  }

  private getGraphicsMetrics() {
    try {
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      
      if (gl) {
        const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
        const renderer = debugInfo ? gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL) : 'Unknown';
        const vendor = debugInfo ? gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) : 'Unknown';
        
        return {
          renderer: renderer || 'WebGL Renderer',
          vendor: vendor || 'Unknown Vendor',
          memory_mb: null // Não acessível via browser
        };
      }
    } catch (error) {
      console.warn('Erro ao obter informações gráficas:', error);
    }

    return {
      renderer: 'Unknown',
      vendor: 'Unknown',
      memory_mb: null
    };
  }

  private async getBatteryMetrics() {
    try {
      const battery = await (navigator as any).getBattery?.();
      
      if (battery) {
        return {
          level: Math.round(battery.level * 100),
          charging: battery.charging,
          estimated_time: battery.dischargingTime === Infinity ? null : battery.dischargingTime
        };
      }
    } catch (error) {
      console.warn('API de bateria não disponível:', error);
    }

    return {
      level: null,
      charging: null,
      estimated_time: null
    };
  }

  private getWindowsVersion(ntVersion: string): string {
    const versions: { [key: string]: string } = {
      '10.0': 'Windows 10/11',
      '6.3': 'Windows 8.1',
      '6.2': 'Windows 8',
      '6.1': 'Windows 7',
      '6.0': 'Windows Vista',
      '5.1': 'Windows XP',
      '5.0': 'Windows 2000'
    };
    
    return versions[ntVersion] || `Windows NT ${ntVersion}`;
  }

  async runFullDiagnostic(deviceName: string = 'Meu Computador'): Promise<any> {
    console.log('🔧 Iniciando diagnóstico real do hardware...');
    
    try {
      const systemInfo = await this.getSystemInfo();
      const hardwareMetrics = await this.getHardwareMetrics();
      
      const diagnosticData = {
        device_name: deviceName,
        system_info: systemInfo,
        hardware_metrics: hardwareMetrics,
        timestamp: new Date().toISOString(),
        diagnostic_type: 'Real Hardware Scan'
      };

      console.log('✅ Diagnóstico concluído:', diagnosticData);
      return diagnosticData;
    } catch (error) {
      console.error('❌ Erro durante diagnóstico:', error);
      throw error;
    }
  }
}

export const realDiagnosticService = RealDiagnosticService.getInstance();
