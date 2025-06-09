# API Core - TechZe Diagnóstico

Esta é a nova API Core consolidada que unifica todas as funcionalidades das APIs v1 e v3 em uma estrutura modular e escalável.

## Estrutura da API Core

### Módulos Principais

#### 1. Autenticação (`/auth`)
- **Login e Registro**: Endpoints para autenticação de usuários
- **Gestão de Tokens**: JWT tokens com refresh automático
- **Perfil de Usuário**: Gerenciamento de informações do usuário
- **Integração Supabase**: Autenticação segura com Supabase

**Endpoints principais:**
- `POST /auth/login` - Login do usuário
- `POST /auth/register` - Registro de novo usuário
- `GET /auth/profile` - Perfil do usuário atual
- `POST /auth/logout` - Logout do usuário
- `POST /auth/refresh` - Renovação de token
- `GET /auth/health` - Health check do sistema de autenticação

#### 2. Diagnósticos (`/diagnostics`)
- **Execução de Diagnósticos**: Diagnósticos rápidos, padrão e completos
- **Análise com IA**: Diagnósticos avançados com inteligência artificial
- **Histórico**: Gestão completa do histórico de diagnósticos
- **Relatórios**: Geração de relatórios detalhados

**Endpoints principais:**
- `POST /diagnostics/run` - Executar diagnóstico
- `GET /diagnostics/health` - Saúde do sistema em tempo real
- `GET /diagnostics/history` - Histórico de diagnósticos
- `GET /diagnostics/{id}` - Detalhes de diagnóstico específico
- `DELETE /diagnostics/{id}` - Remover diagnóstico
- `GET /diagnostics/{id}/report` - Gerar relatório

#### 3. Inteligência Artificial (`/ai`)
- **Predição**: Análise preditiva do comportamento do sistema
- **Detecção de Anomalias**: Identificação automática de problemas
- **Análise de Padrões**: Reconhecimento de padrões no sistema
- **Recomendações**: Sugestões inteligentes de otimização
- **Gestão de Modelos**: Treinamento e gerenciamento de modelos ML

**Endpoints principais:**
- `POST /ai/predict` - Predição de comportamento
- `POST /ai/detect-anomalies` - Detecção de anomalias
- `POST /ai/analyze-patterns` - Análise de padrões
- `GET /ai/recommendations` - Recomendações inteligentes
- `GET /ai/models` - Informações dos modelos
- `POST /ai/train-model` - Treinar modelo
- `GET /ai/health` - Health check dos sistemas de IA

#### 4. Automação (`/automation`)
- **Gestão de Tarefas**: Criação e execução de tarefas automatizadas
- **Workflows**: Fluxos de trabalho complexos
- **Regras de Automação**: Configuração de regras automáticas
- **Agendamento**: Execução programada de tarefas

**Endpoints principais:**
- `POST /automation/tasks` - Criar tarefa
- `GET /automation/tasks` - Listar tarefas
- `POST /automation/tasks/{id}/execute` - Executar tarefa
- `GET /automation/workflows` - Listar workflows
- `POST /automation/rules` - Criar regra de automação
- `GET /automation/health` - Health check do sistema

#### 5. Análise e Relatórios (`/analytics`)
- **Consultas de Dados**: Análise avançada de dados
- **Relatórios Personalizados**: Geração de relatórios sob medida
- **Dashboards**: Criação e gestão de dashboards
- **Métricas em Tempo Real**: Monitoramento contínuo
- **Análise de Tendências**: Identificação de tendências

**Endpoints principais:**
- `POST /analytics/query` - Consultar dados
- `POST /analytics/reports` - Gerar relatório
- `GET /analytics/reports` - Listar relatórios
- `POST /analytics/dashboards` - Criar dashboard
- `GET /analytics/metrics/realtime` - Métricas em tempo real
- `GET /analytics/trends` - Análise de tendências

#### 6. Performance (`/performance`)
- **Métricas do Sistema**: Monitoramento completo de recursos
- **Alertas**: Sistema avançado de alertas e notificações
- **Análise de Performance**: Identificação de gargalos
- **Otimização**: Ferramentas de otimização automática
- **Dashboard de Monitoramento**: Visão consolidada da performance

