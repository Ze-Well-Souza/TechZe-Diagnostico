# 🚀 Guia Completo de Deploy Automatizado no Render

## 📋 Visão Geral

Este guia fornece uma solução **100% automatizada** para deploy da aplicação TechZe Diagnostico no Render, incluindo:

- ✅ Configuração automática de secrets
- ✅ Criação de Blueprint via API
- ✅ Validação de variáveis de ambiente
- ✅ Instruções passo-a-passo detalhadas
- ✅ Templates e checklists

## 🎯 Resultado Final

Após seguir este guia, você terá:

- **API Backend**: `https://techze-diagnostico-api.onrender.com`
- **Frontend React**: `https://techze-diagnostico-frontend.onrender.com`
- **Health Check**: `https://techze-diagnostico-api.onrender.com/health`
- **Deploy automático** a cada push na branch `main`

## 📁 Arquivos Criados

### Scripts de Automação
- `setup_render_deployment.py` - Script principal de automação
- `render_blueprint_creator.py` - Criação automática via API

### Guias Gerados (pasta `render_deployment_guide/`)
- `deployment_instructions.md` - Instruções completas passo-a-passo
- `secrets_checklist.md` - Checklist de todos os secrets necessários
- `validation_report.md` - Status atual das variáveis de ambiente
- `env_template.txt` - Template de referência para variáveis

## 🚀 Opção 1: Automação Completa (Recomendado)

### Pré-requisitos
1. Conta no Render (gratuita)
2. Repositório GitHub conectado ao Render
3. API Key do Render (opcional, para automação total)

### Passo 1: Obter API Key do Render (Opcional)
```bash
# 1. Acesse: https://dashboard.render.com/account/api-keys
# 2. Clique em "Create API Key"
# 3. Configure a variável de ambiente:
set RENDER_API_KEY=sua_api_key_aqui
```

### Passo 2: Executar Automação Completa
```bash
# Gerar guias e validações
python setup_render_deployment.py

# Criar Blueprint automaticamente (se tiver API Key)
python render_blueprint_creator.py
```

### Passo 3: Verificar Resultado
- Acesse o Dashboard do Render
- Verifique se o Blueprint foi criado
- Inicie o primeiro deploy

## 📖 Opção 2: Processo Manual Guiado

### Passo 1: Gerar Guias
```bash
python setup_render_deployment.py
```

### Passo 2: Seguir Instruções
1. Abra `render_deployment_guide/deployment_instructions.md`
2. Siga as instruções passo-a-passo
3. Use `secrets_checklist.md` para verificar todos os secrets

## 🔐 Secrets Necessários

### Obrigatórios
- `SUPABASE_URL` - URL do projeto Supabase
- `SUPABASE_ANON_KEY` - Chave pública do Supabase
- `SUPABASE_SERVICE_ROLE_KEY` - Chave privada do Supabase
- `JWT_SECRET_KEY` - Chave para assinatura de tokens JWT

### Opcionais
- `REDIS_URL` - Para cache (melhora performance)
- `SENTRY_DSN` - Para monitoramento de erros

## 📊 Validação de Ambiente

### Verificar Status Atual
```bash
python setup_render_deployment.py
# Consulte o arquivo: render_deployment_guide/validation_report.md
```

### Exemplo de Saída
```
✅ SUPABASE_URL (OBRIGATÓRIO) - Configurado
✅ SUPABASE_ANON_KEY (OBRIGATÓRIO) - Configurado
✅ SUPABASE_SERVICE_ROLE_KEY (OBRIGATÓRIO) - Configurado
✅ JWT_SECRET_KEY (OBRIGATÓRIO) - Configurado
❌ REDIS_URL (OPCIONAL) - NÃO CONFIGURADO
❌ SENTRY_DSN (OPCIONAL) - NÃO CONFIGURADO
```

## 🏗️ Arquitetura do Deploy

