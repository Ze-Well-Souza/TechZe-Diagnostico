#!/usr/bin/env python3
"""
Deploy Final Automático
TechZe Diagnóstico - Deploy e Monitoramento Final
"""

import requests
import time
from datetime import datetime

def log(msg):
    print(f'[{datetime.now().strftime("%H:%M:%S")}] {msg}')

def main():
    # Configuração
    api_key = 'rnd_Tj1JybEJij6A3UhouM7spm8LRbkX'
    service_id = 'srv-d13i0ps9c44c739cd3e0'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

    log('🚀 Forçando novo deploy...')

    # Forçar deploy
    response = requests.post(f'https://api.render.com/v1/services/{service_id}/deploys', headers=headers, timeout=30)

    if response.status_code == 201:
        deploy_data = response.json()
        deploy_id = deploy_data.get('id')
        log(f'✅ Deploy iniciado! ID: {deploy_id}')
        
        # Monitorar por 5 minutos
        for i in range(15):  # 15 x 20s = 5 minutos
            time.sleep(20)
            
            check_response = requests.get(f'https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}', headers=headers, timeout=30)
            
            if check_response.status_code == 200:
                deploy_info = check_response.json()
                deploy_data = deploy_info.get('deploy', deploy_info)
                status = deploy_data.get('status', 'unknown')
                
                log(f'📊 Status: {status}')
                
                if status == 'live':
                    log('🎉 Deploy concluído com sucesso!')
                    break
                elif status in ['build_failed', 'upload_failed', 'canceled']:
                    log(f'❌ Deploy falhou: {status}')
                    break
            else:
                log(f'⚠️ Erro ao verificar: {check_response.status_code}')
        
        # Teste final
        log('🧪 Testando sites...')
        
        test_urls = ['https://techze-frontend-app.onrender.com', 'https://techreparo.com', 'https://www.techreparo.com']
        
        for url in test_urls:
            try:
                test_response = requests.get(url, timeout=15)
                status_icon = '✅' if test_response.status_code == 200 else '❌'
                log(f'{status_icon} {url}: {test_response.status_code}')
            except Exception as e:
                log(f'❌ {url}: Erro - {e}')
                
    else:
        log(f'❌ Erro ao iniciar deploy: {response.status_code}')

if __name__ == "__main__":
    main()