import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Header } from './Header';
import { useAuth } from '@/hooks/useAuth';

// Mock do hook useAuth
jest.mock('@/hooks/useAuth', () => ({
  useAuth: jest.fn(),
}));

// Mock do useLocation
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useLocation: () => ({ pathname: '/' }),
}));

// Mock dos componentes de UI que usam portais
jest.mock('@/components/ui/dropdown-menu', () => ({
  DropdownMenu: ({ children }: { children: React.ReactNode }) => <div data-testid="dropdown-menu">{children}</div>,
  DropdownMenuTrigger: ({ children }: { children: React.ReactNode }) => <div data-testid="dropdown-trigger">{children}</div>,
  DropdownMenuContent: ({ children }: { children: React.ReactNode }) => <div data-testid="dropdown-content">{children}</div>,
  DropdownMenuItem: ({ children, onClick }: { children: React.ReactNode, onClick?: () => void }) => 
    <button data-testid={`dropdown-item-${typeof children === 'string' ? children : 'custom'}`} onClick={onClick}>{children}</button>,
  DropdownMenuSeparator: () => <hr data-testid="dropdown-separator" />,
}));

// Componente wrapper para fornecer o BrowserRouter
const HeaderWithRouter = () => (
  <BrowserRouter>
    <Header />
  </BrowserRouter>
);

describe('Header', () => {
  // Configuração do mock para usuário não autenticado
  beforeEach(() => {
    (useAuth as jest.Mock).mockReturnValue({
      user: null,
      signOut: jest.fn(),
    });
  });

  // Salva e restaura o valor original de innerWidth
  const originalInnerWidth = window.innerWidth;
  
  afterEach(() => {
    // Restaura o valor original após cada teste
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: originalInnerWidth });
  });

  it('deve renderizar o logo e o nome da aplicação', () => {
    render(<HeaderWithRouter />);
    
    expect(screen.getByText('TechRepair')).toBeInTheDocument();
  });

  it('deve renderizar os links de navegação', () => {
    render(<HeaderWithRouter />);
    
    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Diagnóstico')).toBeInTheDocument();
    expect(screen.getByText('Histórico')).toBeInTheDocument();
    expect(screen.getByText('Relatórios')).toBeInTheDocument();
  });

  it('deve renderizar os botões de login e cadastro quando o usuário não está autenticado', () => {
    render(<HeaderWithRouter />);
    
    expect(screen.getAllByText('Login')[0]).toBeInTheDocument();
    expect(screen.getAllByText('Cadastrar')[0]).toBeInTheDocument();
  });

  it('deve renderizar o menu do usuário quando o usuário está autenticado', () => {
    // Configuração do mock para usuário autenticado
    (useAuth as jest.Mock).mockReturnValue({
      user: {
        email: 'usuario@exemplo.com',
        user_metadata: {
          company_name: 'Empresa Teste'
        }
      },
      signOut: jest.fn(),
    });

    render(<HeaderWithRouter />);
    
    // Verifica se o avatar está presente
    expect(screen.getByText('U')).toBeInTheDocument();
  });

  it('deve chamar a função signOut quando o botão de sair é clicado', () => {
    const mockSignOut = jest.fn();
    
    // Configuração do mock para usuário autenticado com função signOut mockada
    (useAuth as jest.Mock).mockReturnValue({
      user: {
        email: 'usuario@exemplo.com',
        user_metadata: {
          company_name: 'Empresa Teste'
        }
      },
      signOut: mockSignOut,
    });

    render(<HeaderWithRouter />);
    
    // Encontra e clica no botão de sair no dropdown
    const logoutButton = screen.getByTestId('dropdown-item-Sair');
    fireEvent.click(logoutButton);
    
    expect(mockSignOut).toHaveBeenCalled();
  });

  it('deve abrir o menu mobile quando o botão é clicado', () => {
    // Ajusta a largura da viewport para simular um dispositivo móvel
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 500 });
    global.dispatchEvent(new Event('resize'));
    
    render(<HeaderWithRouter />);
    
    // Encontra e clica no botão do menu mobile
    const menuButton = screen.getByRole('button', { name: '' }); // O botão não tem texto, apenas ícone
    fireEvent.click(menuButton);
    
    // Verifica se o menu mobile está visível
    expect(screen.getAllByText('Home').length).toBe(2); // Um no desktop, um no mobile
  });

  it('deve fechar o menu mobile quando um link é clicado', () => {
    // Ajusta a largura da viewport para simular um dispositivo móvel
    Object.defineProperty(window, 'innerWidth', { writable: true, configurable: true, value: 500 });
    global.dispatchEvent(new Event('resize'));
    
    render(<HeaderWithRouter />);
    
    // Abre o menu mobile
    const menuButton = screen.getByRole('button', { name: '' });
    fireEvent.click(menuButton);
    
    // Clica em um link do menu mobile
    const dashboardLink = screen.getAllByText('Dashboard')[1]; // O segundo é o do menu mobile
    fireEvent.click(dashboardLink);
    
    // Verifica se o menu mobile foi fechado
    expect(screen.getAllByText('Home').length).toBe(1); // Apenas o do desktop está visível
  });

  it('deve destacar o link ativo com base na rota atual', () => {
    // Mock do useLocation para simular a rota atual como /dashboard
    jest.spyOn(require('react-router-dom'), 'useLocation').mockReturnValue({ pathname: '/dashboard' });
    
    render(<HeaderWithRouter />);
    
    // Verifica se o link Dashboard tem a classe de ativo
    const dashboardLink = screen.getByText('Dashboard');
    expect(dashboardLink.className).toContain('bg-electric/20');
    
    // Verifica se os outros links não têm a classe de ativo
    const homeLink = screen.getByText('Home');
    expect(homeLink.className).not.toContain('bg-electric/20');
  });
});