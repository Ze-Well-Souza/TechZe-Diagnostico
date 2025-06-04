"""
Repositório base para operações com Supabase
Implementa o padrão Repository para acesso a dados no Supabase
"""
from typing import Dict, List, Any, Optional, Generic, TypeVar, Type
from pydantic import BaseModel
import logging
from datetime import datetime

from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

# Tipo genérico para modelos Pydantic
T = TypeVar('T', bound=BaseModel)


class SupabaseRepository(Generic[T]):
    """
    Classe base de repositório para operações com Supabase
    Deve ser estendida por repositórios específicos
    
    Exemplo:
    ```python
    class UserRepository(SupabaseRepository[UserModel]):
        def __init__(self):
            super().__init__(table_name="users", model_class=UserModel)
    ```
    """
    
    def __init__(self, table_name: str, model_class: Type[T]):
        """
        Inicializa o repositório
        
        Args:
            table_name: Nome da tabela no Supabase
            model_class: Classe do modelo Pydantic
        """
        self.table_name = table_name
        self.model_class = model_class
        self.supabase_client = get_supabase_client()
    
    def _to_model(self, data: Dict[str, Any]) -> T:
        """
        Converte dados do Supabase para modelo Pydantic
        
        Args:
            data: Dados do Supabase
            
        Returns:
            Instância do modelo Pydantic
        """
        try:
            return self.model_class.parse_obj(data)
        except Exception as e:
            logger.error(f"Erro ao converter dados para modelo {self.model_class.__name__}: {e}")
            # Fallback: retorna modelo com dados padrão
            return self.model_class.construct(**data)
    
    async def get_by_id(self, id: str) -> Optional[T]:
        """
        Obtém registro por ID
        
        Args:
            id: ID do registro
            
        Returns:
            Modelo Pydantic ou None se não encontrado
        """
        try:
            result = self.supabase_client.table(self.table_name).select("*").eq("id", id).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Erro ao buscar {self.table_name} por ID: {result.error}")
                return None
                
            data = result.data
            
            if not data or len(data) == 0:
                return None
                
            return self._to_model(data[0])
        except Exception as e:
            logger.error(f"Exceção ao buscar {self.table_name} por ID: {e}")
            return None
    
    async def list(self, 
                 filters: Optional[Dict[str, Any]] = None,
                 limit: int = 100,
                 offset: int = 0,
                 order_by: str = "created_at",
                 order_desc: bool = True) -> List[T]:
        """
        Lista registros com filtros
        
        Args:
            filters: Dicionário de filtros (campo: valor)
            limit: Limite de registros
            offset: Deslocamento para paginação
            order_by: Campo para ordenação
            order_desc: Ordenação descendente
            
        Returns:
            Lista de modelos Pydantic
        """
        try:
            query = self.supabase_client.table(self.table_name).select("*")
            
            # Aplica filtros
            if filters:
                for field, value in filters.items():
                    if value is not None:
                        query = query.eq(field, value)
            
            # Aplica ordenação
            query = query.order(order_by, desc=order_desc)
            
            # Aplica paginação
            query = query.range(offset, offset + limit - 1)
            
            # Executa query
            result = query.execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Erro ao listar {self.table_name}: {result.error}")
                return []
                
            data = result.data
            
            # Converte para modelos
            return [self._to_model(item) for item in data]
        except Exception as e:
            logger.error(f"Exceção ao listar {self.table_name}: {e}")
            return []
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Conta registros com filtros
        
        Args:
            filters: Dicionário de filtros (campo: valor)
            
        Returns:
            Número de registros
        """
        try:
            query = self.supabase_client.table(self.table_name).select("*", count="exact")
            
            # Aplica filtros
            if filters:
                for field, value in filters.items():
                    if value is not None:
                        query = query.eq(field, value)
            
            # Executa query
            result = query.execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Erro ao contar {self.table_name}: {result.error}")
                return 0
                
            return result.count
        except Exception as e:
            logger.error(f"Exceção ao contar {self.table_name}: {e}")
            return 0
    
    async def create(self, data: Dict[str, Any]) -> Optional[T]:
        """
        Cria novo registro
        
        Args:
            data: Dados do registro
            
        Returns:
            Modelo criado ou None se falhar
        """
        try:
            # Adiciona timestamp se não existir
            if "created_at" not in data:
                data["created_at"] = datetime.now().isoformat()
            
            result = self.supabase_client.table(self.table_name).insert(data).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Erro ao criar {self.table_name}: {result.error}")
                return None
                
            created_data = result.data[0] if result.data and len(result.data) > 0 else None
            
            if not created_data:
                return None
                
            return self._to_model(created_data)
        except Exception as e:
            logger.error(f"Exceção ao criar {self.table_name}: {e}")
            return None
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """
        Atualiza registro existente
        
        Args:
            id: ID do registro
            data: Dados para atualizar
            
        Returns:
            Modelo atualizado ou None se falhar
        """
        try:
            # Adiciona timestamp de atualização
            if "updated_at" not in data:
                data["updated_at"] = datetime.now().isoformat()
            
            result = self.supabase_client.table(self.table_name).update(data).eq("id", id).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Erro ao atualizar {self.table_name}: {result.error}")
                return None
                
            updated_data = result.data[0] if result.data and len(result.data) > 0 else None
            
            if not updated_data:
                return None
                
            return self._to_model(updated_data)
        except Exception as e:
            logger.error(f"Exceção ao atualizar {self.table_name}: {e}")
            return None
    
    async def delete(self, id: str) -> bool:
        """
        Remove registro
        
        Args:
            id: ID do registro
            
        Returns:
            True se removido com sucesso
        """
        try:
            result = self.supabase_client.table(self.table_name).delete().eq("id", id).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Erro ao remover {self.table_name}: {result.error}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Exceção ao remover {self.table_name}: {e}")
            return False
    
    async def execute_raw_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executa query SQL raw
        
        Args:
            query: Query SQL
            params: Parâmetros da query
            
        Returns:
            Resultados da query
        """
        try:
            params = params or {}
            result = await self.supabase_client.rpc("execute_sql", {"query": query, "params": params}).execute()
            
            if hasattr(result, 'error') and result.error:
                logger.error(f"Erro ao executar query raw: {result.error}")
                return []
                
            return result.data if hasattr(result, 'data') else []
        except Exception as e:
            logger.error(f"Exceção ao executar query raw: {e}")
            return [] 