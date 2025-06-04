#!/usr/bin/env python3
"""
Script de configuração de segurança e monitoramento para TechZe
"""
import os
import sys
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_redis_availability():
    """Verifica se Redis está disponível"""
    try:
        import redis
        # Tenta conectar no Redis local
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        logger.info("✅ Redis disponível localmente")
        return "redis://localhost:6379"
    except Exception as e:
        logger.warning(f"⚠️ Redis não disponível localmente: {e}")
        
        # Verifica variável de ambiente
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            try:
                r = redis.from_url(redis_url)
                r.ping()
                logger.info("✅ Redis disponível via REDIS_URL")
                return redis_url
            except Exception as e:
                logger.warning(f"⚠️ Redis URL inválida: {e}")
        
        logger.info("ℹ️ Rate limiting funcionará em memória")
        return None


def setup_environment_variables():
    """Configura variáveis de ambiente"""
    env_vars = {
        "RATE_LIMIT_ENABLED": "true",
        "PROMETHEUS_ENABLED": "true",
        "AUDIT_LOG_TO_FILE": "true",
        "AUDIT_LOG_TO_CONSOLE": "true",
        "AUDIT_LOG_TO_SUPABASE": "true",
        "LOG_LEVEL": "INFO"
    }
    
    # Verifica Redis
    redis_url = check_redis_availability()
    if redis_url:
        env_vars["REDIS_URL"] = redis_url
    
    # Verifica Sentry
    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        env_vars["SENTRY_DSN"] = sentry_dsn
        logger.info("✅ Sentry DSN configurado")
    else:
        logger.info("ℹ️ Sentry DSN não configurado - error tracking desabilitado")
    
    # Cria arquivo .env se não existir
    env_file = Path(".env")
    if not env_file.exists():
        logger.info("📝 Criando arquivo .env")
        with open(env_file, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
    else:
        logger.info("ℹ️ Arquivo .env já existe")
    
    # Define variáveis no ambiente atual
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    logger.info("✅ Variáveis de ambiente configuradas")


def install_dependencies():
    """Instala dependências necessárias"""
    logger.info("📦 Verificando dependências...")
    
    # Lista de dependências críticas para segurança
    critical_deps = [
        "slowapi",
        "redis", 
        "prometheus-client",
        "prometheus-fastapi-instrumentator",
        "sentry-sdk[fastapi]"
    ]
    
    try:
        # Verifica se requirements.txt existe
        req_file = Path("requirements.txt")
        if req_file.exists():
            logger.info("📦 Instalando dependências do requirements.txt")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True)
            logger.info("✅ Dependências do requirements.txt instaladas")
        else:
            logger.warning("⚠️ requirements.txt não encontrado")
            
            # Instala dependências críticas individualmente
            logger.info("📦 Instalando dependências críticas...")
            for dep in critical_deps:
                try:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", dep
                    ], check=True)
                    logger.info(f"✅ {dep} instalado")
                except subprocess.CalledProcessError as e:
                    logger.warning(f"⚠️ Erro ao instalar {dep}: {e}")
    
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erro ao instalar dependências: {e}")
        
        # Tenta instalar dependências críticas individualmente
        logger.info("🔄 Tentando instalar dependências críticas individualmente...")
        for dep in critical_deps:
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], check=True)
                logger.info(f"✅ {dep} instalado")
            except subprocess.CalledProcessError as dep_error:
                logger.warning(f"⚠️ Erro ao instalar {dep}: {dep_error}")
        
        return False
    
    return True


def create_log_directories():
    """Cria diretórios de log necessários"""
    log_dirs = [
        "/tmp/techze_logs",
        "/tmp/reports"
    ]
    
    for log_dir in log_dirs:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"📁 Diretório criado: {log_dir}")


def test_security_features():
    """Testa funcionalidades de segurança"""
    logger.info("🧪 Testando funcionalidades de segurança...")
    
    try:
        # Testa imports
        from app.core.rate_limiter import AdvancedRateLimiter
        from app.core.monitoring import TechZeMetrics
        from app.core.error_tracking import ErrorTracker
        from app.core.audit import AuditService
        
        # Testa inicialização
        rate_limiter = AdvancedRateLimiter()
        metrics = TechZeMetrics()
        error_tracker = ErrorTracker()
        audit_service = AuditService()
        
        logger.info("✅ Todos os módulos de segurança carregados com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar módulos de segurança: {e}")
        return False


def generate_security_report():
    """Gera relatório de configuração de segurança"""
    report = """
🔒 RELATÓRIO DE CONFIGURAÇÃO DE SEGURANÇA - TechZe
================================================================

✅ IMPLEMENTADO:
- Rate Limiting avançado com Redis/Memory fallback
- Sistema de auditoria completo
- Monitoramento com Prometheus
- Error tracking com Sentry (se configurado)
- Logs estruturados
- Health checks avançados
- Métricas customizadas

🔧 CONFIGURAÇÕES:
- Rate Limiting: Habilitado
- Prometheus: Habilitado  
- Auditoria: Habilitada (file + console + supabase)
- Redis: {redis_status}
- Sentry: {sentry_status}

📊 ENDPOINTS ADICIONADOS:
- /metrics - Métricas Prometheus
- /health/detailed - Health check detalhado

🚀 PRÓXIMOS PASSOS:
1. Configure SENTRY_DSN para error tracking
2. Configure Redis para rate limiting distribuído
3. Configure alertas no Prometheus/Grafana
4. Implemente dashboard de monitoramento

================================================================
""".format(
        redis_status="Configurado" if os.getenv("REDIS_URL") else "Fallback para memória",
        sentry_status="Configurado" if os.getenv("SENTRY_DSN") else "Não configurado"
    )
    
    print(report)
    
    # Salva relatório em arquivo
    with open("security_setup_report.txt", "w") as f:
        f.write(report)
    
    logger.info("📄 Relatório salvo em security_setup_report.txt")


def main():
    """Função principal"""
    logger.info("🚀 Iniciando configuração de segurança TechZe...")
    
    # Muda para o diretório do script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    try:
        # 1. Instala dependências
        if not install_dependencies():
            logger.error("❌ Falha na instalação de dependências")
            return False
        
        # 2. Configura variáveis de ambiente
        setup_environment_variables()
        
        # 3. Cria diretórios necessários
        create_log_directories()
        
        # 4. Testa funcionalidades
        if not test_security_features():
            logger.error("❌ Falha nos testes de segurança")
            return False
        
        # 5. Gera relatório
        generate_security_report()
        
        logger.info("✅ Configuração de segurança concluída com sucesso!")
        logger.info("🚀 Execute 'python -m app.main' para iniciar o serviço")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante configuração: {e}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)