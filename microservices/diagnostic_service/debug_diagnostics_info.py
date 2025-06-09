#!/usr/bin/env python3
"""Script para debugar o problema com /api/core/diagnostics/info"""

from fastapi.testclient import TestClient
from app.main import app
import json

def test_endpoints():
    """Testa vários endpoints para identificar o problema"""
    client = TestClient(app)
    
    endpoints_to_test = [
        "/api/core/info",
        "/api/core/auth/info",
        "/api/core/auth/health", 
        "/api/core/diagnostics/health",
        "/api/core/diagnostics/info",
        "/api/core/ai/info",
        "/api/core/performance/info"
    ]
    
    print("=== TESTE DE ENDPOINTS ===")
    for endpoint in endpoints_to_test:
        try:
            response = client.get(endpoint)
            print(f"{endpoint:<35} | Status: {response.status_code}")
            if response.status_code != 200:
                print(f"  Error: {response.text[:100]}")
            print()
        except Exception as e:
            print(f"{endpoint:<35} | ERRO: {e}")
            print()

def debug_routes():
    """Lista todas as rotas do app"""
    print("=== ROTAS REGISTRADAS ===")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            if '/api/core/' in route.path:
                print(f"{list(route.methods)} {route.path}")
    print()

def debug_router_details():
    """Debug detalhado do router"""
    from app.api.core.router import api_router
    print("=== DETALHES DO ROUTER API CORE ===")
    for route in api_router.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"{list(route.methods)} {route.path}")
    print()

if __name__ == "__main__":
    debug_routes()
    debug_router_details()
    test_endpoints() 