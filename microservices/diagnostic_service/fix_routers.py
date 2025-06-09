#!/usr/bin/env python
"""
Script para corrigir os nomes dos routers nos domínios da API Core
"""

import os
import glob

# Mapeamento de domínios para seus router names
domain_routers = {
    "auth": "router",
    "diagnostics": "router", 
    "ai": "router",
    "automation": "router",
    "analytics": "router",
    "performance": "router",
    "chat": "router",
    "integration": "integration_router"
}

def fix_router_names():
    """Corrige os nomes dos routers nos arquivos"""
    
    for domain, router_name in domain_routers.items():
        endpoints_file = f"app/api/core/{domain}/endpoints.py"
        
        if not os.path.exists(endpoints_file):
            print(f"⚠️ Arquivo não encontrado: {endpoints_file}")
            continue
        
        # Ler arquivo
        with open(endpoints_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Se o arquivo já usa o router correto, pular
        if f"@{router_name}.get" in content:
            print(f"✅ {domain}: router já correto ({router_name})")
            continue
        
        # Corrigir @router.get para o router correto
        if "@router.get" in content and router_name != "router":
            content = content.replace("@router.get", f"@{router_name}.get")
            print(f"🔧 {domain}: corrigido @router.get -> @{router_name}.get")
        
        # Escrever arquivo corrigido
        with open(endpoints_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ {domain}: arquivo processado")

def main():
    """Função principal"""
    print("🔧 Corrigindo nomes dos routers...")
    fix_router_names()
    print("✅ Correção concluída!")

if __name__ == "__main__":
    main() 