"""Testes de importação de schemas para garantir compatibilidade com Pydantic v2"""

import pytest


def test_import_schemas():
    """Testa se todos os schemas podem ser importados corretamente"""
    # Importar todos os schemas
    from app.schemas import diagnostic, report, system_info, api_contracts
    
    # Importar modelos que usam Decimal
    from app.models import estoque, orcamento, ordem_servico
    
    # Verificar se as classes principais estão disponíveis
    assert hasattr(diagnostic, 'DiagnosticBase')
    assert hasattr(report, 'ReportBase')
    assert hasattr(system_info, 'SystemInfoBase')
    assert hasattr(api_contracts, 'ApiResponse')
    
    # Verificar modelos com campos Decimal
    assert hasattr(estoque, 'ItemEstoque')
    assert hasattr(orcamento, 'OrcamentoStatus')
    assert hasattr(ordem_servico, 'OrdemServico')
    
    # Tentar instanciar alguns modelos para verificar se não há erros de schema
    from app.models.estoque import ItemEstoque, TipoItem, CategoriaItem
    from decimal import Decimal
    
    # Criar instância mínima de ItemEstoque
    item = ItemEstoque(
        codigo="TEST001",
        nome="Item de Teste",
        tipo=TipoItem.PECA_HARDWARE,
        categoria=CategoriaItem.PROCESSADOR,
        preco_custo=Decimal("10.00"),
        preco_venda=Decimal("20.00")
    )
    
    # Verificar se os campos Decimal foram processados corretamente
    assert isinstance(item.preco_custo, Decimal)
    assert isinstance(item.preco_venda, Decimal)
    assert isinstance(item.margem_lucro, Decimal)