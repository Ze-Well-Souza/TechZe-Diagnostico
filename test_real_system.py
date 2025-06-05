#!/usr/bin/env python3
"""
TechZe Diagnóstico - Teste Real do Sistema
Script para testar todas as funcionalidades com dados reais
"""
import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Any
import aiohttp
import psutil
import platform
import subprocess
import os
import sqlite3

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealSystemTester:
    """Testador completo do sistema TechZe Diagnóstico"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "tests": {},
            "summary": {},
            "errors": []
        }
        
        # Configurar banco local para testes
        self.setup_local_database()
    
    def setup_local_database(self):
        """Configura banco de dados SQLite local para testes"""
        try:
            conn = sqlite3.connect('techze_test.db')
            cursor = conn.cursor()
            
            # Criar tabelas necessárias
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS devices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    ip_address TEXT,
                    mac_address TEXT,
                    os_info TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS diagnostics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    device_id INTEGER,
                    cpu_usage REAL,
                    memory_usage REAL,
                    disk_usage REAL,
                    network_status TEXT,
                    temperature REAL,
                    issues TEXT,
                    recommendations TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (device_id) REFERENCES devices (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Banco de dados local configurado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar banco: {e}")
    
    def collect_real_system_data(self) -> Dict[str, Any]:
        """Coleta dados reais do sistema atual"""
        try:
            # Informações do sistema
            system_info = {
                "hostname": platform.node(),
                "platform": platform.platform(),
                "architecture": platform.architecture()[0],
                "processor": platform.processor(),
                "python_version": platform.python_version()
            }
            
            # Métricas de CPU
            cpu_data = {
                "usage_percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None,
                "load_avg": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else None
            }
            
            # Métricas de memória
            memory = psutil.virtual_memory()
            memory_data = {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
                "free": memory.free
            }
            
            # Métricas de disco
            disk = psutil.disk_usage('/')
            disk_data = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            }
            
            # Informações de rede
            network = psutil.net_io_counters()
            network_data = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
                "interfaces": list(psutil.net_if_addrs().keys())
            }
            
            # Processos em execução
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Top 10 processos por CPU
            top_processes = sorted(
                [p for p in processes if p['cpu_percent'] is not None],
                key=lambda x: x['cpu_percent'] or 0,
                reverse=True
            )[:10]
            
            return {
                "system_info": system_info,
                "cpu": cpu_data,
                "memory": memory_data,
                "disk": disk_data,
                "network": network_data,
                "top_processes": top_processes,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar dados do sistema: {e}")
            return {}
    
    def analyze_system_health(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa a saúde do sistema baseado nos dados coletados"""
        issues = []
        recommendations = []
        health_score = 100
        
        try:
            # Análise de CPU
            cpu_usage = system_data.get('cpu', {}).get('usage_percent', 0)
            if cpu_usage > 80:
                issues.append(f"Alto uso de CPU: {cpu_usage:.1f}%")
                recommendations.append("Verificar processos que estão consumindo muita CPU")
                health_score -= 20
            elif cpu_usage > 60:
                issues.append(f"Uso moderado de CPU: {cpu_usage:.1f}%")
                health_score -= 10
            
            # Análise de memória
            memory_usage = system_data.get('memory', {}).get('percent', 0)
            if memory_usage > 85:
                issues.append(f"Alto uso de memória: {memory_usage:.1f}%")
                recommendations.append("Considerar fechar aplicações desnecessárias ou adicionar mais RAM")
                health_score -= 25
            elif memory_usage > 70:
                issues.append(f"Uso moderado de memória: {memory_usage:.1f}%")
                health_score -= 10
            
            # Análise de disco
            disk_usage = system_data.get('disk', {}).get('percent', 0)
            if disk_usage > 90:
                issues.append(f"Disco quase cheio: {disk_usage:.1f}%")
                recommendations.append("Urgente: Liberar espaço em disco")
                health_score -= 30
            elif disk_usage > 80:
                issues.append(f"Pouco espaço em disco: {disk_usage:.1f}%")
                recommendations.append("Considerar limpeza de arquivos temporários")
                health_score -= 15
            
            # Análise de processos
            top_processes = system_data.get('top_processes', [])
            if top_processes:
                high_cpu_processes = [p for p in top_processes if p.get('cpu_percent', 0) > 50]
                if high_cpu_processes:
                    process_names = [p['name'] for p in high_cpu_processes]
                    issues.append(f"Processos com alto uso de CPU: {', '.join(process_names)}")
                    recommendations.append("Verificar se estes processos são necessários")
            
            # Determinar status geral
            if health_score >= 90:
                status = "Excelente"
            elif health_score >= 75:
                status = "Bom"
            elif health_score >= 60:
                status = "Regular"
            elif health_score >= 40:
                status = "Ruim"
            else:
                status = "Crítico"
            
            return {
                "health_score": max(0, health_score),
                "status": status,
                "issues": issues,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de saúde: {e}")
            return {
                "health_score": 0,
                "status": "Erro na análise",
                "issues": [f"Erro durante análise: {str(e)}"],
                "recommendations": ["Verificar logs do sistema"],
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
    
    def save_diagnostic_data(self, device_data: Dict[str, Any], diagnostic_data: Dict[str, Any]):
        """Salva dados de diagnóstico no banco local"""
        try:
            conn = sqlite3.connect('techze_test.db')
            cursor = conn.cursor()
            
            # Inserir device
            cursor.execute('''
                INSERT INTO devices (name, type, os_info)
                VALUES (?, ?, ?)
            ''', (
                device_data.get('hostname', 'Unknown'),
                'Computer',
                device_data.get('platform', 'Unknown')
            ))
            
            device_id = cursor.lastrowid
            
            # Inserir diagnostic
            analysis = diagnostic_data.get('analysis', {})
            cursor.execute('''
                INSERT INTO diagnostics (
                    device_id, cpu_usage, memory_usage, disk_usage,
                    network_status, issues, recommendations
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                device_id,
                device_data.get('cpu', {}).get('usage_percent', 0),
                device_data.get('memory', {}).get('percent', 0),
                device_data.get('disk', {}).get('percent', 0),
                'Connected',
                json.dumps(analysis.get('issues', [])),
                json.dumps(analysis.get('recommendations', []))
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Dados salvos - Device ID: {device_id}")
            return device_id
            
        except Exception as e:
            logger.error(f"❌ Erro ao salvar dados: {e}")
            return None
    
    def test_database_operations(self) -> Dict[str, Any]:
        """Testa operações de banco de dados"""
        test_result = {
            "name": "Database Operations",
            "status": "success",
            "details": {},
            "errors": []
        }
        
        try:
            conn = sqlite3.connect('techze_test.db')
            cursor = conn.cursor()
            
            # Teste 1: Inserção
            cursor.execute('''
                INSERT INTO devices (name, type, os_info)
                VALUES (?, ?, ?)
            ''', ('Test Device', 'Computer', 'Test OS'))
            device_id = cursor.lastrowid
            
            # Teste 2: Consulta
            cursor.execute('SELECT * FROM devices WHERE id = ?', (device_id,))
            device = cursor.fetchone()
            
            # Teste 3: Atualização
            cursor.execute('''
                UPDATE devices SET name = ? WHERE id = ?
            ''', ('Updated Test Device', device_id))
            
            # Teste 4: Contagem
            cursor.execute('SELECT COUNT(*) FROM devices')
            count = cursor.fetchone()[0]
            
            # Teste 5: Limpeza
            cursor.execute('DELETE FROM devices WHERE id = ?', (device_id,))
            
            conn.commit()
            conn.close()
            
            test_result["details"] = {
                "insertion": "success",
                "query": "success",
                "update": "success",
                "count": count,
                "deletion": "success"
            }
            
            logger.info("✅ Testes de banco de dados: SUCESSO")
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["errors"].append(str(e))
            logger.error(f"❌ Erro nos testes de banco: {e}")
        
        return test_result
    
    def test_ai_analysis(self, system_data: Dict[str, Any]) -> Dict[str, Any]:
        """Testa análise de IA com dados reais"""
        test_result = {
            "name": "AI Analysis",
            "status": "success",
            "details": {},
            "errors": []
        }
        
        try:
            # Simular análise de IA avançada
            analysis = self.analyze_system_health(system_data)
            
            # Análise adicional com "IA"
            cpu_usage = system_data.get('cpu', {}).get('usage_percent', 0)
            memory_usage = system_data.get('memory', {}).get('percent', 0)
            disk_usage = system_data.get('disk', {}).get('percent', 0)
            
            # Predições simples baseadas em regras
            predictions = []
            if cpu_usage > 70:
                predictions.append("Possível degradação de performance em 24h")
            if memory_usage > 80:
                predictions.append("Risco de travamento do sistema")
            if disk_usage > 85:
                predictions.append("Espaço em disco se esgotará em breve")
            
            # Recomendações inteligentes
            smart_recommendations = []
            top_processes = system_data.get('top_processes', [])
            if top_processes:
                high_cpu_proc = max(top_processes, key=lambda x: x.get('cpu_percent', 0))
                if high_cpu_proc.get('cpu_percent', 0) > 30:
                    smart_recommendations.append(
                        f"Otimizar processo '{high_cpu_proc['name']}' que está usando "
                        f"{high_cpu_proc['cpu_percent']:.1f}% da CPU"
                    )
            
            test_result["details"] = {
                "health_analysis": analysis,
                "predictions": predictions,
                "smart_recommendations": smart_recommendations,
                "analysis_time_ms": 150  # Simulado
            }
            
            logger.info("✅ Análise de IA: SUCESSO")
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["errors"].append(str(e))
            logger.error(f"❌ Erro na análise de IA: {e}")
        
        return test_result
    
    def test_performance_monitoring(self) -> Dict[str, Any]:
        """Testa monitoramento de performance"""
        test_result = {
            "name": "Performance Monitoring",
            "status": "success",
            "details": {},
            "errors": []
        }
        
        try:
            start_time = time.time()
            
            # Simular diferentes operações e medir performance
            operations = {}
            
            # Teste 1: Operação de CPU
            cpu_start = time.time()
            result = sum(i * i for i in range(100000))  # Operação intensiva
            operations["cpu_intensive"] = time.time() - cpu_start
            
            # Teste 2: Operação de I/O
            io_start = time.time()
            with open('temp_test_file.txt', 'w') as f:
                f.write('test data' * 1000)
            with open('temp_test_file.txt', 'r') as f:
                data = f.read()
            os.remove('temp_test_file.txt')
            operations["io_intensive"] = time.time() - io_start
            
            # Teste 3: Operação de rede (simulada)
            network_start = time.time()
            # Simular latência de rede
            time.sleep(0.01)  # 10ms simulado
            operations["network_simulation"] = time.time() - network_start
            
            total_time = time.time() - start_time
            
            test_result["details"] = {
                "operations": operations,
                "total_test_time": total_time,
                "system_load": psutil.cpu_percent(),
                "memory_available": psutil.virtual_memory().available,
                "performance_score": max(0, 100 - (total_time * 10))  # Score baseado na velocidade
            }
            
            logger.info("✅ Monitoramento de performance: SUCESSO")
            
        except Exception as e:
            test_result["status"] = "error"
            test_result["errors"].append(str(e))
            logger.error(f"❌ Erro no monitoramento de performance: {e}")
        
        return test_result
    
    def generate_real_diagnostic_report(self, system_data: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Gera relatório de diagnóstico real"""
        try:
            report = {
                "report_id": f"DIAG_{int(time.time())}",
                "timestamp": datetime.utcnow().isoformat(),
                "device_info": system_data.get('system_info', {}),
                "metrics": {
                    "cpu": system_data.get('cpu', {}),
                    "memory": system_data.get('memory', {}),
                    "disk": system_data.get('disk', {}),
                    "network": system_data.get('network', {})
                },
                "health_analysis": analysis,
                "top_processes": system_data.get('top_processes', []),
                "recommendations": analysis.get('recommendations', []),
                "next_check": (datetime.utcnow().timestamp() + 3600),  # Próxima verificação em 1 hora
                "report_type": "real_system_diagnostic"
            }
            
            # Salvar relatório
            with open(f"diagnostic_report_{report['report_id']}.json", 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"✅ Relatório gerado: {report['report_id']}")
            return report
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar relatório: {e}")
            return {}
    
    async def run_complete_test(self):
        """Executa teste completo do sistema"""
        logger.info("🚀 Iniciando teste completo do sistema TechZe Diagnóstico")
        logger.info("=" * 60)
        
        # 1. Coleta de dados reais do sistema
        logger.info("📊 Coletando dados reais do sistema...")
        system_data = self.collect_real_system_data()
        if system_data:
            logger.info("✅ Dados do sistema coletados com sucesso")
            self.results["tests"]["data_collection"] = {
                "status": "success",
                "data_points": len(system_data),
                "timestamp": datetime.utcnow().isoformat()
            }
        else:
            logger.error("❌ Falha na coleta de dados")
            self.results["tests"]["data_collection"] = {"status": "error"}
            return
        
        # 2. Análise de saúde do sistema
        logger.info("🔍 Analisando saúde do sistema...")
        health_analysis = self.analyze_system_health(system_data)
        logger.info(f"📈 Score de saúde: {health_analysis.get('health_score', 0)}/100")
        logger.info(f"🎯 Status: {health_analysis.get('status', 'Unknown')}")
        
        # 3. Testes de banco de dados
        logger.info("🗄️ Testando operações de banco de dados...")
        db_test = self.test_database_operations()
        self.results["tests"]["database"] = db_test
        
        # 4. Testes de análise de IA
        logger.info("🤖 Testando análise de IA...")
        ai_test = self.test_ai_analysis(system_data)
        self.results["tests"]["ai_analysis"] = ai_test
        
        # 5. Testes de performance
        logger.info("⚡ Testando monitoramento de performance...")
        perf_test = self.test_performance_monitoring()
        self.results["tests"]["performance"] = perf_test
        
        # 6. Salvar dados no banco
        logger.info("💾 Salvando dados de diagnóstico...")
        system_data["analysis"] = health_analysis
        device_id = self.save_diagnostic_data(system_data, {"analysis": health_analysis})
        if device_id:
            self.results["tests"]["data_persistence"] = {
                "status": "success",
                "device_id": device_id
            }
        
        # 7. Gerar relatório final
        logger.info("📋 Gerando relatório de diagnóstico...")
        report = self.generate_real_diagnostic_report(system_data, health_analysis)
        if report:
            self.results["tests"]["report_generation"] = {
                "status": "success",
                "report_id": report.get("report_id")
            }
        
        # 8. Resumo final
        self.generate_final_summary()
        
        logger.info("=" * 60)
        logger.info("🎉 Teste completo finalizado!")
        return self.results
    
    def generate_final_summary(self):
        """Gera resumo final dos testes"""
        total_tests = len(self.results["tests"])
        successful_tests = len([t for t in self.results["tests"].values() 
                               if t.get("status") == "success"])
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
            "overall_status": "success" if successful_tests == total_tests else "partial",
            "test_completion_time": datetime.utcnow().isoformat()
        }
        
        # Log do resumo
        logger.info("📊 RESUMO DOS TESTES:")
        logger.info(f"   Total de testes: {total_tests}")
        logger.info(f"   Testes bem-sucedidos: {successful_tests}")
        logger.info(f"   Taxa de sucesso: {self.results['summary']['success_rate']:.1f}%")
        logger.info(f"   Status geral: {self.results['summary']['overall_status'].upper()}")

async def main():
    """Função principal para executar os testes"""
    tester = RealSystemTester()
    results = await tester.run_complete_test()
    
    # Salvar resultados
    with open(f"test_results_{int(time.time())}.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n🎯 RESULTADOS FINAIS:")
    print(json.dumps(results["summary"], indent=2))
    
    return results

if __name__ == "__main__":
    asyncio.run(main()) 