#!/usr/bin/env python3
"""
Script de limpeza final do projeto TechZe
Remove arquivos desnecessários e organiza a estrutura final
Refatorado para usar módulos centralizados
"""

from cleanup_project import ProjectCleaner
from utils import Logger, confirm_action


class FinalCleaner(ProjectCleaner):
    """Limpeza final especializada do projeto"""
    
    def __init__(self):
        super().__init__()
        
        # Arquivos específicos da limpeza final
        self.final_cleanup_files = [
            "apply_rls_policies.py",
            "apply_rls_manual.py", 
            "cleanup_project.py",
            "final_cleanup.py",
            "run_cleanup.py",
            "fix_critical_issues.py",
            "validate_system.py",
            "setup_complete.py",
            "run_rls_setup.py",
            "setup_supabase_rls.py",
            "test_integration.py",
            "test_integration_quick.py", 
            "test_connection_quick.py",
            "quick_test.py",
            "start_project.py",
            "supabase_setup_complete.sql"
        ]
        
        # Documentação para mover para docs
        self.docs_to_organize = [
            "CORRECAO_PROBLEMAS.md",
            "COMECE_AQUI.md"
        ]
    
    def final_project_cleanup(self) -> bool:
        """Executa limpeza final completa"""
        self.logger.header("LIMPEZA FINAL DO PROJETO TECHZE")
        
        self.logger.info("Esta limpeza final irá:")
        self.logger.info("• Remover scripts de setup e debug")
        self.logger.info("• Organizar documentação final")
        self.logger.info("• Manter apenas arquivos essenciais")
        self.logger.info("• Preparar projeto para produção")
        self.logger.info("")
        
        if not confirm_action("Deseja continuar com a limpeza final?"):
            self.logger.info("Limpeza final cancelada")
            return False
        
        # Executar limpeza padrão primeiro
        self.logger.step("LIMPEZA PADRÃO")
        super().run_full_cleanup()
        
        # Limpeza específica final
        self.logger.step("LIMPEZA FINAL ESPECÍFICA")
        removed_count = self._remove_final_files()
        
        # Organizar documentação final
        self.logger.step("ORGANIZAÇÃO FINAL DA DOCUMENTAÇÃO")
        docs_moved = self._organize_final_docs()
        
        # Criar estrutura final
        self.logger.step("CRIAÇÃO DA ESTRUTURA FINAL")
        self._create_final_structure()
        
        # Relatório final
        self._generate_final_report(removed_count, docs_moved)
        
        return True
    
    def _remove_final_files(self) -> int:
        """Remove arquivos específicos da limpeza final"""
        from utils import FileManager
        
        removed_count = 0
        
        for file_path in self.final_cleanup_files:
            if FileManager.safe_remove_file(file_path):
                self.logger.success(f"Removed: {file_path}")
                removed_count += 1
            else:
                self.logger.warning(f"Not found: {file_path}")
        
        return removed_count
    
    def _organize_final_docs(self) -> int:
        """Organiza documentação final"""
        from utils import FileManager
        import os
        import shutil
        
        # Garantir que docs existe
        FileManager.ensure_directory("docs")
        
        moved_count = 0
        
        for doc in self.docs_to_organize:
            try:
                if os.path.exists(doc):
                    dest = os.path.join("docs", doc)
                    if not os.path.exists(dest):
                        shutil.move(doc, dest)
                        self.logger.success(f"Moved: {doc} -> docs/")
                        moved_count += 1
                    else:
                        # Se já existe, remove o original
                        os.remove(doc)
                        self.logger.info(f"Removed duplicate: {doc}")
                        
            except Exception as e:
                self.logger.error(f"Error organizing {doc}: {str(e)}")
        
        return moved_count
    
    def _create_final_structure(self) -> None:
        """Cria estrutura final do projeto"""
        from utils import FileManager
        
        # Criar README final
        readme_content = self._generate_final_readme()
        FileManager.write_file("README.md", readme_content)
        self.logger.success("Created final README.md")
        
        # Criar arquivo de configuração de exemplo
        env_example = self._generate_env_example()
        FileManager.write_file(".env.example", env_example)
        self.logger.success("Created .env.example")
        
        # Criar script de inicialização
        start_script = self._generate_start_script()
        FileManager.write_file("start.py", start_script)
        self.logger.success("Created start.py")
    
    def _generate_final_readme(self) -> str:
        """Gera README final do projeto"""
        return """# 🚀 TechZe - Sistema de Diagnóstico

Sistema completo de diagnóstico com frontend React, backend FastAPI e integração Supabase.

## ⚡ Início Rápido

```bash
# 1. Configurar ambiente
cp .env.example .env
# Edite .env com suas credenciais do Supabase

# 2. Instalar dependências
pip install -r requirements.txt
cd frontend-v3 && npm install

# 3. Configurar banco de dados
python project_manager.py setup-db

# 4. Iniciar aplicação
python start.py
```

## 📁 Estrutura do Projeto

```
TechZe-Diagnostico/
├── 📂 frontend-v3/              # Frontend React + TypeScript
├── 📂 microservices/            # Backend FastAPI
├── 📂 docs/                     # Documentação
├── 🔧 config.py                 # Configurações
├── 🛠️ utils.py                  # Utilitários
├── 🗄️ database_manager.py       # Gerenciador de banco
├── ⚙️ project_manager.py        # Gerenciador do projeto
├── 🚀 start.py                  # Script de inicialização
└── 📄 supabase_rls_policies.sql # Políticas SQL
```

## 🎯 Funcionalidades

- ✅ Sistema completo de diagnóstico
- ✅ Interface React moderna
- ✅ API FastAPI robusta
- ✅ Banco Supabase com RLS
- ✅ Autenticação segura
- ✅ Relatórios em tempo real

## 🔧 Comandos Úteis

```bash
# Validar sistema
python project_manager.py validate

# Verificação rápida
python project_manager.py health

# Setup completo
python project_manager.py quick-start
```

## 📚 Documentação

Consulte a pasta `docs/` para documentação detalhada.

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.
"""
    
    def _generate_env_example(self) -> str:
        """Gera arquivo .env.example"""
        return """# Configurações do Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

# Configurações do projeto
PROJECT_NAME=TechZe
PROJECT_VERSION=1.0.0
FRONTEND_PORT=8081
BACKEND_PORT=8000

# Ambiente
NODE_ENV=development
"""
    
    def _generate_start_script(self) -> str:
        """Gera script de inicialização"""
        return """#!/usr/bin/env python3
\"\"\"
Script de inicialização do projeto TechZe
\"\"\"

from project_manager import ProjectManager
from utils import Logger

def main():
    \"\"\"Função principal\"\"\"
    Logger.header("INICIANDO TECHZE")
    
    manager = ProjectManager()
    
    # Verificação rápida
    if not manager.health_check():
        Logger.warning("Sistema com problemas - executando setup...")
        manager.quick_start()
    
    Logger.success("Sistema pronto!")
    Logger.info("Acesse: http://localhost:8081")

if __name__ == "__main__":
    main()
"""
    
    def _generate_final_report(self, removed_count: int, docs_moved: int) -> None:
        """Gera relatório final"""
        self.logger.header("RELATÓRIO DA LIMPEZA FINAL")
        
        self.logger.info(f"Arquivos de setup removidos: {removed_count}")
        self.logger.info(f"Documentos organizados: {docs_moved}")
        self.logger.info("Estrutura final criada: ✅")
        
        self.logger.success("🎉 PROJETO FINALIZADO!")
        self.logger.info("")
        self.logger.info("Estrutura final do projeto:")
        self.logger.info("├── frontend-v3/     # Frontend React")
        self.logger.info("├── microservices/   # Backend FastAPI")
        self.logger.info("├── docs/           # Documentação")
        self.logger.info("├── config.py       # Configurações")
        self.logger.info("├── utils.py        # Utilitários")
        self.logger.info("├── database_manager.py  # Banco")
        self.logger.info("├── project_manager.py   # Gerenciador")
        self.logger.info("├── start.py        # Inicialização")
        self.logger.info("└── README.md       # Documentação principal")
        self.logger.info("")
        self.logger.info("Para iniciar o projeto: python start.py")


def main():
    """Função principal"""
    cleaner = FinalCleaner()
    cleaner.final_project_cleanup()


if __name__ == "__main__":
    main()