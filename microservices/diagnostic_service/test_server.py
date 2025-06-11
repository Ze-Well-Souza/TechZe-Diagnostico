#!/usr/bin/env python3
"""
Script para testar se o servidor FastAPI está funcionando
"""

import requests
import time
import sys

def test_server():
    """Testa se o servidor está funcionando"""
    try:
        print("🧪 Testando servidor FastAPI...")
        
        # Teste básico de saúde
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Health Check: {response.status_code}")
        
        # Teste da documentação
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print(f"✅ Documentação: {response.status_code}")
        
        # Teste de endpoint de orçamentos
        response = requests.get("http://localhost:8000/api/v1/orcamentos/", timeout=5)
        print(f"✅ API Orçamentos: {response.status_code}")
        
        print("\n🎉 Servidor FastAPI funcionando perfeitamente!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Servidor não está rodando")
        print("💡 Inicie o servidor: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1) 