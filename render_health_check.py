#!/usr/bin/env python3
"""
🔍 TechZe Render Health Check Script
Verifica se o deploy no Render está 100% configurado corretamente
"""

import requests
import json
import time
from typing import Dict, List, Tuple
from datetime import datetime

# URLs dos serviços no Render
SERVICES = {
    "backend": "https://techze-diagnostico-api.onrender.com",
    "frontend": "https://techze-diagnostico-frontend.onrender.com"
}

# Endpoints críticos para testar
CRITICAL_ENDPOINTS = [
    ("/health", "GET"),
    ("/api/core/diagnostics/health", "GET"),
    ("/api/v3/pool/metrics", "GET"),
    ("/api/v3/pool/health", "GET"),
    ("/api/core/auth/health", "GET"),
    ("/api/core/ai/health", "GET"),
]

def print_header():
    """Imprime cabeçalho do script"""
    print("=" * 60)
    print("🔍 TECHZE RENDER HEALTH CHECK")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

def check_service_basic(service_name: str, base_url: str) -> Tuple[bool, Dict]:
    """Verifica saúde básica de um serviço"""
    print(f"🔍 Verificando {service_name.upper()}...")
    print(f"🌐 URL: {base_url}")
    
    results = {
        "service": service_name,
        "base_url": base_url,
        "status": "unknown",
        "response_time": None,
        "status_code": None,
        "error": None
    }
    
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/health", timeout=30)
        response_time = time.time() - start_time
        
        results["response_time"] = round(response_time * 1000, 2)  # ms
        results["status_code"] = response.status_code
        
        if response.status_code == 200:
            results["status"] = "healthy"
            print(f"✅ {service_name.capitalize()} está online")
            print(f"⚡ Tempo de resposta: {results['response_time']}ms")
        else:
            results["status"] = "unhealthy"
            print(f"❌ {service_name.capitalize()} retornou status {response.status_code}")
            
    except requests.exceptions.Timeout:
        results["status"] = "timeout"
        results["error"] = "Timeout após 30s"
        print(f"⏰ {service_name.capitalize()} - Timeout")
        
    except requests.exceptions.ConnectionError:
        results["status"] = "unreachable"
        results["error"] = "Conexão falhou"
        print(f"🔌 {service_name.capitalize()} - Serviço inacessível")
        
    except Exception as e:
        results["status"] = "error"
        results["error"] = str(e)
        print(f"❌ {service_name.capitalize()} - Erro: {e}")
    
    print()
    return results["status"] == "healthy", results

def check_backend_endpoints(base_url: str) -> Tuple[bool, List[Dict]]:
    """Verifica endpoints críticos do backend"""
    print("🧪 TESTANDO ENDPOINTS CRÍTICOS...")
    print("-" * 40)
    
    all_healthy = True
    endpoint_results = []
    
    for endpoint, method in CRITICAL_ENDPOINTS:
        print(f"Testing {method} {endpoint}...")
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "status": "unknown",
            "response_time": None,
            "status_code": None,
            "error": None
        }
        
        try:
            start_time = time.time()
            
            if method == "GET":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            elif method == "POST":
                response = requests.post(
                    f"{base_url}{endpoint}", 
                    json={"test": True}, 
                    timeout=10
                )
            
            response_time = time.time() - start_time
            result["response_time"] = round(response_time * 1000, 2)
            result["status_code"] = response.status_code
            
            if 200 <= response.status_code < 300:
                result["status"] = "healthy"
                print(f"  ✅ {response.status_code} ({result['response_time']}ms)")
            else:
                result["status"] = "unhealthy"
                all_healthy = False
                print(f"  ❌ {response.status_code} ({result['response_time']}ms)")
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            all_healthy = False
            print(f"  ❌ Error: {e}")
        
        endpoint_results.append(result)
    
    print()
    return all_healthy, endpoint_results

