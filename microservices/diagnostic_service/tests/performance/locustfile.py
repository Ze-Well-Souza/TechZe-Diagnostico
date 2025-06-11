"""
Testes de Carga - TechZe Diagnóstico Backend
Validação de performance conforme TASK_MASTER.md - Semana 5-6

Meta: Validar se sistema suporta 100 usuários concorrentes
Performance esperada: < 500ms response time
"""

from locust import HttpUser, task, between
import json
import random
from datetime import datetime, date
import uuid


class TechZeUser(HttpUser):
    """Usuário simulado para testes de carga"""
    wait_time = between(1, 3)  # Espera entre 1-3 segundos entre requests
    
    def on_start(self):
        """Setup inicial do usuário"""
        self.base_url = "http://localhost:8000"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    @task(3)
    def health_check(self):
        """Teste básico de health check - 30% das requisições"""
        with self.client.get("/health", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")
    
    @task(2)
    def listar_orcamentos(self):
        """Listar orçamentos - 20% das requisições"""
        with self.client.get("/api/v1/orcamentos/", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 500:
                response.failure("Endpoint com erro 500 - problema crítico identificado")
            else:
                response.failure(f"Erro inesperado: {response.status_code}")
    
    @task(2)
    def listar_estoque(self):
        """Listar itens de estoque - 20% das requisições"""
        with self.client.get("/api/v1/estoque/itens", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 500:
                response.failure("Endpoint com erro 500 - problema crítico identificado")
            else:
                response.failure(f"Erro inesperado: {response.status_code}")
    
    @task(2)
    def listar_ordens_servico(self):
        """Listar ordens de serviço - 20% das requisições"""
        with self.client.get("/api/v1/ordens-servico/", headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 500:
                response.failure("Endpoint com erro 500 - problema crítico identificado")
            else:
                response.failure(f"Erro inesperado: {response.status_code}")
    
    @task(1)
    def criar_orcamento(self):
        """Criar novo orçamento - 10% das requisições"""
        payload = {
            "cliente": {
                "nome": f"Cliente Teste {random.randint(1, 1000)}",
                "telefone": f"11999{random.randint(100000, 999999)}",
                "email": f"cliente{random.randint(1, 1000)}@teste.com"
            },
            "equipamento": {
                "tipo": "notebook",
                "marca": "Dell",
                "modelo": "Inspiron 15",
                "problema_relatado": "Não liga"
            },
            "servicos": [
                {
                    "descricao": "Diagnóstico completo",
                    "tipo": "diagnostico",
                    "valor_unitario": 50.00
                }
            ],
            "observacoes": "Teste de carga automatizado"
        }
        
        with self.client.post("/api/v1/orcamentos/", 
                             json=payload, 
                             headers=self.headers, 
                             catch_response=True) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 422:
                response.failure("Erro de validação - incompatibilidade de payload identificada")
            elif response.status_code == 500:
                response.failure("Erro interno do servidor")
            else:
                response.failure(f"Erro inesperado: {response.status_code}")


class TechZeStressUser(HttpUser):
    """Usuário para teste de stress intensivo"""
    wait_time = between(0.5, 1)  # Menos tempo de espera para stress
    
    def on_start(self):
        self.base_url = "http://localhost:8000"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    @task
    def stress_test_endpoints(self):
        """Teste de stress nos endpoints críticos"""
        endpoints = [
            "/api/v1/orcamentos/",
            "/api/v1/estoque/itens",
            "/api/v1/ordens-servico/",
            "/health"
        ]
        
        endpoint = random.choice(endpoints)
        start_time = datetime.now()
        
        with self.client.get(endpoint, headers=self.headers, catch_response=True) as response:
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000  # em ms
            
            if response_time > 500:  # Meta: < 500ms
                response.failure(f"Response time muito alto: {response_time:.0f}ms > 500ms")
            elif response.status_code == 500:
                response.failure("Endpoint com erro 500")
            elif response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")


# Configurações de teste para diferentes cenários
class QuickLoadTest(TechZeUser):
    """Teste rápido - 10 usuários por 2 minutos"""
    weight = 1

class IntenseLoadTest(TechZeStressUser):
    """Teste intensivo - stress testing"""
    weight = 2 