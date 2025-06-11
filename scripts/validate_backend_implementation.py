#!/usr/bin/env python3
"""
Script de Validação da Implementação Backend - TechZe Diagnóstico
Valida se todas as correções foram aplicadas corretamente
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório do app ao path
sys.path.append(str(Path(__file__).parent.parent))

def test_models_integrity():
    """Testa integridade dos modelos"""
    print("🔍 Testando integridade dos modelos...")
    
    try:
        from app.models.orcamento import (
            Orcamento, OrcamentoCreate, OrcamentoUpdate, 
            OrcamentoResponse, OrcamentoDetalhado,
            DadosCliente, DadosEquipamento, ItemOrcamento, PecaOrcamento,
            StatusOrcamento, TipoServico
        )
        print("✅ Modelos de orçamento - OK")
        
        from app.models.estoque import (
            EstoqueItem, EstoqueMovimentacao, EstoqueAlerta,
            StatusEstoque, TipoMovimentacao
        )
        print("✅ Modelos de estoque - OK")
        
        from app.models.ordem_servico import (
            OrdemServico, OrdemServicoCreate, OrdemServicoUpdate,
            StatusOS, PrioridadeOS
        )
        print("✅ Modelos de ordem de serviço - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos modelos: {e}")
        return False

def test_services_implementation():
    """Testa implementação dos services"""
    print("\n⚙️ Testando implementação dos services...")
    
    try:
        from app.services.orcamento_service import OrcamentoService
        from app.services.estoque_service import EstoqueService
        from app.services.ordem_servico_service import OrdemServicoService
        
        # Testa instanciação
        orcamento_service = OrcamentoService()
        estoque_service = EstoqueService()
        os_service = OrdemServicoService()
        
        print("✅ Services instanciados - OK")
        
        # Verifica métodos críticos do OrcamentoService
        required_methods = [
            'criar_orcamento', 'buscar_orcamento', 'listar_orcamentos',
            'atualizar_orcamento', 'aprovar_orcamento', 'rejeitar_orcamento'
        ]
        
        for method in required_methods:
            if not hasattr(orcamento_service, method):
                print(f"❌ Método {method} faltando no OrcamentoService")
                return False
        
        print("✅ Métodos do OrcamentoService - OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos services: {e}")
        return False

def test_repositories_integration():
    """Testa integração dos repositories"""
    print("\n🗄️ Testando integração dos repositories...")
    
    try:
        from app.db.repositories.orcamento_repository import OrcamentoRepository
        from app.db.repositories.estoque_repository import EstoqueRepository
        from app.db.repositories.ordem_servico_repository import OrdemServicoRepository
        
        # Testa instanciação
        orcamento_repo = OrcamentoRepository()
        estoque_repo = EstoqueRepository()
        os_repo = OrdemServicoRepository()
        
        print("✅ Repositories instanciados - OK")
        
        # Verifica herança do SupabaseRepository
        from app.db.repositories.supabase_repository import SupabaseRepository
        
        if isinstance(orcamento_repo, SupabaseRepository):
            print("✅ OrcamentoRepository herda SupabaseRepository - OK")
        else:
            print("❌ OrcamentoRepository não herda SupabaseRepository")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos repositories: {e}")
        return False

def test_api_endpoints():
    """Testa endpoints da API"""
    print("\n🌐 Testando endpoints da API...")
    
    try:
        from fastapi import APIRouter
        from app.api.endpoints.orcamentos import router as orcamento_router
        from app.api.endpoints.estoque import router as estoque_router
        from app.api.endpoints.ordem_servico import router as os_router
        
        # Verifica se são instâncias válidas de APIRouter
        routers = [
            ("orcamentos", orcamento_router),
            ("estoque", estoque_router),
            ("ordem_servico", os_router)
        ]
        
        for name, router in routers:
            if isinstance(router, APIRouter):
                route_count = len(router.routes)
                print(f"✅ API {name}: {route_count} rotas - OK")
            else:
                print(f"❌ API {name}: Router inválido")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos endpoints: {e}")
        return False

def test_database_migration():
    """Verifica arquivos de migração"""
    print("\n📊 Verificando arquivos de migração...")
    
    try:
        migration_file = Path(__file__).parent.parent / "database" / "migrations" / "001_create_core_tables.sql"
        
        if migration_file.exists():
            size_kb = migration_file.stat().st_size / 1024
            print(f"✅ Migração SQL encontrada: {size_kb:.1f}KB")
            
            # Verifica se contém criação das tabelas principais
            content = migration_file.read_text(encoding='utf-8')
            tables = ['orcamentos', 'estoque_itens', 'ordem_servico']
            
            for table in tables:
                if table in content:
                    print(f"✅ Tabela {table} presente na migração")
                else:
                    print(f"❌ Tabela {table} faltando na migração")
                    return False
        else:
            print("❌ Arquivo de migração não encontrado")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar migração: {e}")
        return False

def test_configurations():
    """Testa configurações"""
    print("\n⚙️ Testando configurações...")
    
    try:
        from app.core.config import get_settings
        
        settings = get_settings()
        
        # Verifica configurações essenciais
        required_settings = [
            'PROJECT_NAME', 'VERSION', 'API_V1_STR',
            'SUPABASE_URL', 'SUPABASE_SERVICE_KEY'
        ]
        
        for setting in required_settings:
            if hasattr(settings, setting):
                value = getattr(settings, setting)
                if value:
                    print(f"✅ {setting}: {'***' if 'KEY' in setting else value}")
                else:
                    print(f"⚠️ {setting}: vazio")
            else:
                print(f"❌ {setting}: não encontrado")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nas configurações: {e}")
        return False

def test_corrected_issues():
    """Testa se os problemas identificados foram corrigidos"""
    print("\n🔧 Verificando correções aplicadas...")
    
    try:
        # Testa se OrcamentoService não usa mais self.supabase diretamente
        from app.services.orcamento_service import OrcamentoService
        import inspect
        
        service = OrcamentoService()
        source = inspect.getsource(OrcamentoService.buscar_orcamento)
        
        if 'self.repository' in source and 'self.supabase' not in source:
            print("✅ OrcamentoService usa repository pattern - CORRIGIDO")
        else:
            print("❌ OrcamentoService ainda usa self.supabase diretamente")
            return False
        
        # Verifica se o OrcamentoAprovacao tem ip_aprovacao
        from app.models.orcamento import OrcamentoAprovacao
        
        if hasattr(OrcamentoAprovacao, '__annotations__') and 'ip_aprovacao' in OrcamentoAprovacao.__annotations__:
            print("✅ OrcamentoAprovacao tem campo ip_aprovacao - CORRIGIDO")
        else:
            print("❌ OrcamentoAprovacao sem campo ip_aprovacao")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar correções: {e}")
        return False

def main():
    """Função principal de validação"""
    print("🎯 VALIDAÇÃO DA IMPLEMENTAÇÃO BACKEND - TECHZE DIAGNÓSTICO")
    print("=" * 70)
    
    tests = [
        ("Integridade dos Modelos", test_models_integrity),
        ("Implementação dos Services", test_services_implementation),
        ("Integração dos Repositories", test_repositories_integration),
        ("Endpoints da API", test_api_endpoints),
        ("Migração do Banco", test_database_migration),
        ("Configurações", test_configurations),
        ("Correções Aplicadas", test_corrected_issues)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"💥 Erro inesperado em {test_name}: {e}")
            results.append((test_name, False))
    
    # Relatório final
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO FINAL DE VALIDAÇÃO")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    success_rate = (passed / total) * 100
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram ({success_rate:.1f}%)")
    
    if passed == total:
        print("\n🎉 BACKEND COMPLETAMENTE VALIDADO!")
        print("✅ Todas as correções aplicadas com sucesso")
        print("✅ Arquitetura implementada corretamente")
        print("✅ Repository pattern funcionando")
        print("✅ Services corrigidos")
        print("🚀 PRONTO PARA PRÓXIMA FASE")
    elif success_rate >= 80:
        print("\n⚠️ BACKEND QUASE PRONTO")
        print(f"✅ {passed} componentes validados")
        print(f"❌ {total - passed} problemas restantes")
        print("🔧 Revise os erros acima")
    else:
        print("\n❌ BACKEND COM PROBLEMAS CRÍTICOS")
        print("🔧 Corrija os erros antes de continuar")
    
    print("\n" + "=" * 70)
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 