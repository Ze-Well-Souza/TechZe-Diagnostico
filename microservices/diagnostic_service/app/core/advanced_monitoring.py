# -*- coding: utf-8 -*-
"""
Sistema de Monitoramento Avan√ßado - Semana 2
Implementa dashboards, alertas e m√©tricas avan√ßadas
"""
import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import psutil

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """N√≠veis de severidade de alertas"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    """Tipos de alertas"""
    PERFORMANCE = "performance"
    SECURITY = "security"
    AVAILABILITY = "availability"
    RESOURCE = "resource"
    BUSINESS = "business"


@dataclass
class Alert:
    """Estrutura de um alerta"""
    id: str
    type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    timestamp: datetime
    source: str
    metrics: Dict[str, Any]
    threshold: Optional[float] = None
    current_value: Optional[float] = None
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """Converte para dicion√°rio"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['resolved_at'] = self.resolved_at.isoformat() if self.resolved_at else None
        data['type'] = self.type.value
        data['severity'] = self.severity.value
        return data


class MetricsCollector:
    """Coletor avan√ßado de m√©tricas"""
    
    def __init__(self):
        self.metrics_history = []
        self.max_history = 1000
        
    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Coleta m√©tricas detalhadas do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Mem√≥ria
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disco
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Rede
            network_io = psutil.net_io_counters()
            network_connections = len(psutil.net_connections())
            
            # Processos
            process_count = len(psutil.pids())
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": cpu_count,
                    "frequency": {
                        "current": cpu_freq.current if cpu_freq else None,
                        "min": cpu_freq.min if cpu_freq else None,
                        "max": cpu_freq.max if cpu_freq else None
                    }
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used,
                    "free": memory.free,
                    "buffers": getattr(memory, 'buffers', 0),
                    "cached": getattr(memory, 'cached', 0)
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": swap.percent
                },
                "disk": {
                    "total": disk_usage.total,
                    "used": disk_usage.used,
                    "free": disk_usage.free,
                    "percent": (disk_usage.used / disk_usage.total) * 100,
                    "io": {
                        "read_count": disk_io.read_count if disk_io else 0,
                        "write_count": disk_io.write_count if disk_io else 0,
                        "read_bytes": disk_io.read_bytes if disk_io else 0,
                        "write_bytes": disk_io.write_bytes if disk_io else 0
                    }
                },
                "network": {
                    "bytes_sent": network_io.bytes_sent,
                    "bytes_recv": network_io.bytes_recv,
                    "packets_sent": network_io.packets_sent,
                    "packets_recv": network_io.packets_recv,
                    "connections": network_connections
                },
                "processes": {
                    "count": process_count
                }
            }
            
            # Adiciona ao hist√≥rico
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > self.max_history:
                self.metrics_history.pop(0)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao coletar m√©tricas do sistema: {e}")
            return {}
    
    async def collect_application_metrics(self) -> Dict[str, Any]:
        """Coleta m√©tricas espec√≠ficas da aplica√ß√£o"""
        try:
            # Simula m√©tricas da aplica√ß√£o
            # Em produ√ß√£o, isso viria do Prometheus ou outras fontes
            
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "requests": {
                    "total": 1000,  # Total de requisi√ß√µes
                    "rate": 10.5,   # Requisi√ß√µes por segundo
                    "errors": 5,    # N√∫mero de erros
                    "error_rate": 0.5  # Taxa de erro em %
                },
                "diagnostics": {
                    "active": 3,
                    "completed_today": 45,
                    "average_duration": 12.5,
                    "success_rate": 98.5
                },
                "users": {
                    "active": 15,
                    "authenticated": 12,
                    "anonymous": 3
                },
                "cache": {
                    "hit_rate": 85.2,
                    "miss_rate": 14.8,
                    "size_mb": 128
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao coletar m√©tricas da aplica√ß√£o: {e}")
            return {}
    
    def get_metrics_history(self, minutes: int = 60) -> List[Dict[str, Any]]:
        """Retorna hist√≥rico de m√©tricas dos √∫ltimos N minutos"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        return [
            metric for metric in self.metrics_history
            if datetime.fromisoformat(metric["timestamp"]) > cutoff_time
        ]


class AlertManager:
    """Gerenciador avan√ßado de alertas"""
    
    def __init__(self):
        self.alerts = []
        self.alert_rules = self._load_default_rules()
        self.notification_channels = []
        
    def _load_default_rules(self) -> List[Dict]:
        """Carrega regras de alerta padr√£o"""
        return [
            {
                "name": "high_cpu_usage",
                "metric": "cpu.percent",
                "threshold": 80,
                "operator": ">",
                "severity": AlertSeverity.HIGH,
                "type": AlertType.PERFORMANCE,
                "description": "Uso de CPU acima de 80%"
            },
            {
                "name": "high_memory_usage",
                "metric": "memory.percent",
                "threshold": 85,
                "operator": ">",
                "severity": AlertSeverity.HIGH,
                "type": AlertType.RESOURCE,
                "description": "Uso de mem√≥ria acima de 85%"
            },
            {
                "name": "low_disk_space",
                "metric": "disk.percent",
                "threshold": 90,
                "operator": ">",
                "severity": AlertSeverity.CRITICAL,
                "type": AlertType.RESOURCE,
                "description": "Espa√ßo em disco abaixo de 10%"
            },
            {
                "name": "high_error_rate",
                "metric": "requests.error_rate",
                "threshold": 5,
                "operator": ">",
                "severity": AlertSeverity.CRITICAL,
                "type": AlertType.AVAILABILITY,
                "description": "Taxa de erro acima de 5%"
            },
            {
                "name": "low_success_rate",
                "metric": "diagnostics.success_rate",
                "threshold": 95,
                "operator": "<",
                "severity": AlertSeverity.MEDIUM,
                "type": AlertType.BUSINESS,
                "description": "Taxa de sucesso de diagn√≥sticos abaixo de 95%"
            }
        ]
    
    def _get_nested_value(self, data: Dict, path: str) -> Optional[float]:
        """Obt√©m valor aninhado usando nota√ß√£o de ponto"""
        try:
            keys = path.split('.')
            value = data
            for key in keys:
                value = value[key]
            return float(value)
        except (KeyError, TypeError, ValueError):
            return None
    
    async def check_alerts(self, system_metrics: Dict, app_metrics: Dict) -> List[Alert]:
        """Verifica se alguma regra de alerta foi violada"""
        new_alerts = []
        all_metrics = {**system_metrics, **app_metrics}
        
        for rule in self.alert_rules:
            try:
                current_value = self._get_nested_value(all_metrics, rule["metric"])
                if current_value is None:
                    continue
                
                threshold = rule["threshold"]
                operator = rule["operator"]
                
                # Verifica condi√ß√£o
                triggered = False
                if operator == ">" and current_value > threshold:
                    triggered = True
                elif operator == "<" and current_value < threshold:
                    triggered = True
                elif operator == "==" and current_value == threshold:
                    triggered = True
                
                if triggered:
                    alert = Alert(
                        id=f"{rule['name']}_{int(time.time())}",
                        type=rule["type"],
                        severity=rule["severity"],
                        title=rule["name"].replace("_", " ").title(),
                        description=f"{rule['description']} (Atual: {current_value:.2f}, Limite: {threshold})",
                        timestamp=datetime.now(),
                        source="alert_manager",
                        metrics=all_metrics,
                        threshold=threshold,
                        current_value=current_value
                    )
                    
                    new_alerts.append(alert)
                    self.alerts.append(alert)
                    
                    logger.warning(f"üö® Alerta disparado: {alert.title}")
                    
            except Exception as e:
                logger.error(f"Erro ao verificar regra {rule['name']}: {e}")
        
        return new_alerts
    
    def get_active_alerts(self) -> List[Alert]:
        """Retorna alertas ativos (n√£o resolvidos)"""
        return [alert for alert in self.alerts if not alert.resolved]
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve um alerta"""
        for alert in self.alerts:
            if alert.id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                logger.info(f"‚úÖ Alerta resolvido: {alert.title}")
                return True
        return False
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Retorna resumo dos alertas"""
        active_alerts = self.get_active_alerts()
        
        summary = {
            "total_active": len(active_alerts),
            "by_severity": {
                "critical": len([a for a in active_alerts if a.severity == AlertSeverity.CRITICAL]),
                "high": len([a for a in active_alerts if a.severity == AlertSeverity.HIGH]),
                "medium": len([a for a in active_alerts if a.severity == AlertSeverity.MEDIUM]),
                "low": len([a for a in active_alerts if a.severity == AlertSeverity.LOW])
            },
            "by_type": {
                "performance": len([a for a in active_alerts if a.type == AlertType.PERFORMANCE]),
                "security": len([a for a in active_alerts if a.type == AlertType.SECURITY]),
                "availability": len([a for a in active_alerts if a.type == AlertType.AVAILABILITY]),
                "resource": len([a for a in active_alerts if a.type == AlertType.RESOURCE]),
                "business": len([a for a in active_alerts if a.type == AlertType.BUSINESS])
            },
            "recent_alerts": [alert.to_dict() for alert in active_alerts[-5:]]
        }
        
        return summary


class DashboardGenerator:
    """Gerador de dashboards din√¢micos"""
    
    def __init__(self, metrics_collector: MetricsCollector, alert_manager: AlertManager):
        self.metrics_collector = metrics_collector
        self.alert_manager = alert_manager
    
    async def generate_operational_dashboard(self) -> Dict[str, Any]:
        """Gera dashboard operacional"""
        try:
            # Coleta m√©tricas atuais
            system_metrics = await self.metrics_collector.collect_system_metrics()
            app_metrics = await self.metrics_collector.collect_application_metrics()
            
            # Hist√≥rico de m√©tricas
            history = self.metrics_collector.get_metrics_history(60)
            
            # Resumo de alertas
            alert_summary = self.alert_manager.get_alert_summary()
            
            dashboard = {
                "title": "Dashboard Operacional - TechZe",
                "generated_at": datetime.now().isoformat(),
                "refresh_interval": 30,
                "sections": {
                    "overview": {
                        "title": "Vis√£o Geral",
                        "widgets": [
                            {
                                "type": "metric",
                                "title": "CPU Usage",
                                "value": system_metrics.get("cpu", {}).get("percent", 0),
                                "unit": "%",
                                "status": self._get_status(system_metrics.get("cpu", {}).get("percent", 0), 80, 90)
                            },
                            {
                                "type": "metric",
                                "title": "Memory Usage",
                                "value": system_metrics.get("memory", {}).get("percent", 0),
                                "unit": "%",
                                "status": self._get_status(system_metrics.get("memory", {}).get("percent", 0), 80, 90)
                            },
                            {
                                "type": "metric",
                                "title": "Disk Usage",
                                "value": system_metrics.get("disk", {}).get("percent", 0),
                                "unit": "%",
                                "status": self._get_status(system_metrics.get("disk", {}).get("percent", 0), 80, 90)
                            },
                            {
                                "type": "metric",
                                "title": "Active Diagnostics",
                                "value": app_metrics.get("diagnostics", {}).get("active", 0),
                                "unit": "",
                                "status": "healthy"
                            }
                        ]
                    },
                    "performance": {
                        "title": "Performance",
                        "widgets": [
                            {
                                "type": "chart",
                                "title": "Request Rate",
                                "data": self._extract_time_series(history, "requests.rate"),
                                "unit": "req/s"
                            },
                            {
                                "type": "chart",
                                "title": "Response Time",
                                "data": self._extract_time_series(history, "diagnostics.average_duration"),
                                "unit": "s"
                            }
                        ]
                    },
                    "alerts": {
                        "title": "Alertas",
                        "widgets": [
                            {
                                "type": "alert_summary",
                                "data": alert_summary
                            }
                        ]
                    }
                }
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard operacional: {e}")
            return {"error": str(e)}
    
    async def generate_security_dashboard(self) -> Dict[str, Any]:
        """Gera dashboard de seguran√ßa"""
        try:
            dashboard = {
                "title": "Dashboard de Seguran√ßa - TechZe",
                "generated_at": datetime.now().isoformat(),
                "sections": {
                    "authentication": {
                        "title": "Autentica√ß√£o",
                        "widgets": [
                            {
                                "type": "metric",
                                "title": "Login Attempts",
                                "value": 150,
                                "unit": "today"
                            },
                            {
                                "type": "metric",
                                "title": "Failed Logins",
                                "value": 5,
                                "unit": "today",
                                "status": "warning" if 5 > 3 else "healthy"
                            }
                        ]
                    },
                    "rate_limiting": {
                        "title": "Rate Limiting",
                        "widgets": [
                            {
                                "type": "metric",
                                "title": "Blocked Requests",
                                "value": 25,
                                "unit": "today"
                            },
                            {
                                "type": "metric",
                                "title": "Rate Limit Hit Rate",
                                "value": 2.5,
                                "unit": "%"
                            }
                        ]
                    },
                    "security_events": {
                        "title": "Eventos de Seguran√ßa",
                        "widgets": [
                            {
                                "type": "list",
                                "title": "Recent Security Events",
                                "data": [
                                    {
                                        "timestamp": datetime.now().isoformat(),
                                        "event": "Rate limit exceeded",
                                        "ip": "192.168.1.100",
                                        "severity": "medium"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Erro ao gerar dashboard de seguran√ßa: {e}")
            return {"error": str(e)}
    
    def _get_status(self, value: float, warning_threshold: float, critical_threshold: float) -> str:
        """Determina status baseado em thresholds"""
        if value >= critical_threshold:
            return "critical"
        elif value >= warning_threshold:
            return "warning"
        else:
            return "healthy"
    
    def _extract_time_series(self, history: List[Dict], metric_path: str) -> List[Dict]:
        """Extrai s√©rie temporal de uma m√©trica"""
        try:
            time_series = []
            for entry in history[-20:]:  # √öltimos 20 pontos
                value = self._get_nested_value(entry, metric_path)
                if value is not None:
                    time_series.append({
                        "timestamp": entry["timestamp"],
                        "value": value
                    })
            return time_series
        except Exception:
            return []
    
    def _get_nested_value(self, data: Dict, path: str) -> Optional[float]:
        """Obt√©m valor aninhado usando nota√ß√£o de ponto"""
        try:
            keys = path.split('.')
            value = data
            for key in keys:
                value = value[key]
            return float(value)
        except (KeyError, TypeError, ValueError):
            return None


class AdvancedMonitoringService:
    """Servi√ßo principal de monitoramento avan√ßado"""
    
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self.dashboard_generator = DashboardGenerator(self.metrics_collector, self.alert_manager)
        self.monitoring_active = False
        self.monitoring_task = None
    
    async def start_monitoring(self, interval: int = 30):
        """Inicia monitoramento cont√≠nuo"""
        if self.monitoring_active:
            logger.warning("Monitoramento j√° est√° ativo")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop(interval))
        logger.info(f"üîç Monitoramento avan√ßado iniciado (intervalo: {interval}s)")
    
    async def stop_monitoring(self):
        """Para monitoramento cont√≠nuo"""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("üõë Monitoramento avan√ßado parado")
    
    async def _monitoring_loop(self, interval: int):
        """Loop principal de monitoramento"""
        while self.monitoring_active:
            try:
                # Coleta m√©tricas
                system_metrics = await self.metrics_collector.collect_system_metrics()
                app_metrics = await self.metrics_collector.collect_application_metrics()
                
                # Verifica alertas
                new_alerts = await self.alert_manager.check_alerts(system_metrics, app_metrics)
                
                if new_alerts:
                    logger.info(f"üö® {len(new_alerts)} novos alertas detectados")
                
                # Aguarda pr√≥ximo ciclo
                await asyncio.sleep(interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                await asyncio.sleep(interval)
    
    async def get_operational_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard operacional"""
        return await self.dashboard_generator.generate_operational_dashboard()
    
    async def get_security_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de seguran√ßa"""
        return await self.dashboard_generator.generate_security_dashboard()
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Retorna resumo de alertas"""
        return self.alert_manager.get_alert_summary()
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Retorna alertas ativos"""
        return [alert.to_dict() for alert in self.alert_manager.get_active_alerts()]
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve um alerta"""
        return self.alert_manager.resolve_alert(alert_id)


# Inst√¢ncia global do servi√ßo
advanced_monitoring = AdvancedMonitoringService()