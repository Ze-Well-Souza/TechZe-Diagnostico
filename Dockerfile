# TechZe-Diagnóstico - Dockerfile Multi-Stage para Produção
# ASSISTENTE IA - Containerização completa

# =============================================================================
# STAGE 1: Frontend Build (React/Vite)
# =============================================================================
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copia arquivos de dependências
COPY package*.json ./
COPY frontend-v3/package*.json ./frontend-v3/

# Instala dependências do frontend
RUN npm ci --only=production

# Copia código fonte do frontend
COPY frontend-v3/ ./frontend-v3/

# Build do frontend para produção
WORKDIR /app/frontend/frontend-v3
RUN npm run build

# =============================================================================
# STAGE 2: Python Dependencies
# =============================================================================
FROM python:3.11-slim AS python-deps

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root para segurança
RUN groupadd -r techze && useradd -r -g techze techze

# Configura diretório de trabalho
WORKDIR /app

# Instala poetry para gerenciamento de dependências
RUN pip install poetry==1.6.1

# Configura poetry
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copia arquivos de dependências Python
COPY microservices/diagnostic_service/pyproject.toml ./
COPY microservices/diagnostic_service/poetry.lock ./

# Instala dependências Python
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# =============================================================================
# STAGE 3: Production Runtime
# =============================================================================
FROM python:3.11-slim AS production

# Instala dependências mínimas do sistema
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Cria usuário não-root
RUN groupadd -r techze && useradd -r -g techze techze

# Configura diretórios
WORKDIR /app
RUN mkdir -p /app/static /app/logs /app/data \
    && chown -R techze:techze /app

# Copia ambiente virtual do Python
COPY --from=python-deps --chown=techze:techze /app/.venv /app/.venv

# Copia build do frontend
COPY --from=frontend-builder --chown=techze:techze /app/frontend/frontend-v3/dist /app/static

# Copia código fonte da aplicação
COPY --chown=techze:techze microservices/diagnostic_service/app /app/app
COPY --chown=techze:techze microservices/diagnostic_service/*.py /app/
COPY --chown=techze:techze *.sql /app/sql/
COPY --chown=techze:techze config.py /app/

# Configura variáveis de ambiente
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ENVIRONMENT=production \
    PORT=8000

# Configuração do Nginx
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Script de inicialização
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expõe portas
EXPOSE 8000 80

# Muda para usuário não-root
USER techze

# Comando de inicialização
ENTRYPOINT ["/entrypoint.sh"]
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 