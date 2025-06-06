# 🚀 Guia de Deploy - TechZe-Diagnostico

## 📋 Índice
1. [Deploy Local](#deploy-local)
2. [Deploy Docker](#deploy-docker)
3. [Deploy Render](#deploy-render)
4. [CI/CD GitHub Actions](#cicd-github-actions)
5. [Monitoramento](#monitoramento)

## 🏠 Deploy Local

### Pré-requisitos
- Python 3.12+
- Node.js 18+
- Redis (opcional)

### Passo a Passo

#### 1. Backend Setup
```bash
cd microservices/diagnostic_service
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

#### 2. Frontend Setup
```bash
cd ../../
npm install
npm run build
```

#### 3. Configuração
```env
# .env
ENVIRONMENT=development
DEBUG=true
SUPABASE_URL=your_url
SUPABASE_KEY=your_key
```

#### 4. Execução
```bash
# Backend
cd microservices/diagnostic_service
python -m app.main

# Frontend (novo terminal)
cd ../../
npm run dev
```

## 🐳 Deploy Docker

### Dockerfile Otimizado
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  backend:
    build: ./microservices/diagnostic_service
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

### Comandos Docker
```bash
# Build e execução
docker-compose up -d

# Logs
docker-compose logs -f

# Parar
docker-compose down
```

## ☁️ Deploy Render

### Configuração render.yaml
```yaml
services:
  - type: web
    name: techze-diagnostic-backend
    env: python
    buildCommand: "cd microservices/diagnostic_service && pip install -r requirements.txt"
    startCommand: "cd microservices/diagnostic_service && python -m app.main"
    plan: starter
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false

  - type: web
    name: techze-diagnostic-frontend
    env: node
    buildCommand: "npm install && npm run build"
    startCommand: "npm run preview"
    plan: starter
```

### Deploy Manual
1. Conecte repositório GitHub ao Render
2. Configure variáveis de ambiente
3. Deploy automático em cada push

### Variáveis de Ambiente Render
```
ENVIRONMENT=production
DEBUG=false
SUPABASE_URL=sua_url_supabase
SUPABASE_KEY=sua_chave_supabase
REDIS_URL=redis://internal_url:6379
SECRET_KEY=chave_secreta_producao
```

## ⚙️ CI/CD GitHub Actions

### Workflow Principal (.github/workflows/deploy.yml)
```yaml
name: Deploy TechZe-Diagnostico

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
          
      - name: Install Backend Dependencies
        run: |
          cd microservices/diagnostic_service
          pip install -r requirements.txt
          
      - name: Run Backend Tests
        run: |
          cd microservices/diagnostic_service
          python -m pytest tests/ -v
          
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install Frontend Dependencies
        run: npm install
        
      - name: Run Frontend Tests
        run: npm test
        
      - name: Build Frontend
        run: npm run build

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to Render
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK }}"
```

### Secrets Necessários
- `RENDER_DEPLOY_HOOK`: Hook de deploy do Render
- `SUPABASE_URL`: URL do Supabase
- `SUPABASE_KEY`: Chave do Supabase

## 📊 Monitoramento

### Health Checks
```bash
# Backend
curl https://seu-app.onrender.com/health

# Performance
curl https://seu-app.onrender.com/api/v3/performance/stats
```

### Métricas Prometheus
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'techze-backend'
    static_configs:
      - targets: ['seu-app.onrender.com:8000']
    metrics_path: '/metrics'
```

### Alertas Básicos
```yaml
# alerts.yml
groups:
  - name: techze.rules
    rules:
      - alert: HighResponseTime
        expr: http_request_duration_seconds > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
```

### Logs Centralizados
```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler('app.log', maxBytes=10485760, backupCount=5),
            logging.StreamHandler()
        ]
    )
```

## 🔧 Troubleshooting Deploy

### Problemas Comuns

#### Build Failure
```bash
# Verificar logs de build
curl -H "Authorization: Bearer $RENDER_TOKEN" \
     "https://api.render.com/v1/services/$SERVICE_ID/deploys"
```

#### Environment Variables
```bash
# Verificar variáveis
printenv | grep SUPABASE
```

#### Dependências
```bash
# Verificar requirements
pip freeze > requirements.txt
```

### Rollback
```bash
# Render rollback
curl -X POST \
  "https://api.render.com/v1/services/$SERVICE_ID/deploys/$DEPLOY_ID/rollback" \
  -H "Authorization: Bearer $RENDER_TOKEN"
```

---

*Atualizado em: 06/01/2025*