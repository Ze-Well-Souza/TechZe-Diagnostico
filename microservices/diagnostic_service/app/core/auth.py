"""
Módulo de Autenticação Simplificado
Implementação básica para desenvolvimento
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security scheme para tokens
security = HTTPBearer(auto_error=False)

# Mock user database para desenvolvimento
MOCK_USERS = {
    "admin": {
        "id": "admin-001",
        "username": "admin",
        "email": "admin@techze.com",
        "role": "admin",
        "permissions": ["*"]  # Todas as permissões
    },
    "tecnico": {
        "id": "tecnico-001", 
        "username": "tecnico",
        "email": "tecnico@techze.com",
        "role": "tecnico",
        "permissions": [
            "orcamentos:create", "orcamentos:read", "orcamentos:update",
            "estoque:read", "estoque:movimentacao",
            "os:create", "os:read", "os:update_status", "os:add_items", "os:add_notes", "os:add_photos"
        ]
    },
    "gerente": {
        "id": "gerente-001",
        "username": "gerente", 
        "email": "gerente@techze.com",
        "role": "gerente",
        "permissions": [
            "orcamentos:*", "estoque:*", "os:*"  # Todas dentro do domínio
        ]
    },
    "cliente": {
        "id": "cliente-001",
        "username": "cliente",
        "email": "cliente@exemplo.com", 
        "role": "cliente",
        "permissions": [
            "orcamentos:read", "orcamentos:approve", "orcamentos:reject",
            "os:read"
        ]
    }
}

# Mock tokens para desenvolvimento
MOCK_TOKENS = {
    "admin-token": "admin",
    "tecnico-token": "tecnico", 
    "gerente-token": "gerente",
    "cliente-token": "cliente"
}

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Dict[str, Any]:
    """
    Obtém o usuário atual baseado no token
    
    Para desenvolvimento, usa tokens mock simples
    Em produção, validaria JWT com Supabase/Auth0
    """
    
    # Para desenvolvimento, permitir acesso sem token (como admin)
    if not credentials:
        return MOCK_USERS["admin"]
    
    token = credentials.credentials
    
    # Verificar token mock
    if token in MOCK_TOKENS:
        username = MOCK_TOKENS[token]
        return MOCK_USERS[username]
    
    # Token inválido
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Verifica se o usuário está ativo
    """
    # Para desenvolvimento, todos os usuários estão ativos
    return current_user

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verifica um token e retorna os dados do usuário
    
    Em produção, faria validação JWT completa
    """
    if token in MOCK_TOKENS:
        username = MOCK_TOKENS[token]
        return MOCK_USERS[username]
    return None

def create_access_token(user_data: Dict[str, Any]) -> str:
    """
    Cria um token de acesso
    
    Em produção, geraria JWT com expiração
    """
    # Para desenvolvimento, retornar token mock
    username = user_data.get("username")
    for token, user in MOCK_TOKENS.items():
        if user == username:
            return token
    
    # Gerar token genérico para desenvolvimento
    return f"{username}-token"

# Funções auxiliares para tokens de API
def get_api_key_user(api_key: str) -> Optional[Dict[str, Any]]:
    """
    Valida API key e retorna dados do usuário
    """
    # Em produção, validaria contra banco de dados
    if api_key == "dev-api-key":
        return MOCK_USERS["admin"]
    return None