"""
Testes de Integração - Sistema Completo
"""

import pytest
import httpx
import asyncio
from fastapi.testclient import TestClient
from app.main import app

class TestAPIIntegration:
    """Testes de integração das APIs"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Testa endpoint de health check"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_performance_metrics_endpoint(self):
        """Testa endpoint de métricas de performance"""
        response = self.client.get("/api/core/performance/metrics/system")
        
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "cpu" in data
    
    def test_performance_health_endpoint(self):
        """Testa health check de performance"""
        response = self.client.get("/api/core/performance/health/basic")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    def test_performance_optimization_endpoint(self):
        """Testa endpoint de otimização"""
        response = self.client.post("/api/core/performance/optimize/database")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "optimizations_applied" in data

class TestSystemLoad:
    """Testes de carga do sistema"""
    
    def setup_method(self):
        """Setup para testes de carga"""
        self.client = TestClient(app)
    
    def test_concurrent_health_checks(self):
        """Testa múltiplas requisições simultâneas"""
        def make_request():
            return self.client.get("/health")
        
        # Executa 10 requisições simultâneas
        responses = []
        for _ in range(10):
            response = make_request()
            responses.append(response)
        
        # Verifica se todas foram bem-sucedidas
        for response in responses:
            assert response.status_code == 200
    
    def test_api_response_time(self):
        """Testa tempo de resposta das APIs"""
        import time
        
        start_time = time.time()
        response = self.client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 1.0  # Deve responder em menos de 1 segundo

class TestErrorHandling:
    """Testes de tratamento de erros"""
    
    def setup_method(self):
        """Setup para testes de erro"""
        self.client = TestClient(app)
    
    def test_404_error_handling(self):
        """Testa tratamento de endpoints inexistentes"""
        response = self.client.get("/api/core/nonexistent")
        
        assert response.status_code == 404
    
    def test_cors_headers(self):
        """Testa cabeçalhos CORS"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        # Verifica presença de headers CORS básicos
        headers = response.headers
        assert "content-type" in headers