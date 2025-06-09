#!/usr/bin/env python
"""
Script para corrigir prefixos duplicados nos routers dos domínios
"""

import os
import re

def fix_router_prefixes():
    """Corrige os prefixos duplicados em todos os domínios"""
    
    # Mapeamento de arquivos e correções
    corrections = [
        {
            "file": "app/api/core/ai/endpoints.py",
            "old": 'router = APIRouter(prefix="/ai", tags=["Artificial Intelligence"])',
            "new": 'router = APIRouter(tags=["Artificial Intelligence"])'
        },
        {
            "file": "app/api/core/analytics/endpoints.py", 
            "old": 'router = APIRouter(prefix="/analytics", tags=["Analytics"])',
            "new": 'router = APIRouter(tags=["Analytics"])'
        },
        {
            "file": "app/api/core/automation/endpoints.py",
            "old": 'router = APIRouter(prefix="/automation", tags=["Automation"])',
            "new": 'router = APIRouter(tags=["Automation"])'
        },
        {
            "file": "app/api/core/chat/endpoints.py",
            "old": 'router = APIRouter(prefix="/chat", tags=["chat"])',
            "new": 'router = APIRouter(tags=["chat"])'
        },
        {
            "file": "app/api/core/integration/endpoints.py",
            "old": 'integration_router = APIRouter(prefix="/integration", tags=["Integration"])',
            "new": 'integration_router = APIRouter(tags=["Integration"])'
        }
    ]
    
    for correction in corrections:
        file_path = correction["file"]
        
        if not os.path.exists(file_path):
            print(f"⚠️ Arquivo não encontrado: {file_path}")
            continue
        
        # Ler arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se precisa de correção
        if correction["old"] in content:
            # Fazer a correção
            content = content.replace(correction["old"], correction["new"])
            
            # Escrever arquivo corrigido
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"✅ {file_path}: prefixo removido")
        else:
            print(f"✅ {file_path}: já correto")

def main():
    """Função principal"""
    print("🔧 Corrigindo prefixos duplicados...")
    fix_router_prefixes()
    print("✅ Correção concluída!")

if __name__ == "__main__":
    main() 