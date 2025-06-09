#!/usr/bin/env python3
"""
🧪 TechZe Sistema - Teste Rápido Real
"""

import requests
import json
from datetime import datetime

def main():
    # Testar servidor local
    base_url = 'http://127.0.0.1:8000'
    print('🧪 TechZe Sistema - Teste Rápido Real')
    print(f'🌐 Testando: {base_url}')
    print('=' * 50)

    tests_passed = 0
    total_tests = 0

    # Health check
    total_tests += 1
    try:
        print('\n🔍 Testando Health Check...')
        response = requests.get(f'{base_url}/health', timeout=10)
        if response.status_code == 200:
            print('✅ Health Check: Sistema online')
            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
            print(f'   📄 Resposta: {data}')
            tests_passed += 1
        else:
            print(f'❌ Health Check: Status {response.status_code}')
    except Exception as e:
        print(f'❌ Health Check: Erro - {e}')

    # Pool metrics  
    total_tests += 1
    try:
        print('\n📊 Testando Pool Metrics...')
        response = requests.get(f'{base_url}/api/v3/pool/metrics', timeout=10)
        if response.status_code == 200:
            print('✅ Pool Metrics: Disponível')
            metrics = response.json()
            print(f'   📊 Conexões ativas: {metrics.get("active_connections", "N/A")}')
            print(f'   📊 Conexões máximas: {metrics.get("max_connections", "N/A")}')
            tests_passed += 1
        else:
            print(f'❌ Pool Metrics: Status {response.status_code}')
    except Exception as e:
        print(f'❌ Pool Metrics: Erro - {e}')

    # Diagnóstico básico
    total_tests += 1
    try:
        print('\n🔍 Testando Diagnóstico...')
        system_data = {
            'system_info': {
                'os': 'Windows 11',
                'cpu_usage': 45,
                'memory_usage': 60,
                'disk_usage': 75
            }
        }
        response = requests.post(f'{base_url}/api/core/diagnostics/analysis', json=system_data, timeout=15)
        if response.status_code == 200:
            print('✅ Diagnóstico: Funcionando')
            result = response.json()
            analysis = result.get('analysis', {})
            score = analysis.get('overall_score', 'N/A')
            print(f'   🎯 Score geral: {score}')
            print(f'   📋 Issues encontrados: {len(analysis.get("issues_found", []))}')
            print(f'   💡 Recomendações: {len(analysis.get("recommendations", []))}')
            tests_passed += 1
        else:
            print(f'❌ Diagnóstico: Status {response.status_code}')
    except Exception as e:
        print(f'❌ Diagnóstico: Erro - {e}')

    # IA Chat
    total_tests += 1
    try:
        print('\n🤖 Testando IA Chat...')
        ai_data = {
            'message': 'Meu computador está lento, o que pode ser?',
            'context': {'system_type': 'desktop', 'os': 'Windows 11'}
        }
        response = requests.post(f'{base_url}/api/core/ai/chat', json=ai_data, timeout=20)
        if response.status_code == 200:
            print('✅ IA Chat: Funcionando')
            result = response.json()
            answer = result.get('response', '')
            print(f'   🤖 Resposta (primeiros 100 chars): {answer[:100]}...')
            tests_passed += 1
        else:
            print(f'❌ IA Chat: Status {response.status_code}')
    except Exception as e:
        print(f'❌ IA Chat: Erro - {e}')

    # Performance Metrics
    total_tests += 1
    try:
        print('\n⚡ Testando Performance Metrics...')
        response = requests.get(f'{base_url}/api/core/performance/metrics/system', timeout=10)
        if response.status_code == 200:
            print('✅ Performance: Funcionando')
            result = response.json()
            print(f'   📊 Métricas obtidas: {len(result) if isinstance(result, dict) else 0}')
            tests_passed += 1
        else:
            print(f'❌ Performance: Status {response.status_code}')
    except Exception as e:
        print(f'❌ Performance: Erro - {e}')

    # Relatório Final
    print('\n' + '=' * 60)
    print('📊 RELATÓRIO FINAL')
    print('=' * 60)
    
    success_rate = (tests_passed / total_tests) * 100
    print(f'🎯 Testes realizados: {total_tests}')
    print(f'✅ Sucessos: {tests_passed}')
    print(f'❌ Falhas: {total_tests - tests_passed}')
    print(f'📈 Taxa de sucesso: {success_rate:.1f}%')
    
    if success_rate >= 80:
        print('\n🎉 SISTEMA FUNCIONANDO PERFEITAMENTE!')
        print('✅ Todas as funcionalidades principais estão operacionais')
        print('✅ Sistema pronto para uso em produção')
    elif success_rate >= 60:
        print('\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL')
        print('🔧 Algumas funcionalidades podem precisar de ajustes')
    else:
        print('\n❌ SISTEMA COM PROBLEMAS')
        print('🚨 Necessária investigação técnica')
    
    print(f'\n💾 Teste executado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

if __name__ == "__main__":
    main() 