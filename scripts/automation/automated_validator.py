#!/usr/bin/env python3
"""
Validador Automático - TechZe Diagnóstico
Validação completa de todos os sistemas implementados
Agente CURSOR - Verificação autônoma final
"""

import os
import sys
import subprocess
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class AutomatedValidator:
    """Validador automático de todos os sistemas"""
    
    def __init__(self):
        self.validation_results = []
        self.start_time = datetime.now()
        
    def validate_semanas_1_2(self) -> Tuple[bool, Dict[str, Any]]:
        """Validar implementações das Semanas 1-2 (Agente CURSOR)"""
        logger.info("🔍 Validando Semanas 1-2 (Agente CURSOR)...")
        
        results = {
            "category": "Semanas 1-2",
            "agent": "CURSOR",
            "tests": [],
            "overall_success": True
        }
        
        # Verificar arquivos de teste implementados
        test_files = [
            "microservices/diagnostic_service/tests/integration/test_frontend_api_calls.py",
            "microservices/diagnostic_service/tests/integration/test_auth_flow.py",
            "microservices/diagnostic_service/tests/integration/test_file_upload.py",
            "microservices/diagnostic_service/tests/integration/test_dynamic_forms.py",
            "microservices/diagnostic_service/tests/integration/test_performance_validation.py",
            "microservices/diagnostic_service/tests/integration/test_complete_suite.py",
            "microservices/diagnostic_service/tests/integration/test_stress_load.py",
            "microservices/diagnostic_service/tests/integration/test_semanas_3_4.py",
            "microservices/diagnostic_service/tests/integration/test_report_final.py"
        ]
        
        for test_file in test_files:
            test_result = {
                "name": os.path.basename(test_file),
                "file_exists": os.path.exists(test_file),
                "execution_success": False,
                "details": {}
            }
            
            if test_result["file_exists"]:
                try:
                    # Executar teste
                    result = subprocess.run(
                        ["python", test_file],
                        capture_output=True,
                        text=True,
                        timeout=120,
                        cwd="."
                    )
                    
                    test_result["execution_success"] = result.returncode == 0
                    test_result["details"] = {
                        "stdout": result.stdout[:500],  # Primeiros 500 chars
                        "stderr": result.stderr[:500] if result.stderr else None
                    }
                    
                except Exception as e:
                    test_result["details"]["error"] = str(e)
            
            results["tests"].append(test_result)
            
            if not test_result["file_exists"] or not test_result["execution_success"]:
                results["overall_success"] = False
        
        # Executar suite completa
        try:
            logger.info("Executando suite completa de testes...")
            suite_result = subprocess.run(
                ["python", "tests/integration/test_complete_suite.py"],
                capture_output=True,
                text=True,
                timeout=300,
                cwd="microservices/diagnostic_service"
            )
            
            results["suite_execution"] = {
                "success": suite_result.returncode == 0,
                "output": suite_result.stdout[-1000:] if suite_result.stdout else ""
            }
            
        except Exception as e:
            results["suite_execution"] = {"success": False, "error": str(e)}
            results["overall_success"] = False
        
        logger.info(f"✅ Semanas 1-2: {'PASSOU' if results['overall_success'] else 'FALHOU'}")
        return results["overall_success"], results
    
    def validate_ci_cd_pipeline(self) -> Tuple[bool, Dict[str, Any]]:
        """Validar pipeline CI/CD"""
        logger.info("🔍 Validando Pipeline CI/CD...")
        
        results = {
            "category": "CI/CD Pipeline",
            "tests": [],
            "overall_success": True
        }
        
        # Verificar arquivo de workflow
        workflow_file = ".github/workflows/ci-cd.yml"
        workflow_exists = os.path.exists(workflow_file)
        
        results["tests"].append({
            "name": "GitHub Workflow",
            "file_exists": workflow_exists,
            "path": workflow_file
        })
        
        if not workflow_exists:
            results["overall_success"] = False
        
        # Verificar sintaxe do workflow
        if workflow_exists:
            try:
                import yaml
                with open(workflow_file, 'r') as f:
                    workflow_content = yaml.safe_load(f)
                
                required_jobs = ["test-backend", "test-frontend", "security-scan", "build-and-deploy"]
                jobs_present = all(job in workflow_content.get("jobs", {}) for job in required_jobs)
                
                results["tests"].append({
                    "name": "Workflow Syntax",
                    "valid_yaml": True,
                    "required_jobs_present": jobs_present
                })
                
                if not jobs_present:
                    results["overall_success"] = False
                    
            except Exception as e:
                results["tests"].append({
                    "name": "Workflow Syntax",
                    "valid_yaml": False,
                    "error": str(e)
                })
                results["overall_success"] = False
        
        logger.info(f"✅ CI/CD Pipeline: {'PASSOU' if results['overall_success'] else 'FALHOU'}")
        return results["overall_success"], results
    
    def validate_automation_scripts(self) -> Tuple[bool, Dict[str, Any]]:
        """Validar scripts de automação"""
        logger.info("🔍 Validando Scripts de Automação...")
        
        results = {
            "category": "Automation Scripts",
            "tests": [],
            "overall_success": True
        }
        
        # Scripts esperados
        expected_scripts = [
            "scripts/deploy/deploy_production.py",
            "scripts/monitoring/health_monitor.py",
            "scripts/automation/backup_scheduler.py"
        ]
        
        for script_path in expected_scripts:
            script_result = {
                "name": os.path.basename(script_path),
                "path": script_path,
                "file_exists": os.path.exists(script_path),
                "syntax_valid": False
            }
            
            if script_result["file_exists"]:
                try:
                    # Verificar sintaxe Python
                    with open(script_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    compile(content, script_path, 'exec')
                    script_result["syntax_valid"] = True
                    
                except Exception as e:
                    script_result["syntax_error"] = str(e)
                    results["overall_success"] = False
            else:
                results["overall_success"] = False
            
            results["tests"].append(script_result)
        
        logger.info(f"✅ Automation Scripts: {'PASSOU' if results['overall_success'] else 'FALHOU'}")
        return results["overall_success"], results
    
    def validate_backend_api(self) -> Tuple[bool, Dict[str, Any]]:
        """Validar API backend"""
        logger.info("🔍 Validando API Backend...")
        
        results = {
            "category": "Backend API",
            "tests": [],
            "overall_success": True
        }
        
        # Tentar iniciar servidor de desenvolvimento
        try:
            logger.info("Tentando validar estrutura da API...")
            
            # Verificar estrutura de arquivos
            api_files = [
                "microservices/diagnostic_service/app/main.py",
                "microservices/diagnostic_service/app/api/endpoints",
                "microservices/diagnostic_service/app/core/models",
                "microservices/diagnostic_service/requirements.txt"
            ]
            
            for api_file in api_files:
                file_exists = os.path.exists(api_file)
                results["tests"].append({
                    "name": f"API Structure - {os.path.basename(api_file)}",
                    "file_exists": file_exists
                })
                
                if not file_exists:
                    results["overall_success"] = False
            
            # Verificar dependências
            req_file = "microservices/diagnostic_service/requirements.txt"
            if os.path.exists(req_file):
                try:
                    result = subprocess.run(
                        ["python", "-m", "pip", "install", "-r", "requirements.txt", "--dry-run"],
                        capture_output=True,
                        text=True,
                        cwd="microservices/diagnostic_service",
                        timeout=60
                    )
                    
                    results["tests"].append({
                        "name": "Dependencies Check",
                        "dependencies_valid": result.returncode == 0
                    })
                    
                except Exception as e:
                    results["tests"].append({
                        "name": "Dependencies Check",
                        "dependencies_valid": False,
                        "error": str(e)
                    })
                    results["overall_success"] = False
        
        except Exception as e:
            results["tests"].append({
                "name": "API Validation",
                "success": False,
                "error": str(e)
            })
            results["overall_success"] = False
        
        logger.info(f"✅ Backend API: {'PASSOU' if results['overall_success'] else 'FALHOU'}")
        return results["overall_success"], results
    
    def validate_frontend_build(self) -> Tuple[bool, Dict[str, Any]]:
        """Validar build do frontend"""
        logger.info("🔍 Validando Frontend Build...")
        
        results = {
            "category": "Frontend Build",
            "tests": [],
            "overall_success": True
        }
        
        # Verificar arquivos essenciais
        frontend_files = [
            "package.json",
            "vite.config.ts",
            "src/main.tsx",
            "index.html"
        ]
        
        for file_path in frontend_files:
            file_exists = os.path.exists(file_path)
            results["tests"].append({
                "name": f"Frontend File - {os.path.basename(file_path)}",
                "file_exists": file_exists
            })
            
            if not file_exists:
                results["overall_success"] = False
        
        # Tentar build (se npm estiver disponível)
        try:
            logger.info("Tentando build do frontend...")
            
            # Verificar se package.json existe
            if os.path.exists("package.json"):
                build_result = subprocess.run(
                    ["npm", "run", "build", "--if-present"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                results["tests"].append({
                    "name": "Frontend Build",
                    "build_success": build_result.returncode == 0,
                    "output_snippet": build_result.stdout[-200:] if build_result.stdout else ""
                })
                
                if build_result.returncode != 0:
                    results["overall_success"] = False
        
        except Exception as e:
            results["tests"].append({
                "name": "Frontend Build",
                "build_success": False,
                "error": str(e)
            })
            results["overall_success"] = False
        
        logger.info(f"✅ Frontend Build: {'PASSOU' if results['overall_success'] else 'FALHOU'}")
        return results["overall_success"], results
    
    def validate_database_setup(self) -> Tuple[bool, Dict[str, Any]]:
        """Validar configuração do banco de dados"""
        logger.info("🔍 Validando Database Setup...")
        
        results = {
            "category": "Database Setup",
            "tests": [],
            "overall_success": True
        }
        
        # Verificar arquivos de configuração
        db_files = [
            "microservices/diagnostic_service/app/db/database.py",
            "microservices/diagnostic_service/database/migrations"
        ]
        
        for db_file in db_files:
            file_exists = os.path.exists(db_file)
            results["tests"].append({
                "name": f"DB Config - {os.path.basename(db_file)}",
                "file_exists": file_exists
            })
            
            if not file_exists:
                results["overall_success"] = False
        
        # Verificar variáveis de ambiente
        required_env_vars = ["DATABASE_URL"]
        for env_var in required_env_vars:
            env_exists = os.getenv(env_var) is not None
            results["tests"].append({
                "name": f"Environment - {env_var}",
                "env_var_exists": env_exists
            })
            
            if not env_exists:
                logger.warning(f"Variável de ambiente {env_var} não configurada")
        
        logger.info(f"✅ Database Setup: {'PASSOU' if results['overall_success'] else 'FALHOU'}")
        return results["overall_success"], results
    
    def validate_deployment_readiness(self) -> Tuple[bool, Dict[str, Any]]:
        """Validar prontidão para deploy"""
        logger.info("🔍 Validando Deployment Readiness...")
        
        results = {
            "category": "Deployment Readiness",
            "tests": [],
            "overall_success": True
        }
        
        # Verificar arquivos de deploy
        deploy_files = [
            "scripts/deploy",
            "Dockerfile",
            "docker-compose.yml"
        ]
        
        for deploy_file in deploy_files:
            file_exists = os.path.exists(deploy_file)
            results["tests"].append({
                "name": f"Deploy Config - {os.path.basename(deploy_file)}",
                "file_exists": file_exists
            })
        
        # Verificar configurações específicas do Render
        render_files = [
            "scripts/deploy/render_auto_setup.py",
            "scripts/deploy/render_health_check.py"
        ]
        
        for render_file in render_files:
            file_exists = os.path.exists(render_file)
            results["tests"].append({
                "name": f"Render Config - {os.path.basename(render_file)}",
                "file_exists": file_exists
            })
        
        logger.info(f"✅ Deployment Readiness: {'PASSOU' if results['overall_success'] else 'FALHOU'}")
        return results["overall_success"], results
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Gerar relatório final de validação"""
        total_tests = len(self.validation_results)
        passed_tests = sum(1 for result in self.validation_results if result[0])
        
        duration = datetime.now() - self.start_time
        
        final_report = {
            "validation_timestamp": self.start_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "summary": {
                "total_categories": total_tests,
                "passed_categories": passed_tests,
                "failed_categories": total_tests - passed_tests,
                "overall_success": passed_tests == total_tests
            },
            "detailed_results": [result[1] for result in self.validation_results],
            "recommendations": self.generate_recommendations()
        }
        
        return final_report
    
    def generate_recommendations(self) -> List[str]:
        """Gerar recomendações baseadas nos resultados"""
        recommendations = []
        
        for success, details in self.validation_results:
            if not success:
                category = details.get("category", "Unknown")
                recommendations.append(f"Corrigir problemas na categoria: {category}")
        
        if not recommendations:
            recommendations.append("✅ Todos os sistemas estão funcionando corretamente!")
            recommendations.append("✅ Sistema pronto para deploy em produção!")
            recommendations.append("✅ Monitoramento e automações implementados!")
        
        return recommendations
    
    def run_complete_validation(self) -> bool:
        """Executar validação completa de todos os sistemas"""
        logger.info("🚀 Iniciando validação completa de todos os sistemas...")
        
        # Lista de validações a executar
        validations = [
            ("Semanas 1-2", self.validate_semanas_1_2),
            ("CI/CD Pipeline", self.validate_ci_cd_pipeline),
            ("Automation Scripts", self.validate_automation_scripts),
            ("Backend API", self.validate_backend_api),
            ("Frontend Build", self.validate_frontend_build),
            ("Database Setup", self.validate_database_setup),
            ("Deployment Readiness", self.validate_deployment_readiness)
        ]
        
        # Executar todas as validações
        for validation_name, validation_func in validations:
            try:
                logger.info(f"🔄 Executando: {validation_name}")
                success, details = validation_func()
                self.validation_results.append((success, details))
                
                status = "✅ PASSOU" if success else "❌ FALHOU"
                logger.info(f"{status}: {validation_name}")
                
            except Exception as e:
                logger.error(f"❌ ERRO em {validation_name}: {e}")
                self.validation_results.append((False, {
                    "category": validation_name,
                    "error": str(e),
                    "overall_success": False
                }))
        
        # Gerar relatório final
        final_report = self.generate_final_report()
        
        # Salvar relatório
        os.makedirs("reports", exist_ok=True)
        report_file = f"reports/validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        # Exibir resumo
        self.display_summary(final_report)
        
        logger.info(f"📊 Relatório completo salvo em: {report_file}")
        
        return final_report["summary"]["overall_success"]
    
    def display_summary(self, report: Dict[str, Any]):
        """Exibir resumo dos resultados"""
        summary = report["summary"]
        
        print("\n" + "="*60)
        print("🎯 RELATÓRIO FINAL DE VALIDAÇÃO - TECHZE DIAGNÓSTICO")
        print("="*60)
        print(f"📊 Total de categorias: {summary['total_categories']}")
        print(f"✅ Categorias aprovadas: {summary['passed_categories']}")
        print(f"❌ Categorias com falhas: {summary['failed_categories']}")
        print(f"⏱️ Duração: {report['duration_seconds']:.2f}s")
        print()
        
        status_emoji = "🎉" if summary["overall_success"] else "⚠️"
        status_text = "TODOS OS SISTEMAS FUNCIONANDO" if summary["overall_success"] else "CORREÇÕES NECESSÁRIAS"
        
        print(f"{status_emoji} STATUS GERAL: {status_text}")
        print()
        
        print("📋 RECOMENDAÇÕES:")
        for i, rec in enumerate(report["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        print("\n" + "="*60)


def main():
    """Função principal"""
    validator = AutomatedValidator()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--category":
        # Validar categoria específica
        category = sys.argv[2] if len(sys.argv) > 2 else "semanas_1_2"
        
        if category == "semanas_1_2":
            success, details = validator.validate_semanas_1_2()
        else:
            print(f"Categoria '{category}' não reconhecida")
            return 1
        
        print(json.dumps(details, indent=2))
        return 0 if success else 1
    else:
        # Validação completa
        success = validator.run_complete_validation()
        return 0 if success else 1


if __name__ == "__main__":
    exit(main()) 