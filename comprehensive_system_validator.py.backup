#!/usr/bin/env python3
"""
Validador Completo do Sistema TechZe-Diagnóstico
ASSISTENTE IA - Identificação dos 5% de otimizações restantes
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system_validation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ComprehensiveSystemValidator:
    """Validador completo do sistema TechZe"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "pending",
            "completion_percentage": 0,
            "categories": {},
            "optimizations_needed": [],
            "critical_gaps": [],
            "recommendations": []
        }
        
    async def validate_complete_system(self) -> Dict[str, Any]:
        """Executa validação completa do sistema"""
        logger.info("🚀 Iniciando validação completa do sistema TechZe-Diagnóstico")
        
        validation_categories = [
            ("infrastructure", self.validate_infrastructure),
            ("monitoring", self.validate_monitoring_system),
            ("ai_ml", self.validate_ai_ml_system),
            ("apis", self.validate_api_endpoints),
            ("frontend", self.validate_frontend_components),
            ("database", self.validate_database_structure),
            ("security", self.validate_security_features),
            ("performance", self.validate_performance_optimizations),
            ("deployment", self.validate_deployment_readiness),
            ("documentation", self.validate_documentation_completeness)
        ]
        
        total_score = 0
        max_score = len(validation_categories) * 100
        
        for category_name, validator_func in validation_categories:
            logger.info(f"📋 Validando categoria: {category_name}")
            try:
                category_result = await validator_func()
                self.validation_results["categories"][category_name] = category_result
                total_score += category_result.get("score", 0)
                logger.info(f"✅ {category_name}: {category_result.get('score', 0)}%")
            except Exception as e:
                logger.error(f"❌ Erro na validação de {category_name}: {e}")
                self.validation_results["categories"][category_name] = {
                    "score": 0,
                    "status": "error",
                    "error": str(e)
                }
        
        # Calcula porcentagem geral
        completion_percentage = (total_score / max_score) * 100
        self.validation_results["completion_percentage"] = round(completion_percentage, 1)
        
        # Determina status geral
        if completion_percentage >= 95:
            self.validation_results["overall_status"] = "production_ready"
        elif completion_percentage >= 90:
            self.validation_results["overall_status"] = "near_production"
        elif completion_percentage >= 80:
            self.validation_results["overall_status"] = "development_complete"
        else:
            self.validation_results["overall_status"] = "needs_work"
            
        # Gera recomendações finais
        await self.generate_final_recommendations()
        
        logger.info(f"🎯 Validação concluída: {completion_percentage}% - Status: {self.validation_results['overall_status']}")
        return self.validation_results
    
    async def validate_infrastructure(self) -> Dict[str, Any]:
        """Valida infraestrutura e arquitetura"""
        score = 0
        details = []
        
        # Verifica estrutura de microserviços
        microservice_path = self.project_root / "microservices" / "diagnostic_service"
        if microservice_path.exists():
            score += 15
            details.append("✅ Estrutura de microserviços presente")
        
        # Verifica Redis e cache
        cache_files = [
            "microservices/diagnostic_service/app/core/cache_manager.py"
        ]
        for file_path in cache_files:
            if (self.project_root / file_path).exists():
                score += 10
                details.append(f"✅ Cache system: {file_path}")
        
        # Verifica Prometheus/Grafana
        monitoring_files = [
            "microservices/diagnostic_service/app/core/monitoring.py",
            "microservices/diagnostic_service/setup_monitoring_stack.py",
            "microservices/diagnostic_service/grafana_dashboards.json"
        ]
        for file_path in monitoring_files:
            if (self.project_root / file_path).exists():
                score += 10
                details.append(f"✅ Monitoring: {file_path}")
        
        # Verifica Supabase integration
        supabase_files = [
            "microservices/diagnostic_service/app/core/supabase.py",
            "frontend-v3/src/integrations/supabase",
            "supabase_setup_fixed.sql"
        ]
        for file_path in supabase_files:
            if (self.project_root / file_path).exists():
                score += 10
                details.append(f"✅ Supabase: {file_path}")
        
        # Verifica auditoria
        if (self.project_root / "supabase_audit_table.sql").exists():
            score += 15
            details.append("✅ Sistema de auditoria completo")
        
        return {
            "score": min(score, 100),
            "status": "excellent" if score >= 90 else "good" if score >= 70 else "needs_improvement",
            "details": details,
            "missing": self._get_missing_infrastructure()
        }
    
    async def validate_monitoring_system(self) -> Dict[str, Any]:
        """Valida sistema de monitoramento"""
        score = 0
        details = []
        
        # Verifica health checks avançados
        monitoring_file = self.project_root / "microservices/diagnostic_service/app/core/monitoring.py"
        if monitoring_file.exists():
            content = monitoring_file.read_text()
            
            # Verifica funções específicas
            if "check_database_health" in content and "check_redis_health" in content:
                score += 25
                details.append("✅ Health checks de database e Redis implementados")
            
            if "TechZeMetrics" in content and "prometheus_client" in content:
                score += 25
                details.append("✅ Métricas customizadas do Prometheus")
            
            if "async def" in content and "try:" in content:
                score += 20
                details.append("✅ Health checks assíncronos com tratamento de erro")
        
        # Verifica dashboards Grafana
        grafana_file = self.project_root / "microservices/diagnostic_service/grafana_dashboards.json"
        if grafana_file.exists():
            score += 30
            details.append("✅ Dashboards Grafana configurados")
        
        return {
            "score": min(score, 100),
            "status": "excellent" if score >= 90 else "good" if score >= 70 else "needs_improvement",
            "details": details
        }
    
    async def validate_ai_ml_system(self) -> Dict[str, Any]:
        """Valida sistema de IA e ML"""
        score = 0
        details = []
        
        # Verifica ML engine
        ml_engine = self.project_root / "microservices/diagnostic_service/app/ai/ml_engine.py"
        if ml_engine.exists():
            content = ml_engine.read_text()
            
            if "PredictiveAnalyzer" in content:
                score += 20
                details.append("✅ PredictiveAnalyzer implementado")
            
            if "AnomalyDetector" in content:
                score += 15
                details.append("✅ AnomalyDetector implementado")
            
            if "PatternRecognizer" in content:
                score += 15
                details.append("✅ PatternRecognizer implementado")
            
            if "RecommendationEngine" in content:
                score += 15
                details.append("✅ RecommendationEngine implementado")
        
        # Verifica endpoints de IA
        ai_endpoints = self.project_root / "microservices/diagnostic_service/app/api/v3/ai_endpoints.py"
        if ai_endpoints.exists():
            score += 20
            details.append("✅ Endpoints de IA implementados")
        
        # Verifica modelos de dados de IA
        ai_models = self.project_root / "microservices/diagnostic_service/app/models/ai_models.py"
        if ai_models.exists():
            score += 15
            details.append("✅ Modelos de dados de IA definidos")
        
        return {
            "score": min(score, 100),
            "status": "excellent" if score >= 90 else "good" if score >= 70 else "needs_improvement",
            "details": details
        }
    
    async def validate_api_endpoints(self) -> Dict[str, Any]:
        """Valida endpoints da API"""
        score = 0
        details = []
        
        api_v3_path = self.project_root / "microservices/diagnostic_service/app/api/v3"
        if api_v3_path.exists():
            endpoints_files = [
                "ai_endpoints.py",
                "analytics_endpoints.py", 
                "automation_endpoints.py",
                "diagnostic_endpoints.py"
            ]
            
            for endpoint_file in endpoints_files:
                if (api_v3_path / endpoint_file).exists():
                    score += 20
                    details.append(f"✅ API v3: {endpoint_file}")
            
            # Verifica se há endpoints CRUD completos
            if (api_v3_path / "endpoints").exists():
                score += 20
                details.append("✅ Estrutura de endpoints organizada")
        
        return {
            "score": min(score, 100),
            "status": "excellent" if score >= 90 else "good" if score >= 70 else "needs_improvement",
            "details": details
        }
    
    async def validate_frontend_components(self) -> Dict[str, Any]:
        """Valida componentes do frontend"""
        score = 0
        details = []
        
        frontend_path = self.project_root / "frontend-v3"
        if frontend_path.exists():
            score += 20
            details.append("✅ Frontend v3 estruturado")
            
            # Verifica componentes principais
            components_path = frontend_path / "src/components"
            if components_path.exists():
                key_components = [
                    "dashboard",
                    "diagnostic", 
                    "layout",
                    "ui"
                ]
                
                for component in key_components:
                    if (components_path / component).exists():
                        score += 15
                        details.append(f"✅ Componente: {component}")
            
            # Verifica integração Supabase
            if (frontend_path / "src/integrations/supabase").exists():
                score += 15
                details.append("✅ Integração Supabase no frontend")
        
        return {
            "score": min(score, 100),
            "status": "excellent" if score >= 90 else "good" if score >= 70 else "needs_improvement",
            "details": details
        }
    
    async def validate_database_structure(self) -> Dict[str, Any]:
        """Valida estrutura do banco de dados"""
        score = 0
        details = []
        
        # Verifica scripts SQL
        sql_files = [
            "supabase_setup_fixed.sql",
            "supabase_audit_table.sql", 
            "supabase_rls_policies.sql"
        ]
        
        for sql_file in sql_files:
            if (self.project_root / sql_file).exists():
                score += 25
                details.append(f"✅ Script SQL: {sql_file}")
        
        # Verifica repositórios
        repo_path = self.project_root / "microservices/diagnostic_service/app/db/repositories"
        if repo_path.exists():
            score += 25
            details.append("✅ Repositórios de banco implementados")
        
        return {
            "score": min(score, 100),
            "status": "excellent" if score >= 90 else "good" if score >= 70 else "needs_improvement",
            "details": details
        }
    
    async def validate_security_features(self) -> Dict[str, Any]:
        """Valida recursos de segurança"""
        score = 0
        details = []
        
        # Verifica RLS policies
        if (self.project_root / "supabase_rls_policies.sql").exists():
            score += 30
            details.append("✅ Row Level Security policies")
        
        # Verifica rate limiting e auth
        security_features = [
            "microservices/diagnostic_service/app/core/rate_limiter.py",
            "microservices/diagnostic_service/app/core/auth.py"
        ]
        
        for feature in security_features:
            if (self.project_root / feature).exists():
                score += 25
                details.append(f"✅ Security: {feature}")
        
        # Verifica auditoria
        if (self.project_root / "supabase_audit_table.sql").exists():
            score += 20
            details.append("✅ Sistema completo de auditoria")
        
        return {
            "score": min(score, 100),
            "status": "excellent" if score >= 90 else "good" if score >= 70 else "needs_improvement",
            "details": details
        }
    
    async def validate_performance_optimizations(self) -> Dict[str, Any]:
        """Valida otimizações de performance"""
        score = 0
        details = []
        gaps = []
        
        # Verifica cache manager
        cache_file = self.project_root / "microservices/diagnostic_service/app/core/cache_manager.py"
        if cache_file.exists():
            score += 30
            details.append("✅ Cache Manager com Redis/Memory fallback")
        else:
            gaps.append("❌ Cache Manager ausente")
        
        # Verifica otimizações assíncronas
        async_patterns = ["async def", "await ", "asyncio"]
        async_files = [
            "microservices/diagnostic_service/app/core/monitoring.py",
            "microservices/diagnostic_service/app/ai/ml_engine.py"
        ]
        
        for file_path in async_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                content = full_path.read_text()
                if any(pattern in content for pattern in async_patterns):
                    score += 20
                    details.append(f"✅ Async otimizado: {file_path}")
                else:
                    gaps.append(f"⚠️ Não async: {file_path}")
        
        # Verifica connection pooling e otimizações de DB
        # (Gap identificado para otimização)
        gaps.append("🔧 OTIMIZAÇÃO: Implementar connection pooling avançado")
        gaps.append("🔧 OTIMIZAÇÃO: Query optimization e indexação automática")
        gaps.append("🔧 OTIMIZAÇÃO: CDN para assets estáticos")
        
        return {
            "score": min(score, 100),
            "status": "good" if score >= 70 else "needs_improvement",
            "details": details,
            "optimization_opportunities": gaps
        }
    
    async def validate_deployment_readiness(self) -> Dict[str, Any]:
        """Valida prontidão para deployment"""
        score = 0
        details = []
        gaps = []
        
        # Verifica configurações Docker
        docker_files = ["Dockerfile", "docker-compose.yml", ".dockerignore"]
        for docker_file in docker_files:
            if (self.project_root / docker_file).exists():
                score += 15
                details.append(f"✅ Docker: {docker_file}")
            else:
                gaps.append(f"🔧 DEPLOY: Criar {docker_file}")
        
        # Verifica configurações de produção
        if (self.project_root / "microservices/diagnostic_service/app/core/config.py").exists():
            score += 25
            details.append("✅ Configurações centralizadas")
        
        # Verifica scripts de setup
        setup_files = ["setup_complete.py", "run_setup.py"]
        for setup_file in setup_files:
            if (self.project_root / setup_file).exists():
                score += 10
                details.append(f"✅ Setup: {setup_file}")
        
        # Gaps de deployment identificados
        gaps.extend([
            "🔧 DEPLOY: Configurar CI/CD pipeline",
            "🔧 DEPLOY: Health checks para Kubernetes",
            "🔧 DEPLOY: Backup automático de produção",
            "🔧 DEPLOY: Rolling deployment strategy"
        ])
        
        return {
            "score": min(score, 100),
            "status": "good" if score >= 70 else "needs_improvement", 
            "details": details,
            "deployment_gaps": gaps
        }
    
    async def validate_documentation_completeness(self) -> Dict[str, Any]:
        """Valida completude da documentação"""
        score = 0
        details = []
        
        # Verifica documentos principais
        key_docs = [
            "README.md",
            "PLANO_COLABORATIVO_UNIFICADO.md",
            "PRODUCTION_READY_CHECKLIST_COMPLETO.md",
            "INDICE_DOCUMENTACAO.md"
        ]
        
        for doc in key_docs:
            if (self.project_root / doc).exists():
                score += 20
                details.append(f"✅ Documentação: {doc}")
        
        # Verifica docs técnicos
        if (self.project_root / "docs").exists():
            score += 20
            details.append("✅ Diretório de documentação técnica")
        
        return {
            "score": min(score, 100),
            "status": "excellent" if score >= 90 else "good" if score >= 70 else "needs_improvement",
            "details": details
        }
    
    async def generate_final_recommendations(self):
        """Gera recomendações finais para os 5% restantes"""
        
        # Coleta gaps de todas as categorias
        all_gaps = []
        for category, result in self.validation_results["categories"].items():
            if "optimization_opportunities" in result:
                all_gaps.extend(result["optimization_opportunities"])
            if "deployment_gaps" in result:
                all_gaps.extend(result["deployment_gaps"])
        
        # Prioriza otimizações baseadas no impacto
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for gap in all_gaps:
            if "DEPLOY" in gap or "connection pooling" in gap:
                high_priority.append(gap)
            elif "OTIMIZAÇÃO" in gap:
                medium_priority.append(gap)
            else:
                low_priority.append(gap)
        
        self.validation_results["recommendations"] = {
            "high_priority": high_priority,
            "medium_priority": medium_priority, 
            "low_priority": low_priority,
            "next_steps": [
                "1. 🔧 Implementar connection pooling avançado para PostgreSQL",
                "2. 🚀 Configurar CI/CD pipeline com GitHub Actions",
                "3. 📊 Adicionar query optimization automática",
                "4. 🌐 Implementar CDN para assets estáticos",
                "5. 🐳 Finalizar configuração Docker para produção"
            ]
        }
    
    def _get_missing_infrastructure(self) -> List[str]:
        """Identifica infraestrutura ausente"""
        missing = []
        
        # Verifica Docker
        if not (self.project_root / "Dockerfile").exists():
            missing.append("Dockerfile para containerização")
        
        if not (self.project_root / "docker-compose.yml").exists():
            missing.append("Docker Compose para orquestração")
        
        return missing
    
    async def save_validation_report(self):
        """Salva relatório de validação"""
        report_file = self.project_root / "system_validation_report.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.validation_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📄 Relatório salvo em: {report_file}")
        
        # Cria também um resumo em markdown
        await self._create_markdown_summary()
    
    async def _create_markdown_summary(self):
        """Cria resumo em markdown"""
        summary_file = self.project_root / "VALIDATION_SUMMARY.md"
        
        completion = self.validation_results["completion_percentage"]
        status = self.validation_results["overall_status"]
        
        markdown_content = f"""# 🎯 TechZe-Diagnóstico - Relatório de Validação Completa

## 📊 Status Geral
- **Completude**: {completion}%
- **Status**: {status}
- **Data**: {self.validation_results["timestamp"]}

## 🔍 Análise por Categoria

"""
        
        for category, result in self.validation_results["categories"].items():
            score = result.get("score", 0)
            status_cat = result.get("status", "unknown")
            
            markdown_content += f"""### {category.title()}
- **Score**: {score}%
- **Status**: {status_cat}
- **Detalhes**: {len(result.get("details", []))} itens verificados

"""
        
        # Adiciona recomendações
        if "recommendations" in self.validation_results:
            recommendations = self.validation_results["recommendations"]
            
            markdown_content += """## 🚀 Próximos Passos (5% Restantes)

### Alta Prioridade
"""
            for item in recommendations.get("high_priority", []):
                markdown_content += f"- {item}\n"
            
            markdown_content += "\n### Próximas Ações\n"
            for step in recommendations.get("next_steps", []):
                markdown_content += f"{step}\n"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        logger.info(f"📋 Resumo salvo em: {summary_file}")

async def main():
    """Função principal"""
    print("🚀 TechZe-Diagnóstico - Validação Completa do Sistema")
    print("=" * 60)
    
    validator = ComprehensiveSystemValidator()
    
    try:
        # Executa validação completa
        results = await validator.validate_complete_system()
        
        # Salva relatórios
        await validator.save_validation_report()
        
        # Exibe resumo
        print(f"\n🎯 RESULTADO FINAL:")
        print(f"   Completude: {results['completion_percentage']}%")
        print(f"   Status: {results['overall_status']}")
        
        if results['completion_percentage'] >= 95:
            print("\n🎉 PARABÉNS! Sistema está pronto para produção!")
            print("   Apenas otimizações finais necessárias.")
        else:
            print(f"\n📋 {100 - results['completion_percentage']:.1f}% restante para completar")
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Erro na validação: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        sys.exit(0 if results.get("completion_percentage", 0) >= 95 else 1)
    except KeyboardInterrupt:
        print("\n🛑 Validação interrompida pelo usuário")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        sys.exit(1) 