#!/usr/bin/env python3
"""
Script para aplicar políticas RLS manualmente no Supabase
Refatorado para usar módulos centralizados
"""

from database_manager import DatabaseManager
from utils import Logger, FileManager

def create_sql_commands(db_manager: DatabaseManager):
    """Cria comandos SQL para aplicar manualmente"""
    Logger.step("GERANDO COMANDOS SQL PARA APLICAÇÃO MANUAL")
    
    sql_commands = db_manager.generate_manual_sql()
    
    # Salvar comandos em arquivo
    if FileManager.write_file('supabase_rls_commands.sql', sql_commands):
        Logger.info("Para aplicar:")
        Logger.info("1. Acesse: https://supabase.com/dashboard/project/pkefwvvkydzzfstzwppv/sql")
        Logger.info("2. Cole o conteúdo do arquivo 'supabase_rls_commands.sql'")
        Logger.info("3. Execute os comandos")
        return True
    else:
        return False


def create_verification_script():
    """Cria script para verificar se RLS foi aplicado"""
    Logger.step("CRIANDO SCRIPT DE VERIFICAÇÃO")
    
    verification_script = '''#!/usr/bin/env python3
"""
Script para verificar se as políticas RLS foram aplicadas corretamente
Refatorado para usar módulos centralizados
"""

from database_manager import DatabaseManager
from utils import Logger

def main():
    """Função principal de verificação"""
    Logger.header("VERIFICAÇÃO DE POLÍTICAS RLS")
    
    db_manager = DatabaseManager()
    verification_results = db_manager.verify_setup()
    
    if verification_results['overall_status'] == 'success':
        Logger.success("Todas as verificações passaram!")
    elif verification_results['overall_status'] == 'partial':
        Logger.warning("Verificação parcialmente bem-sucedida")
    else:
        Logger.error("Verificação falhou")
    
    Logger.info("Detalhes:")
    Logger.info(f"Conexão: {'✅' if verification_results['connection'] else '❌'}")
    
    for table, exists in verification_results['tables'].items():
        Logger.info(f"Tabela {table}: {'✅' if exists else '❌'}")

if __name__ == "__main__":
    main()
'''
    
    if FileManager.write_file('verify_rls.py', verification_script):
        Logger.info("Execute 'python verify_rls.py' após aplicar as políticas")
        return True
    else:
        return False


def main():
    """Função principal"""
    Logger.header("APLICAÇÃO MANUAL DE POLÍTICAS RLS")
    
    # Inicializar gerenciador de banco
    db_manager = DatabaseManager()
    
    # Testar conexão
    if not db_manager.test_connection():
        Logger.error("Não foi possível conectar ao Supabase")
        Logger.info("Verifique as credenciais e tente novamente")
        return
    
    # Verificar tabelas existentes
    existing_tables = db_manager.get_existing_tables()
    
    # Criar comandos SQL
    if not create_sql_commands(db_manager):
        Logger.error("Falha ao criar comandos SQL")
        return
    
    # Criar script de verificação
    if not create_verification_script():
        Logger.error("Falha ao criar script de verificação")
        return
    
    # Instruções finais
    Logger.header("PRÓXIMOS PASSOS")
    
    Logger.info("INSTRUÇÕES PARA APLICAR RLS:")
    Logger.info("")
    Logger.info("1. 🌐 Acesse o Supabase Dashboard:")
    Logger.info("   https://supabase.com/dashboard/project/pkefwvvkydzzfstzwppv/sql")
    Logger.info("")
    Logger.info("2. 📄 Abra o arquivo 'supabase_rls_commands.sql'")
    Logger.info("   (criado neste diretório)")
    Logger.info("")
    Logger.info("3. 📋 Cole o conteúdo no editor SQL do Supabase")
    Logger.info("")
    Logger.info("4. ▶️ Execute os comandos (botão 'Run')")
    Logger.info("")
    Logger.info("5. ✅ Execute 'python verify_rls.py' para verificar")
    Logger.info("")
    
    if existing_tables:
        Logger.info(f"TABELAS ENCONTRADAS: {', '.join(existing_tables)}")
    else:
        Logger.warning("NENHUMA TABELA ENCONTRADA - As tabelas serão criadas pelos comandos SQL")
    
    Logger.info("APÓS APLICAR AS POLÍTICAS:")
    Logger.info("Execute 'python validate_system.py' para validação completa")


if __name__ == "__main__":
    main()