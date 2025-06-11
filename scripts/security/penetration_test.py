#!/usr/bin/env python3
"""
Sistema Avançado de Testes de Penetração - TechZe Diagnóstico
Agente CURSOR - Testes de Segurança com OWASP ZAP e Ferramentas Avançadas
"""

import os
import json
import time
import requests
import subprocess
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityVulnerability:
    """Estrutura de dados para vulnerabilidades de segurança"""
    id: str
    name: str
    description: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    confidence: str  # LOW, MEDIUM, HIGH
    url: str
    method: str
    parameter: str
    attack: str
    evidence: str
    solution: str
    cwe_id: Optional[int] = None
    wasc_id: Optional[int] = None

@dataclass
class PenetrationTestResult:
    """Resultado completo de teste de penetração"""
    test_id: str
    timestamp: datetime
    target_url: str
    test_duration: int  # segundos
    total_vulnerabilities: int
    vulnerabilities_by_severity: Dict[str, int]
    vulnerabilities: List[SecurityVulnerability]
    coverage_percentage: float
    test_type: str  # active, passive, baseline
    status: str  # completed, failed, aborted

class OWASPZAPController:
    """Controlador para OWASP ZAP Proxy"""
    
    def __init__(self, zap_port: int = 8080, zap_host: str = "localhost"):
        self.zap_port = zap_port
        self.zap_host = zap_host
        self.zap_url = f"http://{zap_host}:{zap_port}"
        self.api_key = os.getenv("ZAP_API_KEY", "")
        self.zap_process = None
    
    def start_zap(self, headless: bool = True) -> bool:
        """Iniciar OWASP ZAP daemon"""
        try:
            logger.info("Iniciando OWASP ZAP...")
            
            # Verificar se ZAP já está rodando
            if self._is_zap_running():
                logger.info("ZAP já está em execução")
                return True
            
            # Comando para iniciar ZAP
            cmd = [
                "zap.sh", "-daemon",
                "-port", str(self.zap_port),
                "-config", "api.disablekey=true"
            ]
            
            if headless:
                cmd.append("-nogui")
            
            # Iniciar processo ZAP
            self.zap_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Aguardar ZAP ficar pronto
            for i in range(30):  # 30 segundos timeout
                if self._is_zap_running():
                    logger.info("ZAP iniciado com sucesso")
                    return True
                time.sleep(1)
            
            logger.error("Timeout ao iniciar ZAP")
            return False
            
        except Exception as e:
            logger.error(f"Erro ao iniciar ZAP: {e}")
            return False
    
    def stop_zap(self):
        """Parar OWASP ZAP"""
        try:
            if self.zap_process:
                self.zap_process.terminate()
                self.zap_process.wait(timeout=10)
                logger.info("ZAP finalizado")
        except Exception as e:
            logger.error(f"Erro ao finalizar ZAP: {e}")
    
    def _is_zap_running(self) -> bool:
        """Verificar se ZAP está rodando"""
        try:
            response = requests.get(f"{self.zap_url}/JSON/core/view/version/", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _make_zap_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Fazer requisição para API do ZAP"""
        try:
            full_url = f"{self.zap_url}{endpoint}"
            response = requests.get(full_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Erro na requisição ZAP: {e}")
            return {}

class SecurityScanner:
    """Scanner de segurança principal"""
    
    def __init__(self):
        self.zap = OWASPZAPController()
        self.results_dir = "reports/security"
        os.makedirs(self.results_dir, exist_ok=True)
    
    def run_baseline_scan(self, target_url: str) -> PenetrationTestResult:
        """Executar scan básico de linha de base"""
        logger.info(f"Iniciando baseline scan para: {target_url}")
        
        test_id = f"baseline_{int(time.time())}"
        start_time = datetime.now()
        
        if not self.zap.start_zap():
            raise Exception("Falha ao iniciar ZAP")
        
        try:
            # 1. Configurar contexto
            self._setup_context(target_url)
            
            # 2. Spider passivo
            spider_results = self._run_spider(target_url)
            
            # 3. Scan passivo
            passive_results = self._run_passive_scan(target_url)
            
            # 4. Coleta de resultados
            vulnerabilities = self._collect_vulnerabilities()
            
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds())
            
            result = PenetrationTestResult(
                test_id=test_id,
                timestamp=start_time,
                target_url=target_url,
                test_duration=duration,
                total_vulnerabilities=len(vulnerabilities),
                vulnerabilities_by_severity=self._count_by_severity(vulnerabilities),
                vulnerabilities=vulnerabilities,
                coverage_percentage=spider_results.get("coverage", 0),
                test_type="baseline",
                status="completed"
            )
            
            # Salvar resultados
            self._save_results(result)
            
            return result
            
        finally:
            self.zap.stop_zap()
    
    def run_full_scan(self, target_url: str, authenticated: bool = False) -> PenetrationTestResult:
        """Executar scan completo (ativo + passivo)"""
        logger.info(f"Iniciando full scan para: {target_url}")
        
        test_id = f"full_{int(time.time())}"
        start_time = datetime.now()
        
        if not self.zap.start_zap():
            raise Exception("Falha ao iniciar ZAP")
        
        try:
            # 1. Configurar contexto
            self._setup_context(target_url)
            
            # 2. Autenticação (se necessário)
            if authenticated:
                self._setup_authentication(target_url)
            
            # 3. Spider completo
            spider_results = self._run_spider(target_url, aggressive=True)
            
            # 4. Scan ativo
            active_results = self._run_active_scan(target_url)
            
            # 5. Scan passivo
            passive_results = self._run_passive_scan(target_url)
            
            # 6. Coleta de resultados
            vulnerabilities = self._collect_vulnerabilities()
            
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds())
            
            result = PenetrationTestResult(
                test_id=test_id,
                timestamp=start_time,
                target_url=target_url,
                test_duration=duration,
                total_vulnerabilities=len(vulnerabilities),
                vulnerabilities_by_severity=self._count_by_severity(vulnerabilities),
                vulnerabilities=vulnerabilities,
                coverage_percentage=spider_results.get("coverage", 0),
                test_type="full_active",
                status="completed"
            )
            
            # Salvar resultados
            self._save_results(result)
            
            return result
            
        finally:
            self.zap.stop_zap()
    
    def _setup_context(self, target_url: str):
        """Configurar contexto de scan"""
        logger.info("Configurando contexto ZAP...")
        
        # Criar contexto
        context_name = "TechZe_Context"
        self.zap._make_zap_request(
            "/JSON/context/action/newContext/",
            {"contextName": context_name}
        )
        
        # Adicionar URL ao contexto
        self.zap._make_zap_request(
            "/JSON/context/action/includeInContext/",
            {"contextName": context_name, "regex": f"{target_url}.*"}
        )
    
    def _setup_authentication(self, target_url: str):
        """Configurar autenticação para testes"""
        logger.info("Configurando autenticação...")
        
        # Configurar autenticação baseada em form
        auth_config = {
            "contextId": "0",
            "authMethodName": "formBasedAuthentication",
            "authMethodConfigParams": f"loginUrl={target_url}/login&loginRequestData=username%3D%7B%25username%25%7D%26password%3D%7B%25password%25%7D"
        }
        
        self.zap._make_zap_request(
            "/JSON/authentication/action/setAuthenticationMethod/",
            auth_config
        )
        
        # Adicionar usuário de teste
        test_user = {
            "contextId": "0",
            "name": "test_user",
            "authCredentialsConfigParams": "username=test@techze.com&password=testpass"
        }
        
        self.zap._make_zap_request(
            "/JSON/users/action/newUser/",
            test_user
        )
    
    def _run_spider(self, target_url: str, aggressive: bool = False) -> Dict:
        """Executar spider para descoberta de URLs"""
        logger.info("Executando spider...")
        
        # Iniciar spider
        spider_params = {
            "url": target_url,
            "maxChildren": "10" if not aggressive else "50",
            "recurse": "true",
            "contextName": "TechZe_Context"
        }
        
        spider_response = self.zap._make_zap_request(
            "/JSON/spider/action/scan/",
            spider_params
        )
        
        spider_id = spider_response.get("scan", "0")
        
        # Aguardar conclusão
        while True:
            status = self.zap._make_zap_request(
                "/JSON/spider/view/status/",
                {"scanId": spider_id}
            )
            
            progress = int(status.get("status", "0"))
            logger.info(f"Spider progress: {progress}%")
            
            if progress >= 100:
                break
            
            time.sleep(2)
        
        # Obter resultados
        results = self.zap._make_zap_request("/JSON/spider/view/results/", {"scanId": spider_id})
        
        return {
            "urls_found": len(results.get("results", [])),
            "coverage": min(100, len(results.get("results", [])) * 2)  # Estimativa
        }
    
    def _run_active_scan(self, target_url: str) -> Dict:
        """Executar scan ativo para encontrar vulnerabilidades"""
        logger.info("Executando scan ativo...")
        
        # Iniciar scan ativo
        scan_response = self.zap._make_zap_request(
            "/JSON/ascan/action/scan/",
            {
                "url": target_url,
                "recurse": "true",
                "inScopeOnly": "false",
                "scanPolicyName": "",
                "method": "",
                "postData": "",
                "contextId": "0"
            }
        )
        
        scan_id = scan_response.get("scan", "0")
        
        # Aguardar conclusão
        while True:
            status = self.zap._make_zap_request(
                "/JSON/ascan/view/status/",
                {"scanId": scan_id}
            )
            
            progress = int(status.get("status", "0"))
            logger.info(f"Active scan progress: {progress}%")
            
            if progress >= 100:
                break
            
            time.sleep(5)
        
        return {"scan_id": scan_id, "status": "completed"}
    
    def _run_passive_scan(self, target_url: str) -> Dict:
        """Executar scan passivo"""
        logger.info("Executando scan passivo...")
        
        # Aguardar scan passivo completar
        while True:
            records = self.zap._make_zap_request("/JSON/pscan/view/recordsToScan/")
            
            remaining = int(records.get("recordsToScan", "0"))
            logger.info(f"Passive scan records remaining: {remaining}")
            
            if remaining == 0:
                break
            
            time.sleep(2)
        
        return {"status": "completed"}
    
    def _collect_vulnerabilities(self) -> List[SecurityVulnerability]:
        """Coletar todas as vulnerabilidades encontradas"""
        logger.info("Coletando vulnerabilidades...")
        
        vulnerabilities = []
        
        # Obter alertas do ZAP
        alerts_response = self.zap._make_zap_request("/JSON/core/view/alerts/")
        alerts = alerts_response.get("alerts", [])
        
        for alert in alerts:
            vuln = SecurityVulnerability(
                id=str(alert.get("id", "")),
                name=alert.get("name", ""),
                description=alert.get("description", ""),
                severity=alert.get("risk", "LOW").upper(),
                confidence=alert.get("confidence", "LOW").upper(),
                url=alert.get("url", ""),
                method=alert.get("method", ""),
                parameter=alert.get("param", ""),
                attack=alert.get("attack", ""),
                evidence=alert.get("evidence", ""),
                solution=alert.get("solution", ""),
                cwe_id=int(alert.get("cweid", 0)) if alert.get("cweid") else None,
                wasc_id=int(alert.get("wascid", 0)) if alert.get("wascid") else None
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _count_by_severity(self, vulnerabilities: List[SecurityVulnerability]) -> Dict[str, int]:
        """Contar vulnerabilidades por severidade"""
        counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        
        for vuln in vulnerabilities:
            severity = vuln.severity.upper()
            if severity in counts:
                counts[severity] += 1
        
        return counts
    
    def _save_results(self, result: PenetrationTestResult):
        """Salvar resultados em múltiplos formatos"""
        timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Salvar JSON
        json_file = f"{self.results_dir}/pentest_{result.test_id}_{timestamp}.json"
        with open(json_file, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        
        # Salvar relatório HTML
        html_file = f"{self.results_dir}/pentest_{result.test_id}_{timestamp}.html"
        self._generate_html_report(result, html_file)
        
        logger.info(f"Resultados salvos: {json_file}, {html_file}")
    
    def _generate_html_report(self, result: PenetrationTestResult, output_path: str):
        """Gerar relatório HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TechZe - Relatório de Teste de Penetração</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #dc3545; color: white; padding: 20px; border-radius: 8px; }}
                .summary {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .vulnerability {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #dc3545; }}
                .critical {{ border-left-color: #dc3545; }}
                .high {{ border-left-color: #fd7e14; }}
                .medium {{ border-left-color: #ffc107; }}
                .low {{ border-left-color: #28a745; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🔒 TechZe Diagnóstico - Relatório de Segurança</h1>
                <p>Teste ID: {result.test_id}</p>
                <p>Data: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>URL Testada: {result.target_url}</p>
            </div>
            
            <div class="summary">
                <h2>📊 Resumo Executivo</h2>
                <p><strong>Duração do Teste:</strong> {result.test_duration} segundos</p>
                <p><strong>Tipo de Teste:</strong> {result.test_type}</p>
                <p><strong>Total de Vulnerabilidades:</strong> {result.total_vulnerabilities}</p>
                
                <h3>Vulnerabilidades por Severidade:</h3>
                <table>
                    <tr><th>Severidade</th><th>Quantidade</th></tr>
                    <tr><td>🔴 Crítica</td><td>{result.vulnerabilities_by_severity.get('CRITICAL', 0)}</td></tr>
                    <tr><td>🟠 Alta</td><td>{result.vulnerabilities_by_severity.get('HIGH', 0)}</td></tr>
                    <tr><td>🟡 Média</td><td>{result.vulnerabilities_by_severity.get('MEDIUM', 0)}</td></tr>
                    <tr><td>🟢 Baixa</td><td>{result.vulnerabilities_by_severity.get('LOW', 0)}</td></tr>
                </table>
            </div>
            
            <div class="vulnerabilities">
                <h2>🚨 Vulnerabilidades Detectadas</h2>
        """
        
        # Adicionar vulnerabilidades
        for vuln in result.vulnerabilities:
            severity_class = vuln.severity.lower()
            html_content += f"""
                <div class="vulnerability {severity_class}">
                    <h3>{vuln.name} ({vuln.severity})</h3>
                    <p><strong>URL:</strong> {vuln.url}</p>
                    <p><strong>Método:</strong> {vuln.method}</p>
                    <p><strong>Parâmetro:</strong> {vuln.parameter}</p>
                    <p><strong>Descrição:</strong> {vuln.description}</p>
                    <p><strong>Solução:</strong> {vuln.solution}</p>
                    {f'<p><strong>CWE:</strong> {vuln.cwe_id}</p>' if vuln.cwe_id else ''}
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

class ContinuousSecurityMonitor:
    """Monitor contínuo de segurança"""
    
    def __init__(self):
        self.scanner = SecurityScanner()
        self.monitoring = False
        self.scan_interval = 3600  # 1 hora
        
    def start_monitoring(self, target_url: str):
        """Iniciar monitoramento contínuo"""
        self.monitoring = True
        
        def monitor_loop():
            while self.monitoring:
                try:
                    logger.info("Executando scan de segurança agendado...")
                    result = self.scanner.run_baseline_scan(target_url)
                    
                    # Verificar se há vulnerabilidades críticas
                    critical_count = result.vulnerabilities_by_severity.get('CRITICAL', 0)
                    high_count = result.vulnerabilities_by_severity.get('HIGH', 0)
                    
                    if critical_count > 0 or high_count > 5:
                        self._send_security_alert(result)
                    
                    time.sleep(self.scan_interval)
                    
                except Exception as e:
                    logger.error(f"Erro no monitoramento de segurança: {e}")
                    time.sleep(300)  # 5 minutos em caso de erro
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        logger.info("Monitoramento de segurança iniciado")
    
    def stop_monitoring(self):
        """Parar monitoramento"""
        self.monitoring = False
        logger.info("Monitoramento de segurança parado")
    
    def _send_security_alert(self, result: PenetrationTestResult):
        """Enviar alerta de segurança"""
        critical = result.vulnerabilities_by_severity.get('CRITICAL', 0)
        high = result.vulnerabilities_by_severity.get('HIGH', 0)
        
        alert_message = f"""
🚨 ALERTA DE SEGURANÇA - TechZe Diagnóstico

📊 Vulnerabilidades Detectadas:
• Críticas: {critical}
• Altas: {high}
• Total: {result.total_vulnerabilities}

🎯 URL: {result.target_url}
⏰ Detectado em: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

🔥 AÇÃO NECESSÁRIA: Revisão imediata de segurança requerida!
        """
        
        logger.warning(alert_message)
        
        # Aqui você pode integrar com Slack, email, etc.
        # slack_webhook = os.getenv("SLACK_SECURITY_WEBHOOK")
        # if slack_webhook:
        #     requests.post(slack_webhook, json={"text": alert_message})


def main():
    """Função principal para executar testes de penetração"""
    import argparse
    
    parser = argparse.ArgumentParser(description="TechZe Security Testing Tool")
    parser.add_argument("--url", required=True, help="URL alvo para teste")
    parser.add_argument("--type", choices=["baseline", "full"], default="baseline", help="Tipo de teste")
    parser.add_argument("--monitor", action="store_true", help="Iniciar monitoramento contínuo")
    
    args = parser.parse_args()
    
    scanner = SecurityScanner()
    
    try:
        if args.monitor:
            monitor = ContinuousSecurityMonitor()
            monitor.start_monitoring(args.url)
            logger.info("Monitoramento iniciado. Pressione Ctrl+C para parar.")
            
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                monitor.stop_monitoring()
                logger.info("Monitoramento finalizado")
        
        else:
            if args.type == "baseline":
                result = scanner.run_baseline_scan(args.url)
            else:
                result = scanner.run_full_scan(args.url)
            
            # Exibir resumo
            print("\n" + "="*60)
            print("🔒 RELATÓRIO DE SEGURANÇA - TECHZE DIAGNÓSTICO")
            print("="*60)
            print(f"URL Testada: {result.target_url}")
            print(f"Duração: {result.test_duration}s")
            print(f"Total de Vulnerabilidades: {result.total_vulnerabilities}")
            print(f"Críticas: {result.vulnerabilities_by_severity.get('CRITICAL', 0)}")
            print(f"Altas: {result.vulnerabilities_by_severity.get('HIGH', 0)}")
            print(f"Médias: {result.vulnerabilities_by_severity.get('MEDIUM', 0)}")
            print(f"Baixas: {result.vulnerabilities_by_severity.get('LOW', 0)}")
            print("="*60)
            
            # Avaliar resultado
            critical = result.vulnerabilities_by_severity.get('CRITICAL', 0)
            high = result.vulnerabilities_by_severity.get('HIGH', 0)
            
            if critical > 0:
                print("🔴 STATUS: CRÍTICO - Vulnerabilidades críticas encontradas!")
                return 1
            elif high > 5:
                print("🟠 STATUS: ALTO RISCO - Muitas vulnerabilidades de alto risco!")
                return 1
            else:
                print("🟢 STATUS: APROVADO - Nível de segurança aceitável")
                return 0
    
    except Exception as e:
        logger.error(f"Erro durante teste de segurança: {e}")
        return 1


if __name__ == "__main__":
    exit(main()) 