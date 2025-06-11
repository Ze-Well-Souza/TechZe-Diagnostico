#!/usr/bin/env python3
"""
Script para corrigir warnings de deprecação do datetime.utcnow()
Substitui datetime.utcnow() por datetime.now(timezone.utc)
"""

import os
import re
from pathlib import Path

def fix_datetime_deprecation(file_path):
    """Corrige o uso de datetime.utcnow() em um arquivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Verificar se já tem timezone importado
        has_timezone_import = 'from datetime import' in content and 'timezone' in content
        
        # Padrões para substituir
        patterns = [
            (r'datetime\.utcnow\(\)', 'datetime.now(timezone.utc)'),
        ]
        
        # Aplicar substituições
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        # Adicionar import do timezone se necessário e houve mudanças
        if content != original_content and not has_timezone_import:
            # Procurar por imports de datetime existentes
            datetime_import_patterns = [
                r'from datetime import datetime, timedelta',
                r'from datetime import datetime',
                r'from datetime import timedelta'
            ]
            
            for pattern in datetime_import_patterns:
                if re.search(pattern, content):
                    if 'timedelta' in pattern:
                        new_import = 'from datetime import datetime, timedelta, timezone'
                    else:
                        new_import = 'from datetime import datetime, timezone'
                    
                    content = re.sub(pattern, new_import, content)
                    break
        
        # Salvar apenas se houve mudanças
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corrigido: {file_path}")
            return True
        else:
            print(f"⏭️  Sem mudanças: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao processar {file_path}: {e}")
        return False

def main():
    """Função principal"""
    # Diretório base
    base_dir = Path(__file__).parent
    
    # Arquivos Python para processar
    python_files = []
    
    # Buscar todos os arquivos .py
    for root, dirs, files in os.walk(base_dir):
        # Pular diretórios de cache e venv
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'venv', '.venv']]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('fix_datetime_deprecation'):
                python_files.append(os.path.join(root, file))
    
    print(f"🔍 Encontrados {len(python_files)} arquivos Python")
    print("🔧 Iniciando correção de datetime.utcnow()...\n")
    
    fixed_count = 0
    
    for file_path in python_files:
        if fix_datetime_deprecation(file_path):
            fixed_count += 1
    
    print(f"\n✨ Concluído! {fixed_count} arquivos foram corrigidos.")
    print("\n📝 Mudanças realizadas:")
    print("   • datetime.utcnow() → datetime.now(timezone.utc)")
    print("   • Adicionado import timezone onde necessário")
    print("\n🧪 Execute os testes para verificar se tudo está funcionando:")
    print("   pytest tests/ -v")

if __name__ == "__main__":
    main()