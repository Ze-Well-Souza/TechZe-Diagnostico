#!/usr/bin/env python3
"""
Script de Validação das Correções Críticas
TechZe Diagnóstico - Validação de Contratos de API e Segurança

Este script valida:
1. Contratos de API corrigidos
2. Headers de segurança implementados
3. Performance dos endpoints
4. Compatibilidade frontend-backend
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestStatus(Enum):
    PASS = "✅ PASS"
    FAIL = "❌ FAIL"
    WARNING = "⚠️ WARNING"
    SKIP = "⏭️ SKIP"

@dataclass
class TestResult:
    name: str
    status: TestStatus
    message: str
    details: Dict[str, Any] = None
    duration_ms: float = 0

class APIValidator:
    """Validador de APIs e contratos"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results: List[TestResult] = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_server_health(self) -> TestResult:
        """Testar se o servidor está rodando"""
        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                duration = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    return TestResult(
                        name="Server Health Check",
                        status=TestStatus.PASS,
                        message="Servidor está rodando",
                        details={"response": data, "status_code": response.status},
                        duration_ms=duration
                    )
                else:
                    return TestResult(
                        name="Server Health Check",
                        status=TestStatus.FAIL,
                        message=f"Servidor retornou status {response.status}",
                        duration_ms=duration
                    )
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Server Health Check",
                status=TestStatus.FAIL,
                message=f"Erro ao conectar: {str(e)}",
                duration_ms=duration
            )
    
    async def test_security_headers(self) -> TestResult:
        """Testar headers de segurança"""
        start_time = time.time()
        
        required_headers = {
            'x-content-type-options': 'nosniff',
            'x-frame-options': 'DENY',
            'x-xss-protection': '1; mode=block',
            'strict-transport-security': 'max-age=31536000; includeSubDomains',
            'content-security-policy': True,  # Apenas verificar se existe
            'referrer-policy': 'strict-origin-when-cross-origin'
        }
        
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                duration = (time.time() - start_time) * 1000
                headers = {k.lower(): v for k, v in response.headers.items()}
                
                missing_headers = []
                incorrect_headers = []
                
                for header, expected_value in required_headers.items():
                    if header not in headers:
                        missing_headers.append(header)
                    elif expected_value is not True and headers[header] != expected_value:
                        incorrect_headers.append(f"{header}: got '{headers[header]}', expected '{expected_value}'")
                
                if not missing_headers and not incorrect_headers:
                    return TestResult(
                        name="Security Headers",
                        status=TestStatus.PASS,
                        message="Todos os headers de segurança estão corretos",
                        details={"headers": dict(headers)},
                        duration_ms=duration
                    )
                else:
                    issues = []
                    if missing_headers:
                        issues.append(f"Headers faltando: {missing_headers}")
                    if incorrect_headers:
                        issues.append(f"Headers incorretos: {incorrect_headers}")
                    
                    return TestResult(
                        name="Security Headers",
                        status=TestStatus.FAIL,
                        message="Headers de segurança com problemas",
                        details={"issues": issues, "headers": dict(headers)},
                        duration_ms=duration
                    )
                    
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Security Headers",
                status=TestStatus.FAIL,
                message=f"Erro ao testar headers: {str(e)}",
                duration_ms=duration
            )
    
    async def test_orcamento_contract(self) -> TestResult:
        """Testar contrato de API de orçamento"""
        start_time = time.time()
        
        # Payload de teste compatível com frontend TRAE
        test_payload = {
            "cliente_id": 1,
            "descricao": "Orçamento de teste - validação de contrato",
            "criado_por": 1,
            "endereco": {
                "rua": "Rua Teste, 123",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "estado": "SP",
                "cep": "01234-567"
            },
            "itens": [
                {
                    "codigo_peca": "PC001",  # Campo frontend
                    "nome_peca": "Peça Teste",  # Campo frontend
                    "quantidade": 2,
                    "valor_unitario": 50.00
                }
            ],
            "observacoes": "Teste de validação de contrato",
            "validade_dias": 30
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/orcamentos",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                duration = (time.time() - start_time) * 1000
                
                if response.status in [200, 201]:
                    data = await response.json()
                    return TestResult(
                        name="Orçamento Contract",
                        status=TestStatus.PASS,
                        message="Contrato de orçamento funcionando",
                        details={"response": data, "status_code": response.status},
                        duration_ms=duration
                    )
                elif response.status == 422:
                    # Erro de validação - analisar detalhes
                    error_data = await response.json()
                    return TestResult(
                        name="Orçamento Contract",
                        status=TestStatus.FAIL,
                        message="Erro de validação no contrato",
                        details={"validation_errors": error_data, "payload": test_payload},
                        duration_ms=duration
                    )
                else:
                    return TestResult(
                        name="Orçamento Contract",
                        status=TestStatus.FAIL,
                        message=f"Endpoint retornou status {response.status}",
                        duration_ms=duration
                    )
                    
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Orçamento Contract",
                status=TestStatus.FAIL,
                message=f"Erro ao testar contrato: {str(e)}",
                duration_ms=duration
            )
    
    async def test_estoque_contract(self) -> TestResult:
        """Testar contrato de API de estoque"""
        start_time = time.time()
        
        # Payload de teste com mapeamento frontend->backend
        test_payload = {
            "item_id": 1,
            "quantidade": 10,
            "tipo_movimentacao": "entrada",
            "codigo_peca": "EST001",  # Campo frontend
            "nome_peca": "Item Estoque Teste",  # Campo frontend
            "motivo": "Teste de validação de contrato",
            "custo_unitario": 25.50
        }
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/estoque/movimentacao",
                json=test_payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                duration = (time.time() - start_time) * 1000
                
                if response.status in [200, 201]:
                    data = await response.json()
                    return TestResult(
                        name="Estoque Contract",
                        status=TestStatus.PASS,
                        message="Contrato de estoque funcionando",
                        details={"response": data, "status_code": response.status},
                        duration_ms=duration
                    )
                elif response.status == 422:
                    error_data = await response.json()
                    return TestResult(
                        name="Estoque Contract",
                        status=TestStatus.FAIL,
                        message="Erro de validação no contrato",
                        details={"validation_errors": error_data, "payload": test_payload},
                        duration_ms=duration
                    )
                else:
                    return TestResult(
                        name="Estoque Contract",
                        status=TestStatus.FAIL,
                        message=f"Endpoint retornou status {response.status}",
                        duration_ms=duration
                    )
                    
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return TestResult(
                name="Estoque Contract",
                status=TestStatus.FAIL,
                message=f"Erro ao testar contrato: {str(e)}",
                duration_ms=duration
            )
    
    async def test_performance(self) -> TestResult:
        """Testar performance dos endpoints"""
        endpoints = [
            "/health",
            "/api/v1/orcamentos",
            "/api/v1/estoque",
            "/api/v1/ordens-servico"
        ]
        
        performance_results = []
        total_start = time.time()
        
        for endpoint in endpoints:
            start_time = time.time()
            try:
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    duration = (time.time() - start_time) * 1000
                    performance_results.append({
                        "endpoint": endpoint,
                        "duration_ms": duration,
                        "status": response.status,
                        "success": response.status < 500
                    })
            except Exception as e:
                duration = (time.time() - start_time) * 1000
                performance_results.append({
                    "endpoint": endpoint,
                    "duration_ms": duration,
                    "status": "error",
                    "error": str(e),
                    "success": False
                })
        
        total_duration = (time.time() - total_start) * 1000
        avg_duration = sum(r["duration_ms"] for r in performance_results) / len(performance_results)
        
        # Meta: < 500ms por endpoint
        slow_endpoints = [r for r in performance_results if r["duration_ms"] > 500]
        
        if not slow_endpoints:
            return TestResult(
                name="Performance Test",
                status=TestStatus.PASS,
                message=f"Performance OK - média {avg_duration:.1f}ms",
                details={"results": performance_results, "average_ms": avg_duration},
                duration_ms=total_duration
            )
        else:
            return TestResult(
                name="Performance Test",
                status=TestStatus.WARNING,
                message=f"Endpoints lentos detectados - média {avg_duration:.1f}ms",
                details={"slow_endpoints": slow_endpoints, "all_results": performance_results},
                duration_ms=total_duration
            )
    
    async def run_all_tests(self) -> List[TestResult]:
        """Executar todos os testes"""
        tests = [
            self.test_server_health(),
            self.test_security_headers(),
            self.test_orcamento_contract(),
            self.test_estoque_contract(),
            self.test_performance()
        ]
        
        results = []
        for test in tests:
            try:
                result = await test
                results.append(result)
                self.results.append(result)
            except Exception as e:
                error_result = TestResult(
                    name="Unknown Test",
                    status=TestStatus.FAIL,
                    message=f"Erro inesperado: {str(e)}"
                )
                results.append(error_result)
                self.results.append(error_result)
        
        return results

