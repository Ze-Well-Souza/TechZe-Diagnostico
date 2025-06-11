# 📁 Estrutura do Projeto TechZe-Diagnostico

## 🎯 Visão Geral

Este documento descreve a nova estrutura organizacional do projeto TechZe-Diagnostico, implementada para melhorar a manutenibilidade, clareza e seguir as melhores práticas de desenvolvimento.

## 📂 Estrutura de Diretórios

```
TechZe-Diagnostico/
├── src/                    # 🎨 Código Frontend (React + TypeScript)
├── microservices/          # 🔧 Backend Services (FastAPI + Python)
├── scripts/               # 🤖 Scripts de Automação
│   ├── deploy/            # 🚀 Scripts de Deploy
│   ├── setup/             # ⚙️ Scripts de Configuração
│   ├── maintenance/       # 🔧 Scripts de Manutenção
│   ├── validation/        # ✅ Scripts de Validação
│   └── monitoring/        # 📊 Scripts de Monitoramento
├── config/                # ⚙️ Configurações
│   ├── environments/      # 🌍 Variáveis de Ambiente
│   ├── docker/           # 🐳 Configurações Docker
│   ├── k8s/              # ☸️ Configurações Kubernetes
│   └── database/         # 🗄️ Scripts de Banco de Dados
├── docs/                  # 📚 Documentação
│   ├── api/              # 📋 Documentação da API
│   ├── deployment/       # 🚀 Guias de Deploy
│   ├── developer/        # 👨‍💻 Documentação Técnica
│   ├── planning/         # 📋 Documentos de Planejamento
│   └── user-manual/      # 📖 Manual do Usuário
├── tests/                 # 🧪 Testes
│   ├── e2e/              # 🔄 Testes End-to-End
│   └── integration/      # 🔗 Testes de Integração
├── reports/              # 📊 Relatórios
│   ├── validation/       # ✅ Relatórios de Validação
│   ├── deployment/       # 🚀 Relatórios de Deploy
│   └── system/           # 🖥️ Relatórios de Sistema
└── deploy/               # 🚀 Arquivos de Deploy
    ├── render/           # 🌐 Deploy Render
    ├── docker/           # 🐳 Deploy Docker
    └── k8s/              # ☸️ Deploy Kubernetes
```

## 📋 Detalhamento dos Diretórios

### 🎨 Frontend (`src/`)
- **Propósito**: Código fonte do frontend React
- **Tecnologias**: React, TypeScript, Tailwind CSS, Vite
- **Estrutura**: Componentes, páginas, hooks, contextos, serviços

### 🔧 Backend (`microservices/`)
- **Propósito**: Serviços backend em FastAPI
- **Tecnologias**: FastAPI, Python, SQLAlchemy, Supabase
- **Estrutura**: APIs, modelos, serviços, utilitários

### 🤖 Scripts (`scripts/`)
- **`deploy/`**: Scripts para deploy em produção
- **`setup/`**: Scripts de configuração inicial
- **`maintenance/`**: Scripts de limpeza e manutenção
- **`validation/`**: Scripts de teste e validação
- **`monitoring/`**: Scripts de debug e monitoramento

### ⚙️ Configurações (`config/`)
- **`environments/`**: Arquivos .env e configurações de ambiente
- **`docker/`**: Dockerfiles e docker-compose
- **`k8s/`**: Manifestos Kubernetes
- **`database/`**: Scripts SQL e configurações de banco

### 📚 Documentação (`docs/`)
- **`api/`**: Documentação técnica das APIs
- **`deployment/`**: Guias e instruções de deploy
- **`developer/`**: Documentação para desenvolvedores
- **`planning/`**: PRDs, planos e documentos estratégicos
- **`user-manual/`**: Manual do usuário final

### 🧪 Testes (`tests/`)
- **`e2e/`**: Testes end-to-end com Cypress
- **`integration/`**: Testes de integração

### 📊 Relatórios (`reports/`)
- **`validation/`**: Relatórios de testes e validações
- **`deployment/`**: Relatórios de deploy
- **`system/`**: Relatórios de status e diagnóstico

### 🚀 Deploy (`deploy/`)
- **`render/`**: Configurações específicas do Render
- **`docker/`**: Configurações de deploy Docker
- **`k8s/`**: Configurações de deploy Kubernetes

## 🎯 Benefícios da Nova Estrutura

### ✅ **Organização Clara**
- Cada tipo de arquivo tem seu lugar específico
- Fácil localização de recursos
- Estrutura intuitiva para novos desenvolvedores

### 🔧 **Manutenibilidade**
- Separação clara de responsabilidades
- Redução de conflitos entre arquivos
- Facilita atualizações e modificações

### 🚀 **Deploy Consistente**
- Configurações organizadas por ambiente
- Scripts de deploy centralizados
- Processo de deploy mais confiável

### 📚 **Documentação Acessível**
- Documentação categorizada por tipo
- Fácil acesso a informações específicas
- Melhor experiência para desenvolvedores

### 🧪 **Testes Organizados**
- Testes separados por tipo
- Relatórios centralizados
- Melhor rastreabilidade de qualidade

## 🔄 Migração Realizada

### 📊 **Estatísticas da Reorganização**
- **Arquivos movidos**: ~70 arquivos da raiz
- **Diretórios criados**: 19 novos diretórios
- **READMEs criados**: 19 arquivos explicativos
- **Tempo de execução**: < 5 segundos

### ✅ **Arquivos Mantidos na Raiz**
Apenas arquivos essenciais permaneceram na raiz:
- `README.md` - Documentação principal
- `package.json` - Configuração do projeto
- `tsconfig.json` - Configuração TypeScript
- `vite.config.ts` - Configuração Vite
- `tailwind.config.js` - Configuração Tailwind
- Arquivos de configuração do Git (`.gitignore`, `.github/`)

## 🚀 Próximos Passos

1. **Atualizar Scripts de Build**: Verificar se todos os caminhos estão corretos
2. **Atualizar Documentação**: Revisar links e referências
3. **Validar Deploy**: Testar processo de deploy com nova estrutura
4. **Treinar Equipe**: Apresentar nova estrutura para desenvolvedores

## 📞 Suporte

Para dúvidas sobre a nova estrutura:
- Consulte os READMEs específicos em cada diretório
- Verifique a documentação em `docs/developer/`
- Consulte o `TASK_MASTER.md` em `docs/planning/`

---

**📅 Última atualização**: $(date)
**👨‍💻 Implementado por**: Sistema de Reorganização Automática
**🎯 Objetivo**: Melhorar manutenibilidade e seguir boas práticas