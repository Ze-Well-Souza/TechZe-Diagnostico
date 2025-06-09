#!/usr/bin/env python3
"""
Script de debug para verificar a inicialização da aplicação
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

print("🔍 Iniciando debug da aplicação...")

# Teste 1: Verificar importações v3
print("\n📦 Testando importações v3...")
try:
    from app.api.v3 import ai_endpoints, automation_endpoints, analytics_endpoints, chat_endpoints
    from app.api.v3 import performance_endpoints
    print("✅ Importações v3 bem-sucedidas")
except ImportError as e:
    print(f"❌ Erro de importação v3: {e}")
    sys.exit(1)

# Teste 2: Verificar se os routers têm as rotas corretas
print("\n🛣️ Verificando rotas do performance_endpoints...")
try:
    routes = []
    for route in performance_endpoints.router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            routes.append(f"{list(route.methods)} {route.path}")
    print(f"Rotas encontradas no performance_endpoints: {routes}")
except Exception as e:
    print(f"❌ Erro ao verificar rotas: {e}")

# Teste 3: Simular a criação da app como no main.py
print("\n🚀 Simulando criação da aplicação...")
try:
    from fastapi import FastAPI
    from app.core.config import settings
    
    # Criar app básica
    app = FastAPI(
        title="TechZe Diagnostic Service",
        description="Serviço de diagnóstico técnico avançado",
        version="3.0.0"
    )
    
    # Incluir routers v3
    app.include_router(performance_endpoints.router, prefix="/api/v3")
    
    # Verificar rotas da app
    print("\n📊 Rotas da aplicação após incluir performance_endpoints:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"  {list(route.methods)} {route.path}")
    
    print("\n✅ Aplicação criada com sucesso!")
    
except Exception as e:
    print(f"❌ Erro ao criar aplicação: {e}")
    import traceback
    traceback.print_exc()