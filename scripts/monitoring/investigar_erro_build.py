#!/usr/bin/env python3
"""
Investigar Erro de Build
TechZe Diagnóstico - Análise de Falha no Build
"""

import requests
import json
from datetime import datetime

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f'[{timestamp}] {level}: {msg}')

def main():
    # Configuração
    api_key = 'rnd_Tj1JybEJij6A3UhouM7spm8LRbkX'
    service_id = 'srv-d13i0ps9c44c739cd3e0'
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

    log('🔍 Investigando erro de build...')

    # Obter último deploy
    response = requests.get(f'https://api.render.com/v1/services/{service_id}/deploys', headers=headers, timeout=30)
    
    if response.status_code == 200:
        deploys = response.json()
        if deploys:
            latest_deploy = deploys[0]
            deploy_info = latest_deploy.get('deploy', latest_deploy)
            deploy_id = deploy_info.get('id')
            status = deploy_info.get('status')
            
            log(f'📊 Último deploy: {deploy_id}')
            log(f'📊 Status: {status}')
            
            # Tentar obter logs
            log('📄 Obtendo logs do build...')
            
            try:
                logs_response = requests.get(
                    f'https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}/logs',
                    headers=headers,
                    timeout=30
                )
                
                if logs_response.status_code == 200:
                    logs = logs_response.text
                    
                    log('📋 LOGS DO BUILD:')
                    print('='*60)
                    print(logs)
                    print('='*60)
                    
                    # Analisar erros
                    log('🔍 Analisando erros...')
                    
                    lines = logs.split('\n')
                    errors = []
                    warnings = []
                    
                    for line in lines:
                        line_lower = line.lower()
                        if any(error in line_lower for error in ['error:', 'failed:', 'exception:', 'cannot resolve', 'module not found']):
                            errors.append(line.strip())
                        elif 'warn' in line_lower and any(warning in line_lower for warning in ['deprecated', 'missing', 'not found']):
                            warnings.append(line.strip())
                    
                    if errors:
                        log('❌ ERROS ENCONTRADOS:')
                        for error in errors[-10:]:  # Últimos 10 erros
                            print(f'   {error}')
                    
                    if warnings:
                        log('⚠️ WARNINGS ENCONTRADOS:')
                        for warning in warnings[-5:]:  # Últimos 5 warnings
                            print(f'   {warning}')
                    
                    # Salvar logs completos
                    with open('logs_build_failed.txt', 'w', encoding='utf-8') as f:
                        f.write(logs)
                    
                    log('📄 Logs salvos em: logs_build_failed.txt')
                    
                else:
                    log(f'❌ Erro ao obter logs: {logs_response.status_code}')
                    
            except Exception as e:
                log(f'❌ Erro ao obter logs: {e}', "ERROR")
            
            # Verificar configuração atual
            log('🔧 Verificando configuração atual...')
            
            config_response = requests.get(f'https://api.render.com/v1/services/{service_id}', headers=headers, timeout=30)
            
            if config_response.status_code == 200:
                service_data = config_response.json()
                service_info = service_data.get('service', service_data)
                details = service_info.get('serviceDetails', {})
                
                log('📊 CONFIGURAÇÃO ATUAL:')
                log(f'   Build Command: "{details.get("buildCommand", "")}"')
                log(f'   Publish Path: "{details.get("publishPath", "")}"')
                log(f'   Root Dir: "{details.get("rootDir", "")}"')
                log(f'   Branch: "{details.get("branch", "main")}"')
                
                # Verificar se há problemas na configuração
                build_cmd = details.get('buildCommand', '')
                if not build_cmd:
                    log('❌ Build Command está vazio!', "ERROR")
                elif 'npm install' not in build_cmd:
                    log('⚠️ Build Command pode estar incorreto', "WARNING")
                
                publish_path = details.get('publishPath', '')
                if publish_path != 'dist':
                    log(f'⚠️ Publish Path não é "dist": "{publish_path}"', "WARNING")
            
        else:
            log('❌ Nenhum deploy encontrado')
    else:
        log(f'❌ Erro ao obter deploys: {response.status_code}')

    # Sugerir próximos passos
    log('🛠️ PRÓXIMOS PASSOS SUGERIDOS:')
    print('   1. 📋 Verificar logs completos no arquivo logs_build_failed.txt')
    print('   2. 🔧 Verificar se package.json tem todas as dependências')
    print('   3. 🧪 Testar build localmente: npm install && npm run build')
    print('   4. 📂 Verificar se vite.config.ts está correto')
    print('   5. 🔄 Tentar deploy manual no dashboard se necessário')

if __name__ == "__main__":
    main()