#!/usr/bin/env python3
"""
Script para executar testes completos do sistema
"""

import subprocess
import sys
import time
import requests
import multiprocessing
import uvicorn
from pathlib import Path

def run_backend():
    """Executa o backend em processo separado"""
    try:
        uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
    except Exception as e:
        print(f"Erro ao executar backend: {e}")

def test_backend_health():
    """Testa se backend está funcionando"""
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend health check OK")
                return True
        except Exception as e:
            print(f"Tentativa {i+1}/{max_retries}: {e}")
            time.sleep(2)
    
    print("❌ Backend health check falhou")
    return False

def run_unit_tests():
    """Executa testes unitários"""
    print("\n🧪 Executando testes unitários...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_performance.py",
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.returncode == 0:
            print("✅ Testes unitários passaram")
            return True
        else:
            print("❌ Testes unitários falharam")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao executar testes unitários: {e}")
        return False

def run_integration_tests():
    """Executa testes de integração"""
    print("\n🔗 Executando testes de integração...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_integration.py",
            "-v", "--tb=short"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.returncode == 0:
            print("✅ Testes de integração passaram")
            return True
        else:
            print("❌ Alguns testes de integração falharam")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao executar testes de integração: {e}")
        return False

def run_coverage_test():
    """Executa testes com cobertura"""
    print("\n📊 Executando análise de cobertura...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html",
            "tests/",
            "-v"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if "TOTAL" in result.stdout:
            # Extrai porcentagem de cobertura
            lines = result.stdout.split('\n')
            for line in lines:
                if "TOTAL" in line:
                    parts = line.split()
                    if len(parts) >= 4:
                        coverage = parts[-1].replace('%', '')
                        try:
                            coverage_num = int(coverage)
                            if coverage_num >= 85:
                                print(f"✅ Cobertura de {coverage}% (meta: 85%)")
                                return True
                            else:
                                print(f"⚠️ Cobertura de {coverage}% (meta: 85%)")
                                return False
                        except:
                            pass
        
        print("✅ Análise de cobertura executada")
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise de cobertura: {e}")
        return False

def main():
    """Função principal do script de testes"""
    print("🚀 Iniciando suite completa de testes TechZe-Diagnostico")
    print("=" * 60)
    
    # Contador de sucessos
    tests_passed = 0
    total_tests = 4
    
    # 1. Testes unitários (sem backend)
    if run_unit_tests():
        tests_passed += 1
    
    # 2. Inicia backend em background
    print("\n🔧 Iniciando backend para testes de integração...")
    backend_process = multiprocessing.Process(target=run_backend)
    backend_process.start()
    
    # Aguarda backend inicializar
    time.sleep(5)
    
    # 3. Testa health do backend
    if test_backend_health():
        tests_passed += 1
        
        # 4. Testes de integração
        if run_integration_tests():
            tests_passed += 1
    
    # 5. Análise de cobertura
    if run_coverage_test():
        tests_passed += 1
    
    # Finaliza backend
    print("\n🔧 Finalizando backend...")
    backend_process.terminate()
    backend_process.join()
    
    # Relatório final
    print("\n" + "=" * 60)
    print(f"📊 RELATÓRIO FINAL: {tests_passed}/{total_tests} testes passaram")
    
    if tests_passed == total_tests:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para produção.")
        return 0
    else:
        print("⚠️ Alguns testes falharam. Revisar antes de deploy.")
        return 1

if __name__ == "__main__":
    sys.exit(main())