### Serviços Criados
1. **API Backend** (Python/FastAPI)
   - Runtime: Python 3.11
   - Framework: FastAPI + Uvicorn
   - Banco: Supabase (PostgreSQL)
   - Cache: Redis (opcional)
   - Monitoramento: Sentry (opcional)

2. **Frontend** (React/Vite)
   - Runtime: Node.js 18
   - Framework: React + Vite
   - Build: Otimizado para produção
   - CDN: Render CDN automático

### Configuração Automática
- **Health Checks**: Configurados automaticamente
- **HTTPS**: Certificado SSL gratuito
- **Custom Domain**: Suporte incluído
- **Auto Deploy**: A cada push na branch main
- **Environment Variables**: Carregadas dos secrets

## 🔧 Troubleshooting

### Problema: API Key não funciona
```bash
# Verificar se a API Key está configurada
echo $RENDER_API_KEY  # Linux/Mac
echo %RENDER_API_KEY%  # Windows

# Recriar API Key se necessário
# 1. Acesse: https://dashboard.render.com/account/api-keys
# 2. Delete a chave antiga
# 3. Crie uma nova
```

### Problema: Secrets não carregam
1. Verifique se o arquivo `.env` existe
2. Confirme que as variáveis estão no formato correto: `CHAVE=valor`
3. Execute o script de validação: `python setup_render_deployment.py`

### Problema: Deploy falha
1. Verifique os logs no Dashboard do Render
2. Confirme que todos os secrets obrigatórios estão configurados
3. Verifique se o `render.yaml` está na raiz do repositório

### Problema: Repositório não encontrado
1. Conecte o repositório GitHub ao Render:
   - Dashboard → Account Settings → GitHub
2. Verifique se o repositório está público ou se o Render tem acesso

## 📈 Monitoramento

### URLs de Verificação
- **API Health**: `https://techze-diagnostico-api.onrender.com/health`
- **API Docs**: `https://techze-diagnostico-api.onrender.com/docs`
- **Frontend**: `https://techze-diagnostico-frontend.onrender.com`

### Logs
- Acesse o Dashboard do Render
- Clique no serviço desejado
- Aba "Logs" para monitoramento em tempo real

## 🎯 Próximos Passos

### Após Deploy Bem-sucedido
1. **Configurar Custom Domain** (opcional)
2. **Configurar Sentry** para monitoramento
3. **Configurar Redis** para melhor performance
4. **Configurar CI/CD** avançado
5. **Configurar Backup** do banco de dados

### Otimizações Recomendadas
1. **Caching**: Implementar Redis para cache
2. **CDN**: Configurar CDN para assets estáticos
3. **Monitoring**: Configurar alertas no Sentry
4. **Performance**: Monitorar métricas de performance
5. **Security**: Implementar rate limiting e CORS

## 📞 Suporte

### Recursos Úteis
- [Documentação do Render](https://render.com/docs)
- [Suporte do Render](https://render.com/support)
- [Status do Render](https://status.render.com)

### Comandos Úteis
```bash
# Verificar status dos serviços
curl https://techze-diagnostico-api.onrender.com/health

# Verificar logs via API (com API Key)
curl -H "Authorization: Bearer $RENDER_API_KEY" \
     https://api.render.com/v1/services/SERVICE_ID/logs

# Redeployar serviço via API
curl -X POST -H "Authorization: Bearer $RENDER_API_KEY" \
     https://api.render.com/v1/services/SERVICE_ID/deploys
```

---

## ✅ Checklist Final

- [ ] Scripts de automação executados
- [ ] Secrets configurados no Render
- [ ] Blueprint criado e conectado ao GitHub
- [ ] Primeiro deploy realizado com sucesso
- [ ] API respondendo no endpoint `/health`
- [ ] Frontend carregando corretamente
- [ ] Logs sem erros críticos
- [ ] URLs de produção funcionando

**🎉 Parabéns! Sua aplicação está no ar!**

---

*Gerado automaticamente pelo sistema de automação TechZe Diagnostico*