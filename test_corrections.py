#!/usr/bin/env python3
"""
Teste das correções aplicadas no backend
"""

def test_imports():
    """Testa imports básicos"""
    try:
        from app.services.orcamento_service import OrcamentoService
        from app.models.orcamento import OrcamentoCreate, DadosCliente, DadosEquipamento
        print("✅ Imports básicos OK")
        return True
    except Exception as e:
        print(f"❌ Erro nos imports: {e}")
        return False

def test_service_instantiation():
    """Testa instanciação do service"""
    try:
        from app.services.orcamento_service import OrcamentoService
        service = OrcamentoService()
        print("✅ OrcamentoService instanciado")
        return True
    except Exception as e:
        print(f"❌ Erro na instanciação: {e}")
        return False

def test_repository_pattern():
    """Testa se o repository pattern está funcionando"""
    try:
        from app.services.orcamento_service import OrcamentoService
        service = OrcamentoService()
        
        # Verifica se tem o repository
        if hasattr(service, 'repository'):
            print("✅ Repository pattern implementado")
            return True
        else:
            print("❌ Repository pattern não encontrado")
            return False
    except Exception as e:
        print(f"❌ Erro no repository pattern: {e}")
        return False

def test_model_creation():
    """Testa criação de modelos"""
    try:
        from app.models.orcamento import DadosCliente, DadosEquipamento
        
        cliente = DadosCliente(
            nome="Cliente Teste",
            telefone="11999999999"
        )
        
        equipamento = DadosEquipamento(
            tipo="Desktop",
            problema_relatado="Teste de problema"
        )
        
        print("✅ Modelos criados com sucesso")
        print(f"   Cliente: {cliente.nome}")
        print(f"   Equipamento: {equipamento.tipo}")
        return True
    except Exception as e:
        print(f"❌ Erro na criação de modelos: {e}")
        return False

def main():
    """Função principal"""
    print("🔧 TESTE DAS CORREÇÕES - BACKEND TECHZE")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_service_instantiation,
        test_repository_pattern,
        test_model_creation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"💥 Erro: {e}")
            results.append(False)
    
    # Resultado
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODAS AS CORREÇÕES FUNCIONANDO!")
    else:
        print("⚠️ Ainda há problemas")
    
    return passed == total

if __name__ == "__main__":
    main() 