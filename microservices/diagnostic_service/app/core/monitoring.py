"""
Sistema de Monitoramento e Métricas com Prometheus
"""
import time
import psutil
import uuid
import random
import asyncio
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI, Request, Response
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TechZeMetrics:
    """Métricas customizadas do TechZe"""
    
    def __init__(self):
        # Contadores
        self.diagnostic_requests_total = Counter(
            'techze_diagnostic_requests_total',
            'Total de requisições de diagnóstico',
            ['type', 'status', 'user_id']
        )
        
        self.authentication_attempts_total = Counter(
            'techze_auth_attempts_total',
            'Total de tentativas de autenticação',
            ['status', 'method']
        )
        
        self.rate_limit_exceeded_total = Counter(
            'techze_rate_limit_exceeded_total',
            'Total de rate limits excedidos',
            ['endpoint', 'user_type']
        )
        
        self.errors_total = Counter(
            'techze_errors_total',
            'Total de erros',
            ['error_type', 'endpoint', 'severity']
        )
        
        # Histogramas (para latência)
        self.diagnostic_duration_seconds = Histogram(
            'techze_diagnostic_duration_seconds',
            'Duração dos diagnósticos em segundos',
            ['type', 'status'],
            buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
        )
        
        self.request_duration_seconds = Histogram(
            'techze_request_duration_seconds',
            'Duração das requisições HTTP em segundos',
            ['method', 'endpoint', 'status_code'],
            buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )
        
        # Gauges (valores atuais)
        self.active_diagnostics = Gauge(
            'techze_active_diagnostics',
            'Número de diagnósticos ativos'
        )
        
        self.connected_users = Gauge(
            'techze_connected_users',
            'Número de usuários conectados'
        )
        
        self.system_cpu_usage = Gauge(
            'techze_system_cpu_usage_percent',
            'Uso de CPU do sistema'
        )
        
        self.system_memory_usage = Gauge(
            'techze_system_memory_usage_percent',
            'Uso de memória do sistema'
        )
        
        self.system_disk_usage = Gauge(
            'techze_system_disk_usage_percent',
            'Uso de disco do sistema'
        )
        
        self.database_connections = Gauge(
            'techze_database_connections',
            'Número de conexões ativas com o banco'
        )
        
        # Info (informações estáticas)
        self.app_info = Info(
            'techze_app_info',
            'Informações da aplicação'
        )
        
        # Inicializa informações da aplicação
        self.app_info.info({
            'version': '1.0.0',
            'environment': 'production',
            'service': 'diagnostic-service'
        })
    
    def record_diagnostic_request(self, diagnostic_type: str, status: str, user_id: str = "anonymous"):
        """Registra uma requisição de diagnóstico"""
        self.diagnostic_requests_total.labels(
            type=diagnostic_type,
            status=status,
            user_id=user_id
        ).inc()
    
    def record_diagnostic_duration(self, diagnostic_type: str, status: str, duration_seconds: float):
        """Registra a duração de um diagnóstico"""
        self.diagnostic_duration_seconds.labels(
            type=diagnostic_type,
            status=status
        ).observe(duration_seconds)
    
    def record_authentication_attempt(self, status: str, method: str = "jwt"):
        """Registra tentativa de autenticação"""
        self.authentication_attempts_total.labels(
            status=status,
            method=method
        ).inc()
    
    def record_rate_limit_exceeded(self, endpoint: str, user_type: str = "anonymous"):
        """Registra rate limit excedido"""
        self.rate_limit_exceeded_total.labels(
            endpoint=endpoint,
            user_type=user_type
        ).inc()
    
    def record_error(self, error_type: str, endpoint: str, severity: str = "medium"):
        """Registra um erro"""
        self.errors_total.labels(
            error_type=error_type,
            endpoint=endpoint,
            severity=severity
        ).inc()
    
    def set_active_diagnostics(self, count: int):
        """Define número de diagnósticos ativos"""
        self.active_diagnostics.set(count)
    
    def set_connected_users(self, count: int):
        """Define número de usuários conectados"""
        self.connected_users.set(count)
    
    def update_system_metrics(self):
        """Atualiza métricas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self.system_cpu_usage.set(cpu_percent)
            
            # Memória
            memory = psutil.virtual_memory()
            self.system_memory_usage.set(memory.percent)
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            self.system_disk_usage.set(disk_percent)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar métricas do sistema: {e}")


class HealthChecker:
    """Verificador de saúde avançado"""
    
    def __init__(self):
        self.checks = {}
        self.last_check_time = {}
    
    def register_check(self, name: str, check_func, interval_seconds: int = 60):
        """Registra uma verificação de saúde"""
        self.checks[name] = {
            'func': check_func,
            'interval': interval_seconds,
            'last_result': None,
            'last_error': None
        }
    
    async def run_check(self, name: str) -> Dict[str, Any]:
        """Executa uma verificação específica"""
        if name not in self.checks:
            return {"status": "error", "message": f"Check '{name}' not found"}
        
        check = self.checks[name]
        current_time = time.time()
        
        # Verifica se precisa executar novamente
        last_check = self.last_check_time.get(name, 0)
        if current_time - last_check < check['interval']:
            return check['last_result'] or {"status": "pending"}
        
        try:
            result = await check['func']()
            check['last_result'] = result
            check['last_error'] = None
            self.last_check_time[name] = current_time
            return result
        except Exception as e:
            error_result = {
                "status": "error",
                "message": str(e),
                "timestamp": current_time
            }
            check['last_result'] = error_result
            check['last_error'] = str(e)
            self.last_check_time[name] = current_time
            return error_result
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Executa todas as verificações"""
        results = {}
        overall_status = "healthy"
        
        for name in self.checks:
            result = await self.run_check(name)
            results[name] = result
            
            if result.get("status") == "error":
                overall_status = "unhealthy"
            elif result.get("status") == "warning" and overall_status == "healthy":
                overall_status = "degraded"
        
        return {
            "overall_status": overall_status,
            "timestamp": time.time(),
            "checks": results
        }


