#!/usr/bin/env python3
"""
Verificação Final - Monitoramento da Correção DNS
TechZe Diagnóstico - Status Final
"""

import requests
import subprocess
import time
from datetime import datetime

def log(message, level="INFO"):
    """Log com timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")

def check_dns_resolution(domain):
    """Verifica resolução DNS"""
    try:
        result = subprocess.run(['nslookup', domain], 
                              capture_output=True, text=True, timeout=10)
        if "NXDOMAIN" not in result.stdout and "can't find" not in result.stdout:
            # Extrair o resultado
            lines = result.stdout.split('\n')
            for line in lines:
                if 'techze' in line.lower() and 'onrender.com' in line.lower():
                    if 'techze-frontend-app' in line:
                        return "✅ CORRETO", line.strip()
                    elif 'techze-diagnostico-frontend' in line:
                        return "❌ ERRADO", line.strip()
            return "✅ CONFIGURADO", "DNS resolvido"
        else:
            return "❌ NÃO CONFIGURADO", "NXDOMAIN"
    except Exception as e:
        return "❌ ERRO", str(e)

def test_http_access(url):
    """Testa acesso HTTP"""
    try:
        response = requests.get(url, timeout=10, allow_redirects=True)
        if response.status_code < 400:
            return "✅ ACESSÍVEL", response.status_code, response.url
        else:
            return "❌ ERRO HTTP", response.status_code, response.url
    except requests.exceptions.RequestException as e:
        return "❌ INACESSÍVEL", "ERROR", str(e)

def check_complete_status():
    """Verifica status completo"""
    domains_to_check = [
        "techreparo.com",
        "www.techreparo.com"
    ]
    
    urls_to_test = [
        "https://techreparo.com",
        "https://www.techreparo.com",
        "https://techze-frontend-app.onrender.com"
    ]
    
    print(f"\n{'='*70}")
    print(f"🔍 VERIFICAÇÃO COMPLETA - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*70}")
    
    # 1. Verificação DNS
    print("\n🌐 RESOLUÇÃO DNS:")
    dns_correto = True
    for domain in domains_to_check:
        status, details = check_dns_resolution(domain)
        print(f"   📍 {domain:25} → {status}")
        if details != "DNS resolvido":
            print(f"      {details}")
        if "❌" in status:
            dns_correto = False
    
    # 2. Verificação HTTP
    print("\n🔗 ACESSO HTTP:")
    http_funcionando = True
    for url in urls_to_test:
        status, code, final_url = test_http_access(url)
        print(f"   📍 {url:40} → {status} ({code})")
        if final_url != url and isinstance(final_url, str):
            print(f"      Redirecionado para: {final_url}")
        if "❌" in status:
            http_funcionando = False
    
    # 3. Status geral
    print(f"\n{'='*70}")
    print("📊 STATUS GERAL:")
    
    if dns_correto and http_funcionando:
        print("   🎉 TUDO FUNCIONANDO PERFEITAMENTE!")
        status_geral = "SUCESSO"
    elif dns_correto and not http_funcionando:
        print("   🔄 DNS correto, aguardando propagação...")
        status_geral = "AGUARDANDO_PROPAGACAO"  
    elif not dns_correto:
        print("   ⚠️  DNS ainda não corrigido no IONOS")
        status_geral = "DNS_PENDENTE"
    else:
        print("   ❌ Problemas identificados")
        status_geral = "ERRO"
    
    print(f"{'='*70}\n")
    
    return status_geral

def monitor_continuous():
    """Monitoramento contínuo"""
    print("🚀 INICIANDO MONITORAMENTO CONTÍNUO")
    print("⏹️  Pressione Ctrl+C para parar")
    print("🔄 Verificação a cada 1 minuto")
    
    try:
        while True:
            status = check_complete_status()
            
            if status == "SUCESSO":
                print("🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
                print("✅ Todos os domínios estão funcionando!")
                break
            elif status == "DNS_PENDENTE":
                print("⚠️  Aguardando correção DNS no IONOS...")
            elif status == "AGUARDANDO_PROPAGACAO":
                print("🔄 Aguardando propagação DNS...")
            
            print("⏳ Próxima verificação em 60 segundos...\n")
            time.sleep(60)
            
    except KeyboardInterrupt:
        print("\n🛑 Monitoramento interrompido pelo usuário")

def verify_once():
    """Verificação única"""
    status = check_complete_status()
    
    if status == "SUCESSO":
        print("🎉 PARABÉNS! Configuração finalizada com sucesso!")
    elif status == "DNS_PENDENTE":
        print("📝 PRÓXIMO PASSO: Corrija o DNS no IONOS conforme CONFIGURACAO_FINAL_CORRETA.md")
    elif status == "AGUARDANDO_PROPAGACAO":
        print("⏳ AGUARDE: DNS corrigido, aguardando propagação (15-30 min)")
    
    return status

def main():
    """Função principal"""
    print("🔍 VERIFICAÇÃO FINAL DA CONFIGURAÇÃO")
    print("="*50)
    
    # Verificação única primeiro
    status = verify_once()
    
    if status != "SUCESSO":
        resposta = input("\n🔄 Deseja monitorar continuamente? (s/n): ").lower()
        if resposta in ['s', 'sim', 'y', 'yes']:
            monitor_continuous()
    
    print("\n✅ Verificação finalizada!")

if __name__ == "__main__":
    main()