#!/usr/bin/env python3
"""
Teste rápido do backend TechZe Diagnóstico
Valida se todos os componentes estão funcionando
"""

def test_imports():
    """Testa imports principais"""
    print("🔍 Testando imports...")
    
    try:
        # Testa modelos
        from app.models.orcamento import Orcamento, OrcamentoCreate, DadosCliente, DadosEquipamento
        print("✅ Modelos de orçamento")
        
        from app.models.estoque import EstoqueItem
        print("✅ Modelos de estoque")
        
        from app.models.ordem_servico import OrdemServico
        print("✅ Modelos de ordem de serviço")
        
        # Testa services
        from app.services.orcamento_service import OrcamentoService
        print("✅ Service de orçamento")
        
        # Testa APIs
        from app.api.endpoints.orcamentos import router
        print("✅ API de orçamentos")
        
        # Testa configurações
        from app.core.config import get_settings
        settings = get_settings()
        print(f"✅ Configurações carregadas - Projeto: {settings.PROJECT_NAME}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False

def test_models():
    """Testa criação de modelos"""
    print("\n🏗️ Testando modelos...")
    
    try:
        from app.models.orcamento import DadosCliente, DadosEquipamento, Orcamento
        
        # Cria dados de teste
        cliente = DadosCliente(
            nome="Cliente Teste",
            telefone="11999999999",
            email="teste@email.com"
        )
        
        equipamento = DadosEquipamento(
            tipo="Desktop",
            marca="Dell",
            modelo="OptiPlex",
            problema_relatado="Computador não liga"
        )
        
        # Cria orçamento
        orcamento = Orcamento(
            numero="ORC-2025-001",
            cliente=cliente,
            equipamento=equipamento
        )
        
        print(f"✅ Orçamento criado: {orcamento.numero}")
        print(f"   Cliente: {orcamento.cliente.nome}")
        print(f"   Equipamento: {orcamento.equipamento.tipo}")
        print(f"   Status: {orcamento.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na criação de modelos: {e}")
        return False

def test_services():
    """Testa serviços"""
    print("\n⚙️ Testando services...")
    
    try:
        from app.services.orcamento_service import OrcamentoService
        
        # Instancia service
        service = OrcamentoService()
        print("✅ OrcamentoService instanciado")
        
        # Verifica métodos
        methods = [
            'criar_orcamento',
            'buscar_orcamento', 
            'listar_orcamentos',
            'atualizar_orcamento'
        ]
        
        for method in methods:
            if hasattr(service, method):
                print(f"✅ Método {method} presente")
            else:
                print(f"❌ Método {method} faltando")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro nos services: {e}")
        return False

def test_api_structure():
    """Testa estrutura das APIs"""
    print("\n🌐 Testando estrutura das APIs...")
    
    try:
        from fastapi import APIRouter
        from app.api.endpoints.orcamentos import router as orcamento_router
        
        if isinstance(orcamento_router, APIRouter):
            routes_count = len(orcamento_router.routes)
            print(f"✅ API de orçamentos: {routes_count} rotas")
        else:
            print("❌ Router de orçamentos inválido")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na estrutura de APIs: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🎯 TESTE RÁPIDO DO BACKEND TECHZE")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Modelos", test_models),
        ("Services", test_services),
        ("APIs", test_api_structure),
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
    print("\n📊 RELATÓRIO FINAL")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    print(f"\n🎯 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("🚀 Backend pronto para próxima fase")
        return True
    else:
        print("⚠️ Alguns testes falharam")
        print("🔧 Revise os erros acima")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 