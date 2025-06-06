#!/bin/bash

# =============================================================================
# TechZe Diagnostic Service - Sistema de Backup Automático
# =============================================================================
# Este script implementa um sistema completo de backup automático para:
# - Banco de dados PostgreSQL
# - Arquivos de configuração
# - Logs de aplicação
# - Métricas e dados de monitoramento
# =============================================================================

set -euo pipefail

# Configurações
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_BASE_DIR="${BACKUP_BASE_DIR:-/var/backups/techze-diagnostic}"
LOG_FILE="${LOG_FILE:-$BACKUP_BASE_DIR/backup.log}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
S3_BUCKET="${S3_BUCKET:-techze-diagnostic-backups}"
ENCRYPTION_KEY_FILE="${ENCRYPTION_KEY_FILE:-/etc/techze/backup.key}"

# Configurações do banco de dados
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-techze_diagnostic}"
DB_USER="${DB_USER:-postgres}"
DB_PASSWORD="${DB_PASSWORD}"

# Configurações do Redis
REDIS_HOST="${REDIS_HOST:-localhost}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_PASSWORD="${REDIS_PASSWORD}"

# Configurações de notificação
SLACK_WEBHOOK="${SLACK_WEBHOOK}"
EMAIL_RECIPIENTS="${EMAIL_RECIPIENTS}"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# =============================================================================
# FUNÇÕES UTILITÁRIAS
# =============================================================================

# Função para logging com timestamp
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
    
    case "$level" in
        "ERROR")
            echo -e "${RED}[$timestamp] [$level] $message${NC}" >&2
            ;;
        "WARN")
            echo -e "${YELLOW}[$timestamp] [$level] $message${NC}"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[$timestamp] [$level] $message${NC}"
            ;;
        "INFO")
            echo -e "${BLUE}[$timestamp] [$level] $message${NC}"
            ;;
    esac
}

# Função para verificar dependências
check_dependencies() {
    log "INFO" "Verificando dependências..."
    
    local deps=("pg_dump" "redis-cli" "aws" "gpg" "tar" "gzip")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log "ERROR" "Dependências faltando: ${missing_deps[*]}"
        log "INFO" "Instale as dependências com:"
        log "INFO" "  apt-get update && apt-get install -y postgresql-client redis-tools awscli gnupg tar gzip"
        exit 1
    fi
    
    log "SUCCESS" "Todas as dependências estão disponíveis"
}

# Função para criar diretórios de backup
setup_backup_dirs() {
    log "INFO" "Configurando diretórios de backup..."
    
    local dirs=(
        "$BACKUP_BASE_DIR"
        "$BACKUP_BASE_DIR/database"
        "$BACKUP_BASE_DIR/redis"
        "$BACKUP_BASE_DIR/config"
        "$BACKUP_BASE_DIR/logs"
        "$BACKUP_BASE_DIR/metrics"
        "$BACKUP_BASE_DIR/temp"
    )
    
    for dir in "${dirs[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            log "INFO" "Criado diretório: $dir"
        fi
    done
    
    # Configurar permissões
    chmod 750 "$BACKUP_BASE_DIR"
    chown -R postgres:postgres "$BACKUP_BASE_DIR" 2>/dev/null || true
    
    log "SUCCESS" "Diretórios de backup configurados"
}

# Função para gerar chave de criptografia se não existir
setup_encryption() {
    if [ ! -f "$ENCRYPTION_KEY_FILE" ]; then
        log "INFO" "Gerando chave de criptografia..."
        
        # Criar diretório se não existir
        mkdir -p "$(dirname "$ENCRYPTION_KEY_FILE")"
        
        # Gerar chave aleatória
        openssl rand -base64 32 > "$ENCRYPTION_KEY_FILE"
        chmod 600 "$ENCRYPTION_KEY_FILE"
        
        log "SUCCESS" "Chave de criptografia gerada: $ENCRYPTION_KEY_FILE"
        log "WARN" "IMPORTANTE: Faça backup seguro desta chave!"
    fi
}

