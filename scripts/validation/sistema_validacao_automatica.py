#!/usr/bin/env python3
"""
🎯 TechZe Diagnóstico - Sistema de Validação Automatizada
Sistema completo para testes, monitoramento e correções automáticas
"""

import os
import json
import time
import requests
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
import aiohttp
from colorama import init, Fore, Style

# Inicializar colorama
init()

@dataclass
class ValidacaoResult:
    """Resultado de uma validação"""
    url: str
    timestamp: str
    performance_score: float
    lcp: float
    fcp: float
    cls: float
    tbt: float
    seo_score: float
    accessibility_score: float
    best_practices_score: float
    issues: List[str]
    suggestions: List[str]
    render_logs: Optional[str] = None

class TechZeValidador:
    """Sistema completo de validação automatizada"""
    
    def __init__(self, config: Dict[str, str]):
        self.config = config
        self.render_api_key = config.get('RENDER_API_KEY')
        self.google_api_key = config.get('GOOGLE_API_KEY')
        self.base_url = config.get('BASE_URL', 'https://techreparo.com')
        self.render_api_base = "https://api.render.com/v1"
        self.pagespeed_api_base = "https://www.googleapis.com/pagespeedonline/v5"
        
        # URLs para testar
        self.test_urls = [
            f"{self.base_url}",
            f"{self.base_url}/diagnostics",
            f"{self.base_url}/health",
            f"{self.base_url}/api/v3/diagnostic/health"
        ]
        
        # Headers para APIs
        self.render_headers = {
            'Authorization': f'Bearer {self.render_api_key}',
            'Content-Type': 'application/json'
        }

    async def executar_validacao_completa(self) -> Dict[str, Any]:
        """Executa validação completa do sistema"""
        print(f"{Fore.CYAN}🚀 Iniciando Validação Completa do Sistema TechZe{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        
        resultados = {
            'timestamp': datetime.datetime.now().isoformat(),
            'render_status': await self.verificar_render_status(),
            'performance_tests': await self.executar_testes_performance(),
            'functional_tests': await self.executar_testes_funcionais(),
            'security_tests': await self.executar_testes_seguranca(),
            'issues_detectados': [],
            'correcoes_aplicadas': [],
            'relatorio_final': {}
        }
        
        # Análise e correções automáticas
        await self.analisar_e_corrigir_issues(resultados)
        
        # Gerar relatório
        await self.gerar_relatorio_final(resultados)
        
        return resultados

    async def verificar_render_status(self) -> Dict[str, Any]:
        """Verifica status dos serviços no Render"""
        print(f"{Fore.BLUE}📊 Verificando Status dos Serviços no Render...{Style.RESET_ALL}")
        
        try:
            async with aiohttp.ClientSession() as session:
                # Listar serviços
                async with session.get(
                    f"{self.render_api_base}/services",
                    headers=self.render_headers
                ) as response:
                    if response.status == 200:
                        services = await response.json()
                        
                        status_result = {
                            'status': 'success',
                            'services': [],
                            'deployments': [],
                            'metrics': {}
                        }
                        
                        for service in services:
                            service_info = {
                                'id': service.get('id'),
                                'name': service.get('name'),
                                'type': service.get('type'),
                                'env': service.get('env'),
                                'state': service.get('state'),
                                'url': service.get('serviceDetails', {}).get('url'),
                                'last_deploy': service.get('updatedAt'),
                                'health': await self.verificar_health_service(service.get('id'))
                            }
                            status_result['services'].append(service_info)
                            
                            # Buscar deployments recentes
                            deployments = await self.buscar_deployments_service(service.get('id'))
                            status_result['deployments'].extend(deployments)
                        
                        print(f"{Fore.GREEN}✅ Status dos serviços obtido com sucesso{Style.RESET_ALL}")
                        return status_result
                    else:
                        print(f"{Fore.RED}❌ Erro ao buscar serviços: {response.status}{Style.RESET_ALL}")
                        return {'status': 'error', 'message': f'HTTP {response.status}'}
                        
        except Exception as e:
            print(f"{Fore.RED}❌ Erro na verificação do Render: {str(e)}{Style.RESET_ALL}")
            return {'status': 'error', 'message': str(e)}

    async def verificar_health_service(self, service_id: str) -> Dict[str, Any]:
        """Verifica health de um serviço específico"""
        try:
            async with aiohttp.ClientSession() as session:
                # Buscar logs recentes para verificar saúde
                async with session.get(
                    f"{self.render_api_base}/services/{service_id}/logs",
                    headers=self.render_headers
                ) as response:
                    if response.status == 200:
                        logs = await response.json()
                        
                        # Analisar logs para determinar saúde
                        error_count = 0
                        recent_errors = []
                        
                        for log in logs[-50:]:  # Últimos 50 logs
                            if 'error' in log.get('message', '').lower():
                                error_count += 1
                                recent_errors.append(log.get('message'))
                        
                        health_status = 'healthy' if error_count < 5 else 'unhealthy'
                        
                        return {
                            'status': health_status,
                            'error_count': error_count,
                            'recent_errors': recent_errors[:5]  # Apenas os 5 mais recentes
                        }
                    
                    return {'status': 'unknown', 'error': f'HTTP {response.status}'}
                    
        except Exception as e:
            return {'status': 'unknown', 'error': str(e)}

    async def buscar_deployments_service(self, service_id: str) -> List[Dict[str, Any]]:
        """Busca deployments recentes de um serviço"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.render_api_base}/services/{service_id}/deploys",
                    headers=self.render_headers
                ) as response:
                    if response.status == 200:
                        deploys = await response.json()
                        
                        return [{
                            'service_id': service_id,
                            'deploy_id': deploy.get('id'),
                            'status': deploy.get('status'),
                            'created_at': deploy.get('createdAt'),
                            'finished_at': deploy.get('finishedAt'),
                            'commit': deploy.get('commit', {}).get('message', '')[:50]
                        } for deploy in deploys[:5]]  # Últimos 5 deploys
                    
                    return []
                    
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Erro ao buscar deploys: {str(e)}{Style.RESET_ALL}")
            return []

    async def executar_testes_performance(self) -> Dict[str, Any]:
        """Executa testes de performance usando Google PageSpeed Insights"""
        print(f"{Fore.BLUE}⚡ Executando Testes de Performance...{Style.RESET_ALL}")
        
        resultados = {
            'desktop': {},
            'mobile': {},
            'summary': {}
        }
        
        for url in self.test_urls:
            print(f"{Fore.CYAN}  📊 Testando: {url}{Style.RESET_ALL}")
            
            # Teste Desktop
            desktop_result = await self.testar_pagespeed(url, 'desktop')
            if desktop_result:
                resultados['desktop'][url] = desktop_result
            
            # Teste Mobile
            mobile_result = await self.testar_pagespeed(url, 'mobile')
            if mobile_result:
                resultados['mobile'][url] = mobile_result
            
            # Aguardar para evitar rate limiting
            await asyncio.sleep(2)
        
        # Calcular resumo
        resultados['summary'] = self.calcular_resumo_performance(resultados)
        
        return resultados

    async def testar_pagespeed(self, url: str, strategy: str) -> Optional[Dict[str, Any]]:
        """Executa teste no Google PageSpeed Insights"""
        try:
            params = {
                'url': url,
                'key': self.google_api_key,
                'strategy': strategy,
                'category': ['performance', 'accessibility', 'best-practices', 'seo']
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.pagespeed_api_base}/runPagespeed",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        lighthouse = data.get('lighthouseResult', {})
                        categories = lighthouse.get('categories', {})
                        audits = lighthouse.get('audits', {})
                        
                        return {
                            'url': url,
                            'strategy': strategy,
                            'timestamp': datetime.datetime.now().isoformat(),
                            'performance_score': categories.get('performance', {}).get('score', 0) * 100,
                            'accessibility_score': categories.get('accessibility', {}).get('score', 0) * 100,
                            'best_practices_score': categories.get('best-practices', {}).get('score', 0) * 100,
                            'seo_score': categories.get('seo', {}).get('score', 0) * 100,
                            'metrics': {
                                'lcp': audits.get('largest-contentful-paint', {}).get('numericValue', 0),
                                'fcp': audits.get('first-contentful-paint', {}).get('numericValue', 0),
                                'cls': audits.get('cumulative-layout-shift', {}).get('numericValue', 0),
                                'tbt': audits.get('total-blocking-time', {}).get('numericValue', 0),
                                'speed_index': audits.get('speed-index', {}).get('numericValue', 0)
                            },
                            'issues': self.extrair_issues_lighthouse(audits),
                            'opportunities': self.extrair_opportunities_lighthouse(audits)
                        }
                    else:
                        print(f"{Fore.YELLOW}⚠️ Erro PageSpeed para {url}: {response.status}{Style.RESET_ALL}")
                        return None
                        
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Erro no teste PageSpeed: {str(e)}{Style.RESET_ALL}")
            return None

    def extrair_issues_lighthouse(self, audits: Dict[str, Any]) -> List[str]:
        """Extrai issues do Lighthouse"""
        issues = []
        
        # Verificar auditorias críticas
        critical_audits = [
            'largest-contentful-paint',
            'cumulative-layout-shift',
            'total-blocking-time',
            'server-response-time'
        ]
        
        for audit_name in critical_audits:
            audit = audits.get(audit_name, {})
            if audit.get('score', 1) < 0.5:  # Score abaixo de 50%
                issues.append(f"{audit.get('title', audit_name)}: {audit.get('displayValue', 'N/A')}")
        
        return issues

    def extrair_opportunities_lighthouse(self, audits: Dict[str, Any]) -> List[str]:
        """Extrai oportunidades de otimização do Lighthouse"""
        opportunities = []
        
        opportunity_audits = [
            'unused-css-rules',
            'unused-javascript',
            'render-blocking-resources',
            'unminified-css',
            'unminified-javascript',
            'efficient-animated-content',
            'modern-image-formats'
        ]
        
        for audit_name in opportunity_audits:
            audit = audits.get(audit_name, {})
            if audit.get('score', 1) < 1 and audit.get('details', {}).get('overallSavingsMs', 0) > 100:
                savings = audit.get('details', {}).get('overallSavingsMs', 0)
                opportunities.append(f"{audit.get('title', audit_name)}: Economia de {savings}ms")
        
        return opportunities

    def calcular_resumo_performance(self, resultados: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula resumo dos testes de performance"""
        summary = {
            'total_urls_tested': len(self.test_urls),
            'avg_performance_desktop': 0,
            'avg_performance_mobile': 0,
            'critical_issues': [],
            'recommendations': []
        }
        
        # Calcular médias
        desktop_scores = []
        mobile_scores = []
        
        for url, data in resultados.get('desktop', {}).items():
            if data and 'performance_score' in data:
                desktop_scores.append(data['performance_score'])
        
        for url, data in resultados.get('mobile', {}).items():
            if data and 'performance_score' in data:
                mobile_scores.append(data['performance_score'])
        
        if desktop_scores:
            summary['avg_performance_desktop'] = sum(desktop_scores) / len(desktop_scores)
        
        if mobile_scores:
            summary['avg_performance_mobile'] = sum(mobile_scores) / len(mobile_scores)
        
        # Identificar issues críticos
        for strategy in ['desktop', 'mobile']:
            for url, data in resultados.get(strategy, {}).items():
                if data:
                    if data.get('performance_score', 0) < 50:
                        summary['critical_issues'].append(f"{url} ({strategy}): Score muito baixo")
                    
                    summary['recommendations'].extend(data.get('opportunities', []))
        
        return summary

    async def executar_testes_funcionais(self) -> Dict[str, Any]:
        """Executa testes funcionais das APIs"""
        print(f"{Fore.BLUE}🔧 Executando Testes Funcionais...{Style.RESET_ALL}")
        
        testes = {
            'api_health': await self.testar_api_health(),
            'endpoints_core': await self.testar_endpoints_core(),
            'database_connection': await self.testar_database_connection(),
            'authentication': await self.testar_authentication()
        }
        
        return testes

    async def testar_api_health(self) -> Dict[str, Any]:
        """Testa endpoint de health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'status': 'success',
                            'response_time': response.headers.get('X-Response-Time', 'N/A'),
                            'data': data
                        }
                    else:
                        return {
                            'status': 'error',
                            'status_code': response.status,
                            'message': await response.text()
                        }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def testar_endpoints_core(self) -> Dict[str, Any]:
        """Testa endpoints principais da API"""
        endpoints = [
            '/api/v3/diagnostic/health',
            '/api/v3/ai/models',
            '/api/v3/performance/stats'
        ]
        
        resultados = {}
        
        for endpoint in endpoints:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{self.base_url}{endpoint}") as response:
                        resultados[endpoint] = {
                            'status_code': response.status,
                            'success': response.status == 200,
                            'response_time': response.headers.get('X-Response-Time', 'N/A')
                        }
                        
                        if response.status == 200:
                            data = await response.json()
                            resultados[endpoint]['data_length'] = len(str(data))
                        
            except Exception as e:
                resultados[endpoint] = {
                    'success': False,
                    'error': str(e)
                }
        
        return resultados

    async def testar_database_connection(self) -> Dict[str, Any]:
        """Testa conexão com database via API"""
        try:
            async with aiohttp.ClientSession() as session:
                # Tenta fazer uma query simples
                async with session.get(f"{self.base_url}/api/v3/diagnostic/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        db_status = data.get('database', {}).get('status', 'unknown')
                        
                        return {
                            'status': 'success' if db_status == 'healthy' else 'warning',
                            'db_status': db_status,
                            'details': data.get('database', {})
                        }
                    else:
                        return {
                            'status': 'error',
                            'message': f'HTTP {response.status}'
                        }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def testar_authentication(self) -> Dict[str, Any]:
        """Testa sistema de autenticação"""
        # Implementar testes de auth quando necessário
        return {
            'status': 'skipped',
            'message': 'Testes de autenticação não implementados ainda'
        }

    async def executar_testes_seguranca(self) -> Dict[str, Any]:
        """Executa testes básicos de segurança"""
        print(f"{Fore.BLUE}🔒 Executando Testes de Segurança...{Style.RESET_ALL}")
        
        testes = {
            'https_redirect': await self.testar_https_redirect(),
            'security_headers': await self.testar_security_headers(),
            'cors_policy': await self.testar_cors_policy()
        }
        
        return testes

    async def testar_https_redirect(self) -> Dict[str, Any]:
        """Testa redirecionamento HTTPS"""
        try:
            http_url = self.base_url.replace('https://', 'http://')
            
            async with aiohttp.ClientSession() as session:
                async with session.get(http_url, allow_redirects=False) as response:
                    if response.status in [301, 302, 307, 308]:
                        location = response.headers.get('Location', '')
                        if location.startswith('https://'):
                            return {'status': 'success', 'redirect_to': location}
                    
                    return {
                        'status': 'warning',
                        'message': f'Sem redirecionamento HTTPS adequado: {response.status}'
                    }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def testar_security_headers(self) -> Dict[str, Any]:
        """Testa presença de headers de segurança"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.base_url) as response:
                    headers = response.headers
                    
                    security_headers = {
                        'X-Frame-Options': headers.get('X-Frame-Options'),
                        'X-Content-Type-Options': headers.get('X-Content-Type-Options'),
                        'X-XSS-Protection': headers.get('X-XSS-Protection'),
                        'Strict-Transport-Security': headers.get('Strict-Transport-Security'),
                        'Content-Security-Policy': headers.get('Content-Security-Policy')
                    }
                    
                    missing_headers = [k for k, v in security_headers.items() if not v]
                    
                    return {
                        'status': 'success' if len(missing_headers) < 2 else 'warning',
                        'headers_present': {k: v for k, v in security_headers.items() if v},
                        'missing_headers': missing_headers
                    }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def testar_cors_policy(self) -> Dict[str, Any]:
        """Testa política CORS"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {'Origin': 'https://example.com'}
                async with session.options(f"{self.base_url}/api/v3/diagnostic/health", headers=headers) as response:
                    cors_headers = {
                        'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                        'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                        'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
                    }
                    
                    return {
                        'status': 'success',
                        'cors_headers': cors_headers,
                        'allows_origin': cors_headers['Access-Control-Allow-Origin'] is not None
                    }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def analisar_e_corrigir_issues(self, resultados: Dict[str, Any]):
        """Analisa resultados e aplica correções automáticas quando possível"""
        print(f"{Fore.BLUE}🔧 Analisando Issues e Aplicando Correções...{Style.RESET_ALL}")
        
        issues_detectados = []
        correcoes_aplicadas = []
        
        # Analisar performance
        performance = resultados.get('performance_tests', {})
        summary = performance.get('summary', {})
        
        if summary.get('avg_performance_desktop', 0) < 70:
            issues_detectados.append("Performance desktop abaixo do esperado")
            
        if summary.get('avg_performance_mobile', 0) < 70:
            issues_detectados.append("Performance mobile abaixo do esperado")
        
        # Analisar testes funcionais
        functional = resultados.get('functional_tests', {})
        
        for test_name, test_result in functional.items():
            if test_result.get('status') == 'error':
                issues_detectados.append(f"Erro no teste funcional: {test_name}")
        
        # Analisar render status
        render_status = resultados.get('render_status', {})
        
        for service in render_status.get('services', []):
            if service.get('state') != 'active':
                issues_detectados.append(f"Serviço {service.get('name')} não está ativo")
                
                # Tentar restart automático
                if await self.tentar_restart_service(service.get('id')):
                    correcoes_aplicadas.append(f"Restart aplicado ao serviço {service.get('name')}")
        
        resultados['issues_detectados'] = issues_detectados
        resultados['correcoes_aplicadas'] = correcoes_aplicadas

    async def tentar_restart_service(self, service_id: str) -> bool:
        """Tenta reiniciar um serviço no Render"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.render_api_base}/services/{service_id}/restart",
                    headers=self.render_headers
                ) as response:
                    if response.status == 200:
                        print(f"{Fore.GREEN}✅ Serviço {service_id} reiniciado com sucesso{Style.RESET_ALL}")
                        return True
                    else:
                        print(f"{Fore.YELLOW}⚠️ Falha ao reiniciar serviço {service_id}: {response.status}{Style.RESET_ALL}")
                        return False
        except Exception as e:
            print(f"{Fore.RED}❌ Erro ao tentar reiniciar serviço: {str(e)}{Style.RESET_ALL}")
            return False

    async def gerar_relatorio_final(self, resultados: Dict[str, Any]):
        """Gera relatório final da validação"""
        print(f"{Fore.CYAN}📊 Gerando Relatório Final...{Style.RESET_ALL}")
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"relatorio_validacao_{timestamp}.json"
        
        # Calcular score geral
        performance_summary = resultados.get('performance_tests', {}).get('summary', {})
        avg_desktop = performance_summary.get('avg_performance_desktop', 0)
        avg_mobile = performance_summary.get('avg_performance_mobile', 0)
        
        functional_tests = resultados.get('functional_tests', {})
        functional_success_rate = len([t for t in functional_tests.values() if t.get('success', False)]) / max(len(functional_tests), 1) * 100
        
        render_services = resultados.get('render_status', {}).get('services', [])
        active_services = len([s for s in render_services if s.get('state') == 'active'])
        total_services = max(len(render_services), 1)
        service_health_rate = active_services / total_services * 100
        
        overall_score = (avg_desktop + avg_mobile + functional_success_rate + service_health_rate) / 4
        
        relatorio_final = {
            'timestamp': resultados['timestamp'],
            'overall_score': overall_score,
            'status': 'healthy' if overall_score > 80 else 'warning' if overall_score > 60 else 'critical',
            'performance': {
                'desktop_avg': avg_desktop,
                'mobile_avg': avg_mobile
            },
            'functional_health': functional_success_rate,
            'service_health': service_health_rate,
            'issues_count': len(resultados.get('issues_detectados', [])),
            'corrections_applied': len(resultados.get('correcoes_aplicadas', [])),
            'recommendations': performance_summary.get('recommendations', [])[:5]  # Top 5
        }
        
        resultados['relatorio_final'] = relatorio_final
        
        # Salvar relatório
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)
        
        # Exibir resumo
        self.exibir_resumo_final(relatorio_final)
        
        print(f"{Fore.GREEN}✅ Relatório salvo em: {filename}{Style.RESET_ALL}")

    def exibir_resumo_final(self, relatorio: Dict[str, Any]):
        """Exibe resumo visual do relatório"""
        status = relatorio['status']
        score = relatorio['overall_score']
        
        # Cores baseadas no status
        color = Fore.GREEN if status == 'healthy' else Fore.YELLOW if status == 'warning' else Fore.RED
        
        print(f"\n{color}{'='*60}{Style.RESET_ALL}")
        print(f"{color}🎯 RELATÓRIO FINAL - TECHZE DIAGNÓSTICO{Style.RESET_ALL}")
        print(f"{color}{'='*60}{Style.RESET_ALL}")
        
        print(f"\n{Fore.WHITE}📊 Score Geral: {color}{score:.1f}/100{Style.RESET_ALL}")
        print(f"{Fore.WHITE}🏥 Status: {color}{status.upper()}{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}📈 Performance:{Style.RESET_ALL}")
        print(f"  Desktop: {relatorio['performance']['desktop_avg']:.1f}/100")
        print(f"  Mobile:  {relatorio['performance']['mobile_avg']:.1f}/100")
        
        print(f"\n{Fore.CYAN}🔧 Saúde Funcional: {relatorio['functional_health']:.1f}%{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🚀 Saúde Serviços: {relatorio['service_health']:.1f}%{Style.RESET_ALL}")
        
        print(f"\n{Fore.CYAN}📋 Issues Detectados: {relatorio['issues_count']}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}✅ Correções Aplicadas: {relatorio['corrections_applied']}{Style.RESET_ALL}")
        
        if relatorio.get('recommendations'):
            print(f"\n{Fore.CYAN}💡 Top Recomendações:{Style.RESET_ALL}")
            for i, rec in enumerate(relatorio['recommendations'][:3], 1):
                print(f"  {i}. {rec}")
        
        print(f"\n{color}{'='*60}{Style.RESET_ALL}")

