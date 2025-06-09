from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import time
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Imports da aplicação
from app.core.config import settings

# Imports do connection pooling avançado
try:
    from app.core.advanced_pool import AdvancedConnectionPool, initialize_advanced_pool, get_advanced_pool
    from app.core.advanced_pool_metrics import MetricsEnabledConnectionPool, create_metrics_enabled_pool
    from app.core.database_pool import pool_manager
    ADVANCED_POOL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Advanced pool modules not available: {e}")
    ADVANCED_POOL_AVAILABLE = False

# Imports dos novos módulos de segurança e monitoramento
try:
    from app.core.rate_limiter import setup_rate_limiting
    from app.core.monitoring import setup_monitoring, techze_metrics, monitor_diagnostic
    from app.core.error_tracking import setup_error_tracking, track_errors
    from app.core.audit import audit_service, AuditEventType, audit_endpoint
    from app.core.advanced_monitoring import advanced_monitoring
    from app.core.cache_manager import cache_manager
    SECURITY_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Security modules not available: {e}")
    SECURITY_MODULES_AVAILABLE = False

# Import condicional dos routers para evitar erros em caso de dependências faltantes
try:
    from app.api.router import api_router
    API_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API router not available: {e}")
    API_ROUTER_AVAILABLE = False

try:
    from app.api.v1.router import api_v1_router
    API_V1_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API v1 router not available: {e}")
    API_V1_ROUTER_AVAILABLE = False

# Import da API v3 (Semana 3 - IA, ML e Automação)
try:
    from app.api.v3 import ai_endpoints, automation_endpoints, analytics_endpoints, chat_endpoints
    from app.api.v3 import performance_endpoints
    API_V3_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API v3 router not available: {e}")
    API_V3_ROUTER_AVAILABLE = False

# Import da API Core (Consolidada)
try:
    from app.api.core.router import api_router as core_api_router
    API_CORE_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API Core router not available: {e}")
    API_CORE_ROUTER_AVAILABLE = False

# Import dos analisadores para funcionalidade básica
try:
    from app.services.analyzers import CPUAnalyzer, MemoryAnalyzer, DiskAnalyzer, NetworkAnalyzer
    from app.services.system_info_service import SystemInfoService
    ANALYZERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Analyzers not available: {e}")
    ANALYZERS_AVAILABLE = False

# Função de ciclo de vida da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Iniciando TechZe Diagnostic Service...")
    
    # Inicializar connection pooling avançado
    if ADVANCED_POOL_AVAILABLE:
        try:
            # Configuração dos nós do banco de dados
            db_nodes = [
                {
                    "id": "primary",
                    "host": getattr(settings, 'DATABASE_HOST', 'localhost'),
                    "port": getattr(settings, 'DATABASE_PORT', 5432),
                    "database": getattr(settings, 'DATABASE_NAME', 'techze_db'),
                    "user": getattr(settings, 'DATABASE_USER', 'postgres'),
                    "password": getattr(settings, 'DATABASE_PASSWORD', ''),
                    "weight": 1.0,
                    "is_primary": True
                }
            ]
            
            # Adicionar réplicas se configuradas
            replica_hosts = getattr(settings, 'DATABASE_REPLICA_HOSTS', [])
            for i, replica_host in enumerate(replica_hosts):
                db_nodes.append({
                    "id": f"replica_{i+1}",
                    "host": replica_host,
                    "port": getattr(settings, 'DATABASE_PORT', 5432),
                    "database": getattr(settings, 'DATABASE_NAME', 'techze_db'),
                    "user": getattr(settings, 'DATABASE_USER', 'postgres'),
                    "password": getattr(settings, 'DATABASE_PASSWORD', ''),
                    "weight": 0.5,
                    "is_primary": False
                })
            
            # Configuração do pool avançado
            pool_config = {
                "nodes": db_nodes,
                "strategy": "least_connections",  # Estratégia de balanceamento
                "max_connections_per_node": getattr(settings, 'DATABASE_MAX_CONNECTIONS', 20),
                "min_connections_per_node": getattr(settings, 'DATABASE_MIN_CONNECTIONS', 5),
                "connection_timeout": 30,
                "retry_attempts": 3,
                "circuit_breaker_threshold": 5,
                "circuit_breaker_timeout": 60,
                "enable_metrics": True
            }
            
            # Inicializar pool avançado
            await initialize_advanced_pool(pool_config)
            logger.info("✅ Connection pooling avançado inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar connection pooling avançado: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando TechZe Diagnostic Service...")
    
    # Fechar connection pooling avançado
    if ADVANCED_POOL_AVAILABLE:
        try:
            pool = await get_advanced_pool()
            if pool:
                await pool.close_all()
                logger.info("✅ Connection pooling avançado encerrado")
        except Exception as e:
            logger.error(f"❌ Erro ao encerrar connection pooling: {e}")

# Inicialização da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para diagnóstico completo de hardware e software",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de segurança e monitoramento
if SECURITY_MODULES_AVAILABLE:
    if getattr(settings, 'RATE_LIMIT_ENABLED', True):
        try:
            limiter, advanced_limiter = setup_rate_limiting(app, getattr(settings, 'REDIS_URL', None))
            logger.info("Rate limiting configurado")
        except Exception as e:
            logger.warning(f"Erro ao configurar rate limiting: {e}")

    if getattr(settings, 'PROMETHEUS_ENABLED', True):
        try:
            instrumentator = setup_monitoring(app)
            logger.info("Monitoramento Prometheus configurado")
        except Exception as e:
            logger.warning(f"Erro ao configurar monitoramento: {e}")

    if getattr(settings, 'SENTRY_DSN', None):
        try:
            error_tracker = setup_error_tracking(app, settings.SENTRY_DSN)
            logger.info("Error tracking Sentry configurado")
        except Exception as e:
            logger.warning(f"Erro ao configurar error tracking: {e}")

