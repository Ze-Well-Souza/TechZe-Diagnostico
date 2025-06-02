import pytest
from unittest.mock import Mock, patch, MagicMock
import platform
from app.services.analyzers.cpu_analyzer import CPUAnalyzer


class TestCPUAnalyzer:
    """Testes unitários para o CPUAnalyzer."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.analyzer = CPUAnalyzer()
    
    def test_analyze_success(self):
        """Testa análise bem-sucedida do CPU."""
        with patch.object(self.analyzer, '_get_cpu_usage', return_value=45.0), \
             patch.object(self.analyzer, '_get_cpu_temperature', return_value=65.0), \
             patch.object(self.analyzer, '_get_cpu_info', return_value={
                 'physical_cores': 4,
                 'logical_cores': 8,
                 'architecture': 'x86_64',
                 'processor': 'Intel Core i7'
             }), \
             patch.object(self.analyzer, '_get_cpu_load', return_value={'1min': 1.5, '5min': 1.2, '15min': 1.0}), \
             patch.object(self.analyzer, '_get_cpu_frequency', return_value={'current': 2400.0, 'min': 800.0, 'max': 3600.0}):
            
            result = self.analyzer.analyze()
            
            assert result['status'] == 'healthy'
            assert result['usage'] == 45.0
            assert result['temperature'] == 65.0
            assert 'details' in result
            assert 'load' in result
            assert 'frequency' in result
    
    def test_analyze_error_handling(self):
        """Testa tratamento de erros durante análise."""
        with patch.object(self.analyzer, '_get_cpu_usage', side_effect=Exception("Erro de teste")):
            result = self.analyzer.analyze()
            
            assert result['status'] == 'error'
            assert 'error_message' in result
    
    @patch('psutil.cpu_percent')
    def test_get_cpu_usage(self, mock_cpu_percent):
        """Testa obtenção do uso de CPU."""
        mock_cpu_percent.return_value = 75.5
        
        usage = self.analyzer._get_cpu_usage()
        
        assert usage == 75.5
        mock_cpu_percent.assert_called_once_with(interval=1)
    
    @patch('psutil.cpu_percent')
    def test_get_cpu_usage_error(self, mock_cpu_percent):
        """Testa tratamento de erro na obtenção do uso de CPU."""
        mock_cpu_percent.side_effect = Exception("Erro psutil")
        
        usage = self.analyzer._get_cpu_usage()
        
        assert usage == 0.0
    
    def test_get_cpu_temperature_with_sensors(self):
        """Testa obtenção de temperatura com sensores disponíveis."""
        mock_temp = MagicMock()
        mock_temp.current = 68.5
        
        # Verifica se sensors_temperatures existe antes de fazer o patch
        if hasattr(__import__('psutil'), 'sensors_temperatures'):
            with patch('psutil.sensors_temperatures', return_value={
                'coretemp': [mock_temp]
            }):
                temp = self.analyzer._get_cpu_temperature()
                assert temp == 68.5
        else:
            # No Windows, simula o comportamento
            with patch.object(self.analyzer, '_get_cpu_usage', return_value=50.0):
                temp = self.analyzer._get_cpu_temperature()
                assert isinstance(temp, float)
                assert 30.0 <= temp <= 90.0
    
    def test_get_cpu_temperature_simulated(self):
        """Testa temperatura simulada quando sensores não estão disponíveis."""
        # Verifica se sensors_temperatures existe antes de fazer o patch
        if hasattr(__import__('psutil'), 'sensors_temperatures'):
            with patch('psutil.sensors_temperatures', return_value={}), \
                 patch.object(self.analyzer, '_get_cpu_usage', return_value=50.0):
                temp = self.analyzer._get_cpu_temperature()
                assert isinstance(temp, float)
                assert 30.0 <= temp <= 90.0
        else:
            # No Windows, sempre usa simulação
            with patch.object(self.analyzer, '_get_cpu_usage', return_value=50.0):
                temp = self.analyzer._get_cpu_temperature()
                assert isinstance(temp, float)
                assert 30.0 <= temp <= 90.0
    
    @patch('psutil.cpu_count')
    @patch('platform.machine')
    @patch('platform.processor')
    def test_get_cpu_info(self, mock_processor, mock_machine, mock_cpu_count):
        """Testa obtenção de informações do CPU."""
        mock_processor.return_value = "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel"
        mock_machine.return_value = "AMD64"
        mock_cpu_count.side_effect = [8, 16]  # physical, logical
        
        info = self.analyzer._get_cpu_info()
        
        assert info['physical_cores'] == 8
        assert info['logical_cores'] == 16
        assert info['architecture'] == "AMD64"
        assert 'processor' in info
    
    @patch('platform.system')
    @patch('psutil.getloadavg')
    def test_get_cpu_load_linux(self, mock_getloadavg, mock_system):
        """Testa obtenção de carga do CPU no Linux."""
        mock_system.return_value = 'Linux'
        mock_getloadavg.return_value = (1.5, 1.2, 1.0)
        
        load = self.analyzer._get_cpu_load()
        
        assert load['1min'] == 1.5
        assert load['5min'] == 1.2
        assert load['15min'] == 1.0
    
    @patch('platform.system')
    @patch('psutil.cpu_percent')
    def test_get_cpu_load_windows(self, mock_cpu_percent, mock_system):
        """Testa obtenção de carga do CPU no Windows."""
        mock_system.return_value = 'Windows'
        mock_cpu_percent.return_value = 45.0
        
        load = self.analyzer._get_cpu_load()
        
        assert load['current'] == 0.45  # 45.0 / 100.0
    
    @patch('psutil.cpu_freq')
    def test_get_cpu_frequency(self, mock_cpu_freq):
        """Testa obtenção da frequência do CPU."""
        mock_freq = MagicMock()
        mock_freq.current = 2400.0
        mock_freq.min = 800.0
        mock_freq.max = 3600.0
        mock_cpu_freq.return_value = mock_freq
        
        freq = self.analyzer._get_cpu_frequency()
        
        assert freq['current'] == 2400.0
        assert freq['min'] == 800.0
        assert freq['max'] == 3600.0
    
    def test_determine_status_healthy(self):
        """Testa determinação de status saudável."""
        status = self.analyzer._determine_status(usage=45.0, temperature=65.0)
        assert status == 'healthy'
    
    def test_determine_status_warning(self):
        """Testa determinação de status de aviso."""
        status = self.analyzer._determine_status(usage=85.0, temperature=75.0)
        assert status == 'warning'
    
    def test_determine_status_critical_usage(self):
        """Testa determinação de status crítico por uso."""
        status = self.analyzer._determine_status(usage=95.0, temperature=65.0)
        assert status == 'critical'
    
    def test_determine_status_critical_temperature(self):
        """Testa determinação de status crítico por temperatura."""
        status = self.analyzer._determine_status(usage=45.0, temperature=85.0)
        assert status == 'critical'


class TestCPUAnalyzerIntegration:
    """Testes de integração para o CPUAnalyzer."""
    
    def test_real_cpu_analysis(self):
        """Testa análise real do CPU (sem mocks)."""
        analyzer = CPUAnalyzer()
        result = analyzer.analyze()
        
        # Verifica se os campos obrigatórios estão presentes
        assert 'status' in result
        assert 'usage' in result
        assert 'temperature' in result
        assert 'details' in result
        
        # Verifica se os valores são válidos
        assert result['status'] in ['healthy', 'warning', 'critical', 'error']
        assert isinstance(result['usage'], (int, float))
        assert isinstance(result['temperature'], (int, float))
        assert isinstance(result['details'], dict) 