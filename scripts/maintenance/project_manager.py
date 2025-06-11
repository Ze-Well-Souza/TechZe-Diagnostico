#!/usr/bin/env python3
"""
Gerenciador unificado do projeto TechZe
Centraliza todas as operações de setup, validação e manutenção
"""

import sys
import argparse
from typing import Dict, Any
from database_manager import DatabaseManager
from system_validator import SystemValidator
from cleanup_project import ProjectCleaner
from utils import Logger, confirm_action


class ProjectManager:
    """Gerenciador principal do projeto TechZe"""
    
    def __init__(self):
        self.logger = Logger()
        self.db_manager = DatabaseManager()
        self.validator = SystemValidator()
        self.cleaner = ProjectCleaner()
    
    def setup_database(self, force: bool = False) -> bool:
        """Setup completo do banco de dados"""
        self.logger.header("SETUP DO BANCO DE DADOS")
        
        if not force:
            if not confirm_action("Deseja configurar o banco de dados?", default=True):
                self.logger.info("Setup do banco cancelado")
                return False
        
        return self.db_manager.setup_complete_database()
    
    def validate_system(self, detailed: bool = False) -> Dict[str, Any]:
        """Validação completa do sistema"""
        self.logger.header("VALIDAÇÃO DO SISTEMA")
        
        results = self.validator.run_complete_validation()
        
        if detailed:
            self._print_detailed_results(results)
        
        return results
    
    def cleanup_project(self, force: bool = False) -> bool:
        """Limpeza do projeto"""
        if force or confirm_action("Deseja limpar arquivos temporários?"):
            return self.cleaner.run_full_cleanup()
        else:
            self.logger.info("Limpeza cancelada")
            return False
    
    def generate_manual_sql(self) -> bool:
        """Gera SQL para aplicação manual"""
        self.logger.header("GERAÇÃO DE SQL MANUAL")
        
        sql_content = self.db_manager.generate_manual_sql()
        
        from utils import FileManager
        if FileManager.write_file('manual_setup.sql', sql_content):
            self.logger.success("SQL manual gerado: manual_setup.sql")
            self.logger.info("Execute no Supabase Dashboard SQL Editor")
            return True
        else:
            self.logger.error("Falha ao gerar SQL manual")
            return False
    
    def quick_start(self) -> bool:
        """Início rápido - setup completo automatizado"""
        self.logger.header("INÍCIO RÁPIDO - TECHZE")
        
        self.logger.info("Este processo irá:")
        self.logger.info("1. Validar o ambiente")
        self.logger.info("2. Configurar o banco de dados")
        self.logger.info("3. Validar a configuração")
        self.logger.info("4. Gerar relatório final")
        self.logger.info("")
        
        if not confirm_action("Deseja continuar com o setup automático?", default=True):
            self.logger.info("Setup cancelado")
            return False
        
        # Passo 1: Validação inicial
        self.logger.step("VALIDAÇÃO INICIAL")
        initial_results = self.validator.validate_environment()
        
        if initial_results['overall_status'] == 'error':
            self.logger.error("Ambiente não está configurado corretamente")
            self._print_environment_issues(initial_results)
            return False
        
        # Passo 2: Setup do banco
        self.logger.step("CONFIGURAÇÃO DO BANCO")
        db_success = self.setup_database(force=True)
        
        if not db_success:
            self.logger.warning("Setup do banco teve problemas")
            self.logger.info("Gerando SQL manual como alternativa...")
            self.generate_manual_sql()
        
        # Passo 3: Validação final
        self.logger.step("VALIDAÇÃO FINAL")
        final_results = self.validate_system()
        
        # Passo 4: Relatório
        self._generate_quick_start_report(db_success, final_results)
        
        return final_results.get('overall_status') == 'success'
    
    def health_check(self) -> bool:
        """Verificação rápida de saúde do sistema"""
        self.logger.header("VERIFICAÇÃO DE SAÚDE")
        
        checks = [
            ("Conexão com banco", self.db_manager.test_connection),
            ("Estrutura de arquivos", self._check_file_structure),
            ("Configuração", self._check_configuration)
        ]
        
        all_passed = True
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                if result:
                    self.logger.success(f"{check_name}: OK")
                else:
                    self.logger.error(f"{check_name}: FALHA")
                    all_passed = False
            except Exception as e:
                self.logger.error(f"{check_name}: ERRO - {str(e)}")
                all_passed = False
        
        if all_passed:
            self.logger.success("Sistema funcionando corretamente!")
        else:
            self.logger.warning("Sistema tem problemas - execute validação completa")
        
        return all_passed
    
    def _print_detailed_results(self, results: Dict[str, Any]) -> None:
        """Imprime resultados detalhados"""
        for section_name, section_results in results.items():
            if section_name == 'overall_status':
                continue
            
            self.logger.step(f"DETALHES - {section_name.upper()}")
            
            for key, value in section_results.items():
                if key == 'overall_status':
                    continue
                
                if isinstance(value, bool):
                    status = "✅" if value else "❌"
                    self.logger.info(f"{key}: {status}")
                elif isinstance(value, dict):
                    self.logger.info(f"{key}:")
                    for sub_key, sub_value in value.items():
                        self.logger.info(f"  {sub_key}: {sub_value}")
                else:
                    self.logger.info(f"{key}: {value}")
    
    def _print_environment_issues(self, env_results: Dict[str, Any]) -> None:
        """Imprime problemas do ambiente"""
        self.logger.step("PROBLEMAS ENCONTRADOS")
        
        packages = env_results.get('required_packages', {})
        if packages.get('missing'):
            self.logger.error("Pacotes faltando:")
            for package in packages['missing']:
                self.logger.info(f"  - {package}")
            self.logger.info("Instale com: pip install " + " ".join(packages['missing']))
        
        files = env_results.get('file_structure', {})
        if files.get('missing'):
            self.logger.error("Arquivos/diretórios faltando:")
            for file_path in files['missing']:
                self.logger.info(f"  - {file_path}")
    
    def _generate_quick_start_report(self, db_success: bool, validation_results: Dict[str, Any]) -> None:
        """Gera relatório do quick start"""
        self.logger.header("RELATÓRIO DO SETUP")
        
        self.logger.info(f"Banco de dados: {'✅' if db_success else '❌'}")
        
        overall_status = validation_results.get('overall_status', 'unknown')
        self.logger.info(f"Validação geral: {'✅' if overall_status == 'success' else '⚠️' if overall_status == 'partial' else '❌'}")
        
        if overall_status == 'success':
            self.logger.success("🎉 SETUP CONCLUÍDO COM SUCESSO!")
            self.logger.info("Próximos passos:")
            self.logger.info("1. Inicie o backend: cd microservices && python main.py")
            self.logger.info("2. Inicie o frontend: cd frontend-v3 && npm start")
            self.logger.info("3. Acesse: http://localhost:8081")
        elif overall_status == 'partial':
            self.logger.warning("⚠️ SETUP PARCIALMENTE CONCLUÍDO")
            self.logger.info("Alguns componentes podem precisar de configuração manual")
            self.logger.info("Execute 'python project_manager.py validate --detailed' para mais informações")
        else:
            self.logger.error("❌ SETUP FALHOU")
            self.logger.info("Execute 'python project_manager.py validate --detailed' para diagnóstico")
    
    def _check_file_structure(self) -> bool:
        """Verifica estrutura básica de arquivos"""
        import os
        required_files = ['config.py', 'utils.py', 'database_manager.py']
        return all(os.path.exists(f) for f in required_files)
    
    def _check_configuration(self) -> bool:
        """Verifica configuração básica"""
        try:
            from config import config
            return bool(config.supabase.url and config.supabase.service_role_key)
        except:
            return False