**Endpoints principais:**
- `GET /performance/metrics/system` - Métricas do sistema
- `GET /performance/metrics/database` - Métricas do banco
- `GET /performance/health` - Health check de performance
- `POST /performance/alerts/rules` - Criar regra de alerta
- `GET /performance/alerts/active` - Alertas ativos
- `GET /performance/recommendations` - Recomendações de otimização
- `GET /performance/dashboard` - Dashboard de monitoramento

#### 7. Chat e Assistente Virtual (`/chat`)
- **Sessões de Chat**: Gestão completa de conversas
- **Assistente Virtual**: IA conversacional para suporte
- **WebSocket**: Chat em tempo real
- **Contexto Inteligente**: Manutenção de contexto nas conversas
- **Capacidades do Assistente**: Integração com todos os módulos

**Endpoints principais:**
- `POST /chat/sessions` - Criar sessão de chat
- `GET /chat/sessions` - Listar sessões
- `POST /chat/sessions/{id}/messages` - Enviar mensagem
- `GET /chat/sessions/{id}/messages` - Histórico de mensagens
- `WS /chat/sessions/{id}/ws` - WebSocket para chat em tempo real
- `GET /chat/assistant/capabilities` - Capacidades do assistente
- `POST /chat/assistant/execute` - Executar ação do assistente

## Características da API Core

### 🔒 Segurança
- Autenticação JWT com refresh tokens
- Integração segura com Supabase
- Validação rigorosa de dados
- Rate limiting e proteção contra ataques

### 🚀 Performance
- Arquitetura modular e escalável
- Cache inteligente
- Otimização de consultas
- Monitoramento contínuo de performance

### 🤖 Inteligência Artificial
- Análise preditiva avançada
- Detecção automática de anomalias
- Recomendações inteligentes
- Assistente virtual conversacional

### 📊 Monitoramento
- Métricas em tempo real
- Sistema avançado de alertas
- Dashboards interativos
- Análise de tendências

### 🔄 Automação
- Tarefas automatizadas
- Workflows complexos
- Regras de automação
- Agendamento inteligente

## Migração das APIs Antigas

### De v1 para Core
- ✅ Autenticação migrada e aprimorada
- ✅ Diagnósticos consolidados com novas funcionalidades
- ✅ Estrutura modular implementada

### De v3 para Core
- ✅ IA e ML totalmente integrados
- ✅ Análise avançada consolidada
- ✅ Performance e monitoramento unificados

### Novas Funcionalidades
- ✅ Sistema de chat e assistente virtual
- ✅ Automação avançada
- ✅ Dashboard unificado
- ✅ WebSocket para tempo real

## Uso da API

### Endpoint Base
```
GET /api/core/info
```

### Autenticação
```bash
# Login
curl -X POST /api/core/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Usar token nas requisições
curl -X GET /api/core/diagnostics/health \
  -H "Authorization: Bearer <token>"
```

### Exemplos de Uso

#### Executar Diagnóstico
```bash
curl -X POST /api/core/diagnostics/run \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"type": "comprehensive", "include_ai": true}'
```

#### Chat com Assistente
```bash
# Criar sessão
curl -X POST /api/core/chat/sessions \
  -H "Authorization: Bearer <token>" \
  -d 'user_id=123&title=Diagnóstico do Sistema'

# Enviar mensagem
curl -X POST /api/core/chat/sessions/{session_id}/messages \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "Preciso verificar a performance do sistema", "user_id": "123"}'
```

#### Métricas de Performance
```bash
curl -X GET /api/core/performance/metrics/system \
  -H "Authorization: Bearer <token>"
```

## Próximos Passos

1. **Testes de Integração**: Validar todos os endpoints
2. **Documentação Interativa**: Swagger/OpenAPI completo
3. **Monitoramento**: Implementar métricas detalhadas
4. **Otimização**: Performance tuning baseado em uso real
5. **Expansão**: Novos módulos conforme necessidade

## Suporte

Para dúvidas ou problemas:
- Consulte a documentação técnica completa
- Use o assistente virtual integrado
- Verifique os logs de sistema
- Entre em contato com a equipe de desenvolvimento