# Função para criptografar arquivo
encrypt_file() {
    local input_file="$1"
    local output_file="$2"
    
    if [ ! -f "$ENCRYPTION_KEY_FILE" ]; then
        log "ERROR" "Chave de criptografia não encontrada: $ENCRYPTION_KEY_FILE"
        return 1
    fi
    
    gpg --batch --yes --cipher-algo AES256 --compress-algo 2 \
        --symmetric --passphrase-file "$ENCRYPTION_KEY_FILE" \
        --output "$output_file" "$input_file"
    
    if [ $? -eq 0 ]; then
        log "SUCCESS" "Arquivo criptografado: $output_file"
        rm -f "$input_file"  # Remove arquivo original
        return 0
    else
        log "ERROR" "Falha ao criptografar arquivo: $input_file"
        return 1
    fi
}

# =============================================================================
# FUNÇÕES DE BACKUP
# =============================================================================

# Backup do banco de dados PostgreSQL
backup_database() {
    log "INFO" "Iniciando backup do banco de dados..."
    
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$BACKUP_BASE_DIR/database/postgres_${DB_NAME}_${timestamp}.sql"
    local compressed_file="${backup_file}.gz"
    local encrypted_file="${compressed_file}.gpg"
    
    # Verificar conectividade
    if ! PGPASSWORD="$DB_PASSWORD" pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" &>/dev/null; then
        log "ERROR" "Não foi possível conectar ao banco de dados"
        return 1
    fi
    
    # Fazer backup
    log "INFO" "Executando pg_dump..."
    if PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --no-password \
        --format=custom \
        --compress=9 \
        --file="$backup_file" 2>"$BACKUP_BASE_DIR/temp/pg_dump.log"; then
        
        log "SUCCESS" "Backup do banco criado: $backup_file"
        
        # Comprimir
        gzip "$backup_file"
        log "SUCCESS" "Backup comprimido: $compressed_file"
        
        # Criptografar
        if encrypt_file "$compressed_file" "$encrypted_file"; then
            log "SUCCESS" "Backup do banco de dados concluído: $encrypted_file"
            
            # Calcular hash para verificação
            local hash=$(sha256sum "$encrypted_file" | cut -d' ' -f1)
            echo "$hash" > "${encrypted_file}.sha256"
            
            return 0
        else
            log "ERROR" "Falha ao criptografar backup do banco"
            return 1
        fi
    else
        log "ERROR" "Falha no pg_dump"
        cat "$BACKUP_BASE_DIR/temp/pg_dump.log" | while read line; do
            log "ERROR" "pg_dump: $line"
        done
        return 1
    fi
}

# Backup do Redis
backup_redis() {
    log "INFO" "Iniciando backup do Redis..."
    
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$BACKUP_BASE_DIR/redis/redis_${timestamp}.rdb"
    local compressed_file="${backup_file}.gz"
    local encrypted_file="${compressed_file}.gpg"
    
    # Verificar conectividade
    if [ -n "$REDIS_PASSWORD" ]; then
        if ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" ping &>/dev/null; then
            log "ERROR" "Não foi possível conectar ao Redis"
            return 1
        fi
    else
        if ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping &>/dev/null; then
            log "ERROR" "Não foi possível conectar ao Redis"
            return 1
        fi
    fi
    
    # Fazer backup
    log "INFO" "Executando BGSAVE no Redis..."
    if [ -n "$REDIS_PASSWORD" ]; then
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" BGSAVE
    else
        redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" BGSAVE
    fi
    
    # Aguardar conclusão do BGSAVE
    log "INFO" "Aguardando conclusão do BGSAVE..."
    while true; do
        if [ -n "$REDIS_PASSWORD" ]; then
            local status=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" LASTSAVE)
        else
            local status=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" LASTSAVE)
        fi
        
        sleep 2
        
        if [ -n "$REDIS_PASSWORD" ]; then
            local new_status=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" LASTSAVE)
        else
            local new_status=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" LASTSAVE)
        fi
        
        if [ "$status" != "$new_status" ]; then
            break
        fi
    done
    
    # Copiar arquivo RDB
    local redis_data_dir="/var/lib/redis"
    if [ -f "$redis_data_dir/dump.rdb" ]; then
        cp "$redis_data_dir/dump.rdb" "$backup_file"
        
        # Comprimir e criptografar
        gzip "$backup_file"
        if encrypt_file "$compressed_file" "$encrypted_file"; then
            log "SUCCESS" "Backup do Redis concluído: $encrypted_file"
            
            # Calcular hash
            local hash=$(sha256sum "$encrypted_file" | cut -d' ' -f1)
            echo "$hash" > "${encrypted_file}.sha256"
            
            return 0
        else
            log "ERROR" "Falha ao criptografar backup do Redis"
            return 1
        fi
    else
        log "ERROR" "Arquivo dump.rdb não encontrado"
        return 1
    fi
}

