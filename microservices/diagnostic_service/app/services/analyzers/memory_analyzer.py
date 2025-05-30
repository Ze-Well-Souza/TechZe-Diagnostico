import logging
import psutil
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MemoryAnalyzer:
    """Analisador de memória para diagnóstico de sistema."""
    
    def __init__(self):
        """Inicializa o analisador de memória."""
        pass
    
    def analyze(self) -> Dict[str, Any]:
        """Realiza análise completa da memória.
        
        Returns:
            Dicionário com resultados da análise
        """
        try:
            # Coleta informações da memória
            memory_usage = self._get_memory_usage()
            memory_info = self._get_memory_info()
            swap_info = self._get_swap_info()
            memory_details = self._get_memory_details()
            
            # Determina o status da memória
            status = self._determine_status(memory_usage, swap_info["percent"])
            
            # Compila os resultados
            result = {
                "status": status,
                "usage": memory_usage,
                "available": memory_info["available"],  # Em MB
                "total": memory_info["total"],  # Em MB
                "swap": swap_info,
                "details": memory_details
            }
            
            logger.info(f"Memory analysis completed: {status}")
            return result
            
        except Exception as e:
            logger.exception(f"Error analyzing memory: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def _get_memory_usage(self) -> float:
        """Obtém o uso atual da memória em porcentagem.
        
        Returns:
            Porcentagem de uso da memória
        """
        try:
            return psutil.virtual_memory().percent
        except Exception as e:
            logger.error(f"Error getting memory usage: {str(e)}")
            return 0.0
    
    def _get_memory_info(self) -> Dict[str, float]:
        """Obtém informações básicas da memória.
        
        Returns:
            Dicionário com informações da memória
        """
        try:
            mem = psutil.virtual_memory()
            return {
                "total": mem.total / (1024 * 1024),  # Converte para MB
                "available": mem.available / (1024 * 1024),  # Converte para MB
                "used": mem.used / (1024 * 1024),  # Converte para MB
                "free": mem.free / (1024 * 1024)  # Converte para MB
            }
        except Exception as e:
            logger.error(f"Error getting memory info: {str(e)}")
            return {
                "total": 0.0,
                "available": 0.0,
                "used": 0.0,
                "free": 0.0
            }
    
    def _get_swap_info(self) -> Dict[str, Any]:
        """Obtém informações sobre a memória swap.
        
        Returns:
            Dicionário com informações da memória swap
        """
        try:
            swap = psutil.swap_memory()
            return {
                "total": swap.total / (1024 * 1024),  # Converte para MB
                "used": swap.used / (1024 * 1024),  # Converte para MB
                "free": swap.free / (1024 * 1024),  # Converte para MB
                "percent": swap.percent
            }
        except Exception as e:
            logger.error(f"Error getting swap info: {str(e)}")
            return {
                "total": 0.0,
                "used": 0.0,
                "free": 0.0,
                "percent": 0.0
            }
    
    def _get_memory_details(self) -> Dict[str, Any]:
        """Obtém detalhes adicionais sobre a memória.
        
        Returns:
            Dicionário com detalhes da memória
        """
        try:
            mem = psutil.virtual_memory()
            details = {}
            
            # Adiciona atributos disponíveis
            if hasattr(mem, "cached"):
                details["cached"] = mem.cached / (1024 * 1024)  # Converte para MB
            
            if hasattr(mem, "buffers"):
                details["buffers"] = mem.buffers / (1024 * 1024)  # Converte para MB
            
            if hasattr(mem, "shared"):
                details["shared"] = mem.shared / (1024 * 1024)  # Converte para MB
            
            # Calcula a fragmentação (estimativa simplificada)
            if hasattr(mem, "free") and hasattr(mem, "available") and mem.free > 0:
                details["fragmentation"] = 1 - (mem.free / mem.available)
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting memory details: {str(e)}")
            return {}
    
    def _determine_status(self, memory_usage: float, swap_usage: float) -> str:
        """Determina o status da memória com base no uso.
        
        Args:
            memory_usage: Porcentagem de uso da memória RAM
            swap_usage: Porcentagem de uso da memória swap
            
        Returns:
            Status da memória: "healthy", "warning", "critical" ou "error"
        """
        if memory_usage >= 90 or swap_usage >= 80:
            return "critical"
        elif memory_usage >= 80 or swap_usage >= 60:
            return "warning"
        else:
            return "healthy"