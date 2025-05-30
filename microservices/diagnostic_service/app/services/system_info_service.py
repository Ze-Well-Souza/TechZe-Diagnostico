import logging
import platform
import socket
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from app.models.system_info import SystemInfo
from app.schemas.system_info import SystemInfoCreate, SystemInfoUpdate
from app.services.analyzers import CPUAnalyzer, MemoryAnalyzer, DiskAnalyzer, NetworkAnalyzer

logger = logging.getLogger(__name__)


class SystemInfoService:
    """Serviço para gerenciar informações do sistema."""
    
    def __init__(self):
        """Inicializa o serviço de informações do sistema."""
        self.cpu_analyzer = CPUAnalyzer()
        self.memory_analyzer = MemoryAnalyzer()
        self.disk_analyzer = DiskAnalyzer()
        self.network_analyzer = NetworkAnalyzer()
    
    def create(self, db: Session, *, obj_in: SystemInfoCreate) -> SystemInfo:
        """Cria um novo registro de informações do sistema.
        
        Args:
            db: Sessão do banco de dados
            obj_in: Dados para criar o registro
            
        Returns:
            Objeto SystemInfo criado
        """
        db_obj = SystemInfo(
            hostname=obj_in.hostname,
            os_name=obj_in.os_name,
            os_version=obj_in.os_version,
            os_arch=obj_in.os_arch,
            cpu_info=obj_in.cpu_info,
            cpu_cores=obj_in.cpu_cores,
            memory_total=obj_in.memory_total,
            disk_total=obj_in.disk_total,
            network_interfaces=obj_in.network_interfaces,
            installed_software=obj_in.installed_software,
            hardware_details=obj_in.hardware_details,
            notes=obj_in.notes
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Created system info record: {db_obj.id}")
        return db_obj
    
    def get(self, db: Session, id: uuid.UUID) -> Optional[SystemInfo]:
        """Obtém um registro de informações do sistema pelo ID.
        
        Args:
            db: Sessão do banco de dados
            id: ID do registro
            
        Returns:
            Objeto SystemInfo ou None se não encontrado
        """
        return db.query(SystemInfo).filter(SystemInfo.id == id).first()
    
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[SystemInfo]:
        """Obtém múltiplos registros de informações do sistema.
        
        Args:
            db: Sessão do banco de dados
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            Lista de objetos SystemInfo
        """
        return db.query(SystemInfo).offset(skip).limit(limit).all()
    
    def update(self, db: Session, *, db_obj: SystemInfo, obj_in: SystemInfoUpdate) -> SystemInfo:
        """Atualiza um registro de informações do sistema.
        
        Args:
            db: Sessão do banco de dados
            db_obj: Objeto SystemInfo existente
            obj_in: Dados para atualização
            
        Returns:
            Objeto SystemInfo atualizado
        """
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        logger.info(f"Updated system info record: {db_obj.id}")
        return db_obj
    
    def delete(self, db: Session, *, id: uuid.UUID) -> SystemInfo:
        """Exclui um registro de informações do sistema.
        
        Args:
            db: Sessão do banco de dados
            id: ID do registro
            
        Returns:
            Objeto SystemInfo excluído
        """
        obj = db.query(SystemInfo).get(id)
        db.delete(obj)
        db.commit()
        logger.info(f"Deleted system info record: {id}")
        return obj
    
    def collect_system_info(self) -> Dict[str, Any]:
        """Coleta informações detalhadas sobre o sistema.
        
        Returns:
            Dicionário com informações do sistema
        """
        try:
            # Informações básicas do sistema
            hostname = socket.gethostname()
            os_name = platform.system()
            os_version = platform.version()
            os_arch = platform.machine()
            
            # Coleta informações detalhadas usando os analisadores
            cpu_info = self.cpu_analyzer.analyze()
            memory_info = self.memory_analyzer.analyze()
            disk_info = self.disk_analyzer.analyze()
            network_info = self.network_analyzer.analyze()
            
            # Formata as informações do CPU
            cpu_details = {
                "model": platform.processor(),
                "cores": cpu_info.get("cores", {}).get("physical", 0),
                "threads": cpu_info.get("cores", {}).get("logical", 0),
                "architecture": platform.architecture()[0],
                "frequency": cpu_info.get("frequency", {}).get("current", 0)
            }
            
            # Coleta informações sobre software instalado (simplificado)
            installed_software = self._get_installed_software()
            
            # Coleta detalhes de hardware (simplificado)
            hardware_details = self._get_hardware_details()
            
            # Compila todas as informações
            system_info = {
                "hostname": hostname,
                "os_name": os_name,
                "os_version": os_version,
                "os_arch": os_arch,
                "cpu_info": cpu_details,
                "cpu_cores": cpu_info.get("cores", {}).get("physical", 0),
                "memory_total": memory_info.get("total", 0),
                "disk_total": disk_info.get("total", 0),
                "network_interfaces": self._format_network_interfaces(network_info),
                "installed_software": installed_software,
                "hardware_details": hardware_details,
                "collected_at": datetime.now().isoformat(),
                "raw_data": {
                    "cpu": cpu_info,
                    "memory": memory_info,
                    "disk": disk_info,
                    "network": network_info
                }
            }
            
            logger.info("System information collected successfully")
            return system_info
            
        except Exception as e:
            logger.exception(f"Error collecting system information: {str(e)}")
            return {
                "error": str(e),
                "hostname": socket.gethostname(),
                "collected_at": datetime.now().isoformat()
            }
    
    def _format_network_interfaces(self, network_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Formata as informações das interfaces de rede.
        
        Args:
            network_info: Informações de rede coletadas
            
        Returns:
            Lista formatada de interfaces de rede
        """
        interfaces = []
        
        if "interfaces" in network_info:
            for name, info in network_info["interfaces"].items():
                interfaces.append({
                    "name": name,
                    "mac_address": info.get("mac"),
                    "ipv4": info.get("ipv4"),
                    "ipv6": info.get("ipv6"),
                    "is_up": info.get("is_up", False),
                    "speed": info.get("speed", 0)
                })
        
        return interfaces
    
    def _get_installed_software(self) -> List[Dict[str, str]]:
        """Coleta informações sobre software instalado.
        
        Returns:
            Lista de software instalado
        """
        # Em um sistema real, isso seria implementado para coletar software instalado
        # Por enquanto, retornamos uma lista vazia ou alguns exemplos
        try:
            # Exemplo simplificado - em um sistema real, isso seria implementado
            # para coletar informações reais sobre software instalado
            return [
                {
                    "name": "Python",
                    "version": platform.python_version(),
                    "install_date": ""
                },
                {
                    "name": "Operating System",
                    "version": f"{platform.system()} {platform.version()}",
                    "install_date": ""
                }
            ]
        except Exception as e:
            logger.error(f"Error getting installed software: {str(e)}")
            return []
    
    def _get_hardware_details(self) -> Dict[str, Any]:
        """Coleta detalhes de hardware.
        
        Returns:
            Dicionário com detalhes de hardware
        """
        # Em um sistema real, isso seria implementado para coletar detalhes de hardware
        # Por enquanto, retornamos informações básicas
        try:
            return {
                "system": platform.system(),
                "node": platform.node(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
        except Exception as e:
            logger.error(f"Error getting hardware details: {str(e)}")
            return {}