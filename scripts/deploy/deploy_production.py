#!/usr/bin/env python3
"""
Script de Deploy para Produção - TechZe Diagnóstico
Agente CURSOR - Automação Completa
Integrado com sistema existente Render
"""

import os
import sys
import subprocess
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deploy.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ProductionDeployer:
    """Gerenciador de deploy integrado para produção"""
    
    def __init__(self):
        self.config = {
            "app_name": "techze-diagnostico",
            "version": self.get_version(),
            "environment": "production",
            "render_service_id": os.getenv("RENDER_SERVICE_ID"),
            "render_api_key": os.getenv("RENDER_API_KEY"),
            "health_check_url": "https://techze-diagnostico.onrender.com/health",
            "backup_retention_days": 7,
            "deploy_timeout": 900  # 15 minutos
        }
        
    def get_version(self) -> str:
        """Obter versão do git"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except:
            return "unknown"
    
    def pre_deploy_checks(self) -> bool:
        """Verificações pré-deploy usando sistema existente"""
        logger.info("🔍 Executando verificações pré-deploy...")
        
        checks = [
            ("Git status", self.check_git_status),
            ("Tests passing", self.run_tests),
            ("Render status", self.check_render_status),
            ("Dependencies", self.check_dependencies)
        ]
        
        for check_name, check_func in checks:
            logger.info(f"Verificando: {check_name}")
            if not check_func():
                logger.error(f"❌ Falha na verificação: {check_name}")
                return False
            logger.info(f"✅ {check_name} OK")
        
        return True
    
    def check_git_status(self) -> bool:
        """Verificar status do git"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=True
            )
            return len(result.stdout.strip()) == 0
        except:
            return False
    
    def run_tests(self) -> bool:
        """Executar todos os testes existentes"""
        try:
            # Usar sistema de testes implementado nas Semanas 1-2
            logger.info("Executando testes do CURSOR...")
            
            test_script = "microservices/diagnostic_service/tests/integration/test_complete_suite.py"
            result = subprocess.run(
                ["python", test_script],
                capture_output=True,
                text=True,
                cwd="."
            )
            
            return result.returncode == 0
            
        except Exception as e:
            logger.error(f"Erro ao executar testes: {e}")
            return False
    
    def check_render_status(self) -> bool:
        """Verificar status do serviço Render"""
        if not self.config["render_api_key"]:
            logger.warning("API key do Render não configurada")
            return True
        
        try:
            headers = {"Authorization": f"Bearer {self.config['render_api_key']}"}
            response = requests.get(
                f"https://api.render.com/v1/services/{self.config['render_service_id']}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                service_data = response.json()
                status = service_data.get("service", {}).get("status")
                return status in ["available", "running"]
            
            return False
            
        except Exception as e:
            logger.error(f"Erro ao verificar Render: {e}")
            return False
    
    def check_dependencies(self) -> bool:
        """Verificar dependências"""
        try:
            # Verificar Python dependencies
            result = subprocess.run(
                ["python", "-m", "pip", "check"],
                cwd="microservices/diagnostic_service",
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False
    
    def deploy_to_render(self) -> bool:
        """Deploy usando API do Render"""
        logger.info("🚀 Iniciando deploy no Render...")
        
        if not self.config["render_api_key"]:
            logger.error("API key do Render não configurada")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.config['render_api_key']}",
                "Content-Type": "application/json"
            }
            
            # Trigger deploy
            response = requests.post(
                f"https://api.render.com/v1/services/{self.config['render_service_id']}/deploys",
                headers=headers,
                json={"clearCache": True},
                timeout=30
            )
            
            if response.status_code == 201:
                deploy_data = response.json()
                deploy_id = deploy_data.get("deploy", {}).get("id")
                
                logger.info(f"Deploy iniciado: {deploy_id}")
                
                # Monitorar progresso
                return self.monitor_deploy_progress(deploy_id)
            else:
                logger.error(f"Falha ao iniciar deploy: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erro no deploy Render: {e}")
            return False
    
    def monitor_deploy_progress(self, deploy_id: str) -> bool:
        """Monitorar progresso do deploy"""
        logger.info("📊 Monitorando progresso do deploy...")
        
        headers = {"Authorization": f"Bearer {self.config['render_api_key']}"}
        start_time = time.time()
        
        while time.time() - start_time < self.config["deploy_timeout"]:
            try:
                response = requests.get(
                    f"https://api.render.com/v1/deploys/{deploy_id}",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    deploy_data = response.json()
                    status = deploy_data.get("deploy", {}).get("status")
                    
                    logger.info(f"Status do deploy: {status}")
                    
                    if status == "live":
                        logger.info("✅ Deploy concluído com sucesso!")
                        return True
                    elif status in ["build_failed", "deploy_failed"]:
                        logger.error(f"❌ Deploy falhou: {status}")
                        return False
                    
                time.sleep(30)  # Aguardar 30 segundos
                
            except Exception as e:
                logger.error(f"Erro ao monitorar deploy: {e}")
                time.sleep(30)
        
        logger.error("❌ Timeout no deploy")
        return False
    
    def health_check(self) -> bool:
        """Verificação de saúde pós-deploy"""
        logger.info("🔍 Executando health check...")
        
        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                response = requests.get(
                    self.config["health_check_url"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info("✅ Health check passou!")
                    return True
                    
            except Exception as e:
                logger.debug(f"Health check tentativa {attempt + 1}: {e}")
                
            time.sleep(30)
        
        logger.error("❌ Health check falhou!")
        return False
    
    def run_integration_tests(self) -> bool:
        """Executar testes de integração pós-deploy"""
        logger.info("🧪 Executando testes de integração...")
        
        try:
            # Usar scripts existentes
            test_scripts = [
                "microservices/diagnostic_service/tests/integration/test_frontend_api_calls.py",
                "microservices/diagnostic_service/tests/integration/test_performance_validation.py"
            ]
            
            for script in test_scripts:
                if os.path.exists(script):
                    result = subprocess.run(
                        ["python", script],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    if result.returncode != 0:
                        logger.error(f"Teste falhou: {script}")
                        return False
            
            logger.info("✅ Testes de integração passaram!")
            return True
            
        except Exception as e:
            logger.error(f"Erro nos testes de integração: {e}")
            return False
    
    def generate_deploy_report(self, success: bool):
        """Gerar relatório do deploy"""
        report = {
            "deploy_id": f"deploy_{int(time.time())}",
            "version": self.config["version"],
            "timestamp": datetime.now().isoformat(),
            "status": "success" if success else "failed",
            "environment": self.config["environment"],
            "health_check_url": self.config["health_check_url"]
        }
        
        report_file = f"reports/deploy_report_{self.config['version']}.json"
        os.makedirs("reports", exist_ok=True)
        
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Relatório gerado: {report_file}")
        return report
    
    def send_notification(self, success: bool, report: Dict[str, Any]):
        """Enviar notificação do resultado"""
        status_emoji = "🎉" if success else "❌"
        status_text = "SUCESSO" if success else "FALHA"
        
        message = f"""
        {status_emoji} Deploy {status_text}
        
        Versão: {report['version']}
        Ambiente: {report['environment']}
        Timestamp: {report['timestamp']}
        URL: {report['health_check_url']}
        """
        
        logger.info(message)
        
        # Aqui poderia integrar com Slack, Discord, etc.
        webhook_url = os.getenv("DEPLOY_WEBHOOK_URL")
        if webhook_url:
            try:
                payload = {
                    "text": message,
                    "status": "success" if success else "error",
                    "details": report
                }
                requests.post(webhook_url, json=payload, timeout=10)
            except:
                pass
    
    def run(self) -> bool:
        """Executar deploy completo"""
        logger.info(f"🚀 Iniciando deploy v{self.config['version']} para {self.config['environment']}")
        
        try:
            # Verificações pré-deploy
            if not self.pre_deploy_checks():
                logger.error("❌ Verificações pré-deploy falharam")
                return False
            
            # Deploy no Render
            if not self.deploy_to_render():
                logger.error("❌ Deploy no Render falhou")
                return False
            
            # Health check
            if not self.health_check():
                logger.error("❌ Health check falhou")
                return False
            
            # Testes de integração
            if not self.run_integration_tests():
                logger.warning("⚠️ Alguns testes de integração falharam")
            
            # Gerar relatório e notificar
            report = self.generate_deploy_report(True)
            self.send_notification(True, report)
            
            logger.info("🎉 Deploy concluído com sucesso!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro durante deploy: {e}")
            report = self.generate_deploy_report(False)
            self.send_notification(False, report)
            return False


def main():
    """Função principal"""
    deployer = ProductionDeployer()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--dry-run":
        logger.info("🧪 Modo dry-run - apenas verificações")
        success = deployer.pre_deploy_checks()
    else:
        success = deployer.run()
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main() 