# Log de inicialização do sistema
# Endpoints do connection pooling avançado
if ADVANCED_POOL_AVAILABLE:
    @app.get("/api/v3/pool/metrics")
    async def get_pool_metrics():
        """Retorna métricas do connection pool"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            metrics = await pool.get_metrics()
            return {
                "status": "success",
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter métricas do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v3/pool/health")
    async def get_pool_health():
        """Retorna status de saúde do connection pool"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            health_status = await pool.health_check()
            return {
                "status": "healthy" if health_status["healthy"] else "unhealthy",
                "details": health_status,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao verificar saúde do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v3/pool/stats")
    async def get_pool_stats():
        """Retorna estatísticas detalhadas do pool"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            stats = await pool.get_detailed_stats()
            return {
                "status": "success",
                "stats": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Incluir rotas da API se disponíveis
if API_ROUTER_AVAILABLE:
    app.include_router(api_router, prefix=settings.API_V1_STR)
else:
    logger.warning("API routes not loaded - running in minimal mode")

# Incluir rotas da API v1 se disponíveis
if API_V1_ROUTER_AVAILABLE:
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)
else:
    logger.warning("API v1 routes not loaded - running in minimal mode")

# Incluir rotas da API Core (Consolidada) - PRIORIDADE
if API_CORE_ROUTER_AVAILABLE:
    app.include_router(core_api_router)
    logger.info("✅ API Core routes loaded - Consolidated API with all domains available")
else:
    logger.warning("API Core routes not loaded - falling back to legacy APIs")

# Incluir rotas da API v3 se disponíveis (Semana 3 - IA, ML e Automação) - DEPRECATED
if API_V3_ROUTER_AVAILABLE and not API_CORE_ROUTER_AVAILABLE:
    app.include_router(ai_endpoints.router, prefix="/api/v3")
    app.include_router(automation_endpoints.router, prefix="/api/v3")
    app.include_router(analytics_endpoints.router, prefix="/api/v3")
    app.include_router(chat_endpoints.router, prefix="/api/v3")
    app.include_router(performance_endpoints.router, prefix="/api/v3")
    
    # Incluir diagnostic endpoints
    try:
        from app.api.v3 import diagnostic_endpoints
        app.include_router(diagnostic_endpoints.router)
        logger.info("✅ API v3 Diagnostic endpoints loaded (DEPRECATED - use /api/core instead)")
    except ImportError as e:
        logger.warning(f"Diagnostic endpoints not available: {e}")
    
    logger.info("⚠️ API v3 routes loaded - DEPRECATED, please migrate to /api/core")
else:
    if API_CORE_ROUTER_AVAILABLE:
        logger.info("ℹ️ API v3 routes skipped - using consolidated API Core instead")
    else:
        logger.warning("API v3 routes not loaded - AI/ML features not available")

# Rotas básicas
@app.get("/", tags=["Root"])
async def root():
    """Rota raiz do serviço de diagnóstico."""
    return {
        "message": "Bem-vindo ao Serviço de Diagnóstico do TechZe",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else "disabled",
        "api": settings.API_V1_STR,
        "status": "running",
        "security_features": {
            "modules_available": SECURITY_MODULES_AVAILABLE,
            "rate_limiting": getattr(settings, 'RATE_LIMIT_ENABLED', True),
            "monitoring": getattr(settings, 'PROMETHEUS_ENABLED', True),
            "error_tracking": bool(getattr(settings, 'SENTRY_DSN', None))
        }
    }

# Rotas básicas de teste para auth
@app.get("/api/v1/auth/health", tags=["Auth"])
async def auth_health_test():
    """Health check básico para auth"""
    return {
        "status": "healthy",
        "service": "auth",
        "timestamp": datetime.now().isoformat(),
        "supabase_connected": True
    }

@app.post("/api/v1/auth/token", tags=["Auth"])
async def login_test(email: str, password: str):
    """Endpoint básico de login para teste"""
    # Login de desenvolvimento
    if email == "dev@techze.com" and password == "dev123":
        return {
            "access_token": "dev-token-123",
            "token_type": "bearer",
            "expires_in": 3600,
            "user_info": {
                "id": "dev-user-123",
                "email": email,
                "name": "Dev User",
                "role": "admin"
            }
        }
    else:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

# Rotas básicas de teste para auth
@app.get("/api/v1/auth/health", tags=["Auth"])
async def auth_health_test():
    """Health check básico para auth"""
    return {
        "status": "healthy",
        "service": "auth",
        "timestamp": datetime.now().isoformat(),
        "supabase_connected": True
    }

@app.post("/api/v1/auth/token", tags=["Auth"])
async def login_test(email: str, password: str):
    """Endpoint básico de login para teste"""
    # Login de desenvolvimento
    if email == "dev@techze.com" and password == "dev123":
        return {
            "access_token": "dev-token-123",
            "token_type": "bearer",
            "expires_in": 3600,
            "user_info": {
                "id": "dev-user-123",
                "email": email,
                "name": "Dev User",
                "role": "admin"
            }
        }
    else:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

@app.get("/health", tags=["Health"])
async def health_check():
    """Verificação de saúde do serviço."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": datetime.now().isoformat(),
        "service": "diagnostic-service",
        "environment": settings.ENVIRONMENT,
        "supabase_configured": bool(getattr(settings, 'SUPABASE_URL', None)),
        "api_router_available": API_ROUTER_AVAILABLE,
        "api_v1_router_available": API_V1_ROUTER_AVAILABLE,
        "api_v3_router_available": API_V3_ROUTER_AVAILABLE
    }

@app.get("/info", tags=["Info"])
async def service_info():
    """Informações detalhadas do serviço."""
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,        "api_v3_router_available": API_V3_ROUTER_AVAILABLE,        "environment": settings.ENVIRONMENT,
        "debug_mode": settings.DEBUG,
        "host": settings.HOST,
        "port": settings.PORT,
        "api_prefix": settings.API_V1_STR,
        "cors_origins": settings.BACKEND_CORS_ORIGINS,
        "features": {
            "api_router": API_ROUTER_AVAILABLE,
            "api_v3_ai_ml": API_V3_ROUTER_AVAILABLE,
            "analyzers": ANALYZERS_AVAILABLE,
            "supabase": bool(settings.SUPABASE_URL),
            "docs": settings.DEBUG,
            "security_modules": SECURITY_MODULES_AVAILABLE
        }
    }

