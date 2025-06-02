import logging
import os
import platform
import subprocess
import winreg
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AntivirusAnalyzer:
    """Analisador de antivírus para diagnóstico de sistema."""
    
    def __init__(self):
        """Inicializa o analisador de antivírus."""
        pass
    
    def analyze(self) -> Dict[str, Any]:
        """Realiza análise completa dos sistemas de proteção.
        
        Returns:
            Dicionário com resultados da análise
        """
        try:
            # Coleta informações dos antivírus
            installed_antiviruses = self._get_installed_antiviruses()
            windows_defender = self._check_windows_defender()
            firewall_status = self._check_firewall()
            real_time_protection = self._check_real_time_protection()
            
            # Determina o status geral de proteção
            status = self._determine_protection_status(
                installed_antiviruses, 
                windows_defender, 
                firewall_status, 
                real_time_protection
            )
            
            # Compila os resultados
            result = {
                "status": status,
                "installed_antiviruses": installed_antiviruses,
                "windows_defender": windows_defender,
                "firewall": firewall_status,
                "real_time_protection": real_time_protection,
                "recommendations": self._get_recommendations(status, installed_antiviruses, windows_defender)
            }
            
            logger.info(f"Antivirus analysis completed: {status}")
            return result
            
        except Exception as e:
            logger.exception(f"Error analyzing antivirus protection: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def _get_installed_antiviruses(self) -> List[Dict[str, Any]]:
        """Obtém lista de antivírus instalados no sistema.
        
        Returns:
            Lista de antivírus encontrados
        """
        antiviruses = []
        
        try:
            if platform.system() == "Windows":
                antiviruses.extend(self._scan_windows_antiviruses())
            elif platform.system() == "Linux":
                antiviruses.extend(self._scan_linux_antiviruses())
            
        except Exception as e:
            logger.error(f"Error scanning for antiviruses: {str(e)}")
        
        return antiviruses
    
    def _scan_windows_antiviruses(self) -> List[Dict[str, Any]]:
        """Escaneia antivírus instalados no Windows.
        
        Returns:
            Lista de antivírus encontrados no Windows
        """
        antiviruses = []
        
        # Lista de antivírus conhecidos e seus indicadores
        known_antiviruses = {
            "Norton": ["Norton", "Symantec", "NortonSecurity"],
            "McAfee": ["McAfee", "McAfee Security"],
            "Avast": ["Avast", "AVAST Software"],
            "AVG": ["AVG", "AVG Technologies"],
            "Bitdefender": ["Bitdefender"],
            "Kaspersky": ["Kaspersky", "Kaspersky Lab"],
            "ESET": ["ESET", "NOD32"],
            "Trend Micro": ["Trend Micro"],
            "Malwarebytes": ["Malwarebytes"],
            "Windows Defender": ["Windows Defender", "Microsoft Defender"]
        }
        
        try:
            # Verifica no registro do Windows
            registry_paths = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
                r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
            ]
            
            for path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                    i = 0
                    
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            subkey = winreg.OpenKey(key, subkey_name)
                            
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                publisher = ""
                                version = ""
                                
                                try:
                                    publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                                except FileNotFoundError:
                                    pass
                                
                                try:
                                    version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                                except FileNotFoundError:
                                    pass
                                
                                # Verifica se é um antivírus conhecido
                                for av_name, indicators in known_antiviruses.items():
                                    for indicator in indicators:
                                        if indicator.lower() in display_name.lower() or indicator.lower() in publisher.lower():
                                            antivirus_info = {
                                                "name": av_name,
                                                "display_name": display_name,
                                                "publisher": publisher,
                                                "version": version,
                                                "status": "installed"
                                            }
                                            
                                            # Evita duplicatas
                                            if not any(av["name"] == av_name for av in antiviruses):
                                                antiviruses.append(antivirus_info)
                                            break
                                
                            except FileNotFoundError:
                                pass
                            
                            winreg.CloseKey(subkey)
                            i += 1
                            
                        except OSError:
                            break
                    
                    winreg.CloseKey(key)
                    
                except Exception as e:
                    logger.debug(f"Error accessing registry path {path}: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scanning Windows antiviruses: {str(e)}")
        
        return antiviruses
    
    def _scan_linux_antiviruses(self) -> List[Dict[str, Any]]:
        """Escaneia antivírus instalados no Linux.
        
        Returns:
            Lista de antivírus encontrados no Linux
        """
        antiviruses = []
        
        # Lista de antivírus conhecidos no Linux
        linux_antiviruses = [
            {"name": "ClamAV", "command": "clamscan", "service": "clamav-daemon"},
            {"name": "Sophos", "command": "savscan", "service": "sav-protect"},
            {"name": "ESET", "command": "esets_scan", "service": "esets"},
            {"name": "F-PROT", "command": "fpscan", "service": "f-prot"},
            {"name": "Bitdefender", "command": "bdscan", "service": "bd-protection"}
        ]
        
        for av in linux_antiviruses:
            try:
                # Verifica se o comando existe
                result = subprocess.run(
                    ["which", av["command"]], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                
                if result.returncode == 0:
                    antiviruses.append({
                        "name": av["name"],
                        "command": av["command"],
                        "path": result.stdout.strip(),
                        "status": "installed"
                    })
                    
            except Exception as e:
                logger.debug(f"Error checking {av['name']}: {str(e)}")
                continue
        
        return antiviruses
    
    def _check_windows_defender(self) -> Dict[str, Any]:
        """Verifica o status do Windows Defender.
        
        Returns:
            Informações sobre o Windows Defender
        """
        defender_info = {
            "enabled": False,
            "real_time_protection": False,
            "definition_status": "unknown",
            "last_scan": "unknown"
        }
        
        if platform.system() != "Windows":
            return defender_info
        
        try:
            # Verifica via PowerShell
            powershell_commands = [
                "Get-MpComputerStatus | Select-Object -Property AntivirusEnabled,RealTimeProtectionEnabled,AntivirusSignatureLastUpdated,QuickScanAge",
                "Get-MpPreference | Select-Object -Property DisableRealtimeMonitoring"
            ]
            
            for cmd in powershell_commands:
                try:
                    result = subprocess.run(
                        ["powershell", "-Command", cmd],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    if result.returncode == 0 and result.stdout:
                        output = result.stdout.lower()
                        
                        if "antivirusenabled" in output and "true" in output:
                            defender_info["enabled"] = True
                        
                        if "realtimeprotectionenabled" in output and "true" in output:
                            defender_info["real_time_protection"] = True
                        
                        if "disablerealtimemonitoring" in output and "false" in output:
                            defender_info["real_time_protection"] = True
                        
                except subprocess.TimeoutExpired:
                    logger.warning("PowerShell command timed out")
                    continue
                except Exception as e:
                    logger.debug(f"PowerShell command failed: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"Error checking Windows Defender: {str(e)}")
        
        return defender_info
    
    def _check_firewall(self) -> Dict[str, Any]:
        """Verifica o status do firewall do sistema.
        
        Returns:
            Informações sobre o firewall
        """
        firewall_info = {
            "enabled": False,
            "profiles": {},
            "status": "unknown"
        }
        
        try:
            if platform.system() == "Windows":
                firewall_info = self._check_windows_firewall()
            elif platform.system() == "Linux":
                firewall_info = self._check_linux_firewall()
                
        except Exception as e:
            logger.error(f"Error checking firewall: {str(e)}")
        
        return firewall_info
    
    def _check_windows_firewall(self) -> Dict[str, Any]:
        """Verifica o firewall do Windows.
        
        Returns:
            Status do Windows Firewall
        """
        firewall_info = {
            "enabled": False,
            "profiles": {},
            "status": "unknown"
        }
        
        try:
            # Verifica via netsh
            result = subprocess.run(
                ["netsh", "advfirewall", "show", "allprofiles", "state"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout.lower()
                profiles = ["domain", "private", "public"]
                
                for profile in profiles:
                    if f"{profile} profile" in output:
                        # Extrai o status do perfil
                        profile_section = output.split(f"{profile} profile")[1].split("\n\n")[0]
                        enabled = "on" in profile_section
                        firewall_info["profiles"][profile] = enabled
                        
                        if enabled:
                            firewall_info["enabled"] = True
                
                firewall_info["status"] = "active" if firewall_info["enabled"] else "inactive"
                
        except Exception as e:
            logger.error(f"Error checking Windows firewall: {str(e)}")
        
        return firewall_info
    
    def _check_linux_firewall(self) -> Dict[str, Any]:
        """Verifica firewalls no Linux.
        
        Returns:
            Status dos firewalls no Linux
        """
        firewall_info = {
            "enabled": False,
            "type": "unknown",
            "status": "unknown"
        }
        
        # Lista de firewalls para verificar
        firewalls = [
            {"name": "ufw", "check_cmd": ["ufw", "status"]},
            {"name": "iptables", "check_cmd": ["iptables", "-L"]},
            {"name": "firewalld", "check_cmd": ["firewall-cmd", "--state"]}
        ]
        
        for fw in firewalls:
            try:
                result = subprocess.run(
                    fw["check_cmd"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    output = result.stdout.lower()
                    
                    if fw["name"] == "ufw" and "status: active" in output:
                        firewall_info["enabled"] = True
                        firewall_info["type"] = "ufw"
                        firewall_info["status"] = "active"
                        break
                    elif fw["name"] == "firewalld" and "running" in output:
                        firewall_info["enabled"] = True
                        firewall_info["type"] = "firewalld"
                        firewall_info["status"] = "running"
                        break
                    elif fw["name"] == "iptables" and "chain" in output:
                        firewall_info["type"] = "iptables"
                        # Para iptables, verificamos se há regras ativas
                        if len(output.split('\n')) > 10:  # Mais de cabeçalhos básicos
                            firewall_info["enabled"] = True
                            firewall_info["status"] = "active"
                        break
                        
            except Exception as e:
                logger.debug(f"Error checking {fw['name']}: {str(e)}")
                continue
        
        return firewall_info
    
    def _check_real_time_protection(self) -> Dict[str, Any]:
        """Verifica se a proteção em tempo real está ativa.
        
        Returns:
            Status da proteção em tempo real
        """
        protection_info = {
            "enabled": False,
            "sources": []
        }
        
        try:
            if platform.system() == "Windows":
                # Verifica Windows Defender
                defender_info = self._check_windows_defender()
                if defender_info.get("real_time_protection", False):
                    protection_info["enabled"] = True
                    protection_info["sources"].append("Windows Defender")
                
                # Verifica outros antivírus (implementação básica)
                installed_avs = self._get_installed_antiviruses()
                for av in installed_avs:
                    if av["name"] != "Windows Defender":
                        protection_info["sources"].append(av["name"])
                        protection_info["enabled"] = True
                        
        except Exception as e:
            logger.error(f"Error checking real-time protection: {str(e)}")
        
        return protection_info
    
    def _determine_protection_status(self, antiviruses: List[Dict], defender: Dict, 
                                   firewall: Dict, real_time: Dict) -> str:
        """Determina o status geral de proteção.
        
        Args:
            antiviruses: Lista de antivírus instalados
            defender: Status do Windows Defender
            firewall: Status do firewall
            real_time: Status da proteção em tempo real
            
        Returns:
            Status de proteção: "healthy", "warning", "critical"
        """
        has_antivirus = len(antiviruses) > 0 or defender.get("enabled", False)
        has_firewall = firewall.get("enabled", False)
        has_real_time = real_time.get("enabled", False)
        
        if has_antivirus and has_firewall and has_real_time:
            return "healthy"
        elif has_antivirus or has_firewall:
            return "warning"
        else:
            return "critical"
    
    def _get_recommendations(self, status: str, antiviruses: List[Dict], 
                           defender: Dict) -> List[str]:
        """Gera recomendações baseadas no status de proteção.
        
        Args:
            status: Status atual de proteção
            antiviruses: Lista de antivírus instalados
            defender: Status do Windows Defender
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        if status == "critical":
            recommendations.extend([
                "Sistema em risco! Instale um antivírus imediatamente",
                "Ative o firewall do sistema",
                "Ative a proteção em tempo real"
            ])
        elif status == "warning":
            if not defender.get("enabled", False) and len(antiviruses) == 0:
                recommendations.append("Considere instalar ou ativar um antivírus")
            
            if not defender.get("real_time_protection", False):
                recommendations.append("Ative a proteção em tempo real")
                
            recommendations.append("Mantenha as definições de vírus atualizadas")
        else:
            recommendations.extend([
                "Sistema bem protegido",
                "Mantenha o antivírus sempre atualizado",
                "Faça verificações periódicas completas"
            ])
        
        return recommendations 