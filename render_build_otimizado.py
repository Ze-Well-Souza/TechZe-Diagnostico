#!/usr/bin/env python3
"""
Build Otimizado para Render
TechZe Diagnóstico - Configuração Específica para Render
"""

import requests
import json
import time
from datetime import datetime

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f'[{timestamp}] {level}: {msg}')

def main():
    # Configuração
    api_key = 'rnd_Tj1JybEJij6A3UhouM7spm8LRbkX'
    service_id = 'srv-d13i0ps9c44c739cd3e0'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

    log('🔧 Aplicando configurações otimizadas para Render...')

    # Configuração otimizada para Render
    optimized_config = {
        "serviceDetails": {
            "buildCommand": "npm ci && npm run build",  # npm ci é mais rápido e confiável
            "publishPath": "dist",
            "env": "node",
            "buildFilter": {
                "paths": ["src/**", "public/**", "package.json", "package-lock.json", "vite.config.ts", "tsconfig.json"],
                "ignoredPaths": ["README.md", "docs/**", "tests/**", "*.py", "*.md"]
            }
        },
        "envVars": [
            {
                "key": "NODE_VERSION",
                "value": "18"
            },
            {
                "key": "NPM_CONFIG_PRODUCTION",
                "value": "false"
            }
        ]
    }

    # Aplicar configuração
    try:
        response = requests.patch(
            f'https://api.render.com/v1/services/{service_id}',
            headers=headers,
            json=optimized_config,
            timeout=30
        )
        
        if response.status_code in [200, 202]:
            log('✅ Configurações otimizadas aplicadas!')
            
            # Aguardar propagação
            log('⏳ Aguardando propagação...')
            time.sleep(10)
            
            # Forçar deploy
            log('🚀 Iniciando deploy otimizado...')
            
            deploy_response = requests.post(
                f'https://api.render.com/v1/services/{service_id}/deploys',
                headers=headers,
                timeout=30
            )
            
            if deploy_response.status_code == 201:
                deploy_data = deploy_response.json()
                deploy_id = deploy_data.get('id')
                log(f'✅ Deploy iniciado! ID: {deploy_id}')
                
                # Monitoramento estendido (10 minutos)
                log('👁️ Monitorando deploy (até 10 minutos)...')
                
                for i in range(30):  # 30 x 20s = 10 minutos
                    time.sleep(20)
                    
                    try:
                        check_response = requests.get(
                            f'https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}',
                            headers=headers,
                            timeout=30
                        )
                        
                        if check_response.status_code == 200:
                            deploy_info = check_response.json()
                            deploy_data = deploy_info.get('deploy', deploy_info)
                            status = deploy_data.get('status', 'unknown')
                            
                            log(f'📊 Status: {status} ({i+1}/30)')
                            
                            if status == 'live':
                                log('🎉 Deploy concluído com sucesso!')
                                
                                # Teste imediato
                                log('🧪 Testando resultado...')
                                time.sleep(5)  # Aguardar propagação
                                
                                test_urls = [
                                    'https://techze-frontend-app.onrender.com',
                                    'https://techreparo.com',
                                    'https://www.techreparo.com'
                                ]
                                
                                all_working = True
                                for url in test_urls:
                                    try:
                                        test_response = requests.get(url, timeout=15)
                                        if test_response.status_code == 200:
                                            log(f'✅ {url}: OK')
                                        else:
                                            log(f'❌ {url}: {test_response.status_code}')
                                            all_working = False
                                    except Exception as e:
                                        log(f'❌ {url}: Erro - {e}')
                                        all_working = False
                                
                                if all_working:
                                    log('🎉 SUCESSO TOTAL! Todos os sites funcionando!', "SUCCESS")
                                else:
                                    log('⚠️ Deploy OK, mas alguns sites ainda com problemas', "WARNING")
                                    log('💡 Aguarde 5-10 minutos para propagação DNS completa')
                                
                                break
                                
                            elif status in ['build_failed', 'upload_failed', 'canceled']:
                                log(f'❌ Deploy falhou: {status}', "ERROR")
                                
                                # Tentar obter logs do erro
                                try:
                                    logs_response = requests.get(
                                        f'https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}/logs',
                                        headers=headers,
                                        timeout=30
                                    )
                                    
                                    if logs_response.status_code == 200:
                                        logs = logs_response.text
                                        
                                        # Extrair últimas linhas com erros
                                        lines = logs.split('\n')
                                        error_lines = []
                                        
                                        for line in lines[-50:]:  # Últimas 50 linhas
                                            if any(error in line.lower() for error in ['error:', 'failed:', 'exception:']):
                                                error_lines.append(line.strip())
                                        
                                        if error_lines:
                                            log('❌ ERROS ENCONTRADOS:')
                                            for error in error_lines[-5:]:  # Últimos 5 erros
                                                print(f'   {error}')
                                        
                                        # Salvar logs
                                        with open('render_build_error_logs.txt', 'w', encoding='utf-8') as f:
                                            f.write(logs)
                                        
                                        log('📄 Logs completos salvos: render_build_error_logs.txt')
                                    
                                except Exception as e:
                                    log(f'❌ Erro ao obter logs: {e}')
                                
                                break
                                
                        else:
                            log(f'⚠️ Erro ao verificar deploy: {check_response.status_code}')
                            
                    except Exception as e:
                        log(f'❌ Erro no monitoramento: {e}')
                
                else:
                    log('⏰ Timeout no monitoramento (10 minutos)', "WARNING")
                    log('💡 Verifique manualmente no dashboard do Render')
                
            else:
                log(f'❌ Erro ao iniciar deploy: {deploy_response.status_code}', "ERROR")
                
        else:
            log(f'❌ Erro ao aplicar configurações: {response.status_code}', "ERROR")
            log(f'Resposta: {response.text}')
            
    except Exception as e:
        log(f'❌ Erro inesperado: {e}', "ERROR")

    # Instruções finais
    log('📋 PRÓXIMOS PASSOS SE AINDA HOUVER PROBLEMAS:')
    print('   1. 🌐 Verificar dashboard: https://dashboard.render.com/static/srv-d13i0ps9c44c739cd3e0')
    print('   2. 📄 Verificar logs completos na aba "Logs"')
    print('   3. 🔄 Tentar deploy manual se necessário')
    print('   4. 💬 Contatar suporte do Render se persistir')

if __name__ == "__main__":
    main()