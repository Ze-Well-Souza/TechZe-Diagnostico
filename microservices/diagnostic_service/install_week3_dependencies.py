#!/usr/bin/env python3
"""
Script para instalar dependências da Semana 3 - IA, ML e Automação
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def print_step(step: str):
    """Imprime passo atual"""
    print(f"\n📋 {step}")
    print("-" * 40)

def run_pip_install(packages: list, description: str = ""):
    """Instala pacotes via pip"""
    if description:
        print(f"\n📦 Instalando {description}...")
    
    for package in packages:
        print(f"⏳ Instalando {package}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode == 0:
                print(f"✅ {package} instalado com sucesso")
            else:
                print(f"❌ Erro ao instalar {package}:")
                print(result.stderr)
                return False
        except subprocess.TimeoutExpired:
            print(f"❌ Timeout ao instalar {package}")
            return False
        except Exception as e:
            print(f"❌ Erro inesperado ao instalar {package}: {e}")
            return False
    
    return True

def install_core_dependencies():
    """Instala dependências principais"""
    print_step("Instalando dependências principais")
    
    core_packages = [
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "pydantic>=2.5.0",
        "python-multipart>=0.0.6",
        "websockets>=12.0"
    ]
    
    return run_pip_install(core_packages, "dependências principais")

def install_ai_ml_dependencies():
    """Instala dependências de IA e ML"""
    print_step("Instalando dependências de IA e Machine Learning")
    
    ai_ml_packages = [
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "scipy>=1.11.0",
        "matplotlib>=3.7.0",
        "seaborn>=0.12.0",
        "plotly>=5.17.0"
    ]
    
    return run_pip_install(ai_ml_packages, "dependências de IA e ML")

def install_nlp_dependencies():
    """Instala dependências de NLP"""
    print_step("Instalando dependências de Processamento de Linguagem Natural")
    
    nlp_packages = [
        "nltk>=3.8.0",
        "spacy>=3.7.0",
        "transformers>=4.35.0",
        "torch>=2.1.0",
        "sentence-transformers>=2.2.0"
    ]
    
    # Instala pacotes básicos primeiro
    basic_nlp = ["nltk>=3.8.0"]
    if not run_pip_install(basic_nlp, "NLP básico"):
        return False
    
    # Tenta instalar pacotes mais pesados
    print("\n⚠️ Instalando pacotes de ML mais pesados (pode demorar)...")
    heavy_packages = ["torch>=2.1.0", "transformers>=4.35.0"]
    
    for package in heavy_packages:
        print(f"⏳ Tentando instalar {package}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package, "--timeout", "600"],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos
            )
            
            if result.returncode == 0:
                print(f"✅ {package} instalado com sucesso")
            else:
                print(f"⚠️ Falha ao instalar {package} (opcional)")
                print("💡 Você pode instalar manualmente depois se necessário")
        except:
            print(f"⚠️ Timeout ou erro ao instalar {package} (opcional)")
    
    return True

def install_automation_dependencies():
    """Instala dependências de automação"""
    print_step("Instalando dependências de Automação")
    
    automation_packages = [
        "psutil>=5.9.0",
        "schedule>=1.2.0",
        "croniter>=1.4.0",
        "apscheduler>=3.10.0"
    ]
    
    return run_pip_install(automation_packages, "dependências de automação")

def install_analytics_dependencies():
    """Instala dependências de analytics"""
    print_step("Instalando dependências de Analytics")
    
    analytics_packages = [
        "plotly>=5.17.0",
        "dash>=2.14.0",
        "bokeh>=3.3.0",
        "altair>=5.1.0"
    ]
    
    return run_pip_install(analytics_packages, "dependências de analytics")

def install_voice_dependencies():
    """Instala dependências de voz (opcionais)"""
    print_step("Instalando dependências de Voz (opcionais)")
    
    voice_packages = [
        "speechrecognition>=3.10.0",
        "pyttsx3>=2.90",
        "pyaudio>=0.2.11"
    ]
    
    print("⚠️ Dependências de voz são opcionais e podem falhar em alguns sistemas")
    
    for package in voice_packages:
        print(f"⏳ Tentando instalar {package}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"✅ {package} instalado com sucesso")
            else:
                print(f"⚠️ Falha ao instalar {package} (opcional)")
        except:
            print(f"⚠️ Erro ao instalar {package} (opcional)")
    
    return True

def install_additional_dependencies():
    """Instala dependências adicionais"""
    print_step("Instalando dependências adicionais")
    
    additional_packages = [
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-dotenv>=1.0.0",
        "aiofiles>=23.2.0",
        "httpx>=0.25.0"
    ]
    
    return run_pip_install(additional_packages, "dependências adicionais")

def create_requirements_week3():
    """Cria arquivo requirements específico da Semana 3"""
    print_step("Criando arquivo requirements-week3.txt")
    
    requirements_content = """# Semana 3 - IA, Machine Learning e Automação
