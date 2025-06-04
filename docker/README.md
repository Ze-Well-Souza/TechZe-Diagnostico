# 🐳 TechZe-Diagnóstico - Docker Deployment

## 🚀 Quick Start

### 1. Configurar Environment Variables
```bash
# Copiar template
cp env.example .env

# Editar com suas configurações
nano .env
```

### 2. Build e Deploy
```bash
# Build da aplicação
docker-compose build

# Executar em produção
docker-compose up -d

# Verificar status
docker-compose ps
```

### 3. Acessar Aplicação
- **Frontend**: http://localhost
- **API**: http://localhost:8000
- **Grafana**: http://localhost:3000 (admin/password)
- **Prometheus**: http://localhost:9090

## 📋 Comandos Úteis

### Logs
```bash
# Logs da aplicação
docker-compose logs -f techze-app

# Logs de todos os serviços
docker-compose logs -f

# Logs do Redis
docker-compose logs -f redis
```

### Backup
```bash
# Backup automático está configurado
# Arquivos salvos em volume: backup_data

# Backup manual
docker-compose exec backup /backup.sh
```

### Manutenção
```bash
# Parar todos os serviços
docker-compose down

# Limpar volumes (CUIDADO!)
docker-compose down -v

# Rebuild completo
docker-compose build --no-cache
```

## 🔧 Troubleshooting

### Problemas Comuns

1. **Erro de permissão**:
```bash
sudo chown -R $(whoami):$(whoami) .
```

2. **Redis connection refused**:
```bash
docker-compose restart redis
```

3. **Logs da aplicação**:
```bash
docker-compose exec techze-app tail -f /app/logs/techze.log
```

## 🛡️ Segurança

- Usuário não-root no container
- Rate limiting configurado
- HTTPS ready (configure SSL)
- Secrets via environment variables
- Network isolation

## 📊 Monitoramento

- **Health checks** automáticos
- **Prometheus** métricas
- **Grafana** dashboards
- **Alertmanager** notificações

## 🔄 CI/CD

Para GitHub Actions, adicione secrets:
- `DOCKER_USERNAME`
- `DOCKER_PASSWORD` 
- Todas as variáveis do `.env` 