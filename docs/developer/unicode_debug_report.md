# 🔍 Relatório de Debug - Problemas Unicode

**Data**: 2025-06-06 09:36:18,333

## 📊 Resumo dos Problemas

- **Arquivos analisados**: 8
- **Arquivos problemáticos**: 3

## 📁 Detalhes por Arquivo

### microservices\diagnostic_service\setup_monitoring_stack.py
- **Encoding**: MacRoman
- **Confiança**: 68.92%

### microservices\diagnostic_service\app\ai\ml_engine.py
- **Encoding**: utf-8
- **Confiança**: 99.00%

### microservices\diagnostic_service\app\api\endpoints\monitoring.py
- **Encoding**: utf-8
- **Confiança**: 75.25%

### microservices\diagnostic_service\app\ai\__init__.py
- **Encoding**: utf-8
- **Confiança**: 75.25%

### microservices\diagnostic_service\app\ai\chatbot.py
- **Encoding**: Windows-1254
- **Confiança**: 64.26%

### microservices\diagnostic_service\app\core\monitoring.py
- **Encoding**: utf-8
- **Confiança**: 99.00%

### microservices\diagnostic_service\app\core\advanced_monitoring.py
- **Encoding**: MacRoman
- **Confiança**: 71.83%

### microservices\diagnostic_service\app\api\endpoints\monitoring_advanced.py
- **Encoding**: ascii
- **Confiança**: 100.00%

## 🔧 Recomendações

1. Converter todos os arquivos para UTF-8
2. Adicionar `# -*- coding: utf-8 -*-` no topo dos arquivos Python
3. Configurar IDE para usar UTF-8 por padrão
4. Usar `encoding='utf-8'` em todas as operações de arquivo
