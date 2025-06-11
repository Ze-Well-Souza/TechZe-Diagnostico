#!/usr/bin/env python3
"""
Configurar Domínio Customizado via API do Render
TechZe Diagnóstico - Configuração Automática
"""

import requests
import json
from datetime import datetime

class RenderDomainConfigurator:
    def __init__(self):
        self.render_api_key = "rnd_Tj1JybEJij6A3UhouM7spm8LRbkX"
        self.domain = "techreparo.com"
        self.www_domain = f"www.{self.domain}"
        self.service_id = "srv-d13i0ps9c44c739cd3e0"  # techze-frontend-app
        self.headers = {
            "Authorization": f"Bearer {self.render_api_key}",
            "Content-Type": "application/json"
        }
        
    def log(self, message, level="INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def get_service_details(self):
        """Obtém detalhes do serviço frontend"""
        self.log("🔍 Obtendo detalhes do serviço...")
        
        try:
            response = requests.get(
                f"https://api.render.com/v1/services/{self.service_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                service = response.json()
                self.log(f"✅ Serviço encontrado: {service.get('name', 'N/A')}")
                return service
            else:
                self.log(f"❌ Erro ao obter serviço: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return None
    
    def get_custom_domains(self):
        """Lista domínios customizados atuais"""
        self.log("🔍 Verificando domínios customizados atuais...")
        
        try:
            response = requests.get(
                f"https://api.render.com/v1/services/{self.service_id}/custom-domains",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                domains = response.json()
                self.log(f"📋 Domínios encontrados: {len(domains)}")
                for domain in domains:
                    name = domain.get('name', 'N/A')
                    status = domain.get('verificationStatus', 'N/A')
                    self.log(f"   - {name}: {status}")
                return domains
            else:
                self.log(f"❌ Erro ao obter domínios: {response.status_code}", "ERROR")
                return []
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return []
    
    def add_custom_domain(self, domain_name):
        """Adiciona domínio customizado"""
        self.log(f"🔧 Adicionando domínio: {domain_name}")
        
        try:
            payload = {
                "name": domain_name
            }
            
            response = requests.post(
                f"https://api.render.com/v1/services/{self.service_id}/custom-domains",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                domain = response.json()
                self.log(f"✅ Domínio adicionado: {domain_name}")
                return domain
            else:
                self.log(f"❌ Erro ao adicionar domínio: {response.status_code} - {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return None
    
    def verify_domain(self, domain_name):
        """Verifica domínio customizado"""
        self.log(f"🔍 Verificando domínio: {domain_name}")
        
        try:
            response = requests.post(
                f"https://api.render.com/v1/services/{self.service_id}/custom-domains/{domain_name}/verify",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"✅ Verificação iniciada para: {domain_name}")
                return result
            else:
                self.log(f"❌ Erro na verificação: {response.status_code} - {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return None
    
    def configure_domains_complete(self):
        """Configuração completa dos domínios"""
        self.log("🚀 INICIANDO CONFIGURAÇÃO COMPLETA DOS DOMÍNIOS")
        self.log("="*60)
        
        # 1. Verificar serviço
        service = self.get_service_details()
        if not service:
            self.log("❌ Não foi possível obter detalhes do serviço", "ERROR")
            return False
        
        # 2. Verificar domínios atuais
        current_domains = self.get_custom_domains()
        current_domain_names = [d.get('name') for d in current_domains]
        
        # 3. Adicionar domínios se necessário
        domains_to_add = []
        
        if self.domain not in current_domain_names:
            domains_to_add.append(self.domain)
            
        if self.www_domain not in current_domain_names:
            domains_to_add.append(self.www_domain)
        
        # 4. Adicionar domínios
        for domain in domains_to_add:
            self.add_custom_domain(domain)
        
        # 5. Verificar domínios
        time.sleep(2)  # Aguardar processamento
        
        for domain in [self.domain, self.www_domain]:
            self.verify_domain(domain)
        
        # 6. Status final
        time.sleep(2)
        final_domains = self.get_custom_domains()
        
        # 7. Gerar relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "service_id": self.service_id,
            "service_details": service,
            "domains_configured": final_domains,
            "success": len(final_domains) >= 2
        }
        
        # Salvar relatório
        with open("relatorio_configuracao_render.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log("✅ Configuração concluída!")
        self.log("📄 Relatório salvo: relatorio_configuracao_render.json")
        
        return report
    
    def show_dns_instructions(self):
        """Mostra instruções finais para DNS"""
        
        instructions = f"""
🎯 PRÓXIMOS PASSOS PARA FINALIZAR

1. 🔧 CONFIGURAR DNS NO IONOS:
   
   Acesse: https://my.ionos.com
   Vá em: Domínios & SSL → {self.domain} → DNS
   
   Configure os registros:
   
   📍 DOMÍNIO RAIZ:
   - Tipo: CNAME
   - Host: @ (ou vazio)  
   - Destino: {self.service_id}.onrender.com
   
   📍 SUBDOMÍNIO WWW:
   - Tipo: CNAME
   - Host: www
   - Destino: {self.service_id}.onrender.com

2. ⏰ AGUARDAR PROPAGAÇÃO:
   - DNS propaga em 15-30 minutos geralmente
   - Máximo: 24 horas

3. 🔍 VERIFICAR STATUS:
   Execute: python verificar_dns_continuo.py

4. ✅ TESTE FINAL:
   - https://{self.domain}
   - https://{self.www_domain}
"""
        
        print(instructions)
        
        # Salvar instruções
        with open("INSTRUCOES_FINAIS_DNS.md", "w", encoding="utf-8") as f:
            f.write(instructions)

def main():
    """Função principal"""
    import time
    
    configurator = RenderDomainConfigurator()
    
    try:
        # Executar configuração completa
        report = configurator.configure_domains_complete()
        
        # Mostrar instruções finais
        configurator.show_dns_instructions()
        
        print("\n🎯 CONFIGURAÇÃO RENDER FINALIZADA!")
        print("📖 Agora siga as instruções em 'INSTRUCOES_FINAIS_DNS.md'")
        
    except KeyboardInterrupt:
        print("\n🛑 Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")

if __name__ == "__main__":
    main()