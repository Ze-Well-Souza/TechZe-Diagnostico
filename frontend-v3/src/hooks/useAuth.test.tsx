import React from 'react';
import { renderHook, act, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from './useAuth';
import { supabase } from '@/integrations/supabase/client';
import { useToast } from '@/hooks/use-toast';

// Mock do Supabase
jest.mock('@/integrations/supabase/client', () => ({
  supabase: {
    auth: {
      getSession: jest.fn(),
      onAuthStateChange: jest.fn(),
      signInWithPassword: jest.fn(),
      signUp: jest.fn(),
      signOut: jest.fn(),
    },
  },
}));

// Mock do useToast
jest.mock('@/hooks/use-toast', () => ({
  useToast: jest.fn(),
}));

const mockToast = jest.fn();
const mockSupabase = supabase as jest.Mocked<typeof supabase>;

// Wrapper para fornecer o AuthProvider
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
);

describe('useAuth', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Configuração padrão dos mocks
    (useToast as jest.Mock).mockReturnValue({ toast: mockToast });
    
    // Mock da sessão inicial
    mockSupabase.auth.getSession.mockResolvedValue({
      data: { session: null },
      error: null,
    });
    
    // Mock do listener de mudanças de autenticação
    mockSupabase.auth.onAuthStateChange.mockReturnValue({
      data: {
        subscription: {
          unsubscribe: jest.fn(),
        },
      },
    });
  });

  it('deve lançar erro quando usado fora do AuthProvider', () => {
    // Suprime o erro do console para este teste
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    expect(() => {
      renderHook(() => useAuth());
    }).toThrow('useAuth must be used within an AuthProvider');
    
    consoleSpy.mockRestore();
  });

  it('deve inicializar com valores padrão', async () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    // Verifica os valores iniciais
    expect(result.current.user).toBeNull();
    expect(result.current.session).toBeNull();
    expect(result.current.loading).toBe(true);
    
    // Aguarda o carregamento inicial
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
  });

  it('deve definir usuário e sessão quando há uma sessão ativa', async () => {
    const mockUser = {
      id: 'user-id',
      email: 'usuario@exemplo.com',
      user_metadata: { full_name: 'Usuário Teste' },
    };
    
    const mockSession = {
      user: mockUser,
      access_token: 'access-token',
      refresh_token: 'refresh-token',
    };
    
    mockSupabase.auth.getSession.mockResolvedValue({
      data: { session: mockSession },
      error: null,
    });
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await waitFor(() => {
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.session).toEqual(mockSession);
      expect(result.current.loading).toBe(false);
    });
  });

  it('deve fazer login com sucesso', async () => {
    mockSupabase.auth.signInWithPassword.mockResolvedValue({
      data: { user: null, session: null },
      error: null,
    });
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    let signInResult;
    await act(async () => {
      signInResult = await result.current.signIn('usuario@exemplo.com', 'senha123');
    });
    
    expect(mockSupabase.auth.signInWithPassword).toHaveBeenCalledWith({
      email: 'usuario@exemplo.com',
      password: 'senha123',
    });
    
    expect(signInResult).toEqual({ error: null });
    
    expect(mockToast).toHaveBeenCalledWith({
      title: 'Login realizado com sucesso!',
      description: 'Bem-vindo ao TechRepair Pro',
    });
  });

  it('deve exibir erro ao falhar no login', async () => {
    const mockError = { message: 'Credenciais inválidas' };
    
    mockSupabase.auth.signInWithPassword.mockResolvedValue({
      data: { user: null, session: null },
      error: mockError,
    });
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    let signInResult;
    await act(async () => {
      signInResult = await result.current.signIn('usuario@exemplo.com', 'senhaerrada');
    });
    
    expect(signInResult).toEqual({ error: mockError });
    
    expect(mockToast).toHaveBeenCalledWith({
      title: 'Erro ao fazer login',
      description: 'Credenciais inválidas',
      variant: 'destructive',
    });
  });

  it('deve fazer cadastro com sucesso', async () => {
    mockSupabase.auth.signUp.mockResolvedValue({
      data: { user: null, session: null },
      error: null,
    });
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    let signUpResult;
    await act(async () => {
      signUpResult = await result.current.signUp(
        'novousuario@exemplo.com',
        'senha123',
        'Novo Usuário'
      );
    });
    
    expect(mockSupabase.auth.signUp).toHaveBeenCalledWith({
      email: 'novousuario@exemplo.com',
      password: 'senha123',
      options: {
        data: {
          full_name: 'Novo Usuário',
        },
      },
    });
    
    expect(signUpResult).toEqual({ error: null });
    
    expect(mockToast).toHaveBeenCalledWith({
      title: 'Conta criada com sucesso!',
      description: 'Verifique seu email para confirmar a conta',
    });
  });

  it('deve exibir erro ao falhar no cadastro', async () => {
    const mockError = { message: 'Email já está em uso' };
    
    mockSupabase.auth.signUp.mockResolvedValue({
      data: { user: null, session: null },
      error: mockError,
    });
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    let signUpResult;
    await act(async () => {
      signUpResult = await result.current.signUp(
        'usuario@exemplo.com',
        'senha123',
        'Usuário Teste'
      );
    });
    
    expect(signUpResult).toEqual({ error: mockError });
    
    expect(mockToast).toHaveBeenCalledWith({
      title: 'Erro ao criar conta',
      description: 'Email já está em uso',
      variant: 'destructive',
    });
  });

  it('deve fazer logout com sucesso', async () => {
    mockSupabase.auth.signOut.mockResolvedValue({
      error: null,
    });
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    await act(async () => {
      await result.current.signOut();
    });
    
    expect(mockSupabase.auth.signOut).toHaveBeenCalled();
    
    expect(mockToast).toHaveBeenCalledWith({
      title: 'Logout realizado com sucesso!',
      description: 'Até logo!',
    });
  });

  it('deve exibir erro ao falhar no logout', async () => {
    const mockError = { message: 'Erro interno do servidor' };
    
    mockSupabase.auth.signOut.mockResolvedValue({
      error: mockError,
    });
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    await act(async () => {
      await result.current.signOut();
    });
    
    expect(mockToast).toHaveBeenCalledWith({
      title: 'Erro ao fazer logout',
      description: 'Erro interno do servidor',
      variant: 'destructive',
    });
  });

  it('deve atualizar o estado quando a autenticação muda', async () => {
    let authStateChangeCallback: (event: string, session: any) => void;
    
    mockSupabase.auth.onAuthStateChange.mockImplementation((callback) => {
      authStateChangeCallback = callback;
      return {
        data: {
          subscription: {
            unsubscribe: jest.fn(),
          },
        },
      };
    });
    
    const { result } = renderHook(() => useAuth(), { wrapper });
    
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });
    
    // Simula uma mudança de estado de autenticação
    const mockUser = {
      id: 'user-id',
      email: 'usuario@exemplo.com',
    };
    
    const mockSession = {
      user: mockUser,
      access_token: 'access-token',
    };
    
    act(() => {
      authStateChangeCallback!('SIGNED_IN', mockSession);
    });
    
    expect(result.current.user).toEqual(mockUser);
    expect(result.current.session).toEqual(mockSession);
  });
});