# Endpoint básico de diagnóstico que funciona sem SQLAlchemy
@app.post("/api/v1/diagnostic/quick", tags=["Diagnostic"])
async def quick_diagnostic(request: Request):
    """Executa um diagnóstico rápido do sistema."""
    
    # Aplica decoradores de monitoramento se disponíveis
    if SECURITY_MODULES_AVAILABLE:
        try:
            # Registra início do diagnóstico
            techze_metrics.record_diagnostic_request("quick", "started")
            
            # Log de auditoria
            await audit_service.log_diagnostic_event(
                request=request,
                event_type=AuditEventType.DIAGNOSTIC_STARTED,
                success=True,
                details={"type": "quick"}
            )
        except Exception as e:
            logger.warning(f"Erro ao registrar métricas/auditoria: {e}")
    
    if not ANALYZERS_AVAILABLE:
        # Registra erro nas métricas se disponível
        if SECURITY_MODULES_AVAILABLE:
            try:
                techze_metrics.record_error("analyzers_unavailable", "diagnostic_quick", "high")
            except Exception:
                pass
        
        return {
            "status": "error",
            "message": "Analyzers not available",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Inicializa os analisadores
        cpu_analyzer = CPUAnalyzer()
        memory_analyzer = MemoryAnalyzer()
        disk_analyzer = DiskAnalyzer()
        network_analyzer = NetworkAnalyzer()
        system_info_service = SystemInfoService()
        
        # Executa análises
        cpu_result = cpu_analyzer.analyze()
        memory_result = memory_analyzer.analyze()
        disk_result = disk_analyzer.analyze()
        network_result = network_analyzer.analyze()
        system_info = system_info_service.collect_system_info()
        
        # Calcula health score
        scores = []
        for result in [cpu_result, memory_result, disk_result, network_result]:
            status = result.get("status", "error")
            if status == "healthy":
                scores.append(100)
            elif status == "warning":
                scores.append(70)
            elif status == "critical":
                scores.append(30)
            else:
                scores.append(50)
        
        health_score = int(sum(scores) / len(scores)) if scores else 50
        
        # Registra sucesso se módulos disponíveis
        if SECURITY_MODULES_AVAILABLE:
            try:
                techze_metrics.record_diagnostic_request("quick", "completed")
                
                # Log de auditoria para diagnóstico completo
                await audit_service.log_diagnostic_event(
                    request=request,
                    event_type=AuditEventType.DIAGNOSTIC_COMPLETED,
                    success=True,
                    details={
                        "health_score": health_score,
                        "components_analyzed": ["cpu", "memory", "disk", "network"]
                    }
                )
            except Exception as e:
                logger.warning(f"Erro ao registrar sucesso: {e}")
        
        result = {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "results": {
                "cpu": cpu_result,
                "memory": memory_result,
                "disk": disk_result,
                "network": network_result
            },
            "system_info": system_info
        }
        
        return result
        
    except Exception as e:
        logger.exception(f"Error in quick diagnostic: {str(e)}")
        
        # Registra erro se módulos disponíveis
        if SECURITY_MODULES_AVAILABLE:
            try:
                techze_metrics.record_diagnostic_request("quick", "error")
                techze_metrics.record_error(type(e).__name__, "diagnostic_quick", "high")
                
                # Log de auditoria para erro
                await audit_service.log_diagnostic_event(
                    request=request,
                    event_type=AuditEventType.DIAGNOSTIC_FAILED,
                    success=False,
                    error_message=str(e)
                )
            except Exception as audit_error:
                logger.warning(f"Erro ao registrar erro: {audit_error}")
        
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Novos endpoints para monitoramento avançado (Semana 2)
@app.get("/api/v1/monitoring/dashboard/operational", tags=["Monitoring"])
async def get_operational_dashboard():
    """Retorna dashboard operacional avançado"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Advanced monitoring not available"}
    
    try:
        dashboard = await advanced_monitoring.get_operational_dashboard()
        return dashboard
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard operacional: {e}")
        return {"error": str(e)}

@app.get("/api/v1/monitoring/dashboard/security", tags=["Monitoring"])
async def get_security_dashboard():
    """Retorna dashboard de segurança"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Advanced monitoring not available"}
    
    try:
        dashboard = await advanced_monitoring.get_security_dashboard()
        return dashboard
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard de segurança: {e}")
        return {"error": str(e)}

