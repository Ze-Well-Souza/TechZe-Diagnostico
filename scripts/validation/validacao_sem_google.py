#!/usr/bin/env python3
"""
🎯 TechZe - Sistema de Validação Sem Google API
Versão simplificada que funciona apenas com Render API e testes básicos
"""

import asyncio
import aiohttp
import json
import time
import datetime
from typing import Dict, List, Any
from colorama import init, Fore, Style

init()

class TechZeValidadorSimples:
    """Sistema de validação simplificado"""
    
    def __init__(self, render_api_key: str):
        self.render_api_key = render_api_key
        self.render_headers = {
            'Authorization': f'Bearer {render_api_key}',
            'Content-Type': 'application/json'
        }
        
        self.urls_base = {
            'site_principal': 'https://techreparo.com',
            'api_backend': 'https://techze-diagnostico-api.onrender.com',
            'frontend': 'https://techze-diagnostico-frontend.onrender.com'
        }

    async def executar_validacao_completa(self) -> Dict[str, Any]:
        """Executa validação completa"""
        print(f"{Fore.CYAN}🚀 TechZe - Validação Simplificada{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⏰ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        
        render_status = await self.verificar_render_completo()
        connectivity_tests = await self.testar_conectividade_completa()
        
        relatorio = {
            'timestamp': datetime.datetime.now().isoformat(),
            'render_services': render_status,
            'connectivity': connectivity_tests,
            'score_geral': 0,
            'status_geral': 'UNKNOWN'
        }
        
        await self.calcular_score_final(relatorio)
        self.exibir_relatorio_detalhado(relatorio)
        
        return relatorio

    async def verificar_render_completo(self) -> Dict[str, Any]:
        """Verificação dos serviços Render"""
        print(f"{Fore.BLUE}🔧 Verificando Render Services...{Style.RESET_ALL}")
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                async with session.get(
                    "https://api.render.com/v1/services",
                    headers=self.render_headers
                ) as response:
                    if response.status == 200:
                        services = await response.json()
                        
                        total = len(services)
                        disponíveis = sum(1 for s in services if s.get('state') == 'available')
                        score = (disponíveis / total) * 100 if total > 0 else 0
                        
                        return {
                            'total_services': total,
                            'available': disponíveis,
                            'availability_score': score,
                            'services_info': [
                                {
                                    'name': s.get('name', 'Unknown'),
                                    'type': s.get('type', 'Unknown'), 
                                    'state': s.get('state', 'Unknown'),
                                    'env': s.get('env', 'Unknown')
                                } for s in services[:5]
                            ]
                        }
                    else:
                        return {'error': f'HTTP {response.status}'}
                        
        except Exception as e:
            return {'error': str(e)}

    async def testar_conectividade_completa(self) -> Dict[str, Any]:
        """Testa conectividade com URLs importantes"""
        print(f"{Fore.BLUE}🌐 Testando Conectividade...{Style.RESET_ALL}")
        
        urls_teste = [
            self.urls_base['site_principal'],
            f"{self.urls_base['api_backend']}/",
            f"{self.urls_base['frontend']}/"
        ]
        
        resultados = []
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            for url in urls_teste:
                resultado = await self.testar_url(session, url)
                resultados.append(resultado)
        
        sucessos = sum(1 for r in resultados if r.get('status') == 'OK')
        taxa_sucesso = (sucessos / len(urls_teste)) * 100
        
        return {
            'total_testadas': len(urls_teste),
            'sucessos': sucessos,
            'taxa_sucesso': taxa_sucesso,
            'detalhes': resultados
        }

    async def testar_url(self, session: aiohttp.ClientSession, url: str) -> Dict:
        """Testa uma URL específica"""
        start_time = time.time()
        
        try:
            async with session.get(url) as response:
                response_time = (time.time() - start_time) * 1000
                
                return {
                    'url': url,
                    'status_code': response.status,
                    'response_time_ms': round(response_time, 2),
                    'status': 'OK' if 200 <= response.status < 300 else 'ERROR'
                }
                
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'status': 'ERROR'
            }

    async def calcular_score_final(self, relatorio: Dict[str, Any]):
        """Calcula score final"""
        scores = []
        
        render_info = relatorio.get('render_services', {})
        if 'availability_score' in render_info:
            scores.append(render_info['availability_score'])
        
        conn_info = relatorio.get('connectivity', {})
        if 'taxa_sucesso' in conn_info:
            scores.append(conn_info['taxa_sucesso'])
        
        score_final = sum(scores) / len(scores) if scores else 0
        
        if score_final >= 90:
            status_final = '🟢 EXCELENTE'
        elif score_final >= 75:
            status_final = '🟡 BOM'
        elif score_final >= 60:
            status_final = '🟠 REGULAR'
        else:
            status_final = '🔴 CRÍTICO'
        
        relatorio['score_geral'] = round(score_final, 1)
        relatorio['status_geral'] = status_final

    def exibir_relatorio_detalhado(self, relatorio: Dict[str, Any]):
        """Exibe relatório detalhado"""
        print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🎯 RELATÓRIO TECHZE SIMPLIFICADO{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
        
        score = relatorio.get('score_geral', 0)
        status = relatorio.get('status_geral', 'UNKNOWN')
        print(f"{Fore.WHITE}📊 SCORE GERAL: {Fore.YELLOW}{score}%{Style.RESET_ALL} - {status}")
        
        render_info = relatorio.get('render_services', {})
        if 'availability_score' in render_info:
            print(f"{Fore.WHITE}🔧 Render: {Fore.GREEN}{render_info['availability_score']:.1f}%{Style.RESET_ALL}")
        
        conn_info = relatorio.get('connectivity', {})
        if 'taxa_sucesso' in conn_info:
            print(f"{Fore.WHITE}🌐 Conectividade: {Fore.GREEN}{conn_info['taxa_sucesso']:.1f}%{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}✅ Validação concluída!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

async def main():
    """Execução principal"""
    render_api_key = "rnd_Tj1JybEJij6A3UhouM7spm8LRbkX"
    
    validador = TechZeValidadorSimples(render_api_key)
    
    try:
        relatorio = await validador.executar_validacao_completa()
        
        with open('relatorio_simples.json', 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"{Fore.GREEN}📄 Relatório salvo em: relatorio_simples.json{Style.RESET_ALL}")
        
        return relatorio
        
    except Exception as e:
        print(f"{Fore.RED}❌ Erro: {str(e)}{Style.RESET_ALL}")
        return None

if __name__ == "__main__":
    asyncio.run(main())
