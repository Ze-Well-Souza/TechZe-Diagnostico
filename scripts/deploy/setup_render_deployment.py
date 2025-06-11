#!/usr/bin/env python3
"""
Script de Automação para Deploy no Render

Este script automatiza a configuração de secrets e fornece instruções
para criar um Blueprint no Render para o projeto TechZe Diagnostico.

Autor: Gemini AI Assistant
Data: 2024
"""

import os
import json
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RenderSecret:
    """Representa um secret do Render."""
    key: str
    description: str
    required: bool = True
    example: str = ""


class RenderDeploymentAutomator:
    """Automatiza a configuração de deployment no Render."""
    
    def __init__(self):
        self.secrets = self._define_required_secrets()
        self.render_api_key = os.getenv('RENDER_API_KEY')
        self.github_repo = "https://github.com/seu-usuario/TechZe-Diagnostico"
        
    def _define_required_secrets(self) -> List[RenderSecret]:
        """Define todos os secrets necessários para o projeto."""
        return [
            RenderSecret(
                key="SUPABASE_URL",
                description="URL do projeto Supabase",
                example="https://seu-projeto.supabase.co"
            ),
            RenderSecret(
                key="SUPABASE_ANON_KEY",
                description="Chave anônima do Supabase (pública)",
                example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            ),
            RenderSecret(
                key="SUPABASE_SERVICE_ROLE_KEY",
                description="Chave de service role do Supabase (privada)",
                example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            ),
            RenderSecret(
                key="JWT_SECRET_KEY",
                description="Chave secreta para assinatura de tokens JWT",
                example="sua-chave-secreta-super-segura-aqui"
            ),
            RenderSecret(
                key="REDIS_URL",
                description="URL de conexão com Redis (opcional para cache)",
                required=False,
                example="redis://localhost:6379"
            ),
            RenderSecret(
                key="SENTRY_DSN",
                description="DSN do Sentry para monitoramento de erros",
                required=False,
                example="https://chave@sentry.io/projeto"
            )
        ]
    
    def generate_secrets_checklist(self) -> str:
        """Gera uma checklist dos secrets necessários."""
        checklist = []
        checklist.append("# 🔐 CHECKLIST DE SECRETS PARA RENDER")
        checklist.append("")
        checklist.append("## Secrets Obrigatórios")
        checklist.append("")
        
        for secret in self.secrets:
            if secret.required:
                status = "[ ]"  # Checkbox vazio
                checklist.append(f"{status} **{secret.key}**")
                checklist.append(f"   - Descrição: {secret.description}")
                if secret.example:
                    checklist.append(f"   - Exemplo: `{secret.example}`")
                checklist.append("")
        
        checklist.append("## Secrets Opcionais")
        checklist.append("")
        
        for secret in self.secrets:
            if not secret.required:
                status = "[ ]"  # Checkbox vazio
                checklist.append(f"{status} **{secret.key}**")
                checklist.append(f"   - Descrição: {secret.description}")
                if secret.example:
                    checklist.append(f"   - Exemplo: `{secret.example}`")
                checklist.append("")
        
        return "\n".join(checklist)
    
    def generate_render_instructions(self) -> str:
        """Gera instruções detalhadas para configuração no Render."""
        instructions = []
        instructions.append("# 🚀 GUIA COMPLETO DE DEPLOY NO RENDER")
        instructions.append("")
        instructions.append("## Fase 1: Configuração de Secrets (30 minutos)")
        instructions.append("")
        instructions.append("### Passo 1: Acesse o Dashboard do Render")
        instructions.append("1. Acesse https://dashboard.render.com")
        instructions.append("2. Faça login na sua conta")
        instructions.append("3. No menu lateral, clique em **Environment Groups**")
        instructions.append("4. Clique em **New Environment Group**")
        instructions.append("5. Nomeie como: `techze-diagnostico-secrets`")
        instructions.append("")
        instructions.append("### Passo 2: Adicione os Secrets")
        instructions.append("")
        
        for i, secret in enumerate(self.secrets, 1):
            required_text = "(OBRIGATÓRIO)" if secret.required else "(OPCIONAL)"
            instructions.append(f"**{i}. {secret.key}** {required_text}")
            instructions.append(f"- Clique em **Add Environment Variable**")
            instructions.append(f"- Key: `{secret.key}`")
            instructions.append(f"- Value: [Insira o valor real aqui]")
            instructions.append(f"- Descrição: {secret.description}")
            if secret.example:
                instructions.append(f"- Formato esperado: `{secret.example}`")
            instructions.append("")
        
        instructions.append("## Fase 2: Criação do Blueprint (15 minutos)")
        instructions.append("")
        instructions.append("### Passo 1: Criar Blueprint")
        instructions.append("1. No dashboard do Render, clique em **Blueprints**")
        instructions.append("2. Clique em **New Blueprint**")
        instructions.append("3. Conecte ao seu repositório GitHub")
        instructions.append("4. Selecione o repositório: `TechZe-Diagnostico`")
        instructions.append("5. Branch: `main`")
        instructions.append("6. Blueprint file: `render.yaml` (já configurado)")
        instructions.append("")
        instructions.append("### Passo 2: Configurar Environment Group")
        instructions.append("1. Na seção **Environment Groups**, selecione: `techze-diagnostico-secrets`")
        instructions.append("2. Clique em **Create Blueprint**")
        instructions.append("")
        instructions.append("### Passo 3: Deploy Automático")
        instructions.append("1. O Render irá automaticamente:")
        instructions.append("   - Criar o serviço de API (techze-diagnostico-api)")
        instructions.append("   - Criar o serviço de Frontend (techze-diagnostico-frontend)")
        instructions.append("   - Configurar as variáveis de ambiente")
        instructions.append("   - Iniciar o primeiro deploy")
        instructions.append("")
        instructions.append("## Fase 3: Verificação (10 minutos)")
        instructions.append("")
        instructions.append("### URLs de Acesso")
        instructions.append("- **API**: https://techze-diagnostico-api.onrender.com")
        instructions.append("- **Frontend**: https://techze-diagnostico-frontend.onrender.com")
        instructions.append("- **Health Check**: https://techze-diagnostico-api.onrender.com/health")
        instructions.append("")
        instructions.append("### Verificações")
        instructions.append("- [ ] API responde no endpoint /health")
        instructions.append("- [ ] Frontend carrega corretamente")
        instructions.append("- [ ] Logs não mostram erros críticos")
        instructions.append("- [ ] Conexão com Supabase funcionando")
        instructions.append("")
        
        return "\n".join(instructions)
    
    def create_env_template(self) -> str:
        """Cria um template de arquivo .env para referência."""
        template = []
        template.append("# Template de Variáveis de Ambiente para Render")
        template.append(f"# Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        template.append("")
        template.append("# IMPORTANTE: Não commite este arquivo com valores reais!")
        template.append("# Use este template apenas como referência.")
        template.append("")
        
        for secret in self.secrets:
            required_comment = "# OBRIGATÓRIO" if secret.required else "# OPCIONAL"
            template.append(f"# {secret.description} {required_comment}")
            template.append(f"{secret.key}={secret.example}")
            template.append("")
        
        return "\n".join(template)
    
    def validate_current_env(self) -> Dict[str, bool]:
        """Valida se as variáveis de ambiente atuais estão configuradas."""
        validation = {}
        
        for secret in self.secrets:
            value = os.getenv(secret.key)
            validation[secret.key] = {
                'configured': value is not None and value.strip() != '',
                'required': secret.required,
                'value_preview': value[:20] + '...' if value and len(value) > 20 else value
            }
        
        return validation
    
    def generate_validation_report(self) -> str:
        """Gera um relatório de validação das variáveis atuais."""
        validation = self.validate_current_env()
        report = []
        
        report.append("# 📊 RELATÓRIO DE VALIDAÇÃO DE VARIÁVEIS")
        report.append("")
        report.append("## Status Atual das Variáveis de Ambiente")
        report.append("")
        
        for key, status in validation.items():
            icon = "✅" if status['configured'] else "❌"
            required_text = "(OBRIGATÓRIO)" if status['required'] else "(OPCIONAL)"
            
            report.append(f"{icon} **{key}** {required_text}")
            
            if status['configured']:
                report.append(f"   - Status: Configurado")
                if status['value_preview']:
                    report.append(f"   - Preview: `{status['value_preview']}`")
            else:
                report.append(f"   - Status: NÃO CONFIGURADO")
                if status['required']:
                    report.append(f"   - ⚠️ AÇÃO NECESSÁRIA: Esta variável é obrigatória")
            
            report.append("")
        
        # Resumo
        total_vars = len(validation)
        configured_vars = sum(1 for v in validation.values() if v['configured'])
        required_vars = sum(1 for v in validation.values() if v['required'])
        configured_required = sum(1 for v in validation.values() if v['required'] and v['configured'])
        
        report.append("## 📈 Resumo")
        report.append("")
        report.append(f"- Total de variáveis: {total_vars}")
        report.append(f"- Configuradas: {configured_vars}/{total_vars}")
        report.append(f"- Obrigatórias configuradas: {configured_required}/{required_vars}")
        
        if configured_required == required_vars:
            report.append("- ✅ **Todas as variáveis obrigatórias estão configuradas!**")
        else:
            missing = required_vars - configured_required
            report.append(f"- ❌ **{missing} variáveis obrigatórias precisam ser configuradas**")
        
        return "\n".join(report)
    
    def run_automation(self) -> None:
        """Executa o processo completo de automação."""
        print("🚀 Iniciando automação de deploy no Render...")
        print()
        
        # Criar diretório de output
        output_dir = "render_deployment_guide"
        os.makedirs(output_dir, exist_ok=True)
        
        # Gerar arquivos
        files_to_create = {
            "secrets_checklist.md": self.generate_secrets_checklist(),
            "deployment_instructions.md": self.generate_render_instructions(),
            "env_template.txt": self.create_env_template(),
            "validation_report.md": self.generate_validation_report()
        }
        
        for filename, content in files_to_create.items():
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Criado: {filepath}")
        
        print()
        print("📁 Arquivos gerados na pasta: render_deployment_guide/")
        print()
        print("📋 PRÓXIMOS PASSOS:")
        print("1. Abra o arquivo 'deployment_instructions.md' para instruções completas")
        print("2. Use 'secrets_checklist.md' para verificar todos os secrets necessários")
        print("3. Consulte 'validation_report.md' para status atual das variáveis")
        print("4. Use 'env_template.txt' como referência para configuração")
        print()
        print("🎯 AÇÃO IMEDIATA: Configure os secrets no Render Dashboard primeiro!")


def main():
    """Função principal."""
    automator = RenderDeploymentAutomator()
    automator.run_automation()


if __name__ == "__main__":
    main()