@app.get("/api/v1/monitoring/alerts", tags=["Monitoring"])
async def get_alerts():
    """Retorna alertas ativos"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Advanced monitoring not available"}
    
    try:
        alerts = advanced_monitoring.get_active_alerts()
        return {
            "alerts": alerts,
            "summary": advanced_monitoring.get_alert_summary(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter alertas: {e}")
        return {"error": str(e)}

@app.post("/api/v1/monitoring/alerts/{alert_id}/resolve", tags=["Monitoring"])
async def resolve_alert(alert_id: str):
    """Resolve um alerta específico"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Advanced monitoring not available"}
    
    try:
        resolved = advanced_monitoring.resolve_alert(alert_id)
        return {
            "resolved": resolved,
            "alert_id": alert_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao resolver alerta: {e}")
        return {"error": str(e)}

@app.get("/api/v1/cache/stats", tags=["Cache"])
async def get_cache_stats():
    """Retorna estatísticas do cache"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Cache manager not available"}
    
    try:
        stats = await cache_manager.get_cache_stats()
        return {
            "cache_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter stats do cache: {e}")
        return {"error": str(e)}

@app.post("/api/v1/cache/clear", tags=["Cache"])
async def clear_cache():
    """Limpa todo o cache"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Cache manager not available"}
    
    try:
        await cache_manager.redis_cache.clear()
        return {
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        return {"error": str(e)}

@app.post("/api/v1/cache/invalidate/{pattern}", tags=["Cache"])
async def invalidate_cache_pattern(pattern: str):
    """Invalida padrão específico do cache"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Cache manager not available"}
    
    try:
        await cache_manager.invalidate_pattern(pattern)
        return {
            "message": f"Pattern '{pattern}' invalidated successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao invalidar padrão: {e}")
        return {"error": str(e)}

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Health check detalhado com informações de todos os sistemas"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "diagnostic-service",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "components": {
            "api": {"status": "healthy", "details": "API responding"},
            "config": {"status": "healthy", "details": "Configuration loaded"},
        }
    }
    
    # Verifica componentes opcionais
    if SECURITY_MODULES_AVAILABLE:
        try:
            # Cache
            cache_stats = await cache_manager.get_cache_stats()
            health_data["components"]["cache"] = {
                "status": "healthy" if cache_stats else "degraded",
                "details": f"Redis: {'available' if cache_stats.get('redis_available') else 'unavailable'}"
            }
            
            # Monitoramento
            alert_summary = advanced_monitoring.get_alert_summary()
            critical_alerts = alert_summary.get("by_severity", {}).get("critical", 0)
            health_data["components"]["monitoring"] = {
                "status": "critical" if critical_alerts > 0 else "healthy",
                "details": f"Active alerts: {alert_summary.get('total_active', 0)}"
            }
            
        except Exception as e:
            health_data["components"]["advanced_systems"] = {
                "status": "error",
                "details": f"Error checking advanced systems: {e}"
            }
    
    # Verifica analyzers
    if ANALYZERS_AVAILABLE:
        health_data["components"]["analyzers"] = {
            "status": "healthy",
            "details": "System analyzers available"
        }
    else:
        health_data["components"]["analyzers"] = {
            "status": "degraded",
            "details": "System analyzers not available"
        }
    
    # Determina status geral
    component_statuses = [comp["status"] for comp in health_data["components"].values()]
    if "critical" in component_statuses:
        health_data["status"] = "critical"
    elif "error" in component_statuses:
        health_data["status"] = "error"
    elif "degraded" in component_statuses:
        health_data["status"] = "degraded"
    
    return health_data
@app.post("/api/v1/alerts/webhook", tags=["Alerts"])
async def alertmanager_webhook(request: Request):
    """Recebe webhooks do Alertmanager"""
    try:
        payload = await request.json()
        
        # Processa alertas
        alerts = payload.get("alerts", [])
        for alert in alerts:
            alert_name = alert.get("labels", {}).get("alertname", "Unknown")
            status = alert.get("status", "unknown")
            severity = alert.get("labels", {}).get("severity", "info")
            
            logger.info(f"Alerta recebido: {alert_name} - Status: {status} - Severity: {severity}")
            
            # Se temos monitoramento avançado disponível, processa o alerta
            if SECURITY_MODULES_AVAILABLE:
                try:
                    # Cria alerta no sistema de monitoramento
                    if status == "firing":
                        advanced_monitoring.create_alert(
                            alert_id=alert.get("fingerprint", f"{alert_name}_{int(time.time())}"),
                            title=alert_name,
                            description=alert.get("annotations", {}).get("description", ""),
                            severity=severity,
                            alert_type="system",
                            source="prometheus",
                            metadata=alert
                        )
                    elif status == "resolved":
                        # Tenta resolver o alerta
                        alert_id = alert.get("fingerprint")
                        if alert_id:
                            advanced_monitoring.resolve_alert(alert_id)
                except Exception as e:
                    logger.error(f"Erro ao processar alerta no sistema: {e}")
        
        return {
            "status": "success",
            "processed_alerts": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook do Alertmanager: {e}")
        return {"error": str(e)}, 500
# Manipulação de exceções
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "service": "diagnostic-service"
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "service": "diagnostic-service"
        },
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import time
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Imports da aplicação
from app.core.config import settings

# Imports do connection pooling avançado
try:
    from app.core.advanced_pool import AdvancedConnectionPool, initialize_advanced_pool, get_advanced_pool
    from app.core.advanced_pool_metrics import MetricsEnabledConnectionPool, create_metrics_enabled_pool
    from app.core.database_pool import pool_manager
    ADVANCED_POOL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Advanced pool modules not available: {e}")
    ADVANCED_POOL_AVAILABLE = False

# Imports dos novos módulos de segurança e monitoramento
try:
    from app.core.rate_limiter import setup_rate_limiting
    from app.core.monitoring import setup_monitoring, techze_metrics, monitor_diagnostic
    from app.core.error_tracking import setup_error_tracking, track_errors
    from app.core.audit import audit_service, AuditEventType, audit_endpoint
    from app.core.advanced_monitoring import advanced_monitoring
    from app.core.cache_manager import cache_manager
    SECURITY_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Security modules not available: {e}")
    SECURITY_MODULES_AVAILABLE = False

# Import condicional dos routers para evitar erros em caso de dependências faltantes
try:
    from app.api.router import api_router
    API_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API router not available: {e}")
    API_ROUTER_AVAILABLE = False

try:
    from app.api.v1.router import api_v1_router
    API_V1_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API v1 router not available: {e}")
    API_V1_ROUTER_AVAILABLE = False

# Import da API v3 (Semana 3 - IA, ML e Automação)
try:
    from app.api.v3 import ai_endpoints, automation_endpoints, analytics_endpoints, chat_endpoints
    from app.api.v3 import performance_endpoints
    API_V3_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API v3 router not available: {e}")
    API_V3_ROUTER_AVAILABLE = False

# Import da API Core (Consolidada)
try:
    from app.api.core.router import api_router as core_api_router
    API_CORE_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API Core router not available: {e}")
    API_CORE_ROUTER_AVAILABLE = False

# Import dos analisadores para funcionalidade básica
try:
    from app.services.analyzers import CPUAnalyzer, MemoryAnalyzer, DiskAnalyzer, NetworkAnalyzer
    from app.services.system_info_service import SystemInfoService
    ANALYZERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Analyzers not available: {e}")
    ANALYZERS_AVAILABLE = False

# Função de ciclo de vida da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Iniciando TechZe Diagnostic Service...")
    
    # Inicializar connection pooling avançado
    if ADVANCED_POOL_AVAILABLE:
        try:
            # Configuração dos nós do banco de dados
            db_nodes = [
                {
                    "id": "primary",
                    "host": getattr(settings, 'DATABASE_HOST', 'localhost'),
                    "port": getattr(settings, 'DATABASE_PORT', 5432),
                    "database": getattr(settings, 'DATABASE_NAME', 'techze_db'),
                    "user": getattr(settings, 'DATABASE_USER', 'postgres'),
                    "password": getattr(settings, 'DATABASE_PASSWORD', ''),
                    "weight": 1.0,
                    "is_primary": True
                }
            ]
            
            # Adicionar réplicas se configuradas
            replica_hosts = getattr(settings, 'DATABASE_REPLICA_HOSTS', [])
            for i, replica_host in enumerate(replica_hosts):
                db_nodes.append({
                    "id": f"replica_{i+1}",
                    "host": replica_host,
                    "port": getattr(settings, 'DATABASE_PORT', 5432),
                    "database": getattr(settings, 'DATABASE_NAME', 'techze_db'),
                    "user": getattr(settings, 'DATABASE_USER', 'postgres'),
                    "password": getattr(settings, 'DATABASE_PASSWORD', ''),
                    "weight": 0.5,
                    "is_primary": False
                })
            
            # Configuração do pool avançado
            pool_config = {
                "nodes": db_nodes,
                "strategy": "least_connections",  # Estratégia de balanceamento
                "max_connections_per_node": getattr(settings, 'DATABASE_MAX_CONNECTIONS', 20),
                "min_connections_per_node": getattr(settings, 'DATABASE_MIN_CONNECTIONS', 5),
                "connection_timeout": 30,
                "retry_attempts": 3,
                "circuit_breaker_threshold": 5,
                "circuit_breaker_timeout": 60,
                "enable_metrics": True
            }
            
            # Inicializar pool avançado
            await initialize_advanced_pool(pool_config)
            logger.info("✅ Connection pooling avançado inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar connection pooling avançado: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando TechZe Diagnostic Service...")
    
    # Fechar connection pooling avançado
    if ADVANCED_POOL_AVAILABLE:
        try:
            pool = await get_advanced_pool()
            if pool:
                await pool.close_all()
                logger.info("✅ Connection pooling avançado encerrado")
        except Exception as e:
            logger.error(f"❌ Erro ao encerrar connection pooling: {e}")

# Inicialização da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para diagnóstico completo de hardware e software",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de segurança e monitoramento
if SECURITY_MODULES_AVAILABLE:
    if getattr(settings, 'RATE_LIMIT_ENABLED', True):
        try:
            limiter, advanced_limiter = setup_rate_limiting(app, getattr(settings, 'REDIS_URL', None))
            logger.info("Rate limiting configurado")
        except Exception as e:
            logger.warning(f"Erro ao configurar rate limiting: {e}")

    if getattr(settings, 'PROMETHEUS_ENABLED', True):
        try:
            instrumentator = setup_monitoring(app)
            logger.info("Monitoramento Prometheus configurado")
        except Exception as e:
            logger.warning(f"Erro ao configurar monitoramento: {e}")

    if getattr(settings, 'SENTRY_DSN', None):
        try:
            error_tracker = setup_error_tracking(app, settings.SENTRY_DSN)
            logger.info("Error tracking Sentry configurado")
        except Exception as e:
            logger.warning(f"Erro ao configurar error tracking: {e}")

# Log de inicialização do sistema
# Endpoints do connection pooling avançado
if ADVANCED_POOL_AVAILABLE:
    @app.get("/api/v3/pool/metrics")
    async def get_pool_metrics():
        """Retorna métricas do connection pool"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            metrics = await pool.get_metrics()
            return {
                "status": "success",
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter métricas do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v3/pool/health")
    async def get_pool_health():
        """Retorna status de saúde do connection pool"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            health_status = await pool.health_check()
            return {
                "status": "healthy" if health_status["healthy"] else "unhealthy",
                "details": health_status,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao verificar saúde do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v3/pool/stats")
    async def get_pool_stats():
        """Retorna estatísticas detalhadas do pool"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            stats = await pool.get_detailed_stats()
            return {
                "status": "success",
                "stats": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))

# Incluir rotas da API se disponíveis
if API_ROUTER_AVAILABLE:
    app.include_router(api_router, prefix=settings.API_V1_STR)
else:
    logger.warning("API routes not loaded - running in minimal mode")

# Incluir rotas da API v1 se disponíveis
if API_V1_ROUTER_AVAILABLE:
    app.include_router(api_v1_router, prefix=settings.API_V1_STR)
else:
    logger.warning("API v1 routes not loaded - running in minimal mode")

# Incluir rotas da API Core (Consolidada) - PRIORIDADE
if API_CORE_ROUTER_AVAILABLE:
    app.include_router(core_api_router)
    logger.info("✅ API Core routes loaded - Consolidated API with all domains available")
else:
    logger.warning("API Core routes not loaded - falling back to legacy APIs")

# Incluir rotas da API v3 se disponíveis (Semana 3 - IA, ML e Automação) - DEPRECATED
if API_V3_ROUTER_AVAILABLE and not API_CORE_ROUTER_AVAILABLE:
    app.include_router(ai_endpoints.router, prefix="/api/v3")
    app.include_router(automation_endpoints.router, prefix="/api/v3")
    app.include_router(analytics_endpoints.router, prefix="/api/v3")
    app.include_router(chat_endpoints.router, prefix="/api/v3")
    app.include_router(performance_endpoints.router, prefix="/api/v3")
    
    # Incluir diagnostic endpoints
    try:
        from app.api.v3 import diagnostic_endpoints
        app.include_router(diagnostic_endpoints.router)
        logger.info("✅ API v3 Diagnostic endpoints loaded (DEPRECATED - use /api/core instead)")
    except ImportError as e:
        logger.warning(f"Diagnostic endpoints not available: {e}")
    
    logger.info("⚠️ API v3 routes loaded - DEPRECATED, please migrate to /api/core")
else:
    if API_CORE_ROUTER_AVAILABLE:
        logger.info("ℹ️ API v3 routes skipped - using consolidated API Core instead")
    else:
        logger.warning("API v3 routes not loaded - AI/ML features not available")

# Rotas básicas
@app.get("/", tags=["Root"])
async def root():
    """Rota raiz do serviço de diagnóstico."""
    return {
        "message": "Bem-vindo ao Serviço de Diagnóstico do TechZe",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs" if settings.DEBUG else "disabled",
        "api": settings.API_V1_STR,
        "status": "running",
        "security_features": {
            "modules_available": SECURITY_MODULES_AVAILABLE,
            "rate_limiting": getattr(settings, 'RATE_LIMIT_ENABLED', True),
            "monitoring": getattr(settings, 'PROMETHEUS_ENABLED', True),
            "error_tracking": bool(getattr(settings, 'SENTRY_DSN', None))
        }
    }

# Rotas básicas de teste para auth
@app.get("/api/v1/auth/health", tags=["Auth"])
async def auth_health_test():
    """Health check básico para auth"""
    return {
        "status": "healthy",
        "service": "auth",
        "timestamp": datetime.now().isoformat(),
        "supabase_connected": True
    }

@app.post("/api/v1/auth/token", tags=["Auth"])
async def login_test(email: str, password: str):
    """Endpoint básico de login para teste"""
    # Login de desenvolvimento
    if email == "dev@techze.com" and password == "dev123":
        return {
            "access_token": "dev-token-123",
            "token_type": "bearer",
            "expires_in": 3600,
            "user_info": {
                "id": "dev-user-123",
                "email": email,
                "name": "Dev User",
                "role": "admin"
            }
        }
    else:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

# Rotas básicas de teste para auth
@app.get("/api/v1/auth/health", tags=["Auth"])
async def auth_health_test():
    """Health check básico para auth"""
    return {
        "status": "healthy",
        "service": "auth",
        "timestamp": datetime.now().isoformat(),
        "supabase_connected": True
    }

@app.post("/api/v1/auth/token", tags=["Auth"])
async def login_test(email: str, password: str):
    """Endpoint básico de login para teste"""
    # Login de desenvolvimento
    if email == "dev@techze.com" and password == "dev123":
        return {
            "access_token": "dev-token-123",
            "token_type": "bearer",
            "expires_in": 3600,
            "user_info": {
                "id": "dev-user-123",
                "email": email,
                "name": "Dev User",
                "role": "admin"
            }
        }
    else:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas"
        )

