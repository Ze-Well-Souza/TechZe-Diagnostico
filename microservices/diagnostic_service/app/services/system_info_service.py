import logging
import platform
import psutil
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
        """Coleta informações completas do sistema.
        
        Returns:
            Dicionário com informações do sistema
        """
        try:
            system_info = {
                "hostname": self._get_hostname(),
                "os_name": self._get_os_name(),
                "os_version": self._get_os_version(),
                "architecture": self._get_architecture(),
                "platform": self._get_platform(),
                "python_version": self._get_python_version(),
                "boot_time": self._get_boot_time(),
                "uptime": self._get_uptime(),
                "users": self._get_users(),
                "processes": self._get_process_count()
            }
            
            logger.info("System information collected successfully")
            return system_info
            
        except Exception as e:
            logger.exception(f"Error collecting system information: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_hostname(self) -> str:
        """Obtém o nome do host do sistema.
        
        Returns:
            Nome do host
        """
        try:
            return socket.gethostname()
        except Exception as e:
            logger.error(f"Error getting hostname: {str(e)}")
            return "unknown"
    
    def _get_os_name(self) -> str:
        """Obtém o nome do sistema operacional.
        
        Returns:
            Nome do SO
        """
        try:
            return platform.system()
        except Exception as e:
            logger.error(f"Error getting OS name: {str(e)}")
            return "unknown"
    
    def _get_os_version(self) -> str:
        """Obtém a versão do sistema operacional.
        
        Returns:
            Versão do SO
        """
        try:
            return platform.release()
        except Exception as e:
            logger.error(f"Error getting OS version: {str(e)}")
            return "unknown"
    
    def _get_architecture(self) -> str:
        """Obtém a arquitetura do sistema.
        
        Returns:
            Arquitetura do sistema
        """
        try:
            return platform.machine()
        except Exception as e:
            logger.error(f"Error getting architecture: {str(e)}")
            return "unknown"
    
    def _get_platform(self) -> str:
        """Obtém informações detalhadas da plataforma.
        
        Returns:
            Informações da plataforma
        """
        try:
            return platform.platform()
        except Exception as e:
            logger.error(f"Error getting platform: {str(e)}")
            return "unknown"
    
    def _get_python_version(self) -> str:
        """Obtém a versão do Python.
        
        Returns:
            Versão do Python
        """
        try:
            return platform.python_version()
        except Exception as e:
            logger.error(f"Error getting Python version: {str(e)}")
            return "unknown"
    
    def _get_boot_time(self) -> str:
        """Obtém o horário do último boot do sistema.
        
        Returns:
            Horário do último boot em formato ISO
        """
        try:
            boot_timestamp = psutil.boot_time()
            boot_time = datetime.fromtimestamp(boot_timestamp)
            return boot_time.isoformat()
        except Exception as e:
            logger.error(f"Error getting boot time: {str(e)}")
            return "unknown"
    
    def _get_uptime(self) -> Dict[str, Any]:
        """Calcula o tempo de atividade do sistema.
        
        Returns:
            Dicionário com informações de uptime
        """
        try:
            boot_timestamp = psutil.boot_time()
            current_time = datetime.now().timestamp()
            uptime_seconds = current_time - boot_timestamp
            
            # Converte para dias, horas, minutos
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            return {
                "total_seconds": int(uptime_seconds),
                "days": days,
                "hours": hours,
                "minutes": minutes,
                "formatted": f"{days}d {hours}h {minutes}m"
            }
        except Exception as e:
            logger.error(f"Error calculating uptime: {str(e)}")
            return {
                "total_seconds": 0,
                "days": 0,
                "hours": 0,
                "minutes": 0,
                "formatted": "unknown"
            }
    
    def _get_users(self) -> Dict[str, Any]:
        """Obtém informações sobre usuários logados.
        
        Returns:
            Informações sobre usuários
        """
        try:
            users = psutil.users()
            user_list = []
            
            for user in users:
                user_info = {
                    "name": user.name,
                    "terminal": getattr(user, 'terminal', 'unknown'),
                    "host": getattr(user, 'host', 'unknown'),
                    "started": datetime.fromtimestamp(user.started).isoformat() if hasattr(user, 'started') else 'unknown'
                }
                user_list.append(user_info)
            
            return {
                "count": len(user_list),
                "users": user_list
            }
        except Exception as e:
            logger.error(f"Error getting users: {str(e)}")
            return {
                "count": 0,
                "users": []
            }
    
    def _get_process_count(self) -> int:
        """Obtém o número total de processos em execução.
        
        Returns:
            Número de processos
        """
        try:
            return len(psutil.pids())
        except Exception as e:
            logger.error(f"Error getting process count: {str(e)}")
            return 0