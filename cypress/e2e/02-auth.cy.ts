// TechZe Diagnóstico - Authentication E2E Tests

describe('Authentication Tests', () => {
  beforeEach(() => {
    // Limpar cookies e localStorage antes de cada teste
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  it('should display login form', () => {
    cy.visit('/login');
    cy.get('[data-testid="email-input"]').should('be.visible');
    cy.get('[data-testid="password-input"]').should('be.visible');
    cy.get('[data-testid="login-button"]').should('be.visible');
  });

  it('should validate login form inputs', () => {
    cy.visit('/login');
    
    // Tentar login sem preencher campos
    cy.get('[data-testid="login-button"]').click();
    cy.get('[data-testid="email-error"]').should('be.visible');
    
    // Email inválido
    cy.get('[data-testid="email-input"]').type('invalid-email');
    cy.get('[data-testid="login-button"]').click();
    cy.get('[data-testid="email-error"]').should('be.visible');
    
    // Senha muito curta
    cy.get('[data-testid="email-input"]').clear().type('test@example.com');
    cy.get('[data-testid="password-input"]').type('123');
    cy.get('[data-testid="login-button"]').click();
    cy.get('[data-testid="password-error"]').should('be.visible');
  });

  it('should login successfully', () => {
    cy.visit('/login');
    cy.get('[data-testid="email-input"]').type(Cypress.env('testUser').email);
    cy.get('[data-testid="password-input"]').type(Cypress.env('testUser').password);
    cy.get('[data-testid="login-button"]').click();
    
    // Verificar redirecionamento para dashboard
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid="user-profile"]').should('be.visible');
  });

  it('should show error for invalid credentials', () => {
    cy.visit('/login');
    cy.get('[data-testid="email-input"]').type('wrong@example.com');
    cy.get('[data-testid="password-input"]').type('WrongPassword123!');
    cy.get('[data-testid="login-button"]').click();
    
    // Verificar mensagem de erro
    cy.get('[data-testid="auth-error"]').should('be.visible');
    cy.url().should('include', '/login');
  });

  it('should logout successfully', () => {
    // Login primeiro
    cy.loginAsTestUser();
    
    // Verificar que está logado
    cy.get('[data-testid="user-profile"]').should('be.visible');
    
    // Logout
    cy.get('[data-testid="user-menu"]').click();
    cy.get('[data-testid="logout-button"]').click();
    
    // Verificar redirecionamento para login
    cy.url().should('include', '/login');
  });
});

describe('Authorization Tests', () => {
  it('should redirect unauthenticated users to login', () => {
    // Tentar acessar página protegida sem autenticação
    cy.visit('/dashboard');
    cy.url().should('include', '/login');
    
    cy.visit('/diagnostics');
    cy.url().should('include', '/login');
    
    cy.visit('/settings');
    cy.url().should('include', '/login');
  });

  it('should allow access to authenticated users', () => {
    // Login
    cy.loginAsTestUser();
    
    // Verificar acesso a páginas protegidas
    cy.visit('/dashboard');
    cy.url().should('include', '/dashboard');
    
    cy.visit('/diagnostics');
    cy.url().should('include', '/diagnostics');
    
    cy.visit('/settings');
    cy.url().should('include', '/settings');
  });

  it('should respect role-based permissions', () => {
    // Login como usuário comum
    cy.loginAsTestUser();
    
    // Tentar acessar área administrativa (deve ser redirecionado)
    cy.visit('/admin');
    cy.url().should('not.include', '/admin');
    cy.get('[data-testid="permission-error"]').should('be.visible');
    
    // Verificar que elementos administrativos não estão visíveis
    cy.visit('/dashboard');
    cy.get('[data-testid="admin-panel-link"]').should('not.exist');
  });
});