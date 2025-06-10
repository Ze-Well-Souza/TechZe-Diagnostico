#!/usr/bin/env python3
"""
Forçar Configuração do Render - Método Alternativo
TechZe Diagnóstico - Correção Forçada via API
"""

import requests
import json
import time
from datetime import datetime

class RenderForceConfig:
    def __init__(self):
        self.render_api_key = "rnd_Tj1JybEJij6A3UhouM7spm8LRbkX"
        self.frontend_service_id = "srv-d13i0ps9c44c739cd3e0"
        self.headers = {
            "Authorization": f"Bearer {self.render_api_key}",
            "Content-Type": "application/json"
        }
        
    def log(self, message, level="INFO"):
        """Log com timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def force_service_update(self):
        """Força atualização completa do serviço"""
        self.log("🔧 FORÇANDO atualização completa do serviço...")
        
        # Configuração completa do serviço
        service_config = {
            "name": "techze-frontend-app",
            "type": "static_site",
            "serviceDetails": {
                "buildCommand": "npm install && npm run build",
                "publishPath": "dist",
                "pullRequestPreviewsEnabled": "yes",
                "headers": [],
                "redirects": [],
                "env": "node"
            }
        }
        
        try:
            response = requests.patch(
                f"https://api.render.com/v1/services/{self.frontend_service_id}",
                headers=self.headers,
                json=service_config,
                timeout=30
            )
            
            self.log(f"📊 Status da resposta: {response.status_code}")
            
            if response.status_code in [200, 202]:
                self.log("✅ Configuração forçada com sucesso!", "SUCCESS")
                return response.json()
            else:
                self.log(f"❌ Erro ao forçar configuração: {response.status_code}", "ERROR")
                self.log(f"Resposta: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return None
    
    def update_service_details_only(self):
        """Atualiza apenas os detalhes do serviço"""
        self.log("🎯 Atualizando apenas serviceDetails...")
        
        config_data = {
            "serviceDetails": {
                "buildCommand": "npm install && npm run build",
                "publishPath": "dist"
            }
        }
        
        try:
            response = requests.patch(
                f"https://api.render.com/v1/services/{self.frontend_service_id}",
                headers=self.headers,
                json=config_data,
                timeout=30
            )
            
            if response.status_code in [200, 202]:
                self.log("✅ ServiceDetails atualizado!", "SUCCESS")
                return response.json()
            else:
                self.log(f"❌ Erro: {response.status_code} - {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return None
    
    def try_individual_updates(self):
        """Tenta atualizações individuais"""
        self.log("🔄 Tentando atualizações individuais...")
        
        # Tentar apenas build command
        self.log("1️⃣ Atualizando Build Command...")
        try:
            response1 = requests.patch(
                f"https://api.render.com/v1/services/{self.frontend_service_id}",
                headers=self.headers,
                json={"buildCommand": "npm install && npm run build"},
                timeout=30
            )
            self.log(f"   Build Command: {response1.status_code}")
        except Exception as e:
            self.log(f"   Build Command falhou: {e}", "ERROR")
        
        time.sleep(2)
        
        # Tentar apenas publish path
        self.log("2️⃣ Atualizando Publish Path...")
        try:
            response2 = requests.patch(
                f"https://api.render.com/v1/services/{self.frontend_service_id}",
                headers=self.headers,
                json={"publishPath": "dist"},
                timeout=30
            )
            self.log(f"   Publish Path: {response2.status_code}")
        except Exception as e:
            self.log(f"   Publish Path falhou: {e}", "ERROR")
        
        return True
    
    def verify_current_config(self):
        """Verifica configuração atual"""
        self.log("🔍 Verificando configuração atual...")
        
        try:
            response = requests.get(
                f"https://api.render.com/v1/services/{self.frontend_service_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                service_data = response.json()
                service_info = service_data.get('service', service_data)
                details = service_info.get('serviceDetails', {})
                
                current = {
                    "build_command": details.get('buildCommand', ''),
                    "publish_path": details.get('publishPath', ''),
                    "name": service_info.get('name', ''),
                    "type": service_info.get('type', '')
                }
                
                self.log("📊 CONFIGURAÇÃO ATUAL:")
                self.log(f"   Build Command: '{current['build_command']}'")
                self.log(f"   Publish Path: '{current['publish_path']}'")
                self.log(f"   Nome: {current['name']}")
                self.log(f"   Tipo: {current['type']}")
                
                return current
            else:
                self.log(f"❌ Erro ao verificar: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return None
    
    def create_manual_instructions(self):
        """Cria instruções manuais detalhadas"""
        
        instructions = """