@app.get("/health", tags=["Health"])
async def health_check():
    """Verificação de saúde do serviço."""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "timestamp": datetime.now().isoformat(),
        "service": "diagnostic-service",
        "environment": settings.ENVIRONMENT,
        "supabase_configured": bool(getattr(settings, 'SUPABASE_URL', None)),
        "api_router_available": API_ROUTER_AVAILABLE,
        "api_v1_router_available": API_V1_ROUTER_AVAILABLE,
        "api_v3_router_available": API_V3_ROUTER_AVAILABLE
    }

@app.get("/info", tags=["Info"])
async def service_info():
    """Informações detalhadas do serviço."""
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,        "api_v3_router_available": API_V3_ROUTER_AVAILABLE,        "environment": settings.ENVIRONMENT,
        "debug_mode": settings.DEBUG,
        "host": settings.HOST,
        "port": settings.PORT,
        "api_prefix": settings.API_V1_STR,
        "cors_origins": settings.BACKEND_CORS_ORIGINS,
        "features": {
            "api_router": API_ROUTER_AVAILABLE,
            "api_v3_ai_ml": API_V3_ROUTER_AVAILABLE,
            "analyzers": ANALYZERS_AVAILABLE,
            "supabase": bool(settings.SUPABASE_URL),
            "docs": settings.DEBUG,
            "security_modules": SECURITY_MODULES_AVAILABLE
        }
    }

