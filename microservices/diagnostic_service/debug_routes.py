#!/usr/bin/env python
"""
Debug das rotas da API Core
"""

from fastapi.testclient import TestClient
from app.main import app

def debug_routes():
    """Debug das rotas registradas"""
    client = TestClient(app)
    
    print("=== DEBUG DE ROTAS ===")
    
    # Listar todas as rotas registradas
    print("\n🔍 Rotas registradas:")
    for route in app.routes:
        if hasattr(route, 'path'):
            print(f"   {route.path} - {getattr(route, 'methods', 'N/A')}")
    
    print("\n🧪 Testando endpoints específicos:")
    
    # Testar endpoints específicos
    endpoints_to_test = [
        "/api/core/info",
        "/api/core/performance/info",
        "/api/core/performance/health",
        "/api/core/auth/info",
        "/api/core/auth/health"
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = client.get(endpoint)
            print(f"   📍 {endpoint}: {response.status_code}")
            if response.status_code != 200:
                print(f"     ❌ Error: {response.text[:100]}")
        except Exception as e:
            print(f"   ❌ {endpoint}: Exception - {e}")

if __name__ == "__main__":
    debug_routes() 