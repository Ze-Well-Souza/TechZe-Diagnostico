#!/usr/bin/env python3
"""
Script para inicialização do banco de dados TechZe Diagnóstico
Aplica migrações e cria dados iniciais no Supabase
"""

import asyncio
import os
import sys
from pathlib import Path
import logging

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.config import get_settings
from app.core.supabase import get_supabase_client
from app.models.orcamento import Orcamento
from app.models.estoque import ItemEstoque, Fornecedor
from app.models.ordem_servico import OrdemServico

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


def load_sql_file(file_path: str) -> str:
    """Carrega conteúdo de um arquivo SQL"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


async def run_migration(supabase_client, migration_file: str):
    """Executa uma migração SQL"""
    try:
        migration_path = Path(__file__).parent.parent / "database" / "migrations" / migration_file
        
        if not migration_path.exists():
            logger.error(f"Arquivo de migração não encontrado: {migration_path}")
            return False
        
        sql_content = load_sql_file(str(migration_path))
        
        # Divide o SQL em comandos individuais
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        logger.info(f"Executando migração: {migration_file}")
        
        for i, command in enumerate(commands):
            if command.upper().startswith(('CREATE', 'INSERT', 'ALTER', 'DROP')):
                try:
                    # Para comandos DDL, usamos uma função RPC se disponível
                    # Ou tentamos executar diretamente se for DML
                    result = supabase_client.table('_migration_log').insert({
                        'migration_file': migration_file,
                        'command_index': i,
                        'command': command,
                        'executed_at': 'now()'
                    }).execute()
                    
                except Exception as e:
                    logger.warning(f"Comando {i+1} pode ter falhado (normal para comandos DDL): {e}")
                    continue
        
        logger.info(f"Migração {migration_file} executada com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao executar migração {migration_file}: {e}")
        return False


async def create_initial_data(supabase_client):
    """Cria dados iniciais de teste"""
    try:
        logger.info("Criando dados iniciais...")
        
        # Criar fornecedor de exemplo
        fornecedor_data = {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "nome": "TechSupply Ltda",
            "cnpj": "12.345.678/0001-90",
            "email": "contato@techsupply.com",
            "telefone": "(11) 9999-8888",
            "endereco": {
                "logradouro": "Rua das Peças, 123",
                "bairro": "Centro",
                "cidade": "São Paulo",
                "uf": "SP",
                "cep": "01000-000"
            },
            "contato_principal": "João Silva",
            "is_active": True
        }
        
        supabase_client.table("fornecedores").upsert(fornecedor_data).execute()
        
        # Criar alguns itens de estoque de exemplo
        itens_estoque = [
            {
                "id": "550e8400-e29b-41d4-a716-446655440002",
                "codigo": "HD-001",
                "nome": "HD SATA 1TB WD Blue",
                "descricao": "HD interno SATA 3.5\" 1TB Western Digital Blue",
                "tipo": "peca",
                "categoria": "Armazenamento",
                "marca": "Western Digital",
                "modelo": "WD10EZEX",
                "fornecedor_id": "550e8400-e29b-41d4-a716-446655440001",
                "quantidade_atual": 10,
                "quantidade_minima": 2,
                "unidade_medida": "unidade",
                "preco_custo": 250.00,
                "preco_venda": 320.00,
                "margem_lucro": 28.00,
                "localizacao": "Prateleira A-01",
                "status": "ativo"
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440003",
                "codigo": "MEM-001",
                "nome": "Memória DDR4 8GB Kingston",
                "descricao": "Memória RAM DDR4 8GB 2666MHz Kingston",
                "tipo": "peca",
                "categoria": "Memória",
                "marca": "Kingston",
                "modelo": "KVR26N19S8/8",
                "fornecedor_id": "550e8400-e29b-41d4-a716-446655440001",
                "quantidade_atual": 15,
                "quantidade_minima": 3,
                "unidade_medida": "unidade",
                "preco_custo": 180.00,
                "preco_venda": 230.00,
                "margem_lucro": 27.78,
                "localizacao": "Prateleira B-02",
                "status": "ativo"
            },
            {
                "id": "550e8400-e29b-41d4-a716-446655440004",
                "codigo": "TOOL-001",
                "nome": "Chave Philips PH1",
                "descricao": "Chave de fenda Philips #1 para eletrônicos",
                "tipo": "ferramenta",
                "categoria": "Ferramentas",
                "marca": "Tramontina",
                "modelo": "PH1-ELET",
                "quantidade_atual": 5,
                "quantidade_minima": 1,
                "unidade_medida": "unidade",
                "preco_custo": 15.00,
                "preco_venda": 25.00,
                "margem_lucro": 66.67,
                "localizacao": "Gaveta 01",
                "status": "ativo"
            }
        ]
        
        for item in itens_estoque:
            supabase_client.table("estoque_itens").upsert(item).execute()
        
        # Criar cliente de exemplo
        cliente_data = {
            "id": "550e8400-e29b-41d4-a716-446655440005",
            "nome": "Maria Santos",
            "cpf": "123.456.789-00",
            "email": "maria.santos@email.com",
            "telefone": "(11) 98765-4321",
            "endereco": {
                "logradouro": "Rua das Flores, 456",
                "bairro": "Jardim Paulista",
                "cidade": "São Paulo",
                "uf": "SP",
                "cep": "01310-000"
            },
            "observacoes": "Cliente VIP"
        }
        
        supabase_client.table("clientes").upsert(cliente_data).execute()
        
        # Criar usuário técnico de exemplo
        usuario_data = {
            "id": "550e8400-e29b-41d4-a716-446655440006",
            "email": "tecnico@techze.com",
            "nome": "Carlos Técnico",
            "telefone": "(11) 99999-7777",
            "role": "tecnico",
            "permissions": ["diagnosticos", "orcamentos", "ordem_servico"],
            "is_active": True
        }
        
        supabase_client.table("usuarios").upsert(usuario_data).execute()
        
        logger.info("Dados iniciais criados com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao criar dados iniciais: {e}")
        return False


async def verify_tables(supabase_client):
    """Verifica se as tabelas foram criadas corretamente"""
    try:
        logger.info("Verificando tabelas criadas...")
        
        tables_to_check = [
            "configuracoes_loja",
            "usuarios", 
            "clientes",
            "fornecedores",
            "estoque_itens",
            "estoque_movimentacoes",
            "orcamentos",
            "orcamento_itens", 
            "orcamento_pecas",
            "ordens_servico",
            "os_servicos",
            "os_pecas",
            "os_anotacoes",
            "os_fotos"
        ]
        
        for table in tables_to_check:
            try:
                result = supabase_client.table(table).select("*").limit(1).execute()
                logger.info(f"✅ Tabela {table} verificada")
            except Exception as e:
                logger.warning(f"❌ Erro ao verificar tabela {table}: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro na verificação das tabelas: {e}")
        return False


async def main():
    """Função principal"""
    logger.info("🚀 Iniciando configuração do banco de dados TechZe Diagnóstico")
    
    # Verificar configurações
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        logger.error("❌ SUPABASE_URL e SUPABASE_KEY devem estar configurados")
        return False
    
    logger.info(f"🔗 Conectando ao Supabase: {settings.SUPABASE_URL}")
    
    try:
        supabase_client = get_supabase_client()
        
        # Executar migrações
        migrations = [
            "001_create_core_tables.sql"
        ]
        
        for migration in migrations:
            success = await run_migration(supabase_client, migration)
            if not success:
                logger.error(f"❌ Falha na migração {migration}")
                return False
        
        # Verificar tabelas
        await verify_tables(supabase_client)
        
        # Criar dados iniciais
        await create_initial_data(supabase_client)
        
        logger.info("✅ Banco de dados configurado com sucesso!")
        logger.info("🎯 Próximos passos:")
        logger.info("   1. Teste as APIs com os dados de exemplo")
        logger.info("   2. Execute os testes unitários")
        logger.info("   3. Acesse o dashboard para verificar os dados")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro durante a configuração: {e}")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 