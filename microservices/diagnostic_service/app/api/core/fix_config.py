#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para adicionar model_config a todas as classes BaseSettings.
"""

import re

def fix_config_classes():
    """Adiciona model_config a todas as classes BaseSettings que não o possuem."""
    
    # Ler o arquivo config.py
    with open('config.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Texto do model_config para adicionar
    model_config_text = '''
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }'''
    
    # Lista de classes que precisam de model_config
    config_classes = [
        'MonitoringConfig',
        'IntegrationConfig', 
        'ChatConfig',
        'AutomationConfig',
        'AnalyticsConfig',
        'PerformanceConfig'
    ]
    
    # Adicionar model_config a cada classe que não o possui
    for class_name in config_classes:
        # Padrão para encontrar a classe
        pattern = f'(class {class_name}\(BaseSettings\):.*?)(?=\n\nclass|\n\n# |$)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match and 'model_config' not in match.group(1):
            class_content = match.group(1)
            
            # Inserir model_config no final da classe
            updated_class = class_content + model_config_text
            
            # Substituir no conteúdo
            content = content.replace(class_content, updated_class)
            print(f'model_config adicionado à classe {class_name}')
    
    # Salvar o arquivo atualizado
    with open('config.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print('Correções de configuração concluídas!')

if __name__ == '__main__':
    fix_config_classes()