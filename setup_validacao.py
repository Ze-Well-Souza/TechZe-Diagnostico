#!/usr/bin/env python3
"""
🔧 TechZe - Setup e Configuração do Sistema de Validação
Script para configurar e executar rapidamente o sistema de validação
"""

import os
import json
import asyncio
import subprocess
import sys
from colorama import init, Fore, Style

init()

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    print(f"{Fore.BLUE}🔍 Verificando dependências...{Style.RESET_ALL}")
    
    dependencias = ['aiohttp', 'colorama', 'requests']
    faltando = []
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"{Fore.GREEN}✅ {dep}{Style.RESET_ALL}")
        except ImportError:
            faltando.append(dep)
            print(f"{Fore.RED}❌ {dep}{Style.RESET_ALL}")
    
    if faltando:
        print(f"\n{Fore.YELLOW}📦 Instalando dependências faltantes...{Style.RESET_ALL}")
        for dep in faltando:
            subprocess.run([sys.executable, "-m", "pip", "install", dep])
    
    return len(faltando) == 0

def criar_config_env():
    """Cria arquivo de configuração de ambiente"""
    config_content = """# TechZe Validação - Configurações
# Atualize com suas chaves de API

# Render API (já configurado)
RENDER_API_KEY=rnd_Tj1JybEJij6A3UhouM7spm8LRbkX

# Google PageSpeed Insights API (obtenha em: https://developers.google.com/speed/docs/insights/v5/get-started)
GOOGLE_API_KEY=SUA_GOOGLE_API_KEY_AQUI

# URLs do sistema (já configuradas para seu projeto)
BASE_URL=https://techreparo.com
API_BACKEND=https://techze-diagnostico-api.onrender.com
API_FRONTEND=https://techze-diagnostico-frontend.onrender.com

# Configurações de teste
TIMEOUT=30
MAX_RETRIES=3
"""
    
    with open('.env.validacao', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"{Fore.GREEN}✅ Arquivo .env.validacao criado{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}⚠️ IMPORTANTE: Atualize sua GOOGLE_API_KEY no arquivo .env.validacao{Style.RESET_ALL}")

def criar_script_rapido():
    """Cria script de execução rápida"""
    script_content = """#!/usr/bin/env python3
import asyncio
import os
from sistema_validacao_melhorado import TechZeValidadorMelhorado, ValidacaoConfig

async def executar_validacao_rapida():
    # Carregar configuração do .env
    config = ValidacaoConfig(
        render_api_key=os.getenv('RENDER_API_KEY', 'rnd_Tj1JybEJij6A3UhouM7spm8LRbkX'),
        google_api_key=os.getenv('GOOGLE_API_KEY', 'SUA_GOOGLE_API_KEY_AQUI'),
        base_url=os.getenv('BASE_URL', 'https://techreparo.com'),
        api_backend=os.getenv('API_BACKEND', 'https://techze-diagnostico-api.onrender.com'),
        api_frontend=os.getenv('API_FRONTEND', 'https://techze-diagnostico-frontend.onrender.com')
    )
    
    validador = TechZeValidadorMelhorado(config)
    return await validador.executar_validacao_completa()

if __name__ == "__main__":
    asyncio.run(executar_validacao_rapida())
"""
    
    with open('validacao_rapida.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"{Fore.GREEN}✅ Script validacao_rapida.py criado{Style.RESET_ALL}")

def criar_documentacao():
    """Cria documentação de uso"""
    doc_content = """# 🎯 TechZe - Sistema de Validação Automatizada

## 📋 Como Usar

### 1. Configuração Inicial
```bash
python setup_validacao.py
```

### 2. Configurar Google API Key
1. Acesse: https://developers.google.com/speed/docs/insights/v5/get-started
2. Crie um projeto e ative a PageSpeed Insights API
3. Gere uma API Key
4. Atualize o arquivo `.env.validacao` com sua chave

### 3. Executar Validação
```bash
# Validação completa
python sistema_validacao_melhorado.py

# Validação rápida
python validacao_rapida.py
```

## 📊 O que é testado

### 🔧 Render Services
- Status de todos os serviços
- Health checks
- Deployments recentes

### ⚡ Performance (Google PageSpeed)
- Core Web Vitals (LCP, FCP, CLS, TBT)
- Scores de Performance, SEO, Acessibilidade
- Testes Desktop e Mobile

### 🔍 APIs Funcionais
- `/health` endpoints
- APIs v3 do diagnóstico
- Modelos de IA
- Tempo de resposta

### 🔒 Segurança Básica
- HTTPS ativo
- Security headers
- HSTS, Content Security Policy
- X-Frame-Options

## 📈 Relatórios

O sistema gera:
- Relatório colorido no terminal
- Arquivo JSON detalhado (`relatorio_validacao_techze.json`)
- Score geral de 0-100%
- Recomendações de melhorias

## 🚀 Integração Contínua

Para executar automaticamente:
```bash
# A cada hora
0 * * * * cd /caminho/do/projeto && python validacao_rapida.py

# Diariamente às 9h
0 9 * * * cd /caminho/do/projeto && python sistema_validacao_melhorado.py
```

## 🔑 APIs Utilizadas

- **Render API**: Monitoramento de serviços
- **Google PageSpeed Insights**: Performance e Core Web Vitals
- **Direct HTTP Checks**: Testes funcionais das APIs

## 📞 Suporte

Em caso de problemas:
1. Verifique se as API keys estão corretas
2. Confirme se os serviços estão online
3. Consulte os logs detalhados no arquivo JSON
"""
    
    with open('README_VALIDACAO.md', 'w', encoding='utf-8') as f:
        f.write(doc_content)
    
    print(f"{Fore.GREEN}✅ Documentação README_VALIDACAO.md criada{Style.RESET_ALL}")

def main():
    """Função principal de setup"""
    print(f"{Fore.MAGENTA}🔧 TechZe - Setup do Sistema de Validação{Style.RESET_ALL}\n")
    
    # 1. Verificar dependências
    if not verificar_dependencias():
        print(f"{Fore.RED}❌ Erro ao instalar dependências{Style.RESET_ALL}")
        return False
    
    # 2. Criar arquivos de configuração
    print(f"\n{Fore.BLUE}📁 Criando arquivos de configuração...{Style.RESET_ALL}")
    criar_config_env()
    criar_script_rapido()
    criar_documentacao()
    
    print(f"\n{Fore.GREEN}🎉 Setup completo!{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}📋 Próximos passos:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}1. Configure sua Google API Key no arquivo .env.validacao{Style.RESET_ALL}")
    print(f"{Fore.WHITE}2. Execute: python sistema_validacao_melhorado.py{Style.RESET_ALL}")
    print(f"{Fore.WHITE}3. Consulte README_VALIDACAO.md para mais detalhes{Style.RESET_ALL}")
    
    return True

if __name__ == "__main__":
    main() 