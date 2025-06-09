#!/usr/bin/env python3
"""
Script completo para automação de deploy no Render
Cria Environment Groups e fornece instruções para Blueprint

Autor: Assistente AI
Data: 2024
"""

import os
import json
import requests
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime

# Configuração da API Key do Render
RENDER_API_KEY = "rnd_wwyJ7dxC06APpWiYmEgUYPIoM8GM"

@dataclass
class DeploymentConfig:
    """Configuração para deployment no Render."""
    name: str = "TechZe Diagnóstico"
    repo_url: str = "https://github.com/seu-usuario/TechZe-Diagnostico"
    branch: str = "main"
    blueprint_path: str = "render.yaml"
    environment_group_name: str = "techze-diagnostico-secrets"
    
class RenderDeploymentManager:
    """Gerenciador de deployment no Render."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_owner_id(self) -> Optional[str]:
        """Obtém o Owner ID necessário para criar recursos."""
        url = f"{self.base_url}/owners"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            owners = response.json()
            if owners and len(owners) > 0:
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
    
    def list_environment_groups(self) -> list:
        """Lista todos os Environment Groups existentes."""
        url = f"{self.base_url}/env-groups"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            env_groups = response.json()
            return env_groups
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao listar Environment Groups: {e}")
            return []
    
    def create_environment_group(self, name: str, secrets: Dict[str, str]) -> Optional[str]:
        """Cria um Environment Group no Render."""
        url = f"{self.base_url}/env-groups"
        
        # Verificar se já existe
        existing_groups = self.list_environment_groups()
        for group_data in existing_groups:
            group = group_data.get('envGroup', {})
            if group.get('name') == name:
                print(f"✅ Environment Group '{name}' já existe!")
                print(f"   ID: {group.get('id')}")
                return group.get('id')
        
        # Converter secrets para o formato esperado pela API
        env_vars = [
            {"key": key, "value": value}
            for key, value in secrets.items()
        ]
        
        # Obter Owner ID
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
    
    def get_secrets_from_env(self) -> Dict[str, str]:
        """Obtém secrets do arquivo .env local para referência."""
        secrets = {}
        env_file = ".env"
        
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        # Apenas secrets importantes
                        if key in ['SUPABASE_URL', 'SUPABASE_ANON_KEY', 'SUPABASE_SERVICE_ROLE_KEY', 
                                 'JWT_SECRET_KEY', 'REDIS_URL', 'SENTRY_DSN']:
                            secrets[key] = value
        
        return secrets
    
    def print_blueprint_instructions(self, config: DeploymentConfig, env_group_id: str) -> None:
        """Imprime instruções detalhadas para criar o Blueprint."""
        print("\n" + "="*80)
        print("🎯 INSTRUÇÕES PARA CRIAR BLUEPRINT NO RENDER")
        print("="*80)
        print()
        print("1. 📋 ACESSE O DASHBOARD DO RENDER:")
        print("   https://dashboard.render.com/blueprints")
        print()
        print("2. 🆕 CRIAR NOVO BLUEPRINT:")
        print("   • Clique em 'New Blueprint'")
        print("   • Ou acesse: https://dashboard.render.com/create?type=blueprint")
        print()
        print("3. 🔗 CONECTAR REPOSITÓRIO:")
        print(f"   • Repositório: {config.repo_url}")
        print(f"   • Branch: {config.branch}")
        print("   • Autorize o acesso ao GitHub se necessário")
        print()
        print("4. 📄 CONFIGURAR BLUEPRINT:")
        print(f"   • Arquivo Blueprint: {config.blueprint_path}")
        print("   • O Render detectará automaticamente o render.yaml")
        print()
        print("5. 🔐 CONECTAR ENVIRONMENT GROUP:")
        print(f"   • Selecione o grupo: '{config.environment_group_name}'")
        if env_group_id:
            print(f"   • ID do grupo: {env_group_id}")
        print("   • Isso conectará todos os secrets automaticamente")
        print()
        print("6. ✅ FINALIZAR CRIAÇÃO:")
        print("   • Revise todas as configurações")
        print("   • Clique em 'Create Blueprint'")
        print()
        print("7. 🚀 INICIAR DEPLOY:")
        print("   • Após criar, clique em 'Deploy'")
        print("   • Monitore os logs de build e deploy")
        print("   • Aguarde a conclusão (pode levar alguns minutos)")
        print()
        print("8. 🌐 URLS FINAIS:")
        print("   • API: https://techze-diagnostico-api.onrender.com")
        print("   • Frontend: https://techze-diagnostico-frontend.onrender.com")
        print("   • Health Check: https://techze-diagnostico-api.onrender.com/health")
        print()
        print("9. 📊 MONITORAMENTO:")
        print("   • Dashboard: https://dashboard.render.com")
        print("   • Logs em tempo real disponíveis")
        print("   • Métricas de performance")
        print("   • Alertas automáticos")
        print()
        print("="*80)
    
    def print_deployment_summary(self, config: DeploymentConfig, env_group_id: str, secrets: Dict[str, str]) -> None:
        """Imprime resumo do deployment."""
        print("\n" + "="*80)
        print("📋 RESUMO DO DEPLOYMENT")
        print("="*80)
        print()
        print(f"🏷️  Projeto: {config.name}")
        print(f"📦 Repositório: {config.repo_url}")
        print(f"🌿 Branch: {config.branch}")
        print(f"📄 Blueprint: {config.blueprint_path}")
        print()
        if env_group_id:
            print(f"✅ Environment Group: {config.environment_group_name}")
            print(f"🆔 Group ID: {env_group_id}")
            print(f"🔐 Secrets configurados: {len(secrets)}")
            print()
            print("🔑 Secrets incluídos:")
            for key in secrets.keys():
                print(f"   • {key}")
        else:
            print("❌ Environment Group não foi criado")
        print()
        print(f"⏰ Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

def main():
    """Função principal."""
    print("🚀 AUTOMAÇÃO DE DEPLOY NO RENDER")
    print("=" * 50)
    print()
    
    # Configuração
    config = DeploymentConfig()
    manager = RenderDeploymentManager(RENDER_API_KEY)
    
    # Obter secrets do .env
    print("📋 Carregando secrets do arquivo .env...")
    secrets = manager.get_secrets_from_env()
    
    if not secrets:
        print("⚠️  Nenhum secret encontrado no .env")
        print("   Usando valores de exemplo (CONFIGURE NO RENDER DASHBOARD)")
        secrets = {
            "SUPABASE_URL": "https://your-project.supabase.co",
            "SUPABASE_ANON_KEY": "your-anon-key",
            "SUPABASE_SERVICE_ROLE_KEY": "your-service-role-key",
            "JWT_SECRET_KEY": "your-jwt-secret",
            "REDIS_URL": "redis://localhost:6379",
            "SENTRY_DSN": "https://your-sentry-dsn"
        }
    
    print(f"✅ {len(secrets)} secrets carregados")
    print()
    
    # Criar Environment Group
    print(f"🔐 Criando Environment Group '{config.environment_group_name}'...")
    env_group_id = manager.create_environment_group(config.environment_group_name, secrets)
    print()
    
    # Imprimir instruções e resumo
    manager.print_blueprint_instructions(config, env_group_id)
    manager.print_deployment_summary(config, env_group_id, secrets)
    
    print("\n🎉 AUTOMAÇÃO CONCLUÍDA!")
    print("   Siga as instruções acima para finalizar o deploy.")
    print("   Em caso de dúvidas, consulte: https://render.com/docs")

if __name__ == "__main__":
    main()