🛠️ INSTRUÇÕES MANUAIS PARA CONFIGURAR O RENDER

Como a API não está aplicando as configurações, siga estes passos:

1. 🌐 ACESSE O DASHBOARD:
   https://dashboard.render.com/static/srv-d13i0ps9c44c739cd3e0

2. 🔧 VÁ EM SETTINGS:
   - Clique na aba "Settings" no menu lateral

3. ⚙️ CONFIGURE BUILD COMMAND:
   - Procure por "Build Command"
   - Apague o conteúdo atual
   - Digite: npm install && npm run build
   - Clique em "Save Changes"

4. 📂 CONFIGURE PUBLISH DIRECTORY:
   - Procure por "Publish Directory"
   - Apague "public"
   - Digite: dist
   - Clique em "Save Changes"

5. 🚀 FORCE NOVO DEPLOY:
   - Vá na aba "Manual Deploy"
   - Clique em "Deploy latest commit"
   - Aguarde o deploy completar (5-10 minutos)

6. 🧪 TESTE O RESULTADO:
   - https://techze-frontend-app.onrender.com
   - https://techreparo.com
   - https://www.techreparo.com

⚠️ IMPORTANTE:
- Aguarde cada configuração salvar antes da próxima
- O deploy pode demorar até 10 minutos
- Se ainda der 404, aguarde mais 5 minutos (propagação)

✅ CONFIGURAÇÕES CORRETAS:
- Build Command: npm install && npm run build
- Publish Directory: dist
- Service Type: Static Site
"""
        
        with open("INSTRUCOES_MANUAIS_RENDER.md", "w", encoding="utf-8") as f:
            f.write(instructions)
        
        print(instructions)
        
        return instructions
    
    def run_force_attempt(self):
        """Executa tentativa de força"""
        self.log("🚀 INICIANDO TENTATIVA DE FORÇA NA CONFIGURAÇÃO")
        self.log("="*60)
        
        # 1. Verificar estado atual
        initial_config = self.verify_current_config()
        
        # 2. Tentar atualização completa
        self.log("\n🔧 TENTATIVA 1: Atualização completa...")
        result1 = self.force_service_update()
        
        time.sleep(5)
        
        # 3. Verificar se funcionou
        config_after_1 = self.verify_current_config()
        
        if config_after_1 and config_after_1['build_command'] and config_after_1['publish_path'] == 'dist':
            self.log("✅ SUCESSO! Configuração aplicada!", "SUCCESS")
            return True
        
        # 4. Tentar apenas serviceDetails
        self.log("\n🎯 TENTATIVA 2: Apenas serviceDetails...")
        result2 = self.update_service_details_only()
        
        time.sleep(5)
        
        # 5. Verificar novamente
        config_after_2 = self.verify_current_config()
        
        if config_after_2 and config_after_2['build_command'] and config_after_2['publish_path'] == 'dist':
            self.log("✅ SUCESSO! Configuração aplicada!", "SUCCESS")
            return True
        
        # 6. Tentar atualizações individuais
        self.log("\n🔄 TENTATIVA 3: Atualizações individuais...")
        self.try_individual_updates()
        
        time.sleep(5)
        
        # 7. Verificação final
        final_config = self.verify_current_config()
        
        if final_config and final_config['build_command'] and final_config['publish_path'] == 'dist':
            self.log("✅ SUCESSO! Configuração aplicada!", "SUCCESS")
            return True
        
        # 8. Se nada funcionou, criar instruções manuais
        self.log("\n❌ TODAS AS TENTATIVAS FALHARAM", "ERROR")
        self.log("📋 Criando instruções manuais...", "WARNING")
        
        self.create_manual_instructions()
        
        return False

def main():
    """Função principal"""
    forcer = RenderForceConfig()
    
    try:
        success = forcer.run_force_attempt()
        
        if success:
            print("\n🎉 CONFIGURAÇÃO APLICADA COM SUCESSO!")
            print("🚀 Agora force um novo deploy no dashboard")
        else:
            print("\n📋 SIGA AS INSTRUÇÕES MANUAIS CRIADAS")
            print("📄 Arquivo: INSTRUCOES_MANUAIS_RENDER.md")
        
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()