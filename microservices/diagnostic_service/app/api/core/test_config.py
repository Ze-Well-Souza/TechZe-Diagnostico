#!/usr/bin/env python3
"""
Script de teste para verificar se a configuração da API Core está funcionando.
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv('.env')

print("🔧 Testando configuração da API Core...")
print("="*50)

# Verificar variáveis essenciais
essential_vars = [
    'SUPABASE_URL',
    'SUPABASE_ANON_KEY', 
    'SUPABASE_SERVICE_ROLE_KEY',
    'SUPABASE_JWT_SECRET',
    'SECRET_KEY'
]

print("📋 Verificando variáveis essenciais:")
for var in essential_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: {value[:20]}...")
    else:
        print(f"❌ {var}: NÃO DEFINIDA")

print("\n🔄 Testando importação das configurações...")
try:
    from .config import settings
    print("✅ Configurações importadas com sucesso!")
    print(f"📍 Environment: {settings.ENVIRONMENT.value}")
    print(f"🗄️  Database Host: {settings.DB_HOST}")
    print(f"🔴 Redis Host: {settings.REDIS_HOST}")
    print(f"🔐 Supabase URL: {settings.SUPABASE_URL[:30] if settings.SUPABASE_URL else 'Not configured'}...")
    print("\n🎉 API Core configurada corretamente!")
except Exception as e:
    print(f"❌ Erro ao importar configurações: {e}")
    print("\n🔍 Detalhes do erro:")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("✅ Teste de configuração concluído!")