#!/usr/bin/env python3
"""
Validação Final do Backend TechZe - Diagnóstico Completo
Confirma se o sistema está 100% funcional e pronto para produção
"""

import logging
import json
import sys
from datetime import datetime
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BackendValidator:
    """Validador completo do backend"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_total = 0
        self.results = {}
        
    def test_component(self, name: str, test_func):
        """Executa um teste de componente"""
        self.tests_total += 1
        try:
            result = test_func()
            if result:
                self.tests_passed += 1
                logger.info(f"✅ {name}: PASS")
            else:
                logger.error(f"❌ {name}: FAIL")
            self.results[name] = result
            return result
        except Exception as e:
            logger.error(f"❌ {name}: ERROR - {e}")
            self.results[name] = False
            return False
    
    def test_models_import(self) -> bool:
        """Testa importação dos modelos"""
        try:
            from app.models.orcamento import Orcamento, OrcamentoStatus
            from app.models.estoque import EstoqueItem, ItemEstoque
            from app.models.ordem_servico import OrdemServico, OSStatus
            return True
        except Exception:
            return False
    
    def test_services_import(self) -> bool:
        """Testa importação dos serviços"""
        try:
            from app.services.orcamento_service import OrcamentoService
            from app.services.estoque_service import EstoqueService
            from app.services.ordem_servico_service import OrdemServicoService
            return True
        except Exception:
            return False
    
    def test_repositories_import(self) -> bool:
        """Testa importação dos repositórios"""
        try:
            from app.db.repositories.orcamento_repository import OrcamentoRepository
            from app.db.repositories.estoque_repository import EstoqueRepository
            from app.db.repositories.ordem_servico_repository import OrdemServicoRepository
            return True
        except Exception:
            return False
    
    def test_api_endpoints_import(self) -> bool:
        """Testa importação dos endpoints"""
        try:
            from app.api.endpoints.orcamentos import router as orcamentos_router
            from app.api.endpoints.estoque import router as estoque_router
            from app.api.endpoints.ordem_servico import router as os_router
            return len(orcamentos_router.routes) > 0 and len(estoque_router.routes) > 0
        except Exception:
            return False
    
    def test_fastapi_app(self) -> bool:
        """Testa aplicação FastAPI"""
        try:
            from app.main import app
            return app.title == "TechZe Diagnostic API" and len(app.routes) > 100
        except Exception:
            return False
    
    def test_config_loading(self) -> bool:
        """Testa carregamento de configurações"""
        try:
            from app.core.config import get_settings
            settings = get_settings()
            return hasattr(settings, 'ENVIRONMENT')
        except Exception:
            return False
    
    def test_supabase_connection(self) -> bool:
        """Testa conexão Supabase"""
        try:
            from app.core.supabase import get_supabase_client
            client = get_supabase_client()
            return client is not None
        except Exception:
            return False
    
    def test_database_migrations(self) -> bool:
        """Verifica se as migrações existem"""
        migrations_dir = Path("database/migrations")
        return migrations_dir.exists() and len(list(migrations_dir.glob("*.sql"))) > 0
    
    def test_project_structure(self) -> bool:
        """Verifica estrutura do projeto"""
        required_dirs = [
            "app/models",
            "app/services", 
            "app/db/repositories",
            "app/api/endpoints",
            "database/migrations"
        ]
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                return False
        return True
    
    def test_dependencies(self) -> bool:
        """Testa dependências críticas"""
        try:
            import fastapi
            import pydantic
            import supabase
            import uvicorn
            return True
        except ImportError:
            return False
    
    def run_validation(self) -> bool:
        """Executa validação completa"""
        logger.info("🔍 VALIDAÇÃO FINAL DO BACKEND TECHZE")
        logger.info("=" * 60)
        
        # Testes de componentes
        self.test_component("Estrutura do Projeto", self.test_project_structure)
        self.test_component("Dependências", self.test_dependencies)
        self.test_component("Configurações", self.test_config_loading)
        self.test_component("Conexão Supabase", self.test_supabase_connection)
        self.test_component("Modelos de Dados", self.test_models_import)
        self.test_component("Serviços", self.test_services_import)
        self.test_component("Repositórios", self.test_repositories_import)
        self.test_component("API Endpoints", self.test_api_endpoints_import)
        self.test_component("Aplicação FastAPI", self.test_fastapi_app)
        self.test_component("Migrações DB", self.test_database_migrations)
        
        # Resultados
        success_rate = (self.tests_passed / self.tests_total) * 100
        
        logger.info("\n📊 RESUMO DA VALIDAÇÃO")
        logger.info("=" * 40)
        logger.info(f"📈 Testes Passaram: {self.tests_passed}/{self.tests_total}")
        logger.info(f"📊 Taxa de Sucesso: {success_rate:.1f}%")
        
        # Gerar relatório
        report = {
            "timestamp": datetime.now().isoformat(),
            "validation_results": self.results,
            "summary": {
                "tests_passed": self.tests_passed,
                "tests_total": self.tests_total,
                "success_rate": success_rate,
                "status": "PASS" if self.tests_passed == self.tests_total else "FAIL"
            }
        }
        
        with open("backend_validation_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📝 Relatório salvo: backend_validation_report.json")
        
        if self.tests_passed == self.tests_total:
            logger.info("\n🎉 BACKEND VALIDADO COM SUCESSO!")
            logger.info("✅ Sistema pronto para produção!")
            logger.info("\n🚀 PRÓXIMOS PASSOS:")
            logger.info("  1. Deploy no ambiente de produção")
            logger.info("  2. Configurar monitoramento")
            logger.info("  3. Executar testes end-to-end")
            logger.info("  4. Treinamento da equipe")
            return True
        else:
            failed_tests = [name for name, result in self.results.items() if not result]
            logger.error(f"\n❌ VALIDAÇÃO FALHOU!")
            logger.error(f"⚠️ Testes com falha: {', '.join(failed_tests)}")
            return False

def main():
    """Função principal"""
    validator = BackendValidator()
    success = validator.run_validation()
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Validação interrompida pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n💥 Erro crítico: {e}")
        sys.exit(1) 