# Microserviço de Diagnóstico - TecnoReparo

## Visão Geral

O Microserviço de Diagnóstico é responsável por realizar diagnósticos completos de hardware e software em sistemas computacionais. Este serviço é parte da arquitetura de microserviços do sistema TecnoReparo, desenvolvido para a UlyTech.

## Funcionalidades

- Diagnóstico completo de hardware
- Diagnóstico de software e sistema operacional
- Análise de desempenho de componentes (CPU, memória, disco, rede)
- Detecção automática de problemas
- Análise preditiva para prevenção de falhas
- Geração de relatórios detalhados em PDF
- Cálculo de score de saúde do sistema

## Arquitetura

### Tecnologias Utilizadas

- **Framework**: FastAPI
- **Banco de Dados**: PostgreSQL
- **ORM**: SQLAlchemy
- **Autenticação**: JWT
- **Documentação**: Swagger/OpenAPI
- **Containerização**: Docker
- **Orquestração**: Kubernetes

### Componentes Principais

- **API RESTful**: Interface para comunicação com outros serviços
- **Analisadores Especializados**:
  - CPUAnalyzer: Análise de desempenho da CPU
  - MemoryAnalyzer: Análise de memória RAM
  - DiskAnalyzer: Análise de discos e armazenamento
  - NetworkAnalyzer: Análise de conectividade de rede
- **Gerador de Relatórios**: Criação de relatórios detalhados em PDF
- **Motor de Análise Preditiva**: Previsão de falhas baseada em padrões históricos

## Estrutura do Projeto

```
diagnostic_service/
├── app/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── diagnostics.py
│   │   │   ├── reports.py
│   │   │   └── health.py
│   │   └── router.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── session.py
│   │   └── init_db.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── diagnostic.py
│   │   ├── report.py
│   │   └── system_info.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── diagnostic.py
│   │   ├── report.py
│   │   └── system_info.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── diagnostic_service.py
│   │   ├── analyzers/
│   │   │   ├── __init__.py
│   │   │   ├── cpu_analyzer.py
│   │   │   ├── memory_analyzer.py
│   │   │   ├── disk_analyzer.py
│   │   │   └── network_analyzer.py
│   │   ├── report_service.py
│   │   └── predictive_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── pdf_generator.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   │   ├── __init__.py
│   │   ├── test_diagnostics.py
│   │   ├── test_reports.py
│   │   └── test_health.py
│   ├── test_services/
│   │   ├── __init__.py
│   │   ├── test_diagnostic_service.py
│   │   ├── test_analyzers/
│   │   │   ├── __init__.py
│   │   │   ├── test_cpu_analyzer.py
│   │   │   ├── test_memory_analyzer.py
│   │   │   ├── test_disk_analyzer.py
│   │   │   └── test_network_analyzer.py
│   │   ├── test_report_service.py
│   │   └── test_predictive_service.py
│   └── test_utils/
│       ├── __init__.py
│       └── test_pdf_generator.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── kubernetes/
│   ├── deployment.yaml
│   ├── service.yaml
│   └── configmap.yaml
├── pyproject.toml
├── poetry.lock
├── README.md
└── requirements.txt
```

## Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Conta no Supabase (https://supabase.com)
- Docker (opcional)
- Kubernetes (para produção)

### Configuração do Supabase

1. **Crie um projeto no Supabase:**
   - Acesse https://supabase.com e crie uma nova conta
   - Crie um novo projeto
   - Anote a URL do projeto e a chave anônima (anon key)

2. **Configure as tabelas no Supabase:**
   - Acesse o SQL Editor no painel do Supabase
   - Execute os scripts SQL disponíveis em `docs/INTEGRACAO_SUPABASE_DIAGNOSTICO.md`
   - Desabilite a confirmação de email em Authentication > Settings

### Instalação Local

```bash
# Clone o repositório
git clone https://github.com/Ze-Well-Souza/TechZe-Diagnostico.git
cd TechZe-Diagnostico/microservices/diagnostic_service

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações do Supabase

# Inicie o servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Variáveis de Ambiente Obrigatórias

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here
SECRET_KEY=your-secret-key-here
```

### Execução com Docker

```bash
docker-compose up -d
```

## Testes

### Executando Testes

```bash
pytest
```

### Cobertura de Testes

```bash
pytest --cov=app tests/
```

## API Documentation

Após iniciar o servidor, acesse a documentação da API em:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Segurança

- Autenticação JWT para todas as rotas (exceto health check)
- Validação de entrada em todas as rotas
- Sanitização de dados
- HTTPS em produção
- Rate limiting
- CORS configurado

## Integração Contínua

- GitHub Actions para execução automática de testes
- SonarQube para análise de qualidade de código
- Dependabot para atualização de dependências

## Próximos Passos

- [ ] Implementar análise preditiva avançada com machine learning
- [ ] Adicionar suporte para diagnóstico remoto
- [ ] Integrar com serviços de monitoramento
- [ ] Implementar cache distribuído para resultados de diagnóstico
- [ ] Adicionar suporte para exportação de relatórios em múltiplos formatos