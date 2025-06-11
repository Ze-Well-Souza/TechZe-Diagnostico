from supabase import create_client, Client
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

# Cliente global do Supabase
supabase_client: Client = None

def initialize_supabase() -> Client:
    """Inicializa o cliente do Supabase."""
    global supabase_client
    
    settings = get_settings()
    
    # Usar SUPABASE_SERVICE_KEY se disponível, senão SUPABASE_KEY
    supabase_key = settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY
    
    if not settings.SUPABASE_URL or not supabase_key:
        logger.warning("SUPABASE_URL e SUPABASE_SERVICE_KEY não configurados - modo fallback")
        # Retornar um mock client para desenvolvimento
        return MockSupabaseClient()
    
    try:
        # Configurações básicas sem proxy para evitar erro
        supabase_client = create_client(
            settings.SUPABASE_URL,
            supabase_key,
            options={
                "auto_refresh_token": True,
                "persist_session": True,
            }
        )
        logger.info(f"Cliente Supabase inicializado com sucesso: {settings.SUPABASE_URL}")
        return supabase_client
    except Exception as e:
        logger.warning(f"Erro ao inicializar Supabase: {e} - usando modo fallback")
        return MockSupabaseClient()

def get_supabase_client() -> Client:
    """Retorna o cliente do Supabase."""
    global supabase_client
    
    if supabase_client is None:
        supabase_client = initialize_supabase()
    
    return supabase_client

class MockSupabaseClient:
    """Cliente mock para desenvolvimento quando Supabase não está disponível"""
    
    def __init__(self):
        self.auth = MockAuth()
        logger.info("MockSupabaseClient inicializado para desenvolvimento")
    
    def table(self, table_name):
        return MockTable(table_name)

class MockAuth:
    """Auth mock para desenvolvimento"""
    
    def sign_in_with_password(self, credentials):
        # Simular login de sucesso para desenvolvimento
        return MockAuthResponse()
    
    def sign_out(self):
        return {"message": "Logout simulado"}
    
    def get_user(self):
        return MockUser()

class MockAuthResponse:
    """Response mock para auth"""
    
    def __init__(self):
        self.user = MockUser()

class MockUser:
    """User mock para desenvolvimento"""
    
    def __init__(self):
        self.id = "dev-user-123"
        self.email = "dev@techze.com"
        self.user_metadata = {"name": "Dev User", "role": "admin"}

class MockTable:
    """Table mock para desenvolvimento"""
    
    def __init__(self, table_name):
        self.table_name = table_name
        logger.debug(f"MockTable criada para: {table_name}")
    
    def select(self, *args, **kwargs):
        return self
    
    def insert(self, data):
        logger.debug(f"MockTable.insert chamado para {self.table_name} com dados: {data}")
        return self
    
    def update(self, data):
        logger.debug(f"MockTable.update chamado para {self.table_name} com dados: {data}")
        return self
    
    def eq(self, column, value):
        return self
    
    def filter(self, *args, **kwargs):
        return self
    
    def order(self, *args, **kwargs):
        return self
    
    def limit(self, limit):
        return self
    
    def single(self):
        return self
    
    def execute(self):
        logger.debug(f"MockTable.execute chamado para {self.table_name}")
        return type('MockResult', (), {
            'data': [],
            'error': None,
            'count': 0
        })()