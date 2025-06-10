#!/usr/bin/env python3
"""
Monitoramento Final - DNS Registro A
TechZe Diagnóstico - Acompanhamento da Correção
"""

import requests
import subprocess
import time
from datetime import datetime

def log(message, level="INFO"):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def check_dns_a_record(domain):
    """Verifica registro A"""
    try:
        result = subprocess.run(['nslookup', domain], 
                              capture_output=True, text=True, timeout=10)
        
        # Procurar por IPs do Render
        render_ips = ["216.24.57.4", "216.24.57.252"]
        
        for ip in render_ips:
            if ip in result.stdout:
                return f"✅ CORRETO ({ip})", result.stdout
        
        if "NXDOMAIN" not in result.stdout and "can't find" not in result.stdout:
            return "❌ IP DIFERENTE", result.stdout
        else:
            return "❌ NÃO CONFIGURADO", result.stdout
            
    except Exception as e:
        return "❌ ERRO", str(e)

def test_website_access():
    """Testa acesso aos websites"""
    urls = [
        "https://techreparo.com",
        "https://www.techreparo.com",
        "https://techze-frontend-app.onrender.com"
    ]
    
    results = {}
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            if response.status_code < 400:
                results[url] = {"status": "✅ FUNCIONANDO", "code": response.status_code}
            else:
                results[url] = {"status": "❌ ERRO", "code": response.status_code}
        except Exception as e:
            results[url] = {"status": "❌ INACESSÍVEL", "code": str(e)}
    
    return results

def monitor_dns_change():
    """Monitora a mudança DNS"""
    print("🔍 MONITORAMENTO DNS - REGISTRO A")
    print("="*50)
    print("🎯 Aguardando configuração do registro A para techreparo.com")
    print("📋 IP esperado: 216.24.57.4 ou 216.24.57.252")
    print("⏹️  Pressione Ctrl+C para parar")
    print()
    
    try:
        while True:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"🔍 VERIFICAÇÃO - {timestamp}")
            print("-" * 50)
            
            # Verificar DNS
            status_root, details_root = check_dns_a_record("techreparo.com")
            status_www, details_www = check_dns_a_record("www.techreparo.com")
            
            print(f"📍 techreparo.com     → {status_root}")
            print(f"📍 www.techreparo.com → {status_www}")
            
            # Se ambos estão corretos, testar acesso
            if "✅" in status_root and "✅" in status_www:
                print("\n🔗 TESTANDO ACESSO WEB:")
                web_results = test_website_access()
                
                all_working = True
                for url, result in web_results.items():
                    print(f"   📍 {url:40} → {result['status']} ({result['code']})")
                    if "❌" in result['status']:
                        all_working = False
                
                if all_working:
                    print("\n🎉 SUCESSO! TODOS OS DOMÍNIOS FUNCIONANDO!")
                    print("✅ Configuração DNS finalizada com sucesso!")
                    break
                else:
                    print("\n⏳ DNS correto, aguardando propagação...")
            
            elif "✅" in status_root:
                print("✅ Domínio raiz configurado, aguardando www...")
            elif "✅" in status_www:
                print("✅ Subdomínio www configurado, aguardando domínio raiz...")
            else:
                print("⏳ Aguardando configuração DNS...")
            
            print("\n⏰ Próxima verificação em 30 segundos...")
            print("=" * 50)
            print()
            
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoramento interrompido pelo usuário")

def check_current_status():
    """Verifica status atual"""
    print("📊 STATUS ATUAL:")
    print("-" * 30)
    
    status_root, _ = check_dns_a_record("techreparo.com")
    status_www, _ = check_dns_a_record("www.techreparo.com")
    
    print(f"📍 techreparo.com     → {status_root}")
    print(f"📍 www.techreparo.com → {status_www}")
    
    if "✅" in status_root and "✅" in status_www:
        print("\n🔗 TESTANDO ACESSO:")
        web_results = test_website_access()
        for url, result in web_results.items():
            print(f"   📍 {url:35} → {result['status']}")
        return "COMPLETO"
    elif "✅" in status_root or "✅" in status_www:
        return "PARCIAL"
    else:
        return "PENDENTE"

def main():
    """Função principal"""
    print("🚀 MONITORAMENTO DNS - REGISTRO A")
    print("=" * 50)
    
    status = check_current_status()
    
    if status == "COMPLETO":
        print("\n🎉 Configuração já finalizada!")
    elif status == "PENDENTE":
        print("\n📝 Configure o registro A conforme instruções e execute novamente")
    else:
        resposta = input("\n🔄 Deseja monitorar continuamente? (s/n): ").lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            monitor_dns_change()

if __name__ == "__main__":
    main()