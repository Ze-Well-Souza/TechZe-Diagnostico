# Requisitos Técnicos do Microserviço de Diagnóstico

## Visão Geral

Este documento detalha os requisitos técnicos para o desenvolvimento e implementação do microserviço de diagnóstico do TechCare. O microserviço será responsável por realizar diagnósticos de hardware e software, análise de desempenho, previsão de falhas, geração de relatórios e cálculo de pontuação de saúde do sistema.

## Arquitetura

### Padrão de Arquitetura

O microserviço seguirá uma arquitetura em camadas:

1. **Camada de API**: Endpoints FastAPI para interação com clientes
2. **Camada de Serviços**: Lógica de negócio e orquestração
3. **Camada de Analisadores**: Componentes especializados para análise de diferentes aspectos do sistema
4. **Camada de Dados**: Interação com o Supabase para persistência

### Diagrama de Componentes

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  Cliente (Web)   |     |  Cliente (App)   |     |  Admin Panel     |
|                  |     |                  |     |                  |
+--------+---------+     +--------+---------+     +--------+---------+
         |                        |                        |
         |                        |                        |
         v                        v                        v
+------------------------------------------------------------------+
|                                                                  |
|                      API Gateway / Load Balancer                  |
|                                                                  |
+---------------------------+--------------------------------------+
                            |
                            v
+------------------------------------------------------------------+
|                                                                  |
|                    Microserviço de Diagnóstico                   |
|                                                                  |
|  +----------------+  +----------------+  +----------------+      |
|  |                |  |                |  |                |      |
|  |  API (FastAPI) |  |  Serviços     |  |  Analisadores  |      |
|  |                |  |                |  |                |      |
|  +----------------+  +----------------+  +----------------+      |
|                                                                  |
+---------------------------+--------------------------------------+
                            |
                            v
