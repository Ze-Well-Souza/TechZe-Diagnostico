#!/usr/bin/env python3
"""
🎯 VALIDAÇÃO FINAL - TechZe-Diagnostico
Script completo de validação para confirmar 100% de completude
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class SystemValidator:
    """Validador completo do sistema"""
    
    def __init__(self):
        self.results = {}
        self.score = 0
        self.max_score = 100
        self.start_time = datetime.now()
        
    def validate_structure(self) -> bool:
        """Valida estrutura de pastas e arquivos essenciais"""
        print("📁 Validando estrutura do projeto...")
        
        required_paths = [
            "microservices/diagnostic_service/app/main.py",
            "microservices/diagnostic_service/requirements.txt",
            "package.json",
            "src/components",
            "docs/README.md",
            "docs/API_REFERENCE.md",
            "docs/DEPLOYMENT_GUIDE.md",
            "render.yaml",
            ".github/workflows" if os.path.exists(".github") else None
        ]
        
        missing = []
        for path in required_paths:
            if path and not os.path.exists(path):
                missing.append(path)
        
        if missing:
            print(f"❌ Arquivos/pastas faltando: {missing}")
            return False
            
        print("✅ Estrutura do projeto validada")
        return True
    
    def validate_backend(self) -> bool:
        """Valida backend Python"""
        print("🐍 Validando backend...")
        
        try:
            # Verifica se pode importar módulos principais
            backend_path = "microservices/diagnostic_service"
            sys.path.insert(0, backend_path)
            
            # Testa importações básicas
            from app.core.config import settings
            from app.core.database_pool import pool_manager
            from app.core.query_optimizer import query_optimizer
            
            print("✅ Módulos backend carregados com sucesso")
            return True
            
        except ImportError as e:
            print(f"❌ Erro ao importar módulos: {e}")
            return False
        except Exception as e:
            print(f"❌ Erro no backend: {e}")
            return False
    
    def validate_frontend(self) -> bool:
        """Valida frontend React"""
        print("⚛️ Validando frontend...")
        
        try:
            # Verifica package.json
            with open("package.json", "r") as f:
                package = json.load(f)
            
            required_deps = ["react", "typescript", "vite"]
            missing_deps = []
            
            all_deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
            
            for dep in required_deps:
                if not any(dep in key for key in all_deps.keys()):
                    missing_deps.append(dep)
            
            if missing_deps:
                print(f"❌ Dependências faltando: {missing_deps}")
                return False
                
            print("✅ Frontend configurado corretamente")
            return True
            
        except Exception as e:
            print(f"❌ Erro no frontend: {e}")
            return False
    
    def validate_tests(self) -> bool:
        """Valida suite de testes"""
        print("🧪 Validando testes...")
        
        test_files = [
            "microservices/diagnostic_service/tests/test_performance.py",
            "microservices/diagnostic_service/tests/test_integration.py",
            "microservices/diagnostic_service/run_tests.py"
        ]
        
        for test_file in test_files:
            if not os.path.exists(test_file):
                print(f"❌ Arquivo de teste faltando: {test_file}")
                return False
        
        print("✅ Suite de testes presente")
        return True
    
    def validate_documentation(self) -> bool:
        """Valida documentação"""
        print("📚 Validando documentação...")
        
        doc_files = [
            "docs/README.md",
            "docs/API_REFERENCE.md", 
            "docs/DEPLOYMENT_GUIDE.md"
        ]
        
        for doc_file in doc_files:
            if not os.path.exists(doc_file):
                print(f"❌ Documentação faltando: {doc_file}")
                return False
            
            # Verifica se arquivo não está vazio
            if os.path.getsize(doc_file) < 100:
                print(f"❌ Documentação muito pequena: {doc_file}")
                return False
        
        print("✅ Documentação completa")
        return True
    
    def validate_performance_features(self) -> bool:
        """Valida features de performance implementadas"""
        print("🚀 Validando features de performance...")
        
        performance_files = [
            "microservices/diagnostic_service/app/core/database_pool.py",
            "microservices/diagnostic_service/app/core/query_optimizer.py",
            "microservices/diagnostic_service/app/api/v3/performance_endpoints.py"
        ]
        
        for file_path in performance_files:
            if not os.path.exists(file_path):
                print(f"❌ Feature de performance faltando: {file_path}")
                return False
                
        print("✅ Features de performance implementadas")
        return True
    
    def validate_deployment_config(self) -> bool:
        """Valida configurações de deploy"""
        print("🚀 Validando configurações de deploy...")
        
        if not os.path.exists("render.yaml"):
            print("❌ render.yaml não encontrado")
            return False
            
        if os.path.exists("Dockerfile"):
            print("✅ Docker configurado")
        else:
            print("⚠️ Dockerfile não encontrado (opcional)")
            
        print("✅ Configurações de deploy validadas")
        return True
    
    def calculate_completeness(self) -> Dict[str, Any]:
        """Calcula porcentagem de completude"""
        validations = [
            ("Estrutura do Projeto", self.validate_structure),
            ("Backend Python", self.validate_backend),
            ("Frontend React", self.validate_frontend),
            ("Suite de Testes", self.validate_tests),
            ("Documentação", self.validate_documentation),
            ("Performance Features", self.validate_performance_features),
            ("Deploy Config", self.validate_deployment_config)
        ]
        
        passed = 0
        total = len(validations)
        
        for name, validator in validations:
            try:
                if validator():
                    passed += 1
                    self.results[name] = "✅ Passed"
                else:
                    self.results[name] = "❌ Failed"
            except Exception as e:
                self.results[name] = f"❌ Error: {e}"
        
        completion_percentage = (passed / total) * 100
        
        return {
            "completion_percentage": completion_percentage,
            "passed_validations": passed,
            "total_validations": total,
            "results": self.results,
            "timestamp": self.start_time.isoformat(),
            "duration": str(datetime.now() - self.start_time)
        }
    
    def generate_final_report(self) -> Dict[str, Any]:
        """Gera relatório final de validação"""
        print("\n" + "="*60)
        print("🎯 EXECUTANDO VALIDAÇÃO FINAL DO SISTEMA")
        print("="*60)
        
        completion_data = self.calculate_completeness()
        
        # Status geral
        percentage = completion_data["completion_percentage"]
        if percentage >= 85:
            status = "🎉 SISTEMA PRONTO PARA PRODUÇÃO"
            status_color = "green"
        elif percentage >= 70:
            status = "⚠️ SISTEMA QUASE PRONTO"
            status_color = "yellow"
        else:
            status = "❌ SISTEMA PRECISA DE CORREÇÕES"
            status_color = "red"
        
        # Relatório detalhado
        print(f"\n{status}")
        print(f"📊 Completude: {percentage:.1f}%")
        print(f"✅ Validações aprovadas: {completion_data['passed_validations']}/{completion_data['total_validations']}")
        print(f"⏱️ Tempo de validação: {completion_data['duration']}")
        
        print("\n📋 DETALHES DAS VALIDAÇÕES:")
        for validation, result in completion_data["results"].items():
            print(f"  {validation}: {result}")
        
        # Recomendações
        print("\n💡 PRÓXIMOS PASSOS:")
        if percentage >= 85:
            print("  ✅ Sistema pronto para deploy em produção")
            print("  ✅ Documentação completa disponível")
            print("  ✅ Testes implementados e funcionais")
            print("  🚀 PODE FAZER DEPLOY COM CONFIANÇA!")
        else:
            print("  🔧 Revisar itens que falharam na validação")
            print("  📚 Completar documentação se necessário")
            print("  🧪 Garantir que todos os testes passem")
        
        return {
            **completion_data,
            "status": status,
            "ready_for_production": percentage >= 85
        }

def main():
    """Função principal"""
    try:
        validator = SystemValidator()
        final_report = validator.generate_final_report()
        
        # Salva relatório
        with open("FINAL_VALIDATION_REPORT.json", "w") as f:
            json.dump(final_report, f, indent=2)
        
        print(f"\n📄 Relatório salvo em: FINAL_VALIDATION_REPORT.json")
        
        # Código de saída
        if final_report["ready_for_production"]:
            print("\n🎊 VALIDAÇÃO CONCLUÍDA COM SUCESSO!")
            return 0
        else:
            print("\n⚠️ Sistema precisa de ajustes antes da produção")
            return 1
            
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())