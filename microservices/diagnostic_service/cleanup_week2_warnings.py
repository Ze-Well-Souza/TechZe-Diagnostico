#!/usr/bin/env python3
"""
Script para limpar avisos de importações não utilizadas apenas nos arquivos da Semana 2
Não toca nos arquivos da primeira semana para não impactar o progresso do usuário
"""
import os
import re

def clean_unused_imports(file_path, unused_imports):
    """Remove importações não utilizadas de um arquivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for import_name in unused_imports:
            # Remove importação individual
            pattern1 = rf'^import {re.escape(import_name)}\n'
            content = re.sub(pattern1, '', content, flags=re.MULTILINE)
            
            # Remove de importação múltipla
            pattern2 = rf'from .+ import .+{re.escape(import_name)}.+\n'
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                if f'import ' in line and import_name in line:
                    # Se é uma linha de import múltiplo, remove apenas o item
                    if ',' in line and f'import ' in line:
                        imports = line.split('import ')[1].split(',')
                        imports = [imp.strip() for imp in imports if imp.strip() != import_name]
                        if imports:
                            line = line.split('import ')[0] + 'import ' + ', '.join(imports)
                        else:
                            continue  # Remove a linha inteira se não sobrou nada
                    elif f'import {import_name}' in line:
                        continue  # Remove a linha inteira
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
        
        # Remove linhas vazias duplas
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Limpeza aplicada em: {file_path}")
            return True
        else:
            print(f"ℹ️ Nenhuma mudança necessária em: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False

def main():
    """Função principal"""
    print("🧹 Limpando avisos de importações não utilizadas - Semana 2")
    print("=" * 60)
    
    # Apenas arquivos da Semana 2 - NÃO toca nos arquivos da primeira semana
    week2_files = {
        "app/core/advanced_monitoring.py": ["json"],
        "app/core/cache_manager.py": ["time", "Union"],
        "setup_monitoring_stack.py": ["Path"],
        "test_week2_features.py": ["asyncio", "json", "datetime"],
        "run_week2_validation.py": ["output", "stdout", "service_process"],
        "install_week2_dependencies.py": ["result"]
    }
    
    cleaned_files = 0
    
    for file_path, unused_imports in week2_files.items():
        if os.path.exists(file_path):
            if clean_unused_imports(file_path, unused_imports):
                cleaned_files += 1
        else:
            print(f"⚠️ Arquivo não encontrado: {file_path}")
    
    print("\n" + "=" * 60)
    print(f"📊 Resultado: {cleaned_files} arquivos limpos")
    print("✅ Limpeza concluída - arquivos da primeira semana não foram tocados")

if __name__ == "__main__":
    main()