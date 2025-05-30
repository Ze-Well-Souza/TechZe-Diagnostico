import logging
import platform
import psutil
import socket
import subprocess
import time
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)


class NetworkAnalyzer:
    """Analisador de rede para diagnóstico de sistema."""
    
    def __init__(self):
        """Inicializa o analisador de rede."""
        self.ping_targets = ["8.8.8.8", "1.1.1.1"]  # Servidores DNS do Google e Cloudflare
    
    def analyze(self) -> Dict[str, Any]:
        """Realiza análise completa da rede.
        
        Returns:
            Dicionário com resultados da análise
        """
        try:
            # Coleta informações da rede
            interfaces = self._get_network_interfaces()
            connectivity = self._check_connectivity()
            latency = self._measure_latency()
            bandwidth = self._estimate_bandwidth()
            dns = self._check_dns()
            
            # Determina o status da rede
            status = self._determine_status(connectivity, latency, interfaces)
            
            # Compila os resultados
            result = {
                "status": status,
                "interfaces": interfaces,
                "connectivity": connectivity,
                "latency": latency,
                "bandwidth": bandwidth,
                "dns": dns
            }
            
            logger.info(f"Network analysis completed: {status}")
            return result
            
        except Exception as e:
            logger.exception(f"Error analyzing network: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def _get_network_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """Obtém informações sobre interfaces de rede.
        
        Returns:
            Dicionário com informações por interface
        """
        try:
            interfaces = {}
            net_io = psutil.net_io_counters(pernic=True)
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            for nic, addrs in net_if_addrs.items():
                # Ignora interfaces virtuais e de loopback
                if nic == "lo" or nic.startswith("veth") or nic.startswith("docker"):
                    continue
                
                # Coleta endereços IP
                ipv4 = None
                ipv6 = None
                mac = None
                
                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        ipv4 = addr.address
                    elif addr.family == socket.AF_INET6:  # IPv6
                        ipv6 = addr.address
                    elif addr.family == psutil.AF_LINK:  # MAC
                        mac = addr.address
                
                # Coleta estatísticas da interface
                is_up = net_if_stats.get(nic, None) and net_if_stats[nic].isup
                speed = net_if_stats.get(nic, None) and net_if_stats[nic].speed or 0
                
                # Coleta contadores de I/O
                io_stats = {}
                if nic in net_io:
                    io = net_io[nic]
                    io_stats = {
                        "bytes_sent": io.bytes_sent / (1024 * 1024),  # Converte para MB
                        "bytes_recv": io.bytes_recv / (1024 * 1024),  # Converte para MB
                        "packets_sent": io.packets_sent,
                        "packets_recv": io.packets_recv,
                        "errin": io.errin,
                        "errout": io.errout,
                        "dropin": io.dropin,
                        "dropout": io.dropout
                    }
                
                # Coleta estatísticas novamente após um intervalo para calcular taxas
                time.sleep(0.1)  # Pequeno intervalo para medir a diferença
                net_io_after = psutil.net_io_counters(pernic=True)
                
                # Calcula taxas de transferência
                transfer_rates = {}
                if nic in net_io and nic in net_io_after:
                    io_before = net_io[nic]
                    io_after = net_io_after[nic]
                    time_diff = 0.1  # Segundos
                    
                    bytes_sent_diff = io_after.bytes_sent - io_before.bytes_sent
                    bytes_recv_diff = io_after.bytes_recv - io_before.bytes_recv
                    
                    transfer_rates = {
                        "upload_speed": bytes_sent_diff / (1024 * 1024) / time_diff,  # MB/s
                        "download_speed": bytes_recv_diff / (1024 * 1024) / time_diff  # MB/s
                    }
                
                # Compila informações da interface
                interfaces[nic] = {
                    "ipv4": ipv4,
                    "ipv6": ipv6,
                    "mac": mac,
                    "is_up": is_up,
                    "speed": speed,  # Mbps
                    "stats": io_stats,
                    "transfer_rates": transfer_rates
                }
            
            return interfaces
            
        except Exception as e:
            logger.error(f"Error getting network interfaces: {str(e)}")
            return {}
    
    def _check_connectivity(self) -> Dict[str, Any]:
        """Verifica a conectividade com a Internet.
        
        Returns:
            Dicionário com resultados da verificação
        """
        try:
            # Verifica se há conexão com a Internet
            connected = False
            for target in self.ping_targets:
                if self._ping(target)[0]:
                    connected = True
                    break
            
            # Obtém o hostname local
            hostname = socket.gethostname()
            
            # Tenta resolver o endereço IP local
            local_ip = None
            try:
                local_ip = socket.gethostbyname(hostname)
            except socket.gaierror:
                pass
            
            # Verifica se há um gateway padrão
            gateway = self._get_default_gateway()
            
            return {
                "internet_connected": connected,
                "hostname": hostname,
                "local_ip": local_ip,
                "gateway": gateway
            }
            
        except Exception as e:
            logger.error(f"Error checking connectivity: {str(e)}")
            return {
                "internet_connected": False,
                "error_message": str(e)
            }
    
    def _measure_latency(self) -> Dict[str, Any]:
        """Mede a latência da rede para servidores externos.
        
        Returns:
            Dicionário com resultados de latência
        """
        try:
            results = {}
            for target in self.ping_targets:
                success, latency = self._ping(target)
                results[target] = {
                    "success": success,
                    "latency_ms": latency
                }
            
            # Calcula a latência média
            successful_pings = [result["latency_ms"] for result in results.values() if result["success"]]
            avg_latency = sum(successful_pings) / len(successful_pings) if successful_pings else None
            
            return {
                "targets": results,
                "average_ms": avg_latency
            }
            
        except Exception as e:
            logger.error(f"Error measuring latency: {str(e)}")
            return {
                "error_message": str(e)
            }
    
    def _estimate_bandwidth(self) -> Dict[str, Any]:
        """Estima a largura de banda disponível.
        
        Returns:
            Dicionário com estimativas de largura de banda
        """
        try:
            # Em um sistema real, isso seria implementado com testes reais de velocidade
            # Por enquanto, usamos uma estimativa baseada nas interfaces de rede
            interfaces = self._get_network_interfaces()
            
            # Calcula a média das velocidades de todas as interfaces ativas
            upload_speeds = []
            download_speeds = []
            
            for nic, info in interfaces.items():
                if info["is_up"] and "transfer_rates" in info:
                    rates = info["transfer_rates"]
                    if "upload_speed" in rates:
                        upload_speeds.append(rates["upload_speed"])
                    if "download_speed" in rates:
                        download_speeds.append(rates["download_speed"])
            
            avg_upload = sum(upload_speeds) / len(upload_speeds) if upload_speeds else 0
            avg_download = sum(download_speeds) / len(download_speeds) if download_speeds else 0
            
            return {
                "upload_mbps": avg_upload * 8,  # Converte MB/s para Mbps
                "download_mbps": avg_download * 8,  # Converte MB/s para Mbps
                "estimated": True  # Indica que são valores estimados
            }
            
        except Exception as e:
            logger.error(f"Error estimating bandwidth: {str(e)}")
            return {
                "upload_mbps": 0.0,
                "download_mbps": 0.0,
                "estimated": True
            }
    
    def _check_dns(self) -> Dict[str, Any]:
        """Verifica a resolução DNS.
        
        Returns:
            Dicionário com resultados da verificação DNS
        """
        try:
            domains = ["google.com", "microsoft.com", "amazon.com"]
            results = {}
            
            for domain in domains:
                try:
                    start_time = time.time()
                    ip = socket.gethostbyname(domain)
                    resolve_time = (time.time() - start_time) * 1000  # ms
                    
                    results[domain] = {
                        "success": True,
                        "ip": ip,
                        "resolve_time_ms": resolve_time
                    }
                except socket.gaierror:
                    results[domain] = {
                        "success": False,
                        "error": "DNS resolution failed"
                    }
            
            # Calcula o tempo médio de resolução
            successful_resolves = [result["resolve_time_ms"] for result in results.values() 
                                if result.get("success", False)]
            avg_resolve_time = sum(successful_resolves) / len(successful_resolves) if successful_resolves else None
            
            # Verifica se a resolução DNS está funcionando
            dns_working = any(result.get("success", False) for result in results.values())
            
            return {
                "working": dns_working,
                "domains": results,
                "average_resolve_time_ms": avg_resolve_time
            }
            
        except Exception as e:
            logger.error(f"Error checking DNS: {str(e)}")
            return {
                "working": False,
                "error_message": str(e)
            }
    
    def _ping(self, host: str) -> Tuple[bool, Optional[float]]:
        """Realiza um ping para o host especificado.
        
        Args:
            host: Endereço do host para ping
            
        Returns:
            Tupla com sucesso (bool) e latência em ms (float ou None)
        """
        try:
            # Determina o comando de ping com base no sistema operacional
            if platform.system().lower() == "windows":
                command = ["ping", "-n", "1", "-w", "1000", host]
            else:  # Linux/Mac
                command = ["ping", "-c", "1", "-W", "1", host]
            
            # Executa o comando de ping
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Verifica se o ping foi bem-sucedido
            if result.returncode == 0:
                # Extrai o tempo de latência da saída
                output = result.stdout.lower()
                if "time=" in output or "tempo=" in output:
                    # Extrai o valor de tempo da saída
                    time_str = output.split("time=")[1].split("ms")[0].strip() if "time=" in output else \
                              output.split("tempo=")[1].split("ms")[0].strip()
                    try:
                        return True, float(time_str)
                    except ValueError:
                        return True, None
                return True, None
            else:
                return False, None
                
        except Exception as e:
            logger.error(f"Error pinging {host}: {str(e)}")
            return False, None
    
    def _get_default_gateway(self) -> Optional[str]:
        """Obtém o endereço IP do gateway padrão.
        
        Returns:
            Endereço IP do gateway ou None
        """
        try:
            # Tenta obter o gateway usando psutil (não disponível em todas as plataformas)
            if hasattr(psutil, "net_if_default_gateway"):
                gateways = psutil.net_if_default_gateway()
                if gateways and len(gateways) > 0:
                    return list(gateways.values())[0][0]
            
            # Método alternativo para Windows
            if platform.system().lower() == "windows":
                output = subprocess.check_output(["ipconfig"], text=True)
                for line in output.split("\n"):
                    if "Default Gateway" in line or "Gateway Padrão" in line:
                        parts = line.split(":", 1)
                        if len(parts) > 1 and parts[1].strip():
                            return parts[1].strip()
            
            # Método alternativo para Linux
            elif platform.system().lower() == "linux":
                output = subprocess.check_output(["ip", "route", "show", "default"], text=True)
                if output:
                    parts = output.split()
                    if len(parts) > 2 and parts[0] == "default":
                        return parts[2]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting default gateway: {str(e)}")
            return None
    
    def _determine_status(self, connectivity: Dict[str, Any], latency: Dict[str, Any], 
                         interfaces: Dict[str, Dict[str, Any]]) -> str:
        """Determina o status da rede com base na conectividade e latência.
        
        Args:
            connectivity: Resultados da verificação de conectividade
            latency: Resultados da medição de latência
            interfaces: Informações das interfaces de rede
            
        Returns:
            Status da rede: "healthy", "warning", "critical" ou "error"
        """
        # Verifica se há conexão com a Internet
        if not connectivity.get("internet_connected", False):
            return "critical"
        
        # Verifica se há interfaces de rede ativas
        active_interfaces = [nic for nic, info in interfaces.items() if info.get("is_up", False)]
        if not active_interfaces:
            return "critical"
        
        # Verifica a latência média
        avg_latency = latency.get("average_ms")
        if avg_latency is not None:
            if avg_latency > 200:  # Latência alta
                return "warning"
            elif avg_latency > 500:  # Latência muito alta
                return "critical"
        
        # Verifica erros nas interfaces
        for nic, info in interfaces.items():
            if info.get("is_up", False) and "stats" in info:
                stats = info["stats"]
                if stats.get("errin", 0) > 0 or stats.get("errout", 0) > 0:
                    return "warning"
        
        return "healthy"