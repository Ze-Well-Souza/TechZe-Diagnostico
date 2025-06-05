
describe('Multi-Tenant Functionality', () => {
  beforeEach(() => {
    cy.login('admin@ulytech.com', 'password123')
  })

  it('should isolate data between companies', () => {
    // Test company 1
    cy.switchCompany('ulytech')
    cy.createDevice({ name: 'Laptop Ulytech', type: 'laptop' })
    cy.get('[data-testid="devices-list"]').should('contain', 'Laptop Ulytech')

    // Switch to company 2
    cy.switchCompany('utilimix')
    cy.get('[data-testid="devices-list"]').should('not.contain', 'Laptop Ulytech')
    cy.createDevice({ name: 'Desktop Utilimix', type: 'desktop' })
    cy.get('[data-testid="devices-list"]').should('contain', 'Desktop Utilimix')

    // Switch back to company 1
    cy.switchCompany('ulytech')
    cy.get('[data-testid="devices-list"]').should('contain', 'Laptop Ulytech')
    cy.get('[data-testid="devices-list"]').should('not.contain', 'Desktop Utilimix')
  })

  it('should handle role-based permissions', () => {
    cy.switchCompany('ulytech')
    
    // Admin should see management options
    cy.get('[data-testid="admin-menu"]').should('be.visible')
    cy.get('[data-testid="user-management"]').should('be.visible')

    // Switch to technician account
    cy.logout()
    cy.login('tecnico@ulytech.com', 'password123')
    
    // Technician should not see admin options
    cy.get('[data-testid="admin-menu"]').should('not.exist')
    cy.get('[data-testid="user-management"]').should('not.exist')
  })
})
