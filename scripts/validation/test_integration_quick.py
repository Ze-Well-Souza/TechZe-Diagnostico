#!/usr/bin/env python3
"""
Teste de integração rápido para validar a comunicação entre frontend e backend.
Este script verifica se os serviços estão funcionando corretamente.
"""

import requests
import time
import sys
import json
from typing import Dict, Any


class IntegrationTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.results = []

    def test_backend_health(self) -> bool:
        """Testa se o backend está respondendo."""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            success = response.status_code == 200
            self.results.append({
                "test": "Backend Health Check",
                "status": "PASS" if success else "FAIL",
                "details": f"Status: {response.status_code}"
            })
            return success
        except Exception as e:
            self.results.append({
                "test": "Backend Health Check",
                "status": "FAIL",
                "details": f"Error: {str(e)}"
            })
            return False

    def test_frontend_availability(self) -> bool:
        """Testa se o frontend está disponível."""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            success = response.status_code == 200
            self.results.append({
                "test": "Frontend Availability",
                "status": "PASS" if success else "FAIL",
                "details": f"Status: {response.status_code}"
            })
            return success
        except Exception as e:
            self.results.append({
                "test": "Frontend Availability",
                "status": "FAIL",
                "details": f"Error: {str(e)}"
            })
            return False

    def test_api_endpoints(self) -> bool:
        """Testa endpoints básicos da API."""
        endpoints = [
            "/api/diagnostics",
            "/api/auth/status"
        ]
        
        all_passed = True
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                # Aceita 200, 401 (não autenticado) ou 404 (endpoint não implementado)
                success = response.status_code in [200, 401, 404]
                if not success:
                    all_passed = False
                
                self.results.append({
                    "test": f"API Endpoint {endpoint}",
                    "status": "PASS" if success else "FAIL",
                    "details": f"Status: {response.status_code}"
                })
            except Exception as e:
                all_passed = False
                self.results.append({
                    "test": f"API Endpoint {endpoint}",
                    "status": "FAIL",
                    "details": f"Error: {str(e)}"
                })
        
        return all_passed

    def run_tests(self) -> bool:
        """Executa todos os testes de integração."""
        print("🚀 Iniciando testes de integração rápidos...\n")
        
        # Aguarda um pouco para os serviços iniciarem
        print("⏳ Aguardando serviços iniciarem...")
        time.sleep(5)
        
        tests = [
            self.test_backend_health,
            self.test_api_endpoints,
            # Comentado pois o frontend pode não estar rodando em CI
            # self.test_frontend_availability
        ]
        
        all_passed = True
        for test in tests:
            try:
                result = test()
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"❌ Erro durante teste: {e}")
                all_passed = False
        
        return all_passed

    def print_results(self):
        """Imprime os resultados dos testes."""
        print("\n" + "="*50)
        print("📊 RESULTADOS DOS TESTES DE INTEGRAÇÃO")
        print("="*50)
        
        passed = 0
        failed = 0
        
        for result in self.results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
            print(f"   {result['details']}")
            
            if result["status"] == "PASS":
                passed += 1
            else:
                failed += 1
        
        print(f"\n📈 Resumo: {passed} passou(m), {failed} falhou(ram)")
        
        if failed == 0:
            print("🎉 Todos os testes de integração passaram!")
        else:
            print("⚠️  Alguns testes falharam. Verifique os logs acima.")


def main():
    """Função principal."""
    tester = IntegrationTester()
    
    try:
        success = tester.run_tests()
        tester.print_results()
        
        # Retorna código de saída apropriado
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Testes interrompidos pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erro fatal durante os testes: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()