#!/usr/bin/env python3
"""
Script para Criação Automática de Blueprint no Render

Este script utiliza a API do Render para criar automaticamente
um Blueprint baseado no render.yaml existente.

Pré-requisitos:
- API Key do Render (obtenha em: https://dashboard.render.com/account/api-keys)
- Repositório GitHub conectado à sua conta Render

Autor: Gemini AI Assistant
Data: 2024
"""

import os
import json
import requests
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class BlueprintConfig:
    """Configuração do Blueprint."""
    name: str
    repo_url: str
    branch: str
    blueprint_path: str
    environment_group_name: str


class RenderBlueprintCreator:
    """Criador automático de Blueprint no Render."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('RENDER_API_KEY')
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if not self.api_key:
            raise ValueError(
                "API Key do Render não encontrada. "
                "Defina a variável RENDER_API_KEY ou passe como parâmetro."
            )
    
    def create_environment_group(self, name: str, secrets: Dict[str, str]) -> Optional[str]:
        """Cria um Environment Group no Render."""
        url = f"{self.base_url}/env-groups"
        
        # Converter secrets para o formato esperado pela API
        env_vars = [
            {"key": key, "value": value}
            for key, value in secrets.items()
        ]
        
        # Primeiro, precisamos obter o ownerId (workspace/user ID)
        owner_id = self.get_owner_id()
        if not owner_id:
            print("❌ Não foi possível obter o Owner ID")
            return None
        
        payload = {
            "name": name,
            "ownerId": owner_id,
            "envVars": env_vars
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            env_group = response.json()
            print(f"✅ Environment Group '{name}' criado com sucesso!")
            print(f"   ID: {env_group.get('id')}")
            return env_group.get('id')
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao criar Environment Group: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Detalhes: {e.response.text}")
            return None
    
    def list_repositories(self) -> list:
        """Lista repositórios conectados à conta Render."""
        url = f"{self.base_url}/repos"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            repos = response.json()
            print(f"📁 Encontrados {len(repos)} repositórios conectados:")
            
            for repo in repos:
                print(f"   - {repo.get('name')} ({repo.get('url')})")
            
            return repos
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao listar repositórios: {e}")
            return []
    
    def get_owner_id(self) -> Optional[str]:
        """Obtém o Owner ID (workspace/user ID) necessário para criar recursos."""
        url = f"{self.base_url}/owners"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            owners = response.json()
            if owners and len(owners) > 0:
                # Extrair o owner do primeiro item
                owner_data = owners[0].get('owner', {})
                owner_id = owner_data.get('id')
                owner_name = owner_data.get('name')
                print(f"📋 Owner ID obtido: {owner_id} ({owner_name})")
                return owner_id
            else:
                print("❌ Nenhum owner encontrado")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao obter Owner ID: {e}")
            return None
    
    def create_blueprint_via_dashboard_instructions(self, config: BlueprintConfig) -> None:
        """Fornece instruções para criar Blueprint manualmente no Dashboard."""
        print(f"📋 INSTRUÇÕES PARA CRIAR BLUEPRINT MANUALMENTE:")
        print()
        print(f"1. Acesse: https://dashboard.render.com/blueprints")
        print(f"2. Clique em 'New Blueprint'")
        print(f"3. Conecte ao repositório: {config.repo_url}")
        print(f"4. Selecione a branch: {config.branch}")
        print(f"5. Confirme o arquivo Blueprint: {config.blueprint_path}")
        print(f"6. Selecione o Environment Group: {config.environment_group_name}")
        print(f"7. Clique em 'Create Blueprint'")
        print()
        print(f"🎯 Após criar o Blueprint:")
        print(f"   - Revise as configurações")
        print(f"   - Clique em 'Deploy' para iniciar o primeiro deploy")
        print(f"   - Monitore os logs de deploy")
    
    def get_secrets_from_env(self) -> Dict[str, str]:
        """Obtém secrets do arquivo .env local para referência."""
        secrets = {}
        env_file = ".env"
        
        if not os.path.exists(env_file):
            print(f"⚠️ Arquivo {env_file} não encontrado.")
            return secrets
        
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        secrets[key.strip()] = value.strip()
            
            print(f"📄 Carregados {len(secrets)} secrets do arquivo .env")
            return secrets
            
        except Exception as e:
            print(f"❌ Erro ao ler arquivo .env: {e}")
            return secrets
    
    def interactive_setup(self) -> None:
        """Setup interativo para criação do Blueprint."""
        print("🚀 CRIADOR AUTOMÁTICO DE BLUEPRINT NO RENDER")
        print("=" * 50)
        print()
        
        # Verificar API Key
        if not self.api_key:
            print("❌ API Key do Render não configurada!")
            print("")
            print("Para obter sua API Key:")
            print("1. Acesse: https://dashboard.render.com/account/api-keys")
            print("2. Clique em 'Create API Key'")
            print("3. Defina a variável: RENDER_API_KEY=sua_api_key")
            return
        
        print("✅ API Key configurada!")
        print()
        
        # Listar repositórios
        print("📁 Verificando repositórios conectados...")
        repos = self.list_repositories()
        print()
        
        # Configuração do Blueprint
        config = BlueprintConfig(
            name="techze-diagnostico-blueprint",
            repo_url="https://github.com/seu-usuario/TechZe-Diagnostico",  # Ajuste conforme necessário
            branch="main",
            blueprint_path="render.yaml",
            environment_group_name="techze-diagnostico-secrets"
        )
        
        print(f"📋 Configuração do Blueprint:")
        print(f"   Nome: {config.name}")
        print(f"   Repositório: {config.repo_url}")
        print(f"   Branch: {config.branch}")
        print(f"   Arquivo Blueprint: {config.blueprint_path}")
        print()
        
        # Obter secrets do .env
        print("🔐 Carregando secrets do arquivo .env...")
        secrets = self.get_secrets_from_env()
        
        if not secrets:
            print("⚠️ Nenhum secret encontrado no .env")
            print("   Você precisará configurar manualmente no Dashboard")
            env_group_id = None
        else:
            # Criar Environment Group
            print(f"🏗️ Criando Environment Group '{config.environment_group_name}'...")
            env_group_id = self.create_environment_group(
                config.environment_group_name, 
                secrets
            )
        
        print()
        
        # Fornecer instruções para criar Blueprint manualmente
        print(f"🎯 Instruções para criar Blueprint '{config.name}'...")
        self.create_blueprint_via_dashboard_instructions(config)
        
        if env_group_id:
            print()
            print("🎉 ENVIRONMENT GROUP CRIADO COM SUCESSO!")
            print()
            print("📋 PRÓXIMOS PASSOS:")
            print(f"1. Siga as instruções acima para criar o Blueprint")
            print(f"2. Conecte o Environment Group '{config.environment_group_name}' ao Blueprint")
            print("3. Revise as configurações")
            print("4. Clique em 'Deploy' para iniciar o primeiro deploy")
            print("5. Monitore os logs de deploy")
            print()
            print("🔗 URLs após o deploy:")
            print("   - API: https://techze-diagnostico-api.onrender.com")
            print("   - Frontend: https://techze-diagnostico-frontend.onrender.com")
        else:
            print()
            print("⚠️ Environment Group não foi criado")
            print("   Configure os secrets manualmente no Dashboard")
            print("   Depois siga as instruções acima para criar o Blueprint")


def main():
    """Função principal."""
    # Configuração da API Key do Render
    RENDER_API_KEY = "rnd_wwyJ7dxC06APpWiYmEgUYPIoM8GM"
    
    # Tentar usar a API key fornecida diretamente
    api_key = RENDER_API_KEY
    
    try:
        creator = RenderBlueprintCreator(api_key=api_key)
        creator.interactive_setup()
    except ValueError as e:
        print(f"❌ Erro de configuração: {e}")
        print()
        print("📖 INSTRUÇÕES PARA OBTER API KEY:")
        print("1. Acesse: https://dashboard.render.com/account/api-keys")
        print("2. Clique em 'Create API Key'")
        print("3. Copie a chave gerada")
        print("4. Execute: set RENDER_API_KEY=sua_api_key (Windows)")
        print("   Ou: export RENDER_API_KEY=sua_api_key (Linux/Mac)")
        print("5. Execute este script novamente")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    main()