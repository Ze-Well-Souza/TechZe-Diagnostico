import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

from app.models.diagnostic import Diagnostic, DiagnosticStatus
from app.schemas.diagnostic import DiagnosticCreate, DiagnosticUpdate
from app.services.diagnostic_service import DiagnosticService


class TestDiagnosticService:
    """Testes para o serviço de diagnóstico."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.db = Mock()
        self.service = DiagnosticService(self.db)
        
        # Mock dos analisadores
        self.service.cpu_analyzer = Mock()
        self.service.memory_analyzer = Mock()
        self.service.disk_analyzer = Mock()
        self.service.network_analyzer = Mock()
    
    def test_create_diagnostic(self):
        """Testa criação de diagnóstico."""
        # Arrange
        obj_in = DiagnosticCreate(user_id="user123", device_id="device456")
        mock_diagnostic = Mock(id="test-id")
        self.db.add = Mock()
        self.db.commit = Mock()
        self.db.refresh = Mock()
        
        # Act
        with patch("app.services.diagnostic_service.Diagnostic", return_value=mock_diagnostic):
            result = self.service.create_diagnostic(obj_in)
        
        # Assert
        assert result == mock_diagnostic
        self.db.add.assert_called_once_with(mock_diagnostic)
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(mock_diagnostic)
    
    def test_get_diagnostic(self):
        """Testa obtenção de diagnóstico pelo ID."""
        # Arrange
        diagnostic_id = "test-id"
        mock_query = Mock()
        mock_filter = Mock()
        mock_first = Mock(return_value="diagnostic-result")
        
        self.db.query = Mock(return_value=mock_query)
        mock_query.filter = Mock(return_value=mock_filter)
        mock_filter.first = mock_first
        
        # Act
        result = self.service.get_diagnostic(diagnostic_id)
        
        # Assert
        assert result == "diagnostic-result"
        self.db.query.assert_called_once_with(Diagnostic)
    
    def test_get_diagnostics(self):
        """Testa obtenção de lista de diagnósticos."""
        # Arrange
        user_id = "user123"
        device_id = "device456"
        skip = 0
        limit = 10
        
        # Criar mock chain para query
        mock_query = Mock()
        mock_filtered_query = Mock()
        
        # Configurar o comportamento da query
        self.db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filtered_query
        mock_filtered_query.filter.return_value = mock_filtered_query
        mock_filtered_query.count.return_value = 5
        mock_filtered_query.order_by.return_value = mock_filtered_query
        mock_filtered_query.offset.return_value = mock_filtered_query
        mock_filtered_query.limit.return_value = mock_filtered_query
        mock_filtered_query.all.return_value = ["diagnostic1", "diagnostic2"]
        
        # Act
        items, total = self.service.get_diagnostics(user_id, device_id, skip, limit)
        
        # Assert
        assert items == ["diagnostic1", "diagnostic2"]
        assert total == 5
        self.db.query.assert_called_once_with(Diagnostic)
    
    def test_update_diagnostic(self):
        """Testa atualização de diagnóstico."""
        # Arrange
        diagnostic_id = "test-id"
        obj_in = DiagnosticUpdate(status=DiagnosticStatus.COMPLETED)
        mock_diagnostic = Mock(id="test-id")
        
        # Act
        with patch.object(self.service, 'get_diagnostic', return_value=mock_diagnostic) as mock_get:
            result = self.service.update_diagnostic(diagnostic_id, obj_in)
        
        # Assert
        assert result == mock_diagnostic
        mock_get.assert_called_once_with(diagnostic_id)
        self.db.add.assert_called_once_with(mock_diagnostic)
        self.db.commit.assert_called_once()
        self.db.refresh.assert_called_once_with(mock_diagnostic)
    
    def test_update_diagnostic_not_found(self):
        """Testa atualização de diagnóstico não encontrado."""
        # Arrange
        diagnostic_id = "nonexistent-id"
        obj_in = DiagnosticUpdate(status=DiagnosticStatus.COMPLETED)
        
        # Act
        with patch.object(self.service, 'get_diagnostic', return_value=None) as mock_get:
            result = self.service.update_diagnostic(diagnostic_id, obj_in)
        
        # Assert
        assert result is None
        mock_get.assert_called_once_with(diagnostic_id)
        self.db.add.assert_not_called()
        self.db.commit.assert_not_called()
        self.db.refresh.assert_not_called()
    
    def test_delete_diagnostic(self):
        """Testa exclusão de diagnóstico."""
        # Arrange
        diagnostic_id = "test-id"
        mock_diagnostic = Mock(id="test-id")
        
        # Act
        with patch.object(self.service, 'get_diagnostic', return_value=mock_diagnostic) as mock_get:
            result = self.service.delete_diagnostic(diagnostic_id)
        
        # Assert
        assert result is True
        mock_get.assert_called_once_with(diagnostic_id)
        self.db.delete.assert_called_once_with(mock_diagnostic)
        self.db.commit.assert_called_once()
    
    def test_delete_diagnostic_not_found(self):
        """Testa exclusão de diagnóstico não encontrado."""
        # Arrange
        diagnostic_id = "nonexistent-id"
        
        # Act
        with patch.object(self.service, 'get_diagnostic', return_value=None) as mock_get:
            result = self.service.delete_diagnostic(diagnostic_id)
        
        # Assert
        assert result is False
        mock_get.assert_called_once_with(diagnostic_id)
        self.db.delete.assert_not_called()
        self.db.commit.assert_not_called()
    
    def test_run_diagnostic(self):
        """Testa execução de diagnóstico."""
        # Arrange
        diagnostic_id = "test-id"
        mock_diagnostic = Mock(id="test-id")
        mock_system_info = Mock(to_dict=Mock(return_value={"hostname": "test-pc"}))
        
        # Mock dos resultados dos analisadores
        cpu_result = {"status": "healthy", "usage": 30.5, "temperature": 45.0}
        memory_result = {"status": "healthy", "usage": 40.0, "available": 8192}
        disk_result = {"status": "healthy", "usage": 50.0, "available": 256000}
        network_result = {"status": "healthy", "speed": 100.0}
        
        self.service.cpu_analyzer.analyze = Mock(return_value=cpu_result)
        self.service.memory_analyzer.analyze = Mock(return_value=memory_result)
        self.service.disk_analyzer.analyze = Mock(return_value=disk_result)
        self.service.network_analyzer.analyze = Mock(return_value=network_result)
        
        # Act
        with patch.object(self.service, 'get_diagnostic', return_value=mock_diagnostic) as mock_get, \
             patch.object(self.service, 'update_diagnostic') as mock_update, \
             patch.object(self.service, '_collect_system_info', return_value=mock_system_info) as mock_collect, \
             patch.object(self.service, '_calculate_overall_health', return_value=85) as mock_calculate:
            result = self.service.run_diagnostic(diagnostic_id)
        
        # Assert
        mock_get.assert_called_once_with(diagnostic_id)
        mock_collect.assert_called_once_with(diagnostic_id)
        self.service.cpu_analyzer.analyze.assert_called_once()
        self.service.memory_analyzer.analyze.assert_called_once()
        self.service.disk_analyzer.analyze.assert_called_once()
        self.service.network_analyzer.analyze.assert_called_once()
        mock_calculate.assert_called_once_with(cpu_result, memory_result, disk_result, network_result)
        assert mock_update.call_count == 2  # Uma vez para IN_PROGRESS e outra para COMPLETED
    
    def test_run_diagnostic_not_found(self):
        """Testa execução de diagnóstico não encontrado."""
        # Arrange
        diagnostic_id = "nonexistent-id"
        
        # Act & Assert
        with patch.object(self.service, 'get_diagnostic', return_value=None) as mock_get, \
             pytest.raises(ValueError, match=f"Diagnostic not found: {diagnostic_id}"):
            self.service.run_diagnostic(diagnostic_id)
        
        mock_get.assert_called_once_with(diagnostic_id)
    
    def test_run_diagnostic_with_error(self):
        """Testa execução de diagnóstico com erro."""
        # Arrange
        diagnostic_id = "test-id"
        mock_diagnostic = Mock(id="test-id")
        
        # Act
        with patch.object(self.service, 'get_diagnostic', return_value=mock_diagnostic) as mock_get, \
             patch.object(self.service, 'update_diagnostic') as mock_update, \
             patch.object(self.service, '_collect_system_info', side_effect=Exception("Test error")) as mock_collect:
            result = self.service.run_diagnostic(diagnostic_id)
        
        # Assert
        mock_get.assert_called_once_with(diagnostic_id)
        mock_collect.assert_called_once_with(diagnostic_id)
        assert mock_update.call_count == 2  # Uma vez para IN_PROGRESS e outra para FAILED
        # Verifica se a segunda chamada de update_diagnostic tem status FAILED
        assert mock_update.call_args_list[1][1]['obj_in'].status == DiagnosticStatus.FAILED
    
    def test_collect_system_info(self):
        """Testa coleta de informações do sistema."""
        # Arrange
        diagnostic_id = "test-id"
        mock_diagnostic = Mock(id="test-id")
        mock_system_info = Mock(id="system-info-id")
        
        self.db.add = Mock()
        self.db.commit = Mock()
        self.db.refresh = Mock()
        
        # Act
        with patch("app.services.diagnostic_service.SystemInfo", return_value=mock_system_info) as mock_system_info_class, \
             patch.object(self.service, 'get_diagnostic', return_value=mock_diagnostic) as mock_get:
            result = self.service._collect_system_info(diagnostic_id)
        
        # Assert
        assert result == mock_system_info
        mock_get.assert_called_once_with(diagnostic_id)
        self.db.add.assert_called_with(mock_diagnostic)  # Chamado duas vezes, uma para system_info e outra para diagnostic
        assert self.db.commit.call_count == 2
        self.db.refresh.assert_called_once_with(mock_system_info)
    
    def test_calculate_overall_health(self):
        """Testa cálculo de saúde geral do sistema."""
        # Arrange
        cpu_result = {"status": "healthy"}
        memory_result = {"status": "warning"}
        disk_result = {"status": "healthy"}
        network_result = {"status": "warning"}
        
        # Act
        result = self.service._calculate_overall_health(cpu_result, memory_result, disk_result, network_result)
        
        # Assert
        assert isinstance(result, int)
        assert 0 <= result <= 100
        # Cálculo esperado: (100*0.3 + 60*0.25 + 100*0.25 + 60*0.2) = 82
        assert result == 82