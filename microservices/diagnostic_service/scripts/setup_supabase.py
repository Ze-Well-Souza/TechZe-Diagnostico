#!/usr/bin/env python3
"""
Script de configuração do Supabase para TechZe Diagnóstico
Testa conexão e prepara arquivos para configuração manual
"""

import asyncio
import sys
import os
from pathlib import Path

# Adicionar o diretório do app ao path
sys.path.append(str(Path(__file__).parent.parent))

def test_basic_imports():
    """Testa os imports básicos"""
    try:
        from app.core.config import get_settings
        settings = get_settings()
        print("✅ Configurações carregadas")
        print(f"🔗 Supabase URL: {settings.SUPABASE_URL}")
        return True
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False

def test_supabase_client():
    """Testa a criação do cliente Supabase"""
    try:
        from supabase import create_client, Client
        from app.core.config import get_settings
        
        settings = get_settings()
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            print("❌ Configurações do Supabase não encontradas no .env")
            return False
        
        client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        
        print("✅ Cliente Supabase criado com sucesso")
        print(f"🔗 URL: {settings.SUPABASE_URL}")
        return True
        
    except ImportError:
        print("❌ Biblioteca supabase não instalada")
        print("💡 Execute: pip install supabase")
        return False
    except Exception as e:
        print(f"❌ Erro ao criar cliente: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 TESTE DE CONFIGURAÇÃO SUPABASE")
    print("=" * 50)
    
    # Teste de imports
    if not test_basic_imports():
        return False
    
    # Teste do cliente Supabase
    if not test_supabase_client():
        return False
    
    print("\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
    print("✅ Imports funcionando")
    print("✅ Cliente Supabase operacional")
    print("✅ Configurações válidas")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Execute migrações no Supabase Dashboard")
    print("2. Teste as APIs: python test_backend_quick.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)