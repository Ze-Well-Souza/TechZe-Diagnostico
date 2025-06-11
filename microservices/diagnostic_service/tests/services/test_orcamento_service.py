"""
Testes unitários para OrcamentoService
Testa a lógica de negócio de orçamentos
"""

import pytest
import asyncio
from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch

from app.services.orcamento_service import OrcamentoService
from app.models.orcamento import (
    OrcamentoCreate, OrcamentoUpdate, OrcamentoFiltros,
    StatusOrcamento, PrioridadeOrcamento, DadosCliente,
    DadosEquipamento, ItemOrcamento, PecaOrcamento,
    CondicoesPagamento
)
from app.db.repositories.orcamento_repository import OrcamentoRepository


@pytest.fixture
def mock_repository():
    """Fixture para repository mockado"""
    return Mock(spec=OrcamentoRepository)


@pytest.fixture
def orcamento_service(mock_repository):
    """Fixture para OrcamentoService com repository mockado"""
    service = OrcamentoService()
    service.repository = mock_repository
    return service


@pytest.fixture
def dados_cliente():
    """Fixture para dados de cliente"""
    return DadosCliente(
        nome="João Silva",
        cpf="123.456.789-00",
        telefone="(11) 99999-8888",
        email="joao@email.com",
        endereco={
            "logradouro": "Rua A, 123",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "uf": "SP",
            "cep": "01000-000"
        }
    )


@pytest.fixture
def dados_equipamento():
    """Fixture para dados de equipamento"""
    return DadosEquipamento(
        tipo="notebook",
        marca="Dell",
        modelo="Inspiron 15",
        numero_serie="ABC123",
        descricao_problema="Notebook não liga"
    )


@pytest.fixture
def itens_orcamento():
    """Fixture para itens de orçamento"""
    return [
        ItemOrcamento(
            tipo="diagnostico",
            descricao="Diagnóstico completo",
            quantidade=1,
            valor_unitario=Decimal("50.00"),
            tempo_estimado=60
        ),
        ItemOrcamento(
            tipo="servico",
            descricao="Limpeza e manutenção",
            quantidade=1,
            valor_unitario=Decimal("80.00"),
            tempo_estimado=120
        )
    ]


@pytest.fixture
def pecas_orcamento():
    """Fixture para peças de orçamento"""
    return [
        PecaOrcamento(
            codigo_peca="HD-001",
            nome_peca="HD SATA 1TB",
            quantidade=1,
            valor_unitario=Decimal("320.00")
        )
    ]


@pytest.fixture
def condicoes_pagamento():
    """Fixture para condições de pagamento"""
    return CondicoesPagamento(
        forma_pagamento="dinheiro",
        prazo_dias=30,
        desconto_percentual=0.0,
        observacoes="Pagamento à vista"
    )


@pytest.fixture
def orcamento_create(dados_cliente, dados_equipamento, itens_orcamento, 
                    pecas_orcamento, condicoes_pagamento):
    """Fixture para dados de criação de orçamento"""
    return OrcamentoCreate(
        cliente=dados_cliente,
        equipamento=dados_equipamento,
        itens=itens_orcamento,
        pecas=pecas_orcamento,
        condicoes_pagamento=condicoes_pagamento,
        observacoes="Orçamento de teste",
        prioridade=PrioridadeOrcamento.NORMAL
    )


