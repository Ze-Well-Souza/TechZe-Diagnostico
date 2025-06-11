import { useState, useEffect } from 'react';
import { authService, type Usuario } from '../lib/supabase';

interface AuthState {
  user: Usuario | null;
  loading: boolean;
  isAuthenticated: boolean;
  userType: 'master_admin' | 'admin_loja' | 'tecnico' | null;
}

export const useAuth = () => {
  const [authState, setAuthState] = useState<AuthState>({
    user: null,
    loading: true,
    isAuthenticated: false,
    userType: null
  });

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Verificar localStorage primeiro (modo dev)
      const userType = localStorage.getItem('user_type') as 'master_admin' | 'admin_loja' | 'tecnico' | null;
      const userEmail = localStorage.getItem('user_email');
      const authToken = localStorage.getItem('auth_token');

      if (userType && userEmail && authToken) {
        // Simular usuário para desenvolvimento
        const mockUser: Usuario = {
          id: 'mock-user-id',
          email: userEmail,
          nome: userType === 'master_admin' ? 'Administrador Master' : 'Usuário',
          tipo: userType,
          ativo: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };

        setAuthState({
          user: mockUser,
          loading: false,
          isAuthenticated: true,
          userType
        });
        return;
      }

      // Implementação real do Supabase (comentado para desenvolvimento)
      /*
      try {
        const { user } = await authService.getCurrentUser();
        
        if (user) {
          const { data: profile } = await authService.getUserProfile(user.id);
          
          if (profile && profile.ativo) {
            setAuthState({
              user: profile,
              loading: false,
              isAuthenticated: true,
              userType: profile.tipo
            });
          } else {
            logout();
          }
        } else {
          setAuthState({
            user: null,
            loading: false,
            isAuthenticated: false,
            userType: null
          });
        }
      } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        setAuthState({
          user: null,
          loading: false,
          isAuthenticated: false,
          userType: null
        });
      }
      */
      
      // Se não há dados locais, usuário não está autenticado
      setAuthState({
        user: null,
        loading: false,
        isAuthenticated: false,
        userType: null
      });
    } catch (error) {
      console.error('Erro ao verificar autenticação:', error);
      setAuthState({
        user: null,
        loading: false,
        isAuthenticated: false,
        userType: null
      });
    }
  };

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      // Modo desenvolvimento
      if (email === 'admin@techrepair.com' && password === 'admin123') {
        localStorage.setItem('user_type', 'master_admin');
        localStorage.setItem('user_email', email);
        localStorage.setItem('auth_token', 'demo_token_' + Date.now());
        
        await checkAuthStatus();
        return { success: true };
      }

      return { success: false, error: 'Credenciais inválidas' };

      // Implementação real do login com Supabase
      try {
        const { data, error } = await authService.signIn(email, password);
        
        if (error) {
          return { success: false, error: 'Credenciais inválidas ou erro no servidor' };
        }

        if (data.user) {
          await checkAuthStatus();
          return { success: true };
        }

        return { success: false, error: 'Erro inesperado' };
      } catch (error) {
        console.error('Erro no login:', error);
        return { success: false, error: 'Credenciais inválidas' };
      }
    } catch (error) {
      return { success: false, error: 'Erro ao fazer login' };
    }
  };

  const logout = async () => {
    try {
      // Limpar localStorage
      localStorage.removeItem('user_type');
      localStorage.removeItem('user_email');
      localStorage.removeItem('auth_token');

      // Implementação real do logout com Supabase
      try {
        await authService.signOut();
      } catch (error) {
        console.error('Erro no logout:', error);
      }

      setAuthState({
        user: null,
        loading: false,
        isAuthenticated: false,
        userType: null
      });
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    }
  };

  const hasPermission = (requiredPermission: 'master_admin' | 'admin_loja' | 'tecnico'): boolean => {
    if (!authState.isAuthenticated || !authState.userType) {
      return false;
    }

    // Master admin tem todas as permissões
    if (authState.userType === 'master_admin') {
      return true;
    }

    // Verificar permissão específica
    return authState.userType === requiredPermission;
  };

  const canAccessStore = (storeId?: string): boolean => {
    if (!authState.isAuthenticated || !authState.user) {
      return false;
    }

    // Master admin pode acessar todas as lojas
    if (authState.userType === 'master_admin') {
      return true;
    }

    // Admin de loja só pode acessar sua própria loja
    if (authState.userType === 'admin_loja') {
      return authState.user.loja_id === storeId;
    }

    return false;
  };

  return {
    ...authState,
    login,
    logout,
    hasPermission,
    canAccessStore,
    checkAuthStatus
  };
};