# Verificações de saúde específicas
async def check_database_health() -> Dict[str, Any]:
    """Verifica saúde do banco de dados com testes reais e detalhados"""
    try:
        start_time = time.time()
        from app.core.supabase import get_supabase_client
        
        supabase_client = get_supabase_client()
        connection_errors = []
        query_results = {}
        performance_metrics = {}
        
        # Lista de tabelas para verificar
        tables_to_check = ["device_types", "devices", "diagnostics", "users", "audit_logs"]
        
        # 1. TESTE DE CONECTIVIDADE BÁSICA
        try:
            # Testa uma query simples para verificar conectividade
            connectivity_start = time.time()
            basic_query = supabase_client.table("device_types").select("count", count="exact").limit(1).execute()
            connectivity_time = (time.time() - connectivity_start) * 1000
            
            if hasattr(basic_query, 'error') and basic_query.error:
                connection_errors.append(f"Teste de conectividade falhou: {basic_query.error}")
                query_results["connectivity"] = {"status": "error", "error": str(basic_query.error)}
            else:
                query_results["connectivity"] = {
                    "status": "success", 
                    "response_time_ms": round(connectivity_time, 2)
                }
                performance_metrics["connectivity_ms"] = round(connectivity_time, 2)
        except Exception as e:
            connection_errors.append(f"Exceção no teste de conectividade: {str(e)}")
            query_results["connectivity"] = {"status": "error", "error": str(e)}

        # 2. VERIFICAÇÃO DETALHADA DE TABELAS
        for table in tables_to_check:
            try:
                table_start = time.time()
                
                # Verifica se a tabela existe e obtém contagem
                result = supabase_client.table(table).select("id").limit(1).execute()
                count_result = supabase_client.table(table).select("count", count="exact").execute()
                
                table_time = (time.time() - table_start) * 1000
                
                if hasattr(result, 'error') and result.error:
                    connection_errors.append(f"Erro ao consultar tabela {table}: {result.error}")
                    query_results[table] = {"status": "error", "error": str(result.error)}
                else:
                    count = count_result.count if hasattr(count_result, 'count') else 0
                    query_results[table] = {
                        "status": "success", 
                        "count": count,
                        "response_time_ms": round(table_time, 2)
                    }
                    performance_metrics[f"{table}_query_ms"] = round(table_time, 2)
            except Exception as e:
                connection_errors.append(f"Exceção ao consultar tabela {table}: {str(e)}")
                query_results[table] = {"status": "error", "error": str(e)}

        # 3. TESTE DE OPERAÇÕES CRUD REAIS
        try:
            crud_start = time.time()
            test_id = str(uuid.uuid4())
            
            # Teste de criação na tabela de auditoria (mais seguro)
            create_data = {
                "id": test_id,
                "timestamp": datetime.now().isoformat(),
                "event_type": "system.health_check",
                "severity": "low",
                "action": "health_check_test",
                "details": {"test": True, "timestamp": time.time()},
                "success": True
            }
            
            # CREATE
            create_result = supabase_client.table("audit_logs").insert(create_data).execute()
            create_success = not (hasattr(create_result, 'error') and create_result.error)
            
            # READ
            read_result = supabase_client.table("audit_logs").select("*").eq("id", test_id).execute()
            read_success = not (hasattr(read_result, 'error') and read_result.error) and len(read_result.data) > 0
            
            # UPDATE
            update_result = supabase_client.table("audit_logs").update({"details": {"test": True, "updated": True}}).eq("id", test_id).execute()
            update_success = not (hasattr(update_result, 'error') and update_result.error)
            
            # DELETE
            delete_result = supabase_client.table("audit_logs").delete().eq("id", test_id).execute()
            delete_success = not (hasattr(delete_result, 'error') and delete_result.error)
            
            crud_time = (time.time() - crud_start) * 1000
            
            query_results["crud_operations"] = {
                "status": "success" if all([create_success, read_success, update_success, delete_success]) else "warning",
                "operations": {
                    "create": "success" if create_success else "failed",
                    "read": "success" if read_success else "failed", 
                    "update": "success" if update_success else "failed",
                    "delete": "success" if delete_success else "failed"
                },
                "total_time_ms": round(crud_time, 2)
            }
            performance_metrics["crud_operations_ms"] = round(crud_time, 2)
            
        except Exception as e:
            connection_errors.append(f"Erro no teste CRUD: {str(e)}")
            query_results["crud_operations"] = {"status": "error", "error": str(e)}

        # 4. ESTATÍSTICAS AVANÇADAS DO POSTGRESQL
        try:
            pg_stat_query = """
            SELECT 
                current_database() as db_name,
                pg_size_pretty(pg_database_size(current_database())) as db_size,
                (SELECT count(*) FROM pg_stat_activity) as active_connections,
                (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_queries,
                (SELECT count(*) FROM pg_stat_activity WHERE state = 'idle') as idle_connections,
                (SELECT extract(epoch from now() - pg_postmaster_start_time())) as uptime_seconds,
                (SELECT COALESCE(round(sum(heap_blks_hit) * 100.0 / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0), 2), 0) 
                 FROM pg_statio_user_tables) as cache_hit_ratio,
                (SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public') as table_count
            """
            
            pg_stats_start = time.time()
            pg_stats_result = supabase_client.rpc("execute_sql", {"query": pg_stat_query}).execute()
            pg_stats_time = (time.time() - pg_stats_start) * 1000
            
            if hasattr(pg_stats_result, 'error') and pg_stats_result.error:
                connection_errors.append(f"Erro ao consultar estatísticas do PostgreSQL: {pg_stats_result.error}")
                query_results["pg_stats"] = {"status": "error", "error": str(pg_stats_result.error)}
            else:
                pg_stats = pg_stats_result.data[0] if pg_stats_result.data else {}
                query_results["pg_stats"] = {
                    "status": "success", 
                    "data": pg_stats,
                    "query_time_ms": round(pg_stats_time, 2)
                }
                performance_metrics["pg_stats_query_ms"] = round(pg_stats_time, 2)
                
        except Exception as e:
            connection_errors.append(f"Exceção ao consultar estatísticas do PostgreSQL: {str(e)}")
            query_results["pg_stats"] = {"status": "error", "error": str(e)}

        # 5. TESTE DE AUTENTICAÇÃO E RLS
        try:
            auth_start = time.time()
            
            # Testa funções de autenticação do Supabase
            auth_tests = []
            
            # Teste 1: Função auth.uid()
            try:
                uid_result = supabase_client.rpc("execute_sql", {"query": "SELECT auth.uid() as user_id"}).execute()
                uid_success = not (hasattr(uid_result, 'error') and uid_result.error)
                auth_tests.append({"test": "auth.uid()", "success": uid_success})
            except:
                auth_tests.append({"test": "auth.uid()", "success": False})
            
            # Teste 2: Função auth.jwt()
            try:
                jwt_result = supabase_client.rpc("execute_sql", {"query": "SELECT auth.jwt() as jwt_data"}).execute()
                jwt_success = not (hasattr(jwt_result, 'error') and jwt_result.error)
                auth_tests.append({"test": "auth.jwt()", "success": jwt_success})
            except:
                auth_tests.append({"test": "auth.jwt()", "success": False})
            
            # Teste 3: RLS policies (verifica se estão ativas)
            try:
                rls_query = """
                SELECT schemaname, tablename, rowsecurity 
                FROM pg_tables 
                WHERE schemaname = 'public' AND rowsecurity = true
                """
                rls_result = supabase_client.rpc("execute_sql", {"query": rls_query}).execute()
                rls_success = not (hasattr(rls_result, 'error') and rls_result.error)
                rls_tables = len(rls_result.data) if rls_success and rls_result.data else 0
                auth_tests.append({"test": "rls_policies", "success": rls_success, "rls_tables": rls_tables})
            except:
                auth_tests.append({"test": "rls_policies", "success": False})
            
            auth_time = (time.time() - auth_start) * 1000
            
            query_results["auth_system"] = {
                "status": "success" if all(test["success"] for test in auth_tests) else "warning",
                "tests": auth_tests,
                "total_time_ms": round(auth_time, 2)
            }
            performance_metrics["auth_tests_ms"] = round(auth_time, 2)
            
        except Exception as e:
            connection_errors.append(f"Exceção ao verificar sistema de autenticação: {str(e)}")
            query_results["auth_system"] = {"status": "error", "error": str(e)}

        elapsed_time = int((time.time() - start_time) * 1000)  # ms
        
        # 6. ANÁLISE DE STATUS E PERFORMANCE
        status = "healthy"
        message = "Database connection and operations OK"
        warnings = []
        
        # Verifica erros críticos
        if connection_errors:
            critical_errors = len([e for e in connection_errors if "connectivity" in e or "Exception" in e])
            if critical_errors > 0:
                status = "error"
                message = "Database connection failed: critical errors detected"
            elif len(connection_errors) >= len(tables_to_check) // 2:
                status = "warning" 
                message = "Database connection partially degraded"
            else:
                warnings.append(f"{len(connection_errors)} non-critical errors detected")
        
        # Verifica performance
        if query_results.get("pg_stats", {}).get("status") == "success":
            pg_data = query_results["pg_stats"]["data"]
            if pg_data:
                # Cache hit ratio
                cache_hit_ratio = pg_data.get("cache_hit_ratio", 0)
                if float(cache_hit_ratio) < 80:
                    warnings.append(f"Low cache hit ratio: {cache_hit_ratio}%")
                    if status == "healthy":
                        status = "warning"
                
                # Conexões ativas
                active_connections = pg_data.get("active_connections", 0)
                if int(active_connections) > 50:
                    warnings.append(f"High connection count: {active_connections}")
                    if status == "healthy":
                        status = "warning"
        
        # Verifica tempos de resposta
        slow_operations = []
        for metric, time_ms in performance_metrics.items():
            if time_ms > 1000:  # > 1 segundo
                slow_operations.append(f"{metric}: {time_ms}ms")
        
        if slow_operations:
            warnings.append(f"Slow operations detected: {', '.join(slow_operations)}")
            if status == "healthy":
                status = "warning"
        
        # Ajusta mensagem final
        if warnings and status == "warning":
            message = f"Database functional with {len(warnings)} warnings"
        
        return {
            "status": status,
            "message": message,
            "response_time_ms": elapsed_time,
            "warnings": warnings if warnings else None,
            "performance_metrics": performance_metrics,
            "details": {
                "connection_type": "supabase",
                "query_results": query_results,
                "errors": connection_errors if connection_errors else None,
                "tables_checked": len(tables_to_check),
                "tables_ok": sum(1 for t in query_results.values() if t.get("status") == "success"),
                "operations_tested": len([k for k in query_results.keys() if k in ["connectivity", "crud_operations", "auth_system"]])
            }
        }
    except Exception as e:
        logger.error(f"Erro crítico ao verificar saúde do banco de dados: {e}")
        return {
            "status": "error",
            "message": f"Database health check failed: {str(e)}",
            "response_time_ms": int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
        }


