#!/usr/bin/env python3
import asyncio
import os
from sistema_validacao_melhorado import TechZeValidadorMelhorado, ValidacaoConfig

async def executar_validacao_rapida():
    # Carregar configuração do .env
    config = ValidacaoConfig(
        render_api_key=os.getenv('RENDER_API_KEY', 'rnd_Tj1JybEJij6A3UhouM7spm8LRbkX'),
        google_api_key=os.getenv('GOOGLE_API_KEY', 'SUA_GOOGLE_API_KEY_AQUI'),
        base_url=os.getenv('BASE_URL', 'https://techreparo.com'),
        api_backend=os.getenv('API_BACKEND', 'https://techze-diagnostico-api.onrender.com'),
        api_frontend=os.getenv('API_FRONTEND', 'https://techze-diagnostico-frontend.onrender.com')
    )
    
    validador = TechZeValidadorMelhorado(config)
    return await validador.executar_validacao_completa()

if __name__ == "__main__":
    asyncio.run(executar_validacao_rapida())
