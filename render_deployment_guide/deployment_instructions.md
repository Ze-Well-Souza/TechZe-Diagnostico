# 🚀 GUIA COMPLETO DE DEPLOY NO RENDER

## Fase 1: Configuração de Secrets (30 minutos)

### Passo 1: Acesse o Dashboard do Render
1. Acesse https://dashboard.render.com
2. Faça login na sua conta
3. No menu lateral, clique em **Environment Groups**
4. Clique em **New Environment Group**
5. Nomeie como: `techze-diagnostico-secrets`

### Passo 2: Adicione os Secrets

**1. SUPABASE_URL** (OBRIGATÓRIO)
- Clique em **Add Environment Variable**
- Key: `SUPABASE_URL`
- Value: [Insira o valor real aqui]
- Descrição: URL do projeto Supabase
- Formato esperado: `https://seu-projeto.supabase.co`

**2. SUPABASE_ANON_KEY** (OBRIGATÓRIO)
- Clique em **Add Environment Variable**
- Key: `SUPABASE_ANON_KEY`
- Value: [Insira o valor real aqui]
- Descrição: Chave anônima do Supabase (pública)
- Formato esperado: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**3. SUPABASE_SERVICE_ROLE_KEY** (OBRIGATÓRIO)
- Clique em **Add Environment Variable**
- Key: `SUPABASE_SERVICE_ROLE_KEY`
- Value: [Insira o valor real aqui]
- Descrição: Chave de service role do Supabase (privada)
- Formato esperado: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**4. JWT_SECRET_KEY** (OBRIGATÓRIO)
- Clique em **Add Environment Variable**
- Key: `JWT_SECRET_KEY`
- Value: [Insira o valor real aqui]
- Descrição: Chave secreta para assinatura de tokens JWT
- Formato esperado: `sua-chave-secreta-super-segura-aqui`

**5. REDIS_URL** (OPCIONAL)
- Clique em **Add Environment Variable**
- Key: `REDIS_URL`
- Value: [Insira o valor real aqui]
- Descrição: URL de conexão com Redis (opcional para cache)
- Formato esperado: `redis://localhost:6379`

**6. SENTRY_DSN** (OPCIONAL)
- Clique em **Add Environment Variable**
- Key: `SENTRY_DSN`
- Value: [Insira o valor real aqui]
- Descrição: DSN do Sentry para monitoramento de erros
- Formato esperado: `https://chave@sentry.io/projeto`

## Fase 2: Criação do Blueprint (15 minutos)

### Passo 1: Criar Blueprint
1. No dashboard do Render, clique em **Blueprints**
2. Clique em **New Blueprint**
3. Conecte ao seu repositório GitHub
4. Selecione o repositório: `TechZe-Diagnostico`
5. Branch: `main`
6. Blueprint file: `render.yaml` (já configurado)

### Passo 2: Configurar Environment Group
1. Na seção **Environment Groups**, selecione: `techze-diagnostico-secrets`
2. Clique em **Create Blueprint**

### Passo 3: Deploy Automático
1. O Render irá automaticamente:
   - Criar o serviço de API (techze-diagnostico-api)
   - Criar o serviço de Frontend (techze-diagnostico-frontend)
   - Configurar as variáveis de ambiente
   - Iniciar o primeiro deploy

## Fase 3: Verificação (10 minutos)

### URLs de Acesso
- **API**: https://techze-diagnostico-api.onrender.com
- **Frontend**: https://techze-diagnostico-frontend.onrender.com
- **Health Check**: https://techze-diagnostico-api.onrender.com/health

### Verificações
- [ ] API responde no endpoint /health
- [ ] Frontend carrega corretamente
- [ ] Logs não mostram erros críticos
- [ ] Conexão com Supabase funcionando
