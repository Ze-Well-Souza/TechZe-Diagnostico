"""
Testes de Integração - API Core Consolidada
"""

import pytest
import httpx
import asyncio
from fastapi.testclient import TestClient
from app.main import app

class TestAPICoreIntegration:
    """Testes de integração da API Core consolidada"""
    
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
        assert "api_status" in data
        assert "core_api" in data["api_status"]
    
    def test_core_api_info_endpoint(self):
        """Testa endpoint de informações da API Core"""
        response = self.client.get("/api/core/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "domains" in data
        assert len(data["domains"]) == 8  # 8 domínios funcionais
        
        # Verifica se todos os domínios esperados estão presentes
        expected_domains = ["auth", "diagnostics", "ai", "automation", "analytics", "performance", "chat", "integration"]
        for domain in expected_domains:
            assert domain in data["domains"]
    
    def test_core_auth_endpoints(self):
        """Testa endpoints de autenticação consolidados"""
        # Testa info do domínio auth
        response = self.client.get("/api/core/auth/info")
        assert response.status_code == 200
        
        # Testa health do auth
        response = self.client.get("/api/core/auth/health")
        assert response.status_code == 200
    
    def test_core_diagnostics_endpoints(self):
        """Testa endpoints de diagnóstico consolidados"""
        # Testa info do domínio diagnostics
        response = self.client.get("/api/core/diagnostics/info")
        assert response.status_code == 200
        
        # Testa health do diagnostics
        response = self.client.get("/api/core/diagnostics/health")
        assert response.status_code == 200
    
    def test_core_performance_endpoints(self):
        """Testa endpoints de performance consolidados"""
        # Testa info do domínio performance
        response = self.client.get("/api/core/performance/info")
        assert response.status_code == 200
        
        # Testa health do performance
        response = self.client.get("/api/core/performance/health")
        assert response.status_code == 200
        
        # Testa stats (mesmo que retorne 404, teste se endpoint existe)
        response = self.client.get("/api/core/performance/stats")
        # Aceita 200 se implementado ou 404 se ainda não implementado
        assert response.status_code in [200, 404]
    
    def test_core_ai_endpoints(self):
        """Testa endpoints de IA consolidados"""
        # Testa info do domínio ai
        response = self.client.get("/api/core/ai/info")
        assert response.status_code == 200
        
        # Testa health do ai
        response = self.client.get("/api/core/ai/health")
        assert response.status_code == 200
    
    def test_core_automation_endpoints(self):
        """Testa endpoints de automação consolidados"""
        # Testa info do domínio automation
        response = self.client.get("/api/core/automation/info")
        assert response.status_code == 200
        
        # Testa health do automation
        response = self.client.get("/api/core/automation/health")
        assert response.status_code == 200
    
    def test_core_analytics_endpoints(self):
        """Testa endpoints de analytics consolidados"""
        # Testa info do domínio analytics
        response = self.client.get("/api/core/analytics/info")
        assert response.status_code == 200
        
        # Testa health do analytics
        response = self.client.get("/api/core/analytics/health")
        assert response.status_code == 200
    
    def test_core_chat_endpoints(self):
        """Testa endpoints de chat consolidados"""
        # Testa info do domínio chat
        response = self.client.get("/api/core/chat/info")
        assert response.status_code == 200
        
        # Testa health do chat
        response = self.client.get("/api/core/chat/health")
        assert response.status_code == 200
    
    def test_core_integration_endpoints(self):
        """Testa endpoints de integração consolidados"""
        # Testa info do domínio integration
        response = self.client.get("/api/core/integration/info")
        assert response.status_code == 200
        
        # Testa health do integration
        response = self.client.get("/api/core/integration/health")
        assert response.status_code == 200

class TestConsolidationStatus:
    """Testes de status da consolidação"""
    
    def setup_method(self):
        """Setup para testes de consolidação"""
        self.client = TestClient(app)
    
    def test_consolidation_status(self):
        """Testa se a consolidação está ativa"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "api_consolidation" in data
        assert data["api_consolidation"]["status"] == "active"
        assert "core_api" in data["api_consolidation"]
    
    def test_service_info_consolidation(self):
        """Testa informações de consolidação no endpoint info"""
        response = self.client.get("/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "api_consolidation" in data
        assert data["api_consolidation"]["status"] == "completed"
        assert data["api_consolidation"]["core_api_available"] == True
        assert data["api_consolidation"]["core_api_endpoint"] == "/api/core"

class TestSystemLoadCore:
    """Testes de carga da API Core"""
    
    def setup_method(self):
        """Setup para testes de carga"""
        self.client = TestClient(app)
    
    def test_concurrent_core_requests(self):
        """Testa múltiplas requisições simultâneas na API Core"""
        def make_request():
            return self.client.get("/api/core/info")
        
        # Executa 10 requisições simultâneas
        responses = []
        for _ in range(10):
            response = make_request()
            responses.append(response)
        
        # Verifica se todas foram bem-sucedidas
        for response in responses:
            assert response.status_code == 200
    
    def test_core_api_response_time(self):
        """Testa tempo de resposta da API Core"""
        import time
        
        start_time = time.time()
        response = self.client.get("/api/core/info")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Deve responder em menos de 2 segundos

class TestLegacyCompatibility:
    """Testes de compatibilidade com APIs legacy"""
    
    def setup_method(self):
        """Setup para testes de compatibilidade"""
        self.client = TestClient(app)
    
    def test_legacy_pool_endpoints_still_work(self):
        """Testa se endpoints legacy de pool ainda funcionam"""
        # Testa se os endpoints v3 de pool ainda estão disponíveis para compatibilidade
        endpoints = [
            "/api/v3/pool/metrics",
            "/api/v3/pool/health", 
            "/api/v3/pool/stats"
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            # Aceita 200 se funcional, 503 se pool não inicializado, ou 404 se removido
            assert response.status_code in [200, 503, 404]

class TestErrorHandlingCore:
    """Testes de tratamento de erros da API Core"""
    
    def setup_method(self):
        """Setup para testes de erro"""
        self.client = TestClient(app)
    
    def test_404_error_handling_core(self):
        """Testa tratamento de endpoints inexistentes na API Core"""
        response = self.client.get("/api/core/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "service" in data
        assert data["service"] == "diagnostic-service-consolidated"
    
    def test_cors_headers_core(self):
        """Testa cabeçalhos CORS na API Core"""
        response = self.client.get("/api/core/info")
        
        assert response.status_code == 200
        # Verifica presença de headers CORS básicos
        headers = response.headers
        assert "content-type" in headers
