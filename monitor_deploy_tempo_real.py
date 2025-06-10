#!/usr/bin/env python3
"""
⏳ MONITOR DEPLOY TEMPO REAL
Monitora o progresso dos deploys até conclusão
"""

import requests
import time
from datetime import datetime

# Configurações
RENDER_API_KEY = "rnd_Tj1JybEJij6A3UhouM7spm8LRbkX"

headers = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Accept": "application/json"
}

def log_step(message):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_deploy_status():
    """Verificar status dos deploys"""
    services = {
        "srv-d13i0ps9c44c739cd3e0": "Frontend (Static Site)",
        "srv-d0t22t63jp1c73dui0kg": "Backend (Web Service)"
    }
    
    all_completed = True
    
    for service_id, service_name in services.items():
        response = requests.get(
            f"https://api.render.com/v1/services/{service_id}/deploys?limit=1",
            headers=headers
        )
        
        if response.status_code == 200:
            deploys = response.json()
            if deploys:
                deploy = deploys[0]['deploy']
                status = deploy['status']
                
                status_emoji = {
                    'live': '✅',
                    'build_in_progress': '🔄',
                    'build_failed': '❌',
                    'pre_deploy_in_progress': '⏳',
                    'pre_deploy_failed': '❌'
                }.get(status, '❓')
                
                log_step(f"{status_emoji} {service_name}: {status}")
                
                if status not in ['live']:
                    all_completed = False
    
    return all_completed

def test_domain():
    """Testar domínio principal"""
    try:
        response = requests.get("https://techreparo.com", timeout=5)
        if response.status_code == 200:
            log_step("🎉 SUCESSO! https://techreparo.com está ONLINE!")
            return True
        else:
            log_step(f"⏳ techreparo.com retornou: {response.status_code}")
            return False
    except:
        log_step("⏳ techreparo.com ainda não acessível")
        return False

def main():
    """Monitor contínuo"""
    log_step("🚀 MONITORANDO DEPLOYS EM TEMPO REAL")
    log_step("=" * 50)
    log_step("⏳ Aguardando conclusão dos deploys...")
    print()
    
    check_count = 0
    max_checks = 60  # 30 minutos máximo
    
    while check_count < max_checks:
        check_count += 1
        log_step(f"📊 Verificação #{check_count}")
        
        # Verificar status dos deploys
        all_completed = check_deploy_status()
        
        # Se todos completaram, testar o domínio
        if all_completed:
            log_step("✅ Todos os deploys concluídos!")
            
            if test_domain():
                log_step("🎊 DEPLOY COMPLETO E FUNCIONANDO!")
                break
            else:
                log_step("⏳ Aguardando propagação DNS...")
        
        print()
        
        # Aguardar 30 segundos antes da próxima verificação
        if check_count < max_checks:
            log_step("⏰ Próxima verificação em 30s...")
            time.sleep(30)
    
    if check_count >= max_checks:
        log_step("⚠️ Tempo limite atingido. Verificação manual necessária.")

if __name__ == "__main__":
    main() 