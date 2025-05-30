import logging
import os
import uuid
from datetime import datetime
from typing import Optional, List, Tuple

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.report import Report, ReportStatus
from app.models.diagnostic import Diagnostic
from app.schemas.report import ReportCreate, ReportUpdate
from app.utils.pdf_generator import generate_pdf_report

logger = logging.getLogger(__name__)


class ReportService:
    """Serviço para gerenciar relatórios de diagnóstico."""
    
    def __init__(self, db: Session):
        """Inicializa o serviço de relatórios.
        
        Args:
            db: Sessão do banco de dados
        """
        self.db = db
        
        # Garante que o diretório de armazenamento de relatórios existe
        os.makedirs(settings.REPORT_STORAGE_PATH, exist_ok=True)
    
    def create_report(self, obj_in: ReportCreate) -> Report:
        """Cria um novo relatório.
        
        Args:
            obj_in: Dados para criação do relatório
            
        Returns:
            Objeto Report criado
        """
        # Verifica se o diagnóstico existe
        diagnostic = self.db.query(Diagnostic).filter(Diagnostic.id == obj_in.diagnostic_id).first()
        if not diagnostic:
            raise ValueError(f"Diagnostic not found: {obj_in.diagnostic_id}")
        
        # Cria o relatório
        db_obj = Report(
            title=obj_in.title,
            description=obj_in.description,
            format=obj_in.format,
            diagnostic_id=obj_in.diagnostic_id,
            status=ReportStatus.PENDING
        )
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        logger.info(f"Created report with ID: {db_obj.id}")
        return db_obj
    
    def get_report(self, report_id: str) -> Optional[Report]:
        """Obtém um relatório pelo ID.
        
        Args:
            report_id: ID do relatório
            
        Returns:
            Objeto Report ou None se não encontrado
        """
        return self.db.query(Report).filter(Report.id == report_id).first()
    
    def get_reports(
        self, 
        diagnostic_id: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[Report], int]:
        """Obtém uma lista de relatórios com filtros opcionais.
        
        Args:
            diagnostic_id: Filtrar por ID do diagnóstico
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            Tupla com lista de relatórios e contagem total
        """
        query = self.db.query(Report)
        
        if diagnostic_id:
            query = query.filter(Report.diagnostic_id == diagnostic_id)
        
        total = query.count()
        items = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
        
        return items, total
    
    def update_report(
        self, report_id: str, obj_in: ReportUpdate
    ) -> Optional[Report]:
        """Atualiza um relatório existente.
        
        Args:
            report_id: ID do relatório
            obj_in: Dados para atualização
            
        Returns:
            Objeto Report atualizado ou None se não encontrado
        """
        db_obj = self.get_report(report_id)
        if not db_obj:
            return None
        
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        logger.info(f"Updated report with ID: {db_obj.id}")
        return db_obj
    
    def delete_report(self, report_id: str) -> bool:
        """Exclui um relatório pelo ID.
        
        Args:
            report_id: ID do relatório
            
        Returns:
            True se excluído com sucesso, False caso contrário
        """
        db_obj = self.get_report(report_id)
        if not db_obj:
            return False
        
        # Remove o arquivo físico se existir
        if db_obj.file_path and os.path.exists(db_obj.file_path):
            try:
                os.remove(db_obj.file_path)
            except Exception as e:
                logger.error(f"Error removing report file: {str(e)}")
        
        self.db.delete(db_obj)
        self.db.commit()
        logger.info(f"Deleted report with ID: {report_id}")
        return True
    
    def generate_report(self, report_id: str) -> Optional[Report]:
        """Gera um relatório a partir de um diagnóstico.
        
        Args:
            report_id: ID do relatório a ser gerado
            
        Returns:
            Objeto Report atualizado ou None em caso de erro
        """
        # Obtém o relatório
        report = self.get_report(report_id)
        if not report:
            logger.error(f"Report not found: {report_id}")
            return None
        
        # Obtém o diagnóstico associado
        diagnostic = self.db.query(Diagnostic).filter(Diagnostic.id == report.diagnostic_id).first()
        if not diagnostic:
            error_msg = f"Diagnostic not found for report: {report_id}"
            logger.error(error_msg)
            self.update_report(
                report_id=report_id,
                obj_in=ReportUpdate(
                    status=ReportStatus.FAILED,
                    error_message=error_msg
                )
            )
            return report
        
        # Atualiza o status para em andamento
        self.update_report(
            report_id=report_id,
            obj_in=ReportUpdate(status=ReportStatus.GENERATING)
        )
        
        try:
            # Gera o nome do arquivo
            filename = f"report_{report_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            file_path = os.path.join(settings.REPORT_STORAGE_PATH, filename)
            
            # Gera o relatório PDF
            generate_pdf_report(diagnostic, file_path)
            
            # Gera URL pública (exemplo)
            public_url = f"/api/v1/reports/{report_id}/download"
            
            # Atualiza o relatório com o caminho do arquivo e URL
            self.update_report(
                report_id=report_id,
                obj_in=ReportUpdate(
                    status=ReportStatus.COMPLETED,
                    file_path=file_path,
                    public_url=public_url
                )
            )
            
            logger.info(f"Report generated successfully: {report_id}")
            return self.get_report(report_id)
            
        except Exception as e:
            logger.exception(f"Error generating report {report_id}: {str(e)}")
            self.update_report(
                report_id=report_id,
                obj_in=ReportUpdate(
                    status=ReportStatus.FAILED,
                    error_message=str(e)
                )
            )
            return self.get_report(report_id)