#!/usr/bin/env python3
"""
🔧 RENDER CONFIG FIX - Correção das Configurações via API
Corrige configurações incorretas dos serviços no Render
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

def get_services():
    """Listar todos os serviços"""
    log_step("🔍 Listando todos os serviços...")
    
    response = requests.get(
        "https://api.render.com/v1/services",
        headers=headers
    )
    
    if response.status_code == 200:
        services = response.json()
        log_step(f"✅ Encontrados {len(services)} serviços")
        
        for service in services:
            srv = service['service']
            log_step(f"📋 {srv['name']} ({srv['type']}) - {srv['id']}")
            
        return services
    else:
        log_step(f"❌ Erro ao buscar serviços: {response.status_code}")
        return []

def delete_service(service_id, service_name):
    """Deletar serviço"""
    log_step(f"🗑️ Deletando serviço {service_name}...")
    
    response = requests.delete(
        f"https://api.render.com/v1/services/{service_id}",
        headers=headers
    )
    
    if response.status_code == 204:
        log_step(f"✅ Serviço {service_name} deletado com sucesso!")
        return True
    else:
        log_step(f"❌ Erro ao deletar {service_name}: {response.status_code}")
        return False

def update_service_build_command(service_id, build_command):
    """Atualizar comando de build"""
    log_step(f"🔧 Atualizando build command...")
    
    payload = {
        "buildCommand": build_command
    }
    
    response = requests.patch(
        f"https://api.render.com/v1/services/{service_id}",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        log_step(f"✅ Build command atualizado!")
        return True
    else:
        log_step(f"❌ Erro ao atualizar build command: {response.status_code}")
        log_step(f"📄 Resposta: {response.text}")
        return False

def trigger_deploy(service_id):
    """Disparar novo deploy"""
    log_step("🚀 Disparando novo deploy...")
    
    response = requests.post(
        f"https://api.render.com/v1/services/{service_id}/deploys",
        headers=headers
    )
    
    if response.status_code == 201:
        log_step("✅ Deploy disparado com sucesso!")
        return True
    else:
        log_step(f"❌ Erro ao disparar deploy: {response.status_code}")
        return False

def main():
    """Função principal"""
    log_step("🔧 INICIANDO CORREÇÃO DAS CONFIGURAÇÕES DO RENDER")
    log_step("=" * 60)
    
    # 1. Listar serviços
    services = get_services()
    
    if not services:
        log_step("❌ Nenhum serviço encontrado")
        return
    
    frontend_services = []
    backend_service = None
    
    # 2. Identificar serviços
    for service in services:
        srv = service['service']
        if srv['type'] == 'static_site':
            frontend_services.append(srv)
        elif 'api' in srv['name'].lower():
            backend_service = srv
    
    log_step(f"📊 Frontend services encontrados: {len(frontend_services)}")
    log_step(f"📊 Backend service: {'Sim' if backend_service else 'Não'}")
    
    # 3. Limpar serviços duplicados (manter apenas techze-frontend-app)
    for frontend in frontend_services:
        if frontend['name'] == 'techze-diagnostico-frontend':
            log_step(f"🗑️ Removendo serviço duplicado: {frontend['name']}")
            delete_service(frontend['id'], frontend['name'])
            time.sleep(2)
    
    # 4. Corrigir build command do frontend correto
    correct_frontend = None
    for frontend in frontend_services:
        if frontend['name'] == 'techze-frontend-app':
            correct_frontend = frontend
            break
    
    if correct_frontend:
        log_step(f"🔧 Corrigindo frontend: {correct_frontend['name']}")
        
        # Atualizar build command
        success = update_service_build_command(
            correct_frontend['id'], 
            "npm run build:render"
        )
        
        if success:
            time.sleep(2)
            # Disparar novo deploy
            trigger_deploy(correct_frontend['id'])
    
    log_step("=" * 60)
    log_step("🎯 CORREÇÃO CONCLUÍDA!")
    log_step("⏳ Aguarde 3-5 minutos para o deploy completar")
    log_step("🌐 Teste: https://techreparo.com")

if __name__ == "__main__":
    main() 