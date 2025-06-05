#!/usr/bin/env python3
"""
Script para corrigir os usos de regex= para pattern= em modelos Pydantic
"""

import os
import re
from pathlib import Path

def fix_regex_patterns(directory):
    """Corrige regex= para pattern= em todos os arquivos Python"""
    python_files = list(Path(directory).rglob("*.py"))
    fixed_count = 0
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Substituir regex= por pattern=
            new_content = re.sub(r'\bregex=', 'pattern=', content)
            
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Fixed: {file_path}")
                fixed_count += 1
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    print(f"\n🎯 Fixed {fixed_count} files")

if __name__ == "__main__":
    # Corrige os arquivos do microserviço
    fix_regex_patterns("microservices/diagnostic_service")
    print("🚀 All regex patterns fixed!") 