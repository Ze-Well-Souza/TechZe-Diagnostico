# 🚀 TechZe Diagnostic Service - Funcionalidades Semana 2

## 📋 Resumo das Implementações

Esta documentação descreve as funcionalidades avançadas implementadas na **Semana 2** do projeto TechZe Diagnostic Service, focando em **monitoramento avançado**, **cache inteligente** e **dashboards operacionais**.

## 🎯 Funcionalidades Implementadas

### 1. 📊 Monitoramento Avançado (`advanced_monitoring.py`)

#### Características:
- **Coleta de Métricas Avançadas**: CPU, memória, disco, rede, processos
- **Sistema de Alertas Inteligente**: Alertas por severidade (info, warning, critical)
- **Dashboards Dinâmicos**: Operacional, segurança e negócio
- **Monitoramento em Tempo Real**: Coleta automática a cada 30 segundos

#### Componentes:
```python
# Classes principais
- AdvancedMonitoringService: Serviço principal de monitoramento
- MetricsCollector: Coleta métricas do sistema
- AlertManager: Gerencia alertas e notificações
- DashboardGenerator: Gera dashboards dinâmicos

# Estruturas de dados
- Alert: Representa um alerta do sistema
- Metric: Representa uma métrica coletada
- DashboardComponent: Componente de dashboard
```

#### Endpoints:
- `GET /api/v1/monitoring/dashboard/operational` - Dashboard operacional
- `GET /api/v1/monitoring/dashboard/security` - Dashboard de segurança
- `GET /api/v1/monitoring/alerts` - Lista alertas ativos
- `POST /api/v1/monitoring/alerts/{alert_id}/resolve` - Resolve alerta

### 2. 🔄 Sistema de Cache Avançado (`cache_manager.py`)

#### Características:
- **Cache Redis com Fallback**: Redis principal + memória como fallback
- **Múltiplas Estratégias**: LRU, LFU, TTL, FIFO
- **Cache Inteligente**: TTL automático por padrão de dados
- **Estatísticas Detalhadas**: Hit rate, utilização, performance

#### Componentes:
```python
# Classes principais
- CacheManager: Gerenciador principal
- RedisCache: Cache Redis com fallback
- MemoryCache: Cache em memória
- CacheEntry: Entrada individual do cache

# Estratégias disponíveis
- LRU (Least Recently Used)
- LFU (Least Frequently Used)
- TTL (Time To Live)
- FIFO (First In First Out)
```

#### Padrões de Cache:
```python
cache_patterns = {
    "diagnostic_results": {"ttl": 3600, "prefix": "diag:"},
    "system_metrics": {"ttl": 300, "prefix": "metrics:"},
    "user_sessions": {"ttl": 1800, "prefix": "session:"},
    "api_responses": {"ttl": 600, "prefix": "api:"},
    "reports": {"ttl": 7200, "prefix": "report:"}
}
```

#### Endpoints:
- `GET /api/v1/cache/stats` - Estatísticas do cache
- `POST /api/v1/cache/clear` - Limpa todo o cache
- `POST /api/v1/cache/invalidate/{pattern}` - Invalida padrão específico

### 3. 📈 Stack de Monitoramento Completo

#### Prometheus (`prometheus.yml`)
- **Coleta de Métricas**: Scraping automático do serviço
- **Regras de Alerta**: Alertas configurados para CPU, memória, erros
- **Retenção**: 30 dias de dados históricos

#### Grafana (`grafana_dashboards.json`)
- **Dashboard Operacional**: Métricas de sistema e performance
- **Dashboard de Segurança**: Eventos de segurança e autenticação
- **Dashboard de Negócio**: KPIs e métricas de diagnóstico

#### Alertmanager (`alert_rules.yml`)
- **Alertas de Sistema**: CPU, memória, disco
- **Alertas de Aplicação**: Taxa de erro, tempo de resposta
- **Alertas de Segurança**: Tentativas de login, rate limiting
- **Alertas de Negócio**: Taxa de sucesso, performance

### 4. 🔧 Ferramentas de Configuração

#### Setup Automático (`setup_monitoring_stack.py`)
```bash
# Configura todo o stack de monitoramento
python setup_monitoring_stack.py
```

**Funcionalidades:**
- Verifica dependências (Docker)
- Cria configurações do Docker Compose
- Inicia serviços (Prometheus, Grafana, Alertmanager, Redis)
- Configura datasources no Grafana
- Importa dashboards automaticamente

#### Teste Completo (`test_week2_features.py`)
```bash
# Testa todas as funcionalidades implementadas
python test_week2_features.py
```

**Testes incluídos:**
- Health checks básico e detalhado
- Dashboards operacional e de segurança
- Sistema de alertas
- Cache e estatísticas
- Webhook do Alertmanager
- Teste de carga básico

## 🚀 Como Usar

### 1. Configuração Inicial

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar stack de monitoramento
python setup_monitoring_stack.py

# 3. Iniciar serviço principal
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Acessar Dashboards

- **API Principal**: http://localhost:8000
- **Grafana**: http://localhost:3000 (admin/techze123)
- **Prometheus**: http://localhost:9090
- **Alertmanager**: http://localhost:9093

### 3. Testar Funcionalidades

