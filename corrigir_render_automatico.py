#!/usr/bin/env python3
"""
Correção Automática das Configurações do Render
TechZe Diagnóstico - Automatização de Build e Deploy
"""

import requests
import json
import time
from datetime import datetime

class RenderAutoFix:
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
        
    def update_service_settings(self):
        """Atualiza as configurações do serviço"""
        self.log("🔧 Atualizando configurações do serviço...")
        
        # Configurações corretas para o TechZe
        config_data = {
            "buildCommand": "npm install && npm run build",
            "publishPath": "dist"
        }
        
        try:
            response = requests.patch(
                f"https://api.render.com/v1/services/{self.frontend_service_id}",
                headers=self.headers,
                json=config_data,
                timeout=30
            )
            
            if response.status_code == 200:
                self.log("✅ Configurações atualizadas com sucesso!", "SUCCESS")
                return response.json()
            else:
                self.log(f"❌ Erro ao atualizar configurações: {response.status_code}", "ERROR")
                if response.content:
                    self.log(f"Resposta: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return None
    
    def trigger_deploy(self):
        """Força um novo deploy"""
        self.log("🚀 Iniciando deploy manual...")
        
        try:
            response = requests.post(
                f"https://api.render.com/v1/services/{self.frontend_service_id}/deploys",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 201:
                deploy_data = response.json()
                deploy_id = deploy_data.get('id')
                self.log(f"✅ Deploy iniciado! ID: {deploy_id}", "SUCCESS")
                return deploy_id
            else:
                self.log(f"❌ Erro ao iniciar deploy: {response.status_code}", "ERROR")
                if response.content:
                    self.log(f"Resposta: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return None
    
    def monitor_deploy(self, deploy_id, max_wait_minutes=10):
        """Monitora o progresso do deploy"""
        if not deploy_id:
            return False
            
        self.log(f"👁️ Monitorando deploy {deploy_id}...")
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        while time.time() - start_time < max_wait_seconds:
            try:
                response = requests.get(
                    f"https://api.render.com/v1/services/{self.frontend_service_id}/deploys/{deploy_id}",
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    deploy_info = response.json()
                    deploy_data = deploy_info.get('deploy', deploy_info)
                    status = deploy_data.get('status', 'unknown')
                    
                    self.log(f"📊 Status: {status}")
                    
                    if status == 'live':
                        self.log("🎉 Deploy concluído com sucesso!", "SUCCESS")
                        return True
                    elif status in ['build_failed', 'upload_failed', 'canceled']:
                        self.log(f"❌ Deploy falhou: {status}", "ERROR")
                        return False
                    elif status in ['building', 'uploading', 'pre_deploy']:
                        self.log(f"🔄 Deploy em andamento: {status}")
                        time.sleep(30)  # Aguarda 30 segundos
                    else:
                        self.log(f"⏳ Status: {status}")
                        time.sleep(20)
                        
                else:
                    self.log(f"❌ Erro ao verificar deploy: {response.status_code}", "ERROR")
                    time.sleep(30)
                    
            except Exception as e:
                self.log(f"❌ Erro no monitoramento: {e}", "ERROR")
                time.sleep(30)
        
        self.log("⏰ Timeout no monitoramento", "WARNING")
        return False
    
    def test_deployment(self):
        """Testa se o deploy está funcionando"""
        self.log("🔍 Testando deployment...")
        
        test_urls = [
            "https://techze-frontend-app.onrender.com",
            "https://techreparo.com",
            "https://www.techreparo.com"
        ]
        
        results = {}
        
        for url in test_urls:
            try:
                self.log(f"📡 Testando: {url}")
                response = requests.get(url, timeout=15, allow_redirects=True)
                
                status_icon = "✅" if response.status_code == 200 else "❌"
                self.log(f"{status_icon} {url}: {response.status_code}")
                
                results[url] = {
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "content_length": len(response.content)
                }
                
            except Exception as e:
                self.log(f"❌ {url}: Erro - {e}", "ERROR")
                results[url] = {
                    "status_code": None,
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def get_current_settings(self):
        """Obtém configurações atuais do serviço"""
        self.log("📋 Obtendo configurações atuais...")
        
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
                
                current_settings = {
                    "build_command": details.get('buildCommand', ''),
                    "publish_path": details.get('publishPath', ''),
                    "service_name": service_info.get('name', ''),
                    "type": service_info.get('type', ''),
                    "status": service_info.get('suspended', '')
                }
                
                return current_settings
            else:
                self.log(f"❌ Erro ao obter configurações: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return None
    
    def run_complete_fix(self):
        """Executa correção completa automatizada"""
        self.log("🚀 INICIANDO CORREÇÃO AUTOMÁTICA DO RENDER")
        self.log("="*60)
        
        # 1. Verificar configurações atuais
        current_settings = self.get_current_settings()
        if current_settings:
            self.log("📊 CONFIGURAÇÕES ATUAIS:")
            self.log(f"   Build Command: '{current_settings['build_command']}'")
            self.log(f"   Publish Path: '{current_settings['publish_path']}'")
            self.log(f"   Service Type: {current_settings['type']}")
            self.log(f"   Status: {current_settings['status']}")
            
            # Verificar se precisa de correção
            needs_build_fix = not current_settings['build_command'] or current_settings['build_command'].strip() == ''
            needs_path_fix = current_settings['publish_path'] != 'dist'
            
            if not needs_build_fix and not needs_path_fix:
                self.log("✅ Configurações já estão corretas!", "SUCCESS")
                # Apenas força novo deploy
                deploy_id = self.trigger_deploy()
                if deploy_id:
                    success = self.monitor_deploy(deploy_id)
                    if success:
                        self.test_deployment()
                return
        
        # 2. Atualizar configurações
        self.log("🔧 Corrigindo configurações...")
        update_result = self.update_service_settings()
        
        if not update_result:
            self.log("❌ Falha na atualização. Abortando.", "ERROR")
            return
        
        # 3. Aguardar propagação
        self.log("⏳ Aguardando propagação das configurações...")
        time.sleep(10)
        
        # 4. Forçar novo deploy
        deploy_id = self.trigger_deploy()
        
        if not deploy_id:
            self.log("❌ Falha ao iniciar deploy. Procedimento manual necessário.", "ERROR")
            return
        
        # 5. Monitorar deploy
        deploy_success = self.monitor_deploy(deploy_id)
        
        # 6. Testar resultado
        if deploy_success:
            self.log("🧪 Executando testes finais...")
            test_results = self.test_deployment()
            
            # 7. Relatório final
            self.generate_final_report(test_results, current_settings)
        else:
            self.log("❌ Deploy não foi concluído com sucesso", "ERROR")
    
    def generate_final_report(self, test_results, initial_settings):
        """Gera relatório final"""
        
        print(f"\n{'='*60}")
        print("📊 RELATÓRIO FINAL DA CORREÇÃO")
        print(f"{'='*60}")
        
        # Status das configurações
        print("\n🔧 CONFIGURAÇÕES CORRIGIDAS:")
        print(f"   ✅ Build Command: 'npm install && npm run build'")
        print(f"   ✅ Publish Path: 'dist'")
        
        # Status dos testes
        print("\n🧪 TESTES DE FUNCIONAMENTO:")
        all_working = True
        for url, result in test_results.items():
            if result['success']:
                print(f"   ✅ {url}: OK ({result['status_code']})")
            else:
                print(f"   ❌ {url}: FALHA ({result.get('status_code', 'N/A')})")
                all_working = False
        
        # Resumo final
        if all_working:
            print(f"\n🎉 SUCESSO TOTAL!")
            print("   📱 Site funcionando em todos os domínios")
            print("   ⚡ Build e deploy corrigidos")
            print("   🌐 DNS configurado corretamente")
        else:
            print(f"\n⚠️ CORREÇÕES APLICADAS, MAS ALGUNS PROBLEMAS PERSISTEM")
            print("   🔍 Pode ser necessário aguardar propagação DNS")
            print("   ⏰ Tente novamente em 5-10 minutos")
        
        # Gerar arquivo de relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "initial_settings": initial_settings,
            "corrections_applied": {
                "build_command": "npm install && npm run build",
                "publish_path": "dist"
            },
            "test_results": test_results,
            "all_working": all_working
        }
        
        with open("correcao_render_completa.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo: correcao_render_completa.json")
        print(f"{'='*60}")

def main():
    """Função principal"""
    fixer = RenderAutoFix()
    
    try:
        fixer.run_complete_fix()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Operação interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")

if __name__ == "__main__":
    main()