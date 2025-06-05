import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { jest } from '@jest/globals';
import MobileOptimized from './MobileOptimized';

// Mock dos hooks
jest.mock('../../hooks/useIsMobile', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue(true)
}));

jest.mock('../../hooks/useInstallPWA', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue({
    canInstall: true,
    isInstalled: false,
    promptInstall: jest.fn()
  })
}));

jest.mock('../../hooks/useOfflineStatus', () => ({
  __esModule: true,
  default: jest.fn().mockReturnValue({
    isOnline: true,
    offlineData: [],
    saveForLater: jest.fn()
  })
}));

describe('MobileOptimized', () => {
  beforeEach(() => {
    // Mock para navigator.standalone
    Object.defineProperty(window.navigator, 'standalone', {
      configurable: true,
      value: false
    });

    // Mock para matchMedia
    window.matchMedia = jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));
  });

  test('renderiza o conteúdo filho', () => {
    render(
      <MobileOptimized>
        <div data-testid="child-content">Conteúdo filho</div>
      </MobileOptimized>
    );
    
    expect(screen.getByTestId('child-content')).toBeInTheDocument();
  });

  test('aplica otimizações para dispositivos móveis', () => {
    render(
      <MobileOptimized>
        <div>Conteúdo</div>
      </MobileOptimized>
    );
    
    const container = screen.getByTestId('mobile-optimized-container');
    expect(container).toHaveClass('mobile-optimized');
  });

  test('abre e fecha o menu', () => {
    render(
      <MobileOptimized>
        <div>Conteúdo</div>
      </MobileOptimized>
    );
    
    const menuButton = screen.getByLabelText('Menu');
    fireEvent.click(menuButton);
    
    expect(screen.getByTestId('mobile-menu')).toHaveClass('open');
    
    const closeButton = screen.getByLabelText('Fechar menu');
    fireEvent.click(closeButton);
    
    expect(screen.getByTestId('mobile-menu')).not.toHaveClass('open');
  });

  test('mostra botão de instalação PWA quando disponível', () => {
    const useInstallPWA = jest.requireMock('../../hooks/useInstallPWA').default;
    useInstallPWA.mockReturnValue({
      canInstall: true,
      isInstalled: false,
      promptInstall: jest.fn()
    });

    render(
      <MobileOptimized>
        <div>Conteúdo</div>
      </MobileOptimized>
    );
    
    expect(screen.getByText('Instalar App')).toBeInTheDocument();
  });

  test('mostra indicador offline quando offline', () => {
    const useOfflineStatus = jest.requireMock('../../hooks/useOfflineStatus').default;
    useOfflineStatus.mockReturnValue({
      isOnline: false,
      offlineData: [],
      saveForLater: jest.fn()
    });

    render(
      <MobileOptimized>
        <div>Conteúdo</div>
      </MobileOptimized>
    );
    
    expect(screen.getByText('Você está offline')).toBeInTheDocument();
  });

  test('detecta modo standalone', () => {
    // Simular modo standalone
    Object.defineProperty(window.navigator, 'standalone', {
      configurable: true,
      value: true
    });

    render(
      <MobileOptimized>
        <div>Conteúdo</div>
      </MobileOptimized>
    );
    
    const container = screen.getByTestId('mobile-optimized-container');
    expect(container).toHaveClass('standalone-mode');
  });
});