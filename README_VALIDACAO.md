# 🎯 TechZe - Sistema de Validação Automatizada

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
