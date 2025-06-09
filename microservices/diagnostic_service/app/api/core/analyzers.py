# -*- coding: utf-8 -*-
"""
Módulo de analisadores de sistema para diagnósticos.

Contém classes para análise de CPU, memória, disco, rede, antivírus e drivers.
"""

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import psutil
import platform
import subprocess
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseAnalyzer(ABC):
    """
    Classe base para todos os analisadores.
    """
    
    def __init__(self):
        self.name = self.__class__.__name__
        self.start_time = None
        self.end_time = None
    
    @abstractmethod
    async def analyze(self) -> Dict[str, Any]:
        """
        Executa a análise específica do componente.
        
        Returns:
            dict: Resultados da análise
        """
        pass
    
    def _start_analysis(self):
        """Marca o início da análise."""
        self.start_time = datetime.now()
        logger.info(f"Iniciando análise: {self.name}")
    
    def _end_analysis(self):
        """Marca o fim da análise."""
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"Análise concluída: {self.name} ({duration:.2f}s)")
    
    def _get_analysis_metadata(self) -> Dict[str, Any]:
        """Retorna metadados da análise."""
        return {
            "analyzer": self.name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (
                (self.end_time - self.start_time).total_seconds() 
                if self.start_time and self.end_time else None
            )
        }

class CPUAnalyzer(BaseAnalyzer):
    """
    Analisador de CPU.
    """
    
    async def analyze(self) -> Dict[str, Any]:
        """Analisa o desempenho da CPU."""
        self._start_analysis()
        
        try:
            # Informações básicas da CPU
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "max_frequency": psutil.cpu_freq().max if psutil.cpu_freq() else None,
                "current_frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None,
            }
            
            # Uso da CPU
            cpu_usage = {
                "overall_percent": psutil.cpu_percent(interval=1),
                "per_core_percent": psutil.cpu_percent(interval=1, percpu=True),
            }
            
            # Tempos de CPU
            cpu_times = psutil.cpu_times()
            cpu_times_info = {
                "user": cpu_times.user,
                "system": cpu_times.system,
                "idle": cpu_times.idle,
            }
            
            # Estatísticas de CPU
            cpu_stats = psutil.cpu_stats()
            cpu_stats_info = {
                "ctx_switches": cpu_stats.ctx_switches,
                "interrupts": cpu_stats.interrupts,
                "soft_interrupts": cpu_stats.soft_interrupts,
                "syscalls": cpu_stats.syscalls,
            }
            
            result = {
                "status": "success",
                "info": cpu_info,
                "usage": cpu_usage,
                "times": cpu_times_info,
                "stats": cpu_stats_info,
                "metadata": self._get_analysis_metadata()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de CPU: {e}")
            result = {
                "status": "error",
                "error": str(e),
                "metadata": self._get_analysis_metadata()
            }
        
        self._end_analysis()
        return result

class MemoryAnalyzer(BaseAnalyzer):
    """
    Analisador de memória.
    """
    
    async def analyze(self) -> Dict[str, Any]:
        """Analisa o uso de memória."""
        self._start_analysis()
        
        try:
            # Memória virtual
            virtual_memory = psutil.virtual_memory()
            virtual_info = {
                "total": virtual_memory.total,
                "available": virtual_memory.available,
                "used": virtual_memory.used,
                "free": virtual_memory.free,
                "percent": virtual_memory.percent,
            }
            
            # Memória swap
            swap_memory = psutil.swap_memory()
            swap_info = {
                "total": swap_memory.total,
                "used": swap_memory.used,
                "free": swap_memory.free,
                "percent": swap_memory.percent,
            }
            
            result = {
                "status": "success",
                "virtual_memory": virtual_info,
                "swap_memory": swap_info,
                "metadata": self._get_analysis_metadata()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de memória: {e}")
            result = {
                "status": "error",
                "error": str(e),
                "metadata": self._get_analysis_metadata()
            }
        
        self._end_analysis()
        return result

class DiskAnalyzer(BaseAnalyzer):
    """
    Analisador de disco.
    """
    
    async def analyze(self) -> Dict[str, Any]:
        """Analisa o uso de disco."""
        self._start_analysis()
        
        try:
            # Partições de disco
            partitions = []
            for partition in psutil.disk_partitions():
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        "device": partition.device,
                        "mountpoint": partition.mountpoint,
                        "fstype": partition.fstype,
                        "total": partition_usage.total,
                        "used": partition_usage.used,
                        "free": partition_usage.free,
                        "percent": (partition_usage.used / partition_usage.total) * 100
                    })
                except PermissionError:
                    continue
            
            # I/O de disco
            disk_io = psutil.disk_io_counters()
            io_info = {
                "read_count": disk_io.read_count,
                "write_count": disk_io.write_count,
                "read_bytes": disk_io.read_bytes,
                "write_bytes": disk_io.write_bytes,
                "read_time": disk_io.read_time,
                "write_time": disk_io.write_time,
            } if disk_io else {}
            
            result = {
                "status": "success",
                "partitions": partitions,
                "io_stats": io_info,
                "metadata": self._get_analysis_metadata()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de disco: {e}")
            result = {
                "status": "error",
                "error": str(e),
                "metadata": self._get_analysis_metadata()
            }
        
        self._end_analysis()
        return result

class NetworkAnalyzer(BaseAnalyzer):
    """
    Analisador de rede.
    """
    
    async def analyze(self) -> Dict[str, Any]:
        """Analisa a conectividade de rede."""
        self._start_analysis()
        
        try:
            # Interfaces de rede
            network_interfaces = {}
            for interface, addresses in psutil.net_if_addrs().items():
                network_interfaces[interface] = [
                    {
                        "family": addr.family.name,
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast,
                    }
                    for addr in addresses
                ]
            
            # Estatísticas de rede
            net_io = psutil.net_io_counters()
            io_stats = {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "errin": net_io.errin,
                "errout": net_io.errout,
                "dropin": net_io.dropin,
                "dropout": net_io.dropout,
            } if net_io else {}
            
            # Conexões ativas
            connections = []
            try:
                for conn in psutil.net_connections(kind='inet'):
                    connections.append({
                        "fd": conn.fd,
                        "family": conn.family.name if conn.family else None,
                        "type": conn.type.name if conn.type else None,
                        "laddr": f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else None,
                        "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                        "status": conn.status,
                        "pid": conn.pid,
                    })
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
            
            result = {
                "status": "success",
                "interfaces": network_interfaces,
                "io_stats": io_stats,
                "connections": connections[:50],  # Limitar a 50 conexões
                "metadata": self._get_analysis_metadata()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de rede: {e}")
            result = {
                "status": "error",
                "error": str(e),
                "metadata": self._get_analysis_metadata()
            }
        
        self._end_analysis()
        return result

class AntivirusAnalyzer(BaseAnalyzer):
    """
    Analisador de antivírus.
    """
    
    async def analyze(self) -> Dict[str, Any]:
        """Analisa o status do antivírus."""
        self._start_analysis()
        
        try:
            antivirus_info = {
                "windows_defender": self._check_windows_defender(),
                "third_party": self._check_third_party_antivirus(),
            }
            
            result = {
                "status": "success",
                "antivirus_info": antivirus_info,
                "metadata": self._get_analysis_metadata()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de antivírus: {e}")
            result = {
                "status": "error",
                "error": str(e),
                "metadata": self._get_analysis_metadata()
            }
        
        self._end_analysis()
        return result
    
    def _check_windows_defender(self) -> Dict[str, Any]:
        """Verifica o status do Windows Defender."""
        if platform.system() != "Windows":
            return {"available": False, "reason": "Not Windows"}
        
        try:
            # Comando PowerShell para verificar Windows Defender
            cmd = "Get-MpComputerStatus | ConvertTo-Json"
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                defender_status = json.loads(result.stdout)
                return {
                    "available": True,
                    "enabled": defender_status.get("AntivirusEnabled", False),
                    "real_time_protection": defender_status.get("RealTimeProtectionEnabled", False),
                    "last_scan": defender_status.get("QuickScanEndTime"),
                }
            else:
                return {"available": False, "error": result.stderr}
                
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def _check_third_party_antivirus(self) -> List[Dict[str, Any]]:
        """Verifica antivírus de terceiros."""
        # Lista de processos comuns de antivírus
        antivirus_processes = [
            "avast", "avg", "norton", "mcafee", "kaspersky",
            "bitdefender", "eset", "trend", "sophos", "avira"
        ]
        
        detected_antivirus = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    for av in antivirus_processes:
                        if av in proc_name:
                            detected_antivirus.append({
                                "name": proc.info['name'],
                                "pid": proc.info['pid'],
                                "type": av
                            })
                            break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Erro ao verificar antivírus de terceiros: {e}")
        
        return detected_antivirus

class DriverAnalyzer(BaseAnalyzer):
    """
    Analisador de drivers.
    """
    
    async def analyze(self) -> Dict[str, Any]:
        """Analisa o status dos drivers."""
        self._start_analysis()
        
        try:
            driver_info = {
                "system_drivers": self._get_system_drivers(),
                "device_drivers": self._get_device_drivers(),
            }
            
            result = {
                "status": "success",
                "driver_info": driver_info,
                "metadata": self._get_analysis_metadata()
            }
            
        except Exception as e:
            logger.error(f"Erro na análise de drivers: {e}")
            result = {
                "status": "error",
                "error": str(e),
                "metadata": self._get_analysis_metadata()
            }
        
        self._end_analysis()
        return result
    
    def _get_system_drivers(self) -> List[Dict[str, Any]]:
        """Obtém informações dos drivers do sistema."""
        if platform.system() != "Windows":
            return []
        
        try:
            cmd = "Get-WindowsDriver -Online | Select-Object Driver, Date, Version | ConvertTo-Json"
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                drivers = json.loads(result.stdout)
                return drivers if isinstance(drivers, list) else [drivers]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Erro ao obter drivers do sistema: {e}")
            return []
    
    def _get_device_drivers(self) -> List[Dict[str, Any]]:
        """Obtém informações dos drivers de dispositivos."""
        if platform.system() != "Windows":
            return []
        
        try:
            cmd = "Get-PnpDevice | Where-Object {$_.Status -eq 'Error'} | Select-Object FriendlyName, Status, Problem | ConvertTo-Json"
            result = subprocess.run(
                ["powershell", "-Command", cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                devices = json.loads(result.stdout)
                return devices if isinstance(devices, list) else [devices]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Erro ao obter drivers de dispositivos: {e}")
            return []