```bash
# Executar testes completos
python test_week2_features.py

# Verificar métricas
curl http://localhost:8000/metrics

# Verificar health detalhado
curl http://localhost:8000/health/detailed

# Obter dashboard operacional
curl http://localhost:8000/api/v1/monitoring/dashboard/operational
```

## 📊 Métricas Disponíveis

### Métricas de Sistema
- `techze_system_cpu_usage_percent` - Uso de CPU
- `techze_system_memory_usage_percent` - Uso de memória
- `techze_system_disk_usage_percent` - Uso de disco
- `techze_system_network_bytes_sent` - Bytes enviados pela rede
- `techze_system_network_bytes_recv` - Bytes recebidos pela rede

### Métricas de Aplicação
- `techze_requests_total` - Total de requisições
- `techze_request_duration_seconds` - Duração das requisições
- `techze_errors_total` - Total de erros
- `techze_active_diagnostics` - Diagnósticos ativos
- `techze_connected_users` - Usuários conectados

### Métricas de Cache
- `techze_cache_hit_rate_percent` - Taxa de hit do cache
- `techze_cache_operations_total` - Operações de cache
- `techze_cache_size_bytes` - Tamanho do cache

### Métricas de Segurança
- `techze_auth_attempts_total` - Tentativas de autenticação
- `techze_rate_limit_exceeded_total` - Violações de rate limit
- `techze_security_events_total` - Eventos de segurança

## 🔔 Sistema de Alertas

### Alertas de Sistema
- **HighCPUUsage**: CPU > 80% por 5 minutos
- **CriticalCPUUsage**: CPU > 95% por 2 minutos
- **HighMemoryUsage**: Memória > 85% por 5 minutos
- **HighDiskUsage**: Disco > 90% por 10 minutos

### Alertas de Aplicação
- **HighErrorRate**: Taxa de erro > 0.1/s por 3 minutos
- **HighResponseTime**: Tempo resposta > 5s por 5 minutos
- **ServiceDown**: Serviço indisponível por 1 minuto
- **LowCacheHitRate**: Hit rate < 70% por 10 minutos

### Alertas de Segurança
- **HighFailedLoginAttempts**: Falhas de login > 0.5/s por 2 minutos
- **HighRateLimitViolations**: Violações > 1/s por 3 minutos
- **CriticalSecurityEvent**: Eventos críticos de segurança

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```bash
# Cache Redis
REDIS_URL=redis://localhost:6379

# Monitoramento
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true

# Alertas
ALERTMANAGER_WEBHOOK_URL=http://localhost:8000/api/v1/alerts/webhook
```

### Configuração do Cache

```python
# Configurar padrões de cache personalizados
cache_manager.cache_patterns["custom_data"] = {
    "ttl": 1800,  # 30 minutos
    "prefix": "custom:"
}
```

### Configuração de Alertas

```python
# Criar alerta personalizado
advanced_monitoring.create_alert(
    alert_id="custom_alert",
    title="Custom Alert",
    description="Alert description",
    severity="warning",
    alert_type="custom",
    source="application"
)
```

## 📈 Performance e Otimizações

### Cache Performance
- **Hit Rate Esperado**: > 90% para dados frequentes
- **Latência**: < 1ms para cache em memória, < 5ms para Redis
- **Throughput**: > 10,000 ops/s para operações de cache

### Monitoramento Performance
- **Coleta de Métricas**: Cada 30 segundos
- **Retenção**: 30 dias no Prometheus
- **Dashboards**: Atualização em tempo real

### Alertas Performance
- **Latência de Detecção**: < 1 minuto para alertas críticos
- **Webhook Response**: < 100ms
- **Resolução Automática**: Suportada

## 🔍 Troubleshooting

### Problemas Comuns

1. **Redis não conecta**
   ```bash
   # Verificar se Redis está rodando
   docker ps | grep redis
   
   # Reiniciar Redis
   docker-compose -f docker-compose.monitoring.yml restart redis
   ```

2. **Grafana não carrega dashboards**
   ```bash
   # Verificar logs do Grafana
   docker logs techze-grafana
   
   # Reimportar dashboards
   python setup_monitoring_stack.py
   ```

3. **Alertas não funcionam**
   ```bash
   # Verificar configuração do Alertmanager
   curl http://localhost:9093/api/v1/status
   
   # Verificar webhook
   curl -X POST http://localhost:8000/api/v1/alerts/webhook \
        -H "Content-Type: application/json" \
        -d '{"alerts": []}'
   ```

### Logs Importantes

```bash
# Logs do serviço principal
tail -f logs/diagnostic_service.log

# Logs do Docker Compose
docker-compose -f docker-compose.monitoring.yml logs -f

# Logs específicos do Prometheus
docker logs techze-prometheus
```

## 🎯 Próximos Passos (Semana 3)

1. **Machine Learning**: Análise preditiva de falhas
2. **Automação**: Auto-healing e correções automáticas
3. **Integração**: APIs externas e webhooks
4. **Relatórios**: Geração automática de relatórios
5. **Mobile**: App mobile para monitoramento

---

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs do sistema
2. Executar `python test_week2_features.py`
3. Consultar documentação do Prometheus/Grafana
4. Verificar configurações de rede e firewall