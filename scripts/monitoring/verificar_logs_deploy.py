#!/usr/bin/env python3
"""
Verificação de Logs do Deploy Render
TechZe Diagnóstico - Análise de Logs para Debug
"""

import requests
import json
from datetime import datetime

class RenderLogChecker:
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
        
    def get_latest_deploy_logs(self):
        """Obtém logs do último deploy"""
        self.log("📋 Buscando último deploy...")
        
        try:
            # Primeiro, obter lista de deploys
            response = requests.get(
                f"https://api.render.com/v1/services/{self.frontend_service_id}/deploys",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code != 200:
                self.log(f"❌ Erro ao obter deploys: {response.status_code}", "ERROR")
                return None
            
            deploys = response.json()
            if not deploys:
                self.log("❌ Nenhum deploy encontrado", "ERROR")
                return None
            
            latest_deploy = deploys[0]
            deploy_info = latest_deploy.get('deploy', latest_deploy)
            deploy_id = deploy_info.get('id')
            
            self.log(f"🎯 Último deploy: {deploy_id}")
            self.log(f"📊 Status: {deploy_info.get('status')}")
            self.log(f"⏰ Criado em: {deploy_info.get('createdAt')}")
            
            # Agora obter logs do deploy
            self.log("📄 Obtendo logs do deploy...")
            
            logs_response = requests.get(
                f"https://api.render.com/v1/services/{self.frontend_service_id}/deploys/{deploy_id}/logs",
                headers=self.headers,
                timeout=30
            )
            
            if logs_response.status_code == 200:
                return {
                    'deploy_info': deploy_info,
                    'logs': logs_response.text
                }
            else:
                self.log(f"❌ Erro ao obter logs: {logs_response.status_code}", "ERROR")
                return {
                    'deploy_info': deploy_info,
                    'logs': None
                }
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return None
    
    def analyze_build_logs(self, logs_text):
        """Analisa logs do build"""
        if not logs_text:
            self.log("❌ Logs não disponíveis", "ERROR")
            return []
        
        issues = []
        lines = logs_text.split('\n')
        
        # Procurar por indicadores de problemas
        build_started = False
        build_completed = False
        npm_install_ok = False
        vite_build_ok = False
        files_generated = False
        
        for line in lines:
            line_lower = line.lower()
            
            # Build iniciado
            if 'starting build' in line_lower or 'running build command' in line_lower:
                build_started = True
                
            # NPM install
            if 'npm install' in line_lower and 'added' in line_lower:
                npm_install_ok = True
                
            # Vite build
            if 'vite build' in line_lower and ('completed' in line_lower or 'built in' in line_lower):
                vite_build_ok = True
                
            # Arquivos gerados
            if 'dist/' in line and ('.html' in line or '.js' in line or '.css' in line):
                files_generated = True
                
            # Build concluído
            if 'build completed' in line_lower or 'build succeeded' in line_lower:
                build_completed = True
                
            # Erros
            if any(error in line_lower for error in ['error:', 'failed:', 'exception:', 'cannot resolve']):
                issues.append(f"❌ ERRO: {line.strip()}")
                
            # Warnings importantes
            if 'warn' in line_lower and any(warning in line_lower for warning in ['missing', 'not found', 'deprecated']):
                issues.append(f"⚠️ WARNING: {line.strip()}")
        
        # Verificações de fluxo
        if not build_started:
            issues.append("❌ Build não iniciou corretamente")
            
        if not npm_install_ok:
            issues.append("⚠️ NPM install pode não ter funcionado")
            
        if not vite_build_ok:
            issues.append("❌ Vite build não completou")
            
        if not files_generated:
            issues.append("❌ Arquivos não foram gerados na pasta dist/")
            
        if not build_completed:
            issues.append("❌ Build não foi finalizado")
        
        return issues
    
    def get_service_build_config(self):
        """Verifica configuração atual do build"""
        self.log("🔧 Verificando configuração atual...")
        
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
                
                config = {
                    "build_command": details.get('buildCommand', ''),
                    "publish_path": details.get('publishPath', ''),
                    "auto_deploy": details.get('autoDeploy', 'unknown'),
                    "root_dir": details.get('rootDir', ''),
                    "branch": details.get('branch', 'unknown')
                }
                
                return config
            else:
                self.log(f"❌ Erro ao obter configuração: {response.status_code}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"❌ Erro: {e}", "ERROR")
            return None
    
    def run_complete_analysis(self):
        """Executa análise completa"""
        self.log("🚀 INICIANDO ANÁLISE DE LOGS DO DEPLOY")
        self.log("="*60)
        
        # 1. Verificar configuração atual
        config = self.get_service_build_config()
        if config:
            self.log("📊 CONFIGURAÇÃO ATUAL:")
            for key, value in config.items():
                self.log(f"   {key}: '{value}'")
        
        # 2. Obter logs do último deploy
        deploy_data = self.get_latest_deploy_logs()
        
        if not deploy_data:
            self.log("❌ Não foi possível obter dados do deploy", "ERROR")
            return
        
        # 3. Analisar logs
        issues = []
        if deploy_data['logs']:
            issues = self.analyze_build_logs(deploy_data['logs'])
        
        # 4. Exibir resultados
        self.display_analysis_results(deploy_data, config, issues)
        
        # 5. Sugerir próximos passos
        self.suggest_next_steps(issues, deploy_data['deploy_info'])
        
        # 6. Salvar relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "deploy_info": deploy_data['deploy_info'],
            "config": config,
            "issues_found": issues,
            "logs_available": deploy_data['logs'] is not None,
            "logs_excerpt": deploy_data['logs'][-2000:] if deploy_data['logs'] else None  # Últimas 2000 chars
        }
        
        with open("analise_logs_deploy.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return report
    
    def display_analysis_results(self, deploy_data, config, issues):
        """Exibe resultados da análise"""
        
        print(f"\n{'='*60}")
        print("📊 ANÁLISE DOS LOGS DO DEPLOY")
        print(f"{'='*60}")
        
        deploy_info = deploy_data['deploy_info']
        
        print(f"\n🚀 INFORMAÇÕES DO DEPLOY:")
        print(f"   ID: {deploy_info.get('id')}")
        print(f"   Status: {deploy_info.get('status')}")
        print(f"   Criado: {deploy_info.get('createdAt')}")
        print(f"   Atualizado: {deploy_info.get('updatedAt')}")
        
        if config:
            print(f"\n🔧 CONFIGURAÇÃO DO BUILD:")
            print(f"   Build Command: '{config['build_command']}'")
            print(f"   Publish Path: '{config['publish_path']}'")
            print(f"   Auto Deploy: {config['auto_deploy']}")
            print(f"   Root Dir: '{config['root_dir']}'")
            print(f"   Branch: {config['branch']}")
        
        print(f"\n🔍 PROBLEMAS IDENTIFICADOS:")
        if issues:
            for issue in issues:
                print(f"   {issue}")
        else:
            print("   ✅ Nenhum problema detectado nos logs")
        
        # Mostrar amostra dos logs se disponível
        if deploy_data['logs']:
            lines = deploy_data['logs'].split('\n')
            if len(lines) > 50:
                print(f"\n📄 ÚLTIMAS LINHAS DOS LOGS:")
                for line in lines[-20:]:
                    if line.strip():
                        print(f"   {line}")
        
        print(f"\n{'='*60}")
    
    def suggest_next_steps(self, issues, deploy_info):
        """Sugere próximos passos"""
        
        print(f"\n🛠️ PRÓXIMOS PASSOS RECOMENDADOS:")
        
        if not issues:
            print("   🎯 Logs parecem OK. Possíveis causas do 404:")
            print("      1. 🕐 Aguardar 5-10 minutos (propagação)")
            print("      2. 🔄 Limpar cache do navegador")
            print("      3. 📂 Verificar se index.html foi gerado")
            print("      4. 🌐 Testar URL direta: https://techze-frontend-app.onrender.com")
        
        else:
            critical_issues = [i for i in issues if "❌" in i]
            
            if critical_issues:
                print("   🚨 AÇÕES URGENTES:")
                
                if any("vite build" in issue.lower() for issue in critical_issues):
                    print("      1. ✅ Verificar se package.json tem script 'build'")
                    print("      2. 🔧 Verificar se vite.config.ts está correto")
                
                if any("arquivos não foram gerados" in issue.lower() for issue in critical_issues):
                    print("      3. 📂 Verificar se build gera pasta 'dist/'")
                    print("      4. 🔄 Rodar build localmente para testar")
                
                if any("build não" in issue.lower() for issue in critical_issues):
                    print("      5. 📋 Verificar logs completos no dashboard")
                    print("      6. 🔄 Tentar deploy manual novamente")
        
        print(f"\n📋 COMANDOS ÚTEIS:")
        print("   Para ver logs completos: Dashboard → Logs")
        print("   Para novo deploy: Dashboard → Manual Deploy")
        print("   Para testar local: npm run build")

def main():
    """Função principal"""
    checker = RenderLogChecker()
    
    try:
        report = checker.run_complete_analysis()
        
        print("\n✅ Análise finalizada!")
        print("📄 Relatório salvo: analise_logs_deploy.json")
        
    except Exception as e:
        print(f"\n❌ Erro durante análise: {e}")

if __name__ == "__main__":
    main()