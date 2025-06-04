
export interface DiagnosticMetrics {
  usage_percent: number;
  temperature?: number;
  frequency?: number;
  cores?: number;
  threads?: number;
  load_average?: number[];
}

export interface MemoryMetrics {
  total_gb: number;
  used_gb: number;
  available_gb: number;
  usage_percent: number;
  swap_total_gb?: number;
  swap_used_gb?: number;
}

export interface DiskMetrics {
  total_gb: number;
  used_gb: number;
  free_gb: number;
  usage_percent: number;
  read_speed_mbps?: number;
  write_speed_mbps?: number;
  disk_type?: string;
}

export interface NetworkMetrics {
  download_speed_mbps: number;
  upload_speed_mbps: number;
  latency_ms: number;
  packet_loss_percent?: number;
  interface_name?: string;
}

export interface SystemInfo {
  os: string;
  os_version: string;
  processor: string;
  ram: string;
  storage: string;
  hostname?: string;
  architecture?: string;
}

export interface AntivirusMetrics {
  installed: string[];
  real_time_protection: boolean;
  firewall_enabled: boolean;
  recommendations: string[];
}

export interface DriverMetrics {
  total_drivers: number;
  problematic_drivers: number;
  outdated_drivers: number;
  recommendations: string[];
}

export interface DiagnosticResult {
  id: string;
  user_id: string;
  device_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  cpu_status?: 'good' | 'warning' | 'critical';
  cpu_metrics?: DiagnosticMetrics;
  memory_status?: 'good' | 'warning' | 'critical';
  memory_metrics?: MemoryMetrics;
  disk_status?: 'good' | 'warning' | 'critical';
  disk_metrics?: DiskMetrics;
  network_status?: 'good' | 'warning' | 'critical';
  network_metrics?: NetworkMetrics;
  antivirus_status?: 'good' | 'warning' | 'critical';
  antivirus_metrics?: AntivirusMetrics;
  driver_status?: 'good' | 'warning' | 'critical';
  driver_metrics?: DriverMetrics;
  health_score?: number;
  raw_data?: any;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface Device {
  id: string;
  user_id: string;
  name: string;
  type: string;
  os?: string;
  os_version?: string;
  processor?: string;
  ram?: string;
  storage?: string;
  last_diagnostic_id?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateDiagnosticRequest {
  device_id: string;
  system_info?: SystemInfo;
}

export interface CreateDeviceRequest {
  name: string;
  type: string;
  os?: string;
  os_version?: string;
  processor?: string;
  ram?: string;
  storage?: string;
}
