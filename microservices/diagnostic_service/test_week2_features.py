#!/usr/bin/env python3
"""
Teste das Funcionalidades da Semana 2 - TechZe Diagnostic Service
Testa monitoramento avançado, cache e dashboards
"""
import asyncio
import json
import time
import requests
import sys
from datetime import datetime

# URLs base
BASE_URL = "http://localhost:8000"
GRAFANA_URL = "http://localhost:3000"
PROMETHEUS_URL = "http://localhost:9090"

def print_test_result(test_name, success, details=""):
    """Imprime resultado do teste"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def test_api_health():
    """Testa health check da API"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            details += f" - Service: {data.get('service', 'unknown')}"
        print_test_result("API Health Check", success, details)
        return success
    except Exception as e:
        print_test_result("API Health Check", False, f"Erro: {e}")
        return False

def test_detailed_health():
    """Testa health check detalhado"""
    try:
        response = requests.get(f"{BASE_URL}/health/detailed", timeout=10)
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            status = data.get('status', 'unknown')
            components = len(data.get('components', {}))
            details += f" - Overall: {status} - Components: {components}"
        print_test_result("Detailed Health Check", success, details)
        return success
    except Exception as e:
        print_test_result("Detailed Health Check", False, f"Erro: {e}")
        return False

def test_operational_dashboard():
    """Testa dashboard operacional"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/monitoring/dashboard/operational", timeout=10)
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            if "error" in data:
                success = False
                details += f" - Error: {data['error']}"
            else:
                metrics_count = len(data.get('metrics', {}))
                details += f" - Metrics: {metrics_count}"
        print_test_result("Operational Dashboard", success, details)
        return success
    except Exception as e:
        print_test_result("Operational Dashboard", False, f"Erro: {e}")
        return False

def test_security_dashboard():
    """Testa dashboard de segurança"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/monitoring/dashboard/security", timeout=10)
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            if "error" in data:
                success = False
                details += f" - Error: {data['error']}"
            else:
                metrics_count = len(data.get('metrics', {}))
                details += f" - Security Metrics: {metrics_count}"
        print_test_result("Security Dashboard", success, details)
        return success
    except Exception as e:
        print_test_result("Security Dashboard", False, f"Erro: {e}")
        return False

def test_alerts_endpoint():
    """Testa endpoint de alertas"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/monitoring/alerts", timeout=10)
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            if "error" in data:
                success = False
                details += f" - Error: {data['error']}"
            else:
                alerts_count = len(data.get('alerts', []))
                details += f" - Active Alerts: {alerts_count}"
        print_test_result("Alerts Endpoint", success, details)
        return success
    except Exception as e:
        print_test_result("Alerts Endpoint", False, f"Erro: {e}")
        return False

def test_cache_stats():
    """Testa estatísticas do cache"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/cache/stats", timeout=10)
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            if "error" in data:
                success = False
                details += f" - Error: {data['error']}"
            else:
                cache_stats = data.get('cache_stats', {})
                redis_available = cache_stats.get('redis_available', False)
                details += f" - Redis: {'Available' if redis_available else 'Unavailable'}"
        print_test_result("Cache Stats", success, details)
        return success
    except Exception as e:
        print_test_result("Cache Stats", False, f"Erro: {e}")
        return False

def test_prometheus_metrics():
    """Testa se métricas estão sendo expostas"""
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=10)
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            metrics_text = response.text
            techze_metrics = [line for line in metrics_text.split('\n') if 'techze_' in line and not line.startswith('#')]
            details += f" - TechZe Metrics: {len(techze_metrics)}"
        print_test_result("Prometheus Metrics", success, details)
        return success
    except Exception as e:
        print_test_result("Prometheus Metrics", False, f"Erro: {e}")
        return False

def test_alertmanager_webhook():
    """Testa webhook do Alertmanager"""
    try:
        # Simula um alerta do Alertmanager
        test_alert = {
            "alerts": [
                {
                    "status": "firing",
                    "labels": {
                        "alertname": "TestAlert",
                        "severity": "warning",
                        "service": "techze-diagnostic"
                    },
                    "annotations": {
                        "summary": "Test alert for webhook",
                        "description": "This is a test alert to verify webhook functionality"
                    },
                    "fingerprint": f"test_alert_{int(time.time())}"
                }
            ]
        }
        
        response = requests.post(
            f"{BASE_URL}/api/v1/alerts/webhook",
            json=test_alert,
            timeout=10
        )
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        if success:
            data = response.json()
            processed = data.get('processed_alerts', 0)
            details += f" - Processed: {processed} alerts"
        print_test_result("Alertmanager Webhook", success, details)
        return success
    except Exception as e:
        print_test_result("Alertmanager Webhook", False, f"Erro: {e}")
        return False

