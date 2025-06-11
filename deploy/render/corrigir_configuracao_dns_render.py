#!/usr/bin/env python3
"""
Script para Diagnosticar e Corrigir Configuração DNS + Render
TechZe Diagnóstico - Configuração Completa
"""

import requests
import json
import subprocess
import time
from datetime import datetime
import os

class DNSRenderConfigurator:
    def __init__(self):
        self.render_api_key = "rnd_Tj1JybEJij6A3UhouM7spm8LRbkX"
        self.domain = "techreparo.com"
        self.www_domain = f"www.{self.domain}"
        self.render_headers = {
            "Authorization": f"Bearer {self.render_api_key}",
            "Content-Type": "application/json"
        }
        
    def log(self, message, level="INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def check_dns_current_config(self):
        """Verifica configuração DNS atual"""
        self.log("🔍 Verificando configuração DNS atual...")
        
        dns_results = {
            "domain_root": None,
            "www_subdomain": None,
            "render_target": None
        }
        
        try:
            # Verificar domínio raiz
            result = subprocess.run(['nslookup', self.domain], 
                                  capture_output=True, text=True, timeout=10)
            if "NXDOMAIN" not in result.stdout and "can't find" not in result.stdout:
                dns_results["domain_root"] = "CONFIGURADO"
            else:
                dns_results["domain_root"] = "NÃO CONFIGURADO"
                
            # Verificar www
            result = subprocess.run(['nslookup', self.www_domain], 
                                  capture_output=True, text=True, timeout=10)
            if "NXDOMAIN" not in result.stdout and "can't find" not in result.stdout:
                dns_results["www_subdomain"] = "CONFIGURADO"
            else:
                dns_results["www_subdomain"] = "NÃO CONFIGURADO"
                
            # Verificar target do Render
            result = subprocess.run(['nslookup', 'techze-diagnostico-frontend.onrender.com'], 
                                  capture_output=True, text=True, timeout=10)
            if "NXDOMAIN" not in result.stdout:
                dns_results["render_target"] = "ATIVO"
            else:
                dns_results["render_target"] = "INATIVO"
                
        except Exception as e:
            self.log(f"❌ Erro ao verificar DNS: {e}", "ERROR")
            
        return dns_results
    
    def get_render_services(self):
        """Obtém informações dos serviços no Render"""
        self.log("🔍 Verificando serviços no Render...")
        
        try:
            response = requests.get(
                "https://api.render.com/v1/services",
                headers=self.render_headers,
                timeout=30
            )
            
            if response.status_code == 200:
                services = response.json()
                frontend_service = None
                api_service = None
                
                for service in services:
                    if "frontend" in service.get("name", "").lower():
                        frontend_service = service
                    elif "api" in service.get("name", "").lower():
                        api_service = service
                        
                return {
                    "frontend": frontend_service,
                    "api": api_service,
                    "all_services": services
                }
            else:
                self.log(f"❌ Erro ao obter serviços: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro ao conectar com Render API: {e}", "ERROR")
            return None
    
    def get_custom_domains(self, service_id):
        """Obtém domínios customizados de um serviço"""
        try:
            response = requests.get(
                f"https://api.render.com/v1/services/{service_id}/custom-domains",
                headers=self.render_headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            self.log(f"❌ Erro ao obter domínios customizados: {e}", "ERROR")
            return []
    
    def test_domain_accessibility(self):
        """Testa acessibilidade dos domínios"""
        self.log("🔍 Testando acessibilidade dos domínios...")
        
        domains_to_test = [
            f"https://{self.domain}",
            f"https://{self.www_domain}",
            "https://techze-diagnostico-frontend.onrender.com"
        ]
        
        results = {}
        
        for domain in domains_to_test:
            try:
                response = requests.get(domain, timeout=10, allow_redirects=True)
                results[domain] = {
                    "status": response.status_code,
                    "accessible": response.status_code < 400,
                    "redirect_url": response.url if response.url != domain else None
                }
            except requests.exceptions.RequestException as e:
                results[domain] = {
                    "status": "ERROR",
                    "accessible": False,
                    "error": str(e)
                }
        
        return results    
    def generate_dns_instructions(self):
        """Gera instruções específicas para configuração DNS no IONOS"""
        
        instructions = f"""
📋 INSTRUÇÕES PARA CONFIGURAÇÃO DNS NO IONOS

🔧 PROBLEMA IDENTIFICADO:
- ❌ Domínio raiz '{self.domain}' não está configurado
- ✅ Subdomínio 'www.{self.domain}' já está configurado

🛠️ CORREÇÕES NECESSÁRIAS NO PAINEL IONOS:

1. 📍 ADICIONAR REGISTRO PARA DOMÍNIO RAIZ:
   - Tipo: CNAME
   - Host/Nome: @ (ou deixe vazio para domínio raiz)
   - Valor/Destino: techze-diagnostico-frontend.onrender.com
   - TTL: 3600 (ou deixe padrão)

2. 📍 VERIFICAR REGISTRO WWW (deve estar assim):
   - Tipo: CNAME
   - Host/Nome: www
   - Valor/Destino: techze-diagnostico-frontend.onrender.com
   - TTL: 3600

3. 🔄 REMOVER CONFLITOS:
   - Se existir registro A para @ (domínio raiz), remova-o
   - Se existir registro A para 'www', remova-o
   - Mantenha apenas os CNAMEs conforme acima

📝 PASSO A PASSO DETALHADO:

1. Entre no painel IONOS → Domínios & SSL
2. Clique em '{self.domain}'
3. Vá em 'Configurações DNS' ou 'DNS Management'
4. Clique em 'Adicionar Registro' ou 'Add Record'
5. Configure conforme especificado acima
6. Salve as alterações
7. Aguarde propagação (até 24 horas, geralmente 1-2 horas)

⚠️ IMPORTANTE:
- Não use registros A e CNAME para o mesmo host
- Use apenas CNAME conforme especificado
- Aguarde a propagação DNS antes de testar
"""
        
        return instructions
    
    def create_verification_script(self):
        """Cria script para verificação contínua"""
        
        script_content = f'''#!/usr/bin/env python3
import requests
import subprocess
import time
from datetime import datetime

def check_domain_status():
    domains = [
        "{self.domain}",
        "{self.www_domain}",
        "techze-diagnostico-frontend.onrender.com"
    ]
    
    print(f"\\n{'='*50}")
    print(f"VERIFICAÇÃO DNS - {{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}")
    print(f"{'='*50}")
    
    for domain in domains:
        try:
            # Teste DNS
            result = subprocess.run(['nslookup', domain], 
                                  capture_output=True, text=True, timeout=10)
            dns_ok = "NXDOMAIN" not in result.stdout and "can't find" not in result.stdout
            
            # Teste HTTP
            try:
                response = requests.get(f"https://{{domain}}", timeout=10)
                http_ok = response.status_code < 400
                status_code = response.status_code
            except:
                http_ok = False
                status_code = "ERROR"
            
            print(f"📍 {{domain:35}} - DNS: {{'✅' if dns_ok else '❌'}} | HTTP: {{'✅' if http_ok else '❌'}} | Status: {{status_code}}")
            
        except Exception as e:
            print(f"❌ {{domain:35}} - ERRO: {{e}}")
    
    print(f"{'='*50}\\n")

if __name__ == "__main__":
    print("🔄 Iniciando verificação contínua...")
    print("⏹️  Pressione Ctrl+C para parar")
    
    try:
        while True:
            check_domain_status()
            time.sleep(60)  # Verifica a cada 1 minuto
    except KeyboardInterrupt:
        print("\\n🛑 Verificação interrompida pelo usuário")
'''
        
        with open("verificar_dns_continuo.py", "w", encoding="utf-8") as f:
            f.write(script_content)
        
        # Tornar executável
        os.chmod("verificar_dns_continuo.py", 0o755)
        
        self.log("✅ Script de verificação contínua criado: verificar_dns_continuo.py")    
    def run_complete_diagnosis(self):
        """Executa diagnóstico completo"""
        
        self.log("🚀 INICIANDO DIAGNÓSTICO COMPLETO DNS + RENDER")
        self.log("="*60)
        
        # 1. Verificar DNS atual
        dns_status = self.check_dns_current_config()
        
        # 2. Verificar serviços Render
        render_services = self.get_render_services()
        
        # 3. Testar acessibilidade
        domain_tests = self.test_domain_accessibility()
        
        # 4. Gerar relatório completo
        report = {
            "timestamp": datetime.now().isoformat(),
            "dns_status": dns_status,
            "render_services": render_services,
            "domain_tests": domain_tests
        }
        
        # Salvar relatório
        with open("relatorio_diagnostico_completo.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 5. Exibir resultados
        self.display_diagnosis_results(report)
        
        # 6. Gerar instruções
        instructions = self.generate_dns_instructions()
        
        # 7. Salvar instruções
        with open("INSTRUCOES_DNS_IONOS.md", "w", encoding="utf-8") as f:
            f.write(instructions)
        
        # 8. Criar script de verificação
        self.create_verification_script()
        
        self.log("✅ Diagnóstico completo finalizado!")
        self.log("📄 Arquivos gerados:")
        self.log("   - relatorio_diagnostico_completo.json")
        self.log("   - INSTRUCOES_DNS_IONOS.md")
        self.log("   - verificar_dns_continuo.py")
        
        return report
    
    def display_diagnosis_results(self, report):
        """Exibe resultados do diagnóstico"""
        
        print(f"\\n{'='*60}")
        print("📊 RESULTADOS DO DIAGNÓSTICO")
        print(f"{'='*60}")
        
        # DNS Status
        print("\\n🌐 STATUS DNS:")
        dns = report["dns_status"]
        print(f"   Domínio raiz ({self.domain}): {dns.get('domain_root', 'N/A')}")
        print(f"   Subdomínio (www.{self.domain}): {dns.get('www_subdomain', 'N/A')}")
        print(f"   Target Render: {dns.get('render_target', 'N/A')}")
        
        # Render Services
        print("\\n🚀 SERVIÇOS RENDER:")
        if report["render_services"]:
            services = report["render_services"]
            if services.get("frontend"):
                frontend = services["frontend"]
                print(f"   Frontend: ✅ {frontend.get('name', 'N/A')} - {frontend.get('serviceDetails', {}).get('url', 'N/A')}")
            else:
                print("   Frontend: ❌ Não encontrado")
                
            if services.get("api"):
                api = services["api"]
                print(f"   API: ✅ {api.get('name', 'N/A')} - {api.get('serviceDetails', {}).get('url', 'N/A')}")
            else:
                print("   API: ❌ Não encontrado")
        else:
            print("   ❌ Erro ao obter informações dos serviços")
        
        # Domain Tests
        print("\\n🔗 TESTE DE ACESSIBILIDADE:")
        for domain, result in report["domain_tests"].items():
            status_icon = "✅" if result.get("accessible", False) else "❌"
            status_code = result.get("status", "N/A")
            print(f"   {status_icon} {domain} - Status: {status_code}")
        
        print(f"\\n{'='*60}")

def main():
    """Função principal"""
    configurator = DNSRenderConfigurator()
    
    try:
        # Executar diagnóstico completo
        report = configurator.run_complete_diagnosis()
        
        print("\\n🎯 PRÓXIMOS PASSOS:")
        print("1. 📖 Leia o arquivo 'INSTRUCOES_DNS_IONOS.md'")
        print("2. 🔧 Configure o DNS conforme as instruções")
        print("3. 🔄 Execute 'python verificar_dns_continuo.py' para monitorar")
        print("4. ⏰ Aguarde propagação DNS (1-24 horas)")
        
    except KeyboardInterrupt:
        print("\\n🛑 Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\\n❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()