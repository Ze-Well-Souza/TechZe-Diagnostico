#!/usr/bin/env python3
"""
Script de validação completa do sistema TechZe
"""

import requests
import json
import time
import subprocess
import os
from pathlib import Path
from datetime import datetime

# Configurações
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8081"
SUPABASE_URL = "https://pkefwvvkydzzfstzwppv.supabase.co"
SUPABASE_SERVICE_ROLE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBrZWZ3dnZreWR6emZzdHp3cHB2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzM0MjY3NSwiZXhwIjoyMDYyOTE4Njc1fQ.x9lc7-x9Aj0bB0WOZQ4b_buEwftPgCuGirvxjn_S6m8"

class SystemValidator:
    def __init__(self):
        self.results = {}
        self.start_time = datetime.now()
    
    def print_header(self, title):
        """Imprime cabeçalho formatado"""
        print("\n" + "="*70)
        print(f"🔍 {title}")
        print("="*70)
    
    def print_step(self, step):
        """Imprime passo formatado"""
        print(f"\n📋 {step}")
        print("-" * 50)
    
    def print_result(self, test_name, success, details=""):
        """Registra resultado de um teste"""
        self.results[test_name] = success
        status = "✅ PASSOU" if success else "❌ FALHOU"
        print(f"   {test_name}: {status}")
        if details:
            print(f"      {details}")
    
    def test_backend_health(self):
        """Testa saúde do backend"""
        self.print_step("TESTANDO BACKEND")
        
        try:
            response = requests.get(f"{BACKEND_URL}/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.print_result("Backend Health", True, f"Status: {data.get('status')}")
                
                # Verificar features
                features = data.get('features', {})
                for feature, status in features.items():
                    self.print_result(f"Backend Feature: {feature}", status)
                
                return True
            else:
                self.print_result("Backend Health", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Backend Health", False, f"Erro: {str(e)}")
            return False
    
    def test_backend_endpoints(self):
        """Testa endpoints específicos do backend"""
        self.print_step("TESTANDO ENDPOINTS DA API")
        
        endpoints = [
            ("GET", "/", "Root Endpoint"),
            ("GET", "/info", "Service Info"),
            ("POST", "/api/v1/diagnostic/quick", "Quick Diagnostic"),
        ]
        
        all_passed = True
        
        for method, endpoint, name in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=10)
                else:
                    response = requests.post(f"{BACKEND_URL}{endpoint}", timeout=15)
                
                success = response.status_code == 200
                self.print_result(name, success, f"Status: {response.status_code}")
                
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.print_result(name, False, f"Erro: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_cors(self):
        """Testa configuração de CORS"""
        self.print_step("TESTANDO CORS")
        
        try:
            # Teste de preflight
            headers = {
                'Origin': FRONTEND_URL,
                'Access-Control-Request-Method': 'GET',
                'Access-Control-Request-Headers': 'Content-Type'
            }
            
            response = requests.options(f"{BACKEND_URL}/health", headers=headers, timeout=5)
            
            if response.status_code in [200, 204]:
                cors_origin = response.headers.get('Access-Control-Allow-Origin', '')
                cors_methods = response.headers.get('Access-Control-Allow-Methods', '')
                
                cors_ok = bool(cors_origin and cors_methods)
                self.print_result("CORS Preflight", cors_ok, f"Origin: {cors_origin}")
                
                # Teste de requisição real
                response = requests.get(f"{BACKEND_URL}/health", headers={'Origin': FRONTEND_URL}, timeout=5)
                real_cors_ok = response.status_code == 200
                self.print_result("CORS Real Request", real_cors_ok)
                
                return cors_ok and real_cors_ok
            else:
                self.print_result("CORS Preflight", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("CORS Test", False, f"Erro: {str(e)}")
            return False
    
    def test_frontend(self):
        """Testa frontend"""
        self.print_step("TESTANDO FRONTEND")
        
        try:
            response = requests.get(FRONTEND_URL, timeout=5)
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                is_html = 'text/html' in content_type
                
                self.print_result("Frontend Access", True, f"Content-Type: {content_type}")
                self.print_result("Frontend HTML", is_html)
                
                return is_html
            else:
                self.print_result("Frontend Access", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Frontend Access", False, f"Erro: {str(e)}")
            return False
    
    def test_supabase_connection(self):
        """Testa conexão com Supabase"""
        self.print_step("TESTANDO SUPABASE")
        
        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json"
        }
        
        try:
            # Teste de conexão básica
            response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers, timeout=10)
            
            if response.status_code == 200:
                self.print_result("Supabase Connection", True)
                
                # Testar tabelas
                tables = ['users', 'devices', 'diagnostics', 'reports']
                tables_ok = 0
                
                for table in tables:
                    try:
                        table_response = requests.get(
                            f"{SUPABASE_URL}/rest/v1/{table}?limit=1", 
                            headers=headers, 
                            timeout=5
                        )
                        
                        # 200 = tabela existe, 401 = RLS ativo (esperado)
                        table_exists = table_response.status_code in [200, 401]
                        self.print_result(f"Supabase Table: {table}", table_exists)
                        
                        if table_exists:
                            tables_ok += 1
                            
                    except Exception as e:
                        self.print_result(f"Supabase Table: {table}", False, f"Erro: {str(e)}")
                
                return tables_ok >= 2  # Pelo menos 2 tabelas devem existir
            else:
                self.print_result("Supabase Connection", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Supabase Connection", False, f"Erro: {str(e)}")
            return False
    
    def test_file_structure(self):
        """Verifica estrutura de arquivos"""
        self.print_step("VERIFICANDO ESTRUTURA DE ARQUIVOS")
        
        critical_files = [
            "microservices/diagnostic_service/app/main.py",
            "frontend-v3/package.json",
            "frontend-v3/src/hooks/useDiagnostics.ts",
            "frontend-v3/src/services/diagnosticApiService.ts",
            "frontend-v3/src/types/diagnostic.ts",
        ]
        
        all_exist = True
        
        for file_path in critical_files:
            exists = Path(file_path).exists()
            self.print_result(f"File: {file_path}", exists)
            if not exists:
                all_exist = False
        
        return all_exist
    
    def test_integration(self):
        """Testa integração completa"""
        self.print_step("TESTANDO INTEGRAÇÃO COMPLETA")
        
        try:
            # Simular fluxo completo: Frontend -> Backend -> Supabase
            
            # 1. Testar endpoint de diagnóstico
            response = requests.post(f"{BACKEND_URL}/api/v1/diagnostic/quick", timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                has_health_score = 'health_score' in data
                has_results = 'results' in data
                
                self.print_result("Integration: Diagnostic API", True)
                self.print_result("Integration: Health Score", has_health_score)
                self.print_result("Integration: Results Data", has_results)
                
                return has_health_score and has_results
            else:
                self.print_result("Integration: Diagnostic API", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("Integration Test", False, f"Erro: {str(e)}")
            return False
    
    def generate_report(self):
        """Gera relatório final"""
        self.print_header("RELATÓRIO DE VALIDAÇÃO")
        
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"📊 ESTATÍSTICAS GERAIS:")
        print(f"   Duração da Validação: {duration:.1f} segundos")
        print(f"   Total de Testes: {total_tests}")
        print(f"   Testes Aprovados: {passed_tests}")
        print(f"   Testes Falharam: {failed_tests}")
        print(f"   Taxa de Sucesso: {success_rate:.1f}%")
        
        print(f"\n📋 DETALHES DOS TESTES:")
        for test_name, result in self.results.items():
            status = "✅" if result else "❌"
            print(f"   {status} {test_name}")
        
        # Classificação do sistema
        if success_rate >= 90:
            classification = "🟢 EXCELENTE"
            message = "Sistema funcionando perfeitamente!"
        elif success_rate >= 75:
            classification = "🟡 BOM"
            message = "Sistema funcionando bem com pequenos problemas."
        elif success_rate >= 50:
            classification = "🟠 REGULAR"
            message = "Sistema funcionando mas precisa de atenção."
        else:
            classification = "🔴 CRÍTICO"
            message = "Sistema com problemas sérios que precisam ser corrigidos."
        
        print(f"\n🎯 CLASSIFICAÇÃO DO SISTEMA: {classification}")
        print(f"   {message}")
        
        # Recomendações
        print(f"\n💡 RECOMENDAÇÕES:")
        
        if failed_tests == 0:
            print("   🎉 Parabéns! Todos os testes passaram.")
            print("   Sistema pronto para uso em produção.")
        else:
            print("   🔧 Problemas encontrados que precisam ser corrigidos:")
            
            failed_categories = {
                'Backend': [name for name in self.results if 'Backend' in name and not self.results[name]],
                'Frontend': [name for name in self.results if 'Frontend' in name and not self.results[name]],
                'CORS': [name for name in self.results if 'CORS' in name and not self.results[name]],
                'Supabase': [name for name in self.results if 'Supabase' in name and not self.results[name]],
                'Integration': [name for name in self.results if 'Integration' in name and not self.results[name]],
            }
            
            for category, failed_tests_list in failed_categories.items():
                if failed_tests_list:
                    print(f"      {category}: {len(failed_tests_list)} problema(s)")
        
        # Próximos passos
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        
        if success_rate >= 90:
            print("   1. Sistema validado com sucesso!")
            print("   2. Execute testes de carga se necessário")
            print("   3. Configure monitoramento para produção")
        elif success_rate >= 75:
            print("   1. Corrija os problemas menores identificados")
            print("   2. Execute nova validação")
            print("   3. Sistema quase pronto para produção")
        else:
            print("   1. Execute 'python fix_critical_issues.py'")
            print("   2. Siga as instruções de correção")
            print("   3. Execute nova validação")
        
        # Salvar relatório
        report_data = {
            "timestamp": end_time.isoformat(),
            "duration_seconds": duration,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": success_rate,
            "classification": classification,
            "results": self.results
        }
        
        try:
            with open('validation_report.json', 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Relatório salvo em: validation_report.json")
            
        except Exception as e:
            print(f"\n⚠️ Erro ao salvar relatório: {str(e)}")
    
    def run_validation(self):
        """Executa validação completa"""
        self.print_header("VALIDAÇÃO COMPLETA DO SISTEMA TECHZE")
        
        print(f"🕐 Iniciado em: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Executar todos os testes
        self.test_file_structure()
        self.test_backend_health()
        self.test_backend_endpoints()
        self.test_cors()
        self.test_frontend()
        self.test_supabase_connection()
        self.test_integration()
        
        # Gerar relatório
        self.generate_report()

def main():
    """Função principal"""
    validator = SystemValidator()
    validator.run_validation()

if __name__ == "__main__":
    main()