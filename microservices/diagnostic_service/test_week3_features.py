#!/usr/bin/env python3
"""
Teste das funcionalidades da Semana 3 - IA, ML e Automação
"""

import asyncio
import json
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any

class Week3FeatureTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log do resultado do teste"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    def test_service_health(self) -> bool:
        """Testa se o serviço está rodando"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                api_v3_available = data.get("api_v3_router_available", False)
                self.log_test("Service Health", True, f"Service running, API v3: {api_v3_available}")
                return True
            else:
                self.log_test("Service Health", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Service Health", False, f"Error: {str(e)}")
            return False
    
    def test_ai_prediction(self) -> bool:
        """Testa endpoint de predição de IA"""
        try:
            payload = {
                "prediction_type": "performance",
                "historical_data": {
                    "cpu_usage": [45.2, 52.1, 48.7, 55.3, 49.8],
                    "memory_usage": [67.4, 71.2, 69.8, 73.1, 70.5],
                    "timestamps": [
                        (datetime.now() - timedelta(hours=i)).isoformat()
                        for i in range(5, 0, -1)
                    ]
                },
                "time_horizon": 7,
                "confidence_level": 0.95
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v3/ai/predict",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_predictions = "predictions" in data
                self.log_test("AI Prediction", has_predictions, f"Predictions available: {has_predictions}")
                return has_predictions
            else:
                self.log_test("AI Prediction", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("AI Prediction", False, f"Error: {str(e)}")
            return False
    
    def test_anomaly_detection(self) -> bool:
        """Testa detecção de anomalias"""
        try:
            payload = {
                "metrics": {
                    "cpu_usage": [45.2, 52.1, 98.7, 55.3, 49.8],  # 98.7 é anomalia
                    "memory_usage": [67.4, 71.2, 69.8, 73.1, 70.5],
                    "disk_usage": [45.1, 46.2, 47.1, 48.0, 49.2],
                    "timestamps": [
                        (datetime.now() - timedelta(minutes=i*5)).isoformat()
                        for i in range(5, 0, -1)
                    ]
                },
                "sensitivity": 0.95,
                "method": "statistical"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v3/ai/detect-anomalies",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_anomalies = "anomalies" in data
                self.log_test("Anomaly Detection", has_anomalies, f"Anomalies detected: {has_anomalies}")
                return has_anomalies
            else:
                self.log_test("Anomaly Detection", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Anomaly Detection", False, f"Error: {str(e)}")
            return False
    
    def test_pattern_analysis(self) -> bool:
        """Testa análise de padrões"""
        try:
            payload = {
                "data": {
                    "cpu_usage": [45, 50, 55, 60, 45, 50, 55, 60, 45, 50],
                    "timestamps": [
                        (datetime.now() - timedelta(hours=i)).isoformat()
                        for i in range(10, 0, -1)
                    ]
                },
                "pattern_types": ["seasonal", "trend", "cyclical"],
                "analysis_depth": "detailed"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v3/ai/analyze-patterns",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_patterns = "patterns" in data
                self.log_test("Pattern Analysis", has_patterns, f"Patterns found: {has_patterns}")
                return has_patterns
            else:
                self.log_test("Pattern Analysis", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Pattern Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_recommendations(self) -> bool:
        """Testa sistema de recomendações"""
        try:
            payload = {
                "system_state": {
                    "cpu_usage": 85.5,
                    "memory_usage": 78.2,
                    "disk_usage": 92.1,
                    "network_latency": 45.2
                },
                "user_preferences": {
                    "priority": "performance",
                    "risk_tolerance": "medium"
                },
                "context": {
                    "time_of_day": "business_hours",
                    "system_load": "high"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v3/ai/recommendations",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_recommendations = "recommendations" in data
                self.log_test("AI Recommendations", has_recommendations, f"Recommendations available: {has_recommendations}")
                return has_recommendations
            else:
                self.log_test("AI Recommendations", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("AI Recommendations", False, f"Error: {str(e)}")
            return False
    
    def test_auto_fix(self) -> bool:
        """Testa correção automática"""
        try:
            payload = {
                "problem_type": "performance_optimization",
                "severity": "medium",
                "system_state": {
                    "cpu_usage": 85.5,
                    "memory_usage": 78.2,
                    "disk_usage": 45.1,
                    "running_processes": 156
                },
                "auto_approve": False,  # Não executar automaticamente
                "dry_run": True  # Apenas simular
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v3/automation/auto-fix",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_fixes = "fixes" in data
                self.log_test("Auto Fix", has_fixes, f"Fixes suggested: {has_fixes}")
                return has_fixes
            else:
                self.log_test("Auto Fix", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Auto Fix", False, f"Error: {str(e)}")
            return False
    
    def test_workflow_creation(self) -> bool:
        """Testa criação de workflow"""
        try:
            payload = {
                "workflow_name": "Test Maintenance Workflow",
                "description": "Workflow de teste para manutenção",
                "steps": [
                    {
                        "name": "Check System Health",
                        "type": "diagnostic",
                        "parameters": {"quick_scan": True}
                    },
                    {
                        "name": "Clean Temporary Files",
                        "type": "cleanup",
                        "parameters": {"target": "temp_files"}
                    }
                ],
                "schedule": {
                    "type": "manual",
                    "enabled": False
                },
                "notifications": {
                    "on_success": True,
                    "on_failure": True
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v3/automation/workflows",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                workflow_created = "workflow_id" in data
                self.log_test("Workflow Creation", workflow_created, f"Workflow created: {workflow_created}")
                return workflow_created
            else:
                self.log_test("Workflow Creation", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Workflow Creation", False, f"Error: {str(e)}")
            return False
    
    def test_resource_optimization(self) -> bool:
        """Testa otimização de recursos"""
        try:
            payload = {
                "optimization_type": "performance",
                "target_metrics": ["cpu_usage", "memory_usage"],
                "constraints": {
                    "max_cpu_usage": 80.0,
                    "max_memory_usage": 85.0
                },
                "current_state": {
                    "cpu_usage": 75.2,
                    "memory_usage": 82.1,
                    "disk_usage": 45.3
                },
                "optimization_level": "moderate"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v3/automation/optimize",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_optimizations = "optimizations" in data
                self.log_test("Resource Optimization", has_optimizations, f"Optimizations available: {has_optimizations}")
                return has_optimizations
            else:
                self.log_test("Resource Optimization", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Resource Optimization", False, f"Error: {str(e)}")
            return False
    
    def test_analytics_report_generation(self) -> bool:
        """Testa geração de relatórios"""
        try:
            payload = {
                "report_type": "performance",
                "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
                "end_date": datetime.now().isoformat(),
                "metrics": ["cpu_usage", "memory_usage", "disk_usage"],
                "format": "json",
                "include_charts": True,
                "include_recommendations": True
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v3/analytics/generate-report",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_report = "report" in data
                self.log_test("Analytics Report", has_report, f"Report generated: {has_report}")
                return has_report
            else:
                self.log_test("Analytics Report", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Analytics Report", False, f"Error: {str(e)}")
            return False
    
    def test_metrics_collection(self) -> bool:
        """Testa coleta de métricas"""
        try:
            params = {
                "metric_types": "cpu_usage,memory_usage,disk_usage",
                "start_date": (datetime.now() - timedelta(hours=1)).isoformat(),
                "end_date": datetime.now().isoformat(),
                "aggregation": "avg",
                "interval": "5m"
            }
            
            response = self.session.get(
                f"{self.base_url}/api/v3/analytics/metrics",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_metrics = "metrics" in data
                self.log_test("Metrics Collection", has_metrics, f"Metrics collected: {has_metrics}")
                return has_metrics
            else:
                self.log_test("Metrics Collection", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Metrics Collection", False, f"Error: {str(e)}")
            return False
    
    def test_trend_analysis(self) -> bool:
        """Testa análise de tendências"""
        try:
            params = {
                "metric": "cpu_usage",
                "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
                "end_date": datetime.now().isoformat(),
                "trend_type": "linear"
            }
            
            response = self.session.get(
                f"{self.base_url}/api/v3/analytics/trends",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_trends = "trends" in data
                self.log_test("Trend Analysis", has_trends, f"Trends analyzed: {has_trends}")
                return has_trends
            else:
                self.log_test("Trend Analysis", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Trend Analysis", False, f"Error: {str(e)}")
            return False
    
    def test_predictive_insights(self) -> bool:
        """Testa insights preditivos"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v3/analytics/predictive-insights",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_insights = "insights" in data
                self.log_test("Predictive Insights", has_insights, f"Insights available: {has_insights}")
                return has_insights
            else:
                self.log_test("Predictive Insights", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Predictive Insights", False, f"Error: {str(e)}")
            return False
    
    def test_chat_session(self) -> bool:
        """Testa criação de sessão de chat"""
        try:
            payload = {
                "user_id": "test_user",
                "session_type": "diagnostic",
                "preferences": {
                    "language": "pt-BR",
                    "expertise_level": "intermediate"
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v3/chat/sessions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_session = "session_id" in data
                self.log_test("Chat Session", has_session, f"Session created: {has_session}")
                return has_session
            else:
                self.log_test("Chat Session", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Chat Session", False, f"Error: {str(e)}")
            return False
    
    def test_voice_command(self) -> bool:
        """Testa comando de voz (simulado)"""
        try:
            payload = {
                "session_id": "test_session",
                "audio_data": "fake_base64_audio_data",  # Simulado
                "command_type": "diagnostic",
                "language": "pt-BR"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v3/chat/voice-command",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_response = "response" in data
                self.log_test("Voice Command", has_response, f"Voice processed: {has_response}")
                return has_response
            else:
                self.log_test("Voice Command", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Voice Command", False, f"Error: {str(e)}")
            return False
    
    def test_tutorials(self) -> bool:
        """Testa sistema de tutoriais"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v3/chat/tutorials",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                has_tutorials = "tutorials" in data
                self.log_test("Tutorials", has_tutorials, f"Tutorials available: {has_tutorials}")
                return has_tutorials
            else:
                self.log_test("Tutorials", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Tutorials", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os testes"""
        print("🚀 Iniciando testes da Semana 3 - IA, ML e Automação")
        print("=" * 60)
        
        # Teste básico de saúde
        if not self.test_service_health():
            print("❌ Serviço não está rodando. Abortando testes.")
            return self.generate_report()
        
        # Testes de IA e ML
        print("\n🧠 Testando funcionalidades de IA e ML...")
        self.test_ai_prediction()
        self.test_anomaly_detection()
        self.test_pattern_analysis()
        self.test_recommendations()
        
        # Testes de Automação
        print("\n🔧 Testando funcionalidades de Automação...")
        self.test_auto_fix()
        self.test_workflow_creation()
        self.test_resource_optimization()
        
        # Testes de Analytics
        print("\n📊 Testando funcionalidades de Analytics...")
        self.test_analytics_report_generation()
        self.test_metrics_collection()
        self.test_trend_analysis()
        self.test_predictive_insights()
        
        # Testes de Chat e Assistente
        print("\n💬 Testando funcionalidades de Chat e Assistente...")
        self.test_chat_session()
        self.test_voice_command()
        self.test_tutorials()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório final dos testes"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{success_rate:.1f}%"
            },
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n" + "=" * 60)
        print("📋 RELATÓRIO FINAL DOS TESTES")
        print("=" * 60)
        print(f"Total de testes: {total_tests}")
        print(f"✅ Passou: {passed_tests}")
        print(f"❌ Falhou: {failed_tests}")
        print(f"📊 Taxa de sucesso: {success_rate:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Testes que falharam:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return report

def main():
    """Função principal"""
    tester = Week3FeatureTester()
    report = tester.run_all_tests()
    
    # Salva relatório em arquivo
    with open("week3_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo em: week3_test_report.json")
    
    # Retorna código de saída baseado no sucesso
    success_rate = float(report["summary"]["success_rate"].rstrip("%"))
    return 0 if success_rate >= 80 else 1

if __name__ == "__main__":
    exit(main())