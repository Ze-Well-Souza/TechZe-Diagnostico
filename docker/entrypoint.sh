#!/bin/bash
# TechZe-Diagnóstico - Script de Inicialização
# ASSISTENTE IA - Entrypoint para container de produção

set -e

echo "🚀 TechZe-Diagnóstico - Iniciando container..."

# Aguarda serviços essenciais
echo "⏳ Aguardando Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "✅ Redis disponível"

# Configura permissões
chown -R techze:techze /app/logs /app/data

# Executa migrações se necessário
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🗄️ Executando verificações de banco..."
    python -c "
import asyncio
from app.core.supabase import get_supabase_client

async def check_db():
    try:
        client = get_supabase_client()
        result = client.table('users').select('count').execute()
        print('✅ Conexão com Supabase OK')
    except Exception as e:
        print(f'❌ Erro na conexão: {e}')
        exit(1)

asyncio.run(check_db())
    "
fi

# Inicializa logs
mkdir -p /app/logs
touch /app/logs/techze.log
touch /app/logs/error.log

echo "✅ TechZe-Diagnóstico inicializado com sucesso!"

# Executa comando passado
exec "$@" 