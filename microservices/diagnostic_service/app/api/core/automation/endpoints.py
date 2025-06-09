"""Endpoints de Automação - API Core

Consolida todas as funcionalidades de automação e workflows.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel
from enum import Enum

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Automation"])

# Modelos de dados
class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TriggerType(str, Enum):
    SCHEDULE = "schedule"
    EVENT = "event"
    THRESHOLD = "threshold"
    MANUAL = "manual"

class AutomationTask(BaseModel):
    task_id: Optional[str] = None
    name: str
    description: str
    task_type: str
    parameters: Dict[str, Any] = {}
    priority: TaskPriority = TaskPriority.MEDIUM
    schedule: Optional[str] = None  # Cron expression
    triggers: List[Dict[str, Any]] = []
    dependencies: List[str] = []
    timeout: int = 3600  # seconds
    retry_count: int = 3
    enabled: bool = True

class TaskExecution(BaseModel):
    execution_id: str
    task_id: str
    status: TaskStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    logs: List[str] = []

class WorkflowDefinition(BaseModel):
    workflow_id: Optional[str] = None
    name: str
    description: str
    tasks: List[AutomationTask]
    execution_order: List[str]  # Task IDs in execution order
    parallel_groups: List[List[str]] = []  # Groups of tasks that can run in parallel
    enabled: bool = True
    created_at: Optional[datetime] = None

class AutomationRule(BaseModel):
    rule_id: Optional[str] = None
    name: str
    description: str
    trigger_type: TriggerType
    trigger_conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    enabled: bool = True
    last_triggered: Optional[datetime] = None

# Simulação de armazenamento em memória (em produção seria um banco de dados)
automation_tasks = {}
task_executions = {}
workflows = {}
automation_rules = {}

@router.post("/tasks", response_model=AutomationTask)
async def create_automation_task(task: AutomationTask) -> AutomationTask:
    """
    Cria uma nova tarefa de automação
    """
    try:
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(automation_tasks)}"
        task.task_id = task_id
        
        automation_tasks[task_id] = task
        
        logger.info(f"Tarefa de automação criada: {task_id}")
        return task
        
    except Exception as e:
        logger.error(f"Erro ao criar tarefa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar tarefa: {str(e)}")

@router.get("/tasks", response_model=List[AutomationTask])
async def list_automation_tasks(
    enabled_only: bool = False,
    task_type: Optional[str] = None
) -> List[AutomationTask]:
    """
    Lista todas as tarefas de automação
    """
    try:
        tasks = list(automation_tasks.values())
        
        if enabled_only:
            tasks = [task for task in tasks if task.enabled]
        
        if task_type:
            tasks = [task for task in tasks if task.task_type == task_type]
        
        return tasks
        
    except Exception as e:
        logger.error(f"Erro ao listar tarefas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar tarefas: {str(e)}")

@router.get("/tasks/{task_id}", response_model=AutomationTask)
async def get_automation_task(task_id: str) -> AutomationTask:
    """
    Obtém detalhes de uma tarefa específica
    """
    if task_id not in automation_tasks:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    return automation_tasks[task_id]

@router.put("/tasks/{task_id}", response_model=AutomationTask)
async def update_automation_task(task_id: str, task_update: AutomationTask) -> AutomationTask:
    """
    Atualiza uma tarefa de automação existente
    """
    if task_id not in automation_tasks:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    try:
        task_update.task_id = task_id
        automation_tasks[task_id] = task_update
        
        logger.info(f"Tarefa atualizada: {task_id}")
        return task_update
        
    except Exception as e:
        logger.error(f"Erro ao atualizar tarefa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar tarefa: {str(e)}")

@router.delete("/tasks/{task_id}")
async def delete_automation_task(task_id: str) -> Dict[str, str]:
    """
    Remove uma tarefa de automação
    """
    if task_id not in automation_tasks:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    try:
        del automation_tasks[task_id]
        logger.info(f"Tarefa removida: {task_id}")
        
        return {"message": f"Tarefa {task_id} removida com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro ao remover tarefa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao remover tarefa: {str(e)}")

@router.post("/tasks/{task_id}/execute", response_model=TaskExecution)
async def execute_automation_task(
    task_id: str,
    background_tasks: BackgroundTasks,
    parameters: Optional[Dict[str, Any]] = None
) -> TaskExecution:
    """
    Executa uma tarefa de automação
    """
    if task_id not in automation_tasks:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    task = automation_tasks[task_id]
    
    if not task.enabled:
        raise HTTPException(status_code=400, detail="Tarefa está desabilitada")
    
    try:
        execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(task_executions)}"
        
        execution = TaskExecution(
            execution_id=execution_id,
            task_id=task_id,
            status=TaskStatus.PENDING,
            started_at=datetime.now()
        )
        
        task_executions[execution_id] = execution
        
        # Executar tarefa em background
        background_tasks.add_task(
            _execute_task_background,
            execution_id,
            task,
            parameters or {}
        )
        
        logger.info(f"Execução iniciada: {execution_id} para tarefa {task_id}")
        return execution
        
    except Exception as e:
        logger.error(f"Erro ao executar tarefa: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao executar tarefa: {str(e)}")

@router.get("/executions/{execution_id}", response_model=TaskExecution)
async def get_task_execution(execution_id: str) -> TaskExecution:
    """
    Obtém detalhes de uma execução específica
    """
    if execution_id not in task_executions:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    
    return task_executions[execution_id]

@router.get("/executions", response_model=List[TaskExecution])
async def list_task_executions(
    task_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    limit: int = 100
) -> List[TaskExecution]:
    """
    Lista execuções de tarefas
    """
    try:
        executions = list(task_executions.values())
        
        if task_id:
            executions = [exec for exec in executions if exec.task_id == task_id]
        
        if status:
            executions = [exec for exec in executions if exec.status == status]
        
        # Ordenar por data de início (mais recente primeiro)
        executions.sort(key=lambda x: x.started_at, reverse=True)
        
        return executions[:limit]
        
    except Exception as e:
        logger.error(f"Erro ao listar execuções: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar execuções: {str(e)}")

@router.post("/workflows", response_model=WorkflowDefinition)
async def create_workflow(workflow: WorkflowDefinition) -> WorkflowDefinition:
    """
    Cria um novo workflow de automação
    """
    try:
        workflow_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(workflows)}"
        workflow.workflow_id = workflow_id
        workflow.created_at = datetime.now()
        
        workflows[workflow_id] = workflow
        
        logger.info(f"Workflow criado: {workflow_id}")
        return workflow
        
    except Exception as e:
        logger.error(f"Erro ao criar workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar workflow: {str(e)}")

@router.get("/workflows", response_model=List[WorkflowDefinition])
async def list_workflows(enabled_only: bool = False) -> List[WorkflowDefinition]:
    """
    Lista todos os workflows
    """
    try:
        workflow_list = list(workflows.values())
        
        if enabled_only:
            workflow_list = [wf for wf in workflow_list if wf.enabled]
        
        return workflow_list
        
    except Exception as e:
        logger.error(f"Erro ao listar workflows: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar workflows: {str(e)}")

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(
    workflow_id: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Executa um workflow completo
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow não encontrado")
    
    workflow = workflows[workflow_id]
    
    if not workflow.enabled:
        raise HTTPException(status_code=400, detail="Workflow está desabilitado")
    
    try:
        execution_id = f"workflow_exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Executar workflow em background
        background_tasks.add_task(
            _execute_workflow_background,
            execution_id,
            workflow
        )
        
        logger.info(f"Execução de workflow iniciada: {execution_id}")
        
        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "started",
            "started_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Erro ao executar workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao executar workflow: {str(e)}")

@router.post("/rules", response_model=AutomationRule)
async def create_automation_rule(rule: AutomationRule) -> AutomationRule:
    """
    Cria uma nova regra de automação
    """
    try:
        rule_id = f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(automation_rules)}"
        rule.rule_id = rule_id
        
        automation_rules[rule_id] = rule
        
        logger.info(f"Regra de automação criada: {rule_id}")
        return rule
        
    except Exception as e:
        logger.error(f"Erro ao criar regra: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao criar regra: {str(e)}")

@router.get("/rules", response_model=List[AutomationRule])
async def list_automation_rules(enabled_only: bool = False) -> List[AutomationRule]:
    """
    Lista todas as regras de automação
    """
    try:
        rules = list(automation_rules.values())
        
        if enabled_only:
            rules = [rule for rule in rules if rule.enabled]
        
        return rules
        
    except Exception as e:
        logger.error(f"Erro ao listar regras: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar regras: {str(e)}")

@router.get("/statistics")
async def get_automation_statistics() -> Dict[str, Any]:
    """
    Retorna estatísticas do sistema de automação
    """
    try:
        total_tasks = len(automation_tasks)
        enabled_tasks = len([t for t in automation_tasks.values() if t.enabled])
        total_executions = len(task_executions)
        
        # Estatísticas de execução por status
        status_counts = {}
        for execution in task_executions.values():
            status = execution.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Execuções nas últimas 24 horas
        last_24h = datetime.now() - timedelta(hours=24)
        recent_executions = [
            exec for exec in task_executions.values()
            if exec.started_at >= last_24h
        ]
        
        return {
            "total_tasks": total_tasks,
            "enabled_tasks": enabled_tasks,
            "total_workflows": len(workflows),
            "total_rules": len(automation_rules),
            "total_executions": total_executions,
            "executions_last_24h": len(recent_executions),
            "execution_status_counts": status_counts,
            "success_rate": (
                status_counts.get("completed", 0) / max(total_executions, 1)
            ) * 100,
            "last_updated": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@router.get("/health")
async def automation_health_check() -> Dict[str, Any]:
    """
    Verifica a saúde do sistema de automação
    """
    try:
        # Verificar tarefas com falha recente
        recent_failures = [
            exec for exec in task_executions.values()
            if exec.status == TaskStatus.FAILED and
            exec.started_at >= datetime.now() - timedelta(hours=1)
        ]
        
        # Verificar tarefas em execução há muito tempo
        long_running = [
            exec for exec in task_executions.values()
            if exec.status == TaskStatus.RUNNING and
            exec.started_at <= datetime.now() - timedelta(hours=2)
        ]
        
        health_status = "healthy"
        issues = []
        
        if len(recent_failures) > 5:
            health_status = "degraded"
            issues.append(f"{len(recent_failures)} falhas na última hora")
        
        if len(long_running) > 0:
            health_status = "degraded"
            issues.append(f"{len(long_running)} tarefas executando há mais de 2 horas")
        
        return {
            "status": health_status,
            "timestamp": datetime.now(),
            "issues": issues,
            "recent_failures": len(recent_failures),
            "long_running_tasks": len(long_running),
            "active_tasks": len([t for t in automation_tasks.values() if t.enabled])
        }
        
    except Exception as e:
        logger.error(f"Erro no health check de automação: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(),
            "error": str(e)
        }

# Funções auxiliares para execução em background
async def _execute_task_background(
    execution_id: str,
    task: AutomationTask,
    parameters: Dict[str, Any]
):
    """
    Executa uma tarefa em background
    """
    execution = task_executions[execution_id]
    
    try:
        execution.status = TaskStatus.RUNNING
        execution.logs.append(f"Iniciando execução da tarefa {task.name}")
        
        # Simular execução da tarefa (em produção seria a lógica real)
        import asyncio
        await asyncio.sleep(2)  # Simular processamento
        
        # Simular resultado baseado no tipo de tarefa
        if task.task_type == "system_cleanup":
            result = {
                "files_cleaned": 150,
                "space_freed_mb": 2048,
                "temp_files_removed": 75
            }
        elif task.task_type == "backup":
            result = {
                "backup_size_mb": 1024,
                "files_backed_up": 500,
                "backup_location": "/backups/auto_backup.zip"
            }
        elif task.task_type == "health_check":
            result = {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 23.1,
                "status": "healthy"
            }
        else:
            result = {"message": "Tarefa executada com sucesso"}
        
        execution.status = TaskStatus.COMPLETED
        execution.completed_at = datetime.now()
        execution.duration = int((execution.completed_at - execution.started_at).total_seconds())
        execution.result = result
        execution.logs.append(f"Tarefa {task.name} concluída com sucesso")
        
        logger.info(f"Tarefa {task.task_id} executada com sucesso")
        
    except Exception as e:
        execution.status = TaskStatus.FAILED
        execution.completed_at = datetime.now()
        execution.duration = int((execution.completed_at - execution.started_at).total_seconds())
        execution.error_message = str(e)
        execution.logs.append(f"Erro na execução: {str(e)}")
        
        logger.error(f"Erro na execução da tarefa {task.task_id}: {e}")

async def _execute_workflow_background(
    execution_id: str,
    workflow: WorkflowDefinition
):
    """
    Executa um workflow em background
    """
    try:
        logger.info(f"Iniciando execução do workflow {workflow.workflow_id}")
        
        # Simular execução sequencial das tarefas
        for task_id in workflow.execution_order:
            # Encontrar a tarefa no workflow
            task = next((t for t in workflow.tasks if t.task_id == task_id), None)
            if task:
                # Simular execução da tarefa
                import asyncio
                await asyncio.sleep(1)
                logger.info(f"Tarefa {task.name} do workflow executada")
        
        logger.info(f"Workflow {workflow.workflow_id} concluído com sucesso")
        
    except Exception as e:
        logger.error(f"Erro na execução do workflow {workflow.workflow_id}: {e}")

@router.get("/info")
async def automation_info():
    """
    Informações do domínio automation
    """
    return {
        "domain": "automation",
        "name": "Automation Domain",
        "version": "1.0.0", 
        "description": "Automação de processos e workflows",
        "features": ['Workflow Automation', 'Task Scheduling', 'Process Management'],
        "status": "active"
    }

@router.get("/health")
async def automation_health_check():
    """
    Health check do domínio automation
    """
    return {
        "status": "healthy",
        "domain": "automation",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

