#!/usr/bin/env python3
"""Teste de importação isolada para debugar quando o erro acontece"""

import logging

# Configurar logging para capturar tudo
logging.basicConfig(level=logging.DEBUG)

print("=== INICIANDO TESTE DE IMPORTAÇÃO ISOLADA ===")

print("1. Importando TestClient...")
from fastapi.testclient import TestClient

print("2. Importando FastAPI...")
from fastapi import FastAPI

print("3. Tentando importar router diagnostics diretamente...")
try:
    from app.api.core.diagnostics.endpoints import router as diagnostics_router
    print("✅ Import do diagnostics_router SUCESSO")
except Exception as e:
    print(f"❌ ERRO no import: {e}")
    import traceback
    traceback.print_exc()

print("4. Criando app limpa...")
clean_app = FastAPI()

print("5. Adicionando apenas o router diagnostics...")
clean_app.include_router(diagnostics_router, prefix="/test")

print("6. Criando client...")
client = TestClient(clean_app)

print("7. Testando endpoint...")
response = client.get("/test/info")
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:100]}")

print("=== FIM DO TESTE ===") 