#!/usr/bin/env python3
"""
Script para corrigir problemas críticos identificados pelos testes
"""

import requests
import json
import time
import subprocess
import os
from pathlib import Path

# Configurações
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:8081"
SUPABASE_URL = "https://pkefwvvkydzzfstzwppv.supabase.co"

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"🔧 {title}")
    print("="*60)

def print_step(step):
    """Imprime passo formatado"""
    print(f"\n📋 {step}")
    print("-" * 40)

def fix_cors_issue():
    """Tenta corrigir problemas de CORS"""
    print_step("CORRIGINDO PROBLEMAS DE CORS")
    
    try:
        # Teste básico de CORS
        headers = {
            'Origin': FRONTEND_URL,
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        print("   Testando preflight request...")
        response = requests.options(f"{BACKEND_URL}/health", headers=headers, timeout=5)
        
        if response.status_code in [200, 204]:
            print("   ✅ Preflight request funcionando")
            
            # Verificar headers CORS
            cors_origin = response.headers.get('Access-Control-Allow-Origin', '')
            cors_methods = response.headers.get('Access-Control-Allow-Methods', '')
            cors_headers = response.headers.get('Access-Control-Allow-Headers', '')
            
            print(f"   CORS Origin: {cors_origin}")
            print(f"   CORS Methods: {cors_methods}")
            print(f"   CORS Headers: {cors_headers}")
            
            if cors_origin and cors_methods:
                print("   ✅ CORS configurado corretamente")
                return True
            else:
                print("   ⚠️ CORS headers incompletos")
                return False
        else:
            print(f"   ❌ Preflight falhou: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao testar CORS: {str(e)}")
        return False

def test_api_endpoints():
    """Testa endpoints da API individualmente"""
    print_step("TESTANDO ENDPOINTS DA API INDIVIDUALMENTE")
    
    endpoints = [
        ("/", "Root"),
        ("/health", "Health Check"),
        ("/info", "Service Info"),
        ("/docs", "API Documentation"),
        ("/api/v1/diagnostic/quick", "Quick Diagnostic")
    ]
    
    results = {}
    for endpoint, name in endpoints:
        try:
            print(f"   Testando {name} ({endpoint})...")
            
            if endpoint == "/api/v1/diagnostic/quick":
                # POST request para diagnóstico
                response = requests.post(f"{BACKEND_URL}{endpoint}", timeout=10)
            else:
                # GET request para outros endpoints
                response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"   ✅ {name}: OK")
                results[endpoint] = True
            else:
                print(f"   ⚠️ {name}: Status {response.status_code}")
                results[endpoint] = False
                
        except Exception as e:
            print(f"   ❌ {name}: Erro - {str(e)}")
            results[endpoint] = False
    
    return results

def check_backend_logs():
    """Verifica se há logs de erro no backend"""
    print_step("VERIFICANDO LOGS DO BACKEND")
    
    try:
        # Tentar acessar endpoint de info para ver configurações
        response = requests.get(f"{BACKEND_URL}/info", timeout=5)
        
        if response.status_code == 200:
            info = response.json()
            print("   ✅ Backend respondendo")
            print(f"   Versão: {info.get('version', 'N/A')}")
            print(f"   Ambiente: {info.get('environment', 'N/A')}")
            print(f"   Debug: {info.get('debug_mode', 'N/A')}")
            print(f"   CORS Origins: {info.get('cors_origins', 'N/A')}")
            
            features = info.get('features', {})
            print("   Features:")
            for feature, status in features.items():
                status_icon = "✅" if status else "❌"
                print(f"     {status_icon} {feature}: {status}")
            
            return True
        else:
            print(f"   ❌ Backend não respondeu: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao verificar backend: {str(e)}")
        return False

def test_frontend_access():
    """Testa acesso ao frontend"""
    print_step("TESTANDO ACESSO AO FRONTEND")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        
        if response.status_code == 200:
            print("   ✅ Frontend acessível")
            content_type = response.headers.get('content-type', '')
            print(f"   Content-Type: {content_type}")
            
            # Verificar se é HTML
            if 'text/html' in content_type:
                print("   ✅ Servindo HTML corretamente")
                return True
            else:
                print("   ⚠️ Não está servindo HTML")
                return False
        else:
            print(f"   ❌ Frontend não acessível: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Erro ao acessar frontend: {str(e)}")
        return False

