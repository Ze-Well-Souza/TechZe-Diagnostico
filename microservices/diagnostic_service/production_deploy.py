#!/usr/bin/env python3
"""
Script de Deploy e Validação para Produção - TechZe Diagnostic Service

Executa todas as verificações necessárias antes de colocar o sistema em produção.
"""

import os
import sys
import time
import asyncio
import subprocess
import requests
import psutil
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class TestResult(Enum):
    PASS = "✅"
    FAIL = "❌"
    WARNING = "⚠️"
    SKIP = "⏭️"

@dataclass
class DeployCheck:
    name: str
    result: TestResult
    message: str
    duration: float
    details: Optional[Dict[str, Any]] = None

class ProductionDeployValidator:
    """Validador para deploy em produção"""
    
    def __init__(self):
        self.results: List[DeployCheck] = []
        self.start_time = time.time()
    
    def run_all_checks(self) -> bool:
        """Executa todas as validações de deploy"""
        print("🚀 INICIANDO VALIDAÇÃO PARA PRODUÇÃO - TECHZE DIAGNOSTIC SERVICE")
        print("=" * 70)
        
        checks = [
            ("Configuração do Ambiente", self.check_environment),
            ("Dependências Python", self.check_dependencies),
            ("Estrutura da API", self.check_api_structure),
            ("Testes de Integração", self.check_integration_tests),
            ("Recursos do Sistema", self.check_system_resources),
            ("Segurança", self.check_security),
            ("Performance", self.check_performance),
            ("Health Checks", self.check_health_endpoints),
            ("Docker/Containers", self.check_docker),
            ("Logs e Monitoramento", self.check_monitoring)
        ]
        
        for check_name, check_func in checks:
            self.run_check(check_name, check_func)
        
        return self.generate_report()
    
    def run_check(self, name: str, check_func):
        """Executa uma verificação específica"""
        print(f"\n📋 {name}...")
        start_time = time.time()
        
        try:
            result, message, details = check_func()
            duration = time.time() - start_time
            
            check = DeployCheck(
                name=name,
                result=result,
                message=message,
                duration=duration,
                details=details
            )
            
            self.results.append(check)
            print(f"   {result.value} {message} ({duration:.2f}s)")
            
            if details and result != TestResult.PASS:
                for key, value in details.items():
                    print(f"      • {key}: {value}")
                    
        except Exception as e:
            duration = time.time() - start_time
            check = DeployCheck(
                name=name,
                result=TestResult.FAIL,
                message=f"Erro na verificação: {e}",
                duration=duration
            )
            self.results.append(check)
            print(f"   ❌ Erro na verificação: {e}")
    
    def check_environment(self) -> tuple:
        """Verifica configurações de ambiente"""
        issues = []
        
        # Verificar variáveis críticas
        required_vars = ["ENVIRONMENT", "JWT_SECRET_KEY", "DATABASE_URL"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            issues.append(f"Variáveis ausentes: {', '.join(missing_vars)}")
        
        # Verificar modo de produção
        if os.getenv("DEBUG", "false").lower() == "true":
            issues.append("DEBUG=true em produção")
        
        if os.getenv("ENVIRONMENT") != "production":
            issues.append("ENVIRONMENT não é 'production'")
        
        if issues:
            return TestResult.FAIL, f"Problemas de configuração: {'; '.join(issues)}", {"issues": issues}
        
        return TestResult.PASS, "Configuração de ambiente OK", None
    
    def check_dependencies(self) -> tuple:
        """Verifica dependências Python"""
        try:
            # Verificar imports críticos
            critical_imports = [
                "fastapi", "uvicorn", "sqlalchemy", "psycopg2", 
                "redis", "jwt", "passlib", "psutil"
            ]
            
            missing = []
            for package in critical_imports:
                try:
                    __import__(package)
                except ImportError:
                    missing.append(package)
            
            if missing:
                return TestResult.FAIL, f"Dependências ausentes: {', '.join(missing)}", {"missing": missing}
            
            return TestResult.PASS, "Todas as dependências OK", None
            
        except Exception as e:
            return TestResult.FAIL, f"Erro ao verificar dependências: {e}", None
    
    def check_api_structure(self) -> tuple:
        """Verifica estrutura da API"""
        try:
            # Verificar arquivos críticos
            critical_files = [
                "app/main.py",
                "app/api/core/router.py",
                "app/api/core/auth/endpoints.py",
                "app/api/core/diagnostics/endpoints.py"
            ]
            
            missing_files = []
            for file_path in critical_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)
            
            if missing_files:
                return TestResult.FAIL, f"Arquivos ausentes: {', '.join(missing_files)}", {"missing": missing_files}
            
            return TestResult.PASS, "Estrutura da API completa", None
            
        except Exception as e:
            return TestResult.FAIL, f"Erro ao verificar estrutura: {e}", None
    
    def check_integration_tests(self) -> tuple:
        """Executa testes de integração"""
        try:
            # Executar testes
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/test_integration_core.py", "-v"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return TestResult.PASS, "Todos os testes passaram", {"stdout": result.stdout}
            else:
                return TestResult.FAIL, "Testes falharam", {"stderr": result.stderr}
                
        except subprocess.TimeoutExpired:
            return TestResult.FAIL, "Timeout nos testes", None
        except Exception as e:
            return TestResult.WARNING, f"Não foi possível executar testes: {e}", None
    
    def check_system_resources(self) -> tuple:
        """Verifica recursos do sistema"""
        try:
            issues = []
            
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 80:
                issues.append(f"CPU alta: {cpu_percent}%")
            
            # Memória
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                issues.append(f"Memória alta: {memory.percent}%")
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > 85:
                issues.append(f"Disco cheio: {disk_percent:.1f}%")
            
            if issues:
                return TestResult.WARNING, f"Recursos limitados: {'; '.join(issues)}", {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "disk_percent": disk_percent
                }
            
            return TestResult.PASS, "Recursos suficientes", {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk_percent
            }
            
        except Exception as e:
            return TestResult.WARNING, f"Não foi possível verificar recursos: {e}", None
    
    def check_security(self) -> tuple:
        """Verifica configurações de segurança"""
        issues = []
        
        # JWT Secret
        jwt_secret = os.getenv("JWT_SECRET_KEY", "")
        if len(jwt_secret) < 32:
            issues.append("JWT secret muito curto")
        
        if jwt_secret == "dev-secret-key-change-in-production":
            issues.append("JWT secret ainda é o padrão de desenvolvimento")
        
        # Debug mode
        if os.getenv("DEBUG", "false").lower() == "true":
            issues.append("DEBUG habilitado em produção")
        
        if issues:
            return TestResult.FAIL, f"Problemas de segurança: {'; '.join(issues)}", {"issues": issues}
        
        return TestResult.PASS, "Configurações de segurança OK", None
    
    def check_performance(self) -> tuple:
        """Testa performance básica"""
        try:
            # Simular carga básica
            start_time = time.time()
            
            # Teste simples de import da aplicação
            from app.main import app
            
            load_time = time.time() - start_time
            
            if load_time > 5.0:
                return TestResult.WARNING, f"Carregamento lento: {load_time:.2f}s", {"load_time": load_time}
            
            return TestResult.PASS, f"Performance adequada: {load_time:.2f}s", {"load_time": load_time}
            
        except Exception as e:
            return TestResult.FAIL, f"Erro no teste de performance: {e}", None
    
    def check_health_endpoints(self) -> tuple:
        """Verifica endpoints de health check"""
        try:
            from fastapi.testclient import TestClient
            from app.main import app
            
            client = TestClient(app)
            
            # Testar endpoints críticos
            endpoints = [
                "/api/core/diagnostics/health",
                "/api/core/diagnostics/info",
                "/api/core/auth/health"
            ]
            
            failed_endpoints = []
            for endpoint in endpoints:
                response = client.get(endpoint)
                if response.status_code != 200:
                    failed_endpoints.append(f"{endpoint} ({response.status_code})")
            
            if failed_endpoints:
                return TestResult.FAIL, f"Endpoints falhando: {', '.join(failed_endpoints)}", {"failed": failed_endpoints}
            
            return TestResult.PASS, "Todos os health checks OK", None
            
        except Exception as e:
            return TestResult.FAIL, f"Erro ao testar endpoints: {e}", None
    
    def check_docker(self) -> tuple:
        """Verifica configuração Docker"""
        try:
            docker_files = ["Dockerfile", "docker-compose.yml"]
            missing = [f for f in docker_files if not os.path.exists(f)]
            
            if missing:
                return TestResult.WARNING, f"Arquivos Docker ausentes: {', '.join(missing)}", {"missing": missing}
            
            return TestResult.PASS, "Configuração Docker presente", None
            
        except Exception as e:
            return TestResult.WARNING, f"Não foi possível verificar Docker: {e}", None
    
    def check_monitoring(self) -> tuple:
        """Verifica configuração de logs e monitoramento"""
        try:
            log_issues = []
            
            # Verificar configuração de logging
            log_level = os.getenv("LOG_LEVEL", "INFO")
            if log_level == "DEBUG":
                log_issues.append("LOG_LEVEL=DEBUG em produção")
            
            # Verificar se Sentry está configurado
            if not os.getenv("SENTRY_DSN"):
                log_issues.append("SENTRY_DSN não configurado")
            
            if log_issues:
                return TestResult.WARNING, f"Problemas de monitoramento: {'; '.join(log_issues)}", {"issues": log_issues}
            
            return TestResult.PASS, "Configuração de monitoramento OK", None
            
        except Exception as e:
            return TestResult.WARNING, f"Erro ao verificar monitoramento: {e}", None
    
    def generate_report(self) -> bool:
        """Gera relatório final"""
        total_time = time.time() - self.start_time
        
        passed = sum(1 for r in self.results if r.result == TestResult.PASS)
        failed = sum(1 for r in self.results if r.result == TestResult.FAIL)
        warnings = sum(1 for r in self.results if r.result == TestResult.WARNING)
        total = len(self.results)
        
        print("\n" + "=" * 70)
        print("📊 RELATÓRIO FINAL DE VALIDAÇÃO")
        print("=" * 70)
        
        print(f"⏱️  Tempo total: {total_time:.2f}s")
        print(f"📋 Total de verificações: {total}")
        print(f"✅ Passaram: {passed}")
        print(f"⚠️  Avisos: {warnings}")
        print(f"❌ Falharam: {failed}")
        
        # Resumo por categoria
        if failed > 0:
            print("\n❌ VERIFICAÇÕES QUE FALHARAM:")
            for result in self.results:
                if result.result == TestResult.FAIL:
                    print(f"   • {result.name}: {result.message}")
        
        if warnings > 0:
            print("\n⚠️  AVISOS:")
            for result in self.results:
                if result.result == TestResult.WARNING:
                    print(f"   • {result.name}: {result.message}")
        
        # Decisão final
        print("\n" + "=" * 70)
        if failed == 0:
            if warnings == 0:
                print("🎉 SISTEMA PRONTO PARA PRODUÇÃO!")
                print("✅ Todas as verificações passaram com sucesso.")
                return True
            else:
                print("✅ SISTEMA APROVADO PARA PRODUÇÃO COM AVISOS")
                print("⚠️  Alguns avisos foram encontrados, mas não impedem o deploy.")
                return True
        else:
            print("❌ SISTEMA NÃO PRONTO PARA PRODUÇÃO")
            print("🔧 Corrija os problemas encontrados antes do deploy.")
            return False

def main():
    """Função principal"""
    validator = ProductionDeployValidator()
    success = validator.run_all_checks()
    
    if success:
        print("\n🚀 Execute o deploy com:")
        print("   docker-compose -f docker-compose.prod.yml up -d")
        sys.exit(0)
    else:
        print("\n🛠️  Corrija os problemas e execute novamente:")
        print("   python production_deploy.py")
        sys.exit(1)

if __name__ == "__main__":
    main() 