def print_results(results: List[TestResult]):
    """Imprimir resultados dos testes"""
    print("\n" + "="*80)
    print("🔍 RELATÓRIO DE VALIDAÇÃO - TECHZE DIAGNÓSTICO")
    print("="*80)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🧪 Total de Testes: {len(results)}")
    
    # Contar resultados
    pass_count = sum(1 for r in results if r.status == TestStatus.PASS)
    fail_count = sum(1 for r in results if r.status == TestStatus.FAIL)
    warning_count = sum(1 for r in results if r.status == TestStatus.WARNING)
    
    print(f"✅ Sucessos: {pass_count}")
    print(f"❌ Falhas: {fail_count}")
    print(f"⚠️ Avisos: {warning_count}")
    
    # Score de qualidade
    quality_score = (pass_count / len(results)) * 100
    print(f"📊 Score de Qualidade: {quality_score:.1f}%")
    
    print("\n" + "-"*80)
    print("📋 DETALHES DOS TESTES")
    print("-"*80)
    
    for result in results:
        print(f"\n{result.status.value} {result.name}")
        print(f"   💬 {result.message}")
        if result.duration_ms > 0:
            print(f"   ⏱️ Duração: {result.duration_ms:.1f}ms")
        
        if result.details:
            print(f"   📄 Detalhes:")
            for key, value in result.details.items():
                if isinstance(value, (dict, list)):
                    print(f"      {key}: {json.dumps(value, indent=6, ensure_ascii=False)[:200]}...")
                else:
                    print(f"      {key}: {value}")
    
    print("\n" + "="*80)
    
    # Recomendações
    if fail_count > 0:
        print("🚨 AÇÕES RECOMENDADAS:")
        print("   1. Verificar se o servidor está rodando")
        print("   2. Verificar logs de erro do backend")
        print("   3. Validar configurações de middleware")
        print("   4. Testar endpoints manualmente")
    elif warning_count > 0:
        print("⚠️ MELHORIAS SUGERIDAS:")
        print("   1. Otimizar performance dos endpoints lentos")
        print("   2. Revisar configurações de cache")
        print("   3. Monitorar uso de recursos")
    else:
        print("🎉 PARABÉNS! Todos os testes passaram com sucesso!")
        print("   ✨ Sistema pronto para produção")
    
    print("="*80)

async def main():
    """Função principal"""
    print("🚀 Iniciando validação das correções críticas...")
    
    async with APIValidator() as validator:
        results = await validator.run_all_tests()
        print_results(results)
        
        # Retornar código de saída baseado nos resultados
        fail_count = sum(1 for r in results if r.status == TestStatus.FAIL)
        return 0 if fail_count == 0 else 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)