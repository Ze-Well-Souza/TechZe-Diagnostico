# TechZe Diagnóstico API Core - Dockerfile

# Usar imagem base Python otimizada
FROM python:3.11-slim as base

# Metadados
LABEL maintainer="TechZe Team"
LABEL version="1.0.0"
LABEL description="TechZe Diagnóstico API Core - Sistema consolidado de diagnóstico e monitoramento"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.6.1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libpq-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN groupadd -r techze && useradd -r -g techze techze

# Criar diretórios
RUN mkdir -p /app /app/logs /app/models /app/data && \
    chown -R techze:techze /app

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código da aplicação
COPY . .

# Ajustar permissões
RUN chown -R techze:techze /app

# Mudar para usuário não-root
USER techze

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão
CMD ["python", "main.py"]

# ================================
# Estágio de desenvolvimento
# ================================
FROM base as development

# Instalar dependências de desenvolvimento
RUN pip install \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    isort \
    flake8 \
    mypy \
    pre-commit

# Configurar git hooks (se necessário)
RUN git config --global --add safe.directory /app

# Comando para desenvolvimento (com reload)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ================================
# Estágio de produção
# ================================
FROM base as production

# Otimizações para produção
ENV ENVIRONMENT=production \
    DEBUG=false \
    WORKERS=4

# Remover arquivos desnecessários
RUN find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + || true

# Comando otimizado para produção
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

# ================================
# Estágio de testes
# ================================
FROM development as testing

# Copiar arquivos de teste
COPY tests/ ./tests/

# Instalar dependências de teste adicionais
RUN pip install \
    coverage \
    pytest-xdist \
    pytest-mock

# Comando para executar testes
CMD ["pytest", "tests/", "-v", "--cov=.", "--cov-report=html"]

# ================================
# Estágio de documentação
# ================================
FROM base as docs

# Instalar dependências de documentação
RUN pip install \
    mkdocs \
    mkdocs-material \
    mkdocs-swagger-ui-tag

# Copiar arquivos de documentação
COPY docs/ ./docs/
COPY mkdocs.yml .

# Comando para servir documentação
CMD ["mkdocs", "serve", "--dev-addr", "0.0.0.0:8000"]

# ================================
# Estágio de migração
# ================================
FROM base as migration

# Instalar ferramentas de migração
RUN pip install alembic

# Copiar scripts de migração
COPY migrations/ ./migrations/
COPY alembic.ini .

# Comando para executar migrações
CMD ["alembic", "upgrade", "head"]

# ================================
# Estágio de backup
# ================================
FROM base as backup

# Instalar ferramentas de backup
RUN apt-get update && apt-get install -y \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Copiar scripts de backup
COPY scripts/backup/ ./scripts/backup/

# Comando para executar backup
CMD ["python", "scripts/backup/backup.py"]

# ================================
# Estágio de monitoramento
# ================================
FROM base as monitoring

# Instalar ferramentas de monitoramento
RUN pip install \
    prometheus-client \
    grafana-api \
    elasticsearch

# Expor porta de métricas
EXPOSE 8001

# Comando para monitoramento
CMD ["python", "monitoring/metrics_server.py"]

# ================================
# Estágio de análise
# ================================
FROM base as analytics

# Instalar dependências de análise
RUN pip install \
    jupyter \
    pandas \
    numpy \
    matplotlib \
    seaborn \
    plotly

# Expor porta do Jupyter
EXPOSE 8888

# Comando para análise
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]

# ================================
# Estágio de machine learning
# ================================
FROM base as ml

# Instalar dependências de ML
RUN pip install \
    scikit-learn \
    tensorflow \
    torch \
    transformers \
    mlflow

# Criar diretório para modelos
RUN mkdir -p /app/ml_models && \
    chown -R techze:techze /app/ml_models

# Comando para treinamento de modelos
CMD ["python", "ml/train_models.py"]

# ================================
# Estágio de cache
# ================================
FROM redis:7-alpine as cache

# Copiar configuração do Redis
COPY config/redis.conf /usr/local/etc/redis/redis.conf

# Comando personalizado
CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]

# ================================
# Estágio de proxy
# ================================
FROM nginx:alpine as proxy

# Copiar configuração do Nginx
COPY config/nginx.conf /etc/nginx/nginx.conf
COPY config/default.conf /etc/nginx/conf.d/default.conf

# Expor portas
EXPOSE 80 443

# ================================
# Estágio final (padrão)
# ================================
FROM production as final

# Metadados finais
LABEL stage="production"
LABEL build_date="$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
LABEL git_commit="$(git rev-parse HEAD)"

# Verificações finais
RUN python -c "import main; print('✅ Aplicação carregada com sucesso')" && \
    python -c "from config import settings; print(f'✅ Configurações carregadas: {settings.app_name}')" && \
    echo "✅ Container pronto para produção"