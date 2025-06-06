#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup do Stack de Monitoramento - TechZe Diagnostic Service
Configura Prometheus, Grafana e Alertmanager para monitoramento completo
"""
import os
import sys
import json
import subprocess
import time
import requests
from pathlib import Path

def print_status(message, status="INFO"):
    """Imprime mensagem com status colorido"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}{status}: {message}{colors['RESET']}")

def check_docker():
    """Verifica se Docker est√° dispon√≠vel"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_status("Docker encontrado", "SUCCESS")
            return True
        else:
            print_status("Docker n√£o encontrado", "ERROR")
            return False
    except FileNotFoundError:
        print_status("Docker n√£o est√° instalado", "ERROR")
        return False

def create_docker_compose():
    """Cria arquivo docker-compose.yml para o stack de monitoramento"""
    docker_compose_content = """
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: techze-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./alert_rules.yml:/etc/prometheus/alert_rules.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    restart: unless-stopped
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: techze-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=techze123
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-piechart-panel
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana_dashboards.json:/var/lib/grafana/dashboards/techze_dashboards.json
    restart: unless-stopped
    networks:
      - monitoring
    depends_on:
      - prometheus

  alertmanager:
    image: prom/alertmanager:latest
    container_name: techze-alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:9093'
    restart: unless-stopped
    networks:
      - monitoring

  redis:
    image: redis:alpine
    container_name: techze-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped
    networks:
      - monitoring

  redis-exporter:
    image: oliver006/redis_exporter:latest
    container_name: techze-redis-exporter
    ports:
      - "9121:9121"
    environment:
      - REDIS_ADDR=redis://redis:6379
    restart: unless-stopped
    networks:
      - monitoring
    depends_on:
      - redis

  node-exporter:
    image: prom/node-exporter:latest
    container_name: techze-node-exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:
  redis_data:

networks:
  monitoring:
    driver: bridge
"""
    
    with open('docker-compose.monitoring.yml', 'w') as f:
        f.write(docker_compose_content.strip())
    
    print_status("Arquivo docker-compose.monitoring.yml criado", "SUCCESS")

def create_alertmanager_config():
    """Cria configura√ß√£o do Alertmanager"""
    alertmanager_config = """
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@techze.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: 'critical-alerts'
  - match:
      severity: warning
    receiver: 'warning-alerts'

receivers:
- name: 'web.hook'
  webhook_configs:
  - url: 'http://localhost:8000/api/v1/alerts/webhook'
    send_resolved: true

- name: 'critical-alerts'
  webhook_configs:
  - url: 'http://localhost:8000/api/v1/alerts/webhook'
    send_resolved: true
  # Adicione configura√ß√µes de email/Slack aqui se necess√°rio
  # email_configs:
  # - to: 'admin@techze.com'
  #   subject: 'CRITICAL: {{ .GroupLabels.alertname }}'
  #   body: |
  #     {{ range .Alerts }}
  #     Alert: {{ .Annotations.summary }}
  #     Description: {{ .Annotations.description }}
  #     {{ end }}

