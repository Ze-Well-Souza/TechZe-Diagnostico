"""Endpoints de Autenticação - API Core

Versão simplificada para funcionar sem dependências complexas.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import jwt
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/core/auth/token")

# Configurações simplificadas
SECRET_KEY = "dev-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Funções auxiliares

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cria token JWT de acesso
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    return user_id

# Schemas
class UserLogin(BaseModel):
    """Schema para login de usuário"""
    email: EmailStr
    password: str

class UserRegister(BaseModel):
    """Schema para registro de usuário"""
    email: EmailStr
    password: str
    name: str
    role: Optional[str] = "user"

class Token(BaseModel):
    """Schema para token de acesso"""
    access_token: str
    token_type: str
    expires_in: int
    user_info: Dict[str, Any]

class UserInfo(BaseModel):
    """Schema para informações do usuário"""
    id: str
    email: str
    name: str
    role: str
    created_at: Optional[datetime] = None

# Endpoints básicos para teste

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Endpoint de login que retorna token JWT - versão simplificada
    """
    try:
        # Login básico para desenvolvimento
        if form_data.username == "dev@techze.com" and form_data.password == "dev123":
            
            # Criar token JWT
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": "dev-user-123", "email": form_data.username},
                expires_delta=access_token_expires
            )
            
            user_info = {
                "id": "dev-user-123",
                "email": form_data.username,
                "name": "Dev User",
                "role": "admin"
            }
            
            logger.info(f"Login realizado com sucesso: {form_data.username}")
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user_info": user_info
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou senha incorretos",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
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
    Login usando JSON
    """
    try:
        # Simular form data para reutilizar a lógica
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

@router.post("/register", response_model=Token)
async def register_user(user_register: UserRegister):
    """
    Registro básico para desenvolvimento
    """
    try:
        # Registro básico para desenvolvimento
        user_id = f"user_{hash(user_register.email) % 10000}"
        
        # Criar token JWT
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id, "email": user_register.email},
            expires_delta=access_token_expires
        )
        
        user_info = {
            "id": user_id,
            "email": user_register.email,
            "name": user_register.name,
            "role": user_register.role
        }
        
        logger.info(f"Usuário registrado com sucesso: {user_register.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_info": user_info
        }
        
    except Exception as e:
        logger.error(f"Erro no registro: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao registrar usuário"
        )

@router.get("/profile", response_model=UserInfo)
async def get_current_user_profile(current_user: str = Depends(get_current_user_from_token)):
    """
    Retorna informações do usuário atual
    """
    try:
        # Informações básicas baseadas no token
        return {
            "id": current_user,
            "email": "dev@techze.com",
            "name": "Dev User",
            "role": "admin",
            "created_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Erro ao buscar usuário: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao buscar informações do usuário"
        )

@router.post("/logout")
async def logout_user(current_user: str = Depends(get_current_user_from_token)):
    """
    Logout do usuário
    """
    try:
        logger.info(f"Logout realizado: {current_user}")
        return {"message": "Logout realizado com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro no logout: {e}")
        return {"message": "Logout realizado"}

@router.post("/refresh")
async def refresh_token(current_user: str = Depends(get_current_user_from_token)):
    """
    Renovar token de acesso
    """
    try:
        # Criar novo token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": current_user, "email": "dev@techze.com"},
            expires_delta=access_token_expires
        )
        
        user_info = {
            "id": current_user,
            "email": "dev@techze.com",
            "name": "Dev User",
            "role": "admin"
        }
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_info": user_info
        }
        
    except Exception as e:
        logger.error(f"Erro ao renovar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao renovar token"
        )

@router.get("/info")
async def auth_info():
    """
    Informações do domínio de autenticação
    """
    return {
        "domain": "auth",
        "name": "Authentication Domain",
        "version": "1.0.0",
        "description": "Autenticação e autorização de usuários",
        "endpoints": [
            "/token",
            "/login", 
            "/register",
            "/profile",
            "/logout",
            "/refresh",
            "/info",
            "/health"
        ],
        "features": [
            "JWT Authentication",
            "User Registration",
            "Token Refresh",
            "User Profile"
        ]
    }

@router.get("/health")
async def auth_health_check():
    """
    Health check do sistema de autenticação
    """
    return {
        "status": "healthy",
        "service": "auth",
        "timestamp": datetime.now().isoformat(),
        "version": "simplified"
    }