# Endpoint básico de diagnóstico que funciona sem SQLAlchemy
@app.post("/api/v1/diagnostic/quick", tags=["Diagnostic"])
async def quick_diagnostic(request: Request):
    """Executa um diagnóstico rápido do sistema."""
    
    # Aplica decoradores de monitoramento se disponíveis
    if SECURITY_MODULES_AVAILABLE:
        try:
            # Registra início do diagnóstico
            techze_metrics.record_diagnostic_request("quick", "started")
            
            # Log de auditoria
            await audit_service.log_diagnostic_event(
                request=request,
                event_type=AuditEventType.DIAGNOSTIC_STARTED,
                success=True,
                details={"type": "quick"}
            )
        except Exception as e:
            logger.warning(f"Erro ao registrar métricas/auditoria: {e}")
    
    if not ANALYZERS_AVAILABLE:
        # Registra erro nas métricas se disponível
        if SECURITY_MODULES_AVAILABLE:
            try:
                techze_metrics.record_error("analyzers_unavailable", "diagnostic_quick", "high")
            except Exception:
                pass
        
        return {
            "status": "error",
            "message": "Analyzers not available",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Inicializa os analisadores
        cpu_analyzer = CPUAnalyzer()
        memory_analyzer = MemoryAnalyzer()
        disk_analyzer = DiskAnalyzer()
        network_analyzer = NetworkAnalyzer()
        system_info_service = SystemInfoService()
        
        # Executa análises
        cpu_result = cpu_analyzer.analyze()
        memory_result = memory_analyzer.analyze()
        disk_result = disk_analyzer.analyze()
        network_result = network_analyzer.analyze()
        system_info = system_info_service.collect_system_info()
        
        # Calcula health score
        scores = []
        for result in [cpu_result, memory_result, disk_result, network_result]:
            status = result.get("status", "error")
            if status == "healthy":
                scores.append(100)
            elif status == "warning":
                scores.append(70)
            elif status == "critical":
                scores.append(30)
            else:
                scores.append(50)
        
        health_score = int(sum(scores) / len(scores)) if scores else 50
        
        # Registra sucesso se módulos disponíveis
        if SECURITY_MODULES_AVAILABLE:
            try:
                techze_metrics.record_diagnostic_request("quick", "completed")
                
                # Log de auditoria para diagnóstico completo
                await audit_service.log_diagnostic_event(
                    request=request,
                    event_type=AuditEventType.DIAGNOSTIC_COMPLETED,
                    success=True,
                    details={
                        "health_score": health_score,
                        "components_analyzed": ["cpu", "memory", "disk", "network"]
                    }
                )
            except Exception as e:
                logger.warning(f"Erro ao registrar sucesso: {e}")
        
        result = {
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "results": {
                "cpu": cpu_result,
                "memory": memory_result,
                "disk": disk_result,
                "network": network_result
            },
            "system_info": system_info
        }
        
        return result
        
    except Exception as e:
        logger.exception(f"Error in quick diagnostic: {str(e)}")
        
        # Registra erro se módulos disponíveis
        if SECURITY_MODULES_AVAILABLE:
            try:
                techze_metrics.record_diagnostic_request("quick", "error")
                techze_metrics.record_error(type(e).__name__, "diagnostic_quick", "high")
                
                # Log de auditoria para erro
                await audit_service.log_diagnostic_event(
                    request=request,
                    event_type=AuditEventType.DIAGNOSTIC_FAILED,
                    success=False,
                    error_message=str(e)
                )
            except Exception as audit_error:
                logger.warning(f"Erro ao registrar erro: {audit_error}")
        
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Novos endpoints para monitoramento avançado (Semana 2)
@app.get("/api/v1/monitoring/dashboard/operational", tags=["Monitoring"])
async def get_operational_dashboard():
    """Retorna dashboard operacional avançado"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Advanced monitoring not available"}
    
    try:
        dashboard = await advanced_monitoring.get_operational_dashboard()
        return dashboard
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard operacional: {e}")
        return {"error": str(e)}

@app.get("/api/v1/monitoring/dashboard/security", tags=["Monitoring"])
async def get_security_dashboard():
    """Retorna dashboard de segurança"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Advanced monitoring not available"}
    
    try:
        dashboard = await advanced_monitoring.get_security_dashboard()
        return dashboard
    except Exception as e:
        logger.error(f"Erro ao gerar dashboard de segurança: {e}")
        return {"error": str(e)}

