"""
Testes de Stress e Load Testing
Responsável: Agente CURSOR testando implementações do TRAE
Valida: Performance sob carga, concorrência, limites do sistema
"""

import pytest
import asyncio
import time
import concurrent.futures
from fastapi.testclient import TestClient
from typing import List, Dict, Any
import statistics
import threading
from datetime import datetime

from app.main import app

client = TestClient(app)

class TestStressLoad:
    """Testes de stress e carga do sistema"""
    
    def setup_method(self):
        """Setup antes de cada teste"""
        self.base_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.test_results = []
    
    def test_concurrent_health_checks(self):
        """Testa múltiplas verificações de saúde simultâneas"""
        def make_health_request():
            start_time = time.time()
            response = client.get("/health")
            end_time = time.time()
            
            return {
                "status_code": response.status_code,
                "response_time": (end_time - start_time) * 1000,
                "success": response.status_code == 200
            }
        
        # Executar 50 requests simultâneas
        num_requests = 50
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_health_request) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Analisar resultados
        response_times = [r["response_time"] for r in results]
        success_count = sum(1 for r in results if r["success"])
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"✅ Concurrent Health Checks:")
        print(f"   - Total requests: {num_requests}")
        print(f"   - Successful: {success_count} ({success_count/num_requests*100:.1f}%)")
        print(f"   - Avg response time: {avg_response_time:.2f}ms")
        print(f"   - Min response time: {min_response_time:.2f}ms")
        print(f"   - Max response time: {max_response_time:.2f}ms")
        
        # Assertions
        assert success_count >= num_requests * 0.95  # 95% success rate
        assert avg_response_time < 1000  # Média menor que 1 segundo
        assert max_response_time < 5000  # Máximo menor que 5 segundos
    
    def test_api_endpoints_under_load(self):
        """Testa endpoints principais sob carga"""
        endpoints = [
            "/health",
            "/",
            "/info",
            "/api/v1/orcamentos/"
        ]
        
        def test_endpoint(endpoint):
            results = []
            
            for _ in range(10):  # 10 requests por endpoint
                start_time = time.time()
                response = client.get(endpoint)
                end_time = time.time()
                
                results.append({
                    "endpoint": endpoint,
                    "status_code": response.status_code,
                    "response_time": (end_time - start_time) * 1000,
                    "success": response.status_code in [200, 401, 403]  # Aceitar auth errors
                })
            
            return results
        
        all_results = []
        
        # Testar todos endpoints simultaneamente
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(endpoints)) as executor:
            futures = [executor.submit(test_endpoint, endpoint) for endpoint in endpoints]
            for future in concurrent.futures.as_completed(futures):
                all_results.extend(future.result())
        
        # Analisar por endpoint
        endpoint_stats = {}
        for endpoint in endpoints:
            endpoint_results = [r for r in all_results if r["endpoint"] == endpoint]
            
            if endpoint_results:
                response_times = [r["response_time"] for r in endpoint_results]
                success_count = sum(1 for r in endpoint_results if r["success"])
                
                endpoint_stats[endpoint] = {
                    "total_requests": len(endpoint_results),
                    "successful": success_count,
                    "success_rate": success_count / len(endpoint_results) * 100,
                    "avg_response_time": statistics.mean(response_times),
                    "max_response_time": max(response_times)
                }
        
        print("✅ API Endpoints Under Load:")
        for endpoint, stats in endpoint_stats.items():
            print(f"   {endpoint}:")
            print(f"     - Success rate: {stats['success_rate']:.1f}%")
            print(f"     - Avg response: {stats['avg_response_time']:.2f}ms")
            print(f"     - Max response: {stats['max_response_time']:.2f}ms")
        
        # Verificar que todos endpoints mantêm performance aceitável
        for endpoint, stats in endpoint_stats.items():
            assert stats["success_rate"] >= 90, f"Endpoint {endpoint} tem taxa de sucesso baixa: {stats['success_rate']:.1f}%"
            assert stats["avg_response_time"] < 2000, f"Endpoint {endpoint} muito lento: {stats['avg_response_time']:.2f}ms"
    
    def test_memory_leak_detection(self):
        """Testa se há vazamentos de memória em requests repetidas"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Fazer muitas requests para detectar vazamentos
        for i in range(100):
            response = client.get("/health")
            assert response.status_code == 200
            
            # Verificar a cada 25 requests
            if i % 25 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = current_memory - initial_memory
                
                print(f"   Request {i}: Memory usage: {current_memory:.2f}MB (+{memory_increase:.2f}MB)")
                
                # Alerta se o aumento de memória for muito grande
                if memory_increase > 50:  # 50MB de aumento
                    print(f"   ⚠️ Possível vazamento de memória detectado: +{memory_increase:.2f}MB")
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_increase = final_memory - initial_memory
        
        print(f"✅ Memory Leak Detection:")
        print(f"   - Initial memory: {initial_memory:.2f}MB")
        print(f"   - Final memory: {final_memory:.2f}MB")
        print(f"   - Total increase: {total_increase:.2f}MB")
        
        # Assertion - não deve aumentar mais que 30MB
        assert total_increase < 30, f"Possível vazamento de memória: +{total_increase:.2f}MB"
    
    def test_rapid_fire_requests(self):
        """Testa sistema com rajadas rápidas de requests"""
        def rapid_fire_batch(batch_size=20):
            results = []
            start_batch = time.time()
            
            # Disparar requests o mais rápido possível
            for _ in range(batch_size):
                try:
                    start_time = time.time()
                    response = client.get("/health")
                    end_time = time.time()
                    
                    results.append({
                        "status_code": response.status_code,
                        "response_time": (end_time - start_time) * 1000,
                        "success": response.status_code == 200
                    })
                except Exception as e:
                    results.append({
                        "status_code": 0,
                        "response_time": 0,
                        "success": False,
                        "error": str(e)
                    })
            
            end_batch = time.time()
            batch_time = (end_batch - start_batch) * 1000
            
            return results, batch_time
        
        # Executar 5 rajadas de 20 requests cada
        all_results = []
        batch_times = []
        
        for batch_num in range(5):
            results, batch_time = rapid_fire_batch(20)
            all_results.extend(results)
            batch_times.append(batch_time)
            
            success_in_batch = sum(1 for r in results if r["success"])
            print(f"   Batch {batch_num + 1}: {success_in_batch}/20 successful in {batch_time:.2f}ms")
            
            # Pequena pausa entre rajadas
            time.sleep(0.1)
        
        # Analisar resultados gerais
        total_requests = len(all_results)
        total_successful = sum(1 for r in all_results if r["success"])
        success_rate = total_successful / total_requests * 100
        
        successful_results = [r for r in all_results if r["success"]]
        if successful_results:
            avg_response_time = statistics.mean([r["response_time"] for r in successful_results])
            max_response_time = max([r["response_time"] for r in successful_results])
        else:
            avg_response_time = 0
            max_response_time = 0
        
        print(f"✅ Rapid Fire Requests:")
        print(f"   - Total requests: {total_requests}")
        print(f"   - Success rate: {success_rate:.1f}%")
        print(f"   - Avg response time: {avg_response_time:.2f}ms")
        print(f"   - Max response time: {max_response_time:.2f}ms")
        print(f"   - Avg batch time: {statistics.mean(batch_times):.2f}ms")
        
        # Assertions
        assert success_rate >= 85, f"Taxa de sucesso muito baixa em rajadas: {success_rate:.1f}%"
        assert avg_response_time < 1500, f"Tempo de resposta muito alto em rajadas: {avg_response_time:.2f}ms"
    
    def test_sustained_load(self):
        """Testa carga sustentada por período prolongado"""
        test_duration = 30  # 30 segundos
        requests_per_second = 5
        
        start_test = time.time()
        results = []
        
        print(f"✅ Sustained Load Test: {test_duration}s at {requests_per_second} req/s")
        
        while time.time() - start_test < test_duration:
            second_start = time.time()
            second_results = []
            
            # Fazer requests_per_second requests neste segundo
            for _ in range(requests_per_second):
                try:
                    request_start = time.time()
                    response = client.get("/health")
                    request_end = time.time()
                    
                    second_results.append({
                        "status_code": response.status_code,
                        "response_time": (request_end - request_start) * 1000,
                        "success": response.status_code == 200,
                        "timestamp": request_start
                    })
                except Exception as e:
                    second_results.append({
                        "status_code": 0,
                        "response_time": 0,
                        "success": False,
                        "error": str(e),
                        "timestamp": time.time()
                    })
            
            results.extend(second_results)
            
            # Aguardar até completar 1 segundo
            elapsed = time.time() - second_start
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
            
            # Progress report a cada 10 segundos
            test_elapsed = time.time() - start_test
            if int(test_elapsed) % 10 == 0 and int(test_elapsed) > 0:
                recent_results = [r for r in results if r["timestamp"] > time.time() - 10]
                recent_success = sum(1 for r in recent_results if r["success"])
                print(f"   {int(test_elapsed)}s: {recent_success}/{len(recent_results)} successful in last 10s")
        
        # Analisar resultados finais
        total_requests = len(results)
        total_successful = sum(1 for r in results if r["success"])
        success_rate = total_successful / total_requests * 100 if total_requests > 0 else 0
        
        successful_results = [r for r in results if r["success"]]
        if successful_results:
            response_times = [r["response_time"] for r in successful_results]
            avg_response_time = statistics.mean(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
            max_response_time = max(response_times)
        else:
            avg_response_time = 0
            p95_response_time = 0
            max_response_time = 0
        
        print(f"✅ Sustained Load Results:")
        print(f"   - Duration: {test_duration}s")
        print(f"   - Total requests: {total_requests}")
        print(f"   - Success rate: {success_rate:.1f}%")
        print(f"   - Avg response time: {avg_response_time:.2f}ms")
        print(f"   - P95 response time: {p95_response_time:.2f}ms")
        print(f"   - Max response time: {max_response_time:.2f}ms")
        print(f"   - Throughput: {total_successful / test_duration:.1f} req/s")
        
        # Assertions
        assert success_rate >= 90, f"Taxa de sucesso baixa em carga sustentada: {success_rate:.1f}%"
        assert avg_response_time < 1000, f"Tempo médio alto em carga sustentada: {avg_response_time:.2f}ms"
        assert p95_response_time < 2000, f"P95 muito alto em carga sustentada: {p95_response_time:.2f}ms"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--tb=short"]) 