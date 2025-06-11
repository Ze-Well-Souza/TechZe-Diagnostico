#!/usr/bin/env python3
"""
Endpoints de Integração - API Core

Gerencia a comunicação entre diferentes serviços e sistemas externos.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone
from enum import Enum
import asyncio
import httpx
import json

# Router para integração
integration_router = APIRouter(tags=["Integration"])

# Modelos de dados
class ServiceType(str, Enum):
    """Tipos de serviços disponíveis"""
    DIAGNOSTIC = "diagnostic"
    MONITORING = "monitoring"
    NOTIFICATION = "notification"
    EXTERNAL_API = "external_api"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"

class IntegrationStatus(str, Enum):
    """Status de integração"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    MAINTENANCE = "maintenance"

class ServiceConfig(BaseModel):
    """Configuração de serviço"""
    name: str = Field(..., description="Nome do serviço")
    type: ServiceType = Field(..., description="Tipo do serviço")
    endpoint: str = Field(..., description="URL do endpoint")
    auth_type: Optional[str] = Field(None, description="Tipo de autenticação")
    auth_config: Optional[Dict[str, Any]] = Field(None, description="Configuração de autenticação")
    timeout: int = Field(30, description="Timeout em segundos")
    retry_attempts: int = Field(3, description="Tentativas de retry")
    health_check_path: Optional[str] = Field(None, description="Caminho para health check")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Metadados adicionais")

class ServiceStatus(BaseModel):
    """Status de um serviço"""
    service_id: str
    name: str
    type: ServiceType
    status: IntegrationStatus
    last_check: datetime
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    uptime_percentage: Optional[float] = None

class WebhookConfig(BaseModel):
    """Configuração de webhook"""
    name: str = Field(..., description="Nome do webhook")
    url: str = Field(..., description="URL de destino")
    events: List[str] = Field(..., description="Eventos que disparam o webhook")
    secret: Optional[str] = Field(None, description="Chave secreta para validação")
    headers: Optional[Dict[str, str]] = Field(None, description="Headers customizados")
    active: bool = Field(True, description="Se o webhook está ativo")

class IntegrationRequest(BaseModel):
    """Requisição de integração"""
    service_id: str = Field(..., description="ID do serviço")
    method: str = Field("GET", description="Método HTTP")
    path: str = Field("/", description="Caminho da requisição")
    headers: Optional[Dict[str, str]] = Field(None, description="Headers da requisição")
    body: Optional[Dict[str, Any]] = Field(None, description="Corpo da requisição")
    params: Optional[Dict[str, str]] = Field(None, description="Parâmetros da query")

class IntegrationResponse(BaseModel):
    """Resposta de integração"""
    success: bool
    status_code: Optional[int] = None
    data: Optional[Any] = None
    error: Optional[str] = None
    response_time: float
    timestamp: datetime

class DataSyncConfig(BaseModel):
    """Configuração de sincronização de dados"""
    source_service: str = Field(..., description="Serviço de origem")
    target_service: str = Field(..., description="Serviço de destino")
    sync_type: str = Field(..., description="Tipo de sincronização (real_time, batch, scheduled)")
    data_mapping: Dict[str, str] = Field(..., description="Mapeamento de campos")
    schedule: Optional[str] = Field(None, description="Agendamento (cron format)")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtros de dados")
    active: bool = Field(True, description="Se a sincronização está ativa")

# Simulação de armazenamento em memória
services_registry = {}
webhooks_registry = {}
sync_configs = {}
integration_logs = []

# Endpoints de gerenciamento de serviços
@integration_router.post("/services", response_model=Dict[str, str])
async def register_service(config: ServiceConfig):
    """Registra um novo serviço"""
    service_id = f"{config.type}_{config.name}_{len(services_registry) + 1}"
    
    services_registry[service_id] = {
        "id": service_id,
        "config": config.dict(),
        "status": IntegrationStatus.PENDING,
        "registered_at": datetime.now(timezone.utc),
        "last_check": None,
        "stats": {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0.0
        }
    }
    
    return {
        "service_id": service_id,
        "message": f"Serviço {config.name} registrado com sucesso",
        "status": "registered"
    }

