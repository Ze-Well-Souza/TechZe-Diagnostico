#!/usr/bin/env python3
"""
Script de setup completo do sistema TechZe
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*70)
    print(f"🚀 {title}")
    print("="*70)

def print_step(step):
    """Imprime passo formatado"""
    print(f"\n📋 {step}")
    print("-" * 50)

def run_command(command, cwd=None, check=True):
    """Executa comando e retorna resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            check=check
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_prerequisites():
    """Verifica pré-requisitos"""
    print_step("VERIFICANDO PRÉ-REQUISITOS")
    
    prerequisites = [
        ("python", "Python"),
        ("node", "Node.js"),
        ("npm", "NPM"),
    ]
    
    all_ok = True
    
    for command, name in prerequisites:
        success, stdout, stderr = run_command(f"{command} --version", check=False)
        
        if success:
            version = stdout.strip().split('\n')[0]
            print(f"   ✅ {name}: {version}")
        else:
            print(f"   ❌ {name}: Não encontrado")
            all_ok = False
    
    return all_ok

def setup_backend():
    """Configura backend"""
    print_step("CONFIGURANDO BACKEND")
    
    backend_path = Path("microservices/diagnostic_service")
    
    if not backend_path.exists():
        print("   ❌ Diretório do backend não encontrado")
        return False
    
    # Verificar requirements.txt
    requirements_file = backend_path / "requirements.txt"
    if requirements_file.exists():
        print("   📦 Instalando dependências Python...")
        success, stdout, stderr = run_command(
            "pip install -r requirements.txt", 
            cwd=backend_path
        )
        
        if success:
            print("   ✅ Dependências Python instaladas")
        else:
            print("   ⚠️ Erro ao instalar dependências Python")
            print(f"      {stderr}")
    
    # Verificar arquivo .env
    env_file = backend_path / ".env"
    env_example = backend_path / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("   📝 Criando arquivo .env...")
        try:
            with open(env_example, 'r') as f:
                content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(content)
            
            print("   ✅ Arquivo .env criado")
        except Exception as e:
            print(f"   ⚠️ Erro ao criar .env: {str(e)}")
    
    print("   ✅ Backend configurado")
    return True

def setup_frontend():
    """Configura frontend"""
    print_step("CONFIGURANDO FRONTEND")
    
    frontend_path = Path("frontend-v3")
    
    if not frontend_path.exists():
        print("   ❌ Diretório do frontend não encontrado")
        return False
    
    # Instalar dependências
    package_json = frontend_path / "package.json"
    if package_json.exists():
        print("   📦 Instalando dependências Node.js...")
        success, stdout, stderr = run_command("npm install", cwd=frontend_path)
        
        if success:
            print("   ✅ Dependências Node.js instaladas")
        else:
            print("   ⚠️ Erro ao instalar dependências Node.js")
            print(f"      {stderr}")
            return False
    
    print("   ✅ Frontend configurado")
    return True

def create_startup_scripts():
    """Cria scripts de inicialização"""
    print_step("CRIANDO SCRIPTS DE INICIALIZAÇÃO")
    
    # Script para Windows
    start_backend_bat = """@echo off
echo Iniciando Backend TechZe...
cd microservices\\diagnostic_service
python app\\main.py
pause
"""
    
    start_frontend_bat = """@echo off
echo Iniciando Frontend TechZe...
cd frontend-v3
npm run dev
pause
"""
    
    start_all_bat = """@echo off
echo Iniciando Sistema TechZe Completo...
echo.
echo Abrindo Backend...
start "TechZe Backend" cmd /k "cd microservices\\diagnostic_service && python app\\main.py"
timeout /t 3
echo.
echo Abrindo Frontend...
start "TechZe Frontend" cmd /k "cd frontend-v3 && npm run dev"
echo.
echo Sistema iniciado!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8081
echo.
pause
"""
    
    # Script para Linux/Mac
    start_backend_sh = """#!/bin/bash
echo "Iniciando Backend TechZe..."
cd microservices/diagnostic_service
python app/main.py
"""
    
    start_frontend_sh = """#!/bin/bash
echo "Iniciando Frontend TechZe..."
cd frontend-v3
npm run dev
"""
    
    start_all_sh = """#!/bin/bash
echo "Iniciando Sistema TechZe Completo..."
echo ""
echo "Abrindo Backend..."
gnome-terminal -- bash -c "cd microservices/diagnostic_service && python app/main.py; exec bash" &
sleep 3
echo ""
echo "Abrindo Frontend..."
gnome-terminal -- bash -c "cd frontend-v3 && npm run dev; exec bash" &
echo ""
echo "Sistema iniciado!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8081"
"""
    
    scripts = [
        ("start_backend.bat", start_backend_bat),
        ("start_frontend.bat", start_frontend_bat),
        ("start_all.bat", start_all_bat),
        ("start_backend.sh", start_backend_sh),
        ("start_frontend.sh", start_frontend_sh),
        ("start_all.sh", start_all_sh),
    ]
    
    for filename, content in scripts:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Tornar executável no Linux/Mac
            if filename.endswith('.sh'):
                os.chmod(filename, 0o755)
            
            print(f"   ✅ {filename} criado")
            
        except Exception as e:
            print(f"   ⚠️ Erro ao criar {filename}: {str(e)}")
    
    return True

