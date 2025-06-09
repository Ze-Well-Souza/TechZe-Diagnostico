# 🔑 Guia Completo - Configuração Google PageSpeed Insights API

## 📋 Passo a Passo Detalhado

### 1. Acessar Google Cloud Console
1. Acesse: https://console.cloud.google.com/
2. Faça login com sua conta Google
3. Se for seu primeiro acesso, aceite os termos de serviço

### 2. Criar ou Selecionar Projeto
1. No topo da página, clique no seletor de projeto
2. **Opção A - Novo Projeto:**
   - Clique em "Novo Projeto"
   - Nome: `TechZe-Validacao`
   - Clique em "Criar"
3. **Opção B - Usar Projeto Existente:**
   - Selecione um projeto já criado

### 3. Ativar a API PageSpeed Insights
1. No menu lateral, vá em "APIs e Serviços" > "Biblioteca"
2. Busque por "PageSpeed Insights API"
3. Clique na API encontrada
4. Clique em "ATIVAR"
5. Aguarde alguns segundos para ativação

### 4. Criar Credenciais (API Key)
1. Vá em "APIs e Serviços" > "Credenciais"
2. Clique em "+ CRIAR CREDENCIAIS"
3. Selecione "Chave de API"
4. **IMPORTANTE:** Anote a chave gerada imediatamente
5. Clique em "RESTRINGIR CHAVE" (recomendado)

### 5. Configurar Restrições da API Key
1. **Nome:** `TechZe-PageSpeed-Key`
2. **Restrições de aplicativo:** 
   - Selecione "Endereços IP"
   - Adicione seu IP atual (você pode usar: https://whatismyipaddress.com/)
   - Para desenvolvimento local, adicione: `127.0.0.1`
3. **Restrições de API:**
   - Selecione "Restringir chave"
   - Escolha "PageSpeed Insights API"
4. Clique em "SALVAR"

### 6. Testar a API Key
Execute este comando para testar:
```bash
curl "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=https://techreparo.com&key=SUA_API_KEY_AQUI"
```

### 7. Configurar no Sistema TechZe
1. Abra o arquivo `.env.validacao`
2. Substitua `SUA_GOOGLE_API_KEY_AQUI` pela sua chave real
3. Salve o arquivo

### 8. Verificar Configuração
Execute o sistema de validação:
```bash
python sistema_validacao_melhorado.py
```

## 🚨 Troubleshooting Comum

### Erro "API Key inválida"
- Verifique se copiou a chave completa
- Confirme se a API foi ativada no projeto correto
- Aguarde até 5 minutos para propagação

### Erro "Quota excedida"
- API gratuita: 25.000 consultas/dia
- Para mais, configure billing no Google Cloud

### Erro "Acesso negado"
- Verifique restrições de IP na API Key
- Confirme se seu IP atual está autorizado

## 💡 Dicas Importantes

### Segurança
- **NUNCA** compartilhe sua API Key publicamente
- Use restrições de IP sempre que possível
- Monitore uso no Google Cloud Console

### Limites Gratuitos
- **25.000 consultas/dia** gratuitamente
- Após esse limite, será cobrado
- Monitore uso em "APIs e Serviços" > "Quotas"

### Performance
- Cache resultados para evitar consultas repetidas
- Execute testes apenas quando necessário
- Use estratégia mobile OU desktop, não ambas sempre

## 🔄 URLs Úteis

- **Google Cloud Console:** https://console.cloud.google.com/
- **Documentação API:** https://developers.google.com/speed/docs/insights/v5/get-started
- **Quotas e Limites:** https://developers.google.com/speed/docs/insights/v5/get-started#quotas
- **Teste Manual:** https://developers.google.com/speed/pagespeed/insights/

## 📞 Suporte

Em caso de problemas:
1. Verifique o status da API: https://status.cloud.google.com/
2. Consulte logs no Google Cloud Console
3. Execute testes manuais primeiro
4. Revise as configurações de firewall/proxy

---

*Após configurar a API Key, seu sistema de validação TechZe estará 100% funcional!* 