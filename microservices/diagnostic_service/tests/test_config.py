"""
Test suite for TechZe Diagnostic Service Configuration
Testes abrangentes para configuração do sistema
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from app.core.config import (
    Settings, 
    DatabaseSettings, 
    SecuritySettings, 
    get_settings
)


class TestDatabaseSettings:
    """Test database configuration settings."""
    
    def test_database_settings_defaults(self):
        """Test default database settings."""
        db_settings = DatabaseSettings()
        
        assert db_settings.SUPABASE_URL is None
        assert db_settings.DATABASE_URL is None
        assert db_settings.DB_POOL_SIZE == 10
        assert db_settings.DB_MAX_OVERFLOW == 20
        assert db_settings.DB_POOL_TIMEOUT == 30
    
    @patch.dict(os.environ, {
        'DB_SUPABASE_URL': 'https://test.supabase.co',
        'DB_DATABASE_URL': 'postgresql://test:test@localhost/test',
        'DB_POOL_SIZE': '20'
    })
    def test_database_settings_from_env(self):
        """Test database settings from environment variables."""
        db_settings = DatabaseSettings()
        
        assert db_settings.SUPABASE_URL == 'https://test.supabase.co'
        assert db_settings.DATABASE_URL == 'postgresql://test:test@localhost/test'
        assert db_settings.DB_POOL_SIZE == 20


class TestSecuritySettings:
    """Test security configuration settings."""
    
    def test_security_settings_defaults(self):
        """Test default security settings."""
        security_settings = SecuritySettings()
        
        assert security_settings.JWT_ALGORITHM == "HS256"
        assert security_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert security_settings.RATE_LIMIT_ENABLED is True
        assert security_settings.RATE_LIMIT_PER_MINUTE == 60
        assert len(security_settings.SECRET_KEY) > 0
        assert "localhost:3000" in security_settings.CORS_ORIGINS
    
    @patch.dict(os.environ, {
        'SECURITY_SECRET_KEY': 'test-secret-key',
        'SECURITY_RATE_LIMIT_PER_MINUTE': '100'
    })
    def test_security_settings_from_env(self):
        """Test security settings from environment variables."""
        security_settings = SecuritySettings()
        
        assert security_settings.SECRET_KEY == 'test-secret-key'
        assert security_settings.RATE_LIMIT_PER_MINUTE == 100


class TestMainSettings:
    """Test main application settings."""
    
    def test_settings_defaults(self):
        """Test default application settings."""
        settings = Settings()
        
        assert settings.PROJECT_NAME == "TechZe Diagnostic API"
        assert settings.VERSION == "1.0.0"
        assert settings.API_V1_STR == "/api/v1"
        assert settings.API_V3_STR == "/api/v3"
        assert settings.ENVIRONMENT == "production"
        assert settings.DEBUG is False
        assert settings.HOST == "0.0.0.0"
        assert settings.PORT == 8000  # Default when PORT env var not set
    
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
        
        # Invalid environment should raise error
        with pytest.raises(ValueError, match="ENVIRONMENT must be one of"):
            Settings(ENVIRONMENT="invalid")
    
    def test_debug_auto_configuration(self):
        """Test automatic DEBUG configuration based on environment."""
        # Development should enable debug
        dev_settings = Settings(ENVIRONMENT="development")
        assert dev_settings.DEBUG is True
        
        # Production should disable debug
        prod_settings = Settings(ENVIRONMENT="production")
        assert prod_settings.DEBUG is False
    
    def test_legacy_settings_migration(self):
        """Test migration of legacy environment variables."""
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://legacy.supabase.co',
            'SUPABASE_KEY': 'legacy-key',
            'SECRET_KEY': 'legacy-secret'
        }):
            settings = Settings()
            
            # Legacy values should be migrated to new structure
            assert settings.database.SUPABASE_URL == 'https://legacy.supabase.co'
            assert settings.database.SUPABASE_ANON_KEY == 'legacy-key'
            assert settings.security.SECRET_KEY == 'legacy-secret'
    
    def test_is_development_property(self):
        """Test is_development property."""
        dev_settings = Settings(ENVIRONMENT="development")
        prod_settings = Settings(ENVIRONMENT="production")
        
        assert dev_settings.is_development is True
        assert prod_settings.is_development is False
    
    def test_is_production_property(self):
        """Test is_production property."""
        dev_settings = Settings(ENVIRONMENT="development")
        prod_settings = Settings(ENVIRONMENT="production")
        
        assert dev_settings.is_production is False
        assert prod_settings.is_production is True
    
    def test_get_cors_origins(self):
        """Test CORS origins processing."""
        dev_settings = Settings(ENVIRONMENT="development")
        prod_settings = Settings(ENVIRONMENT="production")
        
        # Development should include additional localhost origins
        dev_origins = dev_settings.get_cors_origins()
        assert "http://localhost" in dev_origins
        assert "http://127.0.0.1" in dev_origins
        
        # Production should only include explicitly configured origins
        prod_origins = prod_settings.get_cors_origins()
        assert len(prod_origins) == len(prod_settings.security.CORS_ORIGINS)


class TestSettingsFactory:
    """Test settings factory and caching."""
    
    def test_get_settings_returns_same_instance(self):
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()
        
        # Should return the same instance (cached)
        assert settings1 is settings2
    
    def test_settings_singleton_behavior(self):
        """Test singleton behavior of settings."""
        from microservices.diagnostic_service.app.core.config import settings
        
        settings1 = get_settings()
        
        # Global settings instance should be same as factory result
        assert settings is settings1


class TestConfigurationIntegration:
    """Integration tests for configuration system."""
    
    @patch.dict(os.environ, {
        'ENVIRONMENT': 'development',
        'PORT': '3001',
        'DB_SUPABASE_URL': 'https://dev.supabase.co',
        'SECURITY_SECRET_KEY': 'dev-secret-key',
        'SENTRY_DSN': 'https://sentry.io/dev'
    })
    def test_full_configuration_integration(self):
        """Test full configuration with multiple environment variables."""
        settings = Settings()
        
        # Main settings
        assert settings.ENVIRONMENT == "development"
        assert settings.DEBUG is True
        assert settings.PORT == 3001
        
        # Database settings
        assert settings.database.SUPABASE_URL == 'https://dev.supabase.co'
        
        # Security settings
        assert settings.security.SECRET_KEY == 'dev-secret-key'
        
        # Monitoring settings
        assert settings.SENTRY_DSN == 'https://sentry.io/dev'
        
        # Properties
        assert settings.is_development is True
        assert settings.is_production is False
    
    def test_configuration_error_handling(self):
        """Test configuration error handling."""
        # Test with invalid environment
        with pytest.raises(ValueError):
            Settings(ENVIRONMENT="invalid")
    
    def test_configuration_backwards_compatibility(self):
        """Test backwards compatibility with legacy configuration."""
        # Create settings with mix of old and new env vars
        with patch.dict(os.environ, {
            'SUPABASE_URL': 'https://old.supabase.co',
            'DB_SUPABASE_URL': 'https://new.supabase.co',  # New should take precedence
            'SECRET_KEY': 'old-secret'
        }):
            settings = Settings()
            
            # New env vars should take precedence
            assert settings.database.SUPABASE_URL == 'https://new.supabase.co'
            
            # Legacy should be used if new doesn't exist
            assert settings.security.SECRET_KEY == 'old-secret'


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
    settings = Settings()
    
    # Should have default values
    assert settings.ENVIRONMENT == "production"
    assert settings.PORT == 8000
    assert settings.DEBUG is False 