def create_readme():
    """Cria README com instruções"""
    print_step("CRIANDO DOCUMENTAÇÃO")
    
    readme_content = """# TechZe - Sistema de Diagnóstico

## 🚀 Início Rápido

### Windows
```batch
# Iniciar tudo de uma vez
start_all.bat

# Ou iniciar separadamente
start_backend.bat
start_frontend.bat
```

### Linux/Mac
```bash
# Iniciar tudo de uma vez
./start_all.sh

# Ou iniciar separadamente
./start_backend.sh
./start_frontend.sh
```

### Manual
```bash
# Terminal 1 - Backend
cd microservices/diagnostic_service
python app/main.py

# Terminal 2 - Frontend
cd frontend-v3
npm run dev
```

## 🌐 URLs

- **Frontend**: http://localhost:8081
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Supabase**: https://supabase.com/dashboard/project/pkefwvvkydzzfstzwppv

## 🔧 Configuração

### Backend
1. Configure o arquivo `.env` em `microservices/diagnostic_service/`
2. Instale dependências: `pip install -r requirements.txt`

### Frontend
1. Instale dependências: `npm install`
2. Configure variáveis de ambiente se necessário

### Supabase
1. Acesse: https://supabase.com/dashboard/project/pkefwvvkydzzfstzwppv/sql
2. Execute os comandos em `supabase_rls_commands.sql`

## 🧪 Validação

```bash
# Validação completa do sistema
python validate_system.py

# Correção de problemas
python fix_critical_issues.py

# Aplicar políticas RLS
python apply_rls_manual.py
```

## 📁 Estrutura

```
TechZe-Diagnostico/
├── microservices/
│   └── diagnostic_service/     # Backend FastAPI
├── frontend-v3/                # Frontend React
├── start_*.bat                 # Scripts Windows
├── start_*.sh                  # Scripts Linux/Mac
└── *.py                        # Scripts de setup/validação
```

## 🆘 Problemas Comuns

### CORS Error
- Verificar se backend está na porta 8000
- Verificar se frontend está na porta 8081
- Reiniciar ambos os serviços

### Backend não inicia
- Verificar dependências Python
- Verificar arquivo .env
- Verificar logs de erro

### Frontend não carrega
- Executar `npm install`
- Verificar se porta 8081 está livre
- Verificar logs do console

## 📞 Suporte

Para problemas ou dúvidas, execute:
```bash
python validate_system.py
```

Este comando irá diagnosticar e sugerir soluções.
"""
    
    try:
        with open("README_SETUP.md", 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print("   ✅ README_SETUP.md criado")
        return True
        
    except Exception as e:
        print(f"   ⚠️ Erro ao criar README: {str(e)}")
        return False

def main():
    """Função principal"""
    print_header("SETUP COMPLETO DO SISTEMA TECHZE")
    
    print("🎯 Este script irá configurar todo o sistema TechZe automaticamente")
    print("   - Verificar pré-requisitos")
    print("   - Configurar backend")
    print("   - Configurar frontend")
    print("   - Criar scripts de inicialização")
    print("   - Criar documentação")
    
    input("\n📋 Pressione Enter para continuar...")
    
    # Verificar pré-requisitos
    if not check_prerequisites():
        print("\n❌ Pré-requisitos não atendidos. Instale as dependências necessárias.")
        return
    
    # Configurar backend
    if not setup_backend():
        print("\n⚠️ Problemas na configuração do backend")
    
    # Configurar frontend
    if not setup_frontend():
        print("\n⚠️ Problemas na configuração do frontend")
    
    # Criar scripts
    create_startup_scripts()
    
    # Criar documentação
    create_readme()
    
    # Instruções finais
    print_header("SETUP CONCLUÍDO!")
    
    print("🎉 Sistema TechZe configurado com sucesso!")
    print()
    print("📋 PRÓXIMOS PASSOS:")
    print()
    print("1. 🌐 Configurar Supabase:")
    print("   python apply_rls_manual.py")
    print()
    print("2. 🚀 Iniciar sistema:")
    print("   Windows: start_all.bat")
    print("   Linux/Mac: ./start_all.sh")
    print()
    print("3. ✅ Validar sistema:")
    print("   python validate_system.py")
    print()
    print("📖 Consulte README_SETUP.md para instruções detalhadas")
    print()
    print("🌐 URLs após inicialização:")
    print("   Frontend: http://localhost:8081")
    print("   Backend: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()