@app.get("/api/v1/monitoring/alerts", tags=["Monitoring"])
async def get_alerts():
    """Retorna alertas ativos"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Advanced monitoring not available"}
    
    try:
        alerts = advanced_monitoring.get_active_alerts()
        return {
            "alerts": alerts,
            "summary": advanced_monitoring.get_alert_summary(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter alertas: {e}")
        return {"error": str(e)}

@app.post("/api/v1/monitoring/alerts/{alert_id}/resolve", tags=["Monitoring"])
async def resolve_alert(alert_id: str):
    """Resolve um alerta específico"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Advanced monitoring not available"}
    
    try:
        resolved = advanced_monitoring.resolve_alert(alert_id)
        return {
            "resolved": resolved,
            "alert_id": alert_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao resolver alerta: {e}")
        return {"error": str(e)}

@app.get("/api/v1/cache/stats", tags=["Cache"])
async def get_cache_stats():
    """Retorna estatísticas do cache"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Cache manager not available"}
    
    try:
        stats = await cache_manager.get_cache_stats()
        return {
            "cache_stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao obter stats do cache: {e}")
        return {"error": str(e)}

@app.post("/api/v1/cache/clear", tags=["Cache"])
async def clear_cache():
    """Limpa todo o cache"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Cache manager not available"}
    
    try:
        await cache_manager.redis_cache.clear()
        return {
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao limpar cache: {e}")
        return {"error": str(e)}

@app.post("/api/v1/cache/invalidate/{pattern}", tags=["Cache"])
async def invalidate_cache_pattern(pattern: str):
    """Invalida padrão específico do cache"""
    if not SECURITY_MODULES_AVAILABLE:
        return {"error": "Cache manager not available"}
    
    try:
        await cache_manager.invalidate_pattern(pattern)
        return {
            "message": f"Pattern '{pattern}' invalidated successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Erro ao invalidar padrão: {e}")
        return {"error": str(e)}

@app.get("/health/detailed", tags=["Health"])
async def detailed_health_check():
    """Health check detalhado com informações de todos os sistemas"""
    health_data = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "diagnostic-service",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "components": {
            "api": {"status": "healthy", "details": "API responding"},
            "config": {"status": "healthy", "details": "Configuration loaded"},
        }
    }
    
    # Verifica componentes opcionais
    if SECURITY_MODULES_AVAILABLE:
        try:
            # Cache
            cache_stats = await cache_manager.get_cache_stats()
            health_data["components"]["cache"] = {
                "status": "healthy" if cache_stats else "degraded",
                "details": f"Redis: {'available' if cache_stats.get('redis_available') else 'unavailable'}"
            }
            
            # Monitoramento
            alert_summary = advanced_monitoring.get_alert_summary()
            critical_alerts = alert_summary.get("by_severity", {}).get("critical", 0)
            health_data["components"]["monitoring"] = {
                "status": "critical" if critical_alerts > 0 else "healthy",
                "details": f"Active alerts: {alert_summary.get('total_active', 0)}"
            }
            
        except Exception as e:
            health_data["components"]["advanced_systems"] = {
                "status": "error",
                "details": f"Error checking advanced systems: {e}"
            }
    
    # Verifica analyzers
    if ANALYZERS_AVAILABLE:
        health_data["components"]["analyzers"] = {
            "status": "healthy",
            "details": "System analyzers available"
        }
    else:
        health_data["components"]["analyzers"] = {
            "status": "degraded",
            "details": "System analyzers not available"
        }
    
    # Determina status geral
    component_statuses = [comp["status"] for comp in health_data["components"].values()]
    if "critical" in component_statuses:
        health_data["status"] = "critical"
    elif "error" in component_statuses:
        health_data["status"] = "error"
    elif "degraded" in component_statuses:
        health_data["status"] = "degraded"
    
    return health_data
@app.post("/api/v1/alerts/webhook", tags=["Alerts"])
async def alertmanager_webhook(request: Request):
    """Recebe webhooks do Alertmanager"""
    try:
        payload = await request.json()
        
        # Processa alertas
        alerts = payload.get("alerts", [])
        for alert in alerts:
            alert_name = alert.get("labels", {}).get("alertname", "Unknown")
            status = alert.get("status", "unknown")
            severity = alert.get("labels", {}).get("severity", "info")
            
            logger.info(f"Alerta recebido: {alert_name} - Status: {status} - Severity: {severity}")
            
            # Se temos monitoramento avançado disponível, processa o alerta
            if SECURITY_MODULES_AVAILABLE:
                try:
                    # Cria alerta no sistema de monitoramento
                    if status == "firing":
                        advanced_monitoring.create_alert(
                            alert_id=alert.get("fingerprint", f"{alert_name}_{int(time.time())}"),
                            title=alert_name,
                            description=alert.get("annotations", {}).get("description", ""),
                            severity=severity,
                            alert_type="system",
                            source="prometheus",
                            metadata=alert
                        )
                    elif status == "resolved":
                        # Tenta resolver o alerta
                        alert_id = alert.get("fingerprint")
                        if alert_id:
                            advanced_monitoring.resolve_alert(alert_id)
                except Exception as e:
                    logger.error(f"Erro ao processar alerta no sistema: {e}")
        
        return {
            "status": "success",
            "processed_alerts": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao processar webhook do Alertmanager: {e}")
        return {"error": str(e)}, 500
# Manipulação de exceções
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "timestamp": datetime.now().isoformat(),
            "service": "diagnostic-service"
        },
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat(),
            "service": "diagnostic-service"
        },
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import time
import logging
from datetime import datetime

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Imports da aplicação
from app.core.config import settings

# Imports do connection pooling avançado
try:
    from app.core.advanced_pool import AdvancedConnectionPool, initialize_advanced_pool, get_advanced_pool
    from app.core.advanced_pool_metrics import MetricsEnabledConnectionPool, create_metrics_enabled_pool
    from app.core.database_pool import pool_manager
    ADVANCED_POOL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Advanced pool modules not available: {e}")
    ADVANCED_POOL_AVAILABLE = False

