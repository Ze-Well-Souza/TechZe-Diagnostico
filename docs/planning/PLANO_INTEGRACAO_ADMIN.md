# Plano de Integração - Sistema Administrativo TechZe

## Estrutura de Acesso Proposta

### 1. **Hierarquia de Usuários**
```
Administrador Master (Super Admin)
├── Dashboard Global
├── Gestão de Lojas
├── Gestão de Administradores de Loja
├── Configurações Globais
└── Relatórios Consolidados

Administrador de Loja
├── Dashboard da Loja
├── Gestão de Clientes da Loja
├── Diagnósticos da Loja
└── Relatórios da Loja

Cliente/Técnico
├── Interface de Diagnóstico
└── Visualização de Relatórios
```

### 2. **Páginas a Implementar**

#### 2.1 Sistema de Autenticação
- [x] **Login Master Admin** (`/admin-login`)
- [ ] **Login Lojista** (`/loja-login`) 
- [ ] **Recuperação de Senha**
- [ ] **Gestão de Sessões**

#### 2.2 Área Administrativa (Master)
- [x] **Dashboard Global** (`/admin/dashboard-global`)
- [x] **Gestão de Clientes** (`/admin/clientes`)
- [ ] **Gestão de Lojas** (`/admin/lojas`)
- [ ] **Gestão de Usuários** (`/admin/usuarios`)
- [ ] **Configurações** (`/admin/configuracoes`)
- [ ] **Relatórios** (`/admin/relatorios`)

#### 2.3 Área do Lojista
- [ ] **Dashboard da Loja** (`/loja/dashboard`)
- [ ] **Clientes da Loja** (`/loja/clientes`)
- [ ] **Diagnósticos** (`/loja/diagnosticos`)
- [ ] **Configurações da Loja** (`/loja/configuracoes`)

### 3. **Componentes a Converter/Criar**

#### 3.1 Componentes do Dashboard Global (✅ Já implementados)
- [x] `GlassCard` - Cards com efeito glassmorphism
- [x] `ProgressRing` - Anéis de progresso animados
- [x] `BentoGrid` - Layout em grid moderno
- [x] `GlobalStats` - Estatísticas globais

#### 3.2 Componentes de Gestão de Clientes (✅ Já implementados)
- [x] `ClientesManagement` - Página principal
- [x] Sistema de filtros e busca
- [x] Modal de cadastro/edição
- [x] Visualizações em grid e tabela

#### 3.3 Novos Componentes Necessários
- [ ] `LoginAdmin` - Tela de login do administrador
- [ ] `LoginLoja` - Tela de login do lojista
- [ ] `GestaoLojas` - CRUD de lojas
- [ ] `GestaoUsuarios` - CRUD de usuários/administradores
- [ ] `DashboardLoja` - Dashboard específico da loja
- [ ] `Configuracoes` - Painel de configurações

### 4. **Integração com APIs Reais**

#### 4.1 Supabase Setup
```typescript
// Configuração já disponível:
PROJECT_ID: waxnnwpsvitmeeivkwkn
ANON_KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SERVICE_ROLE: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 4.2 Tabelas Necessárias
- `usuarios` (admin_master, admin_loja, tecnico)
- `lojas` (centro, norte, sul, etc.)
- `clientes` (dados dos clientes)
- `diagnosticos` (histórico de diagnósticos)
- `configuracoes` (configurações do sistema)

#### 4.3 Autenticação e Autorização
- [ ] Sistema de roles (master_admin, loja_admin, tecnico)
- [ ] JWT tokens com refresh
- [ ] Middleware de proteção de rotas
- [ ] Sistema de permissões granulares

### 5. **Arquivos a Processar**

#### 5.1 Manter e Integrar:
- ✅ `style.css` → Já convertido para `glassmorphism.css`
- ✅ Funcionalidades do `app.js` → Já convertidas para React
- ✅ Layout do `index.html` → Já convertido para componentes React

#### 5.2 Deletar (já integrados):
- [ ] `Analisar_front_dash_adm/index.html`
- [ ] `Analisar_front_dash_adm/index1.html`
- [ ] `Analisar_front_dash_adm/app.js`
- [ ] `Analisar_front_dash_adm/app1.js`
- [ ] `Analisar_front_dash_adm/style.css`
- [ ] `Analisar_front_dash_adm/style1.css`

### 6. **Próximos Passos**

#### Fase 1: Autenticação
1. Criar componente `LoginAdmin`
2. Implementar autenticação com Supabase
3. Sistema de proteção de rotas
4. Gestão de sessões

#### Fase 2: Gestão de Lojas
1. CRUD de lojas
2. Associação loja-administrador
3. Dashboard específico por loja

#### Fase 3: Sistema Completo
1. Área do lojista
2. Permissões granulares
3. Relatórios avançados
4. Configurações globais

#### Fase 4: Deploy e Produção
1. Configuração de variáveis de ambiente
2. Deploy no Render com domínio techreparo.com
3. Monitoramento e logs
4. Backup e recuperação

### 7. **Ordem de Implementação**

1. **Imediato**: Limpar arquivos HTML/JS da pasta de análise
2. **Próximo**: Implementar autenticação de admin master
3. **Seguinte**: Criar gestão de lojas
4. **Final**: Sistema completo com lojistas

---

## Status de Implementação

### ✅ Concluído (75%)
- [x] Análise dos arquivos HTML existentes
- [x] Definição da hierarquia de usuários
- [x] Criação do plano de integração
- [x] Implementação do sistema de rotas
- [x] Conversão do Login Administrativo para React
- [x] Conversão da Gestão de Lojas para React
- [x] Configuração do Supabase (client e tipos)
- [x] Criação do hook useAuth
- [x] Implementação do ProtectedRoute
- [x] Criação do Dashboard da Loja
- [x] Limpeza dos arquivos HTML/JS desnecessários

### 🔄 Em Andamento (20%)
- [x] Sistema de autenticação (modo desenvolvimento)
- [ ] Configuração completa do banco de dados
- [ ] Integração real com APIs do Supabase

### ⏳ Próximos Passos (5%)
- [ ] Executar script SQL no Supabase
- [ ] Ativar autenticação real
- [ ] Implementação de CRUDs completos
- [ ] Sistema de permissões granulares
- [ ] Formulários de cadastro/edição
- [ ] Dashboard com dados reais
- [ ] Testes de integração

**Status Atual**: ✅ Sistema administrativo 75% implementado
**Próximo**: 🔄 Configuração do banco e integração com APIs reais 