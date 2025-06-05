// ***********************************************************
// TechZe Diagnóstico - Cypress E2E Support Configuration
// Este arquivo é processado e carregado automaticamente antes
// dos arquivos de teste e é um ótimo lugar para comandos globais
// ***********************************************************

import './commands'

// Importar comandos personalizados do Testing Library
import '@testing-library/cypress/add-commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Configurações globais antes de cada teste
beforeEach(() => {
  // Interceptar requests de API para controle nos testes
  cy.intercept('GET', '/api/v3/health', { fixture: 'health-check.json' }).as('healthCheck')
  cy.intercept('GET', '/api/v3/diagnostics', { fixture: 'diagnostics.json' }).as('getDiagnostics')
  cy.intercept('POST', '/api/v3/diagnostics', { fixture: 'diagnostic-created.json' }).as('createDiagnostic')
  
  // Mock de autenticação
  cy.intercept('POST', '/auth/login', { fixture: 'auth-success.json' }).as('login')
  cy.intercept('GET', '/auth/user', { fixture: 'user-profile.json' }).as('getProfile')
  
  // Mock de IA/ML
  cy.intercept('POST', '/api/v3/ai/predict', { fixture: 'ai-prediction.json' }).as('aiPredict')
  cy.intercept('POST', '/api/v3/ai/analyze', { fixture: 'ai-analysis.json' }).as('aiAnalyze')
})

// Configurações de viewport para diferentes dispositivos
Cypress.Commands.add('setViewport', (device: string) => {
  const viewports = {
    mobile: [375, 667],
    tablet: [768, 1024], 
    desktop: [1920, 1080],
    ultrawide: [2560, 1440]
  }
  
  const [width, height] = viewports[device] || viewports.desktop
  cy.viewport(width, height)
})

// Comando para login automático nos testes
Cypress.Commands.add('loginAsTestUser', () => {
  cy.visit('/login')
  cy.get('[data-testid="email-input"]').type(Cypress.env('testUser').email)
  cy.get('[data-testid="password-input"]').type(Cypress.env('testUser').password)
  cy.get('[data-testid="login-button"]').click()
  cy.wait('@login')
  cy.url().should('not.include', '/login')
})

// Comando para aguardar carregamento completo da página
Cypress.Commands.add('waitForPageLoad', () => {
  cy.get('[data-testid="loading-spinner"]', { timeout: 10000 }).should('not.exist')
  cy.get('[data-testid="main-content"]').should('be.visible')
})

// Comando para criar diagnóstico de teste
Cypress.Commands.add('createTestDiagnostic', (diagnosticData = {}) => {
  const defaultData = {
    deviceName: 'Test Device',
    deviceType: 'computer',
    issues: ['performance', 'overheating'],
    priority: 'medium'
  }
  
  const data = { ...defaultData, ...diagnosticData }
  
  cy.get('[data-testid="new-diagnostic-button"]').click()
  cy.get('[data-testid="device-name-input"]').type(data.deviceName)
  cy.get('[data-testid="device-type-select"]').select(data.deviceType)
  
  data.issues.forEach(issue => {
    cy.get(`[data-testid="issue-${issue}"]`).check()
  })
  
  cy.get('[data-testid="priority-select"]').select(data.priority)
  cy.get('[data-testid="create-diagnostic-button"]').click()
  cy.wait('@createDiagnostic')
})

// Comando para verificar acessibilidade
Cypress.Commands.add('checkA11y', () => {
  cy.injectAxe()
  cy.checkA11y()
})

// Comando para testar PWA
Cypress.Commands.add('testPWAFeatures', () => {
  // Verificar Service Worker
  cy.window().should('have.property', 'navigator.serviceWorker')
  
  // Verificar Manifest
  cy.get('link[rel="manifest"]').should('exist')
  
  // Verificar ícones PWA
  cy.get('link[rel="apple-touch-icon"]').should('exist')
  cy.get('meta[name="theme-color"]').should('exist')
})

// Declarações de tipos para TypeScript
declare global {
  namespace Cypress {
    interface Chainable {
      setViewport(device: string): Chainable<void>
      loginAsTestUser(): Chainable<void>
      waitForPageLoad(): Chainable<void>
      createTestDiagnostic(data?: object): Chainable<void>
      checkA11y(): Chainable<void>
      testPWAFeatures(): Chainable<void>
    }
  }
} 