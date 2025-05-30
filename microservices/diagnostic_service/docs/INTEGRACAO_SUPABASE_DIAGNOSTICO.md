# Guia de Integração do Supabase com o Microserviço de Diagnóstico

## Visão Geral

Este documento detalha como implementar a integração do Supabase com o microserviço de diagnóstico do TechCare. O Supabase será utilizado como banco de dados e serviço de autenticação para o microserviço.

## Por que Supabase?

O Supabase é uma excelente escolha para este projeto pelos seguintes motivos:

- **API RESTful automática**: Gera endpoints REST para todas as tabelas
- **Autenticação integrada**: Facilita a implementação de autenticação JWT
- **PostgreSQL**: Banco de dados robusto e escalável
- **Tempo real**: Permite atualizações em tempo real para monitoramento
- **Armazenamento de objetos**: Útil para armazenar relatórios de diagnóstico

## Configuração do Projeto no Supabase

### 1. Criar um Novo Projeto

1. Acesse [https://app.supabase.io/](https://app.supabase.io/)
2. Clique em "New Project"
3. Preencha os detalhes do projeto:
   - Nome: `techcare-diagnostic-service`
   - Senha do banco de dados: (crie uma senha forte)
   - Região: (escolha a mais próxima do seu público-alvo)
4. Clique em "Create Project"

### 2. Configurar Tabelas

Acesse o SQL Editor e execute os seguintes comandos para criar as tabelas necessárias:

```sql
-- Tabela de diagnósticos
CREATE TABLE diagnostics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    device_id UUID NOT NULL,
    status TEXT NOT NULL,
    cpu_status TEXT,
    cpu_metrics JSONB,
    memory_status TEXT,
    memory_metrics JSONB,
    disk_status TEXT,
    disk_metrics JSONB,
    network_status TEXT,
    network_metrics JSONB,
    health_score FLOAT,
    raw_data JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de dispositivos
CREATE TABLE devices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    os TEXT,
    os_version TEXT,
    processor TEXT,
    ram TEXT,
    storage TEXT,
    last_diagnostic_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de relatórios
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    diagnostic_id UUID NOT NULL REFERENCES diagnostics(id),
    title TEXT NOT NULL,
    content JSONB NOT NULL,
    format TEXT NOT NULL,
    file_path TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. Configurar Políticas de Segurança (RLS)

Acesse o SQL Editor e execute os seguintes comandos para configurar as políticas de segurança:

```sql
-- Habilitar RLS para todas as tabelas
ALTER TABLE diagnostics ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

-- Políticas para diagnósticos
CREATE POLICY "Usuários podem ver seus próprios diagnósticos" 
    ON diagnostics FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Usuários podem criar diagnósticos" 
    ON diagnostics FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários podem atualizar seus próprios diagnósticos" 
    ON diagnostics FOR UPDATE 
    USING (auth.uid() = user_id);

-- Políticas para dispositivos
CREATE POLICY "Usuários podem ver seus próprios dispositivos" 
    ON devices FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Usuários podem criar dispositivos" 
    ON devices FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários podem atualizar seus próprios dispositivos" 
    ON devices FOR UPDATE 
    USING (auth.uid() = user_id);

-- Políticas para relatórios
CREATE POLICY "Usuários podem ver seus próprios relatórios" 
    ON reports FOR SELECT 
    USING (EXISTS (
        SELECT 1 FROM diagnostics 
        WHERE diagnostics.id = reports.diagnostic_id 
        AND diagnostics.user_id = auth.uid()
    ));

CREATE POLICY "Usuários podem criar relatórios para seus diagnósticos" 
    ON reports FOR INSERT 
    WITH CHECK (EXISTS (
        SELECT 1 FROM diagnostics 
        WHERE diagnostics.id = reports.diagnostic_id 
        AND diagnostics.user_id = auth.uid()
    ));
```

## Integração com FastAPI

### 1. Configurar Dependências

Adicione as seguintes dependências ao arquivo `requirements.txt`:

```
supabase>=1.0.3
python-jose>=3.3.0
python-dotenv>=1.0.0
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

### 2. Configurar Cliente Supabase

Crie um arquivo `app/core/supabase.py` com o seguinte conteúdo:

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

### 3. Configurar Autenticação

Crie um arquivo `app/core/auth.py` com o seguinte conteúdo:

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from app.core.config import settings
from app.core.supabase import get_supabase_client

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

### 4. Implementar Serviço de Diagnóstico

Atualize o arquivo `app/services/diagnostic_service.py` para usar o Supabase:

```python
from uuid import UUID
from app.core.supabase import get_supabase_client
from app.schemas.diagnostic import DiagnosticCreate, DiagnosticUpdate

class DiagnosticService:
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def create_diagnostic(self, diagnostic: DiagnosticCreate, user_id: UUID):
        data = diagnostic.dict()
        data["user_id"] = str(user_id)
        
        result = self.supabase.table("diagnostics").insert(data).execute()
        return result.data[0] if result.data else None
    
    async def get_diagnostic(self, diagnostic_id: UUID, user_id: UUID):
        result = self.supabase.table("diagnostics") \
            .select("*") \
            .eq("id", str(diagnostic_id)) \
            .eq("user_id", str(user_id)) \
            .execute()
        return result.data[0] if result.data else None
    
    async def get_user_diagnostics(self, user_id: UUID):
        result = self.supabase.table("diagnostics") \
            .select("*") \
            .eq("user_id", str(user_id)) \
            .order("created_at", desc=True) \
            .execute()
        return result.data
    
    async def update_diagnostic(self, diagnostic_id: UUID, diagnostic: DiagnosticUpdate, user_id: UUID):
        data = diagnostic.dict(exclude_unset=True)
        
        result = self.supabase.table("diagnostics") \
            .update(data) \
            .eq("id", str(diagnostic_id)) \
            .eq("user_id", str(user_id)) \
            .execute()
        return result.data[0] if result.data else None
```

### 5. Implementar API Endpoints

Crie um arquivo `app/api/endpoints/diagnostics.py` com o seguinte conteúdo:

```python
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_user
from app.schemas.diagnostic import DiagnosticCreate, DiagnosticUpdate, DiagnosticInDB
from app.services.diagnostic_service import DiagnosticService

router = APIRouter()
diagnostic_service = DiagnosticService()

@router.post("/", response_model=DiagnosticInDB, status_code=status.HTTP_201_CREATED)
async def create_diagnostic(
    diagnostic: DiagnosticCreate,
    user_id: UUID = Depends(get_current_user)
):
    result = await diagnostic_service.create_diagnostic(diagnostic, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create diagnostic"
        )
    return result

@router.get("/{diagnostic_id}", response_model=DiagnosticInDB)
async def get_diagnostic(
    diagnostic_id: UUID,
    user_id: UUID = Depends(get_current_user)
):
    result = await diagnostic_service.get_diagnostic(diagnostic_id, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic not found"
        )
    return result

@router.get("/", response_model=List[DiagnosticInDB])
async def get_user_diagnostics(
    user_id: UUID = Depends(get_current_user)
):
    return await diagnostic_service.get_user_diagnostics(user_id)

@router.patch("/{diagnostic_id}", response_model=DiagnosticInDB)
async def update_diagnostic(
    diagnostic_id: UUID,
    diagnostic: DiagnosticUpdate,
    user_id: UUID = Depends(get_current_user)
):
    result = await diagnostic_service.update_diagnostic(diagnostic_id, diagnostic, user_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic not found or update failed"
        )
    return result
```

## Configuração de Ambiente

### 1. Arquivo .env

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
```

### 2. Configuração do FastAPI

Atualize o arquivo `app/core/config.py` para carregar as variáveis de ambiente:

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
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    
    class Config:
        case_sensitive = True

settings = Settings()
```

## Dockerfile

Crie um arquivo `Dockerfile` na raiz do projeto com o seguinte conteúdo:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Próximos Passos

1. Implementar os analisadores (CPU, memória, disco, rede)
2. Implementar o serviço de relatórios
3. Implementar testes unitários e de integração
4. Configurar CI/CD para deploy automático
5. Documentar a API com Swagger/OpenAPI

## Conclusão

A integração do Supabase com o microserviço de diagnóstico fornece uma solução robusta e escalável para armazenamento de dados e autenticação. Seguindo este guia, você terá uma base sólida para desenvolver o microserviço completo.