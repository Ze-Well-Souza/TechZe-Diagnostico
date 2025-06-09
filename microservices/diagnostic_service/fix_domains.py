#!/usr/bin/env python
"""
Script para adicionar endpoints /info e /health em todos os domínios da API Core
"""

import os
from pathlib import Path

# Definir domínios e suas informações
domains_info = {
    "diagnostics": {
        "name": "Diagnostics Domain", 
        "description": "Diagnóstico de hardware e software",
        "features": ["System Diagnostics", "Hardware Analysis", "Performance Tests"]
    },
    "ai": {
        "name": "AI Domain",
        "description": "Inteligência artificial e análise automatizada", 
        "features": ["AI Analysis", "Machine Learning", "Predictive Analysis"]
    },
    "automation": {
        "name": "Automation Domain",
        "description": "Automação de processos e workflows",
        "features": ["Workflow Automation", "Task Scheduling", "Process Management"]
    },
    "analytics": {
        "name": "Analytics Domain", 
        "description": "Análise de dados e métricas",
        "features": ["Data Analysis", "Reports Generation", "Metrics Tracking"]
    },
    "performance": {
        "name": "Performance Domain",
        "description": "Análise de performance e otimização",
        "features": ["Performance Monitoring", "Optimization", "Resource Analysis"]
    },
    "chat": {
        "name": "Chat Domain",
        "description": "Chat e comunicação em tempo real", 
        "features": ["Real-time Chat", "WebSocket Support", "Message History"]
    },
    "integration": {
        "name": "Integration Domain",
        "description": "Integração com sistemas externos",
        "features": ["External APIs", "Data Sync", "Webhook Support"]
    }
}

def add_endpoints_to_domain(domain_name, domain_info):
    """Adiciona endpoints /info e /health a um domínio"""
    
    endpoints_file = f"app/api/core/{domain_name}/endpoints.py"
    
    if not os.path.exists(endpoints_file):
        print(f"⚠️ Arquivo não encontrado: {endpoints_file}")
        return
    
    # Ler arquivo atual
    with open(endpoints_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Verificar se já tem os endpoints
    if "/info" in content and "/health" in content:
        print(f"✅ {domain_name}: endpoints já existem")
        return
    
    # Template para os novos endpoints
    info_endpoint = f'''
@router.get("/info")
async def {domain_name}_info():
    """
    Informações do domínio {domain_name}
    """
    return {{
        "domain": "{domain_name}",
        "name": "{domain_info['name']}",
        "version": "1.0.0", 
        "description": "{domain_info['description']}",
        "features": {domain_info['features']},
        "status": "active"
    }}

@router.get("/health")
async def {domain_name}_health_check():
    """
    Health check do domínio {domain_name}
    """
    return {{
        "status": "healthy",
        "domain": "{domain_name}",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }}
'''
    
    # Adicionar import datetime se não existir
    if "from datetime import datetime" not in content:
        content = content.replace(
            "from fastapi import",
            "from datetime import datetime\nfrom fastapi import"
        )
    
    # Adicionar endpoints no final do arquivo
    content = content.rstrip() + "\n" + info_endpoint + "\n"
    
    # Escrever arquivo atualizado
    with open(endpoints_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {domain_name}: endpoints adicionados")

def main():
    """Função principal"""
    print("🔧 Adicionando endpoints /info e /health aos domínios...")
    
    for domain_name, domain_info in domains_info.items():
        add_endpoints_to_domain(domain_name, domain_info)
    
    print("✅ Processo concluído!")

if __name__ == "__main__":
    main() 