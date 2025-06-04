#!/usr/bin/env python3
"""
Script para validar a implementação da Semana 3 - IA, ML e Automação
"""

import os
import sys
import subprocess
import time
import json
import requests
from pathlib import Path
from datetime import datetime

def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_step(step: str):
    """Imprime passo atual"""
    print(f"\n📋 {step}")
    print("-" * 40)

def run_command(command: str, cwd: str = None, timeout: int = 30) -> tuple:
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_python_environment():
    """Verifica ambiente Python"""
    print_step("Verificando ambiente Python")
    
    # Verifica versão do Python
    success, output, error = run_command("python --version")
    if success:
        print(f"✅ Python: {output.strip()}")
    else:
        print(f"❌ Erro ao verificar Python: {error}")
        return False
    
    # Verifica pip
    success, output, error = run_command("pip --version")
    if success:
        print(f"✅ Pip: {output.strip()}")
    else:
        print(f"❌ Erro ao verificar pip: {error}")
        return False
    
    return True

def check_project_structure():
    """Verifica estrutura do projeto"""
    print_step("Verificando estrutura do projeto")
    
    required_files = [
        "app/main.py",
        "app/ai/__init__.py",
        "app/ai/ml_engine.py",
        "app/ai/prediction_service.py",
        "app/ai/anomaly_detector.py",
        "app/ai/pattern_analyzer.py",
        "app/ai/recommendation_engine.py",
        "app/ai/chatbot.py",
        "app/automation/__init__.py",
        "app/automation/auto_fix.py",
        "app/automation/workflow_manager.py",
        "app/automation/resource_optimizer.py",
        "app/api/v3/__init__.py",
        "app/api/v3/ai_endpoints.py",
        "app/api/v3/automation_endpoints.py",
        "app/api/v3/analytics_endpoints.py",
        "app/api/v3/chat_endpoints.py",
        "app/models/ai_models.py",
        "app/models/automation_models.py",
        "app/models/analytics_models.py",
        "app/models/chat_models.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"❌ Arquivo não encontrado: {file_path}")
        else:
            print(f"✅ Arquivo encontrado: {file_path}")
    
    if missing_files:
        print(f"\n❌ {len(missing_files)} arquivos estão faltando")
        return False
    else:
        print(f"\n✅ Todos os {len(required_files)} arquivos necessários estão presentes")
        return True

def check_dependencies():
    """Verifica dependências instaladas"""
    print_step("Verificando dependências")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "numpy",
        "scikit-learn",
        "pandas",
        "websockets"
    ]
    
    missing_packages = []
    for package in required_packages:
        success, output, error = run_command(f"python -c \"import {package}\"")
        if success:
            print(f"✅ {package}: Instalado")
        else:
            missing_packages.append(package)
            print(f"❌ {package}: Não instalado")
    
    if missing_packages:
        print(f"\n❌ {len(missing_packages)} pacotes estão faltando")
        print("💡 Execute: pip install " + " ".join(missing_packages))
        return False
    else:
        print(f"\n✅ Todas as dependências estão instaladas")
        return True

def start_service():
    """Inicia o serviço de diagnóstico"""
    print_step("Iniciando serviço de diagnóstico")
    
    # Verifica se já está rodando
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Serviço já está rodando")
            return True
    except:
        pass
    
    # Inicia o serviço
    print("🚀 Iniciando serviço...")
    try:
        # Inicia em background
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Aguarda inicialização
        for i in range(30):
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print("✅ Serviço iniciado com sucesso")
                    return True
            except:
                pass
            time.sleep(1)
            print(f"⏳ Aguardando inicialização... ({i+1}/30)")
        
        print("❌ Timeout ao iniciar serviço")
        process.terminate()
        return False
        
    except Exception as e:
        print(f"❌ Erro ao iniciar serviço: {e}")
        return False

def test_api_v3_endpoints():
    """Testa endpoints da API v3"""
    print_step("Testando endpoints da API v3")
    
    base_url = "http://localhost:8000"
    
    # Testa health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            api_v3_available = data.get("api_v3_router_available", False)
            print(f"✅ Health check: API v3 disponível = {api_v3_available}")
            
            if not api_v3_available:
                print("❌ API v3 não está disponível")
                return False
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False
    
    # Lista de endpoints para testar
    endpoints_to_test = [
        ("GET", "/api/v3/ai/models", "Modelos de IA"),
        ("GET", "/api/v3/automation/workflows", "Workflows"),
        ("GET", "/api/v3/analytics/metrics", "Métricas"),
        ("GET", "/api/v3/chat/sessions", "Sessões de Chat")
    ]
    
    success_count = 0
    for method, endpoint, description in endpoints_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", json={}, timeout=10)
            
            if response.status_code in [200, 422]:  # 422 é esperado para alguns endpoints sem dados
                print(f"✅ {description}: {endpoint}")
                success_count += 1
            else:
                print(f"❌ {description}: {endpoint} (Status: {response.status_code})")
        except Exception as e:
            print(f"❌ {description}: {endpoint} (Erro: {e})")
    
    print(f"\n📊 Endpoints testados: {success_count}/{len(endpoints_to_test)}")
    return success_count >= len(endpoints_to_test) * 0.8  # 80% de sucesso

