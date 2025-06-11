"""
Teste de Integração Frontend-Backend - TechZe Diagnóstico
CURSOR testando implementações do TRAE (Frontend)

Objetivo: Verificar se todas as chamadas do frontend chegam corretamente ao backend
"""

import pytest
import requests
import json
from datetime import datetime
import uuid


class TestFrontendApiCalls:
    """Testes de validação de chamadas de API do frontend"""
    
    base_url = "http://localhost:8000"
    
    def setup_method(self):
        """Setup para cada teste"""
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def test_orcamentos_frontend_integration(self):
        """Teste de integração do módulo Orçamentos do frontend"""
        # Simulação de payload enviado pelo frontend TRAE
        frontend_payload = {
            "cliente": {
                "nome": "Cliente Frontend Test",
                "telefone": "11999887766",
                "email": "frontend@test.com"
            },
            "equipamento": {
                "tipo": "smartphone",
                "marca": "Samsung",
                "modelo": "Galaxy S21",
                "problema_relatado": "Tela quebrada"
            },
            "servicos": [
                {
                    "descricao": "Troca de tela",
                    "tipo": "reparo_hardware",
                    "valor_unitario": 250.00
                }
            ]
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/orcamentos/",
            json=frontend_payload,
            headers=self.headers
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code != 201:
            print(f"Erro: {response.text}")
            
        # Validação de incompatibilidade identificada
        if response.status_code == 422:
            pytest.fail("INCOMPATIBILIDADE: Frontend enviando payload que backend rejeita")
        elif response.status_code == 500:
            pytest.fail("ERRO CRÍTICO: Endpoint com erro 500")
        
        assert response.status_code == 201, f"Frontend-Backend integration falhou: {response.status_code}"
    
    def test_estoque_frontend_integration(self):
        """Teste de integração do módulo Estoque do frontend"""
        # Teste de listagem de itens
        response = requests.get(
            f"{self.base_url}/api/v1/estoque/itens",
            headers=self.headers
        )
        
        print(f"Estoque Status: {response.status_code}")
        if response.status_code == 500:
            pytest.fail("FALHA CRÍTICA: Endpoint de estoque com erro 500")
        
        assert response.status_code == 200, f"Estoque frontend integration falhou: {response.status_code}"
    
    def test_ordem_servico_frontend_integration(self):
        """Teste de integração do módulo Ordem de Serviço do frontend"""
        response = requests.get(
            f"{self.base_url}/api/v1/ordens-servico/",
            headers=self.headers
        )
        
        print(f"OS Status: {response.status_code}")
        if response.status_code == 500:
            pytest.fail("FALHA CRÍTICA: Endpoint de OS com erro 500")
        
        assert response.status_code == 200, f"OS frontend integration falhou: {response.status_code}"
    
    def test_frontend_payload_validation(self):
        """Teste de validação de payloads enviados pelo frontend"""
        # Teste com payload típico do frontend TRAE
        invalid_payload = {
            "cliente": {
                "nome": "Test",
                "telefone": "123",
                "endereco": {  # Frontend envia objeto, backend espera string
                    "rua": "Rua teste",
                    "numero": "123"
                }
            },
            "equipamento": {
                "tipo": "tela",  # Enum inválido
                "problema_relatado": "Teste"
            },
            "pecas": [
                {
                    "codigo_peca": "ABC123",  # Frontend usa codigo_peca, backend espera codigo
                    "nome_peca": "Tela LCD"   # Frontend usa nome_peca, backend espera nome
                }
            ]
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/orcamentos/",
            json=invalid_payload,
            headers=self.headers
        )
        
        # Documentar incompatibilidades encontradas
        if response.status_code == 422:
            error_details = response.json()
            print(f"INCOMPATIBILIDADES IDENTIFICADAS: {error_details}")
        
        # Este teste DEVE falhar para demonstrar problemas de integração
        assert response.status_code != 201, "Payload inválido foi aceito - problema de validação"
    
    def test_frontend_performance_check(self):
        """Teste de performance das chamadas do frontend"""
        start_time = datetime.now()
        
        response = requests.get(
            f"{self.base_url}/api/v1/orcamentos/",
            headers=self.headers
        )
        
        end_time = datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        
        print(f"Response time: {response_time:.0f}ms")
        
        # Meta: < 500ms
        if response_time > 500:
            pytest.fail(f"PERFORMANCE CRÍTICA: {response_time:.0f}ms > 500ms")
        
        assert response.status_code == 200
        assert response_time < 500, f"Performance inaceitável: {response_time:.0f}ms"


if __name__ == "__main__":
    # Execução direta para debugging
    test = TestFrontendApiCalls()
    test.setup_method()
    
    print("=== TESTE DE INTEGRAÇÃO FRONTEND-BACKEND ===")
    try:
        test.test_orcamentos_frontend_integration()
        print("✅ Orçamentos: OK")
    except Exception as e:
        print(f"❌ Orçamentos: {e}")
    
    try:
        test.test_estoque_frontend_integration()
        print("✅ Estoque: OK") 
    except Exception as e:
        print(f"❌ Estoque: {e}")
    
    try:
        test.test_ordem_servico_frontend_integration()
        print("✅ OS: OK")
    except Exception as e:
        print(f"❌ OS: {e}") 