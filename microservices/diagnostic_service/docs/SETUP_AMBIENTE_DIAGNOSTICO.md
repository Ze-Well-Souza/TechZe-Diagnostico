# Configuração do Ambiente de Desenvolvimento para o Microserviço de Diagnóstico

## Visão Geral

Este documento fornece instruções detalhadas para configurar o ambiente de desenvolvimento para o microserviço de diagnóstico do TechCare. Siga estas etapas para preparar seu ambiente e começar a implementação.

## Pré-requisitos

- Python 3.10 ou superior
- pip (gerenciador de pacotes Python)
- Git
- Conta no Supabase (para banco de dados)
- Editor de código (VS Code, PyCharm, etc.)

## 1. Configuração do Ambiente Virtual

### Windows

```powershell
# Navegue até o diretório do projeto
cd c:\Projetos_python\projet_tech_v2\microservices\diagnostic_service

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
.\venv\Scripts\activate
```

### Linux/macOS

```bash
# Navegue até o diretório do projeto
cd /caminho/para/projet_tech_v2/microservices/diagnostic_service

# Crie um ambiente virtual
python -m venv venv

# Ative o ambiente virtual
source venv/bin/activate
```

## 2. Instalação das Dependências

### Criar arquivo requirements.txt

Crie um arquivo `requirements.txt` na raiz do diretório do microserviço com o seguinte conteúdo:

```
fastapi>=0.95.0
uvicorn>=0.21.1
pydantic>=1.10.7
supabase>=1.0.3
psutil>=5.9.5
py-cpuinfo>=9.0.0
python-dotenv>=1.0.0
python-jose>=3.3.0
passlib>=1.7.4
python-multipart>=0.0.6
requests>=2.28.2
pywin32>=306; platform_system=="Windows"
pytest>=7.3.1
pytest-cov>=4.1.0
black>=23.3.0
isort>=5.12.0
flake8>=6.0.0
```

### Instalar dependências

```bash
pip install -r requirements.txt
```

## 3. Configuração do Supabase

### 3.1 Criar Conta e Projeto no Supabase

1. Acesse [https://supabase.com](https://supabase.com) e crie uma conta ou faça login
2. Crie um novo projeto:
   - Nome: `techcare-diagnostic-service`
   - Senha do banco de dados: (crie uma senha forte)
   - Região: (escolha a mais próxima do seu público-alvo)
3. Aguarde a criação do projeto (pode levar alguns minutos)

### 3.2 Obter Credenciais do Supabase

1. No dashboard do projeto, clique em "Settings" (Configurações) no menu lateral
2. Clique em "API"
3. Copie a "URL" e a "anon key" (chave pública)
4. Copie também a "service_role key" (chave secreta) para uso em desenvolvimento

### 3.3 Configurar Banco de Dados

1. No dashboard do projeto, clique em "SQL Editor" (Editor SQL)
2. Crie um novo script SQL
3. Cole o script SQL do arquivo `INTEGRACAO_SUPABASE_DIAGNOSTICO.md` para criar as tabelas e políticas de segurança
4. Execute o script

## 4. Configuração do Ambiente Local

### 4.1 Arquivo .env

Crie um arquivo `.env` na raiz do diretório do microserviço com o seguinte conteúdo:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
ENVIRONMENT=development
DEBUG=True
```

Substitua os valores pelos obtidos no passo 3.2.

### 4.2 Arquivo .env.example

Crie um arquivo `.env.example` na raiz do diretório do microserviço com o seguinte conteúdo:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_SERVICE_KEY=your-supabase-service-role-key
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
ENVIRONMENT=development
DEBUG=True
```

### 4.3 Arquivo .gitignore

Crie ou atualize o arquivo `.gitignore` na raiz do diretório do microserviço com o seguinte conteúdo:

```
# Ambiente virtual
venv/
env/
.env

# Arquivos Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Arquivos de teste
.coverage
htmlcov/
.pytest_cache/

# Arquivos de IDE
.idea/
.vscode/
*.swp
*.swo

# Arquivos de sistema
.DS_Store
Thumbs.db
```

## 5. Estrutura Inicial do Projeto

### 5.1 Criar Diretórios

Crie a seguinte estrutura de diretórios no diretório do microserviço:

```bash
mkdir -p app/core
mkdir -p app/api/endpoints
mkdir -p app/models
mkdir -p app/schemas
mkdir -p app/services
mkdir -p app/services/analyzers
mkdir -p app/utils
mkdir -p tests/test_api
mkdir -p tests/test_services
mkdir -p tests/test_analyzers
```

### 5.2 Criar Arquivos Iniciais

Crie os seguintes arquivos iniciais:

#### app/\_\_init\_\_.py

```python
# Arquivo vazio para marcar o diretório como um pacote Python
```

#### app/main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Microserviço de Diagnóstico para o TechCare",
    version="0.1.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique as origens permitidas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
# from app.api.api import api_router
# app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Bem-vindo ao Microserviço de Diagnóstico do TechCare"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

#### app/core/\_\_init\_\_.py

```python
# Arquivo vazio para marcar o diretório como um pacote Python
```

#### app/core/config.py

```python
import os
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Diagnostic Service"
    API_V1_STR: str = "/api/v1"
    
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    class Config:
        case_sensitive = True

settings = Settings()
```

#### app/core/supabase.py

```python
from supabase import create_client
from app.core.config import settings

supabase_client = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)

def get_supabase_client():
    return supabase_client
```

## 6. Dockerfile

Crie um arquivo `Dockerfile` na raiz do diretório do microserviço com o seguinte conteúdo:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 7. docker-compose.yml

Crie um arquivo `docker-compose.yml` na raiz do diretório do microserviço com o seguinte conteúdo:

```yaml
version: '3'

services:
  diagnostic-service:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    env_file:
      - .env
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 8. Executando o Projeto

### 8.1 Executar Localmente

```bash
# Ative o ambiente virtual (se ainda não estiver ativado)
# Windows: .\venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# Execute o servidor de desenvolvimento
uvicorn app.main:app --reload
```

### 8.2 Executar com Docker

```bash
# Construir a imagem
docker-compose build

# Executar o contêiner
docker-compose up
```

## 9. Verificação

Após iniciar o servidor, acesse http://localhost:8000 no seu navegador. Você deverá ver a mensagem de boas-vindas.

Acesse http://localhost:8000/docs para ver a documentação da API gerada automaticamente pelo Swagger.

## 10. Solução de Problemas

### 10.1 Problemas de Conexão com o Supabase

Se você encontrar problemas de conexão com o Supabase, verifique:

1. Se as credenciais no arquivo `.env` estão corretas
2. Se o projeto no Supabase está ativo
3. Se as tabelas foram criadas corretamente

### 10.2 Problemas com Dependências

Se você encontrar problemas com dependências, tente:

```bash
pip install --upgrade -r requirements.txt
```

### 10.3 Problemas com o Docker

Se você encontrar problemas com o Docker, tente:

```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## Conclusão

Seguindo estas instruções, você terá configurado com sucesso o ambiente de desenvolvimento para o microserviço de diagnóstico do TechCare. Agora você está pronto para começar a implementação do serviço conforme o plano de desenvolvimento.