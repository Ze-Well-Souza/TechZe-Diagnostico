#!/bin/bash

# Script de inicialização para o Render
echo "🚀 Iniciando TechZe Diagnóstico API no Render..."

# Definir variáveis de ambiente padrão se não existirem
export ENVIRONMENT=${ENVIRONMENT:-production}
export LOG_LEVEL=${LOG_LEVEL:-info}
export CORS_ORIGINS=${CORS_ORIGINS:-*}

# Verificar se estamos no diretório correto
if [ ! -f "app/main.py" ]; then
    echo "❌ Arquivo app/main.py não encontrado. Verificando estrutura..."
    ls -la
    echo "Conteúdo do diretório atual:"
    pwd
    echo "Tentando navegar para o diretório correto..."
    
    if [ -d "microservices/diagnostic_service" ]; then
        cd microservices/diagnostic_service
        echo "✅ Navegou para microservices/diagnostic_service"
    fi
fi

# Verificar novamente
if [ ! -f "app/main.py" ]; then
    echo "❌ ERRO: Não foi possível encontrar app/main.py"
    echo "Estrutura do diretório:"
    find . -name "main.py" -type f 2>/dev/null || echo "Nenhum main.py encontrado"
    exit 1
fi

echo "✅ Arquivo app/main.py encontrado"
echo "📂 Diretório atual: $(pwd)"

# Verificar se as dependências estão instaladas
echo "📦 Verificando dependências..."
python -c "import fastapi; print(f'✅ FastAPI {fastapi.__version__} instalado')" || {
    echo "❌ FastAPI não encontrado. Instalando dependências..."
    pip install -r requirements.txt
}

# Verificar se o arquivo principal pode ser importado
echo "🔍 Testando importação do módulo principal..."
python -c "from app.main import app; print('✅ Módulo principal importado com sucesso')" || {
    echo "❌ ERRO: Não foi possível importar app.main"
    echo "Verificando estrutura de arquivos:"
    find . -name "*.py" | head -10
    exit 1
}

echo "🎯 Iniciando servidor uvicorn..."
echo "🌐 Host: 0.0.0.0"
echo "🔢 Port: ${PORT:-8000}"

# Iniciar o servidor
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level ${LOG_LEVEL:-info} 