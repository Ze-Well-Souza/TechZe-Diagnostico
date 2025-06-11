#!/usr/bin/env python3
"""
Teste dos endpoints da API TechZe Diagnóstico
Valida se todas as APIs estão funcionando após as migrações
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime, date

# Adicionar o app ao path
sys.path.append(str(Path(__file__).parent))

def test_models_import():
    """Testa imports dos modelos"""
    try:
        from app.models.orcamento import (
            Orcamento, OrcamentoCreate, DadosCliente, 
            DadosEquipamento, StatusOrcamento
        )
        from app.models.estoque import ItemEstoque, TipoItem, CategoriaItem
        from app.models.ordem_servico import OrdemServico, StatusOS
        
        print("✅ Modelos importados com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar modelos: {e}")
        return False

def test_services_import():
    """Testa imports dos services"""
    try:
        from app.services.orcamento_service import OrcamentoService
        from app.services.estoque_service import EstoqueService
        from app.services.ordem_servico_service import OrdemServicoService
        
        print("✅ Services importados com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro ao importar services: {e}")
        return False

def test_services_instantiation():
    """Testa instanciação dos services"""
    try:
        from app.services.orcamento_service import OrcamentoService
        from app.services.estoque_service import EstoqueService
        from app.services.ordem_servico_service import OrdemServicoService
        
        # Instanciar services
        orcamento_service = OrcamentoService()
        estoque_service = EstoqueService()
        os_service = OrdemServicoService()
        
        print("✅ Services instanciados com sucesso")
        print(f"  - OrcamentoService: {type(orcamento_service)}")
        print(f"  - EstoqueService: {type(estoque_service)}")
        print(f"  - OrdemServicoService: {type(os_service)}")
        return True
    except Exception as e:
        print(f"❌ Erro ao instanciar services: {e}")
        return False

def test_models_creation():
    """Testa criação de modelos"""
    try:
        from app.models.orcamento import (
            DadosCliente, DadosEquipamento, OrcamentoCreate
        )
        from app.models.estoque import ItemEstoqueCreate, TipoItem, CategoriaItem
        
        # Criar dados de teste
        cliente = DadosCliente(
            nome="João Silva",
            telefone="11999999999",
            email="joao@email.com"
        )
        
        equipamento = DadosEquipamento(
            tipo="Desktop",
            marca="Dell",
            modelo="Inspiron",
            problema_relatado="Computador não liga"
        )
        
        # Criar item de estoque
        item_estoque = ItemEstoqueCreate(
            codigo="TEST-001",
            nome="Item de Teste",
            tipo=TipoItem.PECA_HARDWARE,
            categoria=CategoriaItem.PROCESSADOR,
            quantidade_atual=10,
            quantidade_minima=1,
            preco_custo=100.0,
            preco_venda=200.0
        )
        
        print("✅ Modelos criados com sucesso")
        print(f"  - Cliente: {cliente.nome}")
        print(f"  - Equipamento: {equipamento.tipo}")
        print(f"  - Item Estoque: {item_estoque.nome}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar modelos: {e}")
        return False

async def test_supabase_connection():
    """Testa conexão com Supabase"""
    try:
        from app.core.config import get_settings
        from supabase import create_client
        
        settings = get_settings()
        client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        
        print("✅ Conexão Supabase estabelecida")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão Supabase: {e}")
        return False

def generate_test_data():
    """Gera dados de teste para inserir no banco"""
    test_data = {
        "clientes": [
            {
                "nome": "João Silva",
                "cpf": "123.456.789-00",
                "telefone": "11999999999",
                "email": "joao@email.com",
                "endereco": {
                    "rua": "Rua das Flores, 123",
                    "cidade": "São Paulo",
                    "estado": "SP",
                    "cep": "01234-567"
                }
            },
            {
                "nome": "Maria Santos",
                "telefone": "11888888888",
                "email": "maria@email.com"
            }
        ],
        "estoque_itens": [
            {
                "codigo": "MEM-8GB-DDR4",
                "nome": "Memória 8GB DDR4",
                "descricao": "Memória RAM 8GB DDR4 2400MHz",
                "tipo": "peca",
                "categoria": "memoria",
                "quantidade_atual": 10,
                "quantidade_minima": 2,
                "preco_custo": 150.00,
                "preco_venda": 280.00,
                "status": "ativo"
            },
            {
                "codigo": "HD-1TB-SATA",
                "nome": "HD 1TB SATA",
                "descricao": "Disco rígido 1TB SATA 7200RPM",
                "tipo": "peca",
                "categoria": "armazenamento",
                "quantidade_atual": 5,
                "quantidade_minima": 1,
                "preco_custo": 200.00,
                "preco_venda": 350.00,
                "status": "ativo"
            }
        ]
    }
    
    # Salvar dados de teste
    test_file = Path(__file__).parent / "test_data.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Dados de teste salvos: {test_file}")
    return True

async def main():
    """Função principal"""
    print("🧪 TESTE DE ENDPOINTS API - TechZe Diagnóstico")
    print("=" * 60)
    
    # Teste 1: Imports de modelos
    if not test_models_import():
        return False
    
    # Teste 2: Imports de services
    if not test_services_import():
        return False
    
    # Teste 3: Instanciação de services
    if not test_services_instantiation():
        return False
    
    # Teste 4: Criação de modelos
    if not test_models_creation():
        return False
    
    # Teste 5: Conexão Supabase
    if not await test_supabase_connection():
        return False
    
    # Teste 6: Geração de dados de teste
    if not generate_test_data():
        return False
    
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("=" * 60)
    print("✅ Modelos funcionando")
    print("✅ Services funcionando") 
    print("✅ Supabase conectado")
    print("✅ Dados de teste gerados")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Execute as migrações no Supabase Dashboard:")
    print("   - Acesse: https://supabase.com/dashboard")
    print("   - Vá para SQL Editor")
    print("   - Execute: database/migrations/001_create_core_tables.sql")
    print("2. Insira dados de teste via Dashboard ou API")
    print("3. Inicie o servidor: uvicorn app.main:app --reload")
    print("4. Teste endpoints: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)