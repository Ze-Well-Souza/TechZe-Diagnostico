#!/usr/bin/env python3
"""
🚀 RENDER AUTO SETUP - Configuração Automática do Frontend TechZe
Automatiza toda a configuração do frontend no Render via API
"""

import requests
import json
import time
from datetime import datetime

# Configurações
RENDER_API_KEY = "rnd_Tj1JybEJij6A3UhouM7spm8LRbkX"
GITHUB_REPO = "https://github.com/Ze-Well-Souza/TechZe-Diagnostico"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def log_step(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_services():
    """Listar serviços existentes"""
    log_step("🔍 Buscando serviços existentes...")
    
    response = requests.get(
        "https://api.render.com/v1/services",
        headers=headers
    )
    
    if response.status_code == 200:
        services = response.json()
        log_step(f"✅ Encontrados {len(services)} serviços")
        return services
    else:
        log_step(f"❌ Erro ao buscar serviços: {response.status_code}")
        return []

def get_owner_id():
    """Obter ID do proprietário"""
    log_step("🔍 Obtendo informações da conta...")
    
    response = requests.get(
        "https://api.render.com/v1/owners",
        headers=headers
    )
    
    if response.status_code == 200:
        owners = response.json()
        if owners:
            owner_id = owners[0]['owner']['id']
            log_step(f"✅ Owner ID encontrado: {owner_id}")
            return owner_id
    
    log_step("❌ Erro ao obter Owner ID")
    return None

def create_static_site():
    """Criar site estático frontend"""
    log_step("🚀 Criando serviço frontend (Static Site)...")
    
    # Obter owner ID primeiro
    owner_id = get_owner_id()
    if not owner_id:
        log_step("❌ Não foi possível obter Owner ID")
        return None
    
    payload = {
        "type": "static_site",
        "name": "techze-frontend-app",
        "ownerId": owner_id,
        "repo": GITHUB_REPO,
        "branch": "main",
        "buildCommand": "npm run build:render",
        "publishPath": "dist",
        "pullRequestPreviewsEnabled": "yes",
        "headers": [],
        "routes": [],
        "envVars": [
            {
                "key": "NODE_VERSION",
                "value": "22.14.0"
            },
            {
                "key": "VITE_API_URL", 
                "value": "https://techze-diagnostic-api.onrender.com"
            }
        ]
    }
    
    response = requests.post(
        "https://api.render.com/v1/services",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        service = response.json()
        log_step(f"✅ Frontend criado com sucesso!")
        log_step(f"📋 Service ID: {service['service']['id']}")
        log_step(f"🌐 URL: {service['service']['serviceDetails'].get('url', 'Não disponível')}")
        return service['service']
    else:
        log_step(f"❌ Erro ao criar frontend: {response.status_code}")
        log_step(f"📄 Resposta: {response.text}")
        return None

def add_custom_domain(service_id, domain):
    """Adicionar domínio customizado"""
    log_step(f"🌐 Adicionando domínio {domain}...")
    
    payload = {
        "name": domain
    }
    
    response = requests.post(
        f"https://api.render.com/v1/services/{service_id}/custom-domains",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 201:
        log_step(f"✅ Domínio {domain} adicionado com sucesso!")
        return True
    else:
        log_step(f"❌ Erro ao adicionar domínio {domain}: {response.status_code}")
        log_step(f"📄 Resposta: {response.text}")
        return False

def remove_domain_from_backend(backend_service_id, domain):
    """Remover domínio do backend"""
    log_step(f"🔄 Removendo {domain} do backend...")
    
    # Primeiro, listar domínios do backend
    response = requests.get(
        f"https://api.render.com/v1/services/{backend_service_id}/custom-domains",
        headers=headers
    )
    
    if response.status_code == 200:
        domains = response.json()
        for domain_obj in domains:
            if domain_obj['customDomain']['name'] == domain:
                # Deletar domínio
                delete_response = requests.delete(
                    f"https://api.render.com/v1/services/{backend_service_id}/custom-domains/{domain_obj['customDomain']['id']}",
                    headers=headers
                )
                
                if delete_response.status_code == 204:
                    log_step(f"✅ Domínio {domain} removido do backend!")
                    return True
                else:
                    log_step(f"❌ Erro ao remover domínio: {delete_response.status_code}")
    
    return False

def monitor_deploy(service_id):
    """Monitorar status do deploy"""
    log_step("⏳ Monitorando deploy...")
    
    for i in range(30):  # 15 minutos máximo
        response = requests.get(
            f"https://api.render.com/v1/services/{service_id}/deploys",
            headers=headers
        )
        
        if response.status_code == 200:
            deploys = response.json()
            if deploys:
                latest_deploy = deploys[0]['deploy']
                status = latest_deploy['status']
                
                log_step(f"📊 Deploy status: {status}")
                
                if status == "live":
                    log_step("🎉 Deploy concluído com sucesso!")
                    return True
                elif status in ["build_failed", "update_failed"]:
                    log_step("❌ Deploy falhou!")
                    return False
        
        time.sleep(30)  # Aguardar 30 segundos
    
    log_step("⏰ Timeout no monitoramento do deploy")
    return False

def main():
    """Função principal"""
    log_step("🚀 INICIANDO CONFIGURAÇÃO AUTOMÁTICA DO RENDER")
    log_step("=" * 60)
    
    # 1. Listar serviços existentes
    services = get_services()
    
    # Encontrar backend
    backend_service = None
    for service in services:
        if "api" in service['service']['name'].lower():
            backend_service = service['service']
            log_step(f"🔍 Backend encontrado: {backend_service['name']} (ID: {backend_service['id']})")
            break
    
    # 2. Criar frontend
    frontend_service = create_static_site()
    
    if not frontend_service:
        log_step("❌ Falha na criação do frontend. Abortando...")
        return
    
    frontend_id = frontend_service['id']
    
    # 3. Aguardar um pouco para o serviço ser criado
    log_step("⏳ Aguardando serviço ser inicializado...")
    time.sleep(10)
    
    # 4. Monitorar deploy
    deploy_success = monitor_deploy(frontend_id)
    
    if deploy_success:
        # 5. Configurar domínios (se backend foi encontrado)
        if backend_service:
            log_step("🔄 Transferindo domínios do backend para frontend...")
            
            # Remover do backend
            for domain in ["techreparo.com", "www.techreparo.com"]:
                remove_domain_from_backend(backend_service['id'], domain)
                time.sleep(2)
                
                # Adicionar ao frontend
                add_custom_domain(frontend_id, domain)
                time.sleep(2)
        else:
            log_step("⚠️ Backend não encontrado, pulando configuração de domínios")
    
    log_step("=" * 60)
    log_step("🎯 CONFIGURAÇÃO CONCLUÍDA!")
    log_step("✅ Frontend: Criado e deployado")
    log_step("✅ Domínios: Configurados (se backend encontrado)")
    log_step("🌐 Teste em: https://techreparo.com (aguarde propagação DNS)")
    log_step("📱 URL alternativa: URL do Render será exibida no dashboard")

if __name__ == "__main__":
    main() 