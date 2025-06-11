#!/usr/bin/env python3
"""
Verificar Todos os Domínios Configurados no Render
TechZe Diagnóstico - Auditoria Completa
"""

import requests
import json
from datetime import datetime

class RenderDomainAuditor:
    def __init__(self):
        self.render_api_key = "rnd_Tj1JybEJij6A3UhouM7spm8LRbkX"
        self.headers = {
            "Authorization": f"Bearer {self.render_api_key}",
            "Content-Type": "application/json"
        }
        
    def log(self, message, level="INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def get_all_services(self):
        """Obtém todos os serviços"""
        self.log("🔍 Obtendo todos os serviços...")
        
        try:
            response = requests.get(
                "https://api.render.com/v1/services",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                services = response.json()
                self.log(f"📋 Serviços encontrados: {len(services)}")
                return services
            else:
                self.log(f"❌ Erro ao obter serviços: {response.status_code}", "ERROR")
                return []
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return []
    
    def get_domains_for_service(self, service_id, service_name):
        """Obtém domínios de um serviço específico"""
        try:
            response = requests.get(
                f"https://api.render.com/v1/services/{service_id}/custom-domains",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                domains = response.json()
                return domains
            else:
                return []
                
        except Exception as e:
            self.log(f"❌ Erro ao obter domínios do serviço {service_name}: {e}", "ERROR")
            return []
    
    def audit_all_domains(self):
        """Auditoria completa de todos os domínios"""
        self.log("🚀 INICIANDO AUDITORIA COMPLETA DOS DOMÍNIOS")
        self.log("="*60)
        
        # 1. Obter todos os serviços
        services = self.get_all_services()
        
        # 2. Verificar domínios de cada serviço
        all_domains_info = []
        
        for service in services:
            service_info = service.get('service', service)
            service_id = service_info.get('id', 'N/A')
            service_name = service_info.get('name', 'N/A')
            service_type = service_info.get('type', 'N/A')
            service_url = service_info.get('serviceDetails', {}).get('url', 'N/A')
            
            self.log(f"🔍 Verificando serviço: {service_name} ({service_type})")
            
            # Obter domínios customizados
            domains = self.get_domains_for_service(service_id, service_name)
            
            service_data = {
                "service_id": service_id,
                "service_name": service_name,
                "service_type": service_type,
                "service_url": service_url,
                "custom_domains": domains,
                "domain_count": len(domains)
            }
            
            all_domains_info.append(service_data)
            
            # Mostrar domínios encontrados
            if domains:
                self.log(f"   📍 Domínios encontrados: {len(domains)}")
                for domain in domains:
                    domain_name = domain.get('name', 'N/A')
                    verification_status = domain.get('verificationStatus', 'N/A')
                    created_at = domain.get('createdAt', 'N/A')
                    self.log(f"      - {domain_name}: {verification_status} (criado: {created_at})")
            else:
                self.log(f"   📍 Nenhum domínio customizado")
        
        # 3. Gerar relatório completo
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_services": len(services),
            "services_with_domains": len([s for s in all_domains_info if s["domain_count"] > 0]),
            "services_details": all_domains_info,
            "techreparo_domains": self.find_techreparo_domains(all_domains_info)
        }
        
        # 4. Salvar relatório
        with open("auditoria_completa_dominios.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 5. Exibir resumo
        self.display_summary(report)
        
        return report
    
    def find_techreparo_domains(self, services_info):
        """Encontra onde estão os domínios techreparo.com"""
        techreparo_domains = []
        
        for service in services_info:
            for domain in service["custom_domains"]:
                domain_name = domain.get('name', '')
                if 'techreparo.com' in domain_name:
                    techreparo_domains.append({
                        "domain": domain_name,
                        "service_name": service["service_name"],
                        "service_id": service["service_id"],
                        "service_type": service["service_type"],
                        "verification_status": domain.get('verificationStatus', 'N/A'),
                        "domain_details": domain
                    })
        
        return techreparo_domains
    
    def display_summary(self, report):
        """Exibe resumo da auditoria"""
        
        print(f"\n{'='*60}")
        print("📊 RESUMO DA AUDITORIA DE DOMÍNIOS")
        print(f"{'='*60}")
        
        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   Total de serviços: {report['total_services']}")
        print(f"   Serviços com domínios: {report['services_with_domains']}")
        print(f"   Domínios techreparo.com encontrados: {len(report['techreparo_domains'])}")
        
        print(f"\n🎯 DOMÍNIOS TECHREPARO.COM:")
        if report['techreparo_domains']:
            for domain_info in report['techreparo_domains']:
                print(f"   📍 {domain_info['domain']}")
                print(f"      Serviço: {domain_info['service_name']} ({domain_info['service_type']})")
                print(f"      ID: {domain_info['service_id']}")
                print(f"      Status: {domain_info['verification_status']}")
                print()
        else:
            print("   ❌ Nenhum domínio techreparo.com encontrado!")
        
        print(f"\n📋 TODOS OS SERVIÇOS:")
        for service in report['services_details']:
            print(f"   🔸 {service['service_name']} ({service['service_type']})")
            print(f"      ID: {service['service_id']}")
            print(f"      URL: {service['service_url']}")
            print(f"      Domínios: {service['domain_count']}")
            if service['custom_domains']:
                for domain in service['custom_domains']:
                    domain_name = domain.get('name', 'N/A')
                    print(f"         - {domain_name}")
            print()
        
        print(f"{'='*60}")
    
    def generate_solution_plan(self, report):
        """Gera plano de solução baseado na auditoria"""
        
        techreparo_domains = report['techreparo_domains']
        
        if not techreparo_domains:
            solution = """
🚨 SOLUÇÃO NECESSÁRIA

❌ PROBLEMA: Domínios techreparo.com não encontrados em nenhum serviço!

🛠️ AÇÃO NECESSÁRIA:
1. Configurar domínios no serviço correto (techze-frontend-app)
2. Corrigir DNS no IONOS

📋 PRÓXIMOS PASSOS:
1. Execute: python configurar_render_corrigido.py
2. Configure DNS conforme instruções
"""
        else:
            wrong_service = None
            correct_service = None
            
            for domain_info in techreparo_domains:
                if domain_info['service_name'] != 'techze-frontend-app':
                    wrong_service = domain_info
                else:
                    correct_service = domain_info
            
            if wrong_service and not correct_service:
                solution = f"""
🚨 SOLUÇÃO NECESSÁRIA

❌ PROBLEMA: Domínios estão no serviço ERRADO!

📍 SITUAÇÃO ATUAL:
- Domínios estão em: {wrong_service['service_name']} ({wrong_service['service_id']})
- Deveriam estar em: techze-frontend-app (srv-d13i0ps9c44c739cd3e0)

🛠️ AÇÃO NECESSÁRIA:
1. Remover domínios do serviço atual
2. Adicionar domínios no serviço correto
3. Verificar DNS

📋 PRÓXIMOS PASSOS:
1. Execute: python mover_dominios_render.py
2. Aguarde propagação DNS
"""
            elif correct_service:
                solution = f"""
✅ DOMÍNIOS JÁ CONFIGURADOS CORRETAMENTE!

📍 SITUAÇÃO ATUAL:
- Domínios estão em: {correct_service['service_name']}
- Status: {correct_service['verification_status']}

🔍 VERIFICAÇÃO NECESSÁRIA:
- Confirmar DNS no IONOS aponta para o serviço correto
- Aguardar propagação se necessário

📋 PRÓXIMOS PASSOS:
1. Execute: python verificar_dns_continuo.py
2. Teste os domínios após propagação
"""
        
        # Salvar plano de solução
        with open("PLANO_SOLUCAO_DOMINIOS.md", "w", encoding="utf-8") as f:
            f.write(solution)
        
        print(solution)
        
        return solution

def main():
    """Função principal"""
    auditor = RenderDomainAuditor()
    
    try:
        # Executar auditoria completa
        report = auditor.audit_all_domains()
        
        # Gerar plano de solução
        auditor.generate_solution_plan(report)
        
        print("\n🎯 AUDITORIA FINALIZADA!")
        print("📄 Arquivos gerados:")
        print("   - auditoria_completa_dominios.json")
        print("   - PLANO_SOLUCAO_DOMINIOS.md")
        
    except KeyboardInterrupt:
        print("\n🛑 Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()