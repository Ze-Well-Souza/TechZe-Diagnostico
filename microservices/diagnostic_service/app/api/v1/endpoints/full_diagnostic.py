from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
import logging
import uuid

from app.core.security import get_current_user
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.services.analyzers import CPUAnalyzer, MemoryAnalyzer, DiskAnalyzer, NetworkAnalyzer, AntivirusAnalyzer, DriverAnalyzer
from app.services.system_info_service import SystemInfoService
from app.db.repositories.diagnostic_repository import DiagnosticRepository
from app.core.models.diagnostic import DiagnosticStatus

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=Dict[str, Any])
async def run_full_diagnostic(
    request: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Executa um diagnóstico completo do sistema.
    
    - **device_id**: ID do dispositivo a ser diagnosticado
    - **diagnostic_id**: ID opcional de um diagnóstico existente
    - **system_info**: Informações opcionais do sistema
    """
    try:
        # Extrair parâmetros da requisição
        device_id = request.get("device_id")
        diagnostic_id = request.get("diagnostic_id")
        system_info_data = request.get("system_info", {})
        
        if not device_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="device_id é obrigatório"
            )
        
        # Inicializar repositório e serviços
        diagnostic_repo = DiagnosticRepository(db)
        
        # Criar ou atualizar diagnóstico
        if diagnostic_id:
            # Verificar se o diagnóstico existe e pertence ao usuário
            diagnostic = diagnostic_repo.get_diagnostic(diagnostic_id)
            if not diagnostic or str(diagnostic.user_id) != current_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Diagnóstico não encontrado"
                )
            
            # Atualizar status para em andamento
            diagnostic = diagnostic_repo.update_diagnostic(
                diagnostic_id=diagnostic_id,
                user_id=current_user,
                status=DiagnosticStatus.IN_PROGRESS
            )
        else:
            # Criar novo diagnóstico
            diagnostic = diagnostic_repo.create_diagnostic(
                user_id=current_user,
                device_id=device_id,
                status=DiagnosticStatus.IN_PROGRESS
            )
            diagnostic_id = diagnostic.id
        
        # Registrar início do diagnóstico
        start_time = datetime.now()
        
        # Inicializar analisadores
        cpu_analyzer = CPUAnalyzer()
        memory_analyzer = MemoryAnalyzer()
        disk_analyzer = DiskAnalyzer()
        network_analyzer = NetworkAnalyzer()
        antivirus_analyzer = AntivirusAnalyzer()
        driver_analyzer = DriverAnalyzer()
        system_info_service = SystemInfoService()
        
        # Executar análises
        cpu_result = cpu_analyzer.analyze()
        memory_result = memory_analyzer.analyze()
        disk_result = disk_analyzer.analyze()
        network_result = network_analyzer.analyze()
        antivirus_result = antivirus_analyzer.analyze()
        driver_result = driver_analyzer.analyze()
        
        # Coletar informações do sistema
        if not system_info_data:
            system_info = system_info_service.collect_system_info()
        else:
            # Usar informações fornecidas e complementar com dados coletados
            system_info = system_info_service.collect_system_info()
            system_info.update(system_info_data)
        
        # Calcular health score
        health_score = _calculate_health_score(
            cpu_result, memory_result, disk_result, network_result, antivirus_result, driver_result
        )
        
        # Compilar dados brutos
        raw_data = {
            "cpu": cpu_result,
            "memory": memory_result,
            "disk": disk_result,
            "network": network_result,
            "antivirus": antivirus_result,
            "drivers": driver_result,
            "system_info": system_info
        }
        
        # Calcular tempo de execução
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Atualizar diagnóstico com resultados
        updated_diagnostic = diagnostic_repo.update_diagnostic(
            diagnostic_id=diagnostic_id,
            user_id=current_user,
            status=DiagnosticStatus.COMPLETED,
            cpu_status=cpu_result["status"],
            memory_status=memory_result["status"],
            disk_status=disk_result["status"],
            network_status=network_result["status"],
            antivirus_status=antivirus_result["status"],
            driver_status=driver_result["status"],
            cpu_metrics=cpu_result,
            memory_metrics=memory_result,
            disk_metrics=disk_result,
            network_metrics=network_result,
            antivirus_metrics=antivirus_result,
            driver_metrics=driver_result,
            overall_health=health_score,
            raw_data=raw_data,
            execution_time=execution_time
        )
        
        # Retornar resultados
        return {
            "message": "Diagnóstico completo executado com sucesso",
            "diagnostic_id": str(diagnostic_id),
            "status": DiagnosticStatus.COMPLETED,
            "health_score": health_score,
            "execution_time": execution_time,
            "results": {
                "cpu": cpu_result,
                "memory": memory_result,
                "disk": disk_result,
                "network": network_result,
                "antivirus": antivirus_result,
                "drivers": driver_result
            },
            "system_info": system_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Erro ao executar diagnóstico completo: {e}")
        
        # Se temos um diagnostic_id, atualizar para status de falha
        if diagnostic_id:
            try:
                diagnostic_repo.update_diagnostic(
                    diagnostic_id=diagnostic_id,
                    user_id=current_user,
                    status=DiagnosticStatus.FAILED,
                    error_message=str(e)
                )
            except Exception as update_error:
                logger.error(f"Erro ao atualizar diagnóstico com falha: {update_error}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao executar diagnóstico: {str(e)}"
        )


def _calculate_health_score(cpu_result, memory_result, disk_result, network_result, antivirus_result, driver_result) -> int:
    """
    Calcula a pontuação de saúde geral do sistema com base nos resultados dos analisadores.
    
    Args:
        cpu_result: Resultado da análise de CPU
        memory_result: Resultado da análise de memória
        disk_result: Resultado da análise de disco
        network_result: Resultado da análise de rede
        antivirus_result: Resultado da análise de antivírus
        driver_result: Resultado da análise de drivers
        
    Returns:
        Pontuação de saúde (0-100)
    """
    # Pesos para cada componente
    weights = {
        "cpu": 0.2,
        "memory": 0.2,
        "disk": 0.2,
        "network": 0.15,
        "antivirus": 0.15,
        "drivers": 0.1
    }
    
    # Pontuação para cada status
    status_scores = {
        "healthy": 100,
        "warning": 70,
        "critical": 30,
        "error": 50,
        "unknown": 50
    }
    
    # Calcular pontuação ponderada
    cpu_score = status_scores.get(cpu_result.get("status", "unknown"), 50)
    memory_score = status_scores.get(memory_result.get("status", "unknown"), 50)
    disk_score = status_scores.get(disk_result.get("status", "unknown"), 50)
    network_score = status_scores.get(network_result.get("status", "unknown"), 50)
    antivirus_score = status_scores.get(antivirus_result.get("status", "unknown"), 50)
    driver_score = status_scores.get(driver_result.get("status", "unknown"), 50)
    
    weighted_score = (
        cpu_score * weights["cpu"] +
        memory_score * weights["memory"] +
        disk_score * weights["disk"] +
        network_score * weights["network"] +
        antivirus_score * weights["antivirus"] +
        driver_score * weights["drivers"]
    )
    
    return int(weighted_score)