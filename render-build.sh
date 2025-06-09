#!/bin/bash

# Script de build personalizado para Render
echo "🚀 Iniciando build do TechZe Diagnostico..."

# Instalar dependências
echo "📦 Instalando dependências..."
npm install

# Dar permissão de execução ao vite
echo "🔧 Configurando permissões..."
chmod +x node_modules/.bin/vite
chmod +x node_modules/vite/bin/vite.js

# Executar build usando npx para garantir permissões
echo "🏗️ Executando build..."
npx vite build

echo "✅ Build concluído com sucesso!" 