# Backup de configurações
backup_config() {
    log "INFO" "Iniciando backup de configurações..."
    
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$BACKUP_BASE_DIR/config/config_${timestamp}.tar"
    local compressed_file="${backup_file}.gz"
    local encrypted_file="${compressed_file}.gpg"
    
    # Arquivos e diretórios para backup
    local config_items=(
        "$PROJECT_ROOT/.env"
        "$PROJECT_ROOT/.env.production"
        "$PROJECT_ROOT/k8s"
        "$PROJECT_ROOT/docker-compose.yml"
        "$PROJECT_ROOT/docker-compose.prod.yml"
        "$PROJECT_ROOT/prometheus.yml"
        "$PROJECT_ROOT/grafana"
        "/etc/techze"
        "/etc/nginx/sites-available/techze-diagnostic"
    )
    
    # Criar lista de arquivos existentes
    local existing_items=()
    for item in "${config_items[@]}"; do
        if [ -e "$item" ]; then
            existing_items+=("$item")
        fi
    done
    
    if [ ${#existing_items[@]} -eq 0 ]; then
        log "WARN" "Nenhum arquivo de configuração encontrado para backup"
        return 0
    fi
    
    # Criar arquivo tar
    if tar -cf "$backup_file" "${existing_items[@]}" 2>/dev/null; then
        log "SUCCESS" "Arquivo de configuração criado: $backup_file"
        
        # Comprimir e criptografar
        gzip "$backup_file"
        if encrypt_file "$compressed_file" "$encrypted_file"; then
            log "SUCCESS" "Backup de configurações concluído: $encrypted_file"
            
            # Calcular hash
            local hash=$(sha256sum "$encrypted_file" | cut -d' ' -f1)
            echo "$hash" > "${encrypted_file}.sha256"
            
            return 0
        else
            log "ERROR" "Falha ao criptografar backup de configurações"
            return 1
        fi
    else
        log "ERROR" "Falha ao criar arquivo tar de configurações"
        return 1
    fi
}

# Backup de logs
backup_logs() {
    log "INFO" "Iniciando backup de logs..."
    
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$BACKUP_BASE_DIR/logs/logs_${timestamp}.tar"
    local compressed_file="${backup_file}.gz"
    local encrypted_file="${compressed_file}.gpg"
    
    # Diretórios de logs
    local log_dirs=(
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/microservices/diagnostic_service/logs"
        "/var/log/techze-diagnostic"
        "/var/log/nginx"
        "/var/log/postgresql"
    )
    
    # Criar lista de diretórios existentes
    local existing_dirs=()
    for dir in "${log_dirs[@]}"; do
        if [ -d "$dir" ]; then
            existing_dirs+=("$dir")
        fi
    done
    
    if [ ${#existing_dirs[@]} -eq 0 ]; then
        log "WARN" "Nenhum diretório de logs encontrado para backup"
        return 0
    fi
    
    # Criar arquivo tar (apenas logs dos últimos 7 dias)
    if find "${existing_dirs[@]}" -name "*.log" -mtime -7 -print0 | tar -czf "$compressed_file" --null -T - 2>/dev/null; then
        log "SUCCESS" "Backup de logs criado: $compressed_file"
        
        # Criptografar
        if encrypt_file "$compressed_file" "$encrypted_file"; then
            log "SUCCESS" "Backup de logs concluído: $encrypted_file"
            
            # Calcular hash
            local hash=$(sha256sum "$encrypted_file" | cut -d' ' -f1)
            echo "$hash" > "${encrypted_file}.sha256"
            
            return 0
        else
            log "ERROR" "Falha ao criptografar backup de logs"
            return 1
        fi
    else
        log "WARN" "Nenhum log recente encontrado ou falha ao criar arquivo"
        return 0
    fi
}

# =============================================================================
# FUNÇÕES DE UPLOAD E LIMPEZA
# =============================================================================

# Upload para S3
upload_to_s3() {
    log "INFO" "Iniciando upload para S3..."
    
    if [ -z "$S3_BUCKET" ]; then
        log "WARN" "Bucket S3 não configurado, pulando upload"
        return 0
    fi
    
    # Verificar se AWS CLI está configurado
    if ! aws sts get-caller-identity &>/dev/null; then
        log "ERROR" "AWS CLI não está configurado corretamente"
        return 1
    fi
    
    local timestamp=$(date '+%Y/%m/%d')
    local upload_count=0
    local failed_count=0
    
    # Upload de todos os arquivos .gpg
    find "$BACKUP_BASE_DIR" -name "*.gpg" -type f | while read -r file; do
        local relative_path=$(realpath --relative-to="$BACKUP_BASE_DIR" "$file")
        local s3_key="$timestamp/$relative_path"
        
        log "INFO" "Uploading: $file -> s3://$S3_BUCKET/$s3_key"
        
        if aws s3 cp "$file" "s3://$S3_BUCKET/$s3_key" --storage-class STANDARD_IA; then
            log "SUCCESS" "Upload concluído: $s3_key"
            ((upload_count++))
            
            # Upload do hash também
            if [ -f "${file}.sha256" ]; then
                aws s3 cp "${file}.sha256" "s3://$S3_BUCKET/${s3_key}.sha256" --storage-class STANDARD_IA
            fi
        else
            log "ERROR" "Falha no upload: $file"
            ((failed_count++))
        fi
    done
    
    log "INFO" "Upload concluído: $upload_count sucessos, $failed_count falhas"
    
    if [ $failed_count -eq 0 ]; then
        return 0
    else
        return 1
    fi
}

# Limpeza de backups antigos
cleanup_old_backups() {
    log "INFO" "Iniciando limpeza de backups antigos..."
    
    # Limpeza local
    local deleted_count=0
    
    find "$BACKUP_BASE_DIR" -name "*.gpg" -type f -mtime +"$RETENTION_DAYS" | while read -r file; do
        log "INFO" "Removendo backup antigo: $file"
        rm -f "$file" "${file}.sha256"
        ((deleted_count++))
    done
    
    log "INFO" "Removidos $deleted_count backups locais antigos"
    
    # Limpeza no S3
    if [ -n "$S3_BUCKET" ] && aws sts get-caller-identity &>/dev/null; then
        log "INFO" "Limpando backups antigos no S3..."
        
        local cutoff_date=$(date -d "$RETENTION_DAYS days ago" '+%Y-%m-%d')
        
        aws s3api list-objects-v2 --bucket "$S3_BUCKET" --query "Contents[?LastModified<='$cutoff_date'].Key" --output text | \
        while read -r key; do
            if [ -n "$key" ] && [ "$key" != "None" ]; then
                log "INFO" "Removendo do S3: $key"
                aws s3 rm "s3://$S3_BUCKET/$key"
            fi
        done
    fi
    
    log "SUCCESS" "Limpeza de backups antigos concluída"
}

# =============================================================================
# FUNÇÕES DE NOTIFICAÇÃO
# =============================================================================

# Enviar notificação Slack
send_slack_notification() {
    local status="$1"
    local message="$2"
    
    if [ -z "$SLACK_WEBHOOK" ]; then
        return 0
    fi
    
    local color="good"
    local emoji=":white_check_mark:"
    
    if [ "$status" = "error" ]; then
        color="danger"
        emoji=":x:"
    elif [ "$status" = "warning" ]; then
        color="warning"
        emoji=":warning:"
    fi
    
    local payload=$(cat <<EOF
{
    "attachments": [
        {
            "color": "$color",
            "title": "$emoji TechZe Diagnostic - Backup Status",
            "text": "$message",
            "fields": [
                {
                    "title": "Servidor",
                    "value": "$(hostname)",
                    "short": true
                },
                {
                    "title": "Timestamp",
                    "value": "$(date '+%Y-%m-%d %H:%M:%S')",
                    "short": true
                }
            ]
        }
    ]
}
EOF
    )
    
    curl -X POST -H 'Content-type: application/json' \
        --data "$payload" \
        "$SLACK_WEBHOOK" &>/dev/null
}

# Enviar notificação por email
send_email_notification() {
    local status="$1"
    local message="$2"
    
    if [ -z "$EMAIL_RECIPIENTS" ]; then
        return 0
    fi
    
    local subject="TechZe Diagnostic - Backup $status"
    
    local body=$(cat <<EOF
TechZe Diagnostic Service - Relatório de Backup

Status: $status
Servidor: $(hostname)
Data/Hora: $(date '+%Y-%m-%d %H:%M:%S')

Detalhes:
$message

Logs completos disponíveis em: $LOG_FILE

--
Sistema de Backup Automático
TechZe Diagnostic Service
EOF
    )
    
    echo "$body" | mail -s "$subject" "$EMAIL_RECIPIENTS" 2>/dev/null || true
}

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

# Função principal de backup
run_backup() {
    local start_time=$(date +%s)
    local backup_status="success"
    local backup_summary=""
    local failed_components=()
    
    log "INFO" "=== Iniciando processo de backup ==="
    log "INFO" "Timestamp: $(date '+%Y-%m-%d %H:%M:%S')"
    log "INFO" "Servidor: $(hostname)"
    log "INFO" "Usuário: $(whoami)"
    
    # Verificar dependências
    if ! check_dependencies; then
        backup_status="error"
        backup_summary="Dependências faltando"
        send_slack_notification "$backup_status" "$backup_summary"
        send_email_notification "$backup_status" "$backup_summary"
        exit 1
    fi
    
    # Configurar ambiente
    setup_backup_dirs
    setup_encryption
    
    # Executar backups
    log "INFO" "Executando backups dos componentes..."
    
    # Backup do banco de dados
    if backup_database; then
        log "SUCCESS" "✅ Backup do banco de dados concluído"
        backup_summary+="✅ Database: OK\n"
    else
        log "ERROR" "❌ Falha no backup do banco de dados"
        backup_summary+="❌ Database: FAILED\n"
        failed_components+=("Database")
        backup_status="error"
    fi
    
    # Backup do Redis
    if backup_redis; then
        log "SUCCESS" "✅ Backup do Redis concluído"
        backup_summary+="✅ Redis: OK\n"
    else
        log "ERROR" "❌ Falha no backup do Redis"
        backup_summary+="❌ Redis: FAILED\n"
        failed_components+=("Redis")
        if [ "$backup_status" != "error" ]; then
            backup_status="warning"
        fi
    fi
    
    # Backup de configurações
    if backup_config; then
        log "SUCCESS" "✅ Backup de configurações concluído"
        backup_summary+="✅ Config: OK\n"
    else
        log "ERROR" "❌ Falha no backup de configurações"
        backup_summary+="❌ Config: FAILED\n"
        failed_components+=("Config")
        if [ "$backup_status" != "error" ]; then
            backup_status="warning"
        fi
    fi
    
    # Backup de logs
    if backup_logs; then
        log "SUCCESS" "✅ Backup de logs concluído"
        backup_summary+="✅ Logs: OK\n"
    else
        log "ERROR" "❌ Falha no backup de logs"
        backup_summary+="❌ Logs: FAILED\n"
        failed_components+=("Logs")
        if [ "$backup_status" != "error" ]; then
            backup_status="warning"
        fi
    fi
    
    # Upload para S3
    if upload_to_s3; then
        log "SUCCESS" "✅ Upload para S3 concluído"
        backup_summary+="✅ S3 Upload: OK\n"
    else
        log "ERROR" "❌ Falha no upload para S3"
        backup_summary+="❌ S3 Upload: FAILED\n"
        failed_components+=("S3 Upload")
        if [ "$backup_status" != "error" ]; then
            backup_status="warning"
        fi
    fi
    
    # Limpeza de backups antigos
    if cleanup_old_backups; then
        log "SUCCESS" "✅ Limpeza de backups antigos concluída"
        backup_summary+="✅ Cleanup: OK\n"
    else
        log "ERROR" "❌ Falha na limpeza de backups antigos"
        backup_summary+="❌ Cleanup: FAILED\n"
        failed_components+=("Cleanup")
        if [ "$backup_status" != "error" ]; then
            backup_status="warning"
        fi
    fi
    
    # Calcular tempo total
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    local duration_formatted=$(printf '%02d:%02d:%02d' $((duration/3600)) $((duration%3600/60)) $((duration%60)))
    
    # Resumo final
    log "INFO" "=== Processo de backup concluído ==="
    log "INFO" "Status: $backup_status"
    log "INFO" "Duração: $duration_formatted"
    
    if [ ${#failed_components[@]} -gt 0 ]; then
        log "WARN" "Componentes com falha: ${failed_components[*]}"
        backup_summary+="\nComponentes com falha: ${failed_components[*]}\n"
    fi
    
    backup_summary+="\nDuração: $duration_formatted"
    
    # Enviar notificações
    send_slack_notification "$backup_status" "$backup_summary"
    send_email_notification "$backup_status" "$backup_summary"
    
    # Retornar código de saída apropriado
    if [ "$backup_status" = "error" ]; then
        exit 1
    elif [ "$backup_status" = "warning" ]; then
        exit 2
    else
        exit 0
    fi
}

# =============================================================================
# EXECUÇÃO
# =============================================================================

# Verificar se está sendo executado como script principal
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    # Processar argumentos da linha de comando
    case "${1:-backup}" in
        "backup")
            run_backup
            ;;
        "test")
            log "INFO" "Executando teste de dependências..."
            check_dependencies
            setup_backup_dirs
            setup_encryption
            log "SUCCESS" "Teste concluído com sucesso"
            ;;
        "cleanup")
            log "INFO" "Executando apenas limpeza..."
            setup_backup_dirs
            cleanup_old_backups
            ;;
        "help")
            echo "Uso: $0 [backup|test|cleanup|help]"
            echo ""
            echo "Comandos:"
            echo "  backup  - Executar backup completo (padrão)"
            echo "  test    - Testar configuração e dependências"
            echo "  cleanup - Executar apenas limpeza de backups antigos"
            echo "  help    - Mostrar esta ajuda"
            echo ""
            echo "Variáveis de ambiente:"
            echo "  BACKUP_BASE_DIR     - Diretório base para backups (padrão: /var/backups/techze-diagnostic)"
            echo "  RETENTION_DAYS      - Dias para manter backups (padrão: 30)"
            echo "  S3_BUCKET          - Bucket S3 para upload"
            echo "  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD - Configurações do PostgreSQL"
            echo "  REDIS_HOST, REDIS_PORT, REDIS_PASSWORD - Configurações do Redis"
            echo "  SLACK_WEBHOOK      - Webhook para notificações Slack"
            echo "  EMAIL_RECIPIENTS   - Emails para notificações"
            ;;
        *)
            log "ERROR" "Comando inválido: $1"
            log "INFO" "Use '$0 help' para ver os comandos disponíveis"
            exit 1
            ;;
    esac
fi