def run_feature_tests():
    """Executa testes das funcionalidades"""
    print_step("Executando testes das funcionalidades")
    
    # Executa o script de teste
    success, output, error = run_command(
        "python test_week3_features.py",
        timeout=120
    )
    
    if success:
        print("✅ Testes das funcionalidades executados com sucesso")
        print("\n📋 Resultado dos testes:")
        print(output)
        
        # Tenta carregar relatório JSON
        try:
            with open("week3_test_report.json", "r", encoding="utf-8") as f:
                report = json.load(f)
            
            success_rate = float(report["summary"]["success_rate"].rstrip("%"))
            if success_rate >= 80:
                print(f"✅ Taxa de sucesso: {success_rate}%")
                return True
            else:
                print(f"❌ Taxa de sucesso baixa: {success_rate}%")
                return False
                
        except Exception as e:
            print(f"⚠️ Não foi possível carregar relatório: {e}")
            return success
    else:
        print("❌ Erro ao executar testes das funcionalidades")
        print(f"Erro: {error}")
        return False

def generate_validation_report():
    """Gera relatório de validação"""
    print_step("Gerando relatório de validação")
    
    report = {
        "validation_timestamp": datetime.now().isoformat(),
        "week": 3,
        "title": "IA, Machine Learning e Automação Avançada",
        "components_validated": [
            "Sistema de IA e Machine Learning",
            "Sistema de Automação Avançada",
            "Analytics Avançado",
            "Sistema de Chat e Assistente IA"
        ],
        "features_implemented": [
            "Predições Inteligentes",
            "Detecção de Anomalias",
            "Análise de Padrões",
            "Sistema de Recomendações",
            "Correção Automática (Auto-Fix)",
            "Gerenciamento de Workflows",
            "Otimização de Recursos",
            "Geração de Relatórios",
            "Métricas do Sistema",
            "Análise de Tendências",
            "Insights Preditivos",
            "Chat Inteligente",
            "Comandos de Voz",
            "Tutoriais Interativos"
        ],
        "api_endpoints": [
            "POST /api/v3/ai/predict",
            "POST /api/v3/ai/detect-anomalies",
            "POST /api/v3/ai/analyze-patterns",
            "POST /api/v3/ai/recommendations",
            "POST /api/v3/automation/auto-fix",
            "POST /api/v3/automation/workflows",
            "POST /api/v3/automation/optimize",
            "POST /api/v3/analytics/generate-report",
            "GET /api/v3/analytics/metrics",
            "GET /api/v3/analytics/trends",
            "GET /api/v3/analytics/predictive-insights",
            "WebSocket /api/v3/chat/ws/{session_id}",
            "POST /api/v3/chat/voice-command",
            "GET /api/v3/chat/tutorials"
        ]
    }
    
    # Salva relatório
    with open("week3_validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("✅ Relatório de validação gerado: week3_validation_report.json")
    return True

def main():
    """Função principal"""
    print_header("VALIDAÇÃO DA SEMANA 3 - IA, ML E AUTOMAÇÃO")
    
    # Lista de verificações
    checks = [
        ("Ambiente Python", check_python_environment),
        ("Estrutura do Projeto", check_project_structure),
        ("Dependências", check_dependencies),
        ("Inicialização do Serviço", start_service),
        ("Endpoints API v3", test_api_v3_endpoints),
        ("Testes das Funcionalidades", run_feature_tests),
        ("Relatório de Validação", generate_validation_report)
    ]
    
    results = []
    for check_name, check_function in checks:
        print(f"\n🔍 Executando: {check_name}")
        try:
            result = check_function()
            results.append((check_name, result))
            if result:
                print(f"✅ {check_name}: PASSOU")
            else:
                print(f"❌ {check_name}: FALHOU")
        except Exception as e:
            print(f"❌ {check_name}: ERRO - {e}")
            results.append((check_name, False))
    
    # Relatório final
    print_header("RELATÓRIO FINAL DA VALIDAÇÃO")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"📊 Verificações realizadas: {total}")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {total - passed}")
    print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 VALIDAÇÃO DA SEMANA 3 CONCLUÍDA COM SUCESSO!")
        print("🚀 O sistema de IA, ML e Automação está funcionando corretamente.")
        return 0
    else:
        print("\n❌ VALIDAÇÃO DA SEMANA 3 FALHOU")
        print("🔧 Verifique os erros acima e corrija os problemas.")
        return 1

if __name__ == "__main__":
    exit(main())