def create_cli_parser() -> argparse.ArgumentParser:
    """Cria parser para linha de comando"""
    parser = argparse.ArgumentParser(
        description="Gerenciador do projeto TechZe",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python project_manager.py quick-start          # Setup completo automatizado
  python project_manager.py setup-db             # Apenas setup do banco
  python project_manager.py validate             # Validação completa
  python project_manager.py validate --detailed  # Validação com detalhes
  python project_manager.py cleanup              # Limpeza do projeto
  python project_manager.py health               # Verificação rápida
  python project_manager.py generate-sql         # Gerar SQL manual
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Quick start
    subparsers.add_parser('quick-start', help='Setup completo automatizado')
    
    # Setup database
    db_parser = subparsers.add_parser('setup-db', help='Configurar banco de dados')
    db_parser.add_argument('--force', action='store_true', help='Forçar setup sem confirmação')
    
    # Validate
    validate_parser = subparsers.add_parser('validate', help='Validar sistema')
    validate_parser.add_argument('--detailed', action='store_true', help='Mostrar detalhes')
    
    # Cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='Limpar projeto')
    cleanup_parser.add_argument('--force', action='store_true', help='Forçar limpeza sem confirmação')
    
    # Health check
    subparsers.add_parser('health', help='Verificação rápida de saúde')
    
    # Generate SQL
    subparsers.add_parser('generate-sql', help='Gerar SQL para aplicação manual')
    
    return parser


def main():
    """Função principal"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = ProjectManager()
    
    try:
        if args.command == 'quick-start':
            success = manager.quick_start()
            sys.exit(0 if success else 1)
        
        elif args.command == 'setup-db':
            success = manager.setup_database(force=args.force)
            sys.exit(0 if success else 1)
        
        elif args.command == 'validate':
            results = manager.validate_system(detailed=args.detailed)
            success = results.get('overall_status') == 'success'
            sys.exit(0 if success else 1)
        
        elif args.command == 'cleanup':
            success = manager.cleanup_project(force=args.force)
            sys.exit(0 if success else 1)
        
        elif args.command == 'health':
            success = manager.health_check()
            sys.exit(0 if success else 1)
        
        elif args.command == 'generate-sql':
            success = manager.generate_manual_sql()
            sys.exit(0 if success else 1)
        
        else:
            parser.print_help()
            sys.exit(1)
    
    except KeyboardInterrupt:
        Logger.info("\nOperação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        Logger.error(f"Erro inesperado: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()