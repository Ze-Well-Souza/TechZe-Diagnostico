import pytest
from unittest.mock import Mock, patch, MagicMock
import platform
import json
from app.services.analyzers.driver_analyzer import DriverAnalyzer


class TestDriverAnalyzer:
    """Testes unitários para o DriverAnalyzer."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.analyzer = DriverAnalyzer()
    
    def test_analyze_success(self):
        """Testa análise bem-sucedida dos drivers."""
        mock_drivers = [
            {"name": "Intel HD Graphics", "version": "27.20.100.9268", "manufacturer": "Intel", "date": "2023-01-15", "signed": True, "status": "ok"},
            {"name": "Realtek Audio", "version": "6.0.9200.1", "manufacturer": "Realtek", "date": "2023-02-20", "signed": True, "status": "ok"}
        ]
        
        with patch.object(self.analyzer, '_get_drivers_info', return_value=mock_drivers), \
             patch.object(self.analyzer, '_identify_problematic_drivers', return_value=[]), \
             patch.object(self.analyzer, '_identify_outdated_drivers', return_value=[]):
            
            result = self.analyzer.analyze()
            
            assert result['status'] == 'healthy'
            assert result['total_drivers'] == 2
            assert result['problematic_drivers'] == 0
            assert result['outdated_drivers'] == 0
            assert 'drivers_info' in result
    
    def test_analyze_error_handling(self):
        """Testa tratamento de erros durante análise."""
        with patch.object(self.analyzer, '_get_drivers_info', side_effect=Exception("Erro de teste")):
            result = self.analyzer.analyze()
            
            assert result['status'] == 'error'
            assert 'error_message' in result
    
    def test_get_drivers_info_windows(self):
        """Testa obtenção de informações de drivers no Windows."""
        with patch('platform.system', return_value="Windows"), \
             patch.object(self.analyzer, '_get_windows_drivers', return_value=[
                 {"name": "Intel HD Graphics", "version": "27.20.100.9268", "manufacturer": "Intel", "date": "2023-01-15", "signed": True}
             ]):
            
            result = self.analyzer._get_drivers_info()
            
            assert len(result) == 1
            assert result[0]['name'] == 'Intel HD Graphics'
    
    def test_get_drivers_info_linux(self):
        """Testa obtenção de informações de drivers no Linux."""
        with patch('platform.system', return_value="Linux"), \
             patch.object(self.analyzer, '_get_linux_drivers', return_value=[
                 {"name": "i915", "version": "5.15.0", "status": "ok"}
             ]):
            
            result = self.analyzer._get_drivers_info()
            
            assert len(result) == 1
            assert result[0]['name'] == 'i915'
    
    def test_get_windows_drivers(self):
        """Testa obtenção de drivers no Windows."""
        if platform.system() == "Windows":
            mock_process = Mock()
            mock_process.returncode = 0
            mock_process.stdout = json.dumps([
                {"DeviceName": "Intel HD Graphics", "DriverVersion": "27.20.100.9268", 
                 "Manufacturer": "Intel", "DriverDate": "\/Date(1673740800000)\/", "IsSigned": True}
            ])
            
            with patch('subprocess.run', return_value=mock_process):
                result = self.analyzer._get_windows_drivers()
                
                assert len(result) == 1
                assert result[0]['name'] == 'Intel HD Graphics'
                assert 'version' in result[0]
                assert 'manufacturer' in result[0]
    
    def test_identify_problematic_drivers(self):
        """Testa identificação de drivers problemáticos."""
        drivers = [
            {"name": "Intel HD Graphics", "status": "ok"},
            {"name": "Problematic Driver", "status": "error"}
        ]
        
        result = self.analyzer._identify_problematic_drivers(drivers)
        
        assert len(result) == 1
        assert result[0]['name'] == 'Problematic Driver'
    
    def test_identify_outdated_drivers(self):
        """Testa identificação de drivers desatualizados."""
        drivers = [
            {"name": "Intel HD Graphics", "signed": True},
            {"name": "Unsigned Driver", "signed": False}
        ]
        
        with patch('platform.system', return_value="Windows"):
            result = self.analyzer._identify_outdated_drivers(drivers)
            
            assert len(result) == 1
            assert result[0]['name'] == 'Unsigned Driver'
            assert 'outdated_reason' in result[0]
    
    def test_determine_driver_status_healthy(self):
        """Testa determinação de status saudável."""
        drivers = [{"name": "Driver 1"}, {"name": "Driver 2"}]
        problematic = []
        outdated = []
        
        status = self.analyzer._determine_driver_status(drivers, problematic, outdated)
        
        assert status == 'healthy'
    
    def test_determine_driver_status_warning(self):
        """Testa determinação de status de aviso."""
        drivers = [{"name": "Driver 1"}, {"name": "Driver 2"}, {"name": "Driver 3"}]
        problematic = []
        outdated = [{"name": "Driver 3"}]
        
        status = self.analyzer._determine_driver_status(drivers, problematic, outdated)
        
        assert status == 'warning'
    
    def test_determine_driver_status_critical(self):
        """Testa determinação de status crítico."""
        drivers = [{"name": "Driver 1"}, {"name": "Driver 2"}, {"name": "Driver 3"}]
        problematic = [{"name": "Driver 2"}, {"name": "Driver 3"}]
        outdated = []
        
        status = self.analyzer._determine_driver_status(drivers, problematic, outdated)
        
        assert status == 'critical'