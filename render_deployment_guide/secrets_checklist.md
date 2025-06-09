# 🔐 CHECKLIST DE SECRETS PARA RENDER

## Secrets Obrigatórios

[ ] **SUPABASE_URL**
   - Descrição: URL do projeto Supabase
   - Exemplo: `https://seu-projeto.supabase.co`

[ ] **SUPABASE_ANON_KEY**
   - Descrição: Chave anônima do Supabase (pública)
   - Exemplo: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

[ ] **SUPABASE_SERVICE_ROLE_KEY**
   - Descrição: Chave de service role do Supabase (privada)
   - Exemplo: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

[ ] **JWT_SECRET_KEY**
   - Descrição: Chave secreta para assinatura de tokens JWT
   - Exemplo: `sua-chave-secreta-super-segura-aqui`

## Secrets Opcionais

[ ] **REDIS_URL**
   - Descrição: URL de conexão com Redis (opcional para cache)
   - Exemplo: `redis://localhost:6379`

[ ] **SENTRY_DSN**
   - Descrição: DSN do Sentry para monitoramento de erros
   - Exemplo: `https://chave@sentry.io/projeto`