def create_simple_cors_test():
    """Cria um teste simples de CORS"""
    print_step("CRIANDO TESTE SIMPLES DE CORS")
    
    test_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Teste CORS</title>
</head>
<body>
    <h1>Teste de CORS</h1>
    <button onclick="testCors()">Testar CORS</button>
    <div id="result"></div>
    
    <script>
        async function testCors() {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = 'Testando...';
            
            try {
                const response = await fetch('http://localhost:8000/health', {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const data = await response.json();
                    resultDiv.innerHTML = `<p style="color: green;">✅ CORS OK: ${JSON.stringify(data)}</p>`;
                } else {
                    resultDiv.innerHTML = `<p style="color: orange;">⚠️ Status: ${response.status}</p>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<p style="color: red;">❌ Erro CORS: ${error.message}</p>`;
            }
        }
    </script>
</body>
</html>
    """
    
    try:
        with open('cors_test.html', 'w', encoding='utf-8') as f:
            f.write(test_html)
        
        print("   ✅ Arquivo cors_test.html criado")
        print("   📝 Para testar CORS:")
        print("      1. Abra cors_test.html no navegador")
        print("      2. Clique em 'Testar CORS'")
        print("      3. Verifique se a requisição funciona")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao criar teste: {str(e)}")
        return False

def suggest_fixes():
    """Sugere correções para problemas comuns"""
    print_step("SUGESTÕES DE CORREÇÃO")
    
    print("   🔧 PROBLEMAS COMUNS E SOLUÇÕES:")
    print()
    
    print("   1. CORS não funcionando:")
    print("      - Verificar se backend está rodando na porta 8000")
    print("      - Verificar se frontend está rodando na porta 8081")
    print("      - Reiniciar ambos os serviços")
    print()
    
    print("   2. API Endpoints falhando:")
    print("      - Verificar se todas as dependências estão instaladas")
    print("      - Verificar arquivo .env no microserviço")
    print("      - Verificar logs do backend para erros")
    print()
    
    print("   3. Frontend não carregando:")
    print("      - Executar 'npm install' no diretório frontend-v3")
    print("      - Verificar se todas as dependências estão instaladas")
    print("      - Verificar se a porta 8081 está livre")
    print()
    
    print("   📋 COMANDOS PARA REINICIAR:")
    print("      # Terminal 1 - Backend")
    print("      cd microservices/diagnostic_service")
    print("      python main.py")
    print()
    print("      # Terminal 2 - Frontend")
    print("      cd frontend-v3")
    print("      npm run dev")

def main():
    """Função principal"""
    print_header("CORREÇÃO DE PROBLEMAS CRÍTICOS")
    
    results = {}
    
    # Verificar backend
    results["Backend Info"] = check_backend_logs()
    
    # Testar endpoints
    api_results = test_api_endpoints()
    results["API Endpoints"] = all(api_results.values())
    
    # Testar CORS
    results["CORS"] = fix_cors_issue()
    
    # Testar frontend
    results["Frontend"] = test_frontend_access()
    
    # Criar teste de CORS
    create_simple_cors_test()
    
    # Mostrar sugestões
    suggest_fixes()
    
    # Relatório final
    print_header("RELATÓRIO DE CORREÇÕES")
    
    total_checks = len(results)
    passed_checks = sum(1 for result in results.values() if result)
    success_rate = (passed_checks / total_checks) * 100
    
    print(f"📊 ESTATÍSTICAS:")
    print(f"   Total de Verificações: {total_checks}")
    print(f"   Verificações Passaram: {passed_checks}")
    print(f"   Taxa de Sucesso: {success_rate:.1f}%")
    
    print(f"\n📋 DETALHES:")
    for check_name, result in results.items():
        status = "✅ OK" if result else "❌ PROBLEMA"
        print(f"   {check_name}: {status}")
    
    if success_rate >= 75:
        print(f"\n🎉 SISTEMA EM BOM ESTADO!")
        print("   Execute 'python validate_system.py' para validação completa")
    else:
        print(f"\n⚠️ SISTEMA PRECISA DE ATENÇÃO")
        print("   Siga as sugestões acima para corrigir os problemas")

if __name__ == "__main__":
    main()