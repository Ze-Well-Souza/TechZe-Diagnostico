#!/usr/bin/env python3
"""
Script para executar todos os testes do TechZe Diagnóstico
Inclui testes unitários, de integração e de cobertura
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))


def run_command(command, description):
    """Executa um comando e retorna o resultado"""
    print(f"\n🔄 {description}")
    print(f"Executando: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            cwd=Path(__file__).parent.parent
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {description} - Falha")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Erro ao executar {description}: {e}")
        return False


def install_dependencies():
    """Instala dependências de teste"""
    print("📦 Verificando dependências de teste...")
    
    dependencies = [
        "pytest",
        "pytest-asyncio", 
        "pytest-cov",
        "pytest-mock",
        "pytest-xdist"  # Para execução paralela
    ]
    
    for dep in dependencies:
        success = run_command(
            ["pip", "install", dep],
            f"Instalando {dep}"
        )
        if not success:
            print(f"⚠️ Falha ao instalar {dep}, continuando...")


def run_unit_tests(coverage=False, verbose=False):
    """Executa testes unitários"""
    command = ["python", "-m", "pytest", "tests/"]
    
    if coverage:
        command.extend([
            "--cov=app",
            "--cov-report=html:htmlcov",
            "--cov-report=term-missing",
            "--cov-report=xml"
        ])
    
    if verbose:
        command.append("-v")
    
    # Adiciona marcadores para excluir testes de integração por padrão
    command.extend(["-m", "not integration"])
    
    return run_command(command, "Executando testes unitários")


def run_integration_tests(verbose=False):
    """Executa testes de integração"""
    command = ["python", "-m", "pytest", "tests/", "-m", "integration"]
    
    if verbose:
        command.append("-v")
    
    return run_command(command, "Executando testes de integração")


def run_linting():
    """Executa verificações de estilo de código"""
    commands = [
        (["flake8", "app/", "tests/"], "Verificação Flake8"),
        (["black", "--check", "app/", "tests/"], "Verificação Black"),
        (["isort", "--check-only", "app/", "tests/"], "Verificação isort")
    ]
    
    results = []
    for command, description in commands:
        try:
            result = run_command(command, description)
            results.append(result)
        except Exception:
            print(f"⚠️ {description} não disponível, instalando...")
            # Tenta instalar a ferramenta
            tool_name = command[0]
            subprocess.run(["pip", "install", tool_name], capture_output=True)
            result = run_command(command, description)
            results.append(result)
    
    return all(results)


def run_security_checks():
    """Executa verificações de segurança"""
    commands = [
        (["safety", "check"], "Verificação de segurança (Safety)"),
        (["bandit", "-r", "app/"], "Verificação de vulnerabilidades (Bandit)")
    ]
    
    results = []
    for command, description in commands:
        try:
            result = run_command(command, description)
            results.append(result)
        except Exception:
            print(f"⚠️ {description} não disponível")
            results.append(True)  # Não falha se não estiver disponível
    
    return all(results)


def generate_coverage_report():
    """Gera relatório de cobertura detalhado"""
    print("\n📊 Gerando relatório de cobertura...")
    
    # Verifica se existe arquivo de cobertura
    coverage_file = Path("htmlcov/index.html")
    if coverage_file.exists():
        print(f"✅ Relatório de cobertura disponível em: {coverage_file.absolute()}")
        print("🌐 Abra o arquivo no navegador para visualizar o relatório detalhado")
    else:
        print("⚠️ Arquivo de cobertura não encontrado. Execute os testes com --coverage primeiro.")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description="Executa testes do TechZe Diagnóstico")
    parser.add_argument("--coverage", action="store_true", help="Gera relatório de cobertura")
    parser.add_argument("--integration", action="store_true", help="Executa testes de integração")
    parser.add_argument("--lint", action="store_true", help="Executa verificações de linting")
    parser.add_argument("--security", action="store_true", help="Executa verificações de segurança")
    parser.add_argument("--all", action="store_true", help="Executa todos os tipos de teste")
    parser.add_argument("--verbose", "-v", action="store_true", help="Saída verbosa")
    parser.add_argument("--install-deps", action="store_true", help="Instala dependências de teste")
    
    args = parser.parse_args()
    
    print("🧪 TechZe Diagnóstico - Execução de Testes")
    print("=" * 50)
    
    # Instala dependências se solicitado
    if args.install_deps or args.all:
        install_dependencies()
    
    results = []
    
    # Executa testes unitários (sempre executado)
    success = run_unit_tests(coverage=args.coverage or args.all, verbose=args.verbose)
    results.append(("Testes Unitários", success))
    
    # Executa testes de integração se solicitado
    if args.integration or args.all:
        success = run_integration_tests(verbose=args.verbose)
        results.append(("Testes de Integração", success))
    
    # Executa linting se solicitado
    if args.lint or args.all:
        success = run_linting()
        results.append(("Verificações de Linting", success))
    
    # Executa verificações de segurança se solicitado
    if args.security or args.all:
        success = run_security_checks()
        results.append(("Verificações de Segurança", success))
    
    # Gera relatório de cobertura se solicitado
    if args.coverage or args.all:
        generate_coverage_report()
    
    # Resumo final
    print("\n" + "=" * 50)
    print("📋 RESUMO DOS TESTES")
    print("=" * 50)
    
    all_passed = True
    for test_type, passed in results:
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_type}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Todos os testes passaram com sucesso!")
        exit_code = 0
    else:
        print("\n💥 Alguns testes falharam. Verifique os logs acima.")
        exit_code = 1
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    if not args.coverage:
        print("   - Execute com --coverage para ver cobertura de código")
    if not args.integration:
        print("   - Execute com --integration para testes de integração")
    if not args.lint:
        print("   - Execute com --lint para verificações de qualidade")
    
    print(f"\n🏁 Execução finalizada com código: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 