- name: 'warning-alerts'
  webhook_configs:
  - url: 'http://localhost:8000/api/v1/alerts/webhook'
    send_resolved: true

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
"""
    
    with open('alertmanager.yml', 'w') as f:
        f.write(alertmanager_config.strip())
    
    print_status("Arquivo alertmanager.yml criado", "SUCCESS")

def setup_grafana_datasource():
    """Configura datasource do Prometheus no Grafana"""
    datasource_config = {
        "name": "Prometheus",
        "type": "prometheus",
        "url": "http://prometheus:9090",
        "access": "proxy",
        "isDefault": True
    }
    
    # Aguarda Grafana estar dispon√≠vel
    print_status("Aguardando Grafana inicializar...", "INFO")
    for i in range(30):
        try:
            response = requests.get("http://localhost:3000/api/health")
            if response.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(2)
    else:
        print_status("Timeout aguardando Grafana", "ERROR")
        return False
    
    # Configura datasource
    try:
        response = requests.post(
            "http://localhost:3000/api/datasources",
            json=datasource_config,
            auth=("admin", "techze123"),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 409]:  # 409 = j√° existe
            print_status("Datasource Prometheus configurado no Grafana", "SUCCESS")
            return True
        else:
            print_status(f"Erro ao configurar datasource: {response.text}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Erro ao conectar com Grafana: {e}", "ERROR")
        return False

def import_grafana_dashboards():
    """Importa dashboards do Grafana"""
    try:
        with open('grafana_dashboards.json', 'r') as f:
            dashboards = json.load(f)
        
        for dashboard_name, dashboard_config in dashboards.items():
            try:
                response = requests.post(
                    "http://localhost:3000/api/dashboards/db",
                    json=dashboard_config,
                    auth=("admin", "techze123"),
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print_status(f"Dashboard '{dashboard_name}' importado", "SUCCESS")
                else:
                    print_status(f"Erro ao importar dashboard '{dashboard_name}': {response.text}", "WARNING")
            except Exception as e:
                print_status(f"Erro ao importar dashboard '{dashboard_name}': {e}", "ERROR")
        
        return True
    except Exception as e:
        print_status(f"Erro ao ler dashboards: {e}", "ERROR")
        return False

def start_monitoring_stack():
    """Inicia o stack de monitoramento"""
    try:
        print_status("Iniciando stack de monitoramento...", "INFO")
        
        # Para containers existentes
        subprocess.run(['docker-compose', '-f', 'docker-compose.monitoring.yml', 'down'], 
                      capture_output=True)
        
        # Inicia novos containers
        result = subprocess.run(['docker-compose', '-f', 'docker-compose.monitoring.yml', 'up', '-d'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print_status("Stack de monitoramento iniciado", "SUCCESS")
            return True
        else:
            print_status(f"Erro ao iniciar stack: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Erro ao executar docker-compose: {e}", "ERROR")
        return False

def verify_services():
    """Verifica se todos os servi√ßos est√£o funcionando"""
    services = {
        "Prometheus": "http://localhost:9090/-/healthy",
        "Grafana": "http://localhost:3000/api/health",
        "Alertmanager": "http://localhost:9093/-/healthy",
        "Redis": "http://localhost:6379"  # Ser√° verificado diferente
    }
    
    print_status("Verificando servi√ßos...", "INFO")
    
    for service, url in services.items():
        if service == "Redis":
            # Verifica Redis via container
            try:
                result = subprocess.run(['docker', 'exec', 'techze-redis', 'redis-cli', 'ping'], 
                                      capture_output=True, text=True)
                if result.returncode == 0 and 'PONG' in result.stdout:
                    print_status(f"‚úÖ {service} est√° funcionando", "SUCCESS")
                else:
                    print_status(f"‚ùå {service} n√£o est√° respondendo", "ERROR")
            except Exception as e:
                print_status(f"‚ùå Erro ao verificar {service}: {e}", "ERROR")
        else:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print_status(f"‚úÖ {service} est√° funcionando", "SUCCESS")
                else:
                    print_status(f"‚ùå {service} retornou status {response.status_code}", "WARNING")
            except Exception as e:
                print_status(f"‚ùå {service} n√£o est√° acess√≠vel: {e}", "ERROR")

def print_access_info():
    """Imprime informa√ß√µes de acesso aos servi√ßos"""
    print_status("\n" + "="*60, "INFO")
    print_status("STACK DE MONITORAMENTO CONFIGURADO COM SUCESSO!", "SUCCESS")
    print_status("="*60, "INFO")
    print_status("", "INFO")
    print_status("üîó URLs de Acesso:", "INFO")
    print_status("", "INFO")
    print_status("üìä Grafana: http://localhost:3000", "INFO")
    print_status("   Usu√°rio: admin", "INFO")
    print_status("   Senha: techze123", "INFO")
    print_status("", "INFO")
    print_status("üìà Prometheus: http://localhost:9090", "INFO")
    print_status("üö® Alertmanager: http://localhost:9093", "INFO")
    print_status("üî¥ Redis: localhost:6379", "INFO")
    print_status("", "INFO")
    print_status("üìã Dashboards Dispon√≠veis:", "INFO")
    print_status("   ‚Ä¢ TechZe - Dashboard Operacional", "INFO")
    print_status("   ‚Ä¢ TechZe - Dashboard de Seguran√ßa", "INFO")
    print_status("   ‚Ä¢ TechZe - Dashboard de Neg√≥cio", "INFO")
    print_status("", "INFO")
    print_status("üîß Para parar o stack:", "INFO")
    print_status("   docker-compose -f docker-compose.monitoring.yml down", "INFO")
    print_status("", "INFO")
    print_status("="*60, "INFO")

def main():
    """Fun√ß√£o principal"""
    print_status("üöÄ Configurando Stack de Monitoramento TechZe", "INFO")
    print_status("", "INFO")
    
    # Verifica Docker
    if not check_docker():
        print_status("Docker √© necess√°rio para executar o stack de monitoramento", "ERROR")
        sys.exit(1)
    
    # Cria arquivos de configura√ß√£o
    print_status("Criando arquivos de configura√ß√£o...", "INFO")
    create_docker_compose()
    create_alertmanager_config()
    
    # Verifica se arquivos necess√°rios existem
    required_files = ['prometheus.yml', 'alert_rules.yml', 'grafana_dashboards.json']
    for file in required_files:
        if not os.path.exists(file):
            print_status(f"Arquivo necess√°rio n√£o encontrado: {file}", "ERROR")
            sys.exit(1)
    
    # Inicia stack
    if not start_monitoring_stack():
        print_status("Falha ao iniciar stack de monitoramento", "ERROR")
        sys.exit(1)
    
    # Aguarda servi√ßos iniciarem
    print_status("Aguardando servi√ßos iniciarem...", "INFO")
    time.sleep(30)
    
    # Verifica servi√ßos
    verify_services()
    
    # Configura Grafana
    print_status("Configurando Grafana...", "INFO")
    if setup_grafana_datasource():
        time.sleep(5)
        import_grafana_dashboards()
    
    # Imprime informa√ß√µes de acesso
    print_access_info()

if __name__ == "__main__":
    main()