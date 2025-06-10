#!/usr/bin/env python3
import requests
import subprocess
import time
from datetime import datetime

def check_domain_status():
    domains = [
        "techreparo.com",
        "www.techreparo.com",
        "techze-diagnostico-frontend.onrender.com"
    ]
    
    print(f"\n==================================================")
    print(f"VERIFICAÇÃO DNS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"==================================================")
    
    for domain in domains:
        try:
            # Teste DNS
            result = subprocess.run(['nslookup', domain], 
                                  capture_output=True, text=True, timeout=10)
            dns_ok = "NXDOMAIN" not in result.stdout and "can't find" not in result.stdout
            
            # Teste HTTP
            try:
                response = requests.get(f"https://{domain}", timeout=10)
                http_ok = response.status_code < 400
                status_code = response.status_code
            except:
                http_ok = False
                status_code = "ERROR"
            
            print(f"📍 {domain:35} - DNS: {'✅' if dns_ok else '❌'} | HTTP: {'✅' if http_ok else '❌'} | Status: {status_code}")
            
        except Exception as e:
            print(f"❌ {domain:35} - ERRO: {e}")
    
    print(f"==================================================\n")

if __name__ == "__main__":
    print("🔄 Iniciando verificação contínua...")
    print("⏹️  Pressione Ctrl+C para parar")
    
    try:
        while True:
            check_domain_status()
            time.sleep(60)  # Verifica a cada 1 minuto
    except KeyboardInterrupt:
        print("\n🛑 Verificação interrompida pelo usuário")