def test_diagnostic_with_cache():
    """Testa diagnóstico com cache"""
    try:
        # Primeiro diagnóstico (deve ir para cache)
        start_time = time.time()
        response1 = requests.post(
            f"{BASE_URL}/api/v1/diagnostic/quick",
            json={"system_info": {"os": "test"}},
            timeout=30
        )
        first_duration = time.time() - start_time
        
        if response1.status_code != 200:
            print_test_result("Diagnostic with Cache", False, f"First request failed: {response1.status_code}")
            return False
        
        # Segundo diagnóstico (deve vir do cache, mais rápido)
        start_time = time.time()
        response2 = requests.post(
            f"{BASE_URL}/api/v1/diagnostic/quick",
            json={"system_info": {"os": "test"}},
            timeout=30
        )
        second_duration = time.time() - start_time
        
        success = response2.status_code == 200
        details = f"First: {first_duration:.2f}s, Second: {second_duration:.2f}s"
        
        # Verifica se o segundo foi mais rápido (indicando cache)
        if success and second_duration < first_duration * 0.8:
            details += " - Cache working!"
        
        print_test_result("Diagnostic with Cache", success, details)
        return success
    except Exception as e:
        print_test_result("Diagnostic with Cache", False, f"Erro: {e}")
        return False

def test_external_services():
    """Testa serviços externos (Prometheus, Grafana)"""
    services = {
        "Prometheus": PROMETHEUS_URL,
        "Grafana": GRAFANA_URL
    }
    
    results = {}
    for service, url in services.items():
        try:
            response = requests.get(f"{url}/api/health", timeout=5)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
        except requests.exceptions.ConnectionError:
            success = False
            details = "Connection refused - Service not running"
        except Exception as e:
            success = False
            details = f"Error: {e}"
        
        print_test_result(f"{service} Service", success, details)
        results[service] = success
    
    return all(results.values())

def run_load_test():
    """Executa teste de carga básico"""
    print("\n🔥 Executando teste de carga básico...")
    
    start_time = time.time()
    success_count = 0
    error_count = 0
    
    for i in range(10):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                success_count += 1
            else:
                error_count += 1
        except Exception:
            error_count += 1
    
    duration = time.time() - start_time
    rps = 10 / duration if duration > 0 else 0
    
    success = error_count == 0
    details = f"10 requests in {duration:.2f}s - {rps:.1f} RPS - Errors: {error_count}"
    print_test_result("Load Test (10 requests)", success, details)
    
    return success

def main():
    """Função principal de teste"""
    print("🧪 Testando Funcionalidades da Semana 2 - TechZe Diagnostic Service")
    print("=" * 70)
    
    tests = [
        ("Basic API", test_api_health),
        ("Detailed Health", test_detailed_health),
        ("Prometheus Metrics", test_prometheus_metrics),
        ("Operational Dashboard", test_operational_dashboard),
        ("Security Dashboard", test_security_dashboard),
        ("Alerts Endpoint", test_alerts_endpoint),
        ("Cache Stats", test_cache_stats),
        ("Alertmanager Webhook", test_alertmanager_webhook),
        ("Diagnostic with Cache", test_diagnostic_with_cache),
    ]
    
    results = {}
    
    print("\n📋 Testando Funcionalidades Principais:")
    print("-" * 40)
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print("\n🌐 Testando Serviços Externos:")
    print("-" * 40)
    results["External Services"] = test_external_services()
    
    print("\n⚡ Teste de Performance:")
    print("-" * 40)
    results["Load Test"] = run_load_test()
    
    # Resumo
    print("\n📊 RESUMO DOS TESTES:")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print("-" * 70)
    print(f"📈 Resultado: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 Todos os testes passaram! Sistema funcionando corretamente.")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Verifique os logs acima.")
        return 1

if __name__ == "__main__":
    sys.exit(main())