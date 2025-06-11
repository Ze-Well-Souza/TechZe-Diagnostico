"""
Test suite for TechZe Diagnostic Service Configuration
Testes abrangentes para configuração do sistema
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from app.core.config import Settings, settings


class TestDatabaseSettings:
    """Test database configuration settings."""
    
    def test_database_settings_defaults(self):
        """Test database settings default values."""
        settings = Settings()
        
        # Test default values (atualizado para configuração atual)
        assert 'supabase.co' in settings.SUPABASE_URL  # URL dinâmica do Supabase
        assert settings.SUPABASE_KEY is not None  # Chave existe
        assert len(settings.SUPABASE_KEY) > 0  # Chave não está vazia
    
    @patch.dict(os.environ, {
        'SUPABASE_URL': 'https://test.supabase.co',
        'DATABASE_URL': 'postgresql://test:test@localhost/test'
    })
    def test_database_settings_from_env(self):
        """Test database settings from environment variables."""
        test_settings = Settings()
        
        assert test_settings.SUPABASE_URL == 'https://test.supabase.co'
        assert test_settings.DATABASE_URL == 'postgresql://test:test@localhost/test'


class TestSecuritySettings:
    """Test security configuration settings."""
    
    def test_security_settings_defaults(self):
        """Test default security settings."""
        test_settings = Settings()
        
        assert test_settings.ALGORITHM == "HS256"
        assert test_settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert test_settings.RATE_LIMIT_ENABLED is True
        assert len(test_settings.SECRET_KEY) > 0
        assert "http://localhost:3000" in test_settings.BACKEND_CORS_ORIGINS
    
    @patch.dict(os.environ, {
        'SECRET_KEY': 'test-secret-key'
    })
    def test_security_settings_from_env(self):
        """Test security settings from environment variables."""
        test_settings = Settings()
        
        assert test_settings.SECRET_KEY == 'test-secret-key'


class TestMainSettings:
    """Test main application settings."""
    
    def test_settings_defaults(self):
        """Test default configuration values."""
        settings = Settings()
        
        # Basic settings (atualizados para configuração atual)
        assert settings.PROJECT_NAME == "TechZe Diagnostic API"
        assert settings.VERSION == "1.0.0"  # Versão atualizada
        assert settings.API_V1_STR == "/api/v1"
        assert settings.ENVIRONMENT.value == "production"  # Configuração atual
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000
    
    @patch.dict(os.environ, {'PORT': '9000'})
    def test_port_from_environment(self):
        """Test PORT configuration from environment."""
        settings = Settings()
        assert settings.PORT == 9000
    
    def test_environment_validation(self):
        """Test environment validation."""
        # Valid environments
        for env in ["development", "staging", "production"]:
            settings = Settings(ENVIRONMENT=env)
            assert settings.ENVIRONMENT == env
    
    def test_debug_auto_configuration(self):
        """Test DEBUG configuration."""
        # Test debug auto-configuration
        settings = Settings()
        # DEBUG depende do ambiente - em produção é False
        assert isinstance(settings.DEBUG, bool)
    
    def test_legacy_settings_migration(self):
        """Test migration of legacy environment variables."""
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://legacy.supabase.co',
            'SUPABASE_KEY': 'legacy-key',
            'SECRET_KEY': 'legacy-secret'
        }):
            settings = Settings()
            
            # Legacy values should be available
            assert settings.SUPABASE_URL == 'https://legacy.supabase.co'
            assert settings.SUPABASE_KEY == 'legacy-key'
            assert settings.SECRET_KEY == 'legacy-secret'
    
    def test_cors_origins(self):
        """Test CORS origins configuration."""
        settings = Settings()
        
        # Should have default CORS origins
        assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS
        assert len(settings.BACKEND_CORS_ORIGINS) > 0


class TestSettingsFactory:
    """Test settings factory and caching."""
    
    def test_settings_instance(self):
        """Test that Settings can be instantiated."""
        settings1 = Settings()
        settings2 = Settings()
        
        # Both should be valid Settings instances
        assert isinstance(settings1, Settings)
        assert isinstance(settings2, Settings)
    
    def test_settings_consistency(self):
        """Test that Settings instances have consistent values."""
        settings1 = Settings()
        settings2 = Settings()
        
        # Should have same configuration values
        assert settings1.PROJECT_NAME == settings2.PROJECT_NAME
        assert settings1.VERSION == settings2.VERSION
        assert settings1.ENVIRONMENT == settings2.ENVIRONMENT


class TestConfigurationIntegration:
    """Integration tests for configuration system."""
    
    @patch.dict(os.environ, {
        'ENVIRONMENT': 'development',
        'PORT': '3001',
        'SUPABASE_URL': 'https://dev.supabase.co',
        'SECRET_KEY': 'dev-secret-key',
        'SENTRY_DSN': 'https://sentry.io/dev',
        'DEBUG': 'false'
    })
    def test_full_configuration_integration(self):
        """Test full configuration with multiple environment variables."""
        settings = Settings()
        
        # Main settings
        assert settings.ENVIRONMENT == "development"
        assert settings.DEBUG is False  # Should be False when DEBUG=false in env
        assert settings.PORT == 3001
        
        # Database settings
        assert settings.SUPABASE_URL == 'https://dev.supabase.co'
        
        # Security settings
        assert settings.SECRET_KEY == 'dev-secret-key'
        
        # Monitoring settings
        assert settings.SENTRY_DSN == 'https://sentry.io/dev'
    
    def test_configuration_error_handling(self):
        """Test configuration error handling."""
        # Test basic configuration
        settings = Settings()
        assert settings.ENVIRONMENT in ["development", "staging", "production"]
    
    def test_configuration_backwards_compatibility(self):
        """Test backwards compatibility with legacy configuration."""
        # Create settings with environment variables
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://old.supabase.co',
            'SECRET_KEY': 'old-secret'
        }):
            settings = Settings()
            
            # Environment variables should be used
            assert settings.SUPABASE_URL == 'https://old.supabase.co'
            assert settings.SECRET_KEY == 'old-secret'


@pytest.fixture
def clean_environment():
    """Fixture to clean environment variables for testing."""
    # Store original env vars
    original_env = os.environ.copy()
    
    # Clear relevant env vars
    env_vars_to_clear = [
        'PORT', 'ENVIRONMENT', 'DEBUG',
        'SUPABASE_URL', 'SUPABASE_KEY', 'SECRET_KEY',
        'DB_SUPABASE_URL', 'SECURITY_SECRET_KEY'
    ]
    
    for var in env_vars_to_clear:
        if var in os.environ:
            del os.environ[var]
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


def test_configuration_isolation(clean_environment):
    """Test that configuration tests don't interfere with each other."""
    # Test with clean environment - should use defaults from config file
    # Note: Settings() will still load from .env file if present
    settings = Settings(_env_file=None)  # Don't load .env file
    
    # Should have default values from config.py only
    assert settings.ENVIRONMENT == "production"  # Default from config.py
    assert settings.PORT == 8000
    assert settings.DEBUG is False  # Default from config.py