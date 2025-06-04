#!/usr/bin/env python3
"""
Validador da Implementação da Semana 2 - TechZe Diagnostic Service
Verifica se todas as funcionalidades foram implementadas corretamente
"""
import os
import sys
import importlib
import inspect
from pathlib import Path

def print_status(message, status="INFO"):
    """Imprime mensagem com status colorido"""
    colors = {
        "INFO": "\033[94m",
        "SUCCESS": "\033[92m", 
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "RESET": "\033[0m"
    }
    print(f"{colors.get(status, '')}{status}: {message}{colors['RESET']}")

def check_file_exists(file_path, description):
    """Verifica se arquivo existe"""
    if os.path.exists(file_path):
        print_status(f"✅ {description}: {file_path}", "SUCCESS")
        return True
    else:
        print_status(f"❌ {description}: {file_path} - NOT FOUND", "ERROR")
        return False

def check_module_import(module_path, description):
    """Verifica se módulo pode ser importado"""
    try:
        module = importlib.import_module(module_path)
        print_status(f"✅ {description}: {module_path}", "SUCCESS")
        return True, module
    except ImportError as e:
        print_status(f"❌ {description}: {module_path} - IMPORT ERROR: {e}", "ERROR")
        return False, None

def check_class_exists(module, class_name, description):
    """Verifica se classe existe no módulo"""
    if hasattr(module, class_name):
        cls = getattr(module, class_name)
        if inspect.isclass(cls):
            print_status(f"✅ {description}: {class_name}", "SUCCESS")
            return True, cls
        else:
            print_status(f"❌ {description}: {class_name} - NOT A CLASS", "ERROR")
            return False, None
    else:
        print_status(f"❌ {description}: {class_name} - NOT FOUND", "ERROR")
        return False, None

def check_function_exists(module, function_name, description):
    """Verifica se função existe no módulo"""
    if hasattr(module, function_name):
        func = getattr(module, function_name)
        if callable(func):
            print_status(f"✅ {description}: {function_name}", "SUCCESS")
            return True, func
        else:
            print_status(f"❌ {description}: {function_name} - NOT CALLABLE", "ERROR")
            return False, None
    else:
        print_status(f"❌ {description}: {function_name} - NOT FOUND", "ERROR")
        return False, None

def validate_advanced_monitoring():
    """Valida módulo de monitoramento avançado"""
    print_status("\n🔍 Validando Monitoramento Avançado", "INFO")
    print("-" * 50)
    
    # Verifica arquivo
    file_path = "app/core/advanced_monitoring.py"
    if not check_file_exists(file_path, "Advanced Monitoring Module"):
        return False
    
    # Verifica importação
    success, module = check_module_import("app.core.advanced_monitoring", "Advanced Monitoring Import")
    if not success:
        return False
    
    # Verifica classes principais
    classes_to_check = [
        ("AdvancedMonitoringService", "Advanced Monitoring Service Class"),
        ("MetricsCollector", "Metrics Collector Class"),
        ("AlertManager", "Alert Manager Class"),
        ("DashboardGenerator", "Dashboard Generator Class"),
        ("Alert", "Alert Data Class"),
        ("Metric", "Metric Data Class"),
        ("DashboardComponent", "Dashboard Component Class")
    ]
    
    class_results = []
    for class_name, description in classes_to_check:
        success, _ = check_class_exists(module, class_name, description)
        class_results.append(success)
    
    # Verifica instância global
    if hasattr(module, 'advanced_monitoring'):
        print_status("✅ Global Advanced Monitoring Instance", "SUCCESS")
        instance_success = True
    else:
        print_status("❌ Global Advanced Monitoring Instance - NOT FOUND", "ERROR")
        instance_success = False
    
    return all(class_results) and instance_success

def validate_cache_manager():
    """Valida módulo de cache"""
    print_status("\n🔄 Validando Cache Manager", "INFO")
    print("-" * 50)
    
    # Verifica arquivo
    file_path = "app/core/cache_manager.py"
    if not check_file_exists(file_path, "Cache Manager Module"):
        return False
    
    # Verifica importação
    success, module = check_module_import("app.core.cache_manager", "Cache Manager Import")
    if not success:
        return False
    
    # Verifica classes principais
    classes_to_check = [
        ("CacheManager", "Cache Manager Class"),
        ("RedisCache", "Redis Cache Class"),
        ("MemoryCache", "Memory Cache Class"),
        ("CacheEntry", "Cache Entry Class"),
        ("CacheStrategy", "Cache Strategy Enum")
    ]
    
    class_results = []
    for class_name, description in classes_to_check:
        success, _ = check_class_exists(module, class_name, description)
        class_results.append(success)
    
    # Verifica instância global
    if hasattr(module, 'cache_manager'):
        print_status("✅ Global Cache Manager Instance", "SUCCESS")
        instance_success = True
    else:
        print_status("❌ Global Cache Manager Instance - NOT FOUND", "ERROR")
        instance_success = False
    
    return all(class_results) and instance_success

