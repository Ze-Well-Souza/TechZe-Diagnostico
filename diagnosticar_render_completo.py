#!/usr/bin/env python3
"""
Diagnóstico Completo do Render
TechZe Diagnóstico - Análise de Problemas no Serviço
"""

import requests
import json
from datetime import datetime

class RenderDiagnostic:
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
        
    def get_service_details(self):
        """Obtém detalhes completos do serviço"""
        self.log("🔍 Verificando detalhes do serviço frontend...")
        
        try:
            response = requests.get(
                f"https://api.render.com/v1/services/{self.frontend_service_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"❌ Erro ao obter serviço: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return None
    
    def get_deploys(self):
        """Obtém histórico de deploys"""
        self.log("🔍 Verificando deploys...")
        
        try:
            response = requests.get(
                f"https://api.render.com/v1/services/{self.frontend_service_id}/deploys",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"❌ Erro ao obter deploys: {response.status_code}", "ERROR")
                return []
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return []
    
    def get_environment_vars(self):
        """Obtém variáveis de ambiente"""
        self.log("🔍 Verificando variáveis de ambiente...")
        
        try:
            response = requests.get(
                f"https://api.render.com/v1/services/{self.frontend_service_id}/env-vars",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"❌ Erro ao obter env vars: {response.status_code}", "ERROR")
                return []
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return []
    
    def analyze_service_issues(self, service_data, deploys, env_vars):
        """Analisa problemas do serviço"""
        issues = []
        
        # Verificar status do serviço
        if service_data:
            service_info = service_data.get('service', service_data)
            suspended = service_info.get('suspended', 'unknown')
            
            if suspended != 'not_suspended':
                issues.append(f"❌ SERVIÇO SUSPENSO: {suspended}")
            
            # Verificar tipo de serviço
            service_type = service_info.get('type', 'unknown')
            if service_type != 'static_site':
                issues.append(f"⚠️ TIPO INESPERADO: {service_type} (esperado: static_site)")
            
            # Verificar configuração
            details = service_info.get('serviceDetails', {})
            build_command = details.get('buildCommand', 'N/A')
            publish_path = details.get('publishPath', 'N/A')
            
            if not build_command or build_command == '':
                issues.append("⚠️ BUILD COMMAND vazio")
            
            if publish_path != 'public' and publish_path != 'dist' and publish_path != 'build':
                issues.append(f"⚠️ PUBLISH PATH suspeito: {publish_path}")
        
        # Verificar deploys
        if deploys:
            latest_deploy = deploys[0] if deploys else None
            if latest_deploy:
                deploy_info = latest_deploy.get('deploy', latest_deploy)
                status = deploy_info.get('status', 'unknown')
                
                if status != 'live':
                    issues.append(f"❌ ÚLTIMO DEPLOY: {status}")
                
                # Verificar se há falhas recentes
                recent_failures = 0
                for deploy in deploys[:5]:  # Últimos 5 deploys
                    deploy_info = deploy.get('deploy', deploy)
                    if deploy_info.get('status') in ['build_failed', 'upload_failed', 'canceled']:
                        recent_failures += 1
                
                if recent_failures > 2:
                    issues.append(f"⚠️ MÚLTIPLAS FALHAS RECENTES: {recent_failures}/5")
        
        return issues
    
    def run_complete_diagnostic(self):
        """Executa diagnóstico completo"""
        self.log("🚀 INICIANDO DIAGNÓSTICO COMPLETO DO RENDER")
        self.log("="*60)
        
        # 1. Obter dados do serviço
        service_data = self.get_service_details()
        
        # 2. Obter deploys
        deploys = self.get_deploys()
        
        # 3. Obter variáveis de ambiente
        env_vars = self.get_environment_vars()
        
        # 4. Analisar problemas
        issues = self.analyze_service_issues(service_data, deploys, env_vars)
        
        # 5. Exibir resultado
        self.display_diagnostic_results(service_data, deploys, env_vars, issues)
        
        # 6. Gerar relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "service_data": service_data,
            "deploys": deploys[:10] if deploys else [],  # Últimos 10
            "env_vars_count": len(env_vars) if env_vars else 0,
            "issues_found": issues,
            "critical_issues": len([i for i in issues if "❌" in i]),
            "warning_issues": len([i for i in issues if "⚠️" in i])
        }
        
        with open("diagnostico_render_completo.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # 7. Sugerir soluções
        self.suggest_solutions(issues, service_data, deploys)
        
        return report
    
    def display_diagnostic_results(self, service_data, deploys, env_vars, issues):
        """Exibe resultados do diagnóstico"""
        
        print(f"\n{'='*60}")
        print("📊 DIAGNÓSTICO DO RENDER")
        print(f"{'='*60}")
        
        # Status do serviço
        if service_data:
            service_info = service_data.get('service', service_data)
            print(f"\n🔧 SERVIÇO:")
            print(f"   Nome: {service_info.get('name', 'N/A')}")
            print(f"   Tipo: {service_info.get('type', 'N/A')}")
            print(f"   Status: {service_info.get('suspended', 'N/A')}")
            print(f"   URL: {service_info.get('serviceDetails', {}).get('url', 'N/A')}")
            
            details = service_info.get('serviceDetails', {})
            print(f"   Build Command: {details.get('buildCommand', 'N/A')}")
            print(f"   Publish Path: {details.get('publishPath', 'N/A')}")
        
        # Status dos deploys
        if deploys:
            print(f"\n🚀 DEPLOYS (últimos 5):")
            for i, deploy in enumerate(deploys[:5]):
                deploy_info = deploy.get('deploy', deploy)
                status = deploy_info.get('status', 'N/A')
                created_at = deploy_info.get('createdAt', 'N/A')
                commit = deploy_info.get('commit', {}).get('message', 'N/A')[:50]
                
                status_icon = "✅" if status == "live" else "❌" if "failed" in status else "🔄"
                print(f"   {i+1}. {status_icon} {status} - {created_at[:19]} - {commit}")
        
        # Variáveis de ambiente
        if env_vars is not None:
            print(f"\n🔧 VARIÁVEIS DE AMBIENTE: {len(env_vars)} configuradas")
        
        # Problemas encontrados
        print(f"\n🚨 PROBLEMAS IDENTIFICADOS:")
        if issues:
            for issue in issues:
                print(f"   {issue}")
        else:
            print("   ✅ Nenhum problema crítico identificado")
        
        print(f"\n{'='*60}")
    
    def suggest_solutions(self, issues, service_data, deploys):
        """Sugere soluções baseadas nos problemas"""
        
        print(f"\n🛠️ SOLUÇÕES SUGERIDAS:")
        
        critical_issues = [i for i in issues if "❌" in i]
        
        if not issues:
            print("   🎯 Problema provavelmente na configuração da aplicação")
            print("   📋 Próximos passos:")
            print("      1. Verificar se a aplicação está construindo corretamente")
            print("      2. Verificar se o index.html está no diretório correto")
            print("      3. Forçar novo deploy")
        
        elif critical_issues:
            print("   🚨 AÇÕES URGENTES:")
            
            if any("SUSPENSO" in issue for issue in critical_issues):
                print("      1. ✅ Reativar serviço no painel do Render")
            
            if any("DEPLOY" in issue for issue in critical_issues):
                print("      2. 🔄 Forçar novo deploy manual")
                print("      3. 📋 Verificar logs do último deploy")
        
        # Sempre sugerir verificação de build
        print("\n📋 VERIFICAÇÕES RECOMENDADAS:")
        print("   1. 🔍 Verificar se o build está gerando arquivos")
        print("   2. 📂 Confirmar se os arquivos estão no diretório correto")
        print("   3. 🔄 Executar deploy manual se necessário")
        
        # Instruções específicas
        print(f"\n🎯 COMANDOS ÚTEIS:")
        print("   Para forçar deploy: Vá ao dashboard → Deploy → Manual Deploy")
        print("   Para ver logs: Dashboard → Logs")

def main():
    """Função principal"""
    diagnostic = RenderDiagnostic()
    
    try:
        report = diagnostic.run_complete_diagnostic()
        
        print("\n✅ Diagnóstico finalizado!")
        print("📄 Relatório salvo: diagnostico_render_completo.json")
        
    except Exception as e:
        print(f"\n❌ Erro durante diagnóstico: {e}")

if __name__ == "__main__":
    main()