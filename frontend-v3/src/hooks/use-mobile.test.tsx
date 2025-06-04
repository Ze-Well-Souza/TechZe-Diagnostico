import { renderHook, act } from '@testing-library/react';
import { useIsMobile } from './use-mobile';

describe('useIsMobile', () => {
  const originalInnerWidth = window.innerWidth;
  const originalMatchMedia = window.matchMedia;

  // Mock para window.matchMedia
  const mockMatchMedia = (matches: boolean) => {
    window.matchMedia = jest.fn().mockImplementation((query) => ({
      matches,
      media: query,
      onchange: null,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));
  };

  // Restaura os valores originais após cada teste
  afterEach(() => {
    window.innerWidth = originalInnerWidth;
    window.matchMedia = originalMatchMedia;
  });

  it('deve retornar true quando a largura da tela é menor que o breakpoint mobile', () => {
    // Configura a largura da tela para um valor mobile (menor que 768px)
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 500 });
    mockMatchMedia(true);

    const { result } = renderHook(() => useIsMobile());

    expect(result.current).toBe(true);
  });

  it('deve retornar false quando a largura da tela é maior que o breakpoint mobile', () => {
    // Configura a largura da tela para um valor desktop (maior ou igual a 768px)
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 1024 });
    mockMatchMedia(false);

    const { result } = renderHook(() => useIsMobile());

    expect(result.current).toBe(false);
  });

  it('deve atualizar o valor quando a largura da tela muda', () => {
    // Inicialmente configura como desktop
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 1024 });
    
    // Cria um mock para addEventListener que captura o callback
    let changeCallback: () => void;
    window.matchMedia = jest.fn().mockImplementation(() => ({
      matches: false,
      addEventListener: (_: string, cb: () => void) => {
        changeCallback = cb;
      },
      removeEventListener: jest.fn(),
    }));

    const { result } = renderHook(() => useIsMobile());
    
    // Inicialmente deve ser false (desktop)
    expect(result.current).toBe(false);

    // Simula uma mudança para mobile
    act(() => {
      // Atualiza a largura da tela
      Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 500 });
      // Atualiza o valor de matches para true
      (window.matchMedia as jest.Mock).mockImplementation(() => ({
        matches: true,
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
      }));
      // Chama o callback para simular o evento de mudança
      changeCallback();
    });

    // Agora deve ser true (mobile)
    expect(result.current).toBe(true);
  });
});