# Imports dos novos módulos de segurança e monitoramento
try:
    from app.core.rate_limiter import setup_rate_limiting
    from app.core.monitoring import setup_monitoring, techze_metrics, monitor_diagnostic
    from app.core.error_tracking import setup_error_tracking, track_errors
    from app.core.audit import audit_service, AuditEventType, audit_endpoint
    from app.core.advanced_monitoring import advanced_monitoring
    from app.core.cache_manager import cache_manager
    SECURITY_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Security modules not available: {e}")
    SECURITY_MODULES_AVAILABLE = False

# Import condicional dos routers para evitar erros em caso de dependências faltantes
try:
    from app.api.router import api_router
    API_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API router not available: {e}")
    API_ROUTER_AVAILABLE = False

try:
    from app.api.v1.router import api_v1_router
    API_V1_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API v1 router not available: {e}")
    API_V1_ROUTER_AVAILABLE = False

# Import da API v3 (Semana 3 - IA, ML e Automação)
try:
    from app.api.v3 import ai_endpoints, automation_endpoints, analytics_endpoints, chat_endpoints
    from app.api.v3 import performance_endpoints
    API_V3_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API v3 router not available: {e}")
    API_V3_ROUTER_AVAILABLE = False

# Import da API Core (Consolidada)
try:
    from app.api.core.router import api_router as core_api_router
    API_CORE_ROUTER_AVAILABLE = True
except ImportError as e:
    logger.warning(f"API Core router not available: {e}")
    API_CORE_ROUTER_AVAILABLE = False

# Import dos analisadores para funcionalidade básica
try:
    from app.services.analyzers import CPUAnalyzer, MemoryAnalyzer, DiskAnalyzer, NetworkAnalyzer
    from app.services.system_info_service import SystemInfoService
    ANALYZERS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Analyzers not available: {e}")
    ANALYZERS_AVAILABLE = False

# Função de ciclo de vida da aplicação
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Iniciando TechZe Diagnostic Service...")
    
    # Inicializar connection pooling avançado
    if ADVANCED_POOL_AVAILABLE:
        try:
            # Configuração dos nós do banco de dados
            db_nodes = [
                {
                    "id": "primary",
                    "host": getattr(settings, 'DATABASE_HOST', 'localhost'),
                    "port": getattr(settings, 'DATABASE_PORT', 5432),
                    "database": getattr(settings, 'DATABASE_NAME', 'techze_db'),
                    "user": getattr(settings, 'DATABASE_USER', 'postgres'),
                    "password": getattr(settings, 'DATABASE_PASSWORD', ''),
                    "weight": 1.0,
                    "is_primary": True
                }
            ]
            
            # Adicionar réplicas se configuradas
            replica_hosts = getattr(settings, 'DATABASE_REPLICA_HOSTS', [])
            for i, replica_host in enumerate(replica_hosts):
                db_nodes.append({
                    "id": f"replica_{i+1}",
                    "host": replica_host,
                    "port": getattr(settings, 'DATABASE_PORT', 5432),
                    "database": getattr(settings, 'DATABASE_NAME', 'techze_db'),
                    "user": getattr(settings, 'DATABASE_USER', 'postgres'),
                    "password": getattr(settings, 'DATABASE_PASSWORD', ''),
                    "weight": 0.5,
                    "is_primary": False
                })
            
            # Configuração do pool avançado
            pool_config = {
                "nodes": db_nodes,
                "strategy": "least_connections",  # Estratégia de balanceamento
                "max_connections_per_node": getattr(settings, 'DATABASE_MAX_CONNECTIONS', 20),
                "min_connections_per_node": getattr(settings, 'DATABASE_MIN_CONNECTIONS', 5),
                "connection_timeout": 30,
                "retry_attempts": 3,
                "circuit_breaker_threshold": 5,
                "circuit_breaker_timeout": 60,
                "enable_metrics": True
            }
            
            # Inicializar pool avançado
            await initialize_advanced_pool(pool_config)
            logger.info("✅ Connection pooling avançado inicializado")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar connection pooling avançado: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando TechZe Diagnostic Service...")
    
    # Fechar connection pooling avançado
    if ADVANCED_POOL_AVAILABLE:
        try:
            pool = await get_advanced_pool()
            if pool:
                await pool.close_all()
                logger.info("✅ Connection pooling avançado encerrado")
        except Exception as e:
            logger.error(f"❌ Erro ao encerrar connection pooling: {e}")

# Inicialização da aplicação FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API para diagnóstico completo de hardware e software",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de segurança e monitoramento
if SECURITY_MODULES_AVAILABLE:
    if getattr(settings, 'RATE_LIMIT_ENABLED', True):
        try:
            limiter, advanced_limiter = setup_rate_limiting(app, getattr(settings, 'REDIS_URL', None))
            logger.info("Rate limiting configurado")
        except Exception as e:
            logger.warning(f"Erro ao configurar rate limiting: {e}")

    if getattr(settings, 'PROMETHEUS_ENABLED', True):
        try:
            instrumentator = setup_monitoring(app)
            logger.info("Monitoramento Prometheus configurado")
        except Exception as e:
            logger.warning(f"Erro ao configurar monitoramento: {e}")

    if getattr(settings, 'SENTRY_DSN', None):
        try:
            error_tracker = setup_error_tracking(app, settings.SENTRY_DSN)
            logger.info("Error tracking Sentry configurado")
        except Exception as e:
            logger.warning(f"Erro ao configurar error tracking: {e}")

# Log de inicialização do sistema
# Endpoints do connection pooling avançado
if ADVANCED_POOL_AVAILABLE:
    @app.get("/api/v3/pool/metrics")
    async def get_pool_metrics():
        """Retorna métricas do connection pool"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            metrics = await pool.get_metrics()
            return {
                "status": "success",
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter métricas do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v3/pool/health")
    async def get_pool_health():
        """Retorna status de saúde do connection pool"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            health_status = await pool.health_check()
            return {
                "status": "healthy" if health_status["healthy"] else "unhealthy",
                "details": health_status,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao verificar saúde do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v3/pool/stats")
    async def get_pool_stats():
        """Retorna estatísticas detalhadas do pool"""
        try:
            pool = await get_advanced_pool()
            if not pool:
                raise HTTPException(status_code=503, detail="Pool não inicializado")
            
            stats = await pool.get_detailed_stats()
            return {
                "status": "success",
                "stats": stats,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do pool: {e}")
            raise HTTPException(status_code=500, detail=str(e))