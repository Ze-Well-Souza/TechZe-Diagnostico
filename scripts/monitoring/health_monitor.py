#!/usr/bin/env python3
"""
Health Monitor - TechZe Diagnóstico
Monitoramento contínuo de saúde do sistema
Agente CURSOR - Automação 24/7
"""

import os
import time
import json
import psutil
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health_monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Monitor de saúde do sistema TechZe"""
    
    def __init__(self):
        self.config = {
            "check_interval": 60,  # segundos
            "api_url": "http://localhost:8000",
            "database_url": os.getenv("DATABASE_URL"),
            "alert_email": os.getenv("ALERT_EMAIL"),
            "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", 587)),
            "smtp_user": os.getenv("SMTP_USER"),
            "smtp_password": os.getenv("SMTP_PASSWORD"),
            
            # Thresholds de alerta
            "cpu_threshold": 80,
            "memory_threshold": 85,
            "disk_threshold": 90,
            "response_time_threshold": 5000,  # ms
            "error_rate_threshold": 5  # %
        }
        
        self.metrics_history = []
        self.alerts_sent = set()
        self.last_health_check = None
        
    def check_system_health(self) -> Dict[str, Any]:
        """Verificar saúde do sistema"""
        health_data = {
            "timestamp": datetime.now().isoformat(),
            "system": self.check_system_metrics(),
            "api": self.check_api_health(),
            "database": self.check_database_health(),
            "services": self.check_services_health(),
            "overall_status": "healthy"
        }
        
        # Determinar status geral
        if any(component.get("status") == "critical" for component in health_data.values() if isinstance(component, dict)):
            health_data["overall_status"] = "critical"
        elif any(component.get("status") == "warning" for component in health_data.values() if isinstance(component, dict)):
            health_data["overall_status"] = "warning"
        
        return health_data
    
    def check_system_metrics(self) -> Dict[str, Any]:
        """Verificar métricas do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            metrics = {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": disk.percent,
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
                "uptime": time.time() - psutil.boot_time(),
                "status": "healthy"
            }
            
            # Verificar thresholds
            if cpu_percent > self.config["cpu_threshold"]:
                metrics["status"] = "critical"
                metrics["alert"] = f"CPU usage high: {cpu_percent}%"
            elif memory.percent > self.config["memory_threshold"]:
                metrics["status"] = "critical"
                metrics["alert"] = f"Memory usage high: {memory.percent}%"
            elif disk.percent > self.config["disk_threshold"]:
                metrics["status"] = "warning"
                metrics["alert"] = f"Disk usage high: {disk.percent}%"
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erro ao verificar métricas do sistema: {e}")
            return {"status": "error", "error": str(e)}
    
    def check_api_health(self) -> Dict[str, Any]:
        """Verificar saúde da API"""
        try:
            start_time = time.time()
            
            # Health check endpoint
            response = requests.get(
                f"{self.config['api_url']}/health",
                timeout=10
            )
            
            response_time = (time.time() - start_time) * 1000
            
            api_health = {
                "status_code": response.status_code,
                "response_time_ms": response_time,
                "status": "healthy"
            }
            
            if response.status_code != 200:
                api_health["status"] = "critical"
                api_health["alert"] = f"API returning {response.status_code}"
            elif response_time > self.config["response_time_threshold"]:
                api_health["status"] = "warning"
                api_health["alert"] = f"Slow response: {response_time:.0f}ms"
            
            # Verificar endpoints críticos
            critical_endpoints = [
                "/api/diagnostics/status",
                "/api/auth/health",
                "/api/dashboard/summary"
            ]
            
            endpoint_results = {}
            for endpoint in critical_endpoints:
                try:
                    start = time.time()
                    resp = requests.get(f"{self.config['api_url']}{endpoint}", timeout=5)
                    duration = (time.time() - start) * 1000
                    
                    endpoint_results[endpoint] = {
                        "status_code": resp.status_code,
                        "response_time_ms": duration,
                        "healthy": resp.status_code < 400
                    }
                    
                except Exception as e:
                    endpoint_results[endpoint] = {
                        "error": str(e),
                        "healthy": False
                    }
            
            api_health["endpoints"] = endpoint_results
            
            # Verificar se algum endpoint crítico falhou
            failed_endpoints = [ep for ep, data in endpoint_results.items() if not data.get("healthy")]
            if failed_endpoints:
                api_health["status"] = "critical"
                api_health["alert"] = f"Critical endpoints failing: {failed_endpoints}"
            
            return api_health
            
        except Exception as e:
            logger.error(f"Erro ao verificar API: {e}")
            return {"status": "critical", "error": str(e), "alert": "API não responsiva"}
    
    def check_database_health(self) -> Dict[str, Any]:
        """Verificar saúde do banco de dados"""
        try:
            import psycopg2
            from urllib.parse import urlparse
            
            parsed = urlparse(self.config["database_url"])
            
            start_time = time.time()
            
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password
            )
            
            cursor = conn.cursor()
            
            # Verificar conectividade
            cursor.execute("SELECT 1")
            connection_time = (time.time() - start_time) * 1000
            
            # Verificar estatísticas da database
            cursor.execute("""
                SELECT 
                    count(*) as active_connections,
                    (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_queries
            """)
            stats = cursor.fetchone()
            
            # Verificar tamanho da database
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)
            db_size = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            db_health = {
                "connection_time_ms": connection_time,
                "active_connections": stats[0],
                "active_queries": stats[1],
                "database_size": db_size,
                "status": "healthy"
            }
            
            if connection_time > 1000:  # > 1 segundo
                db_health["status"] = "warning"
                db_health["alert"] = f"Slow database connection: {connection_time:.0f}ms"
            
            if stats[0] > 100:  # Muitas conexões ativas
                db_health["status"] = "warning"
                db_health["alert"] = f"High connection count: {stats[0]}"
            
            return db_health
            
        except Exception as e:
            logger.error(f"Erro ao verificar database: {e}")
            return {"status": "critical", "error": str(e), "alert": "Database não acessível"}
    
    def check_services_health(self) -> Dict[str, Any]:
        """Verificar saúde dos serviços"""
        services = {
            "redis": self.check_redis(),
            "nginx": self.check_nginx(),
            "celery": self.check_celery()
        }
        
        services_health = {
            "services": services,
            "status": "healthy"
        }
        
        # Verificar se algum serviço crítico falhou
        failed_services = [name for name, data in services.items() if data.get("status") == "critical"]
        if failed_services:
            services_health["status"] = "critical"
            services_health["alert"] = f"Critical services down: {failed_services}"
        
        return services_health
    
    def check_redis(self) -> Dict[str, Any]:
        """Verificar Redis"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, db=0)
            
            start_time = time.time()
            r.ping()
            response_time = (time.time() - start_time) * 1000
            
            info = r.info()
            
            return {
                "status": "healthy",
                "response_time_ms": response_time,
                "memory_usage": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients")
            }
            
        except Exception as e:
            return {"status": "critical", "error": str(e)}
    
    def check_nginx(self) -> Dict[str, Any]:
        """Verificar Nginx"""
        try:
            result = os.popen("systemctl is-active nginx").read().strip()
            
            if result == "active":
                return {"status": "healthy", "service_status": "active"}
            else:
                return {"status": "critical", "service_status": result}
                
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def check_celery(self) -> Dict[str, Any]:
        """Verificar Celery workers"""
        try:
            # Verificar se há workers ativos
            result = os.popen("celery -A app.celery inspect active").read()
            
            if "ERROR" in result:
                return {"status": "critical", "error": "Celery não responsivo"}
            
            return {"status": "healthy", "workers": "active"}
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def send_alert(self, health_data: Dict[str, Any]):
        """Enviar alerta por email"""
        if not self.config["alert_email"] or not self.config["smtp_user"]:
            return
        
        try:
            # Verificar se já enviamos este alerta recentemente
            alert_key = f"{health_data['overall_status']}_{datetime.now().strftime('%Y%m%d_%H')}"
            if alert_key in self.alerts_sent:
                return
            
            msg = MimeMultipart()
            msg['From'] = self.config["smtp_user"]
            msg['To'] = self.config["alert_email"]
            
            if health_data["overall_status"] == "critical":
                msg['Subject'] = "🚨 TechZe System CRITICAL Alert"
                priority = "HIGH"
            else:
                msg['Subject'] = "⚠️ TechZe System Warning"
                priority = "NORMAL"
            
            # Corpo do email
            body = f"""
            TechZe System Health Alert
            
            Status: {health_data['overall_status'].upper()}
            Timestamp: {health_data['timestamp']}
            
            System Metrics:
            - CPU: {health_data.get('system', {}).get('cpu_usage', 'N/A')}%
            - Memory: {health_data.get('system', {}).get('memory_usage', 'N/A')}%
            - Disk: {health_data.get('system', {}).get('disk_usage', 'N/A')}%
            
            API Status: {health_data.get('api', {}).get('status', 'N/A')}
            Database Status: {health_data.get('database', {}).get('status', 'N/A')}
            
            Alerts:
            """
            
            # Adicionar alertas específicos
            for component, data in health_data.items():
                if isinstance(data, dict) and data.get("alert"):
                    body += f"- {component}: {data['alert']}\n"
            
            body += f"\n\nFull health report: {json.dumps(health_data, indent=2)}"
            
            msg.attach(MimeText(body, 'plain'))
            
            # Enviar email
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            server.starttls()
            server.login(self.config["smtp_user"], self.config["smtp_password"])
            server.send_message(msg)
            server.quit()
            
            self.alerts_sent.add(alert_key)
            logger.info(f"Alert sent for {health_data['overall_status']} status")
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta: {e}")
    
    def save_metrics(self, health_data: Dict[str, Any]):
        """Salvar métricas para histórico"""
        self.metrics_history.append(health_data)
        
        # Manter apenas últimas 1440 entradas (24h se check a cada minuto)
        if len(self.metrics_history) > 1440:
            self.metrics_history = self.metrics_history[-1440:]
        
        # Salvar em arquivo
        with open("logs/health_metrics.json", "w") as f:
            json.dump(self.metrics_history[-100:], f, indent=2)  # Últimas 100 entradas
    
    def generate_daily_report(self):
        """Gerar relatório diário"""
        if not self.metrics_history:
            return
        
        today = datetime.now().date()
        today_metrics = [
            m for m in self.metrics_history 
            if datetime.fromisoformat(m["timestamp"]).date() == today
        ]
        
        if not today_metrics:
            return
        
        # Calcular estatísticas
        avg_cpu = sum(m.get("system", {}).get("cpu_usage", 0) for m in today_metrics) / len(today_metrics)
        avg_memory = sum(m.get("system", {}).get("memory_usage", 0) for m in today_metrics) / len(today_metrics)
        
        critical_incidents = len([m for m in today_metrics if m["overall_status"] == "critical"])
        warning_incidents = len([m for m in today_metrics if m["overall_status"] == "warning"])
        
        uptime_percentage = ((len(today_metrics) - critical_incidents) / len(today_metrics)) * 100
        
        report = {
            "date": today.isoformat(),
            "total_checks": len(today_metrics),
            "average_cpu": round(avg_cpu, 2),
            "average_memory": round(avg_memory, 2),
            "critical_incidents": critical_incidents,
            "warning_incidents": warning_incidents,
            "uptime_percentage": round(uptime_percentage, 2)
        }
        
        # Salvar relatório
        with open(f"reports/daily_health_report_{today.isoformat()}.json", "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Daily report generated: {uptime_percentage:.2f}% uptime")
    
    def run_monitoring(self):
        """Executar monitoramento contínuo"""
        logger.info("🔍 Iniciando monitoramento de saúde do sistema")
        
        while True:
            try:
                # Verificar saúde do sistema
                health_data = self.check_system_health()
                
                # Log do status
                logger.info(f"System status: {health_data['overall_status']}")
                
                # Enviar alertas se necessário
                if health_data["overall_status"] in ["critical", "warning"]:
                    self.send_alert(health_data)
                
                # Salvar métricas
                self.save_metrics(health_data)
                
                # Gerar relatório diário (uma vez por dia)
                if not self.last_health_check or \
                   datetime.now().date() > datetime.fromisoformat(self.last_health_check).date():
                    self.generate_daily_report()
                
                self.last_health_check = health_data["timestamp"]
                
                # Aguardar próximo check
                time.sleep(self.config["check_interval"])
                
            except KeyboardInterrupt:
                logger.info("Monitoramento interrompido pelo usuário")
                break
            except Exception as e:
                logger.error(f"Erro no monitoramento: {e}")
                time.sleep(30)  # Aguardar antes de tentar novamente


def main():
    """Função principal"""
    # Criar diretórios necessários
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    monitor = HealthMonitor()
    monitor.run_monitoring()


if __name__ == "__main__":
    main() 