@integration_router.get("/services", response_model=List[ServiceStatus])
async def list_services():
    """Lista todos os serviços registrados"""
    services = []
    
    for service_id, service_data in services_registry.items():
        config = service_data["config"]
        
        # Calcular uptime
        uptime = 95.5 if service_data["status"] == IntegrationStatus.ACTIVE else 0.0
        
        services.append(ServiceStatus(
            service_id=service_id,
            name=config["name"],
            type=config["type"],
            status=service_data["status"],
            last_check=service_data["last_check"] or datetime.now(timezone.utc),
            response_time=service_data["stats"]["avg_response_time"],
            uptime_percentage=uptime
        ))
    
    return services

@integration_router.get("/services/{service_id}", response_model=Dict[str, Any])
async def get_service(service_id: str):
    """Obtém detalhes de um serviço específico"""
    if service_id not in services_registry:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    return services_registry[service_id]

@integration_router.put("/services/{service_id}")
async def update_service(service_id: str, config: ServiceConfig):
    """Atualiza configuração de um serviço"""
    if service_id not in services_registry:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    services_registry[service_id]["config"] = config.dict()
    services_registry[service_id]["updated_at"] = datetime.now(timezone.utc)
    
    return {"message": "Serviço atualizado com sucesso"}

@integration_router.delete("/services/{service_id}")
async def unregister_service(service_id: str):
    """Remove um serviço do registro"""
    if service_id not in services_registry:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    del services_registry[service_id]
    
    return {"message": "Serviço removido com sucesso"}

# Endpoints de comunicação
@integration_router.post("/request", response_model=IntegrationResponse)
async def make_integration_request(request: IntegrationRequest):
    """Faz uma requisição para um serviço integrado"""
    if request.service_id not in services_registry:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    service = services_registry[request.service_id]
    config = service["config"]
    
    start_time = datetime.now(timezone.utc)
    
    try:
        # Simular requisição HTTP
        async with httpx.AsyncClient(timeout=config["timeout"]) as client:
            url = f"{config['endpoint']}{request.path}"
            
            response = await client.request(
                method=request.method,
                url=url,
                headers=request.headers or {},
                params=request.params or {},
                json=request.body if request.body else None
            )
            
            response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            # Atualizar estatísticas
            service["stats"]["total_requests"] += 1
            if response.status_code < 400:
                service["stats"]["successful_requests"] += 1
                service["status"] = IntegrationStatus.ACTIVE
            else:
                service["stats"]["failed_requests"] += 1
            
            # Atualizar tempo médio de resposta
            total_requests = service["stats"]["total_requests"]
            current_avg = service["stats"]["avg_response_time"]
            service["stats"]["avg_response_time"] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
            
            service["last_check"] = datetime.now(timezone.utc)
            
            return IntegrationResponse(
                success=response.status_code < 400,
                status_code=response.status_code,
                data=response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text,
                response_time=response_time,
                timestamp=datetime.now(timezone.utc)
            )
            
    except Exception as e:
        response_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        # Atualizar estatísticas de erro
        service["stats"]["total_requests"] += 1
        service["stats"]["failed_requests"] += 1
        service["status"] = IntegrationStatus.ERROR
        service["last_check"] = datetime.now(timezone.utc)
        
        return IntegrationResponse(
            success=False,
            error=str(e),
            response_time=response_time,
            timestamp=datetime.now(timezone.utc)
        )

