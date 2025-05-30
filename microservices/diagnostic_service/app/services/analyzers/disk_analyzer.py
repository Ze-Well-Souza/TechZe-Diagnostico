import logging
import os
import platform
import psutil
import time
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class DiskAnalyzer:
    """Analisador de disco para diagnóstico de sistema."""
    
    def __init__(self):
        """Inicializa o analisador de disco."""
        pass
    
    def analyze(self) -> Dict[str, Any]:
        """Realiza análise completa dos discos.
        
        Returns:
            Dicionário com resultados da análise
        """
        try:
            # Coleta informações dos discos
            partitions = self._get_partitions()
            disk_usage = self._get_disk_usage(partitions)
            disk_io = self._get_disk_io()
            disk_speed = self._get_disk_speed()
            
            # Calcula o uso médio ponderado pelo tamanho das partições
            total_size = sum(part_info["total"] for part_info in disk_usage.values())
            weighted_usage = 0
            
            for part_info in disk_usage.values():
                if total_size > 0:
                    weight = part_info["total"] / total_size
                    weighted_usage += part_info["percent"] * weight
            
            # Determina o status do disco
            status = self._determine_status(weighted_usage, disk_usage)
            
            # Calcula o espaço total e disponível
            total_space = sum(part_info["total"] for part_info in disk_usage.values())
            available_space = sum(part_info["free"] for part_info in disk_usage.values())
            
            # Compila os resultados
            result = {
                "status": status,
                "usage": weighted_usage,
                "available": available_space,  # Em MB
                "total": total_space,  # Em MB
                "partitions": disk_usage,
                "io": disk_io,
                "speed": disk_speed
            }
            
            logger.info(f"Disk analysis completed: {status}")
            return result
            
        except Exception as e:
            logger.exception(f"Error analyzing disk: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def _get_partitions(self) -> List[str]:
        """Obtém a lista de partições de disco.
        
        Returns:
            Lista de caminhos de partições
        """
        try:
            partitions = []
            for part in psutil.disk_partitions(all=False):
                if os.path.exists(part.mountpoint) and (
                    part.fstype != "" or "removable" not in part.opts
                ):
                    partitions.append(part.mountpoint)
            return partitions
        except Exception as e:
            logger.error(f"Error getting disk partitions: {str(e)}")
            return ["/" if platform.system() != "Windows" else "C:\\"]  # Fallback
    
    def _get_disk_usage(self, partitions: List[str]) -> Dict[str, Dict[str, Any]]:
        """Obtém informações de uso das partições de disco.
        
        Args:
            partitions: Lista de caminhos de partições
            
        Returns:
            Dicionário com informações de uso por partição
        """
        usage = {}
        for part in partitions:
            try:
                disk_usage = psutil.disk_usage(part)
                usage[part] = {
                    "total": disk_usage.total / (1024 * 1024),  # Converte para MB
                    "used": disk_usage.used / (1024 * 1024),  # Converte para MB
                    "free": disk_usage.free / (1024 * 1024),  # Converte para MB
                    "percent": disk_usage.percent
                }
            except Exception as e:
                logger.error(f"Error getting disk usage for {part}: {str(e)}")
        return usage
    
    def _get_disk_io(self) -> Dict[str, Any]:
        """Obtém estatísticas de I/O de disco.
        
        Returns:
            Dicionário com estatísticas de I/O
        """
        try:
            # Coleta estatísticas de I/O
            io_stats = psutil.disk_io_counters(perdisk=True)
            
            # Coleta estatísticas novamente após um intervalo para calcular taxas
            time.sleep(0.1)  # Pequeno intervalo para medir a diferença
            io_stats_after = psutil.disk_io_counters(perdisk=True)
            
            result = {}
            for disk, stats in io_stats.items():
                if disk in io_stats_after:
                    stats_after = io_stats_after[disk]
                    read_bytes_diff = stats_after.read_bytes - stats.read_bytes
                    write_bytes_diff = stats_after.write_bytes - stats.write_bytes
                    time_diff = 0.1  # Segundos
                    
                    result[disk] = {
                        "read_count": stats.read_count,
                        "write_count": stats.write_count,
                        "read_bytes": stats.read_bytes / (1024 * 1024),  # Converte para MB
                        "write_bytes": stats.write_bytes / (1024 * 1024),  # Converte para MB
                        "read_time": stats.read_time if hasattr(stats, "read_time") else None,
                        "write_time": stats.write_time if hasattr(stats, "write_time") else None,
                        "read_speed": read_bytes_diff / (1024 * 1024) / time_diff,  # MB/s
                        "write_speed": write_bytes_diff / (1024 * 1024) / time_diff  # MB/s
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting disk I/O: {str(e)}")
            return {}
    
    def _get_disk_speed(self) -> Dict[str, Any]:
        """Estima a velocidade de leitura/escrita do disco.
        
        Returns:
            Dicionário com velocidades estimadas
        """
        try:
            # Em um sistema real, isso seria implementado com testes reais de velocidade
            # Por enquanto, usamos uma estimativa baseada nas estatísticas de I/O
            io_stats = self._get_disk_io()
            
            # Calcula a média das velocidades de todos os discos
            read_speeds = [stats["read_speed"] for disk, stats in io_stats.items() if "read_speed" in stats]
            write_speeds = [stats["write_speed"] for disk, stats in io_stats.items() if "write_speed" in stats]
            
            avg_read = sum(read_speeds) / len(read_speeds) if read_speeds else 0
            avg_write = sum(write_speeds) / len(write_speeds) if write_speeds else 0
            
            return {
                "read": avg_read,  # MB/s
                "write": avg_write,  # MB/s
                "estimated": True  # Indica que são valores estimados
            }
            
        except Exception as e:
            logger.error(f"Error estimating disk speed: {str(e)}")
            return {
                "read": 0.0,
                "write": 0.0,
                "estimated": True
            }
    
    def _determine_status(self, weighted_usage: float, disk_usage: Dict[str, Dict[str, Any]]) -> str:
        """Determina o status do disco com base no uso.
        
        Args:
            weighted_usage: Uso médio ponderado do disco
            disk_usage: Informações de uso por partição
            
        Returns:
            Status do disco: "healthy", "warning", "critical" ou "error"
        """
        # Verifica se alguma partição está em estado crítico
        for part, info in disk_usage.items():
            if info["percent"] >= 95:
                return "critical"
        
        # Verifica o uso médio ponderado
        if weighted_usage >= 90:
            return "critical"
        elif weighted_usage >= 80:
            return "warning"
        else:
            return "healthy"