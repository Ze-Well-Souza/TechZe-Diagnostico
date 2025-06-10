#!/usr/bin/env python3
"""
📊 RENDER STATUS CHECK - Verificação de Status dos Serviços
Verifica o status atual dos deploys e serviços
"""

import requests
import json
import time
from datetime import datetime

# Configurações
RENDER_API_KEY = "rnd_Tj1JybEJij6A3UhouM7spm8LRbkX"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def log_step(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_services_with_deploys():
    """Listar serviços e seus últimos deploys"""
    log_step("🔍 Verificando status dos serviços...")
    
    response = requests.get(
        "https://api.render.com/v1/services",
        headers=headers
    )
    
    if response.status_code != 200:
        log_step(f"❌ Erro ao buscar serviços: {response.status_code}")
        return
    
    services = response.json()
    log_step(f"✅ Encontrados {len(services)} serviços")
    print()
    
    for service in services:
        srv = service['service']
        log_step(f"📋 {srv['name']} ({srv['type']})")
        log_step(f"   🆔 ID: {srv['id']}")
        
        # URLs do serviço
        if srv['type'] == 'static_site':
            details = srv['serviceDetails']
            log_step(f"   🌐 URL: {details.get('url', 'N/A')}")
        elif srv['type'] == 'web_service':
            details = srv['serviceDetails']
            log_step(f"   🌐 URL: {details.get('url', 'N/A')}")
        
        # Verificar último deploy
        deploy_response = requests.get(
            f"https://api.render.com/v1/services/{srv['id']}/deploys?limit=1",
            headers=headers
        )
        
        if deploy_response.status_code == 200:
            deploys = deploy_response.json()
            if deploys:
                latest_deploy = deploys[0]['deploy']
                status = latest_deploy['status']
                created_at = latest_deploy['createdAt']
                
                status_emoji = {
                    'live': '✅',
                    'build_in_progress': '🔄',
                    'build_failed': '❌',
                    'pre_deploy_in_progress': '⏳',
                    'pre_deploy_failed': '❌',
                    'update_failed': '❌',
                    'canceled': '⚠️'
                }.get(status, '❓')
                
                log_step(f"   {status_emoji} Deploy: {status}")
                log_step(f"   🕐 Criado: {created_at}")
                
                # Se estiver em progresso, mostrar detalhes
                if 'in_progress' in status:
                    log_step(f"   ⏳ Deploy em andamento...")
        
        # Verificar domínios customizados
        domains_response = requests.get(
            f"https://api.render.com/v1/services/{srv['id']}/custom-domains",
            headers=headers
        )
        
        if domains_response.status_code == 200:
            domains = domains_response.json()
            if domains:
                log_step(f"   🌐 Domínios customizados:")
                for domain in domains:
                    domain_name = domain['customDomain']['name']
                    verification_status = domain['customDomain'].get('verificationStatus', 'unknown')
                    log_step(f"      • {domain_name} - {verification_status}")
        
        print()

def test_urls():
    """Testar URLs principais"""
    log_step("🌐 Testando URLs...")
    
    urls_to_test = [
        "https://techreparo.com",
        "https://techze-frontend-app.onrender.com",
        "https://techze-diagnostic-api.onrender.com",
        "https://techze-diagnostic-api.onrender.com/docs"
    ]
    
    for url in urls_to_test:
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            status_emoji = "✅" if response.status_code == 200 else "❌"
            
            content_type = response.headers.get('content-type', 'unknown')
            is_html = 'text/html' in content_type
            is_json = 'application/json' in content_type
            
            content_info = ""
            if is_html:
                content_info = " (HTML - Frontend)"
            elif is_json:
                content_info = " (JSON - API)"
            
            log_step(f"   {status_emoji} {url} - {response.status_code}{content_info}")
            
        except Exception as e:
            log_step(f"   ❌ {url} - Erro: {str(e)}")

def main():
    """Função principal"""
    log_step("📊 VERIFICAÇÃO DE STATUS DO RENDER")
    log_step("=" * 60)
    
    get_services_with_deploys()
    test_urls()
    
    log_step("=" * 60)
    log_step("🎯 VERIFICAÇÃO CONCLUÍDA!")

if __name__ == "__main__":
    main() 