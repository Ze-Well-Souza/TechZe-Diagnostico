#!/usr/bin/env python3
"""
Backup Scheduler - TechZe Diagnóstico
Sistema automatizado de backup com agendamento
Agente CURSOR - Proteção de dados 24/7
"""

import os
import sys
import time
import gzip
import shutil
import subprocess
import json
import schedule
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import boto3
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backup.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BackupScheduler:
    """Agendador automático de backups"""
    
    def __init__(self):
        self.config = {
            # Configurações de banco
            "db_host": os.getenv("DB_HOST", "localhost"),
            "db_port": os.getenv("DB_PORT", "5432"),
            "db_name": os.getenv("DB_NAME", "techze_prod"),
            "db_user": os.getenv("DB_USER", "postgres"),
            "db_password": os.getenv("DB_PASSWORD"),
            
            # Configurações de backup
            "backup_dir": "backups",
            "temp_dir": "temp_backups",
            "retention_days": {
                "daily": 7,
                "weekly": 4,
                "monthly": 12
            },
            
            # Configurações AWS S3 (opcional)
            "aws_access_key": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "s3_bucket": os.getenv("S3_BACKUP_BUCKET"),
            "s3_region": os.getenv("AWS_REGION", "us-east-1"),
            
            # Configurações de notificação
            "webhook_url": os.getenv("BACKUP_WEBHOOK_URL"),
            "alert_email": os.getenv("BACKUP_ALERT_EMAIL"),
        }
        
        self.setup_directories()
        self.setup_s3_client()
    
    def setup_directories(self):
        """Criar diretórios necessários"""
        for dir_name in [self.config["backup_dir"], self.config["temp_dir"], "logs"]:
            os.makedirs(dir_name, exist_ok=True)
    
    def setup_s3_client(self):
        """Configurar cliente S3"""
        if self.config["aws_access_key"] and self.config["aws_secret_key"]:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.config["aws_access_key"],
                aws_secret_access_key=self.config["aws_secret_key"],
                region_name=self.config["s3_region"]
            )
        else:
            self.s3_client = None
            logger.warning("AWS credentials not configured - S3 backup disabled")
    
    def create_database_backup(self, backup_type: str = "daily") -> Dict[str, Any]:
        """Criar backup do banco de dados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"techze_db_{backup_type}_{timestamp}.sql"
        backup_path = os.path.join(self.config["temp_dir"], backup_filename)
        
        try:
            logger.info(f"Iniciando backup {backup_type} do banco de dados...")
            
            # Comando pg_dump
            cmd = [
                "pg_dump",
                "-h", self.config["db_host"],
                "-p", self.config["db_port"],
                "-U", self.config["db_user"],
                "-d", self.config["db_name"],
                "-f", backup_path,
                "--no-password",
                "--verbose"
            ]
            
            # Configurar variável de ambiente para senha
            env = os.environ.copy()
            env["PGPASSWORD"] = self.config["db_password"]
            
            start_time = time.time()
            
            # Executar backup
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hora timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode != 0:
                raise Exception(f"pg_dump failed: {result.stderr}")
            
            # Obter tamanho do arquivo
            file_size = os.path.getsize(backup_path)
            
            # Comprimir backup
            compressed_path = f"{backup_path}.gz"
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remover arquivo não comprimido
            os.remove(backup_path)
            
            compressed_size = os.path.getsize(compressed_path)
            compression_ratio = (1 - compressed_size / file_size) * 100
            
            backup_info = {
                "filename": f"{backup_filename}.gz",
                "path": compressed_path,
                "type": backup_type,
                "timestamp": timestamp,
                "duration_seconds": round(duration, 2),
                "original_size_mb": round(file_size / 1024 / 1024, 2),
                "compressed_size_mb": round(compressed_size / 1024 / 1024, 2),
                "compression_ratio": round(compression_ratio, 2),
                "status": "success"
            }
            
            logger.info(f"Backup concluído: {backup_info['filename']} "
                       f"({backup_info['compressed_size_mb']}MB, "
                       f"{backup_info['compression_ratio']}% compressão)")
            
            return backup_info
            
        except Exception as e:
            logger.error(f"Erro no backup do banco: {e}")
            return {
                "type": backup_type,
                "timestamp": timestamp,
                "status": "failed",
                "error": str(e)
            }
    
    def create_files_backup(self, backup_type: str = "daily") -> Dict[str, Any]:
        """Criar backup dos arquivos da aplicação"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"techze_files_{backup_type}_{timestamp}.tar.gz"
        backup_path = os.path.join(self.config["temp_dir"], backup_filename)
        
        try:
            logger.info(f"Iniciando backup {backup_type} dos arquivos...")
            
            # Diretórios para backup
            dirs_to_backup = [
                "config",
                "logs",
                "uploads",
                "static",
                ".env",
                "docker-compose.yml"
            ]
            
            # Filtrar diretórios que existem
            existing_dirs = [d for d in dirs_to_backup if os.path.exists(d)]
            
            start_time = time.time()
            
            # Criar tar.gz
            cmd = ["tar", "-czf", backup_path] + existing_dirs
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutos timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode != 0:
                raise Exception(f"tar failed: {result.stderr}")
            
            file_size = os.path.getsize(backup_path)
            
            backup_info = {
                "filename": backup_filename,
                "path": backup_path,
                "type": backup_type,
                "timestamp": timestamp,
                "duration_seconds": round(duration, 2),
                "size_mb": round(file_size / 1024 / 1024, 2),
                "directories": existing_dirs,
                "status": "success"
            }
            
            logger.info(f"Backup de arquivos concluído: {backup_info['filename']} "
                       f"({backup_info['size_mb']}MB)")
            
            return backup_info
            
        except Exception as e:
            logger.error(f"Erro no backup de arquivos: {e}")
            return {
                "type": backup_type,
                "timestamp": timestamp,
                "status": "failed",
                "error": str(e)
            }
    
    def upload_to_s3(self, backup_info: Dict[str, Any]) -> bool:
        """Upload backup para S3"""
        if not self.s3_client or not self.config["s3_bucket"]:
            return False
        
        try:
            s3_key = f"backups/{backup_info['type']}/{backup_info['filename']}"
            
            logger.info(f"Enviando {backup_info['filename']} para S3...")
            
            self.s3_client.upload_file(
                backup_info['path'],
                self.config["s3_bucket"],
                s3_key,
                ExtraArgs={'StorageClass': 'STANDARD_IA'}  # Armazenamento econômico
            )
            
            backup_info['s3_key'] = s3_key
            backup_info['s3_bucket'] = self.config["s3_bucket"]
            
            logger.info(f"Upload para S3 concluído: s3://{self.config['s3_bucket']}/{s3_key}")
            return True
            
        except Exception as e:
            logger.error(f"Erro no upload para S3: {e}")
            backup_info['s3_error'] = str(e)
            return False
    
    def move_to_storage(self, backup_info: Dict[str, Any]):
        """Mover backup para armazenamento permanente"""
        storage_dir = os.path.join(self.config["backup_dir"], backup_info["type"])
        os.makedirs(storage_dir, exist_ok=True)
        
        storage_path = os.path.join(storage_dir, backup_info["filename"])
        
        try:
            shutil.move(backup_info["path"], storage_path)
            backup_info["storage_path"] = storage_path
            logger.info(f"Backup movido para: {storage_path}")
        except Exception as e:
            logger.error(f"Erro ao mover backup: {e}")
    
    def cleanup_old_backups(self, backup_type: str):
        """Limpar backups antigos"""
        retention_days = self.config["retention_days"].get(backup_type, 7)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        backup_dir = os.path.join(self.config["backup_dir"], backup_type)
        if not os.path.exists(backup_dir):
            return
        
        deleted_count = 0
        
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            
            try:
                # Extrair timestamp do nome do arquivo
                if backup_type in filename and "_" in filename:
                    timestamp_str = filename.split("_")[2].split(".")[0]  # YYYYMMDD_HHMMSS
                    file_date = datetime.strptime(timestamp_str.split("_")[0], "%Y%m%d")
                    
                    if file_date < cutoff_date:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"Backup antigo removido: {filename}")
                        
            except Exception as e:
                logger.warning(f"Erro ao processar {filename}: {e}")
        
        if deleted_count > 0:
            logger.info(f"Limpeza concluída: {deleted_count} backups {backup_type} removidos")
    
    def cleanup_s3_backups(self, backup_type: str):
        """Limpar backups antigos no S3"""
        if not self.s3_client:
            return
        
        retention_days = self.config["retention_days"].get(backup_type, 7)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            prefix = f"backups/{backup_type}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.config["s3_bucket"],
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return
            
            deleted_count = 0
            
            for obj in response['Contents']:
                if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                    self.s3_client.delete_object(
                        Bucket=self.config["s3_bucket"],
                        Key=obj['Key']
                    )
                    deleted_count += 1
                    logger.info(f"Backup S3 antigo removido: {obj['Key']}")
            
            if deleted_count > 0:
                logger.info(f"Limpeza S3 concluída: {deleted_count} backups {backup_type} removidos")
                
        except Exception as e:
            logger.error(f"Erro na limpeza S3: {e}")
    
    def send_notification(self, backup_results: List[Dict[str, Any]]):
        """Enviar notificação do resultado do backup"""
        try:
            successful_backups = [b for b in backup_results if b["status"] == "success"]
            failed_backups = [b for b in backup_results if b["status"] == "failed"]
            
            message = {
                "timestamp": datetime.now().isoformat(),
                "total_backups": len(backup_results),
                "successful": len(successful_backups),
                "failed": len(failed_backups),
                "status": "success" if not failed_backups else "partial" if successful_backups else "failed"
            }
            
            if self.config["webhook_url"]:
                import requests
                requests.post(self.config["webhook_url"], json=message, timeout=10)
            
            logger.info(f"Backup summary: {message['successful']}/{message['total_backups']} successful")
            
        except Exception as e:
            logger.error(f"Erro ao enviar notificação: {e}")
    
    def save_backup_log(self, backup_results: List[Dict[str, Any]]):
        """Salvar log do backup"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "backups": backup_results
        }
        
        log_file = "logs/backup_history.json"
        
        # Carregar histórico existente
        history = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    history = json.load(f)
            except:
                pass
        
        # Adicionar nova entrada
        history.append(log_entry)
        
        # Manter apenas últimas 100 entradas
        history = history[-100:]
        
        # Salvar histórico atualizado
        with open(log_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def run_backup(self, backup_type: str = "daily"):
        """Executar backup completo"""
        logger.info(f"🔄 Iniciando backup {backup_type}")
        start_time = time.time()
        
        backup_results = []
        
        try:
            # Backup do banco de dados
            db_backup = self.create_database_backup(backup_type)
            backup_results.append(db_backup)
            
            if db_backup["status"] == "success":
                # Upload para S3
                self.upload_to_s3(db_backup)
                # Mover para armazenamento
                self.move_to_storage(db_backup)
            
            # Backup dos arquivos
            files_backup = self.create_files_backup(backup_type)
            backup_results.append(files_backup)
            
            if files_backup["status"] == "success":
                # Upload para S3
                self.upload_to_s3(files_backup)
                # Mover para armazenamento
                self.move_to_storage(files_backup)
            
            # Limpeza de backups antigos
            self.cleanup_old_backups(backup_type)
            self.cleanup_s3_backups(backup_type)
            
            # Notificações e logs
            self.send_notification(backup_results)
            self.save_backup_log(backup_results)
            
            duration = time.time() - start_time
            logger.info(f"✅ Backup {backup_type} concluído em {duration:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Erro no backup {backup_type}: {e}")
            backup_results.append({
                "type": backup_type,
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "status": "failed",
                "error": str(e)
            })
        
        return backup_results
    
    def schedule_backups(self):
        """Agendar backups automáticos"""
        logger.info("📅 Configurando agendamento de backups...")
        
        # Backup diário às 02:00
        schedule.every().day.at("02:00").do(self.run_backup, "daily")
        
        # Backup semanal aos domingos às 03:00
        schedule.every().sunday.at("03:00").do(self.run_backup, "weekly")
        
        # Backup mensal no dia 1 às 04:00
        schedule.every().month.do(self.run_backup, "monthly")
        
        logger.info("✅ Agendamentos configurados:")
        logger.info("  - Diário: 02:00")
        logger.info("  - Semanal: Domingo 03:00")
        logger.info("  - Mensal: Dia 1 04:00")
    
    def run_scheduler(self):
        """Executar agendador de backups"""
        self.schedule_backups()
        
        logger.info("🚀 Agendador de backups iniciado")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar a cada minuto
                
        except KeyboardInterrupt:
            logger.info("Agendador interrompido pelo usuário")


def main():
    """Função principal"""
    if len(sys.argv) > 1:
        backup_type = sys.argv[1]
        if backup_type in ["daily", "weekly", "monthly"]:
            # Executar backup manual
            scheduler = BackupScheduler()
            scheduler.run_backup(backup_type)
        else:
            print("Uso: python backup_scheduler.py [daily|weekly|monthly]")
            print("Ou execute sem argumentos para iniciar o agendador automático")
    else:
        # Executar agendador automático
        scheduler = BackupScheduler()
        scheduler.run_scheduler()


if __name__ == "__main__":
    main() 