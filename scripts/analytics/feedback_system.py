#!/usr/bin/env python3
"""
Sistema Avançado de Feedback e Análise - TechZe Diagnóstico
Agente CURSOR - Feedback Loop Inteligente para Melhoria Contínua
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import logging
import requests
from dataclasses import dataclass
import sqlite3
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Estrutura de dados para resultados de teste"""
    test_type: str
    status: str
    duration: float
    coverage: float
    failures: int
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class SecurityResult:
    """Estrutura de dados para resultados de segurança"""
    scanner: str
    severity: str
    vulnerability_count: int
    critical_issues: List[str]
    recommendations: List[str]
    timestamp: datetime

@dataclass
class PerformanceResult:
    """Estrutura de dados para resultados de performance"""
    metric_name: str
    current_value: float
    baseline_value: float
    threshold: float
    trend: str  # 'improving', 'degrading', 'stable'
    impact_level: str  # 'low', 'medium', 'high', 'critical'

class FeedbackDatabase:
    """Banco de dados para armazenar histórico de feedback"""
    
    def __init__(self, db_path: str = "data/feedback_history.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Inicializar estrutura do banco de dados"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS test_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_sha TEXT,
                    branch TEXT,
                    test_type TEXT,
                    status TEXT,
                    duration REAL,
                    coverage REAL,
                    failures INTEGER,
                    timestamp TEXT,
                    metadata TEXT
                );
                
                CREATE TABLE IF NOT EXISTS security_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_sha TEXT,
                    scanner TEXT,
                    severity TEXT,
                    vulnerability_count INTEGER,
                    critical_issues TEXT,
                    recommendations TEXT,
                    timestamp TEXT
                );
                
                CREATE TABLE IF NOT EXISTS performance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    commit_sha TEXT,
                    metric_name TEXT,
                    current_value REAL,
                    baseline_value REAL,
                    threshold REAL,
                    trend TEXT,
                    impact_level TEXT,
                    timestamp TEXT
                );
                
                CREATE TABLE IF NOT EXISTS feedback_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_type TEXT,
                    priority TEXT,
                    description TEXT,
                    recommended_action TEXT,
                    assigned_to TEXT,
                    status TEXT,
                    created_at TEXT,
                    resolved_at TEXT
                );
            ''')
    
    def save_test_result(self, commit_sha: str, branch: str, result: TestResult):
        """Salvar resultado de teste"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO test_history 
                (commit_sha, branch, test_type, status, duration, coverage, failures, timestamp, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                commit_sha, branch, result.test_type, result.status,
                result.duration, result.coverage, result.failures,
                result.timestamp.isoformat(), json.dumps(result.metadata)
            ))
    
    def save_security_result(self, commit_sha: str, result: SecurityResult):
        """Salvar resultado de segurança"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO security_history 
                (commit_sha, scanner, severity, vulnerability_count, critical_issues, recommendations, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                commit_sha, result.scanner, result.severity,
                result.vulnerability_count, json.dumps(result.critical_issues),
                json.dumps(result.recommendations), result.timestamp.isoformat()
            ))
    
    def save_performance_result(self, commit_sha: str, result: PerformanceResult):
        """Salvar resultado de performance"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO performance_history 
                (commit_sha, metric_name, current_value, baseline_value, threshold, trend, impact_level, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                commit_sha, result.metric_name, result.current_value,
                result.baseline_value, result.threshold, result.trend,
                result.impact_level, datetime.now().isoformat()
            ))
    
    def get_trend_analysis(self, metric_name: str, days: int = 30) -> Dict[str, Any]:
        """Análise de tendências para métrica específica"""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query('''
                SELECT * FROM performance_history 
                WHERE metric_name = ? AND timestamp > ?
                ORDER BY timestamp
            ''', conn, params=[
                metric_name, 
                (datetime.now() - timedelta(days=days)).isoformat()
            ])
        
        if df.empty:
            return {"status": "no_data"}
        
        # Calcular tendências
        values = df['current_value'].values
        trend_slope = np.polyfit(range(len(values)), values, 1)[0]
        
        return {
            "metric": metric_name,
            "data_points": len(values),
            "current_value": values[-1],
            "average": np.mean(values),
            "trend_slope": trend_slope,
            "trend_direction": "improving" if trend_slope < 0 else "degrading" if trend_slope > 0 else "stable",
            "variance": np.var(values),
            "min_value": np.min(values),
            "max_value": np.max(values)
        }

class SmartFeedbackAnalyzer:
    """Analisador inteligente de feedback com IA para recomendações"""
    
    def __init__(self, db: FeedbackDatabase):
        self.db = db
        self.thresholds = {
            "test_coverage": {"warning": 70, "critical": 60},
            "build_time": {"warning": 300, "critical": 600},  # segundos
            "response_time": {"warning": 2000, "critical": 5000},  # ms
            "error_rate": {"warning": 1.0, "critical": 5.0},  # %
            "security_issues": {"warning": 5, "critical": 1}  # issues críticos
        }
    
    def analyze_test_trends(self, days: int = 14) -> Dict[str, Any]:
        """Analisar tendências de testes"""
        logger.info(f"Analisando tendências de teste dos últimos {days} dias")
        
        analysis = {
            "period_days": days,
            "timestamp": datetime.now().isoformat(),
            "trends": {},
            "alerts": [],
            "recommendations": []
        }
        
        # Analisar métricas principais
        metrics = ["test_coverage", "build_time", "response_time", "error_rate"]
        
        for metric in metrics:
            trend_data = self.db.get_trend_analysis(metric, days)
            
            if trend_data.get("status") != "no_data":
                analysis["trends"][metric] = trend_data
                
                # Gerar alertas baseados em thresholds
                current_value = trend_data["current_value"]
                thresholds = self.thresholds.get(metric, {})
                
                if current_value > thresholds.get("critical", float('inf')):
                    analysis["alerts"].append({
                        "level": "CRITICAL",
                        "metric": metric,
                        "current_value": current_value,
                        "threshold": thresholds["critical"],
                        "message": f"{metric} está em nível crítico: {current_value}"
                    })
                elif current_value > thresholds.get("warning", float('inf')):
                    analysis["alerts"].append({
                        "level": "WARNING",
                        "metric": metric,
                        "current_value": current_value,
                        "threshold": thresholds["warning"],
                        "message": f"{metric} está acima do limite recomendado: {current_value}"
                    })
        
        # Gerar recomendações inteligentes
        analysis["recommendations"] = self.generate_smart_recommendations(analysis)
        
        return analysis
    
    def generate_smart_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gerar recomendações inteligentes baseadas na análise"""
        recommendations = []
        
        trends = analysis.get("trends", {})
        alerts = analysis.get("alerts", [])
        
        # Recomendações baseadas em alertas críticos
        for alert in alerts:
            if alert["level"] == "CRITICAL":
                metric = alert["metric"]
                
                if metric == "test_coverage":
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Quality Assurance",
                        "title": "Cobertura de Testes Crítica",
                        "description": f"Cobertura atual: {alert['current_value']}%",
                        "actions": [
                            "Identificar módulos sem cobertura",
                            "Implementar testes unitários prioritários",
                            "Revisar estratégia de testes",
                            "Configurar gates de qualidade mais rigorosos"
                        ],
                        "estimated_effort": "2-3 sprints",
                        "impact": "Redução significativa de bugs em produção"
                    })
                
                elif metric == "build_time":
                    recommendations.append({
                        "priority": "MEDIUM",
                        "category": "DevOps",
                        "title": "Otimização de Build",
                        "description": f"Tempo de build: {alert['current_value']}s",
                        "actions": [
                            "Implementar cache de dependências",
                            "Paralelizar execução de testes",
                            "Otimizar Dockerfile e layers",
                            "Considerar build incremental"
                        ],
                        "estimated_effort": "1 sprint",
                        "impact": "Feedback mais rápido para desenvolvedores"
                    })
                
                elif metric == "response_time":
                    recommendations.append({
                        "priority": "HIGH",
                        "category": "Performance",
                        "title": "Otimização de Performance",
                        "description": f"Tempo de resposta: {alert['current_value']}ms",
                        "actions": [
                            "Profiling de queries lentas",
                            "Implementar cache Redis",
                            "Otimizar índices do banco",
                            "Review de algoritmos críticos"
                        ],
                        "estimated_effort": "1-2 sprints",
                        "impact": "Melhor experiência do usuário"
                    })
        
        # Recomendações baseadas em tendências
        for metric, trend_data in trends.items():
            if trend_data.get("trend_direction") == "degrading":
                variance = trend_data.get("variance", 0)
                
                if variance > 0.1:  # Alta variabilidade
                    recommendations.append({
                        "priority": "MEDIUM",
                        "category": "Stability",
                        "title": f"Instabilidade em {metric}",
                        "description": f"Alta variabilidade detectada: {variance:.3f}",
                        "actions": [
                            "Investigar causas de variabilidade",
                            "Implementar monitoramento mais granular",
                            "Revisar configurações de ambiente",
                            "Estabilizar dependências externas"
                        ],
                        "estimated_effort": "1 sprint",
                        "impact": "Maior previsibilidade do sistema"
                    })
        
        return recommendations
    
    def analyze_security_posture(self) -> Dict[str, Any]:
        """Analisar postura de segurança"""
        logger.info("Analisando postura de segurança")
        
        with sqlite3.connect(self.db.db_path) as conn:
            # Análise de vulnerabilidades por tipo
            security_df = pd.read_sql_query('''
                SELECT scanner, severity, vulnerability_count, timestamp
                FROM security_history 
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 100
            ''', conn, params=[(datetime.now() - timedelta(days=30)).isoformat()])
        
        if security_df.empty:
            return {"status": "no_data", "message": "Nenhum dado de segurança encontrado"}
        
        analysis = {
            "total_scans": len(security_df),
            "latest_scan": security_df.iloc[0].to_dict() if not security_df.empty else None,
            "vulnerability_trend": {},
            "risk_assessment": "low",
            "recommendations": []
        }
        
        # Análise por scanner
        for scanner in security_df['scanner'].unique():
            scanner_data = security_df[security_df['scanner'] == scanner]
            
            analysis["vulnerability_trend"][scanner] = {
                "latest_count": int(scanner_data.iloc[0]['vulnerability_count']),
                "average_count": float(scanner_data['vulnerability_count'].mean()),
                "trend": "improving" if scanner_data['vulnerability_count'].is_monotonic_decreasing else "stable"
            }
        
        # Avaliação de risco
        latest_critical = security_df[security_df['severity'] == 'CRITICAL']['vulnerability_count'].sum()
        
        if latest_critical > 0:
            analysis["risk_assessment"] = "critical"
            analysis["recommendations"].append({
                "priority": "CRITICAL",
                "title": "Vulnerabilidades Críticas Detectadas",
                "description": f"{latest_critical} vulnerabilidades críticas encontradas",
                "immediate_actions": [
                    "Revisar e corrigir vulnerabilidades críticas imediatamente",
                    "Implementar patches de segurança",
                    "Executar pentests adicionais",
                    "Notificar equipe de segurança"
                ]
            })
        
        return analysis
    
    def generate_executive_summary(self) -> Dict[str, Any]:
        """Gerar resumo executivo para stakeholders"""
        logger.info("Gerando resumo executivo")
        
        test_analysis = self.analyze_test_trends()
        security_analysis = self.analyze_security_posture()
        
        # Calcular score geral de qualidade
        quality_score = self.calculate_quality_score(test_analysis, security_analysis)
        
        summary = {
            "generated_at": datetime.now().isoformat(),
            "overall_quality_score": quality_score,
            "status": self.get_overall_status(quality_score),
            "key_metrics": {
                "total_alerts": len(test_analysis.get("alerts", [])),
                "critical_alerts": len([a for a in test_analysis.get("alerts", []) if a["level"] == "CRITICAL"]),
                "security_risk": security_analysis.get("risk_assessment", "unknown"),
                "total_recommendations": len(test_analysis.get("recommendations", []))
            },
            "top_priorities": self.get_top_priorities(test_analysis, security_analysis),
            "recent_improvements": self.identify_improvements(),
            "next_actions": self.get_next_actions(test_analysis, security_analysis)
        }
        
        return summary
    
    def calculate_quality_score(self, test_analysis: Dict, security_analysis: Dict) -> float:
        """Calcular score geral de qualidade (0-100)"""
        base_score = 100.0
        
        # Penalizar por alertas
        alerts = test_analysis.get("alerts", [])
        critical_alerts = len([a for a in alerts if a["level"] == "CRITICAL"])
        warning_alerts = len([a for a in alerts if a["level"] == "WARNING"])
        
        base_score -= (critical_alerts * 20)  # -20 por alerta crítico
        base_score -= (warning_alerts * 5)   # -5 por alerta de warning
        
        # Penalizar por riscos de segurança
        security_risk = security_analysis.get("risk_assessment", "low")
        if security_risk == "critical":
            base_score -= 30
        elif security_risk == "high":
            base_score -= 15
        elif security_risk == "medium":
            base_score -= 5
        
        return max(0, min(100, base_score))
    
    def get_overall_status(self, quality_score: float) -> str:
        """Determinar status geral baseado no score"""
        if quality_score >= 90:
            return "excellent"
        elif quality_score >= 75:
            return "good"
        elif quality_score >= 60:
            return "fair"
        else:
            return "needs_attention"
    
    def get_top_priorities(self, test_analysis: Dict, security_analysis: Dict) -> List[Dict]:
        """Identificar prioridades principais"""
        priorities = []
        
        # Adicionar alertas críticos
        critical_alerts = [a for a in test_analysis.get("alerts", []) if a["level"] == "CRITICAL"]
        for alert in critical_alerts[:3]:  # Top 3
            priorities.append({
                "type": "critical_issue",
                "title": f"Resolver {alert['metric']}",
                "urgency": "immediate",
                "impact": "high"
            })
        
        # Adicionar riscos de segurança
        if security_analysis.get("risk_assessment") == "critical":
            priorities.append({
                "type": "security_issue",
                "title": "Corrigir vulnerabilidades críticas",
                "urgency": "immediate",
                "impact": "critical"
            })
        
        return priorities
    
    def identify_improvements(self) -> List[Dict]:
        """Identificar melhorias recentes"""
        improvements = []
        
        # Analisar tendências positivas dos últimos 7 dias
        metrics = ["test_coverage", "build_time", "response_time"]
        
        for metric in metrics:
            trend_data = self.db.get_trend_analysis(metric, days=7)
            
            if (trend_data.get("status") != "no_data" and 
                trend_data.get("trend_direction") == "improving"):
                
                improvements.append({
                    "metric": metric,
                    "improvement": f"Melhoria de {abs(trend_data.get('trend_slope', 0)):.2f}",
                    "period": "últimos 7 dias"
                })
        
        return improvements
    
    def get_next_actions(self, test_analysis: Dict, security_analysis: Dict) -> List[str]:
        """Definir próximas ações recomendadas"""
        actions = []
        
        # Ações baseadas em alertas
        critical_alerts = [a for a in test_analysis.get("alerts", []) if a["level"] == "CRITICAL"]
        if critical_alerts:
            actions.append("Resolver alertas críticos identificados")
        
        # Ações baseadas em segurança
        if security_analysis.get("risk_assessment") in ["critical", "high"]:
            actions.append("Executar revisão de segurança completa")
        
        # Ações de melhoria contínua
        recommendations = test_analysis.get("recommendations", [])
        high_priority_recs = [r for r in recommendations if r.get("priority") == "HIGH"]
        
        if high_priority_recs:
            actions.append(f"Implementar {len(high_priority_recs)} recomendações de alta prioridade")
        
        if not actions:
            actions.append("Manter monitoramento contínuo da qualidade")
        
        return actions

class FeedbackReportGenerator:
    """Gerador de relatórios de feedback"""
    
    def __init__(self, analyzer: SmartFeedbackAnalyzer):
        self.analyzer = analyzer
    
    def generate_html_report(self, output_path: str = "reports/feedback_report.html"):
        """Gerar relatório HTML detalhado"""
        logger.info(f"Gerando relatório HTML: {output_path}")
        
        executive_summary = self.analyzer.generate_executive_summary()
        test_analysis = self.analyzer.analyze_test_trends()
        security_analysis = self.analyzer.analyze_security_posture()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>TechZe - Relatório de Feedback de Qualidade</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; }}
                .summary {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; }}
                .score {{ font-size: 2em; font-weight: bold; text-align: center; }}
                .alert {{ padding: 10px; margin: 10px 0; border-radius: 4px; }}
                .critical {{ background: #f8d7da; border: 1px solid #f5c6cb; }}
                .warning {{ background: #fff3cd; border: 1px solid #ffeaa7; }}
                .good {{ background: #d4edda; border: 1px solid #c3e6cb; }}
                .recommendation {{ background: white; padding: 15px; margin: 10px 0; border-left: 4px solid #007bff; }}
                .chart {{ margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 TechZe Diagnóstico - Relatório de Feedback de Qualidade</h1>
                <p>Gerado em: {executive_summary['generated_at']}</p>
            </div>
            
            <div class="summary">
                <h2>📊 Resumo Executivo</h2>
                <div class="score">{executive_summary['overall_quality_score']:.1f}/100</div>
                <p><strong>Status Geral:</strong> {executive_summary['status'].upper()}</p>
                
                <h3>Métricas Principais:</h3>
                <ul>
                    <li>Total de Alertas: {executive_summary['key_metrics']['total_alerts']}</li>
                    <li>Alertas Críticos: {executive_summary['key_metrics']['critical_alerts']}</li>
                    <li>Risco de Segurança: {executive_summary['key_metrics']['security_risk'].upper()}</li>
                    <li>Recomendações: {executive_summary['key_metrics']['total_recommendations']}</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>🚨 Alertas Ativos</h2>
        """
        
        # Adicionar alertas
        for alert in test_analysis.get("alerts", []):
            alert_class = "critical" if alert["level"] == "CRITICAL" else "warning"
            html_content += f"""
                <div class="alert {alert_class}">
                    <strong>{alert['level']}:</strong> {alert['message']}
                </div>
            """
        
        # Adicionar recomendações
        html_content += """
            </div>
            
            <div class="section">
                <h2>💡 Recomendações</h2>
        """
        
        for rec in test_analysis.get("recommendations", []):
            html_content += f"""
                <div class="recommendation">
                    <h3>{rec['title']}</h3>
                    <p><strong>Prioridade:</strong> {rec['priority']}</p>
                    <p><strong>Categoria:</strong> {rec['category']}</p>
                    <p>{rec['description']}</p>
                    <p><strong>Esforço Estimado:</strong> {rec['estimated_effort']}</p>
                    <p><strong>Impacto:</strong> {rec['impact']}</p>
                </div>
            """
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        # Salvar arquivo
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Relatório HTML gerado: {output_path}")
        return output_path
    
    def generate_slack_summary(self) -> str:
        """Gerar resumo para Slack"""
        executive_summary = self.analyzer.generate_executive_summary()
        
        status_emoji = {
            "excellent": "🟢",
            "good": "🟡", 
            "fair": "🟠",
            "needs_attention": "🔴"
        }
        
        emoji = status_emoji.get(executive_summary['status'], "⚪")
        
        slack_message = f"""
{emoji} *TechZe Quality Report*

*Overall Score:* {executive_summary['overall_quality_score']:.1f}/100
*Status:* {executive_summary['status'].upper()}

*Key Metrics:*
• Alerts: {executive_summary['key_metrics']['total_alerts']} ({executive_summary['key_metrics']['critical_alerts']} critical)
• Security Risk: {executive_summary['key_metrics']['security_risk'].upper()}
• Recommendations: {executive_summary['key_metrics']['total_recommendations']}

*Top Priorities:*
"""
        
        for priority in executive_summary.get('top_priorities', [])[:3]:
            slack_message += f"• {priority['title']} ({priority['urgency']})\n"
        
        return slack_message


def main():
    """Função principal"""
    # Inicializar sistema de feedback
    db = FeedbackDatabase()
    analyzer = SmartFeedbackAnalyzer(db)
    report_generator = FeedbackReportGenerator(analyzer)
    
    # Gerar análises
    logger.info("Iniciando análise de feedback...")
    
    executive_summary = analyzer.generate_executive_summary()
    html_report = report_generator.generate_html_report()
    slack_summary = report_generator.generate_slack_summary()
    
    # Salvar resumo JSON
    with open("reports/executive_summary.json", "w") as f:
        json.dump(executive_summary, f, indent=2)
    
    # Exibir resumo
    print("\n" + "="*60)
    print("🎯 TECHZE FEEDBACK SYSTEM - RESUMO EXECUTIVO")
    print("="*60)
    print(f"Score de Qualidade: {executive_summary['overall_quality_score']:.1f}/100")
    print(f"Status: {executive_summary['status'].upper()}")
    print(f"Relatório HTML: {html_report}")
    print("\nSlack Summary:")
    print(slack_summary)
    print("="*60)
    
    return executive_summary['overall_quality_score'] >= 75


if __name__ == "__main__":
    main() 