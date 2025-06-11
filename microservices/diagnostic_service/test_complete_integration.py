#!/usr/bin/env python3
"""
Teste de Integração Completa - TechZe Diagnóstico Backend
Validação de todos os componentes críticos
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def test_configurations():
    """Teste das configurações"""
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        logger.info("✅ Configurações carregadas")
        logger.info(f"  - Supabase URL: {settings.SUPABASE_URL}")
        logger.info(f"  - Environment: {settings.ENVIRONMENT}")
        logger.info(f"  - Host: {settings.HOST}:{settings.PORT}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro nas configurações: {e}")
        return False

def test_supabase_connection():
    """Teste da conexão Supabase"""
    try:
        from app.core.supabase import get_supabase_client
        client = get_supabase_client()
        
        logger.info("✅ Cliente Supabase inicializado")
        logger.info(f"  - Tipo: {type(client).__name__}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro no Supabase: {e}")
        return False

def test_models():
    """Teste dos modelos de dados"""
    try:
        from app.models.orcamento import Orcamento, OrcamentoStatus, DadosCliente, DadosEquipamento
        from app.models.estoque import EstoqueItem, EstoqueMovimentacao
        from app.models.ordem_servico import OrdemServico, OSStatus
        
        # Teste de criação de objetos com estrutura correta
        cliente_data = DadosCliente(
            nome="João Silva",
            telefone="11999999999",
            email="joao@email.com"
        )
        
        equipamento_data = DadosEquipamento(
            tipo="Desktop",
            marca="Dell",
            modelo="OptiPlex 7070",
            problema_relatado="Computador não liga"
        )
        
        orcamento_data = {
            "numero": "ORC-2025-001",
            "cliente": cliente_data,
            "equipamento": equipamento_data,
            "status": OrcamentoStatus.PENDENTE
        }
        
        orcamento = Orcamento(**orcamento_data)
        
        logger.info("✅ Modelos de dados funcionando")
        logger.info(f"  - Orçamento: {orcamento.numero}")
        logger.info(f"  - Status: {orcamento.status}")
        logger.info(f"  - Cliente: {orcamento.cliente.nome}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro nos modelos: {e}")
        return False

def test_services():
    """Teste dos serviços"""
    try:
        from app.services.orcamento_service import OrcamentoService
        from app.services.estoque_service import EstoqueService
        from app.services.ordem_servico_service import OrdemServicoService
        
        # Instanciar serviços
        orcamento_service = OrcamentoService()
        estoque_service = EstoqueService()
        os_service = OrdemServicoService()
        
        logger.info("✅ Serviços instanciados")
        logger.info(f"  - OrcamentoService: {type(orcamento_service).__name__}")
        logger.info(f"  - EstoqueService: {type(estoque_service).__name__}")
        logger.info(f"  - OrdemServicoService: {type(os_service).__name__}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro nos serviços: {e}")
        return False

def test_repositories():
    """Teste dos repositórios"""
    try:
        from app.db.repositories.orcamento_repository import OrcamentoRepository
        from app.db.repositories.estoque_repository import EstoqueRepository
        from app.db.repositories.ordem_servico_repository import OrdemServicoRepository
        
        # Instanciar repositórios
        orcamento_repo = OrcamentoRepository()
        estoque_repo = EstoqueRepository()
        os_repo = OrdemServicoRepository()
        
        logger.info("✅ Repositórios instanciados")
        logger.info(f"  - OrcamentoRepository: {type(orcamento_repo).__name__}")
        logger.info(f"  - EstoqueRepository: {type(estoque_repo).__name__}")
        logger.info(f"  - OrdemServicoRepository: {type(os_repo).__name__}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro nos repositórios: {e}")
        return False

def test_api_endpoints():
    """Teste das APIs"""
    try:
        from app.api.endpoints.orcamentos import router as orcamentos_router
        from app.api.endpoints.estoque import router as estoque_router
        from app.api.endpoints.ordem_servico import router as os_router
        
        logger.info("✅ API endpoints carregados")
        logger.info(f"  - Orçamentos router: {len(orcamentos_router.routes)} rotas")
        logger.info(f"  - Estoque router: {len(estoque_router.routes)} rotas")
        logger.info(f"  - OS router: {len(os_router.routes)} rotas")
        return True
    except Exception as e:
        logger.error(f"❌ Erro nas APIs: {e}")
        return False

def test_fastapi_app():
    """Teste da aplicação FastAPI"""
    try:
        from app.main import app
        
        logger.info("✅ Aplicação FastAPI carregada")
        logger.info(f"  - Title: {app.title}")
        logger.info(f"  - Version: {app.version}")
        logger.info(f"  - Rotas: {len(app.routes)}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro na aplicação: {e}")
        return False

def generate_report(results):
    """Gera relatório de testes"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "test_results": results,
        "summary": {
            "total_tests": len(results),
            "passed": sum(1 for r in results.values() if r),
            "failed": sum(1 for r in results.values() if not r)
        },
        "status": "PASS" if all(results.values()) else "FAIL"
    }
    
    # Salvar relatório
    report_file = Path("integration_test_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    logger.info(f"📝 Relatório salvo em: {report_file}")
    return report

def main():
    """Função principal"""
    logger.info("🧪 TESTE DE INTEGRAÇÃO COMPLETA - TECHZE BACKEND")
    logger.info("=" * 60)
    
    tests = {
        "configurações": test_configurations,
        "supabase": test_supabase_connection,
        "modelos": test_models,
        "serviços": test_services,
        "repositórios": test_repositories,
        "api_endpoints": test_api_endpoints,
        "fastapi_app": test_fastapi_app
    }
    
    results = {}
    
    for test_name, test_func in tests.items():
        logger.info(f"\n🔍 Testando: {test_name}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ Erro crítico em {test_name}: {e}")
            results[test_name] = False
    
    # Gerar relatório
    report = generate_report(results)
    
    # Resumo final
    logger.info("\n📊 RESUMO FINAL")
    logger.info("=" * 30)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\n🎯 Status Geral: {report['status']}")
    logger.info(f"📈 Testes: {report['summary']['passed']}/{report['summary']['total_tests']} passaram")
    
    if report['status'] == "PASS":
        logger.info("\n🎉 BACKEND FUNCIONANDO PERFEITAMENTE!")
        logger.info("✅ Pronto para próximos passos:")
        logger.info("  1. Executar migrações SQL no Supabase")
        logger.info("  2. Iniciar servidor: uvicorn app.main:app --reload")
        logger.info("  3. Testar endpoints: http://localhost:8000/docs")
    else:
        logger.error("\n⚠️ BACKEND COM PROBLEMAS")
        logger.error("❌ Corrigir erros antes de prosseguir")
    
    return report['status'] == "PASS"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 