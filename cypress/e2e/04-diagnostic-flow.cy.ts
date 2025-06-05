// TechZe Diagnóstico - Complete Diagnostic Flow E2E Tests

describe('Complete Diagnostic Flow', () => {
  beforeEach(() => {
    // Login antes de cada teste
    cy.loginAsTestUser();
    cy.waitForPageLoad();
  });

  it('should complete full diagnostic lifecycle', () => {
    // 1. Criar novo diagnóstico
    cy.visit('/diagnostics/new');
    cy.get('[data-testid="device-name-input"]').type('Lifecycle Test Device');
    cy.get('[data-testid="device-type-select"]').select('computer');
    cy.get('[data-testid="issue-performance"]').check();
    cy.get('[data-testid="issue-noise"]').check();
    cy.get('[data-testid="issue-description"]').type('Computer is slow and making strange noises when running intensive tasks.');
    cy.get('[data-testid="priority-select"]').select('high');
    cy.get('[data-testid="create-diagnostic-button"]').click();
    
    // 2. Verificar criação e redirecionamento
    cy.url().should('include', '/diagnostics/');
    cy.get('[data-testid="diagnostic-details"]').should('be.visible');
    
    // 3. Capturar ID do diagnóstico da URL
    cy.url().then((url) => {
      const diagnosticId = url.split('/').pop();
      
      // 4. Verificar análise de IA
      cy.get('[data-testid="ai-analysis-section"]').should('be.visible');
      cy.get('[data-testid="ai-analysis-loading"]').should('not.exist', { timeout: 10000 });
      cy.get('[data-testid="ai-recommendations"]').should('be.visible');
      
      // 5. Adicionar comentário técnico
      cy.get('[data-testid="add-technical-note"]').click();
      cy.get('[data-testid="technical-note-input"]').type('Verificado que o sistema de refrigeração está com acúmulo de poeira. CPU throttling detectado.');
      cy.get('[data-testid="save-note"]').click();
      cy.get('[data-testid="note-saved-confirmation"]').should('be.visible');
      
      // 6. Atualizar status do diagnóstico
      cy.get('[data-testid="update-status"]').click();
      cy.get('[data-testid="status-select"]').select('in_progress');
      cy.get('[data-testid="save-status"]').click();
      cy.get('[data-testid="status-badge"]').should('contain', 'Em Progresso');
      
      // 7. Adicionar solução
      cy.get('[data-testid="add-solution"]').click();
      cy.get('[data-testid="solution-title"]').type('Limpeza e otimização do sistema');
      cy.get('[data-testid="solution-description"]').type('1. Limpeza completa do sistema de refrigeração\n2. Substituição da pasta térmica\n3. Otimização do sistema operacional\n4. Atualização de drivers');
      cy.get('[data-testid="solution-cost"]').type('150');
      cy.get('[data-testid="save-solution"]').click();
      cy.get('[data-testid="solution-saved-confirmation"]').should('be.visible');
      
      // 8. Finalizar diagnóstico
      cy.get('[data-testid="update-status"]').click();
      cy.get('[data-testid="status-select"]').select('resolved');
      cy.get('[data-testid="resolution-notes"]').type('Problema resolvido com limpeza e otimização. Performance melhorou significativamente.');
      cy.get('[data-testid="save-status"]').click();
      cy.get('[data-testid="status-badge"]').should('contain', 'Resolvido');
      
      // 9. Verificar histórico de alterações
      cy.get('[data-testid="view-history"]').click();
      cy.get('[data-testid="history-timeline"]').should('be.visible');
      cy.get('[data-testid="history-item"]').should('have.length.at.least', 3);
      
      // 10. Voltar para lista de diagnósticos
      cy.get('[data-testid="back-to-list"]').click();
      cy.url().should('include', '/diagnostics');
      
      // 11. Verificar que o diagnóstico aparece na lista com status correto
      cy.get(`[data-testid="diagnostic-item-${diagnosticId}"]`).should('be.visible');
      cy.get(`[data-testid="diagnostic-item-${diagnosticId}"] [data-testid="status-badge"]`).should('contain', 'Resolvido');
    });
  });

  it('should handle diagnostic with multiple devices', () => {
    // 1. Criar diagnóstico com múltiplos dispositivos
    cy.visit('/diagnostics/new');
    cy.get('[data-testid="multi-device-toggle"]').click();
    
    // 2. Adicionar primeiro dispositivo
    cy.get('[data-testid="add-device"]').click();
    cy.get('[data-testid="device-0-name"]').type('Router Principal');
    cy.get('[data-testid="device-0-type"]').select('network');
    cy.get('[data-testid="device-0-issues"]').check(['connectivity']);
    
    // 3. Adicionar segundo dispositivo
    cy.get('[data-testid="add-device"]').click();
    cy.get('[data-testid="device-1-name"]').type('Computador Sala');
    cy.get('[data-testid="device-1-type"]').select('computer');
    cy.get('[data-testid="device-1-issues"]').check(['connectivity', 'performance']);
    
    // 4. Descrição geral do problema
    cy.get('[data-testid="general-description"]').type('Problemas de conectividade em toda a rede. Computador com lentidão ao acessar internet.');
    cy.get('[data-testid="create-diagnostic-button"]').click();
    
    // 5. Verificar criação e detalhes
    cy.url().should('include', '/diagnostics/');
    cy.get('[data-testid="multi-device-diagnostic"]').should('be.visible');
    cy.get('[data-testid="device-count"]').should('contain', '2');
    
    // 6. Verificar detalhes de cada dispositivo
    cy.get('[data-testid="device-tab-0"]').click();
    cy.get('[data-testid="device-details"]').should('contain', 'Router Principal');
    
    cy.get('[data-testid="device-tab-1"]').click();
    cy.get('[data-testid="device-details"]').should('contain', 'Computador Sala');
    
    // 7. Verificar análise integrada
    cy.get('[data-testid="integrated-analysis"]').should('be.visible');
  });

  it('should export diagnostic report', () => {
    // 1. Visitar um diagnóstico existente
    cy.visit('/diagnostics');
    cy.get('[data-testid="diagnostic-item"]').first().click();
    
    // 2. Exportar relatório
    cy.get('[data-testid="export-report"]').click();
    cy.get('[data-testid="export-format"]').select('pdf');
    cy.get('[data-testid="include-technical-details"]').check();
    cy.get('[data-testid="include-ai-analysis"]').check();
    cy.get('[data-testid="confirm-export"]').click();
    
    // 3. Verificar confirmação de exportação
    cy.get('[data-testid="export-confirmation"]').should('be.visible');
  });

  it('should search and filter diagnostics', () => {
    // 1. Ir para lista de diagnósticos
    cy.visit('/diagnostics');
    
    // 2. Usar filtros
    cy.get('[data-testid="filter-button"]').click();
    cy.get('[data-testid="status-filter"]').select('in_progress');
    cy.get('[data-testid="device-type-filter"]').select('computer');
    cy.get('[data-testid="apply-filters"]').click();
    
    // 3. Verificar resultados filtrados
    cy.get('[data-testid="filtered-results-count"]').should('be.visible');
    cy.get('[data-testid="diagnostic-item"]').each(($item) => {
      cy.wrap($item).find('[data-testid="status-badge"]').should('contain', 'Em Progresso');
      cy.wrap($item).find('[data-testid="device-type"]').should('contain', 'Computador');
    });
    
    // 4. Usar busca
    cy.get('[data-testid="search-input"]').type('performance');
    cy.get('[data-testid="search-button"]').click();
    
    // 5. Verificar resultados da busca
    cy.get('[data-testid="search-results-count"]').should('be.visible');
    cy.get('[data-testid="diagnostic-item"]').should('have.length.at.least', 1);
  });

  it('should handle diagnostic cancellation', () => {
    // 1. Criar novo diagnóstico
    cy.visit('/diagnostics/new');
    cy.get('[data-testid="device-name-input"]').type('Cancellation Test Device');
    cy.get('[data-testid="device-type-select"]').select('computer');
    cy.get('[data-testid="issue-performance"]').check();
    cy.get('[data-testid="create-diagnostic-button"]').click();
    
    // 2. Verificar criação
    cy.url().should('include', '/diagnostics/');
    
    // 3. Cancelar diagnóstico
    cy.get('[data-testid="cancel-diagnostic"]').click();
    cy.get('[data-testid="cancellation-reason"]').type('Cliente desistiu do serviço');
    cy.get('[data-testid="confirm-cancellation"]').click();
    
    // 4. Verificar status cancelado
    cy.get('[data-testid="status-badge"]').should('contain', 'Cancelado');
    cy.get('[data-testid="cancellation-details"]').should('be.visible');
    cy.get('[data-testid="cancellation-reason-display"]').should('contain', 'Cliente desistiu do serviço');
  });
});