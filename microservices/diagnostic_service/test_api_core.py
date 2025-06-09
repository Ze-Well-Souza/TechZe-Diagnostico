#!/usr/bin/env python
"""
Script temporário para testar a API Core
"""

from fastapi.testclient import TestClient
from app.main import app

def test_api_core():
    """Testa a API Core"""
    client = TestClient(app)
    
    print("=== Testando API Core ===")
    
    # Teste 1: Endpoint info da API Core
    try:
        response = client.get('/api/core/info')
        print(f'📍 /api/core/info: Status {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Dados: {data}")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f'   ❌ Exception: {e}')
    
    # Teste 2: Health check
    try:
        response = client.get('/health')
        print(f'📍 /health: Status {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
        else:
            print(f"   ❌ Erro: {response.text}")
    except Exception as e:
        print(f'   ❌ Exception: {e}')
    
    # Teste 3: Performance endpoints (que estão falhando nos testes)
    performance_endpoints = [
        '/api/core/performance/stats',
        '/api/core/performance/health',
        '/api/v3/performance/stats'  # Para comparar
    ]
    
    for endpoint in performance_endpoints:
        try:
            response = client.get(endpoint)
            print(f'📍 {endpoint}: Status {response.status_code}')
            if response.status_code == 200:
                print(f"   ✅ Funcionando")
            elif response.status_code == 404:
                print(f"   ❌ Não encontrado")
            else:
                print(f"   ⚠️ Status: {response.status_code}")
        except Exception as e:
            print(f'   ❌ Exception: {e}')
    
    print("\n=== Teste concluído ===")

if __name__ == "__main__":
    test_api_core() 