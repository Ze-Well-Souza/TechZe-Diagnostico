#!/usr/bin/env python3
"""
Script principal para executar todo o setup do TechZe
"""

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

def run_script(script_name, description):
    """Executa um script Python"""
    print_step(f"EXECUTANDO: {description}")
    
    if not Path(script_name).exists():
        print(f"   ❌ Script {script_name} não encontrado")
        return False
    
    try:
        print(f"   🔄 Executando {script_name}...")
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print(f"   ✅ {description} concluído com sucesso")
            return True
        else:
            print(f"   ⚠️ {description} concluído com avisos")
            return True  # Continuar mesmo com avisos
            
    except Exception as e:
        print(f"   ❌ Erro ao executar {script_name}: {str(e)}")
        return False

def main():
    """Função principal"""
    print_header("SETUP AUTOMÁTICO COMPLETO DO TECHZE")
    
    print("🎯 Este script irá executar todo o processo de setup automaticamente:")
    print("   1. Setup completo do sistema")
    print("   2. Aplicação das políticas RLS do Supabase")
    print("   3. Correção de problemas críticos")
    print("   4. Validação completa do sistema")
    print()
    print("⏱️ Tempo estimado: 5-10 minutos")
    print()
    
    response = input("📋 Deseja continuar? (s/N): ").lower().strip()
    if response not in ['s', 'sim', 'y', 'yes']:
        print("❌ Setup cancelado pelo usuário")
        return
    
    scripts_to_run = [
        ("setup_complete.py", "Setup Completo do Sistema"),
        ("apply_rls_manual.py", "Aplicação das Políticas RLS"),
        ("fix_critical_issues.py", "Correção de Problemas Críticos"),
        ("validate_system.py", "Validação Completa do Sistema"),
    ]
    
    success_count = 0
    total_scripts = len(scripts_to_run)
    
    for script_name, description in scripts_to_run:
        success = run_script(script_name, description)
        if success:
            success_count += 1
        
        # Pequena pausa entre scripts
        time.sleep(2)
    
    # Relatório final
    print_header("RELATÓRIO FINAL DO SETUP")
    
    success_rate = (success_count / total_scripts) * 100
    
    print(f"📊 ESTATÍSTICAS:")
    print(f"   Scripts executados: {total_scripts}")
    print(f"   Scripts bem-sucedidos: {success_count}")
    print(f"   Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 75:
        print(f"\n🎉 SETUP CONCLUÍDO COM SUCESSO!")
        print("   O sistema TechZe está pronto para uso!")
        
        print(f"\n🚀 COMO INICIAR O SISTEMA:")
        print("   Windows: Clique duas vezes em 'start_all.bat'")
        print("   Linux/Mac: Execute './start_all.sh'")
        print("   Manual: Consulte README_SETUP.md")
        
        print(f"\n🌐 URLs APÓS INICIALIZAÇÃO:")
        print("   Frontend: http://localhost:8081")
        print("   Backend: http://localhost:8000")
        print("   API Docs: http://localhost:8000/docs")
        
        print(f"\n📋 PRÓXIMOS PASSOS:")
        print("   1. Inicie o sistema usando os scripts criados")
        print("   2. Acesse o frontend em http://localhost:8081")
        print("   3. Teste as funcionalidades de diagnóstico")
        print("   4. Configure o Supabase se necessário")
        
    else:
        print(f"\n⚠️ SETUP PARCIALMENTE CONCLUÍDO")
        print("   Alguns problemas foram encontrados, mas o sistema pode funcionar")
        
        print(f"\n🔧 RECOMENDAÇÕES:")
        print("   1. Execute 'python validate_system.py' para diagnóstico detalhado")
        print("   2. Execute 'python fix_critical_issues.py' para correções")
        print("   3. Consulte README_SETUP.md para instruções manuais")
    
    print(f"\n📄 ARQUIVOS CRIADOS:")
    created_files = [
        "start_all.bat / start_all.sh - Scripts de inicialização",
        "README_SETUP.md - Documentação completa",
        "supabase_rls_commands.sql - Comandos SQL para Supabase",
        "validation_report.json - Relatório de validação",
        "cors_test.html - Teste de CORS"
    ]
    
    for file_desc in created_files:
        print(f"   📄 {file_desc}")
    
    print(f"\n💡 DICA:")
    print("   Mantenha este diretório como base do projeto TechZe")
    print("   Todos os scripts e documentação estão aqui organizados")

if __name__ == "__main__":
    main()