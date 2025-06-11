# 🛠️ Scripts do TechZe Diagnóstico

Este diretório contém scripts utilitários para desenvolvimento, teste e manutenção do projeto TechZe Diagnóstico.

## 📋 Scripts Disponíveis

### 🗄️ `init_database.py`
**Inicialização do Banco de Dados**

Configura o banco de dados Supabase com todas as tabelas, índices e dados iniciais necessários.

```bash
# Executar inicialização do banco
cd microservices/diagnostic_service
python scripts/init_database.py
```

**Funcionalidades:**
- ✅ Cria todas as tabelas principais (orçamentos, estoque, OS, etc.)
- ✅ Aplica índices para performance
- ✅ Cria triggers para auditoria
- ✅ Insere dados iniciais de teste
- ✅ Verifica integridade das tabelas

**Pré-requisitos:**
- Variáveis de ambiente configuradas:
  - `SUPABASE_URL`: URL do projeto Supabase
  - `SUPABASE_KEY`: Chave de API do Supabase

### 🧪 `run_tests.py`
**Execução de Testes**

Script completo para executar todos os tipos de teste do projeto.

```bash
# Testes unitários básicos
python scripts/run_tests.py

# Testes com cobertura de código
python scripts/run_tests.py --coverage

# Testes de integração
python scripts/run_tests.py --integration

# Verificações de qualidade de código
python scripts/run_tests.py --lint

# Verificações de segurança
python scripts/run_tests.py --security

# Executar todos os tipos de teste
python scripts/run_tests.py --all

# Instalar dependências de teste
python scripts/run_tests.py --install-deps
```

**Funcionalidades:**
- ✅ Testes unitários com pytest
- ✅ Testes de integração marcados
- ✅ Relatórios de cobertura de código
- ✅ Verificações de linting (flake8, black, isort)
- ✅ Verificações de segurança (safety, bandit)
- ✅ Instalação automática de dependências

**Tipos de Teste:**

#### 🔧 Testes Unitários
- Testam funcionalidades isoladas
- Usam mocks para dependências externas
- Execução rápida (< 30 segundos)

#### 🔗 Testes de Integração
- Testam integração com Supabase
- Requerem configuração de banco
- Marcados com `@pytest.mark.integration`

#### 📊 Cobertura de Código
- Relatório HTML em `htmlcov/index.html`
- Meta: > 90% de cobertura
- Relatório XML para CI/CD

## 🚀 Fluxo de Desenvolvimento

### 1. Configuração Inicial
```bash
# 1. Configurar variáveis de ambiente
export SUPABASE_URL="your-supabase-url"
export SUPABASE_KEY="your-supabase-key"

# 2. Inicializar banco de dados
python scripts/init_database.py

# 3. Instalar dependências de teste
python scripts/run_tests.py --install-deps
```

### 2. Desenvolvimento Diário
```bash
# Executar testes durante desenvolvimento
python scripts/run_tests.py --coverage

# Verificar qualidade do código
python scripts/run_tests.py --lint

# Testes completos antes de commit
python scripts/run_tests.py --all
```

### 3. Deploy/Produção
```bash
# Verificações de segurança
python scripts/run_tests.py --security

# Testes de integração completos
python scripts/run_tests.py --integration

# Aplicar migrações em produção
python scripts/init_database.py
```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Banco de Dados
DATABASE_URL=postgresql://user:pass@host:port/db

# Desenvolvimento
DEBUG=true
LOG_LEVEL=DEBUG
ENVIRONMENT=development
```

### Dependências de Desenvolvimento

```bash
pip install pytest pytest-asyncio pytest-cov pytest-mock
pip install flake8 black isort
pip install safety bandit
```

## 📊 Métricas e Qualidade

### Cobertura de Código
- **Meta:** > 90%
- **Atual:** Em desenvolvimento
- **Relatório:** `htmlcov/index.html`

### Qualidade de Código
- **Linting:** flake8 (PEP 8)
- **Formatação:** black
- **Imports:** isort

### Segurança
- **Vulnerabilidades:** safety
- **Análise estática:** bandit

## 🐛 Resolução de Problemas

### Erro de Conexão com Supabase
```bash
# Verificar configurações
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Testar conexão
python -c "from app.core.supabase import get_supabase_client; print('✅ Conexão OK')"
```

### Testes Falhando
```bash
# Executar teste específico
python -m pytest tests/services/test_orcamento_service.py -v

# Debug com logs
python -m pytest tests/ -v -s --log-cli-level=DEBUG
```

### Problemas de Dependências
```bash
# Reinstalar dependências
pip install -r requirements.txt

# Atualizar dependências de teste
python scripts/run_tests.py --install-deps
```

## 📚 Recursos Adicionais

- **Documentação Supabase:** https://supabase.com/docs
- **Pytest Docs:** https://pytest.org
- **FastAPI Testing:** https://fastapi.tiangolo.com/tutorial/testing/

## 🤝 Contribuição

1. Execute os testes antes de fazer commit
2. Mantenha cobertura > 90%
3. Siga as convenções de código (black, flake8)
4. Adicione testes para novas funcionalidades 