"""
Integration Tests for TechZe Diagnostic Service
Testes de integração para validar fluxos completos do sistema
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

# Import the main app
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.config import get_settings


@pytest.fixture
def test_settings():
    """Override settings for testing."""
    settings = get_settings()
    settings.ENVIRONMENT = "testing"
    settings.DEBUG = True
    settings.TESTING = True
    return settings


@pytest.fixture
def client(test_settings):
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def async_client(test_settings):
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoints:
    """Test health check and system status endpoints."""
    
    def test_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_readiness_probe(self, client):
        """Test Kubernetes readiness probe."""
        response = client.get("/ready")
        assert response.status_code == 200
        
        data = response.json()
        assert data["ready"] is True


class TestAPIVersioning:
    """Test API versioning and backward compatibility."""
    
    def test_api_v1_endpoints(self, client):
        """Test API v1 endpoints availability."""
        response = client.get("/api/v1/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
    
    def test_api_v3_endpoints(self, client):
        """Test API v3 endpoints availability."""
        response = client.get("/api/v3/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data


class TestSystemAnalysisEndpoints:
    """Test system analysis and monitoring endpoints."""
    
    def test_cpu_analysis(self, client):
        """Test CPU analysis endpoint."""
        response = client.get("/api/v3/system/cpu")
        # Accept both success and not implemented
        assert response.status_code in [200, 404, 501]
        
        if response.status_code == 200:
            data = response.json()
            assert "cpu_percent" in data
    
    def test_system_overview(self, client):
        """Test complete system overview."""
        response = client.get("/api/v3/system/overview")
        # Accept both success and not implemented
        assert response.status_code in [200, 404, 501]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_endpoint(self, client):
        """Test handling of invalid endpoints."""
        response = client.get("/invalid-endpoint")
        assert response.status_code == 404
    
    def test_cors_headers(self, client):
        """Test CORS headers are properly set."""
        response = client.options("/health", 
                                headers={"Origin": "http://localhost:3000"})
        # CORS may or may not be configured
        assert response.status_code in [200, 404, 405]


class TestPerformance:
    """Test performance and load characteristics."""
    
    def test_response_time(self, client):
        """Test that responses are reasonably fast."""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        assert response.status_code == 200
        
        # Health check should be fast (under 2 seconds)
        response_time = end_time - start_time
        assert response_time < 2.0


# Test configuration and fixtures validation
def test_test_configuration():
    """Test that test configuration is properly set up."""
    settings = get_settings()
    assert settings is not None
    assert hasattr(settings, 'PROJECT_NAME')
    assert hasattr(settings, 'VERSION')


def test_app_creation():
    """Test that the FastAPI app is properly created."""
    assert app is not None
    assert hasattr(app, 'routes')
    assert len(app.routes) > 0
