// TechZe Diagnóstico - AI Features E2E Tests

describe('AI Diagnostic Features', () => {
  beforeEach(() => {
    // Login antes de cada teste
    cy.loginAsTestUser();
    cy.waitForPageLoad();
  });

  it('should analyze device issues with AI', () => {
    // Criar um novo diagnóstico
    cy.visit('/diagnostics/new');
    cy.get('[data-testid="device-name-input"]').type('Test AI Analysis Device');
    cy.get('[data-testid="device-type-select"]').select('computer');
    cy.get('[data-testid="issue-performance"]').check();
    cy.get('[data-testid="issue-overheating"]').check();
    cy.get('[data-testid="issue-description"]').type('The computer is running very slow and gets hot quickly.');
    cy.get('[data-testid="create-diagnostic-button"]').click();
    
    // Aguardar redirecionamento para página de detalhes
    cy.url().should('include', '/diagnostics/');
    
    // Verificar se a análise de IA está presente
    cy.get('[data-testid="ai-analysis-section"]').should('be.visible');
    cy.get('[data-testid="ai-analysis-loading"]').should('not.exist', { timeout: 10000 });
    cy.get('[data-testid="ai-analysis-content"]').should('be.visible');
    
    // Verificar componentes específicos da análise
    cy.get('[data-testid="ai-confidence-score"]').should('be.visible');
    cy.get('[data-testid="ai-recommendations"]').should('be.visible');
    cy.get('[data-testid="ai-severity-level"]').should('be.visible');
  });

  it('should provide AI-powered recommendations', () => {
    // Visitar um diagnóstico existente
    cy.visit('/diagnostics');
    cy.get('[data-testid="diagnostic-item"]').first().click();
    
    // Verificar seção de recomendações
    cy.get('[data-testid="ai-recommendations"]').should('be.visible');
    cy.get('[data-testid="recommendation-item"]').should('have.length.at.least', 1);
    
    // Verificar detalhes das recomendações
    cy.get('[data-testid="recommendation-item"]').first().within(() => {
      cy.get('[data-testid="recommendation-title"]').should('be.visible');
      cy.get('[data-testid="recommendation-description"]').should('be.visible');
      cy.get('[data-testid="recommendation-priority"]').should('be.visible');
    });
  });

  it('should allow feedback on AI analysis', () => {
    // Visitar um diagnóstico existente
    cy.visit('/diagnostics');
    cy.get('[data-testid="diagnostic-item"]').first().click();
    
    // Verificar e usar controles de feedback
    cy.get('[data-testid="ai-feedback-controls"]').should('be.visible');
    cy.get('[data-testid="feedback-helpful"]').click();
    cy.get('[data-testid="feedback-confirmation"]').should('be.visible');
    
    // Adicionar comentário de feedback
    cy.get('[data-testid="feedback-comment"]').type('The analysis was accurate and helpful');
    cy.get('[data-testid="submit-feedback"]').click();
    cy.get('[data-testid="feedback-success"]').should('be.visible');
  });

  it('should compare multiple AI analysis methods', () => {
    // Visitar um diagnóstico existente
    cy.visit('/diagnostics');
    cy.get('[data-testid="diagnostic-item"]').first().click();
    
    // Solicitar análise comparativa
    cy.get('[data-testid="request-comparative-analysis"]').click();
    cy.get('[data-testid="analysis-loading"]').should('be.visible');
    cy.get('[data-testid="analysis-loading"]').should('not.exist', { timeout: 15000 });
    
    // Verificar resultados comparativos
    cy.get('[data-testid="comparative-analysis"]').should('be.visible');
    cy.get('[data-testid="analysis-method-1"]').should('be.visible');
    cy.get('[data-testid="analysis-method-2"]').should('be.visible');
    cy.get('[data-testid="analysis-comparison-chart"]').should('be.visible');
  });

  it('should handle AI analysis errors gracefully', () => {
    // Forçar erro na análise de IA (usando intercept para simular falha)
    cy.intercept('POST', '/api/v3/ai/analyze', {
      statusCode: 500,
      body: { error: 'AI service unavailable' }
    }).as('aiAnalyzeError');
    
    // Criar um novo diagnóstico
    cy.visit('/diagnostics/new');
    cy.get('[data-testid="device-name-input"]').type('Error Test Device');
    cy.get('[data-testid="device-type-select"]').select('computer');
    cy.get('[data-testid="issue-performance"]').check();
    cy.get('[data-testid="create-diagnostic-button"]').click();
    
    // Verificar tratamento de erro
    cy.wait('@aiAnalyzeError');
    cy.get('[data-testid="ai-error-message"]').should('be.visible');
    cy.get('[data-testid="retry-analysis"]').should('be.visible');
    
    // Testar retry
    cy.intercept('POST', '/api/v3/ai/analyze', { fixture: 'ai-analysis.json' }).as('aiAnalyzeRetry');
    cy.get('[data-testid="retry-analysis"]').click();
    cy.wait('@aiAnalyzeRetry');
    cy.get('[data-testid="ai-analysis-content"]').should('be.visible');
  });
});