# Plano de Consolidação de Configurações

## Problema Identificado

Existem 3 arquivos de configuração diferentes causando conflitos de importação:

1. **`c:\Projetos_python\TechZe-Diagnostico\config.py`** (Raiz do projeto)
   - Configuração global do projeto TechZe
   - Define SupabaseConfig, ProjectConfig e tabelas do banco
   - Usado principalmente para setup inicial e scripts de deploy

2. **`microservices\diagnostic_service\app\core\config.py`**
   - Configuração do microserviço de diagnóstico
   - Classe Settings com Pydantic BaseSettings
   - Usado pela maioria dos módulos da aplicação

3. **`microservices\diagnostic_service\app\api\core\config.py`**
   - Configuração específica da API Core consolidada
   - Configurações mais detalhadas e modulares
   - Usado pelos endpoints da API Core

## Conflitos Identificados

### 1. Imports Conflitantes
- `app\api\core\main.py` importa `from config import settings`
- Outros módulos importam `from app.core.config import settings`
- Isso causa ambiguidade sobre qual config usar

### 2. Configurações Duplicadas
- Supabase configurado em todos os 3 arquivos
- Configurações de banco de dados duplicadas
- Configurações de segurança espalhadas

### 3. Estruturas Diferentes
- config.py (raiz): Usa dataclasses
- app/core/config.py: Usa Pydantic BaseSettings
- app/api/core/config.py: Usa Pydantic com múltiplas classes

## Plano de Correção

### Fase 1: Consolidação Hierárquica

1. **Manter config.py (raiz)** para configurações globais do projeto
2. **Consolidar app/core/config.py** como configuração principal do microserviço
3. **Migrar app/api/core/config.py** para usar a configuração consolidada

### Fase 2: Estrutura Proposta

```
config.py (raiz)                    # Configurações globais do projeto
└── microservices/
    └── diagnostic_service/
        └── app/
            └── core/
                ├── config.py       # Configuração principal consolidada
                └── api/
                    └── core/
                        └── config.py   # Configurações específicas da API Core (herda da principal)
```

### Fase 3: Implementação

1. **Atualizar app/core/config.py** com todas as configurações necessárias
2. **Modificar app/api/core/config.py** para herdar da configuração principal
3. **Corrigir imports** em todos os arquivos
4. **Testar** todas as funcionalidades

## Próximos Passos

1. ✅ Análise completa realizada
2. 🔄 Consolidar configurações
3. 🔄 Corrigir imports
4. 🔄 Testar funcionalidades
5. 🔄 Validar deployment

## Arquivos Afetados

Os seguintes arquivos precisam ser atualizados:

- `app/api/core/main.py`
- `app/api/core/security.py`
- `app/api/core/database.py`
- `app/api/core/supabase_client.py`
- `app/api/core/test_config.py`

Todos os outros módulos já usam `from app.core.config import settings` corretamente.