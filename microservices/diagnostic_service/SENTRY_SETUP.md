# Configuração do Sentry

## Como configurar o Sentry para monitoramento de erros

### 1. Criar conta no Sentry

1. Acesse [sentry.io](https://sentry.io)
2. Crie uma conta gratuita
3. Crie um novo projeto para "Python/FastAPI"

### 2. Obter o DSN

1. No dashboard do Sentry, vá em **Settings** > **Projects**
2. Selecione seu projeto
3. Vá em **Client Keys (DSN)**
4. Copie o DSN (formato: `https://key@sentry.io/project-id`)

### 3. Configurar no projeto

#### Para desenvolvimento local:
```bash
# No arquivo .env
SENTRY_DSN=https://sua-chave@sentry.io/seu-project-id
```

#### Para produção no Render:
1. No dashboard do Render, vá em **Environment**
2. Adicione a variável:
   - **Key**: `SENTRY_DSN`
   - **Value**: `https://sua-chave@sentry.io/seu-project-id`

### 4. Verificar configuração

Após configurar, reinicie o servidor. Você deve ver no log:
```
Sentry configurado para ambiente: production, release: 1.0.0
```

### 5. Testar

Para testar se está funcionando, você pode forçar um erro:
```python
# Adicione temporariamente em algum endpoint
raise Exception("Teste do Sentry")
```

## Configurações opcionais

### Variáveis de ambiente adicionais:

```bash
# Ambiente (development, staging, production)
ENVIRONMENT=production

# Versão da aplicação para tracking de releases
APP_VERSION=1.0.0

# Release para tracking
RELEASE=v1.0.0
```

## Desabilitar Sentry

Para desabilitar o Sentry (útil em desenvolvimento):

1. Comente ou remova a variável `SENTRY_DSN` do `.env`
2. Ou defina como vazia: `SENTRY_DSN=`

O sistema detectará automaticamente e desabilitará o monitoramento.

## Recursos do Sentry configurados

- ✅ Captura de exceções automática
- ✅ Monitoramento de performance (20% das transações)
- ✅ Profiling de código (10% das execuções)
- ✅ Integração com FastAPI, SQLAlchemy e Redis
- ✅ Breadcrumbs para rastreamento de contexto
- ✅ Filtros para evitar spam (rate limiting, health checks)
- ✅ Alertas configuráveis

## Troubleshooting

### Erro "Unsupported scheme"
- Verifique se o DSN está no formato correto
- Certifique-se de que não contém espaços ou caracteres especiais

### Sentry não está capturando erros
- Verifique se o DSN está correto
- Confirme que a variável de ambiente está sendo carregada
- Verifique os logs para mensagens de inicialização do Sentry