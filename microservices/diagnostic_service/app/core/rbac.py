"""
Sistema RBAC (Role-Based Access Control) Simplificado
Controle de permissões baseado em roles e permissões específicas
"""

from typing import Dict, Any, List, Callable
from fastapi import HTTPException, status, Depends
from .auth import get_current_user

# Definição de roles e suas permissões padrão
ROLE_PERMISSIONS = {
    "admin": ["*"],  # Acesso total
    "gerente": [
        "orcamentos:*",
        "estoque:*", 
        "os:*",
        "reports:*",
        "dashboard:*"
    ],
    "tecnico": [
        "orcamentos:create", "orcamentos:read", "orcamentos:update",
        "estoque:read", "estoque:list", "estoque:movimentacao",
        "os:create", "os:read", "os:list", "os:update_status", 
        "os:add_items", "os:add_notes", "os:add_photos", "os:dashboard"
    ],
    "cliente": [
        "orcamentos:read", "orcamentos:approve", "orcamentos:reject",
        "os:read"
    ]
}

def has_permission(user: Dict[str, Any], required_permission: str) -> bool:
    """
    Verifica se o usuário tem a permissão específica
    
    Args:
        user: Dados do usuário com role e permissions
        required_permission: Permissão necessária (ex: "orcamentos:create")
    
    Returns:
        bool: True se tem permissão, False caso contrário
    """
    # Admin tem acesso a tudo
    if user.get("role") == "admin":
        return True
    
    # Verificar permissões específicas do usuário
    user_permissions = user.get("permissions", [])
    
    # Permissão exata
    if required_permission in user_permissions:
        return True
    
    # Permissões wildcard (ex: "orcamentos:*")
    domain = required_permission.split(":")[0]
    if f"{domain}:*" in user_permissions:
        return True
    
    # Permissão global wildcard
    if "*" in user_permissions:
        return True
    
    # Verificar permissões baseadas no role
    role_permissions = ROLE_PERMISSIONS.get(user.get("role"), [])
    
    # Permissão exata no role
    if required_permission in role_permissions:
        return True
    
    # Permissões wildcard no role
    if f"{domain}:*" in role_permissions:
        return True
    
    # Permissão global wildcard no role
    if "*" in role_permissions:
        return True
    
    return False

def require_permission(permission: str) -> Callable:
    """
    Decorator/dependency para exigir permissão específica
    
    Args:
        permission: Permissão necessária (ex: "orcamentos:create")
    
    Returns:
        Dependency function para FastAPI
    """
    async def check_permission(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão insuficiente. Necessário: {permission}"
            )
        return None
    
    return check_permission

def require_role(role: str) -> Callable:
    """
    Decorator/dependency para exigir role específico
    
    Args:
        role: Role necessário (ex: "admin", "gerente")
    
    Returns:
        Dependency function para FastAPI
    """
    async def check_role(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        if current_user.get("role") != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role insuficiente. Necessário: {role}"
            )
        return None
    
    return check_role

def require_any_role(roles: List[str]) -> Callable:
    """
    Decorator/dependency para exigir qualquer um dos roles especificados
    
    Args:
        roles: Lista de roles aceitos
    
    Returns:
        Dependency function para FastAPI
    """
    async def check_any_role(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ):
        user_role = current_user.get("role")
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role insuficiente. Necessário um de: {', '.join(roles)}"
            )
        return None
    
    return check_any_role

def get_user_permissions(user: Dict[str, Any]) -> List[str]:
    """
    Retorna todas as permissões do usuário
    
    Args:
        user: Dados do usuário
    
    Returns:
        Lista de permissões
    """
    permissions = set()
    
    # Permissões específicas do usuário
    user_permissions = user.get("permissions", [])
    permissions.update(user_permissions)
    
    # Permissões do role
    role_permissions = ROLE_PERMISSIONS.get(user.get("role"), [])
    permissions.update(role_permissions)
    
    return list(permissions)

def can_access_resource(user: Dict[str, Any], resource_owner_id: str) -> bool:
    """
    Verifica se o usuário pode acessar um recurso específico
    
    Args:
        user: Dados do usuário
        resource_owner_id: ID do dono do recurso
    
    Returns:
        bool: True se pode acessar, False caso contrário
    """
    user_role = user.get("role")
    user_id = user.get("id")
    
    # Admin e gerente podem acessar tudo
    if user_role in ["admin", "gerente"]:
        return True
    
    # Técnicos podem acessar recursos atribuídos a eles
    if user_role == "tecnico":
        return user_id == resource_owner_id
    
    # Clientes podem acessar apenas seus próprios recursos
    if user_role == "cliente":
        return user_id == resource_owner_id
    
    return False

def filter_by_access_level(
    user: Dict[str, Any], 
    items: List[Dict[str, Any]], 
    owner_field: str = "cliente_id"
) -> List[Dict[str, Any]]:
    """
    Filtra uma lista de items baseado no nível de acesso do usuário
    
    Args:
        user: Dados do usuário
        items: Lista de items para filtrar
        owner_field: Campo que identifica o dono do item
    
    Returns:
        Lista filtrada de items
    """
    user_role = user.get("role")
    user_id = user.get("id")
    
    # Admin e gerente veem tudo
    if user_role in ["admin", "gerente"]:
        return items
    
    # Técnicos veem items atribuídos a eles
    if user_role == "tecnico":
        return [
            item for item in items 
            if item.get("tecnico_responsavel") == user_id
        ]
    
    # Clientes veem apenas seus próprios items
    if user_role == "cliente":
        return [
            item for item in items 
            if item.get(owner_field) == user_id or 
               (hasattr(item, "cliente") and item.cliente.get("id") == user_id)
        ]
    
    return []

# Funções auxiliares para verificações específicas

def is_admin(user: Dict[str, Any]) -> bool:
    """Verifica se o usuário é admin"""
    return user.get("role") == "admin"

def is_manager(user: Dict[str, Any]) -> bool:
    """Verifica se o usuário é gerente"""
    return user.get("role") == "gerente"

def is_technician(user: Dict[str, Any]) -> bool:
    """Verifica se o usuário é técnico"""
    return user.get("role") == "tecnico"

def is_client(user: Dict[str, Any]) -> bool:
    """Verifica se o usuário é cliente"""
    return user.get("role") == "cliente"

def can_manage_users(user: Dict[str, Any]) -> bool:
    """Verifica se pode gerenciar usuários"""
    return has_permission(user, "users:manage")

def can_view_reports(user: Dict[str, Any]) -> bool:
    """Verifica se pode visualizar relatórios"""
    return has_permission(user, "reports:view")

def can_manage_system(user: Dict[str, Any]) -> bool:
    """Verifica se pode gerenciar o sistema"""
    return has_permission(user, "system:manage")

# Middleware de auditoria (para logs de acesso)
def log_access(user: Dict[str, Any], resource: str, action: str):
    """
    Registra acesso a recurso para auditoria
    
    Args:
        user: Dados do usuário
        resource: Recurso acessado
        action: Ação realizada
    """
    # TODO: Implementar log de auditoria em produção
    print(f"AUDIT: User {user.get('username')} ({user.get('role')}) {action} on {resource}")

# Exemplo de uso em endpoints:
"""
@router.get("/sensitive-data")
async def get_sensitive_data(
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_permission("data:read"))
):
    # Endpoint protegido que requer permissão específica
    pass

@router.post("/admin-only")
async def admin_endpoint(
    current_user: dict = Depends(get_current_user),
    _: None = Depends(require_role("admin"))
):
    # Endpoint apenas para admins
    pass
""" 