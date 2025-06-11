# TechZe Diagnostic Service - Guia de Desenvolvimento

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker & Docker Compose

### Configuração do Ambiente

#### 1. Clone do Repositório

```bash
git clone https://github.com/techze/diagnostic-service.git
cd TechZe-Diagnostico
```

#### 2. Configuração do Backend

```bash
cd microservices/diagnostic_service

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações
```

#### 3. Configuração do Frontend

```bash
cd ../../  # Voltar para raiz

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
# Editar .env.local com suas configurações
```

#### 4. Configuração do Banco de Dados

```bash
# Executar migrações
cd microservices/diagnostic_service
python -m alembic upgrade head

# Aplicar políticas RLS
psql $DATABASE_URL -f ../../supabase_setup_fixed.sql
```

### Executando o Projeto

#### Desenvolvimento Local

```bash
# Terminal 1 - Backend
cd microservices/diagnostic_service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd ../../
npm run dev

# Terminal 3 - Monitoramento (opcional)
docker-compose up prometheus grafana redis
```

#### Docker Compose

```bash
# Executar tudo com Docker
docker-compose up --build
```

## 🏗️ Estrutura do Projeto

### Backend (FastAPI)

```
microservices/diagnostic_service/
├── app/
│   ├── api/                    # Endpoints da API
│   │   ├── v1/                # API v1 (básica)
│   │   └── v3/                # API v3 (IA/ML)
│   ├── core/                  # Módulos centrais
│   │   ├── config.py          # Configurações
│   │   ├── database.py        # Conexão DB
│   │   ├── advanced_pool.py   # Pool avançado
│   │   ├── monitoring.py      # Monitoramento
│   │   └── security.py        # Segurança
│   ├── services/              # Lógica de negócio
│   │   ├── analyzers/         # Analisadores
│   │   ├── ai/                # Serviços de IA
│   │   └── diagnostic_service.py
│   ├── models/                # Modelos Pydantic
│   ├── schemas/               # Schemas de dados
│   └── utils/                 # Utilitários
├── tests/                     # Testes
├── requirements.txt           # Dependências
└── main.py                    # Ponto de entrada
```

### Frontend (React + TypeScript)

```
src/
├── components/                # Componentes React
│   ├── ui/                   # Componentes base
│   ├── dashboard/            # Dashboard
│   ├── layout/               # Layout
│   └── performance/          # Performance
├── pages/                    # Páginas
├── hooks/                    # Custom hooks
├── services/                 # Serviços API
├── contexts/                 # Contextos React
├── types/                    # Tipos TypeScript
└── utils/                    # Utilitários
```

## 🔧 Padrões de Desenvolvimento

### Backend (Python)

#### Estrutura de Endpoint

```python
from fastapi import APIRouter, Depends, HTTPException
from app.core.auth import get_current_user
from app.schemas.diagnostic import DiagnosticCreate, DiagnosticResponse
from app.services.diagnostic_service import DiagnosticService

router = APIRouter(prefix="/api/v1/diagnostics", tags=["diagnostics"])

@router.post("/", response_model=DiagnosticResponse)
async def create_diagnostic(
    diagnostic: DiagnosticCreate,
    current_user: User = Depends(get_current_user),
    service: DiagnosticService = Depends()
):
    """Criar novo diagnóstico"""
    try:
        result = await service.create(diagnostic, current_user.id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

#### Estrutura de Service

```python
from typing import List, Optional
from app.core.database import get_db
from app.models.diagnostic import Diagnostic
from app.schemas.diagnostic import DiagnosticCreate

class DiagnosticService:
    def __init__(self, db: Database = Depends(get_db)):
        self.db = db
    
    async def create(self, data: DiagnosticCreate, user_id: str) -> Diagnostic:
        """Criar diagnóstico"""
        query = """
            INSERT INTO diagnostics (user_id, type, data, created_at)
            VALUES ($1, $2, $3, NOW())
            RETURNING *
        """
        return await self.db.fetch_one(
            query, user_id, data.type, data.dict()
        )
    
    async def get_by_user(self, user_id: str) -> List[Diagnostic]:
        """Obter diagnósticos do usuário"""
        query = "SELECT * FROM diagnostics WHERE user_id = $1 ORDER BY created_at DESC"
        return await self.db.fetch_all(query, user_id)
```

#### Estrutura de Schema

```python
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any

class DiagnosticBase(BaseModel):
    type: str = Field(..., description="Tipo do diagnóstico")
    data: Dict[str, Any] = Field(..., description="Dados do diagnóstico")

class DiagnosticCreate(DiagnosticBase):
    pass

