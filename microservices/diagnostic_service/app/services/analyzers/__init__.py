"""Analisadores de sistema para diagnóstico.

Este módulo fornece classes para análise de diferentes componentes do sistema:
- CPUAnalyzer: Análise de CPU e temperatura
- MemoryAnalyzer: Análise de memória e uso
- DiskAnalyzer: Análise de disco e armazenamento
- NetworkAnalyzer: Análise de rede e conectividade
- AntivirusAnalyzer: Análise de antivírus e proteção
- DriverAnalyzer: Análise de drivers do sistema
"""

try:
    from .cpu_analyzer import CPUAnalyzer
    from .memory_analyzer import MemoryAnalyzer
    from .disk_analyzer import DiskAnalyzer
    from .network_analyzer import NetworkAnalyzer
    from .antivirus_analyzer import AntivirusAnalyzer
    from .driver_analyzer import DriverAnalyzer
except ImportError:
    # Fallback para casos onde algumas dependências podem não estar disponíveis
    class CPUAnalyzer:
        def analyze(self):
            return {"status": "unknown", "usage": 0, "temperature": 0}
    
    class MemoryAnalyzer:
        def analyze(self):
            return {"status": "unknown", "usage": 0, "available": 0, "total": 0}
    
    class DiskAnalyzer:
        def analyze(self):
            return {"status": "unknown", "usage": 0, "available": 0, "total": 0}
    
    class NetworkAnalyzer:
        def analyze(self):
            return {"status": "unknown", "speed": 0, "latency": 0}

__all__ = [
    "CPUAnalyzer",
    "MemoryAnalyzer", 
    "DiskAnalyzer",
    "NetworkAnalyzer",
    "AntivirusAnalyzer"
]