+------------------------------------------------------------------+
|                                                                  |
|                           Supabase                               |
|                                                                  |
|  +----------------+  +----------------+  +----------------+      |
|  |                |  |                |  |                |      |
|  |  PostgreSQL    |  |  Autenticação |  |  Storage       |      |
|  |                |  |                |  |                |      |
|  +----------------+  +----------------+  +----------------+      |
|                                                                  |
+------------------------------------------------------------------+
```

## Estrutura do Projeto

```
microservices/diagnostic_service/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Ponto de entrada da aplicação
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py              # Autenticação e autorização
│   │   ├── config.py            # Configurações da aplicação
│   │   └── db.py                # Conexão com Supabase
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── base_analyzer.py     # Classe base para analisadores
│   │   ├── cpu_analyzer.py      # Analisador de CPU
│   │   ├── memory_analyzer.py   # Analisador de memória
│   │   ├── disk_analyzer.py     # Analisador de disco
│   │   └── network_analyzer.py  # Analisador de rede
│   ├── models/
│   │   ├── __init__.py
│   │   └── diagnostic.py        # Modelo de dados para diagnóstico
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── diagnostic.py        # Esquemas Pydantic para validação
│   ├── services/
│   │   ├── __init__.py
│   │   ├── diagnostic_service.py # Serviço de diagnóstico
│   │   ├── report_service.py    # Serviço de relatórios
│   │   └── system_info_service.py # Serviço de informações do sistema
│   └── utils/
│       ├── __init__.py
│       ├── logger.py            # Configuração de logging
│       └── helpers.py           # Funções auxiliares
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Configurações para testes
│   ├── test_analyzers/
│   ├── test_services/
│   └── test_api/
├── .env                         # Variáveis de ambiente
├── .env.example                 # Exemplo de variáveis de ambiente
├── .gitignore                   # Arquivos a serem ignorados pelo Git
├── Dockerfile                   # Configuração para Docker
├── docker-compose.yml           # Configuração para Docker Compose
├── requirements.txt             # Dependências do projeto
└── README.md                    # Documentação do projeto
```

## Componentes

### 1. Analisadores

#### 1.1 CPUAnalyzer

**Responsabilidades:**
- Analisar uso da CPU
- Verificar temperatura da CPU
- Verificar frequência da CPU
- Detectar gargalos de processamento

**Métodos:**
- `analyze_usage()`: Analisa o uso atual da CPU
- `analyze_temperature()`: Verifica a temperatura da CPU
- `analyze_frequency()`: Verifica a frequência atual da CPU
- `get_status()`: Retorna o status geral da CPU

#### 1.2 MemoryAnalyzer

**Responsabilidades:**
- Analisar uso da memória RAM
- Verificar memória disponível
- Detectar vazamentos de memória
- Analisar uso de swap

**Métodos:**
- `analyze_usage()`: Analisa o uso atual da memória
- `analyze_available()`: Verifica a memória disponível
- `analyze_swap()`: Analisa o uso de swap
- `get_status()`: Retorna o status geral da memória

#### 1.3 DiskAnalyzer

**Responsabilidades:**
- Analisar espaço em disco
- Verificar velocidade de leitura/escrita
- Detectar fragmentação
- Verificar saúde do disco

**Métodos:**
- `analyze_space()`: Analisa o espaço disponível em disco
- `analyze_io_speed()`: Verifica a velocidade de leitura/escrita
- `analyze_health()`: Verifica a saúde do disco
- `get_status()`: Retorna o status geral do disco

#### 1.4 NetworkAnalyzer

**Responsabilidades:**
- Analisar conectividade de rede
- Verificar velocidade de download/upload
- Detectar problemas de latência
- Verificar configurações de rede

**Métodos:**
- `analyze_connectivity()`: Analisa a conectividade de rede
- `analyze_speed()`: Verifica a velocidade de download/upload
- `analyze_latency()`: Analisa a latência da rede
- `get_status()`: Retorna o status geral da rede

### 2. Serviços

#### 2.1 DiagnosticService

**Responsabilidades:**
- Orquestrar o processo de diagnóstico
- Coordenar os diferentes analisadores
- Calcular pontuação de saúde do sistema
- Persistir resultados no banco de dados

**Métodos:**
- `run_diagnostic()`: Executa um diagnóstico completo
- `get_diagnostic_result()`: Obtém o resultado de um diagnóstico
- `calculate_health_score()`: Calcula a pontuação de saúde do sistema
- `save_diagnostic()`: Salva o diagnóstico no banco de dados

#### 2.2 ReportService

**Responsabilidades:**
- Gerar relatórios a partir dos diagnósticos
- Formatar relatórios em diferentes formatos (PDF, HTML, JSON)
- Persistir relatórios no banco de dados

**Métodos:**
- `generate_report()`: Gera um relatório a partir de um diagnóstico
- `format_report()`: Formata o relatório no formato especificado
- `save_report()`: Salva o relatório no banco de dados

#### 2.3 SystemInfoService

**Responsabilidades:**
- Coletar informações do sistema
- Fornecer informações para os analisadores
- Detectar hardware e software instalados

**Métodos:**
- `get_system_info()`: Obtém informações gerais do sistema
- `get_hardware_info()`: Obtém informações de hardware
- `get_software_info()`: Obtém informações de software

### 3. API

#### 3.1 Endpoints

**Diagnósticos:**
- `POST /api/v1/diagnostics`: Inicia um novo diagnóstico
- `GET /api/v1/diagnostics/{id}`: Obtém um diagnóstico específico
- `GET /api/v1/diagnostics`: Obtém todos os diagnósticos do usuário
- `PATCH /api/v1/diagnostics/{id}`: Atualiza um diagnóstico

**Relatórios:**
- `POST /api/v1/reports`: Gera um novo relatório
- `GET /api/v1/reports/{id}`: Obtém um relatório específico
- `GET /api/v1/reports`: Obtém todos os relatórios do usuário

**Sistema:**
- `GET /api/v1/system/info`: Obtém informações do sistema
- `GET /api/v1/system/health`: Obtém o status de saúde do sistema

## Requisitos Funcionais

1. O microserviço deve ser capaz de realizar diagnósticos completos de hardware e software
2. O microserviço deve calcular uma pontuação de saúde do sistema
3. O microserviço deve gerar relatórios detalhados dos diagnósticos
4. O microserviço deve detectar problemas comuns de hardware e software
5. O microserviço deve fornecer recomendações para resolver problemas detectados
6. O microserviço deve armazenar histórico de diagnósticos para análise de tendências
7. O microserviço deve permitir a exportação de relatórios em diferentes formatos
8. O microserviço deve ser capaz de realizar análises preditivas para prevenção de falhas

## Requisitos Não-Funcionais

1. **Desempenho**: O microserviço deve completar um diagnóstico em menos de 2 minutos
2. **Escalabilidade**: O microserviço deve suportar pelo menos 100 diagnósticos simultâneos
3. **Disponibilidade**: O microserviço deve ter disponibilidade de 99.9%
4. **Segurança**: O microserviço deve implementar autenticação JWT e autorização baseada em funções
5. **Usabilidade**: A API deve ser bem documentada e fácil de usar
6. **Manutenibilidade**: O código deve seguir boas práticas e ser bem documentado
7. **Compatibilidade**: O microserviço deve ser compatível com Windows, Linux e macOS

## Dependências

### Bibliotecas Python

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

### Serviços Externos

- **Supabase**: Para banco de dados, autenticação e armazenamento
- **Docker**: Para containerização
- **CI/CD**: GitHub Actions, Jenkins ou similar

## Integração com Supabase

### Tabelas

1. **diagnostics**: Armazena resultados de diagnósticos
2. **devices**: Armazena informações sobre dispositivos
3. **reports**: Armazena relatórios gerados

### Autenticação

O microserviço utilizará a autenticação JWT fornecida pelo Supabase para proteger os endpoints da API.

## Monitoramento

### Logging

O microserviço implementará logging em diferentes níveis:

- **INFO**: Operações normais
- **WARNING**: Situações potencialmente problemáticas
- **ERROR**: Erros que não impedem o funcionamento do serviço
- **CRITICAL**: Erros que impedem o funcionamento do serviço

### Métricas

O microserviço coletará as seguintes métricas:

- Tempo de resposta dos endpoints
- Número de diagnósticos realizados
- Taxa de sucesso/falha dos diagnósticos
- Uso de recursos (CPU, memória, disco)

## Testes

### Testes Unitários

Testes unitários serão implementados para cada componente do microserviço, com foco em:

- Analisadores
- Serviços
- Utilitários

### Testes de Integração

Testes de integração serão implementados para verificar a interação entre os componentes, com foco em:

- Integração entre analisadores e serviços
- Integração entre serviços e API
- Integração com Supabase

### Testes de Carga

Testes de carga serão implementados para verificar o desempenho do microserviço sob diferentes condições de carga.

## Documentação

### API

A API será documentada usando Swagger/OpenAPI, com descrições detalhadas de cada endpoint, parâmetros e respostas.

### Código

O código será documentado usando docstrings e comentários, seguindo as convenções do PEP 257.

### Usuário

Será fornecida documentação para usuários finais, explicando como utilizar o microserviço e interpretar os resultados dos diagnósticos.

## Deploy

### Containerização

O microserviço será containerizado usando Docker, com um Dockerfile e docker-compose.yml para facilitar o deploy.

### CI/CD

Será implementado um pipeline de CI/CD para automatizar o processo de build, teste e deploy.

### Ambientes

Serão configurados os seguintes ambientes:

- **Desenvolvimento**: Para desenvolvimento e testes locais
- **Homologação**: Para testes de integração e validação
- **Produção**: Para uso em produção

## Próximos Passos

1. Configurar ambiente de desenvolvimento
2. Implementar analisadores
3. Implementar serviços
4. Implementar API
5. Configurar Supabase
6. Implementar testes
7. Configurar CI/CD
8. Realizar deploy