def check_render_configuration():
    """Verifica configuração específica do Render"""
    print("⚙️ VERIFICAÇÃO DE CONFIGURAÇÃO RENDER...")
    print("-" * 40)
    
    # Verificar se o render.yaml existe
    try:
        with open("render.yaml", "r") as f:
            print("✅ render.yaml encontrado")
            
        # Verificar start.sh
        with open("microservices/diagnostic_service/start.sh", "r") as f:
            print("✅ start.sh encontrado")
            
        # Verificar requirements.txt
        with open("microservices/diagnostic_service/requirements.txt", "r") as f:
            print("✅ requirements.txt encontrado")
            
    except FileNotFoundError as e:
        print(f"❌ Arquivo não encontrado: {e}")
    
    print()

def generate_report(backend_results: Dict, frontend_results: Dict, endpoint_results: List[Dict]):
    """Gera relatório final"""
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    
    # Status geral
    backend_healthy = backend_results["status"] == "healthy"
    frontend_healthy = frontend_results["status"] == "healthy"
    endpoints_healthy = all(r["status"] == "healthy" for r in endpoint_results)
    
    overall_status = backend_healthy and frontend_healthy and endpoints_healthy
    
    print(f"🎯 STATUS GERAL: {'✅ SAUDÁVEL' if overall_status else '❌ PROBLEMAS DETECTADOS'}")
    print()
    
    # Detalhes dos serviços
    print("🔍 DETALHES DOS SERVIÇOS:")
    print(f"  Backend:  {'✅' if backend_healthy else '❌'} ({backend_results.get('response_time', 'N/A')}ms)")
    print(f"  Frontend: {'✅' if frontend_healthy else '❌'} ({frontend_results.get('response_time', 'N/A')}ms)")
    print()
    
    # Endpoints com problemas
    failed_endpoints = [r for r in endpoint_results if r["status"] != "healthy"]
    if failed_endpoints:
        print("❌ ENDPOINTS COM PROBLEMAS:")
        for endpoint in failed_endpoints:
            print(f"  {endpoint['method']} {endpoint['endpoint']} - {endpoint.get('error', 'Status não-200')}")
        print()
    
    # Recomendações
    print("💡 RECOMENDAÇÕES:")
    if not backend_healthy:
        print("  🔧 Verificar logs do backend no Render Dashboard")
        print("  🔧 Validar variáveis de ambiente")
        print("  🔧 Verificar start.sh e dependências")
    
    if not frontend_healthy:
        print("  🔧 Verificar build do frontend")
        print("  🔧 Validar configuração do Vite")
    
    if failed_endpoints:
        print("  🔧 Verificar conectividade entre serviços")
        print("  🔧 Validar configuração de CORS")
    
    if overall_status:
        print("  🎉 Sistema funcionando perfeitamente!")
        print("  📈 Considerar monitoramento contínuo")
    
    print()
    
    # URLs úteis
    print("🔗 LINKS ÚTEIS:")
    print("  📊 Render Dashboard: https://dashboard.render.com/")
    print("  🌐 Backend: https://techze-diagnostico-api.onrender.com")
    print("  🌐 Frontend: https://techze-diagnostico-frontend.onrender.com")
    print("  📚 Documentação: https://techze-diagnostico-api.onrender.com/docs")

def main():
    """Função principal"""
    print_header()
    
    # Verificar configuração local
    check_render_configuration()
    
    # Verificar serviços
    backend_healthy, backend_results = check_service_basic("backend", SERVICES["backend"])
    frontend_healthy, frontend_results = check_service_basic("frontend", SERVICES["frontend"])
    
    # Testar endpoints do backend se estiver online
    endpoint_results = []
    if backend_healthy:
        endpoints_healthy, endpoint_results = check_backend_endpoints(SERVICES["backend"])
    
    # Gerar relatório
    generate_report(backend_results, frontend_results, endpoint_results)
    
    # Salvar relatório em JSON
    report = {
        "timestamp": datetime.now().isoformat(),
        "backend": backend_results,
        "frontend": frontend_results,
        "endpoints": endpoint_results,
        "overall_status": backend_healthy and frontend_healthy and all(r["status"] == "healthy" for r in endpoint_results)
    }
    
    with open("render_health_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"💾 Relatório salvo em: render_health_report.json")

if __name__ == "__main__":
    main() 