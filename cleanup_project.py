#!/usr/bin/env python3
"""
Script de limpeza do projeto TechZe
Remove arquivos temporários, de debug e desnecessários
Refatorado para usar módulos centralizados
"""

from utils import Logger, FileManager, ProgressTracker, confirm_action


class ProjectCleaner:
    """Gerenciador de limpeza do projeto"""
    
    def __init__(self):
        self.logger = Logger()
        
        # Arquivos temporários para remover
        self.temp_files = [
            "quick_test.py",
            "test_integration.py", 
            "test_integration_quick.py",
            "test_connection_quick.py",
            "test_supabase_connection.py",
            "run_rls_setup.py",
            "setup_supabase_rls.py",
            "start_project.py",
            "correcao.md",
            "CORRECOES_APLICADAS.md",
            "RESUMO_CORRECOES_FINAIS.md",
            "TASK_DIAGNOSTICO.md",
            "supabase_setup_complete.sql",
            "cors_test.html",
        ]
        
        # Diretórios obsoletos
        self.temp_dirs = [
            "src",
            "public",
            ".pytest_cache",
        ]
        
        # Padrões de cache para limpar
        self.cache_patterns = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".coverage",
            "htmlcov",
            ".tox",
            ".cache",
            "node_modules",
            "dist",
            "build",
            ".DS_Store",
            "Thumbs.db"
        ]
    
    def clean_temp_files(self) -> int:
        """Remove arquivos temporários"""
        self.logger.step("REMOVENDO ARQUIVOS TEMPORÁRIOS")
        
        progress = ProgressTracker(len(self.temp_files), "File Removal")
        
        for file_path in self.temp_files:
            success = FileManager.safe_remove_file(file_path)
            progress.update(success, f"{'Removed' if success else 'Not found'}: {file_path}")
        
        progress.print_summary()
        return progress.summary()['successes']
    
    def clean_temp_directories(self) -> int:
        """Remove diretórios temporários"""
        self.logger.step("REMOVENDO DIRETÓRIOS OBSOLETOS")
        
        progress = ProgressTracker(len(self.temp_dirs), "Directory Removal")
        
        for dir_path in self.temp_dirs:
            success = FileManager.safe_remove_directory(dir_path)
            progress.update(success, f"{'Removed' if success else 'Not found'}: {dir_path}")
        
        progress.print_summary()
        return progress.summary()['successes']
    
    def organize_documentation(self) -> int:
        """Organiza documentação na pasta docs"""
        self.logger.step("ORGANIZANDO DOCUMENTAÇÃO")
        
        docs_to_move = [
            "COMECE_AQUI.md",
            "INSTRUCOES_RAPIDAS.md", 
            "STATUS_FINAL.md",
            "RESUMO_IMPLEMENTACAO.md"
        ]
        
        # Garantir que o diretório docs existe
        FileManager.ensure_directory("docs")
        
        moved_count = 0
        for doc in docs_to_move:
            try:
                import os
                import shutil
                
                if os.path.exists(doc):
                    dest = os.path.join("docs", doc)
                    if not os.path.exists(dest):
                        shutil.move(doc, dest)
                        self.logger.success(f"Moved: {doc} -> docs/")
                        moved_count += 1
                    else:
                        self.logger.warning(f"Already exists: docs/{doc}")
                else:
                    self.logger.warning(f"Not found: {doc}")
                    
            except Exception as e:
                self.logger.error(f"Error moving {doc}: {str(e)}")
        
        return moved_count
    
    def clean_cache_files(self) -> int:
        """Remove arquivos de cache"""
        self.logger.step("LIMPANDO ARQUIVOS DE CACHE")
        
        import os
        import glob
        
        removed_count = 0
        
        for pattern in self.cache_patterns:
            if pattern.startswith("*"):
                # Padrão de arquivo
                files = glob.glob(pattern, recursive=True)
                for file_path in files:
                    if FileManager.safe_remove_file(file_path):
                        removed_count += 1
            else:
                # Diretório
                for root, dirs, files in os.walk('.'):
                    if pattern in dirs:
                        dir_path = os.path.join(root, pattern)
                        if FileManager.safe_remove_directory(dir_path):
                            removed_count += 1
        
        self.logger.info(f"Removed {removed_count} cache files/directories")
        return removed_count
    
    def generate_cleanup_report(self, results: dict) -> None:
        """Gera relatório de limpeza"""
        self.logger.header("RELATÓRIO DE LIMPEZA")
        
        total_removed = sum(results.values())
        
        self.logger.info(f"Arquivos temporários removidos: {results.get('temp_files', 0)}")
        self.logger.info(f"Diretórios removidos: {results.get('temp_dirs', 0)}")
        self.logger.info(f"Documentos organizados: {results.get('docs_moved', 0)}")
        self.logger.info(f"Arquivos de cache removidos: {results.get('cache_files', 0)}")
        self.logger.info(f"Total de itens processados: {total_removed}")
        
        if total_removed > 0:
            self.logger.success("Limpeza concluída com sucesso!")
        else:
            self.logger.info("Nenhum arquivo foi removido (projeto já estava limpo)")
    
    def run_full_cleanup(self) -> bool:
        """Executa limpeza completa"""
        self.logger.header("LIMPEZA DO PROJETO TECHZE")
        
        self.logger.info("Este script irá remover:")
        self.logger.info("• Arquivos de teste temporários")
        self.logger.info("• Scripts de debug e correção")
        self.logger.info("• Documentação de desenvolvimento")
        self.logger.info("• Arquivos de configuração temporários")
        self.logger.info("• Cache e arquivos gerados")
        self.logger.info("")
        
        if not confirm_action("Deseja continuar com a limpeza?"):
            self.logger.info("Limpeza cancelada pelo usuário")
            return False
        
        # Executar limpeza
        results = {
            'temp_files': self.clean_temp_files(),
            'temp_dirs': self.clean_temp_directories(),
            'docs_moved': self.organize_documentation(),
            'cache_files': self.clean_cache_files()
        }
        
        # Gerar relatório
        self.generate_cleanup_report(results)
        
        return True