async def check_redis_health() -> Dict[str, Any]:
    """Verifica saúde do Redis com testes completos de performance e integridade"""
    try:
        start_time = time.time()
        from app.core.cache_manager import cache_manager
        
        # Obtém estatísticas do cache para verificar o Redis
        cache_stats = await cache_manager.get_cache_stats()
        redis_available = cache_stats.get("cache_backend", {}).get("redis_available", False)
        
        if not redis_available:
            return {
                "status": "warning",
                "message": "Redis not available, using memory fallback",
                "response_time_ms": int((time.time() - start_time) * 1000),
                "details": {
                    "redis_available": False,
                    "fallback_active": True,
                    "memory_stats": cache_stats.get("cache_backend", {}).get("memory_fallback", {})
                }
            }
        
        # Informações sobre o Redis
        redis_info = cache_stats.get("cache_backend", {}).get("redis", {})
        
        # Métricas de performance
        performance_metrics = {}
        redis_operations = {}
        warnings = []
        
        # 1. TESTE DE CONECTIVIDADE BÁSICA
        try:
            connectivity_start = time.time()
            
            # Testa ping simples
            basic_test = await cache_manager.get("api_responses", "health_check_ping")
            connectivity_time = (time.time() - connectivity_start) * 1000
            
            redis_operations["connectivity"] = {"status": "success", "response_time_ms": round(connectivity_time, 2)}
            performance_metrics["connectivity_ms"] = round(connectivity_time, 2)
            
        except Exception as e:
            redis_operations["connectivity"] = {"status": "error", "message": str(e)}

        # 2. TESTES CRUD COMPLETOS COM DIFERENTES TIPOS DE DADOS
        test_scenarios = [
            {
                "name": "simple_string",
                "key": f"health_test_string_{uuid.uuid4()}",
                "value": "test_string_value",
                "ttl": 60
            },
            {
                "name": "complex_object",
                "key": f"health_test_object_{uuid.uuid4()}",
                "value": {
                    "timestamp": time.time(),
                    "status": "testing",
                    "random": random.randint(1, 1000),
                    "nested": {
                        "field1": "test value",
                        "field2": 12345,
                        "array": [1, 2, 3, 4, 5],
                        "float_val": 3.14159,
                        "bool_val": True
                    },
                    "list": ["item1", "item2", "item3"]
                },
                "ttl": 120
            },
            {
                "name": "large_data",
                "key": f"health_test_large_{uuid.uuid4()}",
                "value": {"data": "x" * 10000},  # 10KB de dados
                "ttl": 30
            }
        ]
        
        for scenario in test_scenarios:
            scenario_ops = {}
            scenario_start = time.time()
            
            try:
                # CREATE/SET
                set_start = time.time()
                await cache_manager.set("api_responses", scenario["key"], scenario["value"], ttl_override=scenario["ttl"])
                set_time = (time.time() - set_start) * 1000
                scenario_ops["create"] = {"status": "success", "time_ms": round(set_time, 2)}
                
                # READ/GET
                get_start = time.time()
                retrieved_value = await cache_manager.get("api_responses", scenario["key"])
                get_time = (time.time() - get_start) * 1000
                
                if retrieved_value is not None:
                    # Verifica integridade dos dados
                    if scenario["name"] == "simple_string":
                        data_integrity = retrieved_value == scenario["value"]
                    elif scenario["name"] == "complex_object":
                        data_integrity = (
                            isinstance(retrieved_value, dict) and
                            retrieved_value.get("status") == "testing" and
                            retrieved_value.get("nested", {}).get("field1") == "test value" and
                            len(retrieved_value.get("list", [])) == 3
                        )
                    else:  # large_data
                        data_integrity = (
                            isinstance(retrieved_value, dict) and
                            len(retrieved_value.get("data", "")) == 10000
                        )
                    
                    scenario_ops["read"] = {
                        "status": "success", 
                        "time_ms": round(get_time, 2),
                        "data_integrity": "ok" if data_integrity else "corrupted"
                    }
                    
                    if not data_integrity:
                        warnings.append(f"Data corruption detected in {scenario['name']} test")
                else:
                    scenario_ops["read"] = {"status": "error", "message": "Data not found"}
                
                # UPDATE
                update_start = time.time()
                if scenario["name"] == "complex_object":
                    updated_value = scenario["value"].copy()
                    updated_value["updated"] = True
                    updated_value["update_timestamp"] = time.time()
                else:
                    updated_value = f"{scenario['value']}_updated"
                
                await cache_manager.set("api_responses", scenario["key"], updated_value, ttl_override=scenario["ttl"])
                update_time = (time.time() - update_start) * 1000
                
                # Verifica se a atualização foi bem-sucedida
                updated_retrieved = await cache_manager.get("api_responses", scenario["key"])
                update_success = updated_retrieved is not None
                
                if scenario["name"] == "complex_object" and update_success:
                    update_success = updated_retrieved.get("updated") == True
                elif scenario["name"] == "simple_string" and update_success:
                    update_success = "_updated" in str(updated_retrieved)
                
                scenario_ops["update"] = {
                    "status": "success" if update_success else "error",
                    "time_ms": round(update_time, 2)
                }
                
                # DELETE
                delete_start = time.time()
                deleted = await cache_manager.delete("api_responses", scenario["key"])
                delete_time = (time.time() - delete_start) * 1000
                
                scenario_ops["delete"] = {
                    "status": "success" if deleted else "error",
                    "time_ms": round(delete_time, 2)
                }
                
                # Verifica se foi realmente deletado
                after_delete = await cache_manager.get("api_responses", scenario["key"])
                scenario_ops["delete_verification"] = {
                    "status": "success" if after_delete is None else "error",
                    "message": "Successfully deleted" if after_delete is None else "Key still exists"
                }
                
            except Exception as e:
                scenario_ops["error"] = {"status": "error", "message": str(e)}
            
            scenario_total_time = (time.time() - scenario_start) * 1000
            scenario_ops["total_time_ms"] = round(scenario_total_time, 2)
            redis_operations[f"crud_{scenario['name']}"] = scenario_ops
            performance_metrics[f"crud_{scenario['name']}_ms"] = round(scenario_total_time, 2)

        # 3. TESTE DE TTL (Time To Live)
        try:
            ttl_start = time.time()
            ttl_test_key = f"ttl_test_{uuid.uuid4()}"
            ttl_test_value = {"timestamp": time.time(), "test": "ttl_verification"}
            
            # Define TTL de 2 segundos
            await cache_manager.set("api_responses", ttl_test_key, ttl_test_value, ttl_override=2)
            
            # Verifica imediatamente
            immediate_check = await cache_manager.get("api_responses", ttl_test_key)
            
            # Aguarda TTL expirar (3 segundos para garantir)
            await asyncio.sleep(3)
            
            # Verifica novamente após expiração
            after_ttl = await cache_manager.get("api_responses", ttl_test_key)
            
            ttl_time = (time.time() - ttl_start) * 1000
            ttl_working = immediate_check is not None and after_ttl is None
            
            redis_operations["ttl_test"] = {
                "status": "success" if ttl_working else "error",
                "message": "TTL working correctly" if ttl_working else "TTL not working properly",
                "immediate_found": immediate_check is not None,
                "after_expiry_found": after_ttl is not None,
                "total_time_ms": round(ttl_time, 2)
            }
            performance_metrics["ttl_test_ms"] = round(ttl_time, 2)
            
        except Exception as e:
            redis_operations["ttl_test"] = {"status": "error", "message": str(e)}

        # 4. TESTE DE STRESS/PERFORMANCE
        try:
            stress_start = time.time()
            stress_operations = 50  # Reduzido para não sobrecarregar
            stress_success = 0
            
            for i in range(stress_operations):
                try:
                    stress_key = f"stress_test_{i}"
                    stress_value = {"operation": i, "data": f"stress_data_{i}"}
                    
                    await cache_manager.set("api_responses", stress_key, stress_value, ttl_override=10)
                    retrieved = await cache_manager.get("api_responses", stress_key)
                    
                    if retrieved and retrieved.get("operation") == i:
                        stress_success += 1
                    
                    # Limpa chave de teste
                    await cache_manager.delete("api_responses", stress_key)
                    
                except:
                    pass
            
            stress_time = (time.time() - stress_start) * 1000
            stress_rate = (stress_success / stress_operations) * 100
            ops_per_second = (stress_operations * 2) / (stress_time / 1000)  # *2 porque são set+get
            
            redis_operations["stress_test"] = {
                "status": "success" if stress_rate >= 95 else "warning" if stress_rate >= 80 else "error",
                "operations_tested": stress_operations,
                "success_rate": round(stress_rate, 2),
                "ops_per_second": round(ops_per_second, 2),
                "total_time_ms": round(stress_time, 2)
            }
            performance_metrics["stress_test_ms"] = round(stress_time, 2)
            performance_metrics["ops_per_second"] = round(ops_per_second, 2)
            
            if stress_rate < 95:
                warnings.append(f"Stress test performance degraded: {stress_rate}% success rate")
                
        except Exception as e:
            redis_operations["stress_test"] = {"status": "error", "message": str(e)}

        # Calcula latência total
        elapsed_time = int((time.time() - start_time) * 1000)  # ms
        
        # 5. ANÁLISE DE MÉTRICAS DO REDIS
        if redis_info:
            # Verifica uso de memória
            memory_usage = redis_info.get("used_memory_human", "N/A")
            if memory_usage and memory_usage.endswith("M"):
                try:
                    memory_mb = float(memory_usage[:-1])
                    if memory_mb > 512:  # Alerta se > 512MB
                        warnings.append(f"High Redis memory usage: {memory_usage}")
                except (ValueError, TypeError):
                    pass
            elif memory_usage and memory_usage.endswith("G"):
                try:
                    memory_gb = float(memory_usage[:-1])
                    if memory_gb > 0.5:  # Alerta se > 0.5GB
                        warnings.append(f"Very high Redis memory usage: {memory_usage}")
                except (ValueError, TypeError):
                    pass
                
            # Verifica hit rate
            hit_rate = redis_info.get("hit_rate_percent", 0)
            if hit_rate < 70:  # Alerta se < 70%
                warnings.append(f"Low Redis hit rate: {hit_rate}%")
                
            # Verifica muitas conexões
            connected_clients = redis_info.get("connected_clients", 0)
            if connected_clients > 20:  # Alerta se > 20 conexões
                warnings.append(f"High Redis connections: {connected_clients}")

        # 6. DETERMINA STATUS FINAL
        operation_statuses = []
        for op_name, op_data in redis_operations.items():
            if isinstance(op_data, dict):
                if "status" in op_data:
                    operation_statuses.append(op_data["status"])
                elif "crud_" in op_name:
                    # Para operações CRUD, verifica suboperações
                    sub_statuses = []
                    for sub_op in ["create", "read", "update", "delete"]:
                        if sub_op in op_data and "status" in op_data[sub_op]:
                            sub_statuses.append(op_data[sub_op]["status"])
                    if sub_statuses:
                        operation_statuses.extend(sub_statuses)

        success_count = sum(1 for status in operation_statuses if status == "success")
        total_count = len(operation_statuses)
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0

        if success_rate >= 95:
            status = "healthy"
            message = "Redis connection and operations optimal"
        elif success_rate >= 80:
            status = "warning" 
            message = f"Redis functional with degraded performance ({success_rate:.1f}% success)"
        else:
            status = "error"
            message = f"Redis operations failing ({success_rate:.1f}% success)"
            
        # Adiciona warnings à mensagem se status for warning
        if warnings and status in ["healthy", "warning"]:
            if status == "healthy" and len(warnings) > 0:
                status = "warning"
            message += f" ({len(warnings)} warnings)"
            
        return {
            "status": status,
            "message": message,
            "response_time_ms": elapsed_time,
            "warnings": warnings if warnings else None,
            "performance_metrics": performance_metrics,
            "success_rate": round(success_rate, 2),
            "details": {
                "redis_available": True,
                "operations_tested": len(redis_operations),
                "operations_successful": success_count,
                "operations_results": redis_operations,
                "redis_info": {
                    "memory_usage": redis_info.get("used_memory_human", "N/A"),
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "hit_rate_percent": redis_info.get("hit_rate_percent", 0),
                    "total_commands_processed": redis_info.get("total_commands_processed", 0),
                    "uptime_seconds": redis_info.get("uptime_in_seconds", 0)
                },
                "application_stats": cache_stats.get("application_stats", {})
            }
        }
         
    except Exception as e:
        logger.error(f"Erro crítico ao verificar saúde do Redis: {e}")
        return {
            "status": "error",
            "message": f"Redis health check failed: {str(e)}",
            "response_time_ms": int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
        }


