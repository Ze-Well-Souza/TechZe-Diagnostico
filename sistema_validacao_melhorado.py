#!/usr/bin/env python3
"""
🎯 TechZe Diagnóstico - Sistema de Validação Automatizada Melhorado
Sistema otimizado para testes, monitoramento e correções automáticas
Versão: 2.0 - Integrada com APIs Google e Render
"""

import os
import json
import time
import requests
import datetime
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from colorama import init, Fore, Style

# Inicializar colorama
init()

@dataclass
class ValidacaoConfig:
    """Configuração do sistema de validação"""
    render_api_key: str
    google_api_key: str
    base_url: str = "https://techreparo.com"
    api_backend: str = "https://techze-diagnostico-api.onrender.com"
    api_frontend: str = "https://techze-diagnostico-frontend.onrender.com"
    timeout: int = 30
    max_retries: int = 3

@dataclass
class ResultadoValidacao:
    """Resultado detalhado de validação"""
    url: str
    timestamp: str
    status: str
    performance_score: float
    core_vitals: Dict[str, float]
    issues: List[str]
    suggestions: List[str]
    render_status: Optional[str] = None
    response_time: Optional[float] = None

class TechZeValidadorMelhorado:
    """Sistema completo de validação automatizada melhorado"""
    
    def __init__(self, config: ValidacaoConfig):
        self.config = config
        self.render_headers = {
            'Authorization': f'Bearer {config.render_api_key}',
            'Content-Type': 'application/json'
        }
        
        # URLs prioritárias para teste
        self.urls_teste = [
            config.base_url,
            f"{config.base_url}/diagnostics",
            f"{config.api_backend}/health",
            f"{config.api_backend}/api/v3/diagnostic/health",
            f"{config.api_backend}/api/v3/ai/models",
            f"{config.api_frontend}/"
        ]

    async def executar_validacao_completa(self) -> Dict[str, Any]:
        """Executa validação completa e otimizada"""
        print(f"{Fore.CYAN}🚀 TechZe - Validação Automatizada v2.0{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        
        # Executar todas as validações em paralelo para máxima eficiência
        tasks = [
            self.verificar_status_render(),
            self.executar_testes_performance(),
            self.verificar_apis_funcionais(),
            self.verificar_seguranca_basica()
        ]
        
        resultados = await asyncio.gather(*tasks, return_exceptions=True)
        
        relatorio_final = {
            'timestamp': datetime.datetime.now().isoformat(),
            'render_status': resultados[0] if not isinstance(resultados[0], Exception) else {'error': str(resultados[0])},
            'performance': resultados[1] if not isinstance(resultados[1], Exception) else {'error': str(resultados[1])},
            'apis': resultados[2] if not isinstance(resultados[2], Exception) else {'error': str(resultados[2])},
            'security': resultados[3] if not isinstance(resultados[3], Exception) else {'error': str(resultados[3])},
            'score_geral': 0,
            'status_geral': 'UNKNOWN',
            'acoes_recomendadas': []
        }
        
        # Calcular score geral e status
        await self.calcular_score_geral(relatorio_final)
        
        # Exibir relatório
        self.exibir_relatorio_final(relatorio_final)
        
        return relatorio_final

    async def verificar_status_render(self) -> Dict[str, Any]:
        """Verifica status dos serviços no Render de forma otimizada"""
        print(f"{Fore.BLUE}📊 Verificando Render Services...{Style.RESET_ALL}")
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(
                    "https://api.render.com/v1/services",
                    headers=self.render_headers
                ) as response:
                    if response.status == 200:
                        services = await response.json()
                        
                        # Processar serviços em paralelo
                        service_tasks = [
                            self.processar_service_info(service) 
                            for service in services[:10]  # Limitar a 10 serviços
                        ]
                        
                        services_info = await asyncio.gather(*service_tasks, return_exceptions=True)
                        
                        services_ativos = [s for s in services_info if isinstance(s, dict) and s.get('status') == 'available']
                        
                        return {
                            'status': 'success',
                            'total_services': len(services),
                            'services_ativos': len(services_ativos),
                            'services': services_info[:5],  # Apenas os 5 primeiros no relatório
                            'health_score': (len(services_ativos) / len(services)) * 100 if services else 0
                        }
                    else:
                        return {'status': 'error', 'code': response.status}
                        
        except Exception as e:
            print(f"{Fore.RED}❌ Erro Render API: {str(e)[:100]}{Style.RESET_ALL}")
            return {'status': 'error', 'message': str(e)[:100]}

    async def processar_service_info(self, service: Dict) -> Dict[str, Any]:
        """Processa informações de um serviço específico"""
        return {
            'name': service.get('name'),
            'type': service.get('type'),
            'status': service.get('state'),
            'url': service.get('serviceDetails', {}).get('url'),
            'updated': service.get('updatedAt'),
            'env': service.get('env')
        }

    async def executar_testes_performance(self) -> Dict[str, Any]:
        """Executa testes de performance usando Google PageSpeed"""
        print(f"{Fore.BLUE}⚡ Testando Performance (Google PageSpeed)...{Style.RESET_ALL}")
        
        resultados = {'desktop': {}, 'mobile': {}, 'resumo': {}}
        
        # Testar apenas a URL principal para otimizar tempo
        url_principal = self.config.base_url
        
        try:
            # Executar testes desktop e mobile em paralelo
            tasks = [
                self.testar_pagespeed(url_principal, 'desktop'),
                self.testar_pagespeed(url_principal, 'mobile')
            ]
            
            desktop_result, mobile_result = await asyncio.gather(*tasks, return_exceptions=True)
            
            if not isinstance(desktop_result, Exception):
                resultados['desktop'] = desktop_result
            if not isinstance(mobile_result, Exception):
                resultados['mobile'] = mobile_result
                
            # Calcular resumo
            resultados['resumo'] = self.calcular_resumo_performance(resultados)
            
            return resultados
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erro Performance: {str(e)[:100]}{Style.RESET_ALL}")
            return {'error': str(e)[:100]}

    async def testar_pagespeed(self, url: str, strategy: str) -> Dict[str, Any]:
        """Testa uma URL específica no PageSpeed Insights"""
        api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        params = {
            'url': url,
            'key': self.config.google_api_key,
            'strategy': strategy,
            'category': ['PERFORMANCE', 'ACCESSIBILITY', 'BEST_PRACTICES', 'SEO']
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        lighthouse = data.get('lighthouseResult', {})
                        categories = lighthouse.get('categories', {})
                        audits = lighthouse.get('audits', {})
                        
                        # Extrair Core Web Vitals
                        core_vitals = {
                            'lcp': audits.get('largest-contentful-paint', {}).get('numericValue', 0) / 1000,
                            'fcp': audits.get('first-contentful-paint', {}).get('numericValue', 0) / 1000,
                            'cls': audits.get('cumulative-layout-shift', {}).get('numericValue', 0),
                            'tbt': audits.get('total-blocking-time', {}).get('numericValue', 0)
                        }
                        
                        return {
                            'url': url,
                            'strategy': strategy,
                            'performance_score': categories.get('performance', {}).get('score', 0) * 100,
                            'accessibility_score': categories.get('accessibility', {}).get('score', 0) * 100,
                            'seo_score': categories.get('seo', {}).get('score', 0) * 100,
                            'best_practices_score': categories.get('best-practices', {}).get('score', 0) * 100,
                            'core_vitals': core_vitals,
                            'timestamp': datetime.datetime.now().isoformat()
                        }
                    else:
                        return {'error': f'HTTP {response.status}', 'strategy': strategy}
                        
        except Exception as e:
            return {'error': str(e)[:100], 'strategy': strategy}

    def calcular_resumo_performance(self, resultados: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula resumo das métricas de performance"""
        scores = []
        vitals = {'lcp': [], 'fcp': [], 'cls': [], 'tbt': []}
        
        for strategy_result in [resultados.get('desktop', {}), resultados.get('mobile', {})]:
            if 'performance_score' in strategy_result:
                scores.append(strategy_result['performance_score'])
                
                core_vitals = strategy_result.get('core_vitals', {})
                for vital, value in core_vitals.items():
                    if vital in vitals:
                        vitals[vital].append(value)
        
        # Calcular médias
        avg_score = sum(scores) / len(scores) if scores else 0
        avg_vitals = {
            vital: sum(values) / len(values) if values else 0
            for vital, values in vitals.items()
        }
        
        # Determinar status baseado nas métricas
        status = 'BOM' if avg_score >= 90 else 'MÉDIO' if avg_score >= 70 else 'RUIM'
        
        return {
            'score_medio': round(avg_score, 1),
            'core_vitals_medio': avg_vitals,
            'status': status,
            'total_testes': len(scores)
        }

    async def verificar_apis_funcionais(self) -> Dict[str, Any]:
        """Verifica se as APIs principais estão funcionais"""
        print(f"{Fore.BLUE}🔍 Verificando APIs Funcionais...{Style.RESET_ALL}")
        
        # URLs críticas para testar
        apis_criticas = [
            f"{self.config.api_backend}/health",
            f"{self.config.api_backend}/api/v3/diagnostic/health",
            f"{self.config.api_backend}/api/v3/ai/models"
        ]
        
        resultados = []
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                tasks = [self.testar_api_endpoint(session, url) for url in apis_criticas]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if not isinstance(result, Exception):
                        resultados.append(result)
                
                # Calcular estatísticas
                total_apis = len(apis_criticas)
                apis_funcionais = len([r for r in resultados if r.get('status') == 'OK'])
                
                return {
                    'total_testadas': total_apis,
                    'funcionais': apis_funcionais,
                    'taxa_sucesso': (apis_funcionais / total_apis) * 100 if total_apis > 0 else 0,
                    'detalhes': resultados,
                    'status_geral': 'OK' if apis_funcionais == total_apis else 'PARCIAL' if apis_funcionais > 0 else 'ERRO'
                }
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erro APIs: {str(e)[:100]}{Style.RESET_ALL}")
            return {'error': str(e)[:100]}

    async def testar_api_endpoint(self, session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
        """Testa um endpoint específico da API"""
        start_time = time.time()
        
        try:
            async with session.get(url) as response:
                response_time = (time.time() - start_time) * 1000
                
                return {
                    'url': url,
                    'status_code': response.status,
                    'response_time_ms': round(response_time, 2),
                    'status': 'OK' if 200 <= response.status < 300 else 'ERROR',
                    'timestamp': datetime.datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'url': url,
                'error': str(e)[:100],
                'status': 'ERROR',
                'timestamp': datetime.datetime.now().isoformat()
            }

    async def verificar_seguranca_basica(self) -> Dict[str, Any]:
        """Verifica aspectos básicos de segurança"""
        print(f"{Fore.BLUE}🔒 Verificando Segurança Básica...{Style.RESET_ALL}")
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get(self.config.base_url) as response:
                    headers = dict(response.headers)
                    
                    # Verificar headers de segurança importantes
                    security_headers = {
                        'strict-transport-security': 'HSTS' in headers.get('strict-transport-security', ''),
                        'x-content-type-options': headers.get('x-content-type-options') == 'nosniff',
                        'x-frame-options': 'x-frame-options' in headers,
                        'content-security-policy': 'content-security-policy' in headers,
                        'https_redirect': str(response.url).startswith('https://')
                    }
                    
                    security_score = (sum(security_headers.values()) / len(security_headers)) * 100
                    
                    return {
                        'https_ativo': str(response.url).startswith('https://'),
                        'security_headers': security_headers,
                        'security_score': round(security_score, 1),
                        'status': 'BOM' if security_score >= 80 else 'MÉDIO' if security_score >= 60 else 'RUIM'
                    }
                    
        except Exception as e:
            print(f"{Fore.RED}❌ Erro Segurança: {str(e)[:100]}{Style.RESET_ALL}")
            return {'error': str(e)[:100]}

    async def calcular_score_geral(self, relatorio: Dict[str, Any]):
        """Calcula score geral do sistema"""
        scores = []
        
        # Score do Render
        if 'render_status' in relatorio and 'health_score' in relatorio['render_status']:
            scores.append(relatorio['render_status']['health_score'])
        
        # Score de Performance
        if 'performance' in relatorio and 'resumo' in relatorio['performance']:
            scores.append(relatorio['performance']['resumo'].get('score_medio', 0))
        
        # Score das APIs
        if 'apis' in relatorio and 'taxa_sucesso' in relatorio['apis']:
            scores.append(relatorio['apis']['taxa_sucesso'])
        
        # Score de Segurança
        if 'security' in relatorio and 'security_score' in relatorio['security']:
            scores.append(relatorio['security']['security_score'])
        
        # Calcular média ponderada
        score_geral = sum(scores) / len(scores) if scores else 0
        
        # Determinar status geral
        if score_geral >= 90:
            status_geral = '🟢 EXCELENTE'
        elif score_geral >= 75:
            status_geral = '🟡 BOM'
        elif score_geral >= 60:
            status_geral = '🟠 MÉDIO'
        else:
            status_geral = '🔴 CRÍTICO'
        
        relatorio['score_geral'] = round(score_geral, 1)
        relatorio['status_geral'] = status_geral
        
        # Adicionar recomendações baseadas no score
        if score_geral < 75:
            relatorio['acoes_recomendadas'] = [
                "🔧 Otimizar performance do site",
                "🛡️ Melhorar headers de segurança",
                "⚡ Verificar tempo de resposta das APIs",
                "📊 Monitorar métricas Core Web Vitals"
            ]

    def exibir_relatorio_final(self, relatorio: Dict[str, Any]):
        """Exibe relatório final formatado"""
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🎯 RELATÓRIO FINAL - TECHZE DIAGNÓSTICO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
        
        # Score Geral
        score = relatorio.get('score_geral', 0)
        status = relatorio.get('status_geral', 'UNKNOWN')
        print(f"{Fore.WHITE}📊 SCORE GERAL: {Fore.YELLOW}{score}%{Style.RESET_ALL} - {status}")
        
        # Render Status
        render_info = relatorio.get('render_status', {})
        if 'health_score' in render_info:
            print(f"{Fore.WHITE}🔧 Render Services: {Fore.GREEN}{render_info['health_score']:.1f}%{Style.RESET_ALL}")
        
        # Performance
        perf_info = relatorio.get('performance', {}).get('resumo', {})
        if 'score_medio' in perf_info:
            print(f"{Fore.WHITE}⚡ Performance: {Fore.GREEN}{perf_info['score_medio']:.1f}%{Style.RESET_ALL}")
        
        # APIs
        api_info = relatorio.get('apis', {})
        if 'taxa_sucesso' in api_info:
            print(f"{Fore.WHITE}🔍 APIs: {Fore.GREEN}{api_info['taxa_sucesso']:.1f}%{Style.RESET_ALL}")
        
        # Segurança
        sec_info = relatorio.get('security', {})
        if 'security_score' in sec_info:
            print(f"{Fore.WHITE}🔒 Segurança: {Fore.GREEN}{sec_info['security_score']:.1f}%{Style.RESET_ALL}")
        
        # Recomendações
        if relatorio.get('acoes_recomendadas'):
            print(f"\n{Fore.YELLOW}📋 AÇÕES RECOMENDADAS:{Style.RESET_ALL}")
            for acao in relatorio['acoes_recomendadas']:
                print(f"{Fore.WHITE}  • {acao}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}✅ Validação completa finalizada!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")

# Função principal
async def main():
    """Função principal de execução"""
    print(f"{Fore.MAGENTA}🎯 TechZe Diagnóstico - Sistema de Validação v2.0{Style.RESET_ALL}\n")
    
    # Configuração (você deve atualizar com suas chaves)
    config = ValidacaoConfig(
        render_api_key="rnd_Tj1JybEJij6A3UhouM7spm8LRbkX",  # Sua chave fornecida
        google_api_key="SUA_GOOGLE_API_KEY_AQUI",  # Obter em: https://developers.google.com/speed/docs/insights/v5/get-started
        base_url="https://techreparo.com",
        api_backend="https://techze-diagnostico-api.onrender.com",
        api_frontend="https://techze-diagnostico-frontend.onrender.com"
    )
    
    # Verificar se as chaves estão configuradas
    if config.google_api_key == "SUA_GOOGLE_API_KEY_AQUI":
        print(f"{Fore.YELLOW}⚠️ AVISO: Configure sua Google API Key para testes de performance{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Obtenha em: https://developers.google.com/speed/docs/insights/v5/get-started{Style.RESET_ALL}\n")
    
    # Executar validação
    validador = TechZeValidadorMelhorado(config)
    
    try:
        relatorio = await validador.executar_validacao_completa()
        
        # Salvar relatório em arquivo
        with open('relatorio_validacao_techze.json', 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"{Fore.GREEN}📄 Relatório salvo em: relatorio_validacao_techze.json{Style.RESET_ALL}")
        
        return relatorio
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erro durante validação: {str(e)}{Style.RESET_ALL}")
        return None

if __name__ == "__main__":
    asyncio.run(main()) 