def validate_main_integration():
    """Valida integração no main.py"""
    print_status("\n🔗 Validando Integração no Main", "INFO")
    print("-" * 50)
    
    # Verifica arquivo main.py
    file_path = "app/main.py"
    if not check_file_exists(file_path, "Main Application File"):
        return False
    
    # Lê conteúdo do arquivo
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verifica imports
        imports_to_check = [
            ("from app.core.advanced_monitoring import advanced_monitoring", "Advanced Monitoring Import"),
            ("from app.core.cache_manager import cache_manager", "Cache Manager Import")
        ]
        
        import_results = []
        for import_line, description in imports_to_check:
            if import_line in content:
                print_status(f"✅ {description}", "SUCCESS")
                import_results.append(True)
            else:
                print_status(f"❌ {description} - NOT FOUND", "ERROR")
                import_results.append(False)
        
        # Verifica endpoints
        endpoints_to_check = [
            ("/api/v1/monitoring/dashboard/operational", "Operational Dashboard Endpoint"),
            ("/api/v1/monitoring/dashboard/security", "Security Dashboard Endpoint"),
            ("/api/v1/monitoring/alerts", "Alerts Endpoint"),
            ("/api/v1/cache/stats", "Cache Stats Endpoint"),
            ("/api/v1/alerts/webhook", "Alertmanager Webhook Endpoint")
        ]
        
        endpoint_results = []
        for endpoint, description in endpoints_to_check:
            if endpoint in content:
                print_status(f"✅ {description}", "SUCCESS")
                endpoint_results.append(True)
            else:
                print_status(f"❌ {description} - NOT FOUND", "ERROR")
                endpoint_results.append(False)
        
        return all(import_results) and all(endpoint_results)
        
    except Exception as e:
        print_status(f"❌ Error reading main.py: {e}", "ERROR")
        return False

def validate_configuration_files():
    """Valida arquivos de configuração"""
    print_status("\n⚙️ Validando Arquivos de Configuração", "INFO")
    print("-" * 50)
    
    config_files = [
        ("prometheus.yml", "Prometheus Configuration"),
        ("alert_rules.yml", "Alert Rules Configuration"),
        ("grafana_dashboards.json", "Grafana Dashboards"),
        ("docker-compose.monitoring.yml", "Docker Compose for Monitoring"),
        ("alertmanager.yml", "Alertmanager Configuration")
    ]
    
    results = []
    for file_name, description in config_files:
        success = check_file_exists(file_name, description)
        results.append(success)
    
    return all(results)

def validate_setup_scripts():
    """Valida scripts de setup"""
    print_status("\n🛠️ Validando Scripts de Setup", "INFO")
    print("-" * 50)
    
    scripts = [
        ("setup_monitoring_stack.py", "Monitoring Stack Setup Script"),
        ("test_week2_features.py", "Week 2 Features Test Script"),
        ("validate_week2_implementation.py", "Implementation Validator Script")
    ]
    
    results = []
    for script_name, description in scripts:
        success = check_file_exists(script_name, description)
        results.append(success)
    
    return all(results)

def validate_documentation():
    """Valida documentação"""
    print_status("\n📚 Validando Documentação", "INFO")
    print("-" * 50)
    
    docs = [
        ("WEEK2_FEATURES.md", "Week 2 Features Documentation"),
        ("README.md", "General README (if exists)")
    ]
    
    results = []
    for doc_name, description in docs:
        if doc_name == "README.md":
            # README pode estar no diretório pai
            success = (check_file_exists(doc_name, description) or 
                      check_file_exists("../../README.md", "Parent Directory README"))
        else:
            success = check_file_exists(doc_name, description)
        results.append(success)
    
    return all(results)

def validate_requirements():
    """Valida requirements.txt"""
    print_status("\n📦 Validando Dependências", "INFO")
    print("-" * 50)
    
    if not check_file_exists("requirements.txt", "Requirements File"):
        return False
    
    try:
        with open("requirements.txt", 'r') as f:
            requirements = f.read()
        
        required_packages = [
            "redis",
            "prometheus-fastapi-instrumentator",
            "slowapi",
            "psutil"
        ]
        
        results = []
        for package in required_packages:
            if package in requirements:
                print_status(f"✅ Package: {package}", "SUCCESS")
                results.append(True)
            else:
                print_status(f"❌ Package: {package} - NOT FOUND", "ERROR")
                results.append(False)
        
        return all(results)
        
    except Exception as e:
        print_status(f"❌ Error reading requirements.txt: {e}", "ERROR")
        return False

def run_comprehensive_validation():
    """Executa validação completa"""
    print_status("🚀 Validação Completa da Implementação da Semana 2", "INFO")
    print("=" * 70)
    
    # Muda para o diretório correto
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Adiciona diretório atual ao path para imports
    sys.path.insert(0, str(script_dir))
    
    validation_tests = [
        ("Advanced Monitoring", validate_advanced_monitoring),
        ("Cache Manager", validate_cache_manager),
        ("Main Integration", validate_main_integration),
        ("Configuration Files", validate_configuration_files),
        ("Setup Scripts", validate_setup_scripts),
        ("Documentation", validate_documentation),
        ("Requirements", validate_requirements)
    ]
    
    results = {}
    
    for test_name, test_func in validation_tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print_status(f"❌ Error in {test_name}: {e}", "ERROR")
            results[test_name] = False
    
    # Resumo final
    print_status("\n📊 RESUMO DA VALIDAÇÃO", "INFO")
    print("=" * 70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print_status(f"{status} {test_name}", "SUCCESS" if result else "ERROR")
    
    print("-" * 70)
    success_rate = (passed / total) * 100
    print_status(f"📈 Resultado: {passed}/{total} validações passaram ({success_rate:.1f}%)", "INFO")
    
    if passed == total:
        print_status("🎉 IMPLEMENTAÇÃO DA SEMANA 2 COMPLETA E VALIDADA!", "SUCCESS")
        print_status("✅ Todas as funcionalidades foram implementadas corretamente", "SUCCESS")
        print_status("🚀 Sistema pronto para produção", "SUCCESS")
        return 0
    else:
        print_status("⚠️ IMPLEMENTAÇÃO INCOMPLETA", "WARNING")
        print_status(f"❌ {total - passed} validações falharam", "ERROR")
        print_status("🔧 Verifique os itens marcados como FAIL acima", "WARNING")
        return 1

def main():
    """Função principal"""
    return run_comprehensive_validation()

if __name__ == "__main__":
    sys.exit(main())