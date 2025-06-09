# -*- coding: utf-8 -*-
"""
Cliente Supabase para a API Core.

Este módulo fornece uma interface unificada para interagir com o Supabase,
incluindo autenticação e operações de banco de dados.
"""

from typing import Optional
from supabase import create_client, Client
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Cliente Supabase global
_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """
    Retorna uma instância do cliente Supabase.
    
    Utiliza o padrão singleton para garantir que apenas uma instância
    seja criada durante o ciclo de vida da aplicação.
    
    Returns:
        Client: Instância do cliente Supabase
        
    Raises:
        ValueError: Se as configurações do Supabase não estiverem definidas
    """
    global _supabase_client
    
    if _supabase_client is None:
        try:
            # Validar configurações
            if not settings.supabase.url:
                raise ValueError("SUPABASE_URL não configurado")
            
            if not settings.supabase.key:
                raise ValueError("SUPABASE_ANON_KEY não configurado")
            
            # Criar cliente Supabase
            _supabase_client = create_client(
                supabase_url=settings.supabase.url,
                supabase_key=settings.supabase.key
            )
            
            logger.info("Cliente Supabase inicializado com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Supabase: {e}")
            raise
    
    return _supabase_client

def reset_supabase_client():
    """
    Reseta o cliente Supabase.
    
    Útil para testes ou quando as configurações mudam.
    """
    global _supabase_client
    _supabase_client = None
    logger.info("Cliente Supabase resetado")

def health_check() -> dict:
    """
    Verifica a saúde da conexão com o Supabase.
    
    Returns:
        dict: Status da conexão
    """
    try:
        client = get_supabase_client()
        
        # Teste simples de conectividade
        # Tentativa de buscar informações do usuário atual
        response = client.auth.get_session()
        
        return {
            "status": "healthy",
            "connected": True,
            "url": settings.supabase.url,
            "message": "Conexão com Supabase estabelecida"
        }
        
    except Exception as e:
        logger.error(f"Erro no health check do Supabase: {e}")
        return {
            "status": "unhealthy",
            "connected": False,
            "error": str(e),
            "message": "Falha na conexão com Supabase"
        }