# Dependências principais
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
python-multipart>=0.0.6
websockets>=12.0

# IA e Machine Learning
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
scipy>=1.11.0
matplotlib>=3.7.0
seaborn>=0.12.0
plotly>=5.17.0

# NLP (Processamento de Linguagem Natural)
nltk>=3.8.0
# spacy>=3.7.0  # Opcional - instalar manualmente se necessário
# transformers>=4.35.0  # Opcional - instalar manualmente se necessário
# torch>=2.1.0  # Opcional - instalar manualmente se necessário

# Automação
psutil>=5.9.0
schedule>=1.2.0
croniter>=1.4.0
apscheduler>=3.10.0

# Analytics
dash>=2.14.0
bokeh>=3.3.0
altair>=5.1.0

# Voz (opcionais)
# speechrecognition>=3.10.0  # Opcional
# pyttsx3>=2.90  # Opcional
# pyaudio>=0.2.11  # Opcional

# Dependências adicionais
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-dotenv>=1.0.0
aiofiles>=23.2.0
httpx>=0.25.0
"""
    
    try:
        with open("requirements-week3.txt", "w", encoding="utf-8") as f:
            f.write(requirements_content)
        print("✅ Arquivo requirements-week3.txt criado com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar requirements-week3.txt: {e}")
        return False

def verify_installations():
    """Verifica se as instalações foram bem-sucedidas"""
    print_step("Verificando instalações")
    
    packages_to_verify = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "numpy",
        "pandas",
        "sklearn",
        "psutil",
        "schedule",
        "plotly"
    ]
    
    failed_packages = []
    
    for package in packages_to_verify:
        try:
            __import__(package)
            print(f"✅ {package}: OK")
        except ImportError:
            failed_packages.append(package)
            print(f"❌ {package}: Não encontrado")
    
    if failed_packages:
        print(f"\n❌ {len(failed_packages)} pacotes não foram instalados corretamente:")
        for package in failed_packages:
            print(f"  - {package}")
        return False
    else:
        print(f"\n✅ Todos os {len(packages_to_verify)} pacotes principais estão disponíveis")
        return True

def main():
    """Função principal"""
    print_header("INSTALAÇÃO DE DEPENDÊNCIAS - SEMANA 3")
    print("🤖 IA, Machine Learning e Automação Avançada")
    
    # Lista de instalações
    installations = [
        ("Dependências Principais", install_core_dependencies),
        ("IA e Machine Learning", install_ai_ml_dependencies),
        ("NLP", install_nlp_dependencies),
        ("Automação", install_automation_dependencies),
        ("Analytics", install_analytics_dependencies),
        ("Voz (Opcional)", install_voice_dependencies),
        ("Dependências Adicionais", install_additional_dependencies),
        ("Requirements File", create_requirements_week3),
        ("Verificação", verify_installations)
    ]
    
    results = []
    for install_name, install_function in installations:
        print(f"\n🔧 Executando: {install_name}")
        try:
            result = install_function()
            results.append((install_name, result))
            if result:
                print(f"✅ {install_name}: CONCLUÍDO")
            else:
                print(f"❌ {install_name}: FALHOU")
        except Exception as e:
            print(f"❌ {install_name}: ERRO - {e}")
            results.append((install_name, False))
    
    # Relatório final
    print_header("RELATÓRIO DE INSTALAÇÃO")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"📊 Instalações realizadas: {total}")
    print(f"✅ Sucesso: {passed}")
    print(f"❌ Falhas: {total - passed}")
    print(f"📈 Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("\n🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print("🚀 As dependências da Semana 3 estão prontas.")
        print("\n💡 Próximos passos:")
        print("1. Execute: python run_week3_validation.py")
        print("2. Teste as funcionalidades de IA e ML")
        print("3. Configure os modelos de ML conforme necessário")
        return 0
    else:
        print("\n❌ INSTALAÇÃO INCOMPLETA")
        print("🔧 Algumas dependências falharam. Verifique os erros acima.")
        print("\n💡 Você pode:")
        print("1. Tentar instalar manualmente os pacotes que falharam")
        print("2. Usar: pip install -r requirements-week3.txt")
        print("3. Continuar com as dependências disponíveis")
        return 1

if __name__ == "__main__":
    exit(main())