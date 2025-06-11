
📋 INSTRUÇÕES PARA CONFIGURAÇÃO DNS NO IONOS

🔧 PROBLEMA IDENTIFICADO:
- ❌ Domínio raiz 'techreparo.com' não está configurado
- ✅ Subdomínio 'www.techreparo.com' já está configurado

🛠️ CORREÇÕES NECESSÁRIAS NO PAINEL IONOS:

1. 📍 ADICIONAR REGISTRO PARA DOMÍNIO RAIZ:
   - Tipo: CNAME
   - Host/Nome: @ (ou deixe vazio para domínio raiz)
   - Valor/Destino: techze-diagnostico-frontend.onrender.com
   - TTL: 3600 (ou deixe padrão)

2. 📍 VERIFICAR REGISTRO WWW (deve estar assim):
   - Tipo: CNAME
   - Host/Nome: www
   - Valor/Destino: techze-diagnostico-frontend.onrender.com
   - TTL: 3600

3. 🔄 REMOVER CONFLITOS:
   - Se existir registro A para @ (domínio raiz), remova-o
   - Se existir registro A para 'www', remova-o
   - Mantenha apenas os CNAMEs conforme acima

📝 PASSO A PASSO DETALHADO:

1. Entre no painel IONOS → Domínios & SSL
2. Clique em 'techreparo.com'
3. Vá em 'Configurações DNS' ou 'DNS Management'
4. Clique em 'Adicionar Registro' ou 'Add Record'
5. Configure conforme especificado acima
6. Salve as alterações
7. Aguarde propagação (até 24 horas, geralmente 1-2 horas)

⚠️ IMPORTANTE:
- Não use registros A e CNAME para o mesmo host
- Use apenas CNAME conforme especificado
- Aguarde a propagação DNS antes de testar
