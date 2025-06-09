#!/usr/bin/env python3
"""
Script para verificar as rotas disponíveis na aplicação FastAPI
"""

import logging
logging.basicConfig(level=logging.INFO)

try:
    from app.main import app
    print("✅ App importado com sucesso")
    
    # Verificar rotas
    routes = [route for route in app.routes if hasattr(route, 'path')]
    print(f"\n📊 Total de rotas encontradas: {len(routes)}")
    
    print("\n🛣️ Rotas disponíveis:")
    for route in routes:
        methods = getattr(route, 'methods', {'N/A'})
        path = route.path
        print(f"  {methods} {path}")
        
    # Verificar especificamente as rotas que os testes estão procurando
    test_routes = ["/health", "/api/v3/performance/stats", "/api/v3/performance/health"]
    print("\n🔍 Verificando rotas dos testes:")
    available_paths = [route.path for route in routes]
    
    for test_route in test_routes:
        if test_route in available_paths:
            print(f"  ✅ {test_route} - ENCONTRADA")
        else:
            print(f"  ❌ {test_route} - NÃO ENCONTRADA")
            
except Exception as e:
    print(f"❌ Erro ao importar app: {e}")
    import traceback
    traceback.print_exc()