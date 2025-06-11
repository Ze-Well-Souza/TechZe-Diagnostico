from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import ValidationError

from app.core.config import settings

# Atualização para usar algoritmos mais seguros e configurações modernas
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Aumentando o custo do bcrypt para maior segurança
)


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Cria um token JWT de acesso.
    
    Args:
        subject: Identificador do usuário (geralmente user_id)
        expires_delta: Tempo de expiração do token
        
    Returns:
        Token JWT codificado
    """
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Adicionando mais claims para aumentar a segurança
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.now(timezone.utc),  # Issued At
        "nbf": datetime.now(timezone.utc),  # Not Before
        "jti": f"{subject}-{datetime.now(timezone.utc).timestamp()}"  # JWT ID único
    }
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica se a senha em texto plano corresponde à senha hash.
    
    Args:
        plain_password: Senha em texto plano
        hashed_password: Senha hash armazenada
        
    Returns:
        True se a senha corresponder, False caso contrário
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Gera um hash seguro para a senha.
    
    Args:
        password: Senha em texto plano
        
    Returns:
        Hash da senha
    """
    return pwd_context.hash(password)


def decode_access_token(token: str) -> Optional[dict]:
    """Decodifica e valida um token JWT.
    
    Args:
        token: Token JWT a ser decodificado
        
    Returns:
        Payload do token se válido, None caso contrário
    """
    try:
        # Adicionando verificações de segurança adicionais
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM],
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "require_exp": True,
                "require_iat": True,
                "require_nbf": True
            }
        )
        return payload
    except (JWTError, ValidationError):
        return None


def get_token_data(token: str) -> Optional[str]:
    """Extrai o subject (geralmente user_id) do token JWT.
    
    Args:
        token: Token JWT
        
    Returns:
        Subject do token se válido, None caso contrário
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")
    return None


# Configuração de segurança para autenticação via Bearer token
security = HTTPBearer(
    auto_error=True,
    description="Bearer Authentication"
)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Obtém o usuário atual a partir do token JWT.
    
    Args:
        credentials: Credenciais de autorização HTTP
        
    Returns:
        ID do usuário atual
        
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    token = credentials.credentials
    user_id = get_token_data(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id