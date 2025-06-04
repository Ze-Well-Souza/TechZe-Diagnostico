from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import desc, and_, or_, func
from sqlalchemy.orm import Session

from app.models.diagnostic import Diagnostic, DiagnosticStatus


class DiagnosticRepository:
    """Repositório para operações de diagnóstico no banco de dados."""
    
    def __init__(self, db: Session):
        """Inicializa o repositório com uma sessão do banco de dados.
        
        Args:
            db: Sessão do banco de dados
        """
        self.db = db
    
    def create(self, diagnostic_data: Dict[str, Any]) -> Diagnostic:
        """Cria um novo diagnóstico.
        
        Args:
            diagnostic_data: Dados do diagnóstico
            
        Returns:
            Objeto Diagnostic criado
        """
        db_obj = Diagnostic(**diagnostic_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, diagnostic_id: str) -> Optional[Diagnostic]:
        """Obtém um diagnóstico pelo ID.
        
        Args:
            diagnostic_id: ID do diagnóstico
            
        Returns:
            Objeto Diagnostic ou None se não encontrado
        """
        return self.db.query(Diagnostic).filter(Diagnostic.id == diagnostic_id).first()
    
    def get_by_user_id(self, user_id: str, skip: int = 0, limit: int = 100) -> List[Diagnostic]:
        """Obtém diagnósticos de um usuário específico.
        
        Args:
            user_id: ID do usuário
            skip: Número de registros para pular
            limit: Número máximo de registros para retornar
            
        Returns:
            Lista de diagnósticos
        """
        return self.db.query(Diagnostic)\
            .filter(Diagnostic.user_id == user_id)\
            .order_by(desc(Diagnostic.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    def update(self, diagnostic_id: str, update_data: Dict[str, Any]) -> Optional[Diagnostic]:
        """Atualiza um diagnóstico existente.
        
        Args:
            diagnostic_id: ID do diagnóstico
            update_data: Dados para atualização
            
        Returns:
            Objeto Diagnostic atualizado ou None se não encontrado
        """
        db_obj = self.get_by_id(diagnostic_id)
        if db_obj:
            for key, value in update_data.items():
                setattr(db_obj, key, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, diagnostic_id: str) -> bool:
        """Exclui um diagnóstico pelo ID.
        
        Args:
            diagnostic_id: ID do diagnóstico
            
        Returns:
            True se excluído com sucesso, False caso contrário
        """
        db_obj = self.get_by_id(diagnostic_id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False
    
    def get_diagnostics_paginated(
        self,
        user_id: str,
        page: int = 1,
        limit: int = 10,
        filters: Dict[str, Any] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[List[Diagnostic], int]:
        """Obtém diagnósticos paginados com filtros.
        
        Args:
            user_id: ID do usuário
            page: Número da página (começando em 1)
            limit: Itens por página
            filters: Filtros adicionais (device_id, status, etc.)
            start_date: Data inicial para filtro (formato ISO)
            end_date: Data final para filtro (formato ISO)
            
        Returns:
            Tupla com lista de diagnósticos e contagem total
        """
        # Inicializar query base
        query = self.db.query(Diagnostic).filter(Diagnostic.user_id == user_id)
        
        # Aplicar filtros adicionais
        if filters:
            for key, value in filters.items():
                if hasattr(Diagnostic, key) and value is not None:
                    query = query.filter(getattr(Diagnostic, key) == value)
        
        # Aplicar filtros de data
        if start_date:
            try:
                start_datetime = datetime.fromisoformat(start_date)
                query = query.filter(Diagnostic.created_at >= start_datetime)
            except ValueError:
                pass  # Ignorar data inválida
        
        if end_date:
            try:
                end_datetime = datetime.fromisoformat(end_date)
                query = query.filter(Diagnostic.created_at <= end_datetime)
            except ValueError:
                pass  # Ignorar data inválida
        
        # Obter contagem total
        total = query.count()
        
        # Aplicar paginação
        offset = (page - 1) * limit
        items = query.order_by(desc(Diagnostic.created_at)).offset(offset).limit(limit).all()
        
        return items, total