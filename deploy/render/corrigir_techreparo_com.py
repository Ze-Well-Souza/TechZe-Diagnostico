#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚨 SCRIPT DE CORREÇÃO AUTOMÁTICA: techreparo.com
Corrige o problema de deployment do frontend React no TechZe-Diagnostico
"""

import os
import sys
import requests
import subprocess
import json
from datetime import datetime
import time

# Configurações
RENDER_API_KEY = "rnd_Tj1JybEJij6A3UhouM7spm8LRbkX"
RENDER_API_BASE = "https://api.render.com/v1"
REPO_URL = "https://github.com/Ze-Well-Souza/TechZe-Diagnostico"

class TechReparoCorretor:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {RENDER_API_KEY}",
            "Content-Type": "application/json"
        }
        self.backend_service_id = "srv-d0t22t63jp1c73dui0kg"
        
    def print_status(self, message, tipo="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        print(f"{icons.get(tipo, 'ℹ️')} [{timestamp}] {message}")
    
    def verificar_servicos_atuais(self):
        """Verifica serviços atualmente configurados no Render"""
        self.print_status("Verificando serviços atuais no Render...")
        
        try:
            response = requests.get(f"{RENDER_API_BASE}/services", headers=self.headers)
            if response.status_code == 200:
                services = response.json()
                self.print_status(f"Encontrados {len(services)} serviços:", "SUCCESS")
                
                for service in services:
                    service_data = service.get('service', {})
                    name = service_data.get('name', 'Unknown')
                    service_type = service_data.get('type', 'Unknown')
                    url = service_data.get('serviceDetails', {}).get('url', 'N/A')
                    
                    print(f"  📦 {name} ({service_type})")
                    print(f"     URL: {url}")
                
                return services
            else:
                self.print_status(f"Erro ao verificar serviços: {response.status_code}", "ERROR")
                return []
                
        except Exception as e:
            self.print_status(f"Erro na verificação: {str(e)}", "ERROR")
            return []
    
    def verificar_dominios_customizados(self):
        """Verifica domínios customizados do backend"""
        self.print_status("Verificando domínios customizados...")
        
        try:
            url = f"{RENDER_API_BASE}/services/{self.backend_service_id}/custom-domains"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                domains = response.json()
                self.print_status(f"Encontrados {len(domains)} domínios:", "SUCCESS")
                
                for domain in domains:
                    domain_data = domain.get('customDomain', {})
                    name = domain_data.get('name')
                    status = domain_data.get('verificationStatus')
                    print(f"  🌐 {name} - Status: {status}")
                
                return domains
            else:
                self.print_status(f"Erro ao verificar domínios: {response.status_code}", "ERROR")
                return []
                
        except Exception as e:
            self.print_status(f"Erro na verificação de domínios: {str(e)}", "ERROR")
            return []
    
    def criar_servico_frontend(self):
        """Cria serviço frontend no Render"""
        self.print_status("Criando serviço frontend...")
        
        service_config = {
            "type": "static_site",
            "name": "techze-diagnostico-frontend",
            "repo": REPO_URL,
            "branch": "main",
            "buildCommand": "npm install && npm run build",
            "publishPath": "./dist",
            "pullRequestPreviewsEnabled": "yes",
            "envVars": [
                {
                    "key": "NODE_VERSION",
                    "value": "22.14.0"
                },
                {
                    "key": "VITE_API_URL", 
                    "value": "https://techze-diagnostic-api.onrender.com"
                }
            ]
        }
        
        try:
            response = requests.post(
                f"{RENDER_API_BASE}/services",
                headers=self.headers,
                json=service_config
            )
            
            if response.status_code == 201:
                service = response.json()
                service_id = service.get('service', {}).get('id')
                self.print_status(f"Frontend criado com sucesso! ID: {service_id}", "SUCCESS")
                return service_id
            else:
                self.print_status(f"Erro ao criar frontend: {response.status_code}", "ERROR")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            self.print_status(f"Erro na criação do frontend: {str(e)}", "ERROR")
            return None
    
    def mover_dominio_customizado(self, frontend_service_id):
        """Move domínio customizado do backend para o frontend"""
        self.print_status("Movendo domínio customizado para o frontend...")
        
        # 1. Remover domínio do backend
        dominios = self.verificar_dominios_customizados()
        
        for domain in dominios:
            domain_data = domain.get('customDomain', {})
            domain_id = domain_data.get('id')
            domain_name = domain_data.get('name')
            
            if domain_name in ['techreparo.com', 'www.techreparo.com']:
                self.print_status(f"Removendo {domain_name} do backend...")
                
                try:
                    url = f"{RENDER_API_BASE}/services/{self.backend_service_id}/custom-domains/{domain_id}"
                    response = requests.delete(url, headers=self.headers)
                    
                    if response.status_code == 204:
                        self.print_status(f"Domínio {domain_name} removido do backend", "SUCCESS")
                    else:
                        self.print_status(f"Erro ao remover {domain_name}: {response.status_code}", "ERROR")
                        
                except Exception as e:
                    self.print_status(f"Erro ao remover domínio: {str(e)}", "ERROR")
        
        # 2. Aguardar um pouco
        time.sleep(5)
        
        # 3. Adicionar domínio ao frontend
        if frontend_service_id:
            self.print_status("Adicionando domínio ao frontend...")
            
            for domain_name in ['techreparo.com', 'www.techreparo.com']:
                domain_config = {"name": domain_name}
                
                try:
                    url = f"{RENDER_API_BASE}/services/{frontend_service_id}/custom-domains"
                    response = requests.post(url, headers=self.headers, json=domain_config)
                    
                    if response.status_code == 201:
                        self.print_status(f"Domínio {domain_name} adicionado ao frontend", "SUCCESS")
                    else:
                        self.print_status(f"Erro ao adicionar {domain_name}: {response.status_code}", "ERROR")
                        
                except Exception as e:
                    self.print_status(f"Erro ao adicionar domínio: {str(e)}", "ERROR")
    
    def executar_correcao_completa(self):
        """Executa correção completa do problema"""
        self.print_status("🚀 INICIANDO CORREÇÃO COMPLETA DO TECHREPARO.COM", "INFO")
        print("=" * 60)
        
        # 1. Diagnóstico inicial
        self.print_status("1️⃣ Verificando estado atual...")
        services = self.verificar_servicos_atuais()
        dominios = self.verificar_dominios_customizados()
        
        # 2. Verificar se frontend já existe
        frontend_exists = False
        frontend_service_id = None
        
        for service in services:
            service_data = service.get('service', {})
            if 'frontend' in service_data.get('name', '').lower():
                frontend_exists = True
                frontend_service_id = service_data.get('id')
                break
        
        if frontend_exists:
            self.print_status("Frontend já existe, configurando domínios...", "INFO")
        else:
            # 3. Criar serviço frontend
            self.print_status("2️⃣ Criando serviço frontend...")
            frontend_service_id = self.criar_servico_frontend()
            
            if not frontend_service_id:
                self.print_status("Falha na criação do frontend", "ERROR")
                return False
        
        # 4. Aguardar deployment
        if not frontend_exists:
            self.print_status("3️⃣ Aguardando deployment do frontend...")
            time.sleep(30)  # Aguardar deployment inicial
        
        # 5. Mover domínio customizado
        self.print_status("4️⃣ Configurando domínios customizados...")
        self.mover_dominio_customizado(frontend_service_id)
        
        # 6. Verificação final
        self.print_status("5️⃣ Verificação final...")
        time.sleep(10)
        
        try:
            response = requests.get("https://techreparo.com", timeout=10)
            if response.status_code == 200 and 'text/html' in response.headers.get('content-type', ''):
                self.print_status("✅ CORREÇÃO CONCLUÍDA COM SUCESSO!", "SUCCESS")
                self.print_status("🌐 techreparo.com agora serve a aplicação React", "SUCCESS")
                return True
            else:
                self.print_status("⚠️ Domínio ainda não está servindo HTML", "WARNING")
                self.print_status("Aguarde alguns minutos para propagação", "INFO")
                return True
        except Exception as e:
            self.print_status(f"Erro na verificação final: {str(e)}", "ERROR")
            return False

def main():
    print("🔧 TechZe - Corretor Automático do techreparo.com")
    print("=" * 50)
    
    corretor = TechReparoCorretor()
    
    try:
        sucesso = corretor.executar_correcao_completa()
        
        if sucesso:
            print("\n" + "=" * 50)
            print("✅ CORREÇÃO FINALIZADA")
            print("🌐 Teste: https://techreparo.com")
            print("📚 API Docs: https://techze-diagnostic-api.onrender.com/docs")
            print("⏱️  Aguarde 2-5 minutos para propagação completa")
        else:
            print("\n" + "=" * 50)
            print("❌ Correção teve problemas")
            print("📋 Verifique o diagnóstico: DIAGNOSTICO_TECHREPARO_COM.md")
            
    except KeyboardInterrupt:
        print("\n⚠️ Operação cancelada pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {str(e)}")

if __name__ == "__main__":
    main() 