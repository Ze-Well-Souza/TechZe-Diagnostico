#!/usr/bin/env python3
"""
Teste da API TechZe em execução
Verifica se todos os endpoints estão funcionando
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class APITester:
    """Classe para testar a API TechZe"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
    async def test_endpoint(self, session: aiohttp.ClientSession, method: str, endpoint: str, 
                           data: Dict[Any, Any] = None) -> Dict[str, Any]:
        """Testa um endpoint específico"""
        try:
            url = f"{self.base_url}{endpoint}"
            
            if method.upper() == "GET":
                async with session.get(url, headers=self.headers) as response:
                    return {
                        "endpoint": endpoint,
                        "method": method,
                        "status": response.status,
                        "success": response.status < 400,
                        "response": await response.text() if response.status < 500 else "Error"
                    }
            elif method.upper() == "POST":
                async with session.post(url, headers=self.headers, json=data) as response:
                    return {
                        "endpoint": endpoint,
                        "method": method,
                        "status": response.status,
                        "success": response.status < 400,
                        "response": await response.text() if response.status < 500 else "Error"
                    }
                    
        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method,
                "status": 0,
                "success": False,
                "error": str(e)
            }
    
    async def test_health_check(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Testa o health check"""
        return await self.test_endpoint(session, "GET", "/health")
    
    async def test_docs(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Testa a documentação"""
        return await self.test_endpoint(session, "GET", "/docs")
    
    async def test_openapi(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Testa o OpenAPI spec"""
        return await self.test_endpoint(session, "GET", "/openapi.json")
    
    async def test_api_core(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Testa o endpoint consolidado"""
        return await self.test_endpoint(session, "GET", "/api/core/")
    
    async def test_orcamentos_list(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Testa listagem de orçamentos"""
        return await self.test_endpoint(session, "GET", "/api/core/orcamentos/")
    
    async def test_estoque_list(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Testa listagem de estoque"""
        return await self.test_endpoint(session, "GET", "/api/core/estoque/")
    
    async def test_ordem_servico_list(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        """Testa listagem de OS"""
        return await self.test_endpoint(session, "GET", "/api/core/ordem-servico/")
    
    async def test_all_endpoints(self) -> Dict[str, Any]:
        """Testa todos os endpoints principais"""
        logger.info("🧪 INICIANDO TESTE DA API TECHZE")
        logger.info("=" * 50)
        
        tests = []
        
        async with aiohttp.ClientSession() as session:
            # Testes básicos
            tests.append(await self.test_health_check(session))
            tests.append(await self.test_docs(session))
            tests.append(await self.test_openapi(session))
            
            # Testes da API Core
            tests.append(await self.test_api_core(session))
            tests.append(await self.test_orcamentos_list(session))
            tests.append(await self.test_estoque_list(session))
            tests.append(await self.test_ordem_servico_list(session))
        
        # Análise dos resultados
        total_tests = len(tests)
        successful_tests = sum(1 for test in tests if test.get('success', False))
        
        logger.info("\n📊 RESULTADOS DOS TESTES")
        logger.info("=" * 30)
        
        for test in tests:
            status_icon = "✅" if test.get('success', False) else "❌"
            status_code = test.get('status', 0)
            endpoint = test.get('endpoint', 'Unknown')
            method = test.get('method', 'GET')
            
            logger.info(f"{status_icon} {method} {endpoint} - Status: {status_code}")
            
            if not test.get('success', False) and 'error' in test:
                logger.error(f"   Error: {test['error']}")
        
        logger.info(f"\n🎯 Resumo: {successful_tests}/{total_tests} testes passaram")
        
        if successful_tests == total_tests:
            logger.info("🎉 TODOS OS TESTES PASSARAM! API FUNCIONANDO PERFEITAMENTE!")
        else:
            logger.warning(f"⚠️ {total_tests - successful_tests} testes falharam")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests) * 100,
            "all_passed": successful_tests == total_tests,
            "tests": tests
        }

async def main():
    """Função principal"""
    tester = APITester()
    
    try:
        results = await tester.test_all_endpoints()
        
        # Salva relatório
        with open("api_test_report.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"📝 Relatório salvo em: api_test_report.json")
        
        return results['all_passed']
        
    except Exception as e:
        logger.error(f"💥 Erro crítico: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n🛑 Teste interrompido pelo usuário")
        exit(1) 