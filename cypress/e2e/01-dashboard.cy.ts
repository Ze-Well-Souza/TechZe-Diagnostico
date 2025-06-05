// TechZe Diagnóstico - Dashboard E2E Tests
describe('Dashboard Tests', () => {
  beforeEach(() => {
    // Visitar a página principal
    cy.visit('/')
  })

  it('should load the dashboard successfully', () => {
    cy.get('[data-testid="dashboard-title"]').should('contain', 'Dashboard')
    cy.get('[data-testid="stats-cards"]').should('be.visible')
    cy.get('[data-testid="recent-diagnostics"]').should('be.visible')
  })

  it('should display correct metrics', () => {
    cy.get('[data-testid="total-devices"]').should('be.visible')
    cy.get('[data-testid="active-diagnostics"]').should('be.visible')
    cy.get('[data-testid="success-rate"]').should('be.visible')
  })

  it('should navigate to diagnostics page', () => {
    cy.get('[data-testid="view-all-diagnostics"]').click()
    cy.url().should('include', '/diagnostics')
  })

  it('should be responsive on mobile', () => {
    cy.viewport('iphone-x')
    cy.get('[data-testid="mobile-menu-button"]').should('be.visible')
    cy.get('[data-testid="dashboard-content"]').should('be.visible')
  })
})

describe('Diagnostics Management', () => {
  it('should create a new diagnostic', () => {
    cy.visit('/diagnostics')
    cy.get('[data-testid="new-diagnostic-btn"]').click()
    
    cy.get('[data-testid="device-name"]').type('Test Device')
    cy.get('[data-testid="device-type"]').select('Computer')
    cy.get('[data-testid="issues"]').check(['performance'])
    
    cy.get('[data-testid="submit-diagnostic"]').click()
    cy.get('[data-testid="success-message"]').should('be.visible')
  })

  it('should view diagnostic details', () => {
    cy.visit('/diagnostics')
    cy.get('[data-testid="diagnostic-item"]').first().click()
    
    cy.url().should('include', '/diagnostics/')
    cy.get('[data-testid="diagnostic-details"]').should('be.visible')
    cy.get('[data-testid="ai-analysis"]').should('be.visible')
  })
})

describe('PWA Features', () => {
  it('should work offline', () => {
    cy.visit('/')
    // Simular modo offline
    cy.window().then((win) => {
      cy.wrap(win.navigator).invoke('setOnLine', false)
    })
    
    cy.get('[data-testid="offline-indicator"]').should('be.visible')
    cy.get('[data-testid="cached-content"]').should('be.visible')
  })

  it('should show install prompt', () => {
    cy.visit('/')
    
    // Simular evento beforeinstallprompt
    cy.window().then((win) => {
      const event = new Event('beforeinstallprompt')
      win.dispatchEvent(event)
    })
    
    cy.get('[data-testid="install-app-btn"]').should('be.visible')
  })
}) 