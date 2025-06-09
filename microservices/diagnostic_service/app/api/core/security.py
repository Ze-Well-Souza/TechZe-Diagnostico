# -*- coding: utf-8 -*-
"""
Módulo de segurança para a API Core.

Fornece funcionalidades de autenticação, autorização e validação de tokens.
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from datetime import datetime, timedelta
import logging

from .config import settings
from .supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/core/auth/token")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT de acesso.
    
    Args:
        data: Dados para incluir no token
        expires_delta: Tempo de expiração do token
        
    Returns:
        str: Token JWT codificado
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.security.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.security.secret_key, 
        algorithm=settings.security.algorithm
    )
    
    return encoded_jwt

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica e decodifica um token JWT.
    
    Args:
        token: Token JWT para verificar
        
    Returns:
        dict: Dados decodificados do token ou None se inválido
    """
    try:
        payload = jwt.decode(
            token, 
            settings.security.secret_key, 
            algorithms=[settings.security.algorithm]
        )
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token expirado")
        return None
        
    except jwt.JWTError as e:
        logger.warning(f"Erro na validação do token: {e}")
        return None

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Obtém o usuário atual baseado no token JWT.
    
    Args:
        token: Token JWT do usuário
        
    Returns:
        dict: Dados do usuário atual
        
    Raises:
        HTTPException: Se o token for inválido ou usuário não encontrado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verificar token
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        # Buscar usuário no Supabase
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        
        if not user_response.user:
            raise credentials_exception
            
        return {
            "id": user_response.user.id,
            "email": user_response.user.email,
            "user_metadata": user_response.user.user_metadata,
            "app_metadata": user_response.user.app_metadata,
            "created_at": user_response.user.created_at
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        raise credentials_exception

async def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Obtém o usuário atual ativo.
    
    Args:
        current_user: Usuário atual
        
    Returns:
        dict: Dados do usuário ativo
        
    Raises:
        HTTPException: Se o usuário estiver inativo
    """
    # Verificar se o usuário está ativo
    # Por padrão, consideramos todos os usuários ativos
    # Esta lógica pode ser expandida conforme necessário
    
    return current_user

def check_permissions(required_permissions: list) -> callable:
    """
    Decorator para verificar permissões do usuário.
    
    Args:
        required_permissions: Lista de permissões necessárias
        
    Returns:
        callable: Decorator de verificação de permissões
    """
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_user)):
        user_permissions = current_user.get("app_metadata", {}).get("permissions", [])
        
        for permission in required_permissions:
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão necessária: {permission}"
                )
        
        return current_user
    
    return permission_checker

def validate_api_key(api_key: str) -> bool:
    """
    Valida uma chave de API.
    
    Args:
        api_key: Chave de API para validar
        
    Returns:
        bool: True se a chave for válida
    """
    # Implementar validação de API key conforme necessário
    # Por enquanto, apenas verifica se não está vazia
    return bool(api_key and len(api_key) > 10)