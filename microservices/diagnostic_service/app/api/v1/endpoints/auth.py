"""
Endpoints de Autenticação - Sistema TechZe Diagnóstico
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import jwt
import bcrypt
import logging

from app.core.config import settings
from app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

class UserLogin(BaseModel):
    """Schema para login de usuário"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Schema para token de acesso"""
    access_token: str
    token_type: str
    expires_in: int
    user_info: Dict[str, Any]

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login que retorna token JWT
    """
    try:
        supabase = get_supabase_client()
        
        # Autenticar com Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": form_data.username,
            "password": form_data.password
        })
        
        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Criar token JWT
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": auth_response.user.id, "email": auth_response.user.email},
            expires_delta=access_token_expires
        )
        
        user_info = {
            "id": auth_response.user.id,
            "email": auth_response.user.email,
            "name": auth_response.user.user_metadata.get("name", ""),
            "role": auth_response.user.user_metadata.get("role", "user")
        }
        
        logger.info(f"Login realizado com sucesso: {form_data.username}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_info": user_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno do servidor"
        )

@router.post("/login", response_model=Token)
async def login_user(user_login: UserLogin):
    """
    Login alternativo usando JSON
    """
    try:
        # Usar o mesmo endpoint interno
        from fastapi.security import OAuth2PasswordRequestForm
        
        # Simular form data
        form_data = OAuth2PasswordRequestForm(
            username=user_login.email,
            password=user_login.password
        )
        
        return await login_for_access_token(form_data)
        
    except Exception as e:
        logger.error(f"Erro no login JSON: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro no login"
        )

@router.get("/me")
async def get_current_user_info():
    """
    Retorna informações do usuário atual
    """
    try:
        supabase = get_supabase_client()
        
        # Buscar dados do usuário via Supabase Auth
        user = await supabase.auth.get_user()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )
        
        return {
            "id": user.user.id,
            "email": user.user.email,
            "name": user.user.user_metadata.get("name", ""),
            "role": user.user.user_metadata.get("role", "user")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar informações do usuário"
        )

@router.post("/logout")
async def logout_user():
    """
    Logout do usuário
    """
    try:
        supabase = get_supabase_client()
        
        # Supabase logout
        supabase.auth.sign_out()
        
        logger.info(f"Logout realizado: {current_user}")
        
        return {"message": "Logout realizado com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro no logout: {e}")
        return {"message": "Logout realizado"}

@router.get("/health")
async def auth_health_check():
    """
    Health check do sistema de autenticação
    """
    try:
        supabase = get_supabase_client()
        return {
            "status": "healthy",
            "supabase_connected": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro no health check de auth: {e}")
        return {
            "status": "unhealthy",
            "supabase_connected": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Funções auxiliares

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cria token JWT de acesso
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user_from_token(token: str = Depends(oauth2_scheme)) -> str:
    """
    Valida token JWT e retorna ID do usuário
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    return user_id 