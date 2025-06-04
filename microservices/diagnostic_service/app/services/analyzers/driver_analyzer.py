import logging
import os
import platform
import subprocess
import winreg
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class DriverAnalyzer:
    """Analisador de drivers para diagnóstico de sistema."""
    
    def __init__(self):
        """Inicializa o analisador de drivers."""
        pass
    
    def analyze(self) -> Dict[str, Any]:
        """Realiza análise completa dos drivers do sistema.
        
        Returns:
            Dicionário com resultados da análise
        """
        try:
            # Coleta informações dos drivers
            drivers_info = self._get_drivers_info()
            problematic_drivers = self._identify_problematic_drivers(drivers_info)
            outdated_drivers = self._identify_outdated_drivers(drivers_info)
            
            # Determina o status geral dos drivers
            status = self._determine_driver_status(
                drivers_info, 
                problematic_drivers, 
                outdated_drivers
            )
            
            # Compila os resultados
            result = {
                "status": status,
                "total_drivers": len(drivers_info),
                "problematic_drivers": len(problematic_drivers),
                "outdated_drivers": len(outdated_drivers),
                "drivers_info": drivers_info,
                "problematic_list": problematic_drivers,
                "outdated_list": outdated_drivers,
                "recommendations": self._get_recommendations(status, problematic_drivers, outdated_drivers)
            }
            
            logger.info(f"Driver analysis completed: {status}")
            return result
            
        except Exception as e:
            logger.exception(f"Error analyzing drivers: {str(e)}")
            return {
                "status": "error",
                "error_message": str(e)
            }
    
    def _get_drivers_info(self) -> List[Dict[str, Any]]:
        """Obtém informações sobre os drivers instalados no sistema.
        
        Returns:
            Lista de informações sobre drivers
        """
        drivers = []
        
        try:
            if platform.system() == "Windows":
                drivers = self._get_windows_drivers()
            elif platform.system() == "Linux":
                drivers = self._get_linux_drivers()
                
        except Exception as e:
            logger.error(f"Error getting drivers information: {str(e)}")
        
        return drivers
    
    def _get_windows_drivers(self) -> List[Dict[str, Any]]:
        """Obtém informações sobre drivers no Windows.
        
        Returns:
            Lista de informações sobre drivers no Windows
        """
        drivers = []
        
        try:
            # Usar PowerShell para obter informações sobre drivers
            powershell_cmd = "Get-WmiObject Win32_PnPSignedDriver | Select-Object DeviceName, DriverVersion, Manufacturer, DriverDate, IsSigned | ConvertTo-Json"
            
            result = subprocess.run(
                ["powershell", "-Command", powershell_cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                import json
                try:
                    # Processar saída JSON
                    driver_objects = json.loads(result.stdout)
                    
                    # Garantir que temos uma lista mesmo se apenas um driver for retornado
                    if not isinstance(driver_objects, list):
                        driver_objects = [driver_objects]
                    
                    for driver in driver_objects:
                        if driver.get("DeviceName"):
                            driver_info = {
                                "name": driver.get("DeviceName", "Unknown"),
                                "version": driver.get("DriverVersion", "Unknown"),
                                "manufacturer": driver.get("Manufacturer", "Unknown"),
                                "date": driver.get("DriverDate", "Unknown"),
                                "signed": driver.get("IsSigned", False),
                                "status": "ok"  # Status padrão
                            }
                            drivers.append(driver_info)
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding driver JSON: {str(e)}")
            
            # Verificar drivers no Device Manager
            self._check_device_manager_status(drivers)
            
        except Exception as e:
            logger.error(f"Error getting Windows drivers: {str(e)}")
        
        return drivers
    
    def _check_device_manager_status(self, drivers: List[Dict[str, Any]]):
        """Verifica o status dos dispositivos no Gerenciador de Dispositivos.
        
        Args:
            drivers: Lista de drivers para atualizar com informações de status
        """
        try:
            # Usar PowerShell para obter dispositivos com problemas
            powershell_cmd = "Get-WmiObject Win32_PnPEntity | Where-Object {$_.ConfigManagerErrorCode -ne 0} | Select-Object Name, DeviceID, ConfigManagerErrorCode | ConvertTo-Json"
            
            result = subprocess.run(
                ["powershell", "-Command", powershell_cmd],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout and result.stdout.strip() != "":
                import json
                try:
                    # Processar saída JSON
                    problem_devices = json.loads(result.stdout)
                    
                    # Garantir que temos uma lista mesmo se apenas um dispositivo for retornado
                    if not isinstance(problem_devices, list):
                        problem_devices = [problem_devices]
                    
                    # Mapear códigos de erro para descrições
                    error_codes = {
                        1: "Device not configured correctly",
                        3: "Driver missing",
                        10: "Device cannot start",
                        12: "Cannot find hardware",
                        14: "Device needs to be restarted",
                        18: "Reinstall drivers",
                        19: "Registry corrupted",
                        21: "Device disabled",
                        22: "System failure",
                        24: "Device removed",
                        28: "Drivers not installed",
                        31: "Device not working properly",
                        32: "Service startup failed",
                        33: "Drivers corrupted",
                        34: "Device disabled",
                        35: "System failure",
                        36: "Device not present",
                        37: "Device not configured",
                        38: "Windows cannot load drivers",
                        39: "Registry corrupted",
                        40: "Driver corrupted",
                        41: "Device missing",
                        42: "Device needs restart",
                        43: "Device malfunctioning",
                        44: "Hardware failure",
                        45: "Device removed",
                        46: "Device waiting to be started",
                        47: "Device not started",
                        48: "System failure",
                        49: "Registry corrupted",
                        50: "System failure"
                    }
                    
                    # Atualizar status dos drivers com problemas
                    for device in problem_devices:
                        device_name = device.get("Name")
                        error_code = device.get("ConfigManagerErrorCode")
                        
                        if device_name:
                            # Encontrar o driver correspondente na lista
                            for driver in drivers:
                                if driver["name"] == device_name:
                                    driver["status"] = "error"
                                    driver["error_code"] = error_code
                                    driver["error_description"] = error_codes.get(error_code, "Unknown error")
                                    break
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding problem devices JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Error checking device manager status: {str(e)}")
    
    def _get_linux_drivers(self) -> List[Dict[str, Any]]:
        """Obtém informações sobre drivers no Linux.
        
        Returns:
            Lista de informações sobre drivers no Linux
        """
        drivers = []
        
        try:
            # Usar lsmod para listar módulos do kernel
            result = subprocess.run(
                ["lsmod"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                # Pular o cabeçalho
                if len(lines) > 1:
                    for line in lines[1:]:
                        parts = line.split()
                        if len(parts) >= 3:
                            module_name = parts[0]
                            module_size = parts[1]
                            used_count = parts[2]
                            
                            driver_info = {
                                "name": module_name,
                                "size": module_size,
                                "used_count": used_count,
                                "status": "ok"  # Status padrão
                            }
                            drivers.append(driver_info)
        except Exception as e:
            logger.error(f"Error getting Linux drivers: {str(e)}")
        
        return drivers
    
    def _identify_problematic_drivers(self, drivers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica drivers problemáticos.
        
        Args:
            drivers: Lista de informações sobre drivers
            
        Returns:
            Lista de drivers problemáticos
        """
        return [driver for driver in drivers if driver.get("status") == "error"]
    
    def _identify_outdated_drivers(self, drivers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identifica drivers potencialmente desatualizados.
        
        Args:
            drivers: Lista de informações sobre drivers
            
        Returns:
            Lista de drivers potencialmente desatualizados
        """
        # Esta é uma implementação simplificada
        # Em um cenário real, seria necessário verificar contra um banco de dados de versões atuais
        outdated = []
        
        # Verificar drivers sem assinatura digital (potencialmente desatualizados)
        for driver in drivers:
            if platform.system() == "Windows":
                if not driver.get("signed", True):
                    driver_copy = driver.copy()
                    driver_copy["outdated_reason"] = "Driver não possui assinatura digital"
                    outdated.append(driver_copy)
        
        return outdated
    
    def _determine_driver_status(self, drivers: List[Dict[str, Any]], 
                               problematic: List[Dict[str, Any]],
                               outdated: List[Dict[str, Any]]) -> str:
        """Determina o status geral dos drivers.
        
        Args:
            drivers: Lista de todos os drivers
            problematic: Lista de drivers problemáticos
            outdated: Lista de drivers desatualizados
            
        Returns:
            Status dos drivers: "healthy", "warning", "critical" ou "error"
        """
        if not drivers:
            return "unknown"
        
        problematic_percent = len(problematic) / len(drivers) * 100 if drivers else 0
        outdated_percent = len(outdated) / len(drivers) * 100 if drivers else 0
        
        if problematic_percent >= 5:  # Se 5% ou mais dos drivers têm problemas
            return "critical"
        elif problematic_percent > 0 or outdated_percent >= 10:  # Se há algum driver com problema ou 10% desatualizados
            return "warning"
        else:
            return "healthy"
    
    def _get_recommendations(self, status: str, problematic: List[Dict[str, Any]], 
                           outdated: List[Dict[str, Any]]) -> List[str]:
        """Gera recomendações baseadas no status dos drivers.
        
        Args:
            status: Status geral dos drivers
            problematic: Lista de drivers problemáticos
            outdated: Lista de drivers desatualizados
            
        Returns:
            Lista de recomendações
        """
        recommendations = []
        
        if status == "critical":
            recommendations.append("Atualize ou reinstale os drivers com problemas imediatamente")
            
            # Adicionar recomendações específicas para cada driver problemático
            for driver in problematic:
                error_desc = driver.get("error_description", "problema desconhecido")
                recommendations.append(f"Driver '{driver.get('name')}': {error_desc}")
                
        elif status == "warning":
            if problematic:
                recommendations.append("Verifique e atualize os drivers com problemas")
                
            if outdated:
                recommendations.append("Considere atualizar os drivers sem assinatura digital")
                
        else:  # healthy
            recommendations.append("Todos os drivers estão funcionando corretamente")
            recommendations.append("Continue mantendo seus drivers atualizados regularmente")
        
        return recommendations