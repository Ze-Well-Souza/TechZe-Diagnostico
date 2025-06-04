#!/usr/bin/env python3
"""
Script de teste para o serviço de diagnóstico.
Executa testes locais para verificar se o serviço está funcionando corretamente.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime

# Adiciona o diretório do app ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.analyzers import CPUAnalyzer, MemoryAnalyzer, DiskAnalyzer, NetworkAnalyzer, AntivirusAnalyzer, DriverAnalyzer
from app.services.system_info_service import SystemInfoService

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class DiagnosticTester:
    """Classe para testar o serviço de diagnóstico."""
    
    def __init__(self):
        self.cpu_analyzer = CPUAnalyzer()
        self.memory_analyzer = MemoryAnalyzer()
        self.disk_analyzer = DiskAnalyzer()
        self.network_analyzer = NetworkAnalyzer()
        self.antivirus_analyzer = AntivirusAnalyzer()
        self.driver_analyzer = DriverAnalyzer()
        self.system_info_service = SystemInfoService()
    
    async def test_all_analyzers(self):
        """Testa todos os analisadores."""
        print("=" * 60)
        print("TESTE COMPLETO DO SERVIÇO DE DIAGNÓSTICO")
        print("=" * 60)
        print(f"Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        try:
            # Executa análises em paralelo
            print("🔄 Executando análises em paralelo...")
            
            cpu_task = asyncio.create_task(self._test_cpu_analyzer())
            memory_task = asyncio.create_task(self._test_memory_analyzer())
            disk_task = asyncio.create_task(self._test_disk_analyzer())
            network_task = asyncio.create_task(self._test_network_analyzer())
            antivirus_task = asyncio.create_task(self._test_antivirus_analyzer())
            driver_task = asyncio.create_task(self._test_driver_analyzer())
            system_info_task = asyncio.create_task(self._test_system_info())
            
            # Aguarda todas as análises
            cpu_result, memory_result, disk_result, network_result, antivirus_result, driver_result, system_info = await asyncio.gather(
                cpu_task, memory_task, disk_task, network_task, antivirus_task, driver_task, system_info_task,
                return_exceptions=True
            )
            
            # Compila os resultados
            results = {
                "cpu": cpu_result,
                "memory": memory_result,
                "disk": disk_result,
                "network": network_result,
                "antivirus": antivirus_result,
                "drivers": driver_result,
                "system_info": system_info
            }
            
            # Calcula o health score
            health_score = self._calculate_health_score(results)
            
            # Exibe resumo
            self._display_summary(results, health_score)
            
            return results
            
        except Exception as e:
            logger.exception(f"Erro no teste completo: {str(e)}")
            print(f"❌ Erro no teste: {str(e)}")
            return None
    
    async def _test_cpu_analyzer(self):
        """Testa o analisador de CPU."""
        print("🔍 Testando analisador de CPU...")
        try:
            result = await asyncio.to_thread(self.cpu_analyzer.analyze)
            print(f"✅ CPU: {result.get('status', 'unknown')} - Uso: {result.get('usage', 0):.1f}%")
            return result
        except Exception as e:
            print(f"❌ Erro no analisador de CPU: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _test_memory_analyzer(self):
        """Testa o analisador de memória."""
        print("🔍 Testando analisador de memória...")
        try:
            result = await asyncio.to_thread(self.memory_analyzer.analyze)
            total_gb = result.get('total', 0) / 1024
            available_gb = result.get('available', 0) / 1024
            print(f"✅ Memória: {result.get('status', 'unknown')} - Uso: {result.get('usage', 0):.1f}% - Total: {total_gb:.1f}GB")
            return result
        except Exception as e:
            print(f"❌ Erro no analisador de memória: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _test_disk_analyzer(self):
        """Testa o analisador de disco."""
        print("🔍 Testando analisador de disco...")
        try:
            result = await asyncio.to_thread(self.disk_analyzer.analyze)
            total_gb = result.get('total', 0) / 1024
            available_gb = result.get('available', 0) / 1024
            print(f"✅ Disco: {result.get('status', 'unknown')} - Uso: {result.get('usage', 0):.1f}% - Total: {total_gb:.1f}GB")
            return result
        except Exception as e:
            print(f"❌ Erro no analisador de disco: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _test_network_analyzer(self):
        """Testa o analisador de rede."""
        print("🔍 Testando analisador de rede...")
        try:
            result = await asyncio.to_thread(self.network_analyzer.analyze)
            interfaces_count = len(result.get('interfaces', {}))
            connectivity = result.get('connectivity', {}).get('internet_connected', False)
            print(f"✅ Rede: {result.get('status', 'unknown')} - Interfaces: {interfaces_count} - Internet: {'Sim' if connectivity else 'Não'}")
            return result
        except Exception as e:
            print(f"❌ Erro no analisador de rede: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _test_antivirus_analyzer(self):
        """Testa o analisador de antivírus."""
        print("🔍 Testando analisador de antivírus...")
        try:
            result = await asyncio.to_thread(self.antivirus_analyzer.analyze)
            av_count = len(result.get('installed_antiviruses', []))
            defender_enabled = result.get('windows_defender', {}).get('enabled', False)
            print(f"✅ Antivírus: {result.get('status', 'unknown')} - Instalados: {av_count} - Defender: {'Sim' if defender_enabled else 'Não'}")
            return result
        except Exception as e:
            print(f"❌ Erro no analisador de antivírus: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _test_driver_analyzer(self):
        """Testa o analisador de drivers."""
        print("🔍 Testando analisador de drivers...")
        try:
            result = await asyncio.to_thread(self.driver_analyzer.analyze)
            total_drivers = result.get('total_drivers', 0)
            problematic = result.get('problematic_drivers', 0)
            outdated = result.get('outdated_drivers', 0)
            print(f"✅ Drivers: {result.get('status', 'unknown')} - Total: {total_drivers} - Problemáticos: {problematic} - Desatualizados: {outdated}")
            return result
        except Exception as e:
            print(f"❌ Erro no analisador de drivers: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _test_system_info(self):
        """Testa a coleta de informações do sistema."""
        print("🔍 Testando coleta de informações do sistema...")
        try:
            result = await asyncio.to_thread(self.system_info_service.collect_system_info)
            hostname = result.get('hostname', 'unknown')
            os_name = result.get('os_name', 'unknown')
            print(f"✅ Sistema: {hostname} - OS: {os_name}")
            return result
        except Exception as e:
            print(f"❌ Erro na coleta de informações do sistema: {str(e)}")
            return {"error": str(e)}
    
    def _calculate_health_score(self, results):
        """Calcula o health score baseado nos resultados."""
        try:
            scores = []
            
            # Score da CPU
            cpu_status = results.get("cpu", {}).get("status", "error")
            if cpu_status == "healthy":
                scores.append(100)
            elif cpu_status == "warning":
                scores.append(70)
            elif cpu_status == "critical":
                scores.append(30)
            else:
                scores.append(50)
            
            # Score da Memória
            memory_status = results.get("memory", {}).get("status", "error")
            if memory_status == "healthy":
                scores.append(100)
            elif memory_status == "warning":
                scores.append(70)
            elif memory_status == "critical":
                scores.append(30)
            else:
                scores.append(50)
            
            # Score do Disco
            disk_status = results.get("disk", {}).get("status", "error")
            if disk_status == "healthy":
                scores.append(100)
            elif disk_status == "warning":
                scores.append(70)
            elif disk_status == "critical":
                scores.append(30)
            else:
                scores.append(50)
            
            # Score da Rede
            network_status = results.get("network", {}).get("status", "error")
            if network_status == "healthy":
                scores.append(100)
            elif network_status == "warning":
                scores.append(70)
            elif network_status == "critical":
                scores.append(30)
            else:
                scores.append(50)
            
            # Score do Antivírus
            antivirus_status = results.get("antivirus", {}).get("status", "error")
            if antivirus_status == "healthy":
                scores.append(100)
            elif antivirus_status == "warning":
                scores.append(70)
            elif antivirus_status == "critical":
                scores.append(30)
            else:
                scores.append(50)
                
            # Score dos Drivers
            driver_status = results.get("drivers", {}).get("status", "error")
            if driver_status == "healthy":
                scores.append(100)
            elif driver_status == "warning":
                scores.append(70)
            elif driver_status == "critical":
                scores.append(30)
            else:
                scores.append(50)
            
            return int(sum(scores) / len(scores)) if scores else 50
            
        except Exception as e:
            logger.error(f"Erro ao calcular health score: {str(e)}")
            return 50
    
    def _display_summary(self, results, health_score):
        """Exibe o resumo dos resultados."""
        print()
        print("=" * 60)
        print("RESUMO DOS RESULTADOS")
        print("=" * 60)
        
        # Health Score
        if health_score >= 90:
            score_emoji = "🟢"
            score_text = "EXCELENTE"
        elif health_score >= 70:
            score_emoji = "🟡"
            score_text = "BOM"
        elif health_score >= 50:
            score_emoji = "🟠"
            score_text = "REGULAR"
        else:
            score_emoji = "🔴"
            score_text = "CRÍTICO"
        
        print(f"Health Score: {score_emoji} {health_score}/100 ({score_text})")
        print()
        
        # Status dos componentes
        components = [
            ("CPU", results.get("cpu", {}).get("status", "error")),
            ("Memória", results.get("memory", {}).get("status", "error")),
            ("Disco", results.get("disk", {}).get("status", "error")),
            ("Rede", results.get("network", {}).get("status", "error")),
            ("Antivírus", results.get("antivirus", {}).get("status", "error")),
            ("Drivers", results.get("drivers", {}).get("status", "error"))
        ]
        
        for component, status in components:
            if status == "healthy":
                emoji = "🟢"
                status_text = "HEALTHY"
            elif status == "warning":
                emoji = "🟡"
                status_text = "WARNING"
            elif status == "critical":
                emoji = "🔴"
                status_text = "CRITICAL"
            else:
                emoji = "⚪"
                status_text = "ERROR"
            
            print(f"{component}: {emoji} {status_text}")
        
        print()
        print("=" * 60)
        print(f"Teste concluído em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)


async def main():
    """Função principal."""
    try:
        tester = DiagnosticTester()
        results = await tester.test_all_analyzers()
        
        if results:
            print("\n🎉 Teste concluído com sucesso!")
            print("O serviço de diagnóstico está funcionando corretamente.")
        else:
            print("\n❌ Teste falhou!")
            print("Verifique os logs para mais detalhes.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Teste interrompido pelo usuário.")
    except Exception as e:
        logger.exception(f"Erro no teste: {str(e)}")
        print(f"\n❌ Erro no teste: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())