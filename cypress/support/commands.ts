
// Comandos customizados para testes E2E
/// <reference types="cypress" />

declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>
      logout(): Chainable<void>
      createDevice(deviceData: any): Chainable<void>
      runDiagnostic(deviceId: string): Chainable<void>
      switchCompany(companyCode: string): Chainable<void>
    }
  }
}

// Login command
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.session([email, password], () => {
    cy.visit('/auth')
    cy.get('[data-testid="email-input"]').type(email)
    cy.get('[data-testid="password-input"]').type(password)
    cy.get('[data-testid="login-button"]').click()
    cy.url().should('include', '/dashboard')
  })
})

// Logout command
Cypress.Commands.add('logout', () => {
  cy.get('[data-testid="user-menu"]').click()
  cy.get('[data-testid="logout-button"]').click()
  cy.url().should('include', '/')
})

// Create device command
Cypress.Commands.add('createDevice', (deviceData) => {
  cy.get('[data-testid="add-device-button"]').click()
  cy.get('[data-testid="device-name-input"]').type(deviceData.name)
  cy.get('[data-testid="device-type-select"]').select(deviceData.type)
  cy.get('[data-testid="save-device-button"]').click()
})

// Run diagnostic command
Cypress.Commands.add('runDiagnostic', (deviceId) => {
  cy.get(`[data-testid="device-${deviceId}"]`).click()
  cy.get('[data-testid="run-diagnostic-button"]').click()
  cy.get('[data-testid="diagnostic-status"]').should('contain', 'completed')
})

// Switch company command  
Cypress.Commands.add('switchCompany', (companyCode) => {
  cy.get('[data-testid="company-switcher"]').click()
  cy.get(`[data-testid="company-${companyCode}"]`).click()
  cy.get('[data-testid="current-company"]').should('contain', companyCode)
})
