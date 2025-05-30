from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional
import logging
from app.core.config import settings
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extrai e valida o usuário atual a partir do token JWT."""
    try:
        token = credentials.credentials
        
        # Decodifica o token JWT do Supabase
        payload = jwt.decode(
            token, 
            settings.SUPABASE_JWT_SECRET, 
            algorithms=["HS256"],
            options={"verify_aud": False}  # Supabase usa audience específica
        )
        
        user_id = payload.get("sub")
        if user_id is None:
            logger.warning("Token JWT não contém 'sub' (user_id)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: user_id não encontrado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"Usuário autenticado: {user_id}")
        return user_id
        
    except JWTError as e:
        logger.error(f"Erro ao decodificar token JWT: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Erro inesperado na autenticação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[str]:
    """Extrai o usuário atual se o token estiver presente, caso contrário retorna None."""
    if credentials is None:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

def verify_supabase_token(token: str) -> dict:
    """Verifica um token do Supabase e retorna o payload."""
    try:
        supabase = get_supabase_client()
        
        # Verifica o token usando o cliente do Supabase
        user = supabase.auth.get_user(token)
        
        if user and user.user:
            return {
                "user_id": user.user.id,
                "email": user.user.email,
                "metadata": user.user.user_metadata
            }
        else:
            raise ValueError("Token inválido")
            
    except Exception as e:
        logger.error(f"Erro ao verificar token do Supabase: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )