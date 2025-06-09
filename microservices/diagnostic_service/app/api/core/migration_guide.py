#!/usr/bin/env python3
"""
Guia de Migração - API Core

Script para auxiliar na migração das APIs v1 e v3 para a nova estrutura core.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any

class APIMigrationGuide:
    """Guia de migração para a API Core"""
    
    def __init__(self):
        self.migration_map = {
            "v1": {
                "auth": {
                    "old_endpoints": [
                        "/api/v1/auth/token",
                        "/api/v1/auth/login",
                        "/api/v1/auth/me",
                        "/api/v1/auth/logout",
                        "/api/v1/auth/health"
                    ],
                    "new_endpoints": [
                        "/api/core/auth/token",
                        "/api/core/auth/login",
                        "/api/core/auth/profile",
                        "/api/core/auth/logout",
                        "/api/core/auth/health"
                    ],
                    "changes": [
                        "Endpoint /me renomeado para /profile",
                        "Adicionado endpoint /register",
                        "Adicionado endpoint /refresh para renovação de tokens",
                        "Melhorada integração com Supabase"
                    ]
                },
                "diagnostics": {
                    "old_endpoints": [
                        "/api/v1/diagnostic/full"
                    ],
                    "new_endpoints": [
                        "/api/core/diagnostics/run",
                        "/api/core/diagnostics/health",
                        "/api/core/diagnostics/history",
                        "/api/core/diagnostics/{id}",
                        "/api/core/diagnostics/{id}/report"
                    ],
                    "changes": [
                        "Endpoint /full migrado para /run com parâmetros type",
                        "Adicionados tipos: quick, standard, comprehensive",
                        "Integração com IA para diagnósticos avançados",
                        "Sistema de histórico completo",
                        "Geração de relatórios personalizados"
                    ]
                }
            },
            "v3": {
                "ai": {
                    "old_endpoints": [
                        "/api/v3/ai/predict",
                        "/api/v3/ai/detect-anomalies",
                        "/api/v3/ai/analyze-patterns",
                        "/api/v3/ai/recommendations",
                        "/api/v3/ai/models",
                        "/api/v3/ai/train-model"
                    ],
                    "new_endpoints": [
                        "/api/core/ai/predict",
                        "/api/core/ai/detect-anomalies",
                        "/api/core/ai/analyze-patterns",
                        "/api/core/ai/recommendations",
                        "/api/core/ai/models",
                        "/api/core/ai/train-model",
                        "/api/core/ai/health"
                    ],
                    "changes": [
                        "Todos os endpoints mantidos com funcionalidades aprimoradas",
                        "Adicionado health check específico para IA",
                        "Melhorada gestão de modelos ML",
                        "Integração com sistema de chat para IA conversacional"
                    ]
                },
                "diagnostics": {
                    "old_endpoints": [
                        "/api/v3/diagnostic/run",
                        "/api/v3/diagnostic/health",
                        "/api/v3/diagnostic/status/{id}"
                    ],
                    "new_endpoints": [
                        "/api/core/diagnostics/run",
                        "/api/core/diagnostics/health",
                        "/api/core/diagnostics/{id}"
                    ],
                    "changes": [
                        "Endpoint /status/{id} renomeado para /{id}",
                        "Consolidação com funcionalidades da v1",
                        "Adicionadas opções de diagnóstico com IA"
                    ]
                }
            },
            "new_modules": {
                "automation": {
                    "endpoints": [
                        "/api/core/automation/tasks",
                        "/api/core/automation/workflows",
                        "/api/core/automation/rules",
                        "/api/core/automation/health"
                    ],
                    "description": "Novo módulo para automação de tarefas e workflows"
                },
                "analytics": {
                    "endpoints": [
                        "/api/core/analytics/query",
                        "/api/core/analytics/reports",
                        "/api/core/analytics/dashboards",
                        "/api/core/analytics/metrics/realtime",
                        "/api/core/analytics/trends"
                    ],
                    "description": "Módulo consolidado para análise e relatórios"
                },
                "performance": {
                    "endpoints": [
                        "/api/core/performance/metrics/system",
                        "/api/core/performance/metrics/database",
                        "/api/core/performance/alerts/rules",
                        "/api/core/performance/alerts/active",
                        "/api/core/performance/recommendations",
                        "/api/core/performance/dashboard"
                    ],
                    "description": "Módulo avançado de monitoramento e performance"
                },
                "chat": {
                    "endpoints": [
                        "/api/core/chat/sessions",
                        "/api/core/chat/sessions/{id}/messages",
                        "/api/core/chat/sessions/{id}/ws",
                        "/api/core/chat/assistant/capabilities",
                        "/api/core/chat/assistant/execute"
                    ],
                    "description": "Sistema de chat e assistente virtual inteligente"
                }
            }
        }
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """Gera relatório completo de migração"""
        report = {
            "migration_date": datetime.utcnow().isoformat(),
            "summary": {
                "total_old_endpoints": 0,
                "total_new_endpoints": 0,
                "new_modules": len(self.migration_map["new_modules"]),
                "breaking_changes": [],
                "improvements": []
            },
            "detailed_mapping": self.migration_map,
            "client_update_guide": self._generate_client_update_guide(),
            "testing_checklist": self._generate_testing_checklist()
        }
        
        # Calcular totais
        for version in ["v1", "v3"]:
            for module in self.migration_map[version]:
                report["summary"]["total_old_endpoints"] += len(
                    self.migration_map[version][module]["old_endpoints"]
                )
                report["summary"]["total_new_endpoints"] += len(
                    self.migration_map[version][module]["new_endpoints"]
                )
        
        # Adicionar novos endpoints
        for module in self.migration_map["new_modules"]:
            report["summary"]["total_new_endpoints"] += len(
                self.migration_map["new_modules"][module]["endpoints"]
            )
        
        return report
    
    def _generate_client_update_guide(self) -> Dict[str, List[str]]:
        """Gera guia de atualização para clientes"""
        return {
            "immediate_actions": [
                "Atualizar base URL de /api/v1 e /api/v3 para /api/core",
                "Verificar autenticação - endpoint /me agora é /profile",
                "Atualizar endpoints de diagnóstico conforme mapeamento",
                "Implementar tratamento para novos campos de resposta"
            ],
            "optional_upgrades": [
                "Integrar com novos módulos de automação",
                "Implementar chat e assistente virtual",
                "Utilizar novos endpoints de analytics",
                "Configurar alertas de performance",
                "Implementar WebSocket para tempo real"
            ],
            "code_examples": [
                "// Antes (v1)\nfetch('/api/v1/auth/me')\n\n// Depois (core)\nfetch('/api/core/auth/profile')",
                "// Antes (v1)\nfetch('/api/v1/diagnostic/full')\n\n// Depois (core)\nfetch('/api/core/diagnostics/run', {\n  method: 'POST',\n  body: JSON.stringify({type: 'comprehensive'})\n})",
                "// Novo - Chat WebSocket\nconst ws = new WebSocket('/api/core/chat/sessions/123/ws')\nws.onmessage = (event) => {\n  const message = JSON.parse(event.data)\n  console.log('Assistant:', message.message)\n}"
            ]
        }
    
    def _generate_testing_checklist(self) -> Dict[str, List[str]]:
        """Gera checklist de testes"""
        return {
            "authentication": [
                "✓ Login com email/senha",
                "✓ Registro de novo usuário",
                "✓ Renovação de token",
                "✓ Logout",
                "✓ Acesso a perfil do usuário",
                "✓ Health check de autenticação"
            ],
            "diagnostics": [
                "✓ Diagnóstico rápido",
                "✓ Diagnóstico padrão",
                "✓ Diagnóstico completo",
                "✓ Diagnóstico com IA",
                "✓ Histórico de diagnósticos",
                "✓ Geração de relatórios",
                "✓ Health check do sistema"
            ],
            "ai_features": [
                "✓ Predição de comportamento",
                "✓ Detecção de anomalias",
                "✓ Análise de padrões",
                "✓ Recomendações inteligentes",
                "✓ Gestão de modelos ML",
                "✓ Treinamento de modelos"
            ],
            "new_modules": [
                "✓ Criação e execução de tarefas automatizadas",
                "✓ Configuração de workflows",
                "✓ Geração de relatórios personalizados",
                "✓ Dashboards interativos",
                "✓ Alertas de performance",
                "✓ Chat com assistente virtual",
                "✓ WebSocket em tempo real"
            ],
            "performance": [
                "✓ Métricas do sistema",
                "✓ Métricas do banco de dados",
                "✓ Configuração de alertas",
                "✓ Dashboard de monitoramento",
                "✓ Recomendações de otimização"
            ]
        }
    
    def save_migration_report(self, filename: str = None) -> str:
        """Salva relatório de migração em arquivo"""
        if not filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"api_migration_report_{timestamp}.json"
        
        report = self.generate_migration_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def print_migration_summary(self):
        """Imprime resumo da migração"""
        report = self.generate_migration_report()
        
        print("\n" + "="*60)
        print("         RELATÓRIO DE MIGRAÇÃO - API CORE")
        print("="*60)
        
        print(f"\n📅 Data da Migração: {report['migration_date']}")
        
        summary = report['summary']
        print(f"\n📊 Resumo:")
        print(f"   • Endpoints antigos: {summary['total_old_endpoints']}")
        print(f"   • Endpoints novos: {summary['total_new_endpoints']}")
        print(f"   • Novos módulos: {summary['new_modules']}")
        
        print(f"\n🔄 Principais Mudanças:")
        print(f"   • APIs v1 e v3 consolidadas em /api/core")
        print(f"   • Estrutura modular implementada")
        print(f"   • Novos módulos: automation, analytics, performance, chat")
        print(f"   • Assistente virtual com IA integrado")
        print(f"   • WebSocket para comunicação em tempo real")
        
        print(f"\n🚀 Novos Recursos:")
        for module, info in report['detailed_mapping']['new_modules'].items():
            print(f"   • {module.title()}: {info['description']}")
        
        print(f"\n✅ Próximos Passos:")
        print(f"   1. Atualizar clientes para usar /api/core")
        print(f"   2. Executar testes de integração")
        print(f"   3. Implementar novos recursos opcionais")
        print(f"   4. Monitorar performance e métricas")
        print(f"   5. Treinar usuários nos novos recursos")
        
        print("\n" + "="*60)

def main():
    """Função principal"""
    migration_guide = APIMigrationGuide()
    
    # Imprimir resumo
    migration_guide.print_migration_summary()
    
    # Salvar relatório detalhado
    filename = migration_guide.save_migration_report()
    print(f"\n📄 Relatório detalhado salvo em: {filename}")
    
    print(f"\n💡 Para mais informações, consulte:")
    print(f"   • README.md da API Core")
    print(f"   • Documentação técnica completa")
    print(f"   • Exemplos de uso nos endpoints")

if __name__ == "__main__":
    main()