"""
Endpoints da API v3 - Automação Avançada
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from ...automation.auto_fix import (
    AutoFixEngine,
    WorkflowManager,
    ResourceOptimizer,
    ProcessAutomator
)
from ...models.automation_models import (
    AutoFixRequest,
    AutoFixResponse,
    WorkflowRequest,
    WorkflowResponse,
    OptimizationRequest,
    OptimizationResponse,
    AutomationTask,
    AutomationStatus,
    ScheduledTask,
    AutomationRule
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/automation", tags=["Advanced Automation"])

# Instâncias dos engines de automação
auto_fix_engine = AutoFixEngine()
workflow_manager = WorkflowManager()
resource_optimizer = ResourceOptimizer()
process_automator = ProcessAutomator()

@router.post("/auto-fix", response_model=AutoFixResponse)
async def execute_auto_fix(
    request: AutoFixRequest,
    background_tasks: BackgroundTasks
) -> AutoFixResponse:
    """
    Executa correção automática de problemas detectados
    """
    try:
        logger.info(f"Iniciando auto-correção para {request.problem_type}")
        
        # Validar se o problema pode ser corrigido automaticamente
        can_fix = await auto_fix_engine.can_auto_fix(
            problem_type=request.problem_type,
            severity=request.severity,
            system_state=request.system_state
        )
        
        if not can_fix["possible"]:
            return AutoFixResponse(
                fix_id=f"fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                problem_type=request.problem_type,
                status="not_applicable",
                success=False,
                actions_taken=[],
                error_message=can_fix["reason"],
                execution_time=0,
                risk_level="none",
                rollback_available=False,
                created_at=datetime.now()
            )
        
        # Executar correção
        if request.execute_immediately:
            fix_result = await auto_fix_engine.execute_fix(
                problem_type=request.problem_type,
                parameters=request.parameters,
                safety_checks=request.safety_checks
            )
        else:
            # Agendar para execução posterior
            fix_id = f"fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            background_tasks.add_task(
                auto_fix_engine.schedule_fix,
                request,
                fix_id
            )
            fix_result = {
                "fix_id": fix_id,
                "status": "scheduled",
                "success": True,
                "actions_taken": ["Correção agendada"],
                "execution_time": 0,
                "risk_level": can_fix["risk_level"]
            }
        
        return AutoFixResponse(
            fix_id=fix_result["fix_id"],
            problem_type=request.problem_type,
            status=fix_result["status"],
            success=fix_result["success"],
            actions_taken=fix_result["actions_taken"],
            error_message=fix_result.get("error"),
            execution_time=fix_result["execution_time"],
            risk_level=fix_result["risk_level"],
            rollback_available=fix_result.get("rollback_available", False),
            rollback_steps=fix_result.get("rollback_steps", []),
            verification_results=fix_result.get("verification", {}),
            created_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erro na auto-correção: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na correção: {str(e)}")

@router.post("/workflows", response_model=WorkflowResponse)
async def create_automation_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks
) -> WorkflowResponse:
    """
    Cria e executa workflow de automação personalizado
    """
    try:
        logger.info(f"Criando workflow: {request.workflow_name}")
        
        # Validar workflow
        validation_result = await workflow_manager.validate_workflow(request.steps)
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"Workflow inválido: {validation_result['errors']}"
            )
        
        # Criar workflow
        workflow_result = await workflow_manager.create_workflow(
            name=request.workflow_name,
            description=request.description,
            steps=request.steps,
            triggers=request.triggers,
            schedule=request.schedule
        )
        
        # Executar se solicitado
        if request.execute_immediately:
            background_tasks.add_task(
                workflow_manager.execute_workflow,
                workflow_result["workflow_id"]
            )
            execution_status = "running"
        else:
            execution_status = "created"
        
        return WorkflowResponse(
            workflow_id=workflow_result["workflow_id"],
            workflow_name=request.workflow_name,
            status=execution_status,
            steps_count=len(request.steps),
            estimated_duration=workflow_result["estimated_duration"],
            next_execution=workflow_result.get("next_execution"),
            triggers_active=len(request.triggers) > 0,
            created_at=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na criação de workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/optimize", response_model=OptimizationResponse)
async def optimize_system_resources(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks
) -> OptimizationResponse:
    """
    Executa otimização automática de recursos do sistema
    """
    try:
        logger.info(f"Iniciando otimização: {request.optimization_type}")
        
        # Analisar estado atual
        current_state = await resource_optimizer.analyze_current_state(
            target_resources=request.target_resources
        )
        
        # Gerar plano de otimização
        optimization_plan = await resource_optimizer.create_optimization_plan(
            optimization_type=request.optimization_type,
            current_state=current_state,
            target_metrics=request.target_metrics,
            constraints=request.constraints
        )
        
        # Executar otimização
        if request.execute_immediately:
            optimization_result = await resource_optimizer.execute_optimization(
                plan=optimization_plan,
                safety_mode=request.safety_mode
            )
        else:
            # Agendar otimização
            optimization_id = f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            background_tasks.add_task(
                resource_optimizer.schedule_optimization,
                optimization_plan,
                optimization_id
            )
            optimization_result = {
                "optimization_id": optimization_id,
                "status": "scheduled",
                "improvements": optimization_plan["expected_improvements"],
                "execution_time": 0
            }
        
        return OptimizationResponse(
            optimization_id=optimization_result["optimization_id"],
            optimization_type=request.optimization_type,
            status=optimization_result["status"],
            improvements_achieved=optimization_result["improvements"],
            resources_optimized=request.target_resources,
            performance_gain=optimization_result.get("performance_gain", {}),
            execution_time=optimization_result["execution_time"],
            rollback_available=optimization_result.get("rollback_available", False),
            next_optimization=optimization_result.get("next_optimization"),
            created_at=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Erro na otimização: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/tasks", response_model=List[AutomationTask])
async def get_automation_tasks(
    status_filter: Optional[str] = None,
    task_type: Optional[str] = None,
    limit: int = 50
) -> List[AutomationTask]:
    """
    Lista tarefas de automação ativas e históricas
    """
    try:
        # Obter tarefas de todos os engines
        all_tasks = []
        
        # Tarefas do auto-fix
        fix_tasks = await auto_fix_engine.get_tasks(status_filter, limit)
        all_tasks.extend(fix_tasks)
        
        # Tarefas de workflow
        workflow_tasks = await workflow_manager.get_tasks(status_filter, limit)
        all_tasks.extend(workflow_tasks)
        
        # Tarefas de otimização
        optimization_tasks = await resource_optimizer.get_tasks(status_filter, limit)
        all_tasks.extend(optimization_tasks)
        
        # Filtrar por tipo se especificado
        if task_type:
            all_tasks = [task for task in all_tasks if task.task_type == task_type]
        
        # Ordenar por data de criação (mais recentes primeiro)
        all_tasks.sort(key=lambda x: x.created_at, reverse=True)
        
        return all_tasks[:limit]
        
    except Exception as e:
        logger.error(f"Erro ao listar tarefas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/tasks/{task_id}/status", response_model=AutomationStatus)
async def get_task_status(task_id: str) -> AutomationStatus:
    """
    Obtém status detalhado de uma tarefa específica
    """
    try:
        # Procurar tarefa em todos os engines
        task_status = None
        
        # Verificar no auto-fix
        task_status = await auto_fix_engine.get_task_status(task_id)
        if task_status:
            return task_status
        
        # Verificar no workflow manager
        task_status = await workflow_manager.get_task_status(task_id)
        if task_status:
            return task_status
        
        # Verificar no resource optimizer
        task_status = await resource_optimizer.get_task_status(task_id)
        if task_status:
            return task_status
        
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/tasks/{task_id}/cancel")
async def cancel_automation_task(task_id: str) -> Dict[str, str]:
    """
    Cancela uma tarefa de automação em execução
    """
    try:
        logger.info(f"Cancelando tarefa {task_id}")
        
        # Tentar cancelar em todos os engines
        cancelled = False
        
        if await auto_fix_engine.cancel_task(task_id):
            cancelled = True
        elif await workflow_manager.cancel_task(task_id):
            cancelled = True
        elif await resource_optimizer.cancel_task(task_id):
            cancelled = True
        
        if not cancelled:
            raise HTTPException(status_code=404, detail="Tarefa não encontrada ou não pode ser cancelada")
        
        return {
            "message": f"Tarefa {task_id} cancelada com sucesso",
            "status": "cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao cancelar tarefa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/tasks/{task_id}/rollback")
async def rollback_automation_task(task_id: str) -> Dict[str, Any]:
    """
    Executa rollback de uma tarefa de automação
    """
    try:
        logger.info(f"Executando rollback da tarefa {task_id}")
        
        # Tentar rollback em todos os engines
        rollback_result = None
        
        rollback_result = await auto_fix_engine.rollback_task(task_id)
        if not rollback_result:
            rollback_result = await workflow_manager.rollback_task(task_id)
        if not rollback_result:
            rollback_result = await resource_optimizer.rollback_task(task_id)
        
        if not rollback_result:
            raise HTTPException(
                status_code=404, 
                detail="Tarefa não encontrada ou rollback não disponível"
            )
        
        return {
            "task_id": task_id,
            "rollback_status": rollback_result["status"],
            "actions_reverted": rollback_result["actions_reverted"],
            "rollback_time": rollback_result["execution_time"],
            "success": rollback_result["success"],
            "message": rollback_result.get("message", "Rollback executado com sucesso")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no rollback: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/schedules", response_model=List[ScheduledTask])
async def get_scheduled_tasks() -> List[ScheduledTask]:
    """
    Lista todas as tarefas agendadas
    """
    try:
        scheduled_tasks = []
        
        # Obter tarefas agendadas de todos os engines
        scheduled_tasks.extend(await auto_fix_engine.get_scheduled_tasks())
        scheduled_tasks.extend(await workflow_manager.get_scheduled_tasks())
        scheduled_tasks.extend(await resource_optimizer.get_scheduled_tasks())
        
        # Ordenar por próxima execução
        scheduled_tasks.sort(key=lambda x: x.next_execution)
        
        return scheduled_tasks
        
    except Exception as e:
        logger.error(f"Erro ao listar tarefas agendadas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/schedules/{schedule_id}/pause")
async def pause_scheduled_task(schedule_id: str) -> Dict[str, str]:
    """
    Pausa uma tarefa agendada
    """
    try:
        logger.info(f"Pausando tarefa agendada {schedule_id}")
        
        # Tentar pausar em todos os engines
        paused = False
        
        if await auto_fix_engine.pause_scheduled_task(schedule_id):
            paused = True
        elif await workflow_manager.pause_scheduled_task(schedule_id):
            paused = True
        elif await resource_optimizer.pause_scheduled_task(schedule_id):
            paused = True
        
        if not paused:
            raise HTTPException(status_code=404, detail="Tarefa agendada não encontrada")
        
        return {
            "message": f"Tarefa {schedule_id} pausada",
            "status": "paused"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao pausar tarefa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/schedules/{schedule_id}/resume")
async def resume_scheduled_task(schedule_id: str) -> Dict[str, str]:
    """
    Resume uma tarefa agendada pausada
    """
    try:
        logger.info(f"Resumindo tarefa agendada {schedule_id}")
        
        # Tentar resumir em todos os engines
        resumed = False
        
        if await auto_fix_engine.resume_scheduled_task(schedule_id):
            resumed = True
        elif await workflow_manager.resume_scheduled_task(schedule_id):
            resumed = True
        elif await resource_optimizer.resume_scheduled_task(schedule_id):
            resumed = True
        
        if not resumed:
            raise HTTPException(status_code=404, detail="Tarefa agendada não encontrada")
        
        return {
            "message": f"Tarefa {schedule_id} resumida",
            "status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao resumir tarefa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/rules", response_model=List[AutomationRule])
async def get_automation_rules() -> List[AutomationRule]:
    """
    Lista regras de automação ativas
    """
    try:
        all_rules = []
        
        # Obter regras de todos os engines
        all_rules.extend(await auto_fix_engine.get_automation_rules())
        all_rules.extend(await workflow_manager.get_automation_rules())
        all_rules.extend(await resource_optimizer.get_automation_rules())
        
        return all_rules
        
    except Exception as e:
        logger.error(f"Erro ao listar regras: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/rules")
async def create_automation_rule(rule: AutomationRule) -> Dict[str, str]:
    """
    Cria nova regra de automação
    """
    try:
        logger.info(f"Criando regra de automação: {rule.rule_name}")
        
        # Determinar engine apropriado baseado no tipo
        if rule.rule_type == "auto_fix":
            rule_id = await auto_fix_engine.create_automation_rule(rule)
        elif rule.rule_type == "workflow":
            rule_id = await workflow_manager.create_automation_rule(rule)
        elif rule.rule_type == "optimization":
            rule_id = await resource_optimizer.create_automation_rule(rule)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de regra não suportado: {rule.rule_type}"
            )
        
        return {
            "message": f"Regra {rule.rule_name} criada com sucesso",
            "rule_id": rule_id,
            "status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar regra: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.delete("/rules/{rule_id}")
async def delete_automation_rule(rule_id: str) -> Dict[str, str]:
    """
    Remove uma regra de automação
    """
    try:
        logger.info(f"Removendo regra {rule_id}")
        
        # Tentar remover de todos os engines
        deleted = False
        
        if await auto_fix_engine.delete_automation_rule(rule_id):
            deleted = True
        elif await workflow_manager.delete_automation_rule(rule_id):
            deleted = True
        elif await resource_optimizer.delete_automation_rule(rule_id):
            deleted = True
        
        if not deleted:
            raise HTTPException(status_code=404, detail="Regra não encontrada")
        
        return {
            "message": f"Regra {rule_id} removida com sucesso",
            "status": "deleted"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover regra: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.get("/statistics")
async def get_automation_statistics() -> Dict[str, Any]:
    """
    Retorna estatísticas de automação
    """
    try:
        stats = {
            "auto_fix": await auto_fix_engine.get_statistics(),
            "workflows": await workflow_manager.get_statistics(),
            "optimization": await resource_optimizer.get_statistics(),
            "overall": {
                "total_tasks_executed": 0,
                "success_rate": 0.0,
                "average_execution_time": 0,
                "time_saved_hours": 0,
                "last_updated": datetime.now()
            }
        }
        
        # Calcular estatísticas gerais
        total_tasks = (
            stats["auto_fix"]["total_executions"] +
            stats["workflows"]["total_executions"] +
            stats["optimization"]["total_executions"]
        )
        
        if total_tasks > 0:
            total_successes = (
                stats["auto_fix"]["successful_executions"] +
                stats["workflows"]["successful_executions"] +
                stats["optimization"]["successful_executions"]
            )
            
            stats["overall"]["total_tasks_executed"] = total_tasks
            stats["overall"]["success_rate"] = total_successes / total_tasks
            
            # Calcular tempo médio de execução
            total_time = (
                stats["auto_fix"]["total_execution_time"] +
                stats["workflows"]["total_execution_time"] +
                stats["optimization"]["total_execution_time"]
            )
            stats["overall"]["average_execution_time"] = total_time / total_tasks
            
            # Estimar tempo economizado (baseado em execução manual)
            manual_time_factor = 10  # Assume que automação é 10x mais rápida
            stats["overall"]["time_saved_hours"] = (total_time * manual_time_factor) / 3600
        
        return stats
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/emergency-stop")
async def emergency_stop_all_automation() -> Dict[str, str]:
    """
    Para todas as automações em execução (emergência)
    """
    try:
        logger.warning("PARADA DE EMERGÊNCIA - Parando todas as automações")
        
        # Parar todos os engines
        await auto_fix_engine.emergency_stop()
        await workflow_manager.emergency_stop()
        await resource_optimizer.emergency_stop()
        
        return {
            "message": "Todas as automações foram paradas",
            "status": "emergency_stopped",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro na parada de emergência: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

@router.post("/resume-all")
async def resume_all_automation() -> Dict[str, str]:
    """
    Resume todas as automações após parada de emergência
    """
    try:
        logger.info("Resumindo todas as automações")
        
        # Resumir todos os engines
        await auto_fix_engine.resume_all()
        await workflow_manager.resume_all()
        await resource_optimizer.resume_all()
        
        return {
            "message": "Todas as automações foram resumidas",
            "status": "operational",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao resumir automações: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")