async def main():
    """Função principal"""
    print(f"{Fore.CYAN}🎯 TechZe Diagnóstico - Sistema de Validação Automatizada{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    # Configuração
    config = {
        'RENDER_API_KEY': os.getenv('RENDER_API_KEY', 'rnd_Tj1JybEJij6A3UhouM7spm8LRbkX'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY', ''),  # Usuário deve fornecer
        'BASE_URL': os.getenv('BASE_URL', 'https://techreparo.com')
    }
    
    # Verificar se tem API key do Google
    if not config['GOOGLE_API_KEY']:
        print(f"{Fore.YELLOW}⚠️ Google API Key não encontrada!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Para obter uma chave:{Style.RESET_ALL}")
        print("1. Acesse: https://developers.google.com/speed/docs/insights/v5/get-started")
        print("2. Clique em 'Get a Key'")
        print("3. Configure a variável: export GOOGLE_API_KEY=sua_chave")
        print(f"\n{Fore.YELLOW}Continuando sem testes de performance...{Style.RESET_ALL}\n")
    
    # Criar validador
    validador = TechZeValidador(config)
    
    try:
        # Executar validação completa
        resultados = await validador.executar_validacao_completa()
        
        print(f"\n{Fore.GREEN}🎉 Validação completa finalizada!{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Validação interrompida pelo usuário{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}❌ Erro durante validação: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    # Instalar dependências se necessário
    try:
        import aiohttp
        import colorama
    except ImportError:
        print("Instalando dependências...")
        os.system("pip install aiohttp colorama")
        import aiohttp
        import colorama
    
    # Executar
    asyncio.run(main()) 