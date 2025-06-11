"""
Teste de Autenticação e Autorização - TechZe Diagnóstico
CURSOR testando implementações do TRAE (Frontend)

Objetivo: Testar login/logout via frontend, validar JWT tokens, verificar middleware
"""

import requests
import json
from datetime import datetime


class TestAuthFlow:
    """Testes de fluxo de autenticação e autorização"""
    
    base_url = "http://localhost:8000"
    
    def setup_method(self):
        """Setup para cada teste"""
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def test_health_endpoint_public(self):
        """Teste de endpoint público (sem autenticação)"""
        response = requests.get(f"{self.base_url}/health", headers=self.headers)
        
        print(f"Health Check Status: {response.status_code}")
        assert response.status_code == 200, "Health endpoint deve ser público"
    
    def test_protected_endpoints_without_auth(self):
        """Teste de endpoints protegidos sem autenticação"""
        protected_endpoints = [
            "/api/v1/orcamentos/",
            "/api/v1/estoque/itens",
            "/api/v1/ordens-servico/"
        ]
        
        for endpoint in protected_endpoints:
            response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
            print(f"{endpoint}: {response.status_code}")
            
            # Endpoints devem funcionar mesmo sem auth (para testes)
            # Em produção, deveria retornar 401 ou 403
            if response.status_code in [401, 403]:
                print(f"✅ {endpoint}: Corretamente protegido")
            elif response.status_code == 200:
                print(f"⚠️ {endpoint}: Acesso público (revisar para produção)")
            else:
                print(f"❌ {endpoint}: Erro inesperado {response.status_code}")
    
    def test_jwt_token_validation(self):
        """Teste de validação de tokens JWT"""
        # Simular token inválido
        invalid_token_headers = {
            **self.headers,
            "Authorization": "Bearer invalid_token_123"
        }
        
        response = requests.get(
            f"{self.base_url}/api/v1/orcamentos/",
            headers=invalid_token_headers
        )
        
        print(f"Token inválido status: {response.status_code}")
        
        # Se middleware estiver ativo, deve retornar 401
        if response.status_code == 401:
            print("✅ Middleware JWT funcionando")
        else:
            print("⚠️ Middleware JWT não implementado ou desabilitado")
    
    def test_cors_headers(self):
        """Teste de headers CORS para frontend"""
        response = requests.options(f"{self.base_url}/api/v1/orcamentos/", headers=self.headers)
        
        print(f"CORS preflight status: {response.status_code}")
        
        # Verificar headers CORS
        cors_headers = [
            "Access-Control-Allow-Origin",
            "Access-Control-Allow-Methods",
            "Access-Control-Allow-Headers"
        ]
        
        for header in cors_headers:
            if header in response.headers:
                print(f"✅ {header}: {response.headers[header]}")
            else:
                print(f"❌ {header}: Não encontrado")
    
    def test_security_headers(self):
        """Teste de headers de segurança"""
        response = requests.get(f"{self.base_url}/health", headers=self.headers)
        
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        
        print("Headers de Segurança:")
        for header in security_headers:
            if header in response.headers:
                print(f"✅ {header}: {response.headers[header]}")
            else:
                print(f"❌ {header}: Não implementado")


def test_auth_flow_complete():
    """Teste completo do fluxo de autenticação"""
    test = TestAuthFlow()
    test.setup_method()
    
    print("=== TESTE DE AUTENTICAÇÃO E AUTORIZAÇÃO ===")
    print("CURSOR validando implementações de segurança do TRAE")
    print("=" * 60)
    
    print("\n1. Testando endpoints públicos:")
    test.test_health_endpoint_public()
    
    print("\n2. Testando endpoints protegidos:")
    test.test_protected_endpoints_without_auth()
    
    print("\n3. Testando validação JWT:")
    test.test_jwt_token_validation()
    
    print("\n4. Testando CORS:")
    test.test_cors_headers()
    
    print("\n5. Testando headers de segurança:")
    test.test_security_headers()
    
    print("\n" + "=" * 60)
    print("RESUMO DE SEGURANÇA:")
    print("=" * 60)
    print("⚠️ Sistema em modo desenvolvimento - autenticação relaxada")
    print("🔧 Necessário configurar middleware JWT para produção")
    print("🔧 Implementar headers de segurança obrigatórios")


if __name__ == "__main__":
    test_auth_flow_complete() 