"""Configurações de Produção para Autenticação

Sistema robusto de autenticação para ambiente de produção.
"""

import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from fastapi import HTTPException, status
import jwt
import logging

logger = logging.getLogger(__name__)

class ProductionAuthSettings:
    """Configurações de autenticação para produção"""
    
    def __init__(self):
        # JWT Settings
        self.secret_key = os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32))
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
        
        # Password Settings
        self.password_min_length = 8
        self.require_special_chars = True
        self.bcrypt_rounds = 12
        
        # Security Settings
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 15
        
        # Database
        self.database_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/techze_prod")
        
        # Production mode
        self.environment = os.getenv("ENVIRONMENT", "production")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"

# Global settings
auth_settings = ProductionAuthSettings()

# Password hashing
pwd_context = CryptContext(
    schemes=["bcrypt"], 
    deprecated="auto",
    bcrypt__rounds=auth_settings.bcrypt_rounds
)

class ProductionAuthService:
    """Serviço de autenticação para produção"""
    
    def __init__(self):
        self.settings = auth_settings
        self.failed_attempts: Dict[str, Dict[str, Any]] = {}
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verificar senha com hash bcrypt"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Gerar hash da senha"""
        return pwd_context.hash(password)
    
    def validate_password_strength(self, password: str) -> bool:
        """Validar força da senha"""
        if len(password) < self.settings.password_min_length:
            return False
        
        if self.settings.require_special_chars:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(char in special_chars for char in password):
                return False
            
            # Verificar maiúscula, minúscula e número
            if not (any(c.isupper() for c in password) and 
                   any(c.islower() for c in password) and 
                   any(c.isdigit() for c in password)):
                return False
        
        return True
    
    def check_rate_limit(self, identifier: str) -> bool:
        """Verificar se usuário não está bloqueado por tentativas"""
        if identifier not in self.failed_attempts:
            return True
        
        attempt_data = self.failed_attempts[identifier]
        lockout_until = attempt_data.get("lockout_until")
        
        if lockout_until and datetime.now() < lockout_until:
            return False
        
        return True
    
    def record_failed_attempt(self, identifier: str):
        """Registrar tentativa de login falhada"""
        now = datetime.now()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = {"attempts": 0, "first_attempt": now}
        
        self.failed_attempts[identifier]["attempts"] += 1
        self.failed_attempts[identifier]["last_attempt"] = now
        
        # Se excedeu tentativas, bloquear
        if self.failed_attempts[identifier]["attempts"] >= self.settings.max_login_attempts:
            lockout_until = now + timedelta(minutes=self.settings.lockout_duration_minutes)
            self.failed_attempts[identifier]["lockout_until"] = lockout_until
            
            logger.warning(f"Usuário {identifier} bloqueado até {lockout_until}")
    
    def clear_failed_attempts(self, identifier: str):
        """Limpar tentativas falhadas após login bem-sucedido"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Criar token JWT de acesso"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=self.settings.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        
        return jwt.encode(to_encode, self.settings.secret_key, algorithm=self.settings.algorithm)
    
    def create_refresh_token(self, data: dict) -> str:
        """Criar token JWT de refresh"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=self.settings.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })
        
        return jwt.encode(to_encode, self.settings.secret_key, algorithm=self.settings.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verificar e decodificar token JWT"""
        try:
            payload = jwt.decode(
                token, 
                self.settings.secret_key, 
                algorithms=[self.settings.algorithm]
            )
            
            # Verificar tipo do token
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Token inválido: esperado {token_type}"
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except jwt.JWTError as e:
            logger.error(f"Erro ao verificar token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
    
    def get_security_headers(self) -> Dict[str, str]:
        """Headers de segurança para produção"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

# Instância global do serviço
auth_service = ProductionAuthService()

def get_production_auth_service() -> ProductionAuthService:
    """Retorna instância do serviço de autenticação"""
    return auth_service
