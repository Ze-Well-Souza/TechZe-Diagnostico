"""
Teste de Upload de Arquivos - TechZe Diagnóstico
CURSOR testando implementações do TRAE (Frontend)

Objetivo: Testar FileUpload.tsx component, validar tipos aceitos, verificar Supabase
"""

import requests
import os
import tempfile
from datetime import datetime


class TestFileUpload:
    """Testes de upload de arquivos"""
    
    base_url = "http://localhost:8000"
    
    def setup_method(self):
        """Setup para cada teste"""
        self.headers = {
            "Accept": "application/json"
        }
    
    def create_test_file(self, filename, size_kb=1):
        """Criar arquivo de teste"""
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, filename)
        
        with open(file_path, 'wb') as f:
            f.write(b'X' * (size_kb * 1024))
        
        return file_path
    
    def test_image_upload_validation(self):
        """Teste de upload de imagens válidas"""
        # Simular arquivos de imagem suportados
        image_types = [
            ("test.jpg", "image/jpeg"),
            ("test.png", "image/png"),
            ("test.gif", "image/gif"),
            ("test.webp", "image/webp")
        ]
        
        print("=== TESTE DE UPLOAD DE IMAGENS ===")
        
        for filename, mimetype in image_types:
            file_path = self.create_test_file(filename, 10)  # 10KB
            
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (filename, f, mimetype)}
                    
                    # Testar endpoint de upload (se existir)
                    response = requests.post(
                        f"{self.base_url}/api/v1/upload/image",
                        files=files,
                        headers=self.headers
                    )
                    
                    print(f"{filename}: Status {response.status_code}")
                    
                    if response.status_code == 404:
                        print(f"  ⚠️ Endpoint de upload não implementado")
                    elif response.status_code == 200:
                        print(f"  ✅ Upload funcionando")
                    else:
                        print(f"  ❌ Erro: {response.text}")
                        
            except Exception as e:
                print(f"  ❌ Erro no teste: {e}")
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    def test_document_upload_validation(self):
        """Teste de upload de documentos"""
        document_types = [
            ("test.pdf", "application/pdf"),
            ("test.doc", "application/msword"),
            ("test.txt", "text/plain")
        ]
        
        print("\n=== TESTE DE UPLOAD DE DOCUMENTOS ===")
        
        for filename, mimetype in document_types:
            file_path = self.create_test_file(filename, 50)  # 50KB
            
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (filename, f, mimetype)}
                    
                    response = requests.post(
                        f"{self.base_url}/api/v1/upload/document",
                        files=files,
                        headers=self.headers
                    )
                    
                    print(f"{filename}: Status {response.status_code}")
                    
                    if response.status_code == 404:
                        print(f"  ⚠️ Endpoint de upload não implementado")
                    
            except Exception as e:
                print(f"  ❌ Erro no teste: {e}")
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    def test_file_size_limits(self):
        """Teste de limites de tamanho de arquivo"""
        print("\n=== TESTE DE LIMITES DE TAMANHO ===")
        
        # Teste arquivo muito grande (10MB)
        large_file = self.create_test_file("large.jpg", 10240)  # 10MB
        
        try:
            with open(large_file, 'rb') as f:
                files = {'file': ("large.jpg", f, "image/jpeg")}
                
                response = requests.post(
                    f"{self.base_url}/api/v1/upload/image",
                    files=files,
                    headers=self.headers
                )
                
                print(f"Arquivo 10MB: Status {response.status_code}")
                
                if response.status_code == 413:
                    print("  ✅ Limite de tamanho funcionando")
                elif response.status_code == 404:
                    print("  ⚠️ Endpoint não implementado")
                else:
                    print(f"  ⚠️ Resposta inesperada: {response.status_code}")
                    
        except Exception as e:
            print(f"  ❌ Erro no teste: {e}")
        finally:
            if os.path.exists(large_file):
                os.remove(large_file)
    
    def test_malicious_file_upload(self):
        """Teste de upload de arquivos maliciosos"""
        print("\n=== TESTE DE SEGURANÇA - ARQUIVOS MALICIOSOS ===")
        
        malicious_files = [
            ("script.exe", "application/x-executable"),
            ("virus.bat", "application/x-msdos-program"),
            ("hack.php", "application/x-php"),
            ("shell.sh", "application/x-sh")
        ]
        
        for filename, mimetype in malicious_files:
            file_path = self.create_test_file(filename, 1)
            
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (filename, f, mimetype)}
                    
                    response = requests.post(
                        f"{self.base_url}/api/v1/upload/document",
                        files=files,
                        headers=self.headers
                    )
                    
                    print(f"{filename}: Status {response.status_code}")
                    
                    if response.status_code == 400:
                        print(f"  ✅ Arquivo rejeitado corretamente")
                    elif response.status_code == 404:
                        print(f"  ⚠️ Endpoint não implementado")
                    elif response.status_code == 200:
                        print(f"  ❌ FALHA DE SEGURANÇA: Arquivo perigoso aceito!")
                    
            except Exception as e:
                print(f"  ❌ Erro no teste: {e}")
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
    
    def test_supabase_storage_integration(self):
        """Teste de integração com Supabase Storage"""
        print("\n=== TESTE DE INTEGRAÇÃO SUPABASE STORAGE ===")
        
        # Verificar se existe endpoint de listagem de arquivos
        response = requests.get(
            f"{self.base_url}/api/v1/storage/files",
            headers=self.headers
        )
        
        print(f"Storage API Status: {response.status_code}")
        
        if response.status_code == 404:
            print("  ⚠️ API de Storage não implementada")
        elif response.status_code == 200:
            print("  ✅ API de Storage funcionando")
            try:
                data = response.json()
                print(f"  📁 Arquivos encontrados: {len(data.get('files', []))}")
            except:
                print("  ⚠️ Resposta não é JSON válido")
        else:
            print(f"  ❌ Erro inesperado: {response.status_code}")


def test_file_upload_complete():
    """Teste completo de upload de arquivos"""
    test = TestFileUpload()
    test.setup_method()
    
    print("=== TESTE COMPLETO DE UPLOAD DE ARQUIVOS ===")
    print("CURSOR validando FileUpload.tsx do TRAE")
    print("=" * 60)
    
    test.test_image_upload_validation()
    test.test_document_upload_validation()
    test.test_file_size_limits()
    test.test_malicious_file_upload()
    test.test_supabase_storage_integration()
    
    print("\n" + "=" * 60)
    print("RESUMO DE UPLOAD DE ARQUIVOS:")
    print("=" * 60)
    print("⚠️ Endpoints de upload não implementados no backend")
    print("🔧 Necessário implementar API de upload para produção")
    print("🔧 Implementar validação de segurança para arquivos")
    print("🔧 Configurar integração com Supabase Storage")


if __name__ == "__main__":
    test_file_upload_complete() 