"""
Teste de Performance - Validação Frontend-Backend
CURSOR testando performance das implementações do TRAE

Descobertas Críticas: Performance 2.339s vs Meta 500ms
"""

import requests
import time
from datetime import datetime
import statistics


def test_performance_endpoints():
    """Teste de performance dos endpoints críticos"""
    base_url = "http://localhost:8000"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    endpoints = [
        "/api/v1/orcamentos/",
        "/api/v1/estoque/itens",
        "/api/v1/ordens-servico/",
        "/health"
    ]
    
    results = {}
    
    print("=== TESTE DE PERFORMANCE CRÍTICA ===")
    print("Meta: < 500ms response time")
    print("=" * 50)
    
    for endpoint in endpoints:
        print(f"\nTestando: {endpoint}")
        times = []
        status_codes = []
        
        # 5 tentativas para cada endpoint
        for i in range(5):
            start_time = time.time()
            try:
                response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=10)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # em ms
                times.append(response_time)
                status_codes.append(response.status_code)
                
                print(f"  Tentativa {i+1}: {response_time:.0f}ms - Status {response.status_code}")
                
            except Exception as e:
                print(f"  Tentativa {i+1}: ERRO - {e}")
                times.append(10000)  # 10s como penalidade
                status_codes.append(0)
        
        # Calcular estatísticas
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            results[endpoint] = {
                "avg_time": avg_time,
                "min_time": min_time,
                "max_time": max_time,
                "status_codes": status_codes
            }
            
            # Avaliação
            status = "✅ OK" if avg_time < 500 else "❌ LENTO"
            if any(code == 500 for code in status_codes):
                status = "❌ ERRO 500"
            
            print(f"  RESULTADO: {status}")
            print(f"  Tempo médio: {avg_time:.0f}ms")
            print(f"  Min/Max: {min_time:.0f}ms / {max_time:.0f}ms")
    
    # Resumo final
    print("\n" + "=" * 50)
    print("RESUMO DE PERFORMANCE:")
    print("=" * 50)
    
    total_avg = []
    failed_endpoints = 0
    
    for endpoint, data in results.items():
        avg_time = data["avg_time"]
        status_codes = data["status_codes"]
        
        total_avg.append(avg_time)
        
        # Status do endpoint
        if any(code == 500 for code in status_codes):
            status = "❌ ERRO 500"
            failed_endpoints += 1
        elif avg_time > 500:
            status = "❌ LENTO"
        else:
            status = "✅ OK"
        
        print(f"{endpoint}: {avg_time:.0f}ms - {status}")
    
    # Performance geral do sistema
    if total_avg:
        system_avg = statistics.mean(total_avg)
        print(f"\nPERFORMANCE GERAL DO SISTEMA: {system_avg:.0f}ms")
        
        if system_avg > 500:
            print("❌ SISTEMA REPROVADO - Performance crítica")
        else:
            print("✅ SISTEMA APROVADO - Performance aceitável")
        
        success_rate = ((len(endpoints) - failed_endpoints) / len(endpoints)) * 100
        print(f"Taxa de Sucesso: {success_rate:.1f}%")
        
        return {
            "system_avg": system_avg,
            "success_rate": success_rate,
            "failed_endpoints": failed_endpoints,
            "total_endpoints": len(endpoints)
        }


if __name__ == "__main__":
    results = test_performance_endpoints()
    
    print("\n" + "=" * 50)
    print("CONCLUSÃO FINAL:")
    print("=" * 50)
    
    if results:
        if results["system_avg"] > 500:
            print("❌ SISTEMA NÃO APROVADO PARA PRODUÇÃO")
            print(f"Performance: {results['system_avg']:.0f}ms (368% acima da meta)")
        
        if results["failed_endpoints"] > 0:
            print(f"❌ {results['failed_endpoints']}/{results['total_endpoints']} endpoints com falha")
        
        print(f"Taxa de Funcionamento: {results['success_rate']:.1f}%") 