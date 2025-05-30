from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Cliente global do Supabase
supabase_client: Client = None

def initialize_supabase() -> Client:
    """Inicializa o cliente do Supabase."""
    global supabase_client
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        logger.error("SUPABASE_URL e SUPABASE_KEY devem estar configurados")
        raise ValueError("Configurações do Supabase não encontradas")
    
    try:
        supabase_client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        logger.info("Cliente Supabase inicializado com sucesso")
        return supabase_client
    except Exception as e:
        logger.error(f"Erro ao inicializar cliente Supabase: {e}")
        raise

def get_supabase_client() -> Client:
    """Retorna o cliente do Supabase."""
    global supabase_client
    
    if supabase_client is None:
        supabase_client = initialize_supabase()
    
    return supabase_client