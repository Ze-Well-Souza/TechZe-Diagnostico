"""
Testes de Performance e Segurança - TechZe Diagnóstico
SEMANAS 3-4: Testes avançados de performance, segurança e otimização
"""

import pytest
import time
import concurrent.futures
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestPerformanceAdvanced:
    """Testes avançados de performance"""
    
    def test_memory_usage_monitoring(self):
        """Testa monitoramento de uso de memória sob carga"""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # Fazer múltiplas requests que consomem memória
            for i in range(50):
                payload = {
                    "cliente": {
                        "nome": f"Cliente Teste {i}",
                        "telefone": f"(11) 9999{i:04d}"
                    },
                    "equipamento": {
                        "tipo": "notebook",
                        "problema_relatado": f"Problema complexo {i} que requer análise detalhada do sistema"
                    }
                }
                
                try:
                    response = client.post("/api/v1/orcamentos/", json=payload)
                except Exception:
                    pass
            
            memory_after = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = memory_after - memory_before
            
            print(f"📊 Memória antes: {memory_before:.2f}MB")
            print(f"📊 Memória depois: {memory_after:.2f}MB")
            print(f"📊 Aumento: {memory_increase:.2f}MB")
            
            # Aceitar até 50MB de aumento
            assert memory_increase < 50, f"Vazamento de memória detectado: +{memory_increase:.2f}MB"
            
        except ImportError:
            pytest.skip("psutil não disponível")
    
    def test_database_connection_pool(self):
        """Testa pool de conexões do banco"""
        
        def make_db_request():
            try:
                response = client.get("/api/v1/orcamentos/")
                return response.status_code
            except Exception:
                return 500
        
        # Fazer 100 requests simultâneas para testar pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_db_request) for _ in range(100)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        success_count = sum(1 for status in results if status in [200, 404])
        success_rate = success_count / len(results)
        
        print(f"📊 Pool de conexões - Taxa de sucesso: {success_rate:.2%}")
        assert success_rate >= 0.90, "Pool de conexões com problemas"


class TestSecurityValidation:
    """Testes de segurança e validação"""
    
    def test_sql_injection_attempts(self):
        """Testa tentativas de SQL injection"""
        
        malicious_inputs = [
            "'; DROP TABLE orcamentos; --",
            "1' OR '1'='1",
            "admin'; DELETE FROM users; --"
        ]
        
        for malicious_input in malicious_inputs:
            payload = {
                "cliente": {
                    "nome": malicious_input,
                    "telefone": "(11) 99999-9999"
                },
                "equipamento": {
                    "tipo": "notebook",
                    "problema_relatado": "Teste de segurança com payload SQL malicioso para verificar proteções"
                }
            }
            
            response = client.post("/api/v1/orcamentos/", json=payload)
            
            # Se retornar 200/201, verificar se dados foram sanitizados
            if response.status_code in [200, 201]:
                data = response.json()
                nome_retornado = data.get("cliente", {}).get("nome", "")
                assert "DROP" not in nome_retornado.upper()
                assert "DELETE" not in nome_retornado.upper()
            
            # Ou deve retornar erro de validação
            elif response.status_code not in [400, 422]:
                pytest.fail(f"Possível vulnerabilidade SQL: {response.status_code}")
        
        print("✅ Proteção contra SQL injection validada")
    
    def test_input_size_limits(self):
        """Testa limites de tamanho de entrada"""
        
        # String muito grande
        very_long_string = "A" * 10000
        
        payload = {
            "cliente": {
                "nome": very_long_string,
                "telefone": "(11) 99999-9999"
            },
            "equipamento": {
                "tipo": "notebook",
                "problema_relatado": very_long_string
            }
        }
        
        response = client.post("/api/v1/orcamentos/", json=payload)
        
        # Deve rejeitar entradas muito grandes
        assert response.status_code in [400, 422], "Entrada muito grande foi aceita"
        
        print("✅ Limites de entrada validados")


class TestErrorHandling:
    """Testes de tratamento de erros"""
    
    def test_404_handling(self):
        """Testa tratamento de recursos não encontrados"""
        
        response = client.get("/api/v1/orcamentos/id-inexistente")
        assert response.status_code == 404
        
        # Verificar estrutura da resposta de erro
        error_data = response.json()
        assert "detail" in error_data or "message" in error_data
        
        print("✅ Tratamento de 404 validado")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