async def check_system_resources() -> Dict[str, Any]:
    """Verifica recursos do sistema"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = "healthy"
        warnings = []
        
        if cpu_percent > 80:
            status = "warning"
            warnings.append(f"High CPU usage: {cpu_percent}%")
        
        if memory.percent > 85:
            status = "warning"
            warnings.append(f"High memory usage: {memory.percent}%")
        
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > 90:
            status = "warning"
            warnings.append(f"High disk usage: {disk_percent}%")
        
        return {
            "status": status,
            "message": "System resources OK" if not warnings else "; ".join(warnings),
            "details": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk_percent,
                "available_memory_gb": round(memory.available / (1024**3), 2),
                "free_disk_gb": round(disk.free / (1024**3), 2)
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to check system resources: {str(e)}"
        }


# Instâncias globais
techze_metrics = TechZeMetrics()
health_checker = HealthChecker()


def setup_monitoring(app: FastAPI):
    """Configura monitoramento na aplicação"""
    
    # Instrumentação automática do Prometheus
    instrumentator = Instrumentator()
    instrumentator.instrument(app)
    
    # Registra verificações de saúde
    health_checker.register_check("database", check_database_health, 30)
    health_checker.register_check("redis", check_redis_health, 60)
    health_checker.register_check("system", check_system_resources, 30)
    
    # Endpoint de métricas
    @app.get("/metrics")
    async def metrics():
        """Endpoint de métricas do Prometheus"""
        # Atualiza métricas do sistema antes de retornar
        techze_metrics.update_system_metrics()
        return Response(generate_latest(), media_type="text/plain")
    
    # Endpoint de saúde avançado
    @app.get("/health/detailed")
    async def detailed_health():
        """Endpoint de saúde detalhado"""
        return await health_checker.run_all_checks()
    
    # Middleware para métricas de requisições
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        # Registra duração da requisição
        duration = time.time() - start_time
        techze_metrics.request_duration_seconds.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code
        ).observe(duration)
        
        return response
    
    logger.info("Monitoramento configurado com Prometheus")
    return instrumentator


# Decorador para métricas automáticas
def monitor_diagnostic(diagnostic_type: str):
    """Decorador para monitorar diagnósticos automaticamente"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Incrementa diagnósticos ativos
                techze_metrics.active_diagnostics.inc()
                
                # Executa função
                result = await func(*args, **kwargs)
                
                # Registra sucesso
                duration = time.time() - start_time
                techze_metrics.record_diagnostic_request(diagnostic_type, "success")
                techze_metrics.record_diagnostic_duration(diagnostic_type, "success", duration)
                
                return result
                
            except Exception as e:
                # Registra erro
                duration = time.time() - start_time
                techze_metrics.record_diagnostic_request(diagnostic_type, "error")
                techze_metrics.record_diagnostic_duration(diagnostic_type, "error", duration)
                techze_metrics.record_error(type(e).__name__, f"diagnostic_{diagnostic_type}")
                
                raise
            finally:
                # Decrementa diagnósticos ativos
                techze_metrics.active_diagnostics.dec()
        
        return wrapper
    return decorator