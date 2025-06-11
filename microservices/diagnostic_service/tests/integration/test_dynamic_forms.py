"""
Teste de Formulários Dinâmicos - TechZe Diagnóstico
CURSOR testando implementações do TRAE (Frontend)

Objetivo: Testar DynamicForm.tsx, validar 19 tipos de campo, verificar validação brasileira
"""

import requests
import re
from datetime import datetime


class TestDynamicForms:
    """Testes de formulários dinâmicos e validações"""
    
    base_url = "http://localhost:8000"
    
    def setup_method(self):
        """Setup para cada teste"""
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def test_cpf_validation(self):
        """Teste de validação de CPF brasileiro"""
        print("=== TESTE DE VALIDAÇÃO CPF ===")
        
        cpf_cases = [
            ("12345678901", False, "CPF inválido"),
            ("11111111111", False, "CPF com dígitos repetidos"),
            ("123.456.789-01", False, "CPF inválido com formatação"),
            ("000.000.000-00", False, "CPF zeros"),
            ("111.444.777-35", True, "CPF válido"),  # CPF válido de exemplo
        ]
        
        for cpf, is_valid, description in cpf_cases:
            payload = {
                "cliente": {
                    "nome": "Teste CPF",
                    "cpf": cpf,
                    "telefone": "11999999999",
                    "email": "test@test.com"
                },
                "equipamento": {
                    "tipo": "smartphone",
                    "problema_relatado": "Teste CPF"
                }
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/orcamentos/",
                    json=payload,
                    headers=self.headers
                )
                
                print(f"CPF {cpf}: Status {response.status_code} - {description}")
                
                if not is_valid and response.status_code == 422:
                    print(f"  ✅ CPF inválido rejeitado corretamente")
                elif is_valid and response.status_code in [200, 201]:
                    print(f"  ✅ CPF válido aceito")
                elif not is_valid and response.status_code in [200, 201]:
                    print(f"  ❌ FALHA: CPF inválido foi aceito")
                else:
                    print(f"  ⚠️ Resposta inesperada: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Erro no teste: {e}")
    
    def test_cnpj_validation(self):
        """Teste de validação de CNPJ brasileiro"""
        print("\n=== TESTE DE VALIDAÇÃO CNPJ ===")
        
        cnpj_cases = [
            ("12345678000101", False, "CNPJ inválido"),
            ("11.111.111/0001-11", False, "CNPJ com dígitos repetidos"),
            ("11.222.333/0001-81", True, "CNPJ válido"),  # CNPJ válido de exemplo
        ]
        
        for cnpj, is_valid, description in cnpj_cases:
            payload = {
                "cliente": {
                    "nome": "Teste CNPJ",
                    "cnpj": cnpj,
                    "telefone": "11999999999",
                    "email": "test@test.com"
                },
                "equipamento": {
                    "tipo": "smartphone", 
                    "problema_relatado": "Teste CNPJ"
                }
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/orcamentos/",
                    json=payload,
                    headers=self.headers
                )
                
                print(f"CNPJ {cnpj}: Status {response.status_code} - {description}")
                
            except Exception as e:
                print(f"  ❌ Erro no teste: {e}")
    
    def test_cep_validation(self):
        """Teste de validação de CEP brasileiro"""
        print("\n=== TESTE DE VALIDAÇÃO CEP ===")
        
        cep_cases = [
            ("01234567", False, "CEP sem formatação"),
            ("01234-567", True, "CEP válido com formatação"),
            ("00000-000", False, "CEP zeros"),
            ("99999-999", True, "CEP válido"),
        ]
        
        for cep, is_valid, description in cep_cases:
            payload = {
                "cliente": {
                    "nome": "Teste CEP",
                    "telefone": "11999999999",
                    "email": "test@test.com",
                    "endereco": f"Rua Teste, 123, {cep}"
                },
                "equipamento": {
                    "tipo": "smartphone",
                    "problema_relatado": "Teste CEP"
                }
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/orcamentos/",
                    json=payload,
                    headers=self.headers
                )
                
                print(f"CEP {cep}: Status {response.status_code} - {description}")
                
            except Exception as e:
                print(f"  ❌ Erro no teste: {e}")
    
    def test_phone_validation(self):
        """Teste de validação de telefone brasileiro"""
        print("\n=== TESTE DE VALIDAÇÃO TELEFONE ===")
        
        phone_cases = [
            ("11999999999", True, "Celular SP válido"),
            ("(11) 99999-9999", True, "Celular formatado"),
            ("1133334444", True, "Fixo SP válido"),
            ("(11) 3333-4444", True, "Fixo formatado"),
            ("999999999", False, "Telefone incompleto"),
            ("12345", False, "Muito curto"),
        ]
        
        for phone, is_valid, description in phone_cases:
            payload = {
                "cliente": {
                    "nome": "Teste Telefone",
                    "telefone": phone,
                    "email": "test@test.com"
                },
                "equipamento": {
                    "tipo": "smartphone",
                    "problema_relatado": "Teste telefone"
                }
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/orcamentos/",
                    json=payload,
                    headers=self.headers
                )
                
                print(f"Tel {phone}: Status {response.status_code} - {description}")
                
            except Exception as e:
                print(f"  ❌ Erro no teste: {e}")
    
    def test_form_field_types(self):
        """Teste dos 19 tipos de campo do DynamicForm"""
        print("\n=== TESTE DOS 19 TIPOS DE CAMPO ===")
        
        field_types = [
            "text", "email", "password", "number", "tel", "url", "date", 
            "datetime-local", "time", "search", "color", "range",
            "textarea", "select", "checkbox", "radio", "file",
            "cpf", "cnpj"  # Campos brasileiros específicos
        ]
        
        print(f"Tipos de campo esperados no DynamicForm.tsx: {len(field_types)}")
        
        for field_type in field_types:
            print(f"  📋 {field_type}: Deve ser suportado pelo TRAE")
        
        print("\n⚠️ Não é possível testar os tipos diretamente via API")
        print("🔧 Teste deve ser feito na interface React do TRAE")
    
    def test_form_wizard_flow(self):
        """Teste de formulário em etapas (wizard)"""
        print("\n=== TESTE DE FORM WIZARD ===")
        
        # Simular criação de orçamento em etapas
        wizard_data = {
            "step1": {"cliente_info": "Dados básicos"},
            "step2": {"equipamento_info": "Informações do dispositivo"},
            "step3": {"problema_info": "Descrição do problema"},
            "step4": {"servicos_info": "Serviços solicitados"},
            "step5": {"aprovacao_info": "Confirmação final"}
        }
        
        print(f"Etapas do wizard esperadas: {len(wizard_data)}")
        
        for step, data in wizard_data.items():
            print(f"  📋 {step}: {data}")
        
        print("\n⚠️ FormWizard.tsx deve implementar navegação entre etapas")
        print("🔧 Validação por etapa deve ser funcional")


def test_dynamic_forms_complete():
    """Teste completo de formulários dinâmicos"""
    test = TestDynamicForms()
    test.setup_method()
    
    print("=== TESTE COMPLETO DE FORMULÁRIOS DINÂMICOS ===")
    print("CURSOR validando DynamicForm.tsx e FormWizard.tsx do TRAE")
    print("=" * 70)
    
    # Aguardar servidor
    import time
    time.sleep(3)
    
    test.test_cpf_validation()
    test.test_cnpj_validation()  
    test.test_cep_validation()
    test.test_phone_validation()
    test.test_form_field_types()
    test.test_form_wizard_flow()
    
    print("\n" + "=" * 70)
    print("RESUMO DE FORMULÁRIOS DINÂMICOS:")
    print("=" * 70)
    print("⚠️ Validações brasileiras devem ser implementadas no frontend")
    print("🔧 DynamicForm.tsx deve suportar 19 tipos de campo")
    print("🔧 FormWizard.tsx deve permitir navegação por etapas")
    print("🔧 Validação em tempo real deve funcionar")


if __name__ == "__main__":
    test_dynamic_forms_complete() 