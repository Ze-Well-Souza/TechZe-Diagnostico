# Testes do Frontend

Este diretório contém os testes para o frontend da aplicação TechZe-Diagnostico. Os testes são implementados usando Jest e React Testing Library.

## Estrutura de Testes

Os testes estão organizados da seguinte forma:

- **Testes de Componentes**: Testam componentes React individuais
- **Testes de Hooks**: Testam hooks personalizados
- **Testes de Integração**: Testam a interação entre múltiplos componentes

## Configuração

A configuração do Jest está definida no arquivo `jest.config.js` na raiz do projeto frontend. Configurações adicionais estão no arquivo `jest.setup.js`.

## Executando os Testes

Para executar os testes, você pode usar os seguintes comandos:

```bash
# Executar todos os testes
npm test

# Executar testes em modo de observação (watch mode)
npm run test:watch

# Executar testes com cobertura
npm run test:coverage
```

## Convenções de Nomenclatura

- Arquivos de teste devem ser nomeados com o sufixo `.test.tsx` ou `.test.ts`
- Arquivos de teste devem estar localizados próximos aos arquivos que estão testando

## Mocks

Para componentes que dependem de contextos, hooks ou serviços externos, usamos mocks para isolar o componente sendo testado. Exemplos de mocks incluem:

- `useAuth`: Mock do hook de autenticação
- `useDiagnostics`: Mock do hook de diagnósticos
- `diagnosticApiService`: Mock do serviço de API de diagnósticos

## Testes Implementados

### Componentes

- `DiagnosticCard.test.tsx`: Testa o componente de cartão de diagnóstico
- `DeviceCard.test.tsx`: Testa o componente de cartão de dispositivo
- `Header.test.tsx`: Testa o componente de cabeçalho

### Hooks

- `useAuth.test.tsx`: Testa o hook de autenticação
- `useDiagnostics.test.ts`: Testa o hook de diagnósticos
- `use-mobile.test.tsx`: Testa o hook de detecção de dispositivos móveis

## Integração Contínua

Os testes são executados automaticamente em cada push e pull request através do GitHub Actions. A configuração está definida no arquivo `.github/workflows/ci.yml`.

## Cobertura de Código

O relatório de cobertura de código é gerado quando você executa `npm run test:coverage`. O relatório é salvo no diretório `coverage/`.

## Boas Práticas

1. **Teste comportamentos, não implementações**: Foque em testar o que o componente faz, não como ele faz.
2. **Use seletores acessíveis**: Prefira seletores como `getByRole`, `getByLabelText` em vez de `getByTestId`.
3. **Mantenha os testes simples**: Cada teste deve verificar uma única funcionalidade.
4. **Evite testes frágeis**: Não teste estilos ou implementações específicas que podem mudar frequentemente.
5. **Simule eventos do usuário**: Use `fireEvent` ou `userEvent` para simular interações do usuário.