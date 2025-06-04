#!/usr/bin/env python3
"""
Script para aplicar políticas RLS no Supabase automaticamente
Refatorado para usar módulos centralizados
"""

from database_manager import DatabaseManager
from utils import Logger, confirm_action


def main():
    """Função principal"""
    Logger.header("APLICAÇÃO AUTOMÁTICA DE POLÍTICAS RLS")
    
    # Confirmar ação
    if not confirm_action("Deseja aplicar as políticas RLS automaticamente?", default=True):
        Logger.info("Operação cancelada pelo usuário")
        return
    
    # Inicializar gerenciador de banco
    db_manager = DatabaseManager()
    
    # Executar setup completo
    success = db_manager.setup_complete_database()
    
    if success:
        Logger.success("Políticas RLS aplicadas com sucesso!")
        Logger.info("Execute 'python verify_rls.py' para verificar o resultado")
    else:
        Logger.warning("Aplicação das políticas concluída com problemas")
        Logger.info("Verifique os logs acima para detalhes")
        Logger.info("Considere usar 'python apply_rls_manual.py' para aplicação manual")


if __name__ == "__main__":
    main()