class TestOrcamentoService:
    """Testes para OrcamentoService"""
    
    @pytest.mark.asyncio
    async def test_criar_orcamento_sucesso(self, orcamento_service, mock_repository, orcamento_create):
        """Testa criação de orçamento com sucesso"""
        # Arrange
        mock_repository.gerar_proximo_numero.return_value = "ORC-202501-0001"
        mock_repository.create.return_value = Mock(
            id="test-id",
            numero="ORC-202501-0001",
            status=StatusOrcamento.PENDENTE
        )
        
        # Act
        resultado = await orcamento_service.criar_orcamento(orcamento_create)
        
        # Assert
        assert resultado is not None
        assert resultado.numero == "ORC-202501-0001"
        assert resultado.status == StatusOrcamento.PENDENTE
        mock_repository.gerar_proximo_numero.assert_called_once()
        mock_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_calcular_valor_total_correto(self, orcamento_service, itens_orcamento, pecas_orcamento):
        """Testa cálculo correto do valor total"""
        # Arrange
        valor_esperado = Decimal("450.00")  # 50 + 80 + 320
        
        # Act
        valor_calculado = orcamento_service._calcular_valor_total(itens_orcamento + pecas_orcamento)
        
        # Assert
        assert valor_calculado == valor_esperado
    
    @pytest.mark.asyncio
    async def test_aplicar_desconto_correto(self, orcamento_service):
        """Testa aplicação de desconto"""
        # Arrange
        valor_original = Decimal("100.00")
        desconto_percentual = 10.0
        valor_esperado = Decimal("10.00")
        
        # Act
        desconto_calculado = orcamento_service._aplicar_desconto(valor_original, desconto_percentual)
        
        # Assert
        assert desconto_calculado == valor_esperado
    
    @pytest.mark.asyncio
    async def test_buscar_orcamento_existente(self, orcamento_service, mock_repository):
        """Testa busca de orçamento existente"""
        # Arrange
        orcamento_id = "test-id"
        mock_orcamento = Mock(id=orcamento_id, numero="ORC-202501-0001")
        mock_repository.get_by_id.return_value = mock_orcamento
        
        # Act
        resultado = await orcamento_service.buscar_orcamento(orcamento_id)
        
        # Assert
        assert resultado == mock_orcamento
        mock_repository.get_by_id.assert_called_once_with(orcamento_id)
    
    @pytest.mark.asyncio
    async def test_buscar_orcamento_inexistente(self, orcamento_service, mock_repository):
        """Testa busca de orçamento inexistente"""
        # Arrange
        orcamento_id = "id-inexistente"
        mock_repository.get_by_id.return_value = None
        
        # Act
        resultado = await orcamento_service.buscar_orcamento(orcamento_id)
        
        # Assert
        assert resultado is None
        mock_repository.get_by_id.assert_called_once_with(orcamento_id)
    
    @pytest.mark.asyncio
    async def test_listar_orcamentos_com_filtros(self, orcamento_service, mock_repository):
        """Testa listagem de orçamentos com filtros"""
        # Arrange
        filtros = OrcamentoFiltros(
            status=StatusOrcamento.PENDENTE,
            data_inicio=date.today() - timedelta(days=30),
            data_fim=date.today()
        )
        mock_orcamentos = [Mock(id="1"), Mock(id="2")]
        mock_repository.listar_com_filtros.return_value = mock_orcamentos
        
        # Act
        resultado = await orcamento_service.listar_orcamentos(filtros)
        
        # Assert
        assert len(resultado) == 2
        mock_repository.listar_com_filtros.assert_called_once_with(filtros)
    
    @pytest.mark.asyncio
    async def test_aprovar_orcamento_sucesso(self, orcamento_service, mock_repository):
        """Testa aprovação de orçamento"""
        # Arrange
        orcamento_id = "test-id"
        assinatura = "assinatura-digital"
        ip_cliente = "192.168.1.1"
        
        mock_repository.aprovar_orcamento.return_value = True
        
        # Act
        resultado = await orcamento_service.aprovar_orcamento(
            orcamento_id, assinatura, ip_cliente
        )
        
        # Assert
        assert resultado is True
        mock_repository.aprovar_orcamento.assert_called_once_with(
            orcamento_id, assinatura, ip_cliente
        )
    
    @pytest.mark.asyncio
    async def test_rejeitar_orcamento_sucesso(self, orcamento_service, mock_repository):
        """Testa rejeição de orçamento"""
        # Arrange
        orcamento_id = "test-id"
        mock_repository.rejeitar_orcamento.return_value = True
        
        # Act
        resultado = await orcamento_service.rejeitar_orcamento(orcamento_id)
        
        # Assert
        assert resultado is True
        mock_repository.rejeitar_orcamento.assert_called_once_with(orcamento_id)
    
    @pytest.mark.asyncio
    async def test_gerar_numero_orcamento_formato_correto(self, orcamento_service, mock_repository):
        """Testa geração de número de orçamento com formato correto"""
        # Arrange
        numero_esperado = "ORC-202501-0001"
        mock_repository.gerar_proximo_numero.return_value = numero_esperado
        
        # Act
        numero_gerado = await mock_repository.gerar_proximo_numero()
        
        # Assert
        assert numero_gerado == numero_esperado
        assert numero_gerado.startswith("ORC-")
        partes = numero_gerado.split("-")
        assert len(partes) == 3
        assert len(partes[1]) == 6  # YYYYMM
        assert len(partes[2]) == 4  # NNNN
    
    @pytest.mark.asyncio
    async def test_atualizar_orcamento_sucesso(self, orcamento_service, mock_repository):
        """Testa atualização de orçamento"""
        # Arrange
        orcamento_id = "test-id"
        dados_atualizacao = OrcamentoUpdate(
            observacoes="Observações atualizadas",
            prioridade=PrioridadeOrcamento.ALTA
        )
        
        mock_orcamento_original = Mock(
            id=orcamento_id,
            status=StatusOrcamento.PENDENTE,
            itens=[],
            pecas=[],
            condicoes_pagamento=Mock(desconto_percentual=0.0)
        )
        
        mock_repository.get_by_id.return_value = mock_orcamento_original
        mock_repository.update.return_value = mock_orcamento_original
        
        # Act
        resultado = await orcamento_service.atualizar_orcamento(orcamento_id, dados_atualizacao)
        
        # Assert
        assert resultado is not None
        mock_repository.get_by_id.assert_called_once_with(orcamento_id)
        mock_repository.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_buscar_orcamentos_vencidos(self, orcamento_service, mock_repository):
        """Testa busca de orçamentos vencidos"""
        # Arrange
        mock_orcamentos_vencidos = [Mock(id="1"), Mock(id="2")]
        mock_repository.buscar_vencidos.return_value = mock_orcamentos_vencidos
        
        # Act
        resultado = await orcamento_service.buscar_orcamentos_vencidos()
        
        # Assert
        assert len(resultado) == 2
        mock_repository.buscar_vencidos.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_gerar_relatorio_orcamentos(self, orcamento_service, mock_repository):
        """Testa geração de relatório de orçamentos"""
        # Arrange
        data_inicio = date.today() - timedelta(days=30)
        data_fim = date.today()
        
        mock_estatisticas = {
            "total_orcamentos": 10,
            "aprovados": 7,
            "pendentes": 2,
            "rejeitados": 1,
            "valor_total": 5000.0,
            "taxa_aprovacao": 70.0
        }
        
        mock_repository.estatisticas_periodo.return_value = mock_estatisticas
        
        # Act
        resultado = await orcamento_service.gerar_relatorio_orcamentos(data_inicio, data_fim)
        
        # Assert
        assert resultado["total_orcamentos"] == 10
        assert resultado["taxa_aprovacao"] == 70.0
        mock_repository.estatisticas_periodo.assert_called_once_with(data_inicio, data_fim)
    
    @pytest.mark.asyncio
    async def test_validar_orcamento_valido(self, orcamento_service, orcamento_create):
        """Testa validação de orçamento válido"""
        # Act
        resultado = orcamento_service._validar_orcamento(orcamento_create)
        
        # Assert
        assert resultado is True
    
    @pytest.mark.asyncio
    async def test_validar_orcamento_sem_itens(self, orcamento_service, orcamento_create):
        """Testa validação de orçamento sem itens"""
        # Arrange
        orcamento_create.itens = []
        orcamento_create.pecas = []
        
        # Act & Assert
        with pytest.raises(ValueError, match="Orçamento deve ter pelo menos um item ou peça"):
            orcamento_service._validar_orcamento(orcamento_create)
    
    @pytest.mark.asyncio
    async def test_validar_orcamento_valor_zero(self, orcamento_service, orcamento_create):
        """Testa validação de orçamento com valor zero"""
        # Arrange
        for item in orcamento_create.itens:
            item.valor_unitario = Decimal("0.00")
        for peca in orcamento_create.pecas:
            peca.valor_unitario = Decimal("0.00")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Valor total do orçamento deve ser maior que zero"):
            orcamento_service._validar_orcamento(orcamento_create)


class TestOrcamentoServiceIntegracao:
    """Testes de integração para OrcamentoService (com repository real)"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_fluxo_completo_orcamento(self, orcamento_create):
        """Testa fluxo completo de orçamento (criação, aprovação, atualização)"""
        # Este teste requer conexão real com Supabase
        # Marcar com @pytest.mark.integration para execução opcional
        
        service = OrcamentoService()
        
        # Criar orçamento
        orcamento = await service.criar_orcamento(orcamento_create)
        assert orcamento is not None
        assert orcamento.status == StatusOrcamento.PENDENTE
        
        # Buscar orçamento criado
        orcamento_encontrado = await service.buscar_orcamento(orcamento.id)
        assert orcamento_encontrado is not None
        assert orcamento_encontrado.numero == orcamento.numero
        
        # Aprovar orçamento
        aprovado = await service.aprovar_orcamento(
            orcamento.id, "assinatura-teste", "127.0.0.1"
        )
        assert aprovado is True
        
        # Verificar status atualizado
        orcamento_aprovado = await service.buscar_orcamento(orcamento.id)
        assert orcamento_aprovado.status == StatusOrcamento.APROVADO
        assert orcamento_aprovado.data_aprovacao is not None


# Configuração para execução dos testes
if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 