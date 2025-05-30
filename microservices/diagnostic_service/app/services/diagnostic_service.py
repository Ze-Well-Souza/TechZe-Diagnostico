import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

from sqlalchemy.orm import Session

from app.models.diagnostic import Diagnostic, DiagnosticStatus
from app.models.system_info import SystemInfo
from app.schemas.diagnostic import DiagnosticCreate, DiagnosticUpdate
from app.schemas.system_info import SystemInfoCreate
from app.services.analyzers.cpu_analyzer import CPUAnalyzer
from app.services.analyzers.memory_analyzer import MemoryAnalyzer
from app.services.analyzers.disk_analyzer import DiskAnalyzer
from app.services.analyzers.network_analyzer import NetworkAnalyzer

logger = logging.getLogger(__name__)


class DiagnosticService:
    """Serviço para gerenciar diagnósticos de sistema."""
    
    def __init__(self, db: Session):
        """Inicializa o serviço de diagnóstico.
        
        Args:
            db: Sessão do banco de dados
        """
        self.db = db
        self.cpu_analyzer = CPUAnalyzer()
        self.memory_analyzer = MemoryAnalyzer()
        self.disk_analyzer = DiskAnalyzer()
        self.network_analyzer = NetworkAnalyzer()
    
    def create_diagnostic(self, obj_in: DiagnosticCreate) -> Diagnostic:
        """Cria um novo diagnóstico.
        
        Args:
            obj_in: Dados para criação do diagnóstico
            
        Returns:
            Objeto Diagnostic criado
        """
        db_obj = Diagnostic(
            user_id=obj_in.user_id,
            device_id=obj_in.device_id,
            status=DiagnosticStatus.PENDING
        )
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        logger.info(f"Created diagnostic with ID: {db_obj.id}")
        return db_obj
    
    def get_diagnostic(self, diagnostic_id: str) -> Optional[Diagnostic]:
        """Obtém um diagnóstico pelo ID.
        
        Args:
            diagnostic_id: ID do diagnóstico
            
        Returns:
            Objeto Diagnostic ou None se não encontrado
        """
        return self.db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    
    def get_diagnostics(
        self, 
        user_id: Optional[str] = None, 
        device_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[Diagnostic], int]:
        """Obtém uma lista de diagnósticos com filtros opcionais.
        
        Args:
            user_id: Filtrar por ID do usuário
            device_id: Filtrar por ID do dispositivo
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            Tupla com lista de diagnósticos e contagem total
        """
        query = self.db.query(Diagnostic)
        
        if user_id:
            query = query.filter(Diagnostic.user_id == user_id)
        
        if device_id:
            query = query.filter(Diagnostic.device_id == device_id)
        
        total = query.count()
        items = query.order_by(Diagnostic.created_at.desc()).offset(skip).limit(limit).all()
        
        return items, total
    
    def update_diagnostic(
        self, diagnostic_id: str, obj_in: DiagnosticUpdate
    ) -> Optional[Diagnostic]:
        """Atualiza um diagnóstico existente.
        
        Args:
            diagnostic_id: ID do diagnóstico
            obj_in: Dados para atualização
            
        Returns:
            Objeto Diagnostic atualizado ou None se não encontrado
        """
        db_obj = self.get_diagnostic(diagnostic_id)
        if not db_obj:
            return None
        
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        logger.info(f"Updated diagnostic with ID: {db_obj.id}")
        return db_obj
    
    def delete_diagnostic(self, diagnostic_id: str) -> bool:
        """Exclui um diagnóstico pelo ID.
        
        Args:
            diagnostic_id: ID do diagnóstico
            
        Returns:
            True se excluído com sucesso, False caso contrário
        """
        db_obj = self.get_diagnostic(diagnostic_id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        logger.info(f"Deleted diagnostic with ID: {diagnostic_id}")
        return True
    
    def run_diagnostic(self, diagnostic_id: str) -> Diagnostic:
        """Executa um diagnóstico completo do sistema.
        
        Args:
            diagnostic_id: ID do diagnóstico a ser executado
            
        Returns:
            Objeto Diagnostic atualizado com os resultados
        """
        # Obtém o diagnóstico
        diagnostic = self.get_diagnostic(diagnostic_id)
        if not diagnostic:
            logger.error(f"Diagnostic not found: {diagnostic_id}")
            raise ValueError(f"Diagnostic not found: {diagnostic_id}")
        
        # Atualiza o status para em andamento
        self.update_diagnostic(
            diagnostic_id=diagnostic_id,
            obj_in=DiagnosticUpdate(status=DiagnosticStatus.IN_PROGRESS)
        )
        
        start_time = time.time()
        error_message = None
        raw_data = {}
        
        try:
            # Coleta informações do sistema
            system_info = self._collect_system_info(diagnostic_id)
            
            # Executa análises
            cpu_result = self.cpu_analyzer.analyze()
            memory_result = self.memory_analyzer.analyze()
            disk_result = self.disk_analyzer.analyze()
            network_result = self.network_analyzer.analyze()
            
            # Calcula o score de saúde geral
            overall_health = self._calculate_overall_health(
                cpu_result, memory_result, disk_result, network_result
            )
            
            # Compila os dados brutos
            raw_data = {
                "cpu": cpu_result,
                "memory": memory_result,
                "disk": disk_result,
                "network": network_result,
                "system_info": system_info.to_dict() if system_info else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Atualiza o diagnóstico com os resultados
            update_data = {
                "status": DiagnosticStatus.COMPLETED,
                "cpu_status": cpu_result.get("status"),
                "memory_status": memory_result.get("status"),
                "disk_status": disk_result.get("status"),
                "network_status": network_result.get("status"),
                "cpu_usage": cpu_result.get("usage"),
                "cpu_temperature": cpu_result.get("temperature"),
                "memory_usage": memory_result.get("usage"),
                "memory_available": memory_result.get("available"),
                "disk_usage": disk_result.get("usage"),
                "disk_available": disk_result.get("available"),
                "network_speed": network_result.get("speed"),
                "overall_health": overall_health,
                "raw_data": raw_data,
                "execution_time": time.time() - start_time
            }
            
            logger.info(f"Diagnostic completed successfully: {diagnostic_id}")
            
        except Exception as e:
            logger.exception(f"Error running diagnostic {diagnostic_id}: {str(e)}")
            error_message = str(e)
            update_data = {
                "status": DiagnosticStatus.FAILED,
                "error_message": error_message,
                "execution_time": time.time() - start_time
            }
        
        # Atualiza o diagnóstico com os resultados ou erro
        return self.update_diagnostic(
            diagnostic_id=diagnostic_id,
            obj_in=DiagnosticUpdate(**update_data)
        )
    
    def _collect_system_info(self, diagnostic_id: str) -> Optional[SystemInfo]:
        """Coleta informações do sistema e cria um registro SystemInfo.
        
        Args:
            diagnostic_id: ID do diagnóstico
            
        Returns:
            Objeto SystemInfo criado ou None em caso de erro
        """
        try:
            # Aqui seria implementada a coleta real de informações do sistema
            # Por enquanto, usamos dados de exemplo
            system_info_data = {
                "hostname": "example-pc",
                "os_name": "Windows",
                "os_version": "10 Pro",
                "os_arch": "x64",
                "kernel_version": "10.0.19041",
                "cpu_model": "Intel Core i7-9700K",
                "cpu_cores": 8,
                "cpu_threads": 8,
                "cpu_frequency": "3.6 GHz",
                "total_memory": 16384,  # 16 GB em MB
                "total_disk": 512000,  # 500 GB em MB
                "ip_address": "192.168.1.100",
                "mac_address": "00:11:22:33:44:55",
                "installed_software": [
                    {"name": "Google Chrome", "version": "91.0.4472.124"},
                    {"name": "Microsoft Office", "version": "2019"}
                ],
                "hardware_details": {
                    "motherboard": {
                        "manufacturer": "ASUS",
                        "model": "ROG STRIX Z390-E GAMING"
                    },
                    "graphics_card": {
                        "manufacturer": "NVIDIA",
                        "model": "GeForce RTX 2070",
                        "memory": "8 GB"
                    }
                }
            }
            
            # Cria o objeto SystemInfo
            system_info = SystemInfo(**system_info_data)
            self.db.add(system_info)
            self.db.commit()
            self.db.refresh(system_info)
            
            # Associa ao diagnóstico
            diagnostic = self.get_diagnostic(diagnostic_id)
            diagnostic.system_info_id = system_info.id
            self.db.add(diagnostic)
            self.db.commit()
            
            return system_info
            
        except Exception as e:
            logger.exception(f"Error collecting system info: {str(e)}")
            return None
    
    def _calculate_overall_health(self, cpu_result: Dict[str, Any], memory_result: Dict[str, Any], 
                                disk_result: Dict[str, Any], network_result: Dict[str, Any]) -> int:
        """Calcula o score de saúde geral do sistema.
        
        Args:
            cpu_result: Resultados da análise de CPU
            memory_result: Resultados da análise de memória
            disk_result: Resultados da análise de disco
            network_result: Resultados da análise de rede
            
        Returns:
            Score de saúde geral (0-100)
        """
        # Pesos para cada componente
        weights = {
            "cpu": 0.3,
            "memory": 0.25,
            "disk": 0.25,
            "network": 0.2
        }
        
        # Mapeia status para scores
        status_scores = {
            "healthy": 100,
            "warning": 60,
            "critical": 20,
            "error": 0
        }
        
        # Calcula o score ponderado
        cpu_score = status_scores.get(cpu_result.get("status", "error"), 0)
        memory_score = status_scores.get(memory_result.get("status", "error"), 0)
        disk_score = status_scores.get(disk_result.get("status", "error"), 0)
        network_score = status_scores.get(network_result.get("status", "error"), 0)
        
        overall_score = (
            cpu_score * weights["cpu"] +
            memory_score * weights["memory"] +
            disk_score * weights["disk"] +
            network_score * weights["network"]
        )
        
        return round(overall_score)