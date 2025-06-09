#!/usr/bin/env python3
"""Teste direto dos endpoints para debugar o problema 401 no diagnostics"""

from fastapi.testclient import TestClient
from app.main import app
import traceback

def test_direct_functions():
    """Testa as funções diretamente"""
    print("=== TESTE DIRETO DAS FUNÇÕES ===")
    
    try:
        # Importar e testar função diretamente
        from app.api.core.diagnostics.endpoints import diagnostics_info, diagnostics_health_check
        
        print("✅ Import funcionou")
        
        # Testar função info diretamente
        result_info = diagnostics_info()
        print(f"Info direto: {result_info}")
        
        # Testar função health diretamente  
        result_health = diagnostics_health_check()
        print(f"Health direto: {result_health}")
        
    except Exception as e:
        print(f"❌ Erro no teste direto: {e}")
        traceback.print_exc()

def test_with_client():
    """Testa com TestClient"""
    print("\n=== TESTE COM TESTCLIENT ===")
    
    client = TestClient(app)
    
    # Testar outros endpoints que funcionam
    print("🧪 Testando endpoints que funcionam:")
    
    response = client.get("/api/core/auth/info")
    print(f"AUTH INFO: {response.status_code}")
    
    response = client.get("/api/core/ai/info") 
    print(f"AI INFO: {response.status_code}")
    
    # Testar diagnostics
    print("\n🧪 Testando diagnostics:")
    
    response = client.get("/api/core/diagnostics/info")
    print(f"DIAGNOSTICS INFO: {response.status_code}")
    if response.status_code != 200:
        print(f"  Response: {response.text[:200]}")
    
    response = client.get("/api/core/diagnostics/health")
    print(f"DIAGNOSTICS HEALTH: {response.status_code}")
    if response.status_code != 200:
        print(f"  Response: {response.text[:200]}")

def test_router_isolation():
    """Testa router isolado"""
    print("\n=== TESTE ROUTER ISOLADO ===")
    
    try:
        from app.api.core.diagnostics.endpoints import router
        from fastapi import FastAPI
        
        # Criar app isolada só com o router diagnostics
        isolated_app = FastAPI()
        isolated_app.include_router(router, prefix="/diagnostics")
        
        isolated_client = TestClient(isolated_app)
        
        response = isolated_client.get("/diagnostics/info")
        print(f"ISOLATED INFO: {response.status_code}")
        
        response = isolated_client.get("/diagnostics/health")
        print(f"ISOLATED HEALTH: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Erro no teste isolado: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_functions()
    test_with_client()
    test_router_isolation() 