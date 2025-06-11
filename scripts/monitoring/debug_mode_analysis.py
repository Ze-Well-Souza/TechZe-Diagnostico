#!/usr/bin/env python3
"""
🔍 MODO DEPURAÇÃO COMPLETA - TechZe Diagnostic Service
Análise profunda de todos os aspectos do projeto
"""

import os
import sys
import json
import ast
import importlib.util
import traceback
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import subprocess

class TechZeDebugAnalyzer:
    """Analisador completo de depuração do projeto TechZe"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.successes = []
        self.api_analysis = {}
        
    def log_issue(self, category: str, severity: str, message: str, details: str = ""):
        """Registra um problema encontrado"""
        self.issues.append({
            "category": category,
            "severity": severity,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        
    def log_warning(self, category: str, message: str, suggestion: str = ""):
        """Registra um aviso"""
        self.warnings.append({
            "category": category,
            "message": message,
            "suggestion": suggestion,
            "timestamp": datetime.now().isoformat()
        })
        
    def log_success(self, category: str, message: str):
        """Registra um sucesso"""
        self.successes.append({
            "category": category,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

    def analyze_api_structure(self) -> Dict[str, Any]:
        """Analisa a estrutura das APIs"""
        print("🔍 Analisando estrutura das APIs...")
        
        api_structure = {
            "core": {"exists": False, "endpoints": 0, "domains": []},
            "v1": {"exists": False, "endpoints": 0, "files": []},
            "v3": {"exists": False, "endpoints": 0, "files": []},
            "legacy_dependencies": []
        }
        
        # Verifica API Core
        core_path = self.project_root / "app" / "api" / "core"
        if core_path.exists():
            api_structure["core"]["exists"] = True
            
            # Conta domínios na API Core
            domains = [d.name for d in core_path.iterdir() if d.is_dir() and not d.name.startswith("__")]
            api_structure["core"]["domains"] = domains
            
            # Conta endpoints aproximadamente
            endpoint_count = 0
            for domain_dir in core_path.iterdir():
                if domain_dir.is_dir() and not domain_dir.name.startswith("__"):
                    endpoints_file = domain_dir / "endpoints.py"
                    if endpoints_file.exists():
                        try:
                            with open(endpoints_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                endpoint_count += content.count("@router.")
                        except Exception as e:
                            self.log_warning("API_ANALYSIS", f"Erro ao ler {endpoints_file}: {e}")
            
            api_structure["core"]["endpoints"] = endpoint_count
            self.log_success("API_STRUCTURE", f"API Core encontrada com {len(domains)} domínios e ~{endpoint_count} endpoints")
        else:
            self.log_issue("API_STRUCTURE", "CRITICAL", "API Core não encontrada", str(core_path))
        
        # Verifica APIs V1 e V3
        for version in ["v1", "v3"]:
            version_path = self.project_root / "app" / "api" / version
            if version_path.exists():
                api_structure[version]["exists"] = True
                
                # Lista arquivos Python
                py_files = list(version_path.glob("*.py"))
                api_structure[version]["files"] = [f.name for f in py_files]
                
                # Conta endpoints aproximadamente
                endpoint_count = 0
                for py_file in py_files:
                    if py_file.name != "__init__.py":
                        try:
                            with open(py_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                endpoint_count += content.count("@app.") + content.count("@router.")
                        except Exception as e:
                            self.log_warning("API_ANALYSIS", f"Erro ao ler {py_file}: {e}")
                
                api_structure[version]["endpoints"] = endpoint_count
                
                if endpoint_count > 0:
                    self.log_warning("LEGACY_API", f"API {version.upper()} ainda existe com ~{endpoint_count} endpoints", 
                                   f"Considere remover se não estiver sendo usada")
                else:
                    self.log_success("LEGACY_API", f"API {version.upper()} existe mas parece vazia")
        
        return api_structure

    def check_imports_and_dependencies(self) -> List[Dict[str, Any]]:
        """Verifica imports e dependências das APIs legacy"""
        print("🔍 Verificando imports e dependências...")
        
        dependencies = []
        
        # Verifica main.py
        main_path = self.project_root / "app" / "main.py"
        if main_path.exists():
            try:
                with open(main_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Busca imports de v1 e v3
                v1_imports = [line.strip() for line in content.split('\n') if 'api.v1' in line and 'import' in line]
                v3_imports = [line.strip() for line in content.split('\n') if 'api.v3' in line and 'import' in line]
                
                if v1_imports:
                    dependencies.append({
                        "file": "app/main.py",
                        "type": "import",
                        "api_version": "v1",
                        "lines": v1_imports
                    })
                    self.log_issue("DEPENDENCY", "HIGH", "main.py tem imports da API v1", str(v1_imports))
                
                if v3_imports:
                    dependencies.append({
                        "file": "app/main.py", 
                        "type": "import",
                        "api_version": "v3",
                        "lines": v3_imports
                    })
                    self.log_issue("DEPENDENCY", "HIGH", "main.py tem imports da API v3", str(v3_imports))
                
                # Verifica include_router
                if ".include_router(v1_" in content or ".include_router(v3_" in content:
                    self.log_issue("DEPENDENCY", "CRITICAL", "main.py está carregando routers v1/v3")
                else:
                    self.log_success("DEPENDENCY", "main.py NÃO está carregando routers v1/v3")
                    
            except Exception as e:
                self.log_issue("FILE_ACCESS", "HIGH", f"Erro ao ler main.py: {e}")
        
        return dependencies

    def run_import_test(self) -> Dict[str, Any]:
        """Testa imports dos módulos principais"""
        print("🔍 Testando imports...")
        
        import_test = {
            "main_app": False,
            "api_core": False,
            "config": False,
            "errors": []
        }
        
        # Testa import do main
        try:
            sys.path.insert(0, str(self.project_root))
            from app.main import app
            import_test["main_app"] = True
            self.log_success("IMPORT", "app.main importado com sucesso")
        except Exception as e:
            import_test["errors"].append(f"app.main: {str(e)}")
            self.log_issue("IMPORT", "CRITICAL", f"Erro ao importar app.main: {e}")
        
        # Testa import da API Core
        try:
            from app.api.core.router import api_router
            import_test["api_core"] = True
            self.log_success("IMPORT", "API Core importada com sucesso")
        except Exception as e:
            import_test["errors"].append(f"api_core: {str(e)}")
            self.log_issue("IMPORT", "HIGH", f"Erro ao importar API Core: {e}")
        
        return import_test

    def can_remove_legacy_apis(self) -> bool:
        """Determina se as APIs legacy podem ser removidas com segurança"""
        # Verifica se há imports ativos das APIs v1/v3 no main.py
        main_imports_legacy = any(
            i for i in self.issues 
            if i["category"] == "DEPENDENCY" and "main.py" in i["message"] and ("v1" in i["message"] or "v3" in i["message"])
        )
        
        # Verifica se há routers sendo carregados
        router_loading_legacy = any(
            i for i in self.issues
            if i["category"] == "DEPENDENCY" and "routers v1/v3" in i["message"]
        )
        
        return not (main_imports_legacy or router_loading_legacy)

    def is_ready_for_production(self) -> bool:
        """Determina se o sistema está pronto para produção"""
        critical_issues = [i for i in self.issues if i["severity"] == "CRITICAL"]
        
        # Critérios para produção
        api_core_working = any(s for s in self.successes if "API Core" in s["message"])
        main_imports_ok = any(s for s in self.successes if "app.main importado" in s["message"])
        
        return len(critical_issues) == 0 and api_core_working and main_imports_ok

    def run_complete_analysis(self) -> Dict[str, Any]:
        """Executa análise completa"""
        print("🚀 INICIANDO MODO DEPURAÇÃO COMPLETA")
        print("=" * 60)
        
        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "project_path": str(self.project_root),
            "analysis_sections": {}
        }
        
        # Executa análises principais
        try:
            analysis_results["analysis_sections"]["api_structure"] = self.analyze_api_structure()
            analysis_results["analysis_sections"]["dependencies"] = self.check_imports_and_dependencies()
            analysis_results["analysis_sections"]["imports"] = self.run_import_test()
            
            # Gera resumo
            analysis_results["summary"] = {
                "total_issues": len(self.issues),
                "critical_issues": len([i for i in self.issues if i["severity"] == "CRITICAL"]),
                "high_issues": len([i for i in self.issues if i["severity"] == "HIGH"]),
                "warnings": len(self.warnings),
                "successes": len(self.successes),
                "can_remove_legacy_apis": self.can_remove_legacy_apis(),
                "ready_for_production": self.is_ready_for_production()
            }
            
            analysis_results["issues"] = self.issues
            analysis_results["warnings"] = self.warnings
            analysis_results["successes"] = self.successes
            
        except Exception as e:
            self.log_issue("ANALYSIS", "CRITICAL", f"Erro durante análise: {e}", traceback.format_exc())
            analysis_results["fatal_error"] = str(e)
        
        return analysis_results

def main():
    """Função principal"""
    analyzer = TechZeDebugAnalyzer()
    
    try:
        # Executa análise completa
        results = analyzer.run_complete_analysis()
        
        # Salva resultados
        output_file = "debug_analysis_report.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Exibe resumo
        print("\n" + "=" * 60)
        print("📊 RESUMO DA ANÁLISE DE DEPURAÇÃO")
        print("=" * 60)
        
        summary = results["summary"]
        print(f"🔍 Issues Críticos: {summary['critical_issues']}")
        print(f"⚠️ Issues Alta Prioridade: {summary['high_issues']}")
        print(f"📝 Warnings: {summary['warnings']}")
        print(f"✅ Sucessos: {summary['successes']}")
        print(f"🗑️ Pode remover APIs legacy: {'✅ SIM' if summary['can_remove_legacy_apis'] else '❌ NÃO'}")
        print(f"🚀 Pronto para produção: {'✅ SIM' if summary['ready_for_production'] else '❌ NÃO'}")
        
        print(f"\n📄 Relatório completo salvo em: {output_file}")
        
        return 0 if summary["ready_for_production"] else 1
        
    except Exception as e:
        print(f"❌ ERRO FATAL: {e}")
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    exit(main()) 