class DiagnosticResponse(DiagnosticBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
```

### Frontend (React + TypeScript)

#### Estrutura de Componente

```typescript
import React, { useState, useEffect } from 'react';
import { useDiagnostics } from '@/hooks/useDiagnostics';
import { Diagnostic } from '@/types/diagnostic';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface DiagnosticListProps {
  userId: string;
}

export const DiagnosticList: React.FC<DiagnosticListProps> = ({ userId }) => {
  const { diagnostics, loading, error, fetchDiagnostics } = useDiagnostics();
  
  useEffect(() => {
    fetchDiagnostics(userId);
  }, [userId]);
  
  if (loading) return <div>Carregando...</div>;
  if (error) return <div>Erro: {error}</div>;
  
  return (
    <div className="space-y-4">
      {diagnostics.map((diagnostic) => (
        <Card key={diagnostic.id}>
          <CardHeader>
            <CardTitle>{diagnostic.type}</CardTitle>
          </CardHeader>
          <CardContent>
            <p>Criado em: {new Date(diagnostic.created_at).toLocaleDateString()}</p>
            <Button onClick={() => viewDetails(diagnostic.id)}>
              Ver Detalhes
            </Button>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};
```

#### Custom Hook

```typescript
import { useState, useCallback } from 'react';
import { diagnosticApiService } from '@/services/diagnosticApiService';
import { Diagnostic } from '@/types/diagnostic';

export const useDiagnostics = () => {
  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const fetchDiagnostics = useCallback(async (userId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await diagnosticApiService.getByUser(userId);
      setDiagnostics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro desconhecido');
    } finally {
      setLoading(false);
    }
  }, []);
  
  const createDiagnostic = useCallback(async (data: DiagnosticCreate) => {
    try {
      const newDiagnostic = await diagnosticApiService.create(data);
      setDiagnostics(prev => [newDiagnostic, ...prev]);
      return newDiagnostic;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao criar diagnóstico');
      throw err;
    }
  }, []);
  
  return {
    diagnostics,
    loading,
    error,
    fetchDiagnostics,
    createDiagnostic
  };
};
```

## 🧪 Testes

### Backend (Pytest)

#### Teste de Endpoint

```python
import pytest
from httpx import AsyncClient
from app.main import app
from app.core.auth import create_access_token

@pytest.mark.asyncio
async def test_create_diagnostic():
    # Arrange
    token = create_access_token({"sub": "user-123"})
    headers = {"Authorization": f"Bearer {token}"}
    
    diagnostic_data = {
        "type": "hardware",
        "data": {"cpu_usage": 75, "memory_usage": 60}
    }
    
    # Act
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/diagnostics/",
            json=diagnostic_data,
            headers=headers
        )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "hardware"
    assert "id" in data
```

#### Teste de Service

```python
import pytest
from unittest.mock import AsyncMock
from app.services.diagnostic_service import DiagnosticService
from app.schemas.diagnostic import DiagnosticCreate

@pytest.mark.asyncio
async def test_diagnostic_service_create():
    # Arrange
    mock_db = AsyncMock()
    mock_db.fetch_one.return_value = {
        "id": "diag-123",
        "user_id": "user-123",
        "type": "hardware",
        "data": {"cpu_usage": 75}
    }
    
    service = DiagnosticService(db=mock_db)
    diagnostic_data = DiagnosticCreate(
        type="hardware",
        data={"cpu_usage": 75}
    )
    
    # Act
    result = await service.create(diagnostic_data, "user-123")
    
    # Assert
    assert result["id"] == "diag-123"
    assert result["type"] == "hardware"
    mock_db.fetch_one.assert_called_once()
```

### Frontend (Jest + React Testing Library)

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DiagnosticList } from '@/components/DiagnosticList';
import { diagnosticApiService } from '@/services/diagnosticApiService';

// Mock do serviço
jest.mock('@/services/diagnosticApiService');
const mockDiagnosticService = diagnosticApiService as jest.Mocked<typeof diagnosticApiService>;

describe('DiagnosticList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('should render diagnostics list', async () => {
    // Arrange
    const mockDiagnostics = [
      {
        id: '1',
        type: 'hardware',
        created_at: '2025-06-06T10:00:00Z',
        data: {}
      }
    ];
    
    mockDiagnosticService.getByUser.mockResolvedValue(mockDiagnostics);
    
    // Act
    render(<DiagnosticList userId="user-123" />);
    
    // Assert
    await waitFor(() => {
      expect(screen.getByText('hardware')).toBeInTheDocument();
    });
    
    expect(mockDiagnosticService.getByUser).toHaveBeenCalledWith('user-123');
  });
  
  it('should handle error state', async () => {
    // Arrange
    mockDiagnosticService.getByUser.mockRejectedValue(new Error('API Error'));
    
    // Act
    render(<DiagnosticList userId="user-123" />);
    
    // Assert
    await waitFor(() => {
      expect(screen.getByText(/Erro: API Error/)).toBeInTheDocument();
    });
  });
});
```

## 📊 Monitoramento e Debugging

### Logs Estruturados

```python
import structlog
from app.core.config import settings

# Configuração do structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Uso nos endpoints
@router.post("/diagnostics/")
async def create_diagnostic(diagnostic: DiagnosticCreate):
    logger.info(
        "Creating diagnostic",
        diagnostic_type=diagnostic.type,
        user_id=current_user.id,
        request_id=request.headers.get("X-Request-ID")
    )
    
    try:
        result = await service.create(diagnostic)
        logger.info(
            "Diagnostic created successfully",
            diagnostic_id=result.id,
            duration_ms=timer.elapsed()
        )
        return result
    except Exception as e:
        logger.error(
            "Failed to create diagnostic",
            error=str(e),
            error_type=type(e).__name__
        )
        raise
```

### Métricas Customizadas

```python
from prometheus_client import Counter, Histogram, Gauge

# Métricas de negócio
diagnostics_created_total = Counter(
    'diagnostics_created_total',
    'Total de diagnósticos criados',
    ['type', 'user_type']
)

diagnostic_processing_duration = Histogram(
    'diagnostic_processing_duration_seconds',
    'Tempo de processamento de diagnósticos',
    ['type']
)

active_users = Gauge(
    'active_users',
    'Usuários ativos no sistema'
)

# Uso nos serviços
class DiagnosticService:
    async def create(self, data: DiagnosticCreate, user_id: str):
        with diagnostic_processing_duration.labels(type=data.type).time():
            result = await self._create_diagnostic(data, user_id)
            
        diagnostics_created_total.labels(
            type=data.type,
            user_type=await self._get_user_type(user_id)
        ).inc()
        
        return result
```

## 🔒 Segurança

### Autenticação JWT

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user(user_id)
    if user is None:
        raise credentials_exception
    return user
```

### Validação de Input

```python
from pydantic import BaseModel, validator, Field
from typing import Optional
import re

class DiagnosticCreate(BaseModel):
    type: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    data: dict = Field(...)
    
    @validator('type')
    def validate_type(cls, v):
        allowed_types = ['hardware', 'software', 'network', 'performance']
        if v not in allowed_types:
            raise ValueError(f'Type must be one of: {allowed_types}')
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9\s\-_.,!?]+$', v):
            raise ValueError('Description contains invalid characters')
        return v
    
    @validator('data')
    def validate_data(cls, v):
        # Limitar tamanho do JSON
        import json
        if len(json.dumps(v)) > 10000:  # 10KB
            raise ValueError('Data payload too large')
        return v
```

## 🚀 Deploy

### Dockerfile Otimizado

```dockerfile
# Multi-stage build
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage final
FROM python:3.11-slim

WORKDIR /app

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash app

# Copiar dependências do builder
COPY --from=builder /root/.local /home/app/.local

# Copiar código da aplicação
COPY --chown=app:app . .

# Configurar PATH
ENV PATH=/home/app/.local/bin:$PATH

# Mudar para usuário não-root
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose para Desenvolvimento

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/techze_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./app:/app/app:ro
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=techze_db
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
  
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
  
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  postgres_data:
  grafana_data:
```

## 📝 Convenções de Código

### Python (Backend)

- **PEP 8**: Seguir padrões de estilo Python
- **Type Hints**: Usar anotações de tipo
- **Docstrings**: Documentar funções e classes
- **Black**: Formatação automática
- **isort**: Organização de imports

### TypeScript (Frontend)

- **ESLint**: Linting de código
- **Prettier**: Formatação automática
- **Naming**: camelCase para variáveis, PascalCase para componentes
- **Interfaces**: Definir tipos explícitos

### Git

- **Conventional Commits**: Formato padronizado de commits
- **Branch Naming**: feature/*, bugfix/*, hotfix/*
- **Pull Requests**: Obrigatórios para main/develop

```bash
# Exemplos de commits
git commit -m "feat: add connection pooling metrics endpoint"
git commit -m "fix: resolve memory leak in diagnostic service"
git commit -m "docs: update API documentation"
git commit -m "test: add unit tests for auth service"
```

---

## 📚 Recursos Adicionais

- [Documentação Técnica](./TECHNICAL_DOCUMENTATION.md)
- [API Reference](./API_REFERENCE.md)
- [Guia de Deploy](./DEPLOYMENT_GUIDE.md)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Versão**: 3.0.0  
**Última Atualização**: 2025-06-06  
**Autor**: TechZe Development Team