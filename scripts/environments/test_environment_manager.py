#!/usr/bin/env python3
"""
Sistema Avançado de Gerenciamento de Ambientes de Teste - TechZe Diagnóstico
Agente CURSOR - Isolamento e Controle de Ambientes de Teste
"""

import os
import json
import time
import docker
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass, asdict
import subprocess
import tempfile
import shutil
from pathlib import Path
import hashlib
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestEnvironment:
    """Estrutura de dados para ambiente de teste"""
    env_id: str
    name: str
    type: str  # docker, vm, local
    status: str  # creating, running, stopped, destroying
    created_at: datetime
    last_used: datetime
    port_mappings: Dict[str, int]
    resource_limits: Dict[str, Any]
    database_snapshot: Optional[str] = None
    docker_container_id: Optional[str] = None
    test_data_hash: Optional[str] = None

@dataclass
class DatabaseSnapshot:
    """Snapshot de banco de dados para teste"""
    snapshot_id: str
    name: str
    created_at: datetime
    size_mb: float
    tables_count: int
    records_count: int
    file_path: str
    checksum: str

class DockerTestEnvironment:
    """Gerenciador de ambientes de teste Docker"""
    
    def __init__(self):
        self.client = docker.from_env()
        self.network_name = "techze_test_network"
        self.base_image = "techze/test-environment"
        self._ensure_network()
    
    def _ensure_network(self):
        """Garantir que a rede de teste existe"""
        try:
            self.client.networks.get(self.network_name)
        except docker.errors.NotFound:
            self.client.networks.create(
                self.network_name,
                driver="bridge",
                options={"com.docker.network.bridge.enable_icc": "true"}
            )
            logger.info(f"Rede de teste criada: {self.network_name}")
    
    def create_environment(self, env_config: Dict[str, Any]) -> TestEnvironment:
        """Criar novo ambiente de teste"""
        env_id = f"test_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Criando ambiente de teste: {env_id}")
        
        # Configurações do container
        container_config = {
            "image": self.base_image,
            "name": f"techze_test_{env_id}",
            "environment": env_config.get("environment", {}),
            "networks": [self.network_name],
            "ports": self._generate_port_mappings(env_config.get("ports", [])),
            "mem_limit": env_config.get("memory_limit", "512m"),
            "cpu_quota": env_config.get("cpu_quota", 50000),  # 50% CPU
            "detach": True,
            "remove": False
        }
        
        # Volumes para dados de teste
        volumes = {
            f"techze_test_data_{env_id}": {"bind": "/app/data", "mode": "rw"}
        }
        container_config["volumes"] = volumes
        
        try:
            # Criar container
            container = self.client.containers.run(**container_config)
            
            # Aguardar container ficar pronto
            self._wait_for_container_ready(container)
            
            environment = TestEnvironment(
                env_id=env_id,
                name=env_config.get("name", f"Test Environment {env_id}"),
                type="docker",
                status="running",
                created_at=datetime.now(),
                last_used=datetime.now(),
                port_mappings=container_config["ports"],
                resource_limits={
                    "memory": env_config.get("memory_limit", "512m"),
                    "cpu_quota": env_config.get("cpu_quota", 50000)
                },
                docker_container_id=container.id
            )
            
            logger.info(f"Ambiente criado com sucesso: {env_id}")
            return environment
            
        except Exception as e:
            logger.error(f"Erro ao criar ambiente: {e}")
            raise
    
    def _generate_port_mappings(self, requested_ports: List[int]) -> Dict[str, int]:
        """Gerar mapeamento de portas disponíveis"""
        port_mappings = {}
        base_port = 30000
        
        for i, internal_port in enumerate(requested_ports):
            external_port = base_port + i
            
            # Verificar se porta está disponível
            while self._is_port_in_use(external_port):
                external_port += 1
            
            port_mappings[f"{internal_port}/tcp"] = external_port
        
        return port_mappings
    
    def _is_port_in_use(self, port: int) -> bool:
        """Verificar se porta está em uso"""
        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return True
        return False
    
    def _wait_for_container_ready(self, container, timeout: int = 60):
        """Aguardar container ficar pronto"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            container.reload()
            if container.status == "running":
                # Verificar se serviços internos estão prontos
                try:
                    # Executar health check
                    result = container.exec_run("curl -f http://localhost:8000/health || exit 1")
                    if result.exit_code == 0:
                        return
                except:
                    pass
            
            time.sleep(2)
        
        raise Exception(f"Container não ficou pronto em {timeout} segundos")
    
    def destroy_environment(self, env_id: str):
        """Destruir ambiente de teste"""
        logger.info(f"Destruindo ambiente: {env_id}")
        
        try:
            # Remover container
            container_name = f"techze_test_{env_id}"
            try:
                container = self.client.containers.get(container_name)
                container.stop(timeout=10)
                container.remove()
            except docker.errors.NotFound:
                pass
            
            # Remover volume de dados
            volume_name = f"techze_test_data_{env_id}"
            try:
                volume = self.client.volumes.get(volume_name)
                volume.remove()
            except docker.errors.NotFound:
                pass
            
            logger.info(f"Ambiente destruído: {env_id}")
            
        except Exception as e:
            logger.error(f"Erro ao destruir ambiente: {e}")
            raise

class DatabaseSnapshotManager:
    """Gerenciador de snapshots de banco de dados"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.snapshots_dir = Path("data/db_snapshots")
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots: Dict[str, DatabaseSnapshot] = {}
        self._load_snapshots_index()
    
    def create_snapshot(self, name: str, description: str = "") -> DatabaseSnapshot:
        """Criar snapshot do banco de dados"""
        snapshot_id = f"snap_{int(time.time())}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
        
        logger.info(f"Criando snapshot do banco: {snapshot_id}")
        
        # Arquivo de dump
        dump_file = self.snapshots_dir / f"{snapshot_id}.sql"
        
        try:
            # Comando pg_dump
            dump_cmd = [
                "pg_dump",
                "--host", self.db_config["host"],
                "--port", str(self.db_config["port"]),
                "--username", self.db_config["username"],
                "--dbname", self.db_config["database"],
                "--file", str(dump_file),
                "--verbose",
                "--clean",
                "--create",
                "--if-exists"
            ]
            
            # Executar dump
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db_config["password"]
            
            result = subprocess.run(
                dump_cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"pg_dump falhou: {result.stderr}")
            
            # Calcular estatísticas
            stats = self._analyze_dump(dump_file)
            
            # Calcular checksum
            checksum = self._calculate_checksum(dump_file)
            
            snapshot = DatabaseSnapshot(
                snapshot_id=snapshot_id,
                name=name,
                created_at=datetime.now(),
                size_mb=dump_file.stat().st_size / (1024 * 1024),
                tables_count=stats["tables"],
                records_count=stats["records"],
                file_path=str(dump_file),
                checksum=checksum
            )
            
            self.snapshots[snapshot_id] = snapshot
            self._save_snapshots_index()
            
            logger.info(f"Snapshot criado: {snapshot_id} ({snapshot.size_mb:.2f} MB)")
            return snapshot
            
        except Exception as e:
            # Limpar arquivo em caso de erro
            if dump_file.exists():
                dump_file.unlink()
            logger.error(f"Erro ao criar snapshot: {e}")
            raise
    
    def restore_snapshot(self, snapshot_id: str, target_db: str = None):
        """Restaurar snapshot para banco de teste"""
        if snapshot_id not in self.snapshots:
            raise ValueError(f"Snapshot não encontrado: {snapshot_id}")
        
        snapshot = self.snapshots[snapshot_id]
        target_db = target_db or f"test_db_{int(time.time())}"
        
        logger.info(f"Restaurando snapshot {snapshot_id} para {target_db}")
        
        # Verificar integridade do arquivo
        if not self._verify_snapshot_integrity(snapshot):
            raise Exception("Integridade do snapshot comprometida")
        
        try:
            # Criar banco de teste
            self._create_test_database(target_db)
            
            # Comando psql para restaurar
            restore_cmd = [
                "psql",
                "--host", self.db_config["host"],
                "--port", str(self.db_config["port"]),
                "--username", self.db_config["username"],
                "--dbname", target_db,
                "--file", snapshot.file_path,
                "--quiet"
            ]
            
            env = os.environ.copy()
            env["PGPASSWORD"] = self.db_config["password"]
            
            result = subprocess.run(
                restore_cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                raise Exception(f"Restore falhou: {result.stderr}")
            
            logger.info(f"Snapshot restaurado para: {target_db}")
            return target_db
            
        except Exception as e:
            logger.error(f"Erro ao restaurar snapshot: {e}")
            raise
    
    def _create_test_database(self, db_name: str):
        """Criar banco de dados de teste"""
        create_cmd = [
            "createdb",
            "--host", self.db_config["host"],
            "--port", str(self.db_config["port"]),
            "--username", self.db_config["username"],
            db_name
        ]
        
        env = os.environ.copy()
        env["PGPASSWORD"] = self.db_config["password"]
        
        subprocess.run(create_cmd, env=env, check=True)
    
    def _analyze_dump(self, dump_file: Path) -> Dict[str, int]:
        """Analisar dump para extrair estatísticas"""
        tables = 0
        records = 0
        
        with open(dump_file, 'r') as f:
            for line in f:
                if line.startswith('CREATE TABLE'):
                    tables += 1
                elif line.startswith('COPY ') and ' FROM stdin;' in line:
                    # Contar registros aproximadamente
                    records += 100  # Estimativa
        
        return {"tables": tables, "records": records}
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcular checksum do arquivo"""
        hash_sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        
        return hash_sha256.hexdigest()
    
    def _verify_snapshot_integrity(self, snapshot: DatabaseSnapshot) -> bool:
        """Verificar integridade do snapshot"""
        if not Path(snapshot.file_path).exists():
            return False
        
        current_checksum = self._calculate_checksum(Path(snapshot.file_path))
        return current_checksum == snapshot.checksum
    
    def _load_snapshots_index(self):
        """Carregar índice de snapshots"""
        index_file = self.snapshots_dir / "snapshots_index.json"
        
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    data = json.load(f)
                
                for snap_data in data.get("snapshots", []):
                    snapshot = DatabaseSnapshot(
                        snapshot_id=snap_data["snapshot_id"],
                        name=snap_data["name"],
                        created_at=datetime.fromisoformat(snap_data["created_at"]),
                        size_mb=snap_data["size_mb"],
                        tables_count=snap_data["tables_count"],
                        records_count=snap_data["records_count"],
                        file_path=snap_data["file_path"],
                        checksum=snap_data["checksum"]
                    )
                    self.snapshots[snapshot.snapshot_id] = snapshot
                    
            except Exception as e:
                logger.warning(f"Erro ao carregar índice de snapshots: {e}")
    
    def _save_snapshots_index(self):
        """Salvar índice de snapshots"""
        index_file = self.snapshots_dir / "snapshots_index.json"
        
        data = {
            "snapshots": [asdict(snapshot) for snapshot in self.snapshots.values()],
            "last_updated": datetime.now().isoformat()
        }
        
        with open(index_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def cleanup_old_snapshots(self, max_age_days: int = 7):
        """Limpar snapshots antigos"""
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        
        to_remove = []
        for snapshot_id, snapshot in self.snapshots.items():
            if snapshot.created_at < cutoff_date:
                to_remove.append(snapshot_id)
        
        for snapshot_id in to_remove:
            self.delete_snapshot(snapshot_id)
        
        logger.info(f"Removidos {len(to_remove)} snapshots antigos")
    
    def delete_snapshot(self, snapshot_id: str):
        """Deletar snapshot"""
        if snapshot_id not in self.snapshots:
            return
        
        snapshot = self.snapshots[snapshot_id]
        
        # Remover arquivo
        if Path(snapshot.file_path).exists():
            Path(snapshot.file_path).unlink()
        
        # Remover do índice
        del self.snapshots[snapshot_id]
        self._save_snapshots_index()
        
        logger.info(f"Snapshot removido: {snapshot_id}")

class TestEnvironmentManager:
    """Gerenciador principal de ambientes de teste"""
    
    def __init__(self, db_config: Dict[str, str]):
        self.docker_manager = DockerTestEnvironment()
        self.db_manager = DatabaseSnapshotManager(db_config)
        self.environments: Dict[str, TestEnvironment] = {}
        self.cleanup_thread = None
        self.running = False
    
    def create_isolated_environment(self, config: Dict[str, Any]) -> TestEnvironment:
        """Criar ambiente de teste isolado"""
        logger.info("Criando ambiente de teste isolado...")
        
        # 1. Criar snapshot do banco (se solicitado)
        db_snapshot = None
        if config.get("create_db_snapshot", True):
            snapshot_name = f"test_snapshot_{int(time.time())}"
            db_snapshot = self.db_manager.create_snapshot(snapshot_name)
        
        # 2. Criar ambiente Docker
        docker_config = {
            "name": config.get("name", "Test Environment"),
            "ports": config.get("ports", [8000, 5432, 6379]),
            "environment": {
                "NODE_ENV": "test",
                "PYTHONPATH": "/app",
                "DATABASE_URL": config.get("test_db_url", ""),
                **config.get("environment", {})
            },
            "memory_limit": config.get("memory_limit", "1g"),
            "cpu_quota": config.get("cpu_quota", 100000)  # 100% CPU
        }
        
        environment = self.docker_manager.create_environment(docker_config)
        
        # 3. Configurar snapshot no ambiente
        if db_snapshot:
            environment.database_snapshot = db_snapshot.snapshot_id
        
        # 4. Registrar ambiente
        self.environments[environment.env_id] = environment
        
        logger.info(f"Ambiente isolado criado: {environment.env_id}")
        return environment
    
    def prepare_test_data(self, env_id: str, data_config: Dict[str, Any]):
        """Preparar dados de teste específicos"""
        if env_id not in self.environments:
            raise ValueError(f"Ambiente não encontrado: {env_id}")
        
        environment = self.environments[env_id]
        
        # Restaurar snapshot se disponível
        if environment.database_snapshot:
            test_db_name = f"test_db_{env_id}"
            self.db_manager.restore_snapshot(
                environment.database_snapshot,
                test_db_name
            )
            
            # Atualizar configuração do ambiente
            container = self.docker_manager.client.containers.get(
                environment.docker_container_id
            )
            
            # Atualizar variável de ambiente do banco
            # Nota: Isso requer restart do container para algumas aplicações
            
        # Executar scripts de dados de teste adicionais
        test_scripts = data_config.get("test_scripts", [])
        for script in test_scripts:
            self._execute_test_script(environment, script)
    
    def _execute_test_script(self, environment: TestEnvironment, script: str):
        """Executar script de teste no ambiente"""
        try:
            container = self.docker_manager.client.containers.get(
                environment.docker_container_id
            )
            
            result = container.exec_run(f"python /app/scripts/{script}")
            
            if result.exit_code != 0:
                logger.warning(f"Script de teste falhou: {script}")
                logger.warning(result.output.decode())
            
        except Exception as e:
            logger.error(f"Erro ao executar script: {e}")
    
    def run_parallel_tests(self, test_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Executar testes em paralelo em ambientes isolados"""
        logger.info(f"Executando {len(test_configs)} testes em paralelo")
        
        results = []
        threads = []
        
        def run_test(config):
            try:
                # Criar ambiente
                environment = self.create_isolated_environment(config)
                
                # Preparar dados
                if "test_data" in config:
                    self.prepare_test_data(environment.env_id, config["test_data"])
                
                # Executar teste
                test_result = self._execute_test_suite(environment, config["test_suite"])
                
                results.append({
                    "env_id": environment.env_id,
                    "config": config,
                    "result": test_result,
                    "status": "success"
                })
                
            except Exception as e:
                results.append({
                    "env_id": None,
                    "config": config,
                    "result": None,
                    "status": "error",
                    "error": str(e)
                })
            
            finally:
                # Limpar ambiente
                if 'environment' in locals():
                    self.cleanup_environment(environment.env_id)
        
        # Iniciar threads
        for config in test_configs:
            thread = threading.Thread(target=run_test, args=(config,))
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        return results
    
    def _execute_test_suite(self, environment: TestEnvironment, test_suite: str) -> Dict[str, Any]:
        """Executar suite de testes em ambiente específico"""
        logger.info(f"Executando suite de testes: {test_suite}")
        
        try:
            container = self.docker_manager.client.containers.get(
                environment.docker_container_id
            )
            
            # Aguardar ambiente estar pronto
            self._wait_for_environment_ready(environment)
            
            # Executar testes
            test_cmd = f"python -m pytest {test_suite} -v --json-report --json-report-file=/tmp/test_result.json"
            
            result = container.exec_run(test_cmd, workdir="/app")
            
            # Obter resultado JSON
            json_result = container.exec_run("cat /tmp/test_result.json")
            
            if json_result.exit_code == 0:
                test_data = json.loads(json_result.output.decode())
                return {
                    "exit_code": result.exit_code,
                    "output": result.output.decode(),
                    "test_data": test_data,
                    "success": result.exit_code == 0
                }
            else:
                return {
                    "exit_code": result.exit_code,
                    "output": result.output.decode(),
                    "success": False
                }
        
        except Exception as e:
            logger.error(f"Erro ao executar testes: {e}")
            return {
                "exit_code": -1,
                "error": str(e),
                "success": False
            }
    
    def _wait_for_environment_ready(self, environment: TestEnvironment, timeout: int = 120):
        """Aguardar ambiente estar completamente pronto"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                container = self.docker_manager.client.containers.get(
                    environment.docker_container_id
                )
                
                # Verificar se todos os serviços estão prontos
                health_check = container.exec_run("curl -f http://localhost:8000/health")
                db_check = container.exec_run("pg_isready -h localhost -p 5432")
                
                if health_check.exit_code == 0 and db_check.exit_code == 0:
                    return True
                
            except Exception:
                pass
            
            time.sleep(2)
        
        raise Exception(f"Ambiente não ficou pronto em {timeout} segundos")
    
    def cleanup_environment(self, env_id: str):
        """Limpar ambiente de teste"""
        if env_id not in self.environments:
            return
        
        logger.info(f"Limpando ambiente: {env_id}")
        
        environment = self.environments[env_id]
        
        try:
            # Destruir ambiente Docker
            self.docker_manager.destroy_environment(env_id)
            
            # Remover do registro
            del self.environments[env_id]
            
        except Exception as e:
            logger.error(f"Erro ao limpar ambiente: {e}")
    
    def start_cleanup_service(self, cleanup_interval: int = 3600):
        """Iniciar serviço de limpeza automática"""
        self.running = True
        
        def cleanup_loop():
            while self.running:
                try:
                    # Limpar ambientes antigos (mais de 2 horas)
                    cutoff_time = datetime.now() - timedelta(hours=2)
                    
                    to_cleanup = []
                    for env_id, env in self.environments.items():
                        if env.last_used < cutoff_time:
                            to_cleanup.append(env_id)
                    
                    for env_id in to_cleanup:
                        self.cleanup_environment(env_id)
                    
                    # Limpar snapshots antigos
                    self.db_manager.cleanup_old_snapshots()
                    
                    time.sleep(cleanup_interval)
                    
                except Exception as e:
                    logger.error(f"Erro no serviço de limpeza: {e}")
                    time.sleep(300)  # 5 minutos em caso de erro
        
        self.cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        logger.info("Serviço de limpeza automática iniciado")
    
    def stop_cleanup_service(self):
        """Parar serviço de limpeza"""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        logger.info("Serviço de limpeza parado")
    
    def get_environment_stats(self) -> Dict[str, Any]:
        """Obter estatísticas dos ambientes"""
        active_envs = len([e for e in self.environments.values() if e.status == "running"])
        
        return {
            "total_environments": len(self.environments),
            "active_environments": active_envs,
            "snapshots_count": len(self.db_manager.snapshots),
            "resource_usage": self._get_resource_usage()
        }
    
    def _get_resource_usage(self) -> Dict[str, Any]:
        """Calcular uso de recursos"""
        total_memory = 0
        total_cpu = 0
        
        for env in self.environments.values():
            if env.status == "running":
                memory_str = env.resource_limits.get("memory", "0m")
                memory_mb = int(memory_str.replace("m", "").replace("g", "000"))
                total_memory += memory_mb
                
                cpu_quota = env.resource_limits.get("cpu_quota", 0)
                total_cpu += cpu_quota / 100000  # Converter para porcentagem
        
        return {
            "total_memory_mb": total_memory,
            "total_cpu_percent": total_cpu,
            "system_memory_percent": psutil.virtual_memory().percent,
            "system_cpu_percent": psutil.cpu_percent()
        }


def main():
    """Função principal para testar o sistema"""
    # Configuração do banco
    db_config = {
        "host": "localhost",
        "port": 5432,
        "username": "postgres",
        "password": "test_password",
        "database": "techze_test"
    }
    
    # Inicializar gerenciador
    manager = TestEnvironmentManager(db_config)
    
    try:
        # Criar ambiente de teste
        config = {
            "name": "Integration Test Environment",
            "ports": [8000, 5432],
            "create_db_snapshot": True,
            "memory_limit": "1g"
        }
        
        environment = manager.create_isolated_environment(config)
        
        print(f"Ambiente criado: {environment.env_id}")
        print(f"Portas: {environment.port_mappings}")
        
        # Simular uso por 30 segundos
        time.sleep(30)
        
        # Limpar
        manager.cleanup_environment(environment.env_id)
        
        print("Teste concluído com sucesso")
        
    except Exception as e:
        logger.error(f"Erro no teste: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 