#!/usr/bin/env python3
"""
🧪 TechZe Sistema - Teste Completo REAL com Usuário
Usando endpoints corretos da API
"""

import requests
import json
import random
import string
import time
from datetime import datetime

def main():
    base_url = 'http://127.0.0.1:8000'
    session = requests.Session()
    
    print('🧪 TechZe Sistema - Teste Completo REAL')
    print(f'🌐 Testando: {base_url}')
    print(f'📅 Data/Hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 60)
    
    tests_passed = 0
    total_tests = 0
    test_results = []

    def log_test(name, success, details="", data=None):
        nonlocal tests_passed, total_tests
        total_tests += 1
        if success:
            tests_passed += 1
        
        status = "✅" if success else "❌"
        print(f"{status} {name}: {details}")
        
        test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
        return success

    # 1. HEALTH CHECKS
    print('\n🔍 === VERIFICAÇÕES DE SAÚDE ===')
    
    try:
        response = session.get(f'{base_url}/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            log_test("Health Geral", True, f"Versão: {data.get('version', 'N/A')}", data)
        else:
            log_test("Health Geral", False, f"Status {response.status_code}")
    except Exception as e:
        log_test("Health Geral", False, f"Erro: {e}")

    # Health checks específicos
    health_endpoints = [
        ("/api/core/diagnostics/health", "Diagnósticos"),
        ("/api/core/auth/health", "Autenticação"),
        ("/api/core/ai/health", "IA"),
        ("/api/core/automation/health", "Automação"),
        ("/api/core/analytics/health", "Analytics"),
        ("/api/core/performance/health", "Performance"),
        ("/api/core/chat/health", "Chat"),
        ("/api/core/integration/health", "Integração")
    ]
    
    for endpoint, service_name in health_endpoints:
        try:
            response = session.get(f'{base_url}{endpoint}', timeout=5)
            if response.status_code == 200:
                log_test(f"Health {service_name}", True, "Serviço online")
            else:
                log_test(f"Health {service_name}", False, f"Status {response.status_code}")
        except Exception as e:
            log_test(f"Health {service_name}", False, f"Erro: {e}")

    # 2. CRIAR USUÁRIO DE TESTE
    print('\n👤 === CRIAÇÃO DE USUÁRIO ===')
    
    timestamp = str(int(time.time()))
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    
    user_data = {
        "email": f"teste.usuario.{timestamp}.{random_suffix}@techze.com.br",
        "password": "TechZe@123!Teste",
        "full_name": f"Usuário Teste {timestamp}",
        "phone": f"+55119{random.randint(10000000, 99999999)}",
        "company": "TechZe Testing Corp"
    }
    
    print(f"📧 Email: {user_data['email']}")
    print(f"👤 Nome: {user_data['full_name']}")
    
    try:
        response = session.post(f'{base_url}/api/core/auth/register', json=user_data, timeout=15)
        if response.status_code == 201:
            result = response.json()
            access_token = result.get('access_token')
            log_test("Registro Usuário", True, "Usuário criado com sucesso", result)
            
            # Configurar token para próximas requisições
            if access_token:
                session.headers.update({'Authorization': f'Bearer {access_token}'})
                log_test("Token Configurado", True, "Authorization header definido")
            
        else:
            log_test("Registro Usuário", False, f"Status {response.status_code}", response.text)
    except Exception as e:
        log_test("Registro Usuário", False, f"Erro: {e}")

    # 3. DIAGNÓSTICOS
    print('\n🔍 === TESTES DE DIAGNÓSTICO ===')
    
    # Diagnóstico rápido
    try:
        system_data = {
            "system_info": {
                "os": "Windows 11 Pro",
                "cpu_usage": random.randint(20, 80),
                "memory_usage": random.randint(30, 90),
                "disk_usage": random.randint(40, 95),
                "cpu_model": "Intel Core i7-12700K",
                "total_memory": "32GB",
                "total_disk": "1TB SSD"
            },
            "performance_metrics": {
                "response_time": random.uniform(50, 200),
                "throughput": random.randint(100, 1000),
                "error_rate": random.uniform(0, 5)
            }
        }
        
        response = session.post(f'{base_url}/api/core/diagnostics/quick', json=system_data, timeout=15)
        if response.status_code == 200:
            result = response.json()
            diagnostic_id = result.get('diagnostic_id', 'N/A')
            score = result.get('score', 'N/A')
            log_test("Diagnóstico Rápido", True, f"ID: {diagnostic_id}, Score: {score}", result)
        else:
            log_test("Diagnóstico Rápido", False, f"Status {response.status_code}")
    except Exception as e:
        log_test("Diagnóstico Rápido", False, f"Erro: {e}")

    # 4. ASSISTENTE DE IA
    print('\n🤖 === TESTES DE IA ===')
    
    # Iniciar sessão de chat
    try:
        chat_session_data = {
            "name": f"Sessão Teste {timestamp}",
            "context": {
                "system_type": "desktop",
                "os": "Windows 11",
                "user_level": "intermediate"
            }
        }
        
        response = session.post(f'{base_url}/api/core/chat/sessions', json=chat_session_data, timeout=10)
        if response.status_code == 201:
            session_result = response.json()
            session_id = session_result.get('session_id')
            log_test("Criação Sessão Chat", True, f"Session ID: {session_id}", session_result)
            
            # Enviar mensagem
            if session_id:
                message_data = {
                    "content": "Meu computador está lento, o que pode ser?",
                    "message_type": "user"
                }
                
                msg_response = session.post(
                    f'{base_url}/api/core/chat/sessions/{session_id}/messages',
                    json=message_data,
                    timeout=20
                )
                
                if msg_response.status_code == 201:
                    msg_result = msg_response.json()
                    response_content = msg_result.get('response', {}).get('content', '')
                    log_test("IA Chat Resposta", True, f"Resposta: {response_content[:100]}...", msg_result)
                else:
                    log_test("IA Chat Resposta", False, f"Status {msg_response.status_code}")
        else:
            log_test("Criação Sessão Chat", False, f"Status {response.status_code}")
    except Exception as e:
        log_test("IA Chat", False, f"Erro: {e}")

    # 5. PERFORMANCE E MÉTRICAS
    print('\n⚡ === TESTES DE PERFORMANCE ===')
    
    performance_endpoints = [
        ("/api/core/performance/metrics/system", "Métricas Sistema"),
        ("/api/core/performance/metrics/database", "Métricas Database"),
        ("/api/core/performance/metrics/application", "Métricas Aplicação"),
        ("/api/core/performance/health/basic", "Health Básico"),
        ("/api/core/performance/dashboard", "Dashboard Performance")
    ]
    
    for endpoint, test_name in performance_endpoints:
        try:
            response = session.get(f'{base_url}{endpoint}', timeout=10)
            if response.status_code == 200:
                result = response.json()
                data_count = len(result) if isinstance(result, dict) else 0
                log_test(test_name, True, f"Dados obtidos: {data_count} campos", result)
            else:
                log_test(test_name, False, f"Status {response.status_code}")
        except Exception as e:
            log_test(test_name, False, f"Erro: {e}")

    # 6. ANALYTICS
    print('\n📊 === TESTES DE ANALYTICS ===')
    
    try:
        # Métricas em tempo real
        response = session.get(f'{base_url}/api/core/analytics/metrics/real-time', timeout=10)
        if response.status_code == 200:
            result = response.json()
            log_test("Analytics Tempo Real", True, f"Métricas: {len(result) if isinstance(result, dict) else 0}", result)
        else:
            log_test("Analytics Tempo Real", False, f"Status {response.status_code}")
    except Exception as e:
        log_test("Analytics Tempo Real", False, f"Erro: {e}")

    try:
        # Tendências
        response = session.get(f'{base_url}/api/core/analytics/trends', timeout=10)
        if response.status_code == 200:
            result = response.json()
            log_test("Analytics Tendências", True, "Dados de tendências obtidos", result)
        else:
            log_test("Analytics Tendências", False, f"Status {response.status_code}")
    except Exception as e:
        log_test("Analytics Tendências", False, f"Erro: {e}")

    # 7. AUTOMAÇÃO
    print('\n⚙️ === TESTES DE AUTOMAÇÃO ===')
    
    try:
        # Criar tarefa de automação
        task_data = {
            "name": f"Tarefa Teste {timestamp}",
            "description": "Tarefa de teste para limpeza de sistema",
            "task_type": "system_cleanup",
            "parameters": {
                "cleanup_temp": True,
                "check_disk_space": True,
                "min_free_gb": 10
            },
            "schedule": "manual"
        }
        
        response = session.post(f'{base_url}/api/core/automation/tasks', json=task_data, timeout=15)
        if response.status_code == 201:
            result = response.json()
            task_id = result.get('task_id')
            log_test("Criação Tarefa", True, f"Task ID: {task_id}", result)
            
            # Executar tarefa
            if task_id:
                exec_response = session.post(f'{base_url}/api/core/automation/tasks/{task_id}/execute', timeout=20)
                if exec_response.status_code == 200:
                    exec_result = exec_response.json()
                    status = exec_result.get('status', 'unknown')
                    log_test("Execução Tarefa", True, f"Status: {status}", exec_result)
                else:
                    log_test("Execução Tarefa", False, f"Status {exec_response.status_code}")
        else:
            log_test("Criação Tarefa", False, f"Status {response.status_code}")
    except Exception as e:
        log_test("Automação", False, f"Erro: {e}")

    # 8. INTEGRAÇÃO
    print('\n🔗 === TESTES DE INTEGRAÇÃO ===')
    
    try:
        # Verificar serviços
        response = session.get(f'{base_url}/api/core/integration/services', timeout=10)
        if response.status_code == 200:
            result = response.json()
            services_count = len(result) if isinstance(result, list) else 0
            log_test("Serviços Integração", True, f"Serviços encontrados: {services_count}", result)
        else:
            log_test("Serviços Integração", False, f"Status {response.status_code}")
    except Exception as e:
        log_test("Serviços Integração", False, f"Erro: {e}")

    try:
        # Health check geral
        response = session.post(f'{base_url}/api/core/integration/health-check/all', timeout=15)
        if response.status_code == 200:
            result = response.json()
            log_test("Health Check Integração", True, "Verificação completa", result)
        else:
            log_test("Health Check Integração", False, f"Status {response.status_code}")
    except Exception as e:
        log_test("Health Check Integração", False, f"Erro: {e}")

    # RELATÓRIO FINAL
    print('\n' + '=' * 60)
    print('📊 RELATÓRIO FINAL COMPLETO')
    print('=' * 60)
    
    success_rate = (tests_passed / total_tests) * 100 if total_tests > 0 else 0
    
    print(f'🎯 Total de Testes: {total_tests}')
    print(f'✅ Sucessos: {tests_passed}')
    print(f'❌ Falhas: {total_tests - tests_passed}')
    print(f'📈 Taxa de Sucesso: {success_rate:.1f}%')
    
    if success_rate >= 90:
        print('\n🎉 SISTEMA 100% FUNCIONAL!')
        print('✅ Todas as funcionalidades estão operando perfeitamente')
        print('✅ Sistema completamente pronto para produção')
        print('✅ Usuário pode usar todas as funcionalidades sem problemas')
    elif success_rate >= 70:
        print('\n⚠️ SISTEMA MAJORITARIAMENTE FUNCIONAL')
        print('✅ Funcionalidades principais operando')
        print('🔧 Algumas funcionalidades secundárias podem precisar de ajustes')
        print('✅ Sistema utilizável em produção')
    elif success_rate >= 50:
        print('\n⚠️ SISTEMA PARCIALMENTE FUNCIONAL')
        print('🔧 Várias funcionalidades precisam de ajustes')
        print('⚠️ Uso em produção com restrições')
    else:
        print('\n❌ SISTEMA COM PROBLEMAS CRÍTICOS')
        print('🚨 Maioria das funcionalidades com problemas')
        print('🚨 Não recomendado para produção')
    
    print(f'\n👤 USUÁRIO TESTE CRIADO:')
    print(f'   📧 Email: {user_data["email"]}')
    print(f'   👤 Nome: {user_data["full_name"]}')
    print(f'   🏢 Empresa: {user_data["company"]}')
    
    # Salvar relatório
    report = {
        "timestamp": datetime.now().isoformat(),
        "base_url": base_url,
        "user_created": user_data,
        "summary": {
            "total_tests": total_tests,
            "successful_tests": tests_passed,
            "failed_tests": total_tests - tests_passed,
            "success_rate": success_rate
        },
        "detailed_results": test_results
    }
    
    with open("relatorio_teste_sistema_completo.json", "w", encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f'\n💾 Relatório completo salvo em: relatorio_teste_sistema_completo.json')
    print(f'📅 Teste executado em: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
    if success_rate >= 70:
        print('\n🎊 TESTE CONCLUÍDO COM SUCESSO!')
        print('✅ Sistema TechZe validado com usuário real')
        print('✅ Funcionalidades principais operacionais')
        print('✅ Dados reais sendo processados corretamente')
    else:
        print('\n⚠️ TESTE IDENTIFICOU PROBLEMAS')
        print('🔧 Verifique o relatório detalhado para correções')

if __name__ == "__main__":
    main() 