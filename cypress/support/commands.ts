/// <reference types="cypress" />

// Comandos customizados para TechZe Diagnóstico
// Este arquivo contém comandos reutilizáveis para os testes E2E

// Comando para fazer login
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.session([email, password], () => {
    cy.visit('/login')
    cy.get('[data-testid="email-input"]').type(email)
    cy.get('[data-testid="password-input"]').type(password)
    cy.get('[data-testid="login-button"]').click()
    cy.url().should('not.include', '/login')
  })
})

// Comando para navegar para dashboard
Cypress.Commands.add('goToDashboard', () => {
  cy.visit('/dashboard')
  cy.get('[data-testid="dashboard-title"]').should('be.visible')
})

// Comando para testar responsividade
Cypress.Commands.add('testResponsive', () => {
  // Desktop
  cy.viewport(1920, 1080)
  cy.get('[data-testid="main-content"]').should('be.visible')
  
  // Tablet
  cy.viewport(768, 1024)
  cy.get('[data-testid="main-content"]').should('be.visible')
  
  // Mobile
  cy.viewport(375, 667)
  cy.get('[data-testid="main-content"]').should('be.visible')
})

declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>
      goToDashboard(): Chainable<void>
      testResponsive(): Chainable<void>
    }
  }
} 