#!/bin/bash

# Script de inicialização simplificado para o Render
echo "🚀 Iniciando TechZe Diagnóstico API no Render..."

# Definir variáveis de ambiente padrão
export ENVIRONMENT=${ENVIRONMENT:-production}
export LOG_LEVEL=${LOG_LEVEL:-info}
export CORS_ORIGINS=${CORS_ORIGINS:-*}
export PYTHONPATH="."

# Verificar se estamos no diretório correto
echo "📂 Diretório atual: $(pwd)"
echo "📋 Conteúdo do diretório:"
ls -la

# Se o arquivo main.py não estiver na raiz, tentar localizar
if [ ! -f "app/main.py" ]; then
    echo "⚠️ app/main.py não encontrado no diretório atual"
    
    # Verificar se estamos no diretório raiz do projeto
    if [ -d "microservices/diagnostic_service" ]; then
        echo "📁 Navegando para microservices/diagnostic_service"
        cd microservices/diagnostic_service
    fi
    
    # Verificar novamente
    if [ ! -f "app/main.py" ]; then
        echo "❌ ERRO: app/main.py não encontrado"
        echo "🔍 Procurando arquivos main.py:"
        find . -name "main.py" -type f 2>/dev/null || echo "Nenhum main.py encontrado"
        exit 1
    fi
fi

echo "✅ Arquivo app/main.py encontrado"
echo "📂 Diretório de trabalho: $(pwd)"

# Verificar imports críticos
echo "🔍 Testando importações..."
python -c "
import sys
sys.path.insert(0, '.')
try:
    from app.main import app
    print('✅ Importação do app bem-sucedida')
except ImportError as e:
    print(f'❌ Erro de importação: {e}')
    import os
    print(f'PYTHONPATH: {os.environ.get(\"PYTHONPATH\", \"não definido\")}')
    print(f'sys.path: {sys.path[:3]}...')
    exit(1)
"

echo "🎯 Iniciando servidor uvicorn..."
echo "🌐 Host: 0.0.0.0"
echo "🔢 Port: ${PORT:-8000}"

# Iniciar o servidor com configurações otimizadas
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --log-level ${LOG_LEVEL:-info} \
    --access-log \
    --timeout-keep-alive 65 \
    --timeout-graceful-shutdown 30 