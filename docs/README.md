# TechZe-Diagnostico - Documentação Completa

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura do Sistema](#arquitetura-do-sistema)
3. [Guia de Instalação](#guia-de-instalação)
4. [Manual do Usuário](#manual-do-usuário)
5. [Manual Técnico](#manual-técnico)
6. [API Documentation](#api-documentation)
7. [Troubleshooting](#troubleshooting)

## 🎯 Visão Geral

O **TechZe-Diagnostico** é um sistema completo de diagnóstico de hardware e software desenvolvido para atender até 4 lojas de assistência técnica. O sistema oferece:

### Funcionalidades Principais
- ✅ **Diagnóstico Completo**: CPU, Memória, Disco, Rede
- ✅ **Interface Web Responsiva**: Dashboard moderno e intuitivo
- ✅ **APIs RESTful**: Integração fácil com outros sistemas
- ✅ **Relatórios PDF**: Documentação profissional dos diagnósticos
- ✅ **Monitoramento em Tempo Real**: Performance e métricas
- ✅ **Sistema de Cache**: Otimização de performance
- ✅ **Rate Limiting**: Proteção contra sobrecarga

### Status Atual
🎊 **87% Completo** - Sistema pronto para produção!

**Componentes Ativos:**
- ✅ Backend FastAPI (8000)
- ✅ Frontend React (5173)  
- ✅ Database Supabase
- ✅ Cache Redis
- ✅ Monitoramento Prometheus
- ✅ Deploy Automático (Render)

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Frontend React   │────│   Backend FastAPI   │────│   Database Supabase │
│   Port: 5173       │    │   Port: 8000        │    │   PostgreSQL + Auth │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
           │                           │                           │
           │                           │                           │
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   CDN / Static     │    │   Cache Redis       │    │   File Storage      │
│   Assets           │    │   Performance       │    │   Reports & Logs    │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

### Tecnologias Utilizadas

**Backend:**
- FastAPI 0.104.1
- Python 3.12+
- SQLAlchemy 2.0
- Pydantic 2.5
- Supabase 2.3

**Frontend:**
- React 18+
- TypeScript
- Vite
- Tailwind CSS

**Infraestrutura:**
- Docker
- Render (Deploy)
- GitHub Actions (CI/CD)
- Prometheus (Monitoring)

## 🚀 Guia de Instalação

### Pré-requisitos
- Python 3.12+
- Node.js 18+
- Git
- Docker (opcional)

### Instalação Local

#### 1. Clone o Repositório
```bash
git clone https://github.com/seu-usuario/TechZe-Diagnostico.git
cd TechZe-Diagnostico
```

#### 2. Configure o Backend
```bash
cd microservices/diagnostic_service
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

#### 3. Configure o Frontend
```bash
cd ../../  # Volta para raiz
npm install
```

#### 4. Variáveis de Ambiente
Crie um arquivo `.env` na raiz:
```env
# Supabase
SUPABASE_URL=sua_url_aqui
SUPABASE_KEY=sua_key_aqui

# Redis (opcional)
REDIS_URL=redis://localhost:6379

# Configurações
ENVIRONMENT=development
DEBUG=true
```

#### 5. Execute o Sistema
```bash
# Terminal 1 - Backend
cd microservices/diagnostic_service
python -m app.main

# Terminal 2 - Frontend  
npm run dev
```

### Instalação com Docker
```bash
docker-compose up -d
```

## 👥 Manual do Usuário

### Acesso ao Sistema
1. Abra o navegador em `http://localhost:5173`
2. A interface principal será exibida

### Executando Diagnóstico

#### Diagnóstico Rápido
1. Clique em **"Iniciar Diagnóstico"**
2. Aguarde a análise completa (30-60 segundos)
3. Visualize os resultados no dashboard

#### Diagnóstico Detalhado
1. Selecione **"Diagnóstico Avançado"**
2. Escolha os componentes específicos:
   - CPU e Performance
   - Memória RAM
   - Discos e Storage
   - Rede e Conectividade
3. Configure parâmetros avançados
4. Execute e acompanhe em tempo real

### Interpretando Resultados

#### Indicadores de Saúde
- 🟢 **Verde (80-100%)**: Componente saudável
- 🟡 **Amarelo (60-79%)**: Atenção necessária  
- 🔴 **Vermelho (<60%)**: Problema crítico

#### Relatórios
- **PDF**: Download automático após diagnóstico
- **Histórico**: Acesse diagnósticos anteriores
- **Comparação**: Compare resultados ao longo do tempo

### Funcionalidades Avançadas

#### Dashboard de Monitoramento
- Métricas em tempo real
- Alertas de performance
- Gráficos de tendência

#### Configurações
- Personalizar thresholds de alerta
- Configurar relatórios automáticos
- Gerenciar usuários (futuro)

## 🔧 Manual Técnico

### Arquitetura do Backend

#### Estrutura de Pastas
```
microservices/diagnostic_service/
├── app/
│   ├── api/           # Endpoints REST
│   ├── core/          # Configurações centrais
│   ├── services/      # Lógica de negócio
│   ├── models/        # Modelos de dados
│   └── schemas/       # Validação Pydantic
├── tests/             # Testes automatizados
└── docs/              # Documentação
```

#### Principais Módulos

**Services/Analyzers:**
- `cpu_analyzer.py`: Análise de processador
- `memory_analyzer.py`: Análise de memória
- `disk_analyzer.py`: Análise de discos
- `network_analyzer.py`: Análise de rede

**Core Systems:**
- `database_pool.py`: Pool de conexões otimizado
- `query_optimizer.py`: Otimização de queries
- `cache_manager.py`: Sistema de cache
- `monitoring.py`: Métricas e alertas

### Performance Optimization

#### Connection Pooling
```python
# Configuração automática
pool_manager.initialize_pool("main", {
    "max_connections": 20,
    "min_connections": 5
})
```

#### Query Caching
```python
# Cache automático para queries lentas
result = await query_optimizer.execute_optimized_query(
    "SELECT * FROM diagnostics WHERE date > ?",
    {"date": "2024-01-01"}
)
```

#### Rate Limiting
```python
# Configurado automaticamente
# Default: 100 requests/minute por IP
```

### Configurações Avançadas

#### Environment Variables
```env
# Performance
RATE_LIMIT_ENABLED=true
PROMETHEUS_ENABLED=true
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=sua_chave_secreta
ALGORITHM=HS256

# Monitoring
SENTRY_DSN=sua_sentry_dsn
LOG_LEVEL=INFO
```

#### Monitoramento
- **Prometheus**: `http://localhost:8000/metrics`
- **Health Check**: `http://localhost:8000/health`
- **Performance**: `http://localhost:8000/api/v3/performance/stats`

### Desenvolvimento

#### Executar Testes
```bash
# Testes unitários
python -m pytest tests/test_performance.py -v

# Testes de integração  
python -m pytest tests/test_integration.py -v

# Suite completa
python run_tests.py
```

#### Adicionar Novos Analyzers
1. Crie arquivo em `services/analyzers/`
2. Herde de `BaseAnalyzer`
3. Implemente método `analyze()`
4. Registre no `__init__.py`

```python
class CustomAnalyzer(BaseAnalyzer):
    async def analyze(self) -> AnalysisResult:
        # Sua lógica aqui
        return AnalysisResult(...)
```

## 📡 API Documentation

### Base URL
- **Desenvolvimento**: `http://localhost:8000`
- **Produção**: `https://techze-diagnostic-backend.onrender.com`

### Autenticação
```http
Authorization: Bearer {token}
```

### Endpoints Principais

#### Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-06T12:00:00Z"
}
```

#### Executar Diagnóstico
```http
POST /api/v1/diagnostic/quick
```
**Response:**
```json
{
  "id": "diag-123",
  "status": "completed",
  "results": {
    "cpu": {"health": 85, "issues": []},
    "memory": {"health": 92, "issues": []},
    "disk": {"health": 78, "issues": ["Low space on C:"]},
    "network": {"health": 95, "issues": []}
  }
}
```

#### Performance Stats
```http
GET /api/v3/performance/stats
```
**Response:**
```json
{
  "database_pools": {...},
  "query_performance": {...},
  "cache_stats": {...}
}
```

### Códigos de Status
- `200`: Sucesso
- `400`: Dados inválidos
- `401`: Não autorizado
- `404`: Não encontrado
- `429`: Rate limit excedido
- `500`: Erro interno

## 🚨 Troubleshooting

### Problemas Comuns

#### Backend não inicia
**Sintomas:** Erro ao executar `python -m app.main`
**Soluções:**
1. Verificar ambiente virtual ativado
2. Instalar dependências: `pip install -r requirements.txt`
3. Verificar arquivo `.env`
4. Verificar porta 8000 disponível

#### Frontend não carrega
**Sintomas:** Erro ao acessar `localhost:5173`
**Soluções:**
1. Executar `npm install`
2. Verificar versão Node.js (18+)
3. Limpar cache: `npm run build`
4. Verificar porta 5173 disponível

#### Erro de conexão com banco
**Sintomas:** "Database connection failed"
**Soluções:**
1. Verificar credenciais Supabase
2. Testar conectividade de rede
3. Verificar configuração de CORS
4. Revisar logs do backend

#### Performance baixa
**Sintomas:** Respostas lentas (>2s)
**Soluções:**
1. Verificar cache Redis funcionando
2. Monitorar uso de CPU/memória
3. Analisar queries lentas
4. Verificar connection pool

### Logs e Debugging

#### Logs do Backend
```bash
# Visualizar logs em tempo real
tail -f logs/app.log

# Logs específicos
grep "ERROR" logs/app.log
```

#### Debug Mode
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

#### Performance Profiling
```bash
# Análise de performance
python -m pytest --cov=app tests/
```

### Contato Suporte
- **Email**: suporte@techze.com
- **GitHub Issues**: [Link para issues]
- **Discord**: [Link do servidor]

---

## 📄 Changelog

### v0.1.0 (2024-01-06)
- ✅ Sistema base implementado
- ✅ APIs v3 com performance optimization
- ✅ Frontend responsivo completo
- ✅ Deploy automático configurado
- ✅ Suite de testes implementada

---

*Documentação atualizada em: 06/01/2025*