def main():
    """Função principal de limpeza"""
    cleaner = ProjectCleaner()
    cleaner.run_full_cleanup()


if __name__ == "__main__":
    main()
    
    for file_path in files_to_remove:
        if safe_remove(file_path):
            removed_files += 1
    
    print_step("REMOVENDO DIRETÓRIOS OBSOLETOS")
    
    removed_dirs = 0
    total_dirs = len(directories_to_remove)
    
    for dir_path in directories_to_remove:
        if safe_remove(dir_path):
            removed_dirs += 1
    
    print_step("LIMPANDO CACHE E ARQUIVOS TEMPORÁRIOS")
    
    # Limpar cache Python
    cache_patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".coverage",
        "htmlcov",
        ".tox",
        ".cache",
        ".pytest_cache",
        "*.egg-info",
        "dist",
        "build",
    ]
    
    cache_removed = 0
    
    # Buscar e remover cache recursivamente
    for root, dirs, files in os.walk("."):
        # Remover diretórios de cache
        for dir_name in dirs[:]:  # Cópia da lista para modificar durante iteração
            if dir_name in ["__pycache__", ".pytest_cache", "htmlcov", ".tox", ".cache", "dist", "build"]:
                cache_path = os.path.join(root, dir_name)
                if safe_remove(cache_path):
                    cache_removed += 1
                    dirs.remove(dir_name)  # Não entrar no diretório removido
        
        # Remover arquivos de cache
        for file_name in files:
            if (file_name.endswith(('.pyc', '.pyo', '.pyd')) or 
                file_name == '.coverage' or
                file_name.endswith('.egg-info')):
                cache_path = os.path.join(root, file_name)
                if safe_remove(cache_path):
                    cache_removed += 1
    
    print_step("ORGANIZANDO ARQUIVOS RESTANTES")
    
    # Criar diretório para documentação se não existir
    docs_dir = "docs"
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
        print(f"   ✅ Criado diretório: {docs_dir}")
    
    # Mover documentação para pasta docs
    docs_to_move = [
        "INSTRUCOES_RAPIDAS.md",
        "RESUMO_IMPLEMENTACAO.md", 
        "STATUS_FINAL.md",
        "COMECE_AQUI.md",
    ]
    
    moved_docs = 0
    for doc_file in docs_to_move:
        if os.path.exists(doc_file):
            try:
                shutil.move(doc_file, os.path.join(docs_dir, doc_file))
                print(f"   ✅ Movido para docs/: {doc_file}")
                moved_docs += 1
            except Exception as e:
                print(f"   ❌ Erro ao mover {doc_file}: {str(e)}")
    
    # Relatório final
    print_header("RELATÓRIO DE LIMPEZA")
    
    print(f"📊 ESTATÍSTICAS:")
    print(f"   Arquivos removidos: {removed_files}/{total_files}")
    print(f"   Diretórios removidos: {removed_dirs}/{total_dirs}")
    print(f"   Cache removido: {cache_removed} itens")
    print(f"   Documentos organizados: {moved_docs} arquivos")
    
    success_rate = ((removed_files + removed_dirs + moved_docs) / 
                   (total_files + total_dirs + len(docs_to_move))) * 100
    
    print(f"   Taxa de sucesso: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print(f"\n🎉 LIMPEZA CONCLUÍDA COM SUCESSO!")
        print("   O projeto está agora mais organizado e limpo!")
        
        print(f"\n📁 ESTRUTURA FINAL:")
        print("   ├── frontend-v3/          # Frontend React")
        print("   ├── microservices/        # Backend FastAPI")
        print("   ├── docs/                 # Documentação")
        print("   ├── run_setup.py          # Setup automático")
        print("   ├── validate_system.py    # Validação")
        print("   ├── fix_critical_issues.py # Correções")
        print("   ├── apply_rls_manual.py   # Supabase RLS")
        print("   ├── setup_complete.py     # Configuração")
        print("   ├── start_*.bat/.sh       # Scripts de inicialização")
        print("   └── supabase_rls_policies.sql # Políticas SQL")
        
        print(f"\n🚀 PRÓXIMOS PASSOS:")
        print("   1. Execute: python run_setup.py")
        print("   2. Inicie o sistema com start_all.bat/.sh")
        print("   3. Acesse http://localhost:8081")
        
        print(f"\n📚 DOCUMENTAÇÃO:")
        print("   • docs/COMECE_AQUI.md - Início rápido")
        print("   • docs/INSTRUCOES_RAPIDAS.md - Comandos essenciais")
        print("   • docs/STATUS_FINAL.md - Status da implementação")
        
    else:
        print(f"\n⚠️ LIMPEZA PARCIALMENTE CONCLUÍDA")
        print("   Alguns arquivos podem não ter sido removidos")
        print("   Verifique manualmente se necessário")
    
    print(f"\n💡 DICA:")
    print("   O projeto agora está limpo e organizado")
    print("   Mantenha apenas os arquivos essenciais para produção")

if __name__ == "__main__":
    main()