# Endpoints de health check
@integration_router.post("/services/{service_id}/health-check")
async def check_service_health(service_id: str):
    """Verifica a saúde de um serviço específico"""
    if service_id not in services_registry:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    
    service = services_registry[service_id]
    config = service["config"]
    
    if not config.get("health_check_path"):
        return {"message": "Health check não configurado para este serviço"}
    
    # Fazer health check
    health_request = IntegrationRequest(
        service_id=service_id,
        method="GET",
        path=config["health_check_path"]
    )
    
    result = await make_integration_request(health_request)
    
    return {
        "service_id": service_id,
        "healthy": result.success,
        "response_time": result.response_time,
        "status_code": result.status_code,
        "timestamp": result.timestamp
    }

@integration_router.post("/health-check/all")
async def check_all_services_health():
    """Verifica a saúde de todos os serviços"""
    results = []
    
    for service_id in services_registry.keys():
        try:
            health_result = await check_service_health(service_id)
            results.append(health_result)
        except Exception as e:
            results.append({
                "service_id": service_id,
                "healthy": False,
                "error": str(e),
                "timestamp": datetime.now(timezone.utc)
            })
    
    healthy_count = sum(1 for r in results if r.get("healthy", False))
    total_count = len(results)
    
    return {
        "summary": {
            "total_services": total_count,
            "healthy_services": healthy_count,
            "unhealthy_services": total_count - healthy_count,
            "overall_health": (healthy_count / total_count * 100) if total_count > 0 else 0
        },
        "services": results,
        "timestamp": datetime.now(timezone.utc)
    }

# Endpoints de webhooks
@integration_router.post("/webhooks", response_model=Dict[str, str])
async def register_webhook(config: WebhookConfig):
    """Registra um novo webhook"""
    webhook_id = f"webhook_{len(webhooks_registry) + 1}"
    
    webhooks_registry[webhook_id] = {
        "id": webhook_id,
        "config": config.dict(),
        "created_at": datetime.now(timezone.utc),
        "stats": {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0
        }
    }
    
    return {
        "webhook_id": webhook_id,
        "message": f"Webhook {config.name} registrado com sucesso"
    }

@integration_router.get("/webhooks")
async def list_webhooks():
    """Lista todos os webhooks registrados"""
    return list(webhooks_registry.values())

@integration_router.post("/webhooks/{webhook_id}/trigger")
async def trigger_webhook(webhook_id: str, event_data: Dict[str, Any]):
    """Dispara um webhook específico"""
    if webhook_id not in webhooks_registry:
        raise HTTPException(status_code=404, detail="Webhook não encontrado")
    
    webhook = webhooks_registry[webhook_id]
    config = webhook["config"]
    
    if not config["active"]:
        raise HTTPException(status_code=400, detail="Webhook está inativo")
    
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                config["url"],
                json=event_data,
                headers=config.get("headers", {})
            )
            
            webhook["stats"]["total_calls"] += 1
            if response.status_code < 400:
                webhook["stats"]["successful_calls"] += 1
            else:
                webhook["stats"]["failed_calls"] += 1
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "response": response.text
            }
            
    except Exception as e:
        webhook["stats"]["total_calls"] += 1
        webhook["stats"]["failed_calls"] += 1
        
        return {
            "success": False,
            "error": str(e)
        }

# Endpoints de sincronização de dados
@integration_router.post("/sync/configure")
async def configure_data_sync(config: DataSyncConfig):
    """Configura sincronização de dados entre serviços"""
    sync_id = f"sync_{len(sync_configs) + 1}"
    
    sync_configs[sync_id] = {
        "id": sync_id,
        "config": config.dict(),
        "created_at": datetime.now(timezone.utc),
        "last_sync": None,
        "stats": {
            "total_syncs": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "records_synced": 0
        }
    }
    
    return {
        "sync_id": sync_id,
        "message": "Sincronização configurada com sucesso"
    }

@integration_router.get("/sync")
async def list_sync_configs():
    """Lista todas as configurações de sincronização"""
    return list(sync_configs.values())

@integration_router.post("/sync/{sync_id}/execute")
async def execute_sync(sync_id: str, background_tasks: BackgroundTasks):
    """Executa uma sincronização específica"""
    if sync_id not in sync_configs:
        raise HTTPException(status_code=404, detail="Configuração de sincronização não encontrada")
    
    # Executar sincronização em background
    background_tasks.add_task(_execute_data_sync, sync_id)
    
    return {
        "message": "Sincronização iniciada",
        "sync_id": sync_id,
        "status": "running"
    }

async def _execute_data_sync(sync_id: str):
    """Executa a sincronização de dados (função auxiliar)"""
    sync_config = sync_configs[sync_id]
    config = sync_config["config"]
    
    try:
        # Simular sincronização de dados
        await asyncio.sleep(2)  # Simular processamento
        
        # Atualizar estatísticas
        sync_config["stats"]["total_syncs"] += 1
        sync_config["stats"]["successful_syncs"] += 1
        sync_config["stats"]["records_synced"] += 100  # Simular registros sincronizados
        sync_config["last_sync"] = datetime.now(timezone.utc)
        
        # Log da sincronização
        integration_logs.append({
            "type": "sync",
            "sync_id": sync_id,
            "status": "success",
            "records": 100,
            "timestamp": datetime.now(timezone.utc)
        })
        
    except Exception as e:
        sync_config["stats"]["total_syncs"] += 1
        sync_config["stats"]["failed_syncs"] += 1
        
        integration_logs.append({
            "type": "sync",
            "sync_id": sync_id,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc)
        })

# Endpoints de monitoramento
@integration_router.get("/metrics")
async def get_integration_metrics():
    """Obtém métricas de integração"""
    total_services = len(services_registry)
    active_services = sum(1 for s in services_registry.values() if s["status"] == IntegrationStatus.ACTIVE)
    
    total_webhooks = len(webhooks_registry)
    active_webhooks = sum(1 for w in webhooks_registry.values() if w["config"]["active"])
    
    total_syncs = len(sync_configs)
    active_syncs = sum(1 for s in sync_configs.values() if s["config"]["active"])
    
    # Calcular estatísticas agregadas
    total_requests = sum(s["stats"]["total_requests"] for s in services_registry.values())
    successful_requests = sum(s["stats"]["successful_requests"] for s in services_registry.values())
    
    return {
        "services": {
            "total": total_services,
            "active": active_services,
            "inactive": total_services - active_services,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0
        },
        "webhooks": {
            "total": total_webhooks,
            "active": active_webhooks,
            "inactive": total_webhooks - active_webhooks
        },
        "synchronization": {
            "total": total_syncs,
            "active": active_syncs,
            "inactive": total_syncs - active_syncs
        },
        "requests": {
            "total": total_requests,
            "successful": successful_requests,
            "failed": total_requests - successful_requests
        },
        "timestamp": datetime.now(timezone.utc)
    }

@integration_router.get("/logs")
async def get_integration_logs(limit: int = 100):
    """Obtém logs de integração"""
    return {
        "logs": integration_logs[-limit:],
        "total": len(integration_logs),
        "timestamp": datetime.now(timezone.utc)
    }

@integration_router.get("/health")
async def integration_health_check():
    """Health check do sistema de integração"""
    return {
        "status": "healthy",
        "services_count": len(services_registry),
        "webhooks_count": len(webhooks_registry),
        "sync_configs_count": len(sync_configs),
        "timestamp": datetime.now(timezone.utc),
        "version": "1.0.0"
    }

@integration_router.get("/info")
async def integration_info():
    """
    Informações do domínio integration
    """
    return {
        "domain": "integration",
        "name": "Integration Domain",
        "version": "1.0.0", 
        "description": "Integração com sistemas externos",
        "features": ['External APIs', 'Data Sync', 'Webhook Support'],
        "status": "active"
    }

@integration_router.get("/health/detail")
async def integration_health_detail():
    """
    Health check do domínio integration
    """
    return {
        "status": "healthy",
        "domain": "integration",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

