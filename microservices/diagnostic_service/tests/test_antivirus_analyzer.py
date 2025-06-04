import pytest
from unittest.mock import Mock, patch, MagicMock
import platform
from app.services.analyzers.antivirus_analyzer import AntivirusAnalyzer


class TestAntivirusAnalyzer:
    """Testes unitários para o AntivirusAnalyzer."""
    
    def setup_method(self):
        """Setup executado antes de cada teste."""
        self.analyzer = AntivirusAnalyzer()
    
    def test_analyze_success(self):
        """Testa análise bem-sucedida do antivírus."""
        with patch.object(self.analyzer, '_get_installed_antiviruses', return_value=[
                {'name': 'Windows Defender', 'version': '4.18.2104.14', 'enabled': True}
             ]), \
             patch.object(self.analyzer, '_check_windows_defender', return_value={
                 'enabled': True,
                 'real_time_protection': True,
                 'up_to_date': True
             }), \
             patch.object(self.analyzer, '_check_firewall', return_value={
                 'enabled': True,
                 'profiles': {'domain': True, 'private': True, 'public': True},
                 'status': 'healthy'
             }), \
             patch.object(self.analyzer, '_check_real_time_protection', return_value={
                 'enabled': True,
                 'sources': ['Windows Defender']
             }):
            
            result = self.analyzer.analyze()
            
            assert result['status'] == 'healthy'
            assert len(result['installed_antiviruses']) == 1
            assert result['windows_defender']['enabled'] == True
            assert result['firewall']['enabled'] == True
            assert result['real_time_protection']['enabled'] == True
            assert 'recommendations' in result
    
    def test_analyze_error_handling(self):
        """Testa tratamento de erros durante análise."""
        with patch.object(self.analyzer, '_get_installed_antiviruses', side_effect=Exception("Erro de teste")):
            result = self.analyzer.analyze()
            
            assert result['status'] == 'error'
            assert 'error_message' in result
    
    def test_get_installed_antiviruses_windows(self):
        """Testa obtenção de antivírus instalados no Windows."""
        with patch('platform.system', return_value="Windows"), \
             patch.object(self.analyzer, '_scan_windows_antiviruses', return_value=[
                 {'name': 'Windows Defender', 'version': '4.18.2104.14', 'enabled': True}
             ]):
            
            result = self.analyzer._get_installed_antiviruses()
            
            assert len(result) == 1
            assert result[0]['name'] == 'Windows Defender'
    
    def test_get_installed_antiviruses_linux(self):
        """Testa obtenção de antivírus instalados no Linux."""
        with patch('platform.system', return_value="Linux"), \
             patch.object(self.analyzer, '_scan_linux_antiviruses', return_value=[
                 {'name': 'ClamAV', 'version': '0.103.6', 'enabled': True}
             ]):
            
            result = self.analyzer._get_installed_antiviruses()
            
            assert len(result) == 1
            assert result[0]['name'] == 'ClamAV'
    
    def test_determine_protection_status_healthy(self):
        """Testa determinação de status saudável."""
        antiviruses = [{'name': 'Windows Defender', 'enabled': True}]
        defender = {'enabled': True, 'real_time_protection': True}
        firewall = {'enabled': True}
        real_time = {'enabled': True}
        
        status = self.analyzer._determine_protection_status(antiviruses, defender, firewall, real_time)
        
        assert status == 'healthy'
    
    def test_determine_protection_status_warning(self):
        """Testa determinação de status de aviso."""
        antiviruses = [{'name': 'Windows Defender', 'enabled': True}]
        defender = {'enabled': True, 'real_time_protection': False}
        firewall = {'enabled': True}
        real_time = {'enabled': False}
        
        status = self.analyzer._determine_protection_status(antiviruses, defender, firewall, real_time)
        
        assert status == 'warning'
    
    def test_determine_protection_status_critical(self):
        """Testa determinação de status crítico."""
        antiviruses = []
        defender = {'enabled': False, 'real_time_protection': False}
        firewall = {'enabled': False}
        real_time = {'enabled': False}
        
        status = self.analyzer._determine_protection_status(antiviruses, defender, firewall, real_time)
        
        assert status == 'critical'
    
    def test_check_windows_defender_enabled(self):
        """Testa verificação do Windows Defender ativado."""
        if platform.system() == "Windows":
            with patch('winreg.OpenKey'), \
                 patch('winreg.QueryValueEx', return_value=(1, 'REG_DWORD')):
                
                result = self.analyzer._check_windows_defender()
                
                assert result['enabled'] == True
        else:
            # Em sistemas não-Windows, o método deve retornar valores padrão
            result = self.analyzer._check_windows_defender()
            assert 'enabled' in result
    
    def test_check_firewall_enabled(self):
        """Testa verificação do firewall ativado."""
        with patch.object(self.analyzer, '_check_windows_firewall', return_value={
                'enabled': True,
                'profiles': {'domain': True, 'private': True, 'public': True},
                'status': 'healthy'
            }) if platform.system() == "Windows" else patch('subprocess.run'):
            
            result = self.analyzer._check_firewall()
            
            assert 'enabled' in result
            if platform.system() == "Windows":
                assert result['enabled'] == True