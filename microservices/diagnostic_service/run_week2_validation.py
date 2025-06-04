#!/usr/bin/env python3
"""
Script Principal de Validação da Semana 2
Executa todos os testes e validações das funcionalidades implementadas
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 70)
    print(f"🚀 {title}")
    print("=" * 70)

def print_status(message, status="INFO"):
    """Imprime mensagem com status colorido"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}{status}: {message}{colors['RESET']}")

def run_command(command, description, timeout=60):
    """Executa comando e retorna resultado"""
    print_status(f"Executando: {description}", "INFO")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            print_status(f"✅ {description} - SUCESSO", "SUCCESS")
            return True, result.stdout
        else:
            print_status(f"❌ {description} - FALHOU", "ERROR")
            if result.stderr:
                print_status(f"Erro: {result.stderr[:200]}...", "ERROR")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print_status(f"⏰ {description} - TIMEOUT", "WARNING")
        return False, "Timeout"
    except Exception as e:
        print_status(f"❌ {description} - ERRO: {e}", "ERROR")
        return False, str(e)

def check_python_environment():
    """Verifica ambiente Python"""
    print_header("VERIFICAÇÃO DO AMBIENTE PYTHON")
    
    # Verifica versão do Python
    success, output = run_command("python --version", "Versão do Python")
    if success:
        print_status(f"Python: {output.strip()}", "INFO")
    
    # Verifica pip
    success, _ = run_command("pip --version", "Verificação do pip")
    
    # Verifica se está no diretório correto
    if os.path.exists("app/main.py"):
        print_status("✅ Diretório correto encontrado", "SUCCESS")
        return True
    else:
        print_status("❌ Diretório incorreto - app/main.py não encontrado", "ERROR")
        return False

def install_dependencies():
    """Instala dependências necessárias"""
    print_header("INSTALAÇÃO DE DEPENDÊNCIAS")
    
    # Verifica se requirements.txt existe
    if not os.path.exists("requirements.txt"):
        print_status("❌ requirements.txt não encontrado", "ERROR")
        return False
    
    # Instala dependências
    success, output = run_command(
        "pip install -r requirements.txt",
        "Instalação de dependências",
        timeout=300
    )
    
    if success:
        print_status("✅ Dependências instaladas com sucesso", "SUCCESS")
        return True
    else:
        print_status("⚠️ Algumas dependências podem ter falhado", "WARNING")
        # Tenta instalar dependências críticas individualmente
        critical_deps = [
            "fastapi",
            "uvicorn",
            "redis",
            "psutil",
            "prometheus-fastapi-instrumentator"
        ]
        
        for dep in critical_deps:
            run_command(f"pip install {dep}", f"Instalação de {dep}")
        
        return True

def validate_implementation():
    """Executa validação da implementação"""
    print_header("VALIDAÇÃO DA IMPLEMENTAÇÃO")
    
    success, output = run_command(
        "python validate_week2_implementation.py",
        "Validação da implementação da Semana 2"
    )
    
    if success:
        print_status("✅ Implementação validada com sucesso", "SUCCESS")
    else:
        print_status("❌ Falhas na validação da implementação", "ERROR")
    
    return success

def start_service_for_testing():
    """Inicia serviço para testes"""
    print_header("INICIANDO SERVIÇO PARA TESTES")
    
    print_status("Iniciando TechZe Diagnostic Service...", "INFO")
    print_status("Aguarde 10 segundos para o serviço inicializar", "INFO")
    
    # Inicia serviço em background
    try:
        process = subprocess.Popen(
            ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Aguarda inicialização
        time.sleep(10)
        
        # Verifica se processo ainda está rodando
        if process.poll() is None:
            print_status("✅ Serviço iniciado com sucesso", "SUCCESS")
            return True, process
        else:
            stdout, stderr = process.communicate()
            print_status(f"❌ Serviço falhou ao iniciar: {stderr[:200]}", "ERROR")
            return False, None
    except Exception as e:
        print_status(f"❌ Erro ao iniciar serviço: {e}", "ERROR")
        return False, None

def run_functional_tests(service_process):
    """Executa testes funcionais"""
    print_header("TESTES FUNCIONAIS")
    
    # Testa health check básico
    success, _ = run_command(
        'curl -s http://localhost:8000/health',
        "Health Check Básico"
    )
    
    if not success:
        print_status("⚠️ curl não disponível, tentando com Python", "WARNING")
        success, _ = run_command(
            'python -c "import requests; print(requests.get(\'http://localhost:8000/health\').status_code)"',
            "Health Check com Python"
        )
    
    # Executa testes completos da Semana 2
    success, output = run_command(
        "python test_week2_features.py",
        "Testes das funcionalidades da Semana 2",
        timeout=120
    )
    
    return success

def stop_service(service_process):
    """Para o serviço"""
    if service_process:
        print_status("Parando serviço...", "INFO")
        service_process.terminate()
        try:
            service_process.wait(timeout=5)
            print_status("✅ Serviço parado com sucesso", "SUCCESS")
        except subprocess.TimeoutExpired:
            service_process.kill()
            print_status("⚠️ Serviço forçado a parar", "WARNING")

def generate_report():
    """Gera relatório final"""
    print_header("RELATÓRIO FINAL")
    
    print_status("📋 FUNCIONALIDADES IMPLEMENTADAS NA SEMANA 2:", "INFO")
    print_status("", "INFO")
    print_status("✅ Monitoramento Avançado (advanced_monitoring.py)", "SUCCESS")
    print_status("   • Coleta de métricas de sistema em tempo real", "INFO")
    print_status("   • Sistema de alertas inteligente", "INFO")
    print_status("   • Dashboards operacional e de segurança", "INFO")
    print_status("", "INFO")
    print_status("✅ Sistema de Cache Avançado (cache_manager.py)", "SUCCESS")
    print_status("   • Cache Redis com fallback para memória", "INFO")
    print_status("   • Múltiplas estratégias de cache (LRU, LFU, TTL, FIFO)", "INFO")
    print_status("   • Estatísticas detalhadas e invalidação inteligente", "INFO")
    print_status("", "INFO")
    print_status("✅ Stack de Monitoramento Completo", "SUCCESS")
    print_status("   • Prometheus para coleta de métricas", "INFO")
    print_status("   • Grafana com dashboards pré-configurados", "INFO")
    print_status("   • Alertmanager para notificações", "INFO")
    print_status("   • Redis para cache distribuído", "INFO")
    print_status("", "INFO")
    print_status("✅ Novos Endpoints de API", "SUCCESS")
    print_status("   • /api/v1/monitoring/dashboard/operational", "INFO")
    print_status("   • /api/v1/monitoring/dashboard/security", "INFO")
    print_status("   • /api/v1/monitoring/alerts", "INFO")
    print_status("   • /api/v1/cache/stats", "INFO")
    print_status("   • /api/v1/alerts/webhook", "INFO")
    print_status("", "INFO")
    print_status("✅ Ferramentas de Configuração", "SUCCESS")
    print_status("   • setup_monitoring_stack.py - Setup automático", "INFO")
    print_status("   • test_week2_features.py - Testes completos", "INFO")
    print_status("   • validate_week2_implementation.py - Validação", "INFO")
    print_status("", "INFO")
    print_status("📚 DOCUMENTAÇÃO COMPLETA:", "INFO")
    print_status("   • WEEK2_FEATURES.md - Documentação detalhada", "INFO")
    print_status("   • Configurações Prometheus/Grafana", "INFO")
    print_status("   • Scripts de setup e teste", "INFO")
    print_status("", "INFO")
    print_status("🎯 PRÓXIMOS PASSOS:", "INFO")
    print_status("   1. Executar: python setup_monitoring_stack.py", "INFO")
    print_status("   2. Acessar Grafana: http://localhost:3000", "INFO")
    print_status("   3. Monitorar métricas: http://localhost:9090", "INFO")
    print_status("   4. Testar APIs: http://localhost:8000/docs", "INFO")

def main():
    """Função principal"""
    print_header("VALIDAÇÃO COMPLETA DA SEMANA 2 - TECHZE DIAGNOSTIC SERVICE")
    
    # Muda para o diretório correto
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Etapas de validação
    steps = [
        ("Verificação do Ambiente", check_python_environment),
        ("Instalação de Dependências", install_dependencies),
        ("Validação da Implementação", validate_implementation)
    ]
    
    results = []
    
    # Executa etapas básicas
    for step_name, step_func in steps:
        try:
            result = step_func()
            results.append((step_name, result))
            if not result and step_name == "Verificação do Ambiente":
                print_status("❌ Ambiente inválido, abortando", "ERROR")
                return 1
        except Exception as e:
            print_status(f"❌ Erro em {step_name}: {e}", "ERROR")
            results.append((step_name, False))
    
    # Tenta iniciar serviço e executar testes
    service_started, service_process = start_service_for_testing()
    if service_started:
        try:
            test_result = run_functional_tests(service_process)
            results.append(("Testes Funcionais", test_result))
        finally:
            stop_service(service_process)
    else:
        results.append(("Testes Funcionais", False))
        print_status("⚠️ Testes funcionais pulados devido a falha no serviço", "WARNING")
    
    # Gera relatório final
    generate_report()
    
    # Resumo final
    print_header("RESUMO FINAL")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for step_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print_status(f"{status} {step_name}", "SUCCESS" if result else "ERROR")
    
    success_rate = (passed / total) * 100
    print_status(f"📈 Taxa de Sucesso: {passed}/{total} ({success_rate:.1f}%)", "INFO")
    
    if passed == total:
        print_status("🎉 VALIDAÇÃO COMPLETA - SEMANA 2 IMPLEMENTADA COM SUCESSO!", "SUCCESS")
        return 0
    else:
        print_status("⚠️ VALIDAÇÃO PARCIAL - ALGUMAS ETAPAS FALHARAM", "WARNING")
        return 1

if __name__ == "__main__":
    sys.exit(main())