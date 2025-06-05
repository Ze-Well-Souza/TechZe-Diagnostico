
# TechZe Diagnóstico - Documentação Completa

## 📋 Visão Geral

Sistema completo de diagnóstico técnico multi-tenant para lojas de assistência técnica, desenvolvido com React, FastAPI e Supabase.

## 🏗️ Arquitetura

### Frontend (React + TypeScript)
- **Framework**: React 18 + Vite
- **Linguagem**: TypeScript
- **UI**: Tailwind CSS + Shadcn/UI
- **Estado**: React Query + Context API
- **PWA**: Service Worker + Offline Support

### Backend (Python + FastAPI)
- **Framework**: FastAPI
- **Linguagem**: Python 3.11+
- **Banco**: Supabase (PostgreSQL)
- **Cache**: Redis (opcional)
- **Monitoramento**: Prometheus + Grafana

## 🚀 Funcionalidades Implementadas

### ✅ Multi-Tenancy
- Isolamento completo de dados por loja
- Autenticação JWT com contexto de empresa
- Políticas RLS (Row Level Security)
- Troca dinâmica entre empresas

### ✅ Segurança
- Autenticação robusta com Supabase Auth
- Autorização baseada em roles
- Auditoria completa de ações
- Circuit Breaker para integrações

### ✅ Diagnósticos
- Análise completa de CPU, memória, disco
- Detecção de antivírus e drivers
- Relatórios em PDF
- Histórico completo

### ✅ Monitoramento
- Métricas Prometheus
- Dashboards por empresa
- Alertas automáticos
- Logs de auditoria

### ✅ Integração
- Zendesk (tickets)
- Sistemas de nota fiscal
- Email automático
- Webhooks para CRM

### ✅ Qualidade
- Testes unitários (Vitest)
- Testes E2E (Cypress)
- Cobertura de código
- CI/CD GitHub Actions

## 📦 Instalação e Setup

### Pré-requisitos
```bash
node >= 18
python >= 3.11
docker (opcional)
```

### Frontend
```bash
npm install
npm run dev
```

### Backend
```bash
cd microservices/diagnostic_service
pip install -r requirements.txt
python app/main.py
```

### Testes
```bash
# Frontend
npm run test
npm run test:e2e

# Backend
cd microservices/diagnostic_service
pytest
```

## 🏢 Multi-Tenancy - Como Funciona

### 1. Estrutura de Dados
```sql
-- Empresas
CREATE TABLE companies (
  id UUID PRIMARY KEY,
  code TEXT UNIQUE,
  name TEXT,
  subdomain TEXT
);

-- Usuários por empresa
CREATE TABLE company_users (
  user_id UUID REFERENCES auth.users,
  company_id UUID REFERENCES companies,
  role TEXT DEFAULT 'tecnico'
);
```

### 2. Políticas RLS
```sql
-- Exemplo para dispositivos
CREATE POLICY "Isolamento por empresa" 
ON devices FOR ALL 
USING (
  EXISTS (
    SELECT 1 FROM profiles p
    WHERE p.id = auth.uid() 
    AND p.current_company_id = devices.company_id
  )
);
```

### 3. Uso no Frontend
```typescript
// Inicializar tenant
await multiTenantService.initializeTenant('empresa-123');

// Trocar empresa
await multiTenantService.switchTenant('empresa-456');

// Verificar permissões
const claims = await jwtAuthService.getCurrentUserClaims();
const hasPermission = jwtAuthService.hasPermission(claims, 'diagnostics:write');
```

## 🔒 Segurança

### Autenticação JWT
- Tokens com claims customizados
- Renovação automática
- Contexto de empresa no token

### Auditoria
```typescript
// Log automático de ações
await AuditService.logAction('DIAGNOSTIC_CREATED', 'DEVICE', deviceId, {
  health_score: 85,
  issues_found: 3
});
```

### Backup Automático
```typescript
// Agendar backups
await BackupService.scheduleAutomaticBackups('empresa-123', 24); // 24h
```

## 📊 Monitoramento

### Métricas Coletadas
- Performance de requisições
- Saúde dos dispositivos
- Uso por empresa
- Erros e exceptions

### Dashboards
- Visão geral por empresa
- Comparativo entre lojas
- Alertas em tempo real

## 🔌 Integrações

### Zendesk
```typescript
await IntegrationService.createZendeskTicket({
  subject: 'Problema no dispositivo',
  description: 'Diagnóstico encontrou falhas',
  priority: 'high'
}, diagnosticId);
```

### Nota Fiscal
```typescript
await IntegrationService.emitirNotaFiscal({
  valor: 150.00,
  descricao: 'Serviço de diagnóstico',
  clienteId: 'cliente-123'
}, diagnosticId);
```

## 🧪 Testes

### Estrutura de Testes
```
src/tests/
├── unit/           # Testes unitários
├── integration/    # Testes de integração
└── e2e/           # Testes end-to-end

cypress/
├── e2e/           # Testes Cypress
└── support/       # Comandos customizados
```

### Comandos Cypress
```typescript
// Login multi-tenant
cy.login('user@empresa.com', 'password');
cy.switchCompany('empresa-123');

// Testar isolamento
cy.createDevice({ name: 'Laptop', type: 'laptop' });
cy.switchCompany('empresa-456');
cy.get('[data-testid="devices-list"]').should('not.contain', 'Laptop');
```

## 🚀 Deploy

### CI/CD Pipeline
1. **Testes**: Unitários + E2E paralelos
2. **Build**: Por ambiente (dev/staging/prod)
3. **Deploy Canário**: Lançamento progressivo
4. **Monitoramento**: Health checks automáticos

### Ambientes
- **Development**: Auto-deploy em PRs
- **Staging**: Deploy manual
- **Production**: Deploy canário com aprovação

## 📈 Performance

### Otimizações Implementadas
- Cache distribuído (Redis)
- Lazy loading de componentes
- Otimização de queries
- Circuit breaker para APIs externas

### Métricas de Performance
- Tempo de resposta < 200ms
- Disponibilidade > 99.9%
- Taxa de erro < 0.1%

## 🛠️ Manutenção

### Logs e Debugging
- Logs estruturados (JSON)
- Correlation IDs
- Métricas de negócio
- Alertas proativos

### Backup e Recovery
- Backup automático diário
- Retenção de 30 dias
- Restore point-in-time
- Testes de recovery mensais

## 📞 Suporte

### Troubleshooting
1. Verificar logs de auditoria
2. Consultar métricas Prometheus
3. Validar políticas RLS
4. Testar conectividade APIs

### Contatos
- **Técnico**: Consultar logs e métricas
- **Funcional**: Documentação interativa
- **Emergência**: Alertas automáticos

## 🔄 Roadmap

### Próximas Funcionalidades
- [ ] Chat bot IA integrado
- [ ] Análise preditiva
- [ ] API pública para parceiros
- [ ] Mobile app nativo

### Melhorias Planejadas
- [ ] Cache ainda mais otimizado
- [ ] Mais integrações (SAP, ERP)
- [ ] Dashboard executivo
- [ ] Relatórios avançados
