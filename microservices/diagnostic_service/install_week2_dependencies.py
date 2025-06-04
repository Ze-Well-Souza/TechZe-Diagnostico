#!/usr/bin/env python3
"""
Instalador de Dependências da Semana 2
Instala todas as dependências necessárias para as funcionalidades da Semana 2
"""
import subprocess
import sys

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

def install_package(package_name):
    """Instala um pacote específico"""
    try:
        print_status(f"Instalando {package_name}...", "INFO")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        print_status(f"✅ {package_name} instalado com sucesso", "SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"❌ Erro ao instalar {package_name}: {e}", "ERROR")
        return False

def main():
    """Função principal"""
    print_status("🚀 Instalando Dependências da Semana 2", "INFO")
    print("=" * 50)
    
    # Dependências específicas da Semana 2
    week2_dependencies = [
        "redis",
        "slowapi", 
        "prometheus-fastapi-instrumentator",
        "psutil"
    ]
    
    success_count = 0
    total_count = len(week2_dependencies)
    
    for package in week2_dependencies:
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print_status(f"📊 Resultado: {success_count}/{total_count} pacotes instalados", "INFO")
    
    if success_count == total_count:
        print_status("🎉 Todas as dependências foram instaladas com sucesso!", "SUCCESS")
        print_status("✅ Sistema pronto para executar funcionalidades da Semana 2", "SUCCESS")
        return 0
    else:
        print_status("⚠️ Algumas dependências falharam na instalação", "WARNING")
        print_status("🔧 Tente executar manualmente: pip install -r requirements.txt", "INFO")
        return 1

if __name__ == "__main__":
    sys.exit(main())