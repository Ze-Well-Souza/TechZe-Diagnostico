# 🚀 TechZe - Instruções Rápidas

## ⚡ Setup Automático (Recomendado)

```bash
python run_setup.py
```

Este comando irá:
- ✅ Configurar todo o sistema automaticamente
- ✅ Aplicar políticas do Supabase
- ✅ Corrigir problemas críticos
- ✅ Validar o sistema completo
- ✅ Criar scripts de inicialização

## 🚀 Iniciar Sistema

### Windows
```batch
start_all.bat
```

### Linux/Mac
```bash
./start_all.sh
```

### Manual
```bash
# Terminal 1 - Backend
cd microservices/diagnostic_service
python app/main.py

# Terminal 2 - Frontend  
cd frontend-v3
npm run dev
```

## 🌐 URLs

- **Frontend**: http://localhost:8081
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 🔧 Scripts Disponíveis

| Script | Descrição |
|--------|-----------|
| `run_setup.py` | Setup automático completo |
| `setup_complete.py` | Configuração do sistema |
| `apply_rls_manual.py` | Políticas Supabase |
| `fix_critical_issues.py` | Correção de problemas |
| `validate_system.py` | Validação completa |

## 🆘 Problemas?

```bash
python validate_system.py
```

Este comando irá diagnosticar e sugerir soluções.

## 📖 Documentação Completa

Consulte `README_SETUP.md` para instruções detalhadas.

---

**🎯 Para começar rapidamente: Execute `python run_setup.py` e siga as instruções!**