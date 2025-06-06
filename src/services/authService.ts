import { apiClient } from "./apiClient";

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user_info: {
    id: string;
    email: string;
    name: string;
    role: string;
  };
}

export interface LoginRequest {
  email: string;
  password: string;
}

export class AuthService {
  private static readonly TOKEN_KEY = 'techze_auth_token';
  private static readonly USER_KEY = 'techze_user_info';

  /**
   * Realiza login usando o endpoint de auth do backend
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      console.log("Tentando login via backend auth...");
      
      // Usar FormData para compatibilidade com OAuth2PasswordRequestForm
      const formData = new FormData();
      formData.append('username', credentials.email);
      formData.append('password', credentials.password);

      const response = await fetch(`${apiClient.baseURL}/api/v1/auth/token`, {
        method: 'POST',
        body: formData,
        headers: {
          'Accept': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Erro ao fazer login');
      }

      const authData: AuthResponse = await response.json();
      
      // Salvar token e dados do usuário
      this.saveAuthData(authData);
      
      return authData;
    } catch (error) {
      console.error("Erro no login:", error);
      throw error;
    }
  }

  /**
   * Verifica se há token válido salvo
   */
  isAuthenticated(): boolean {
    const token = this.getToken();
    if (!token) return false;

    try {
      // Verificar se token não expirou (básico)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      
      return payload.exp > currentTime;
    } catch {
      return false;
    }
  }

  /**
   * Obtém token de acesso salvo
   */
  getToken(): string | null {
    return localStorage.getItem(AuthService.TOKEN_KEY);
  }

  /**
   * Obtém informações do usuário salvas
   */
  getUserInfo(): AuthResponse['user_info'] | null {
    const userInfo = localStorage.getItem(AuthService.USER_KEY);
    return userInfo ? JSON.parse(userInfo) : null;
  }

  /**
   * Realiza logout limpando dados locais
   */
  async logout(): Promise<void> {
    try {
      // Tentar logout no backend (opcional)
      const token = this.getToken();
      if (token) {
        try {
          await fetch(`${apiClient.baseURL}/api/v1/auth/logout`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          });
        } catch (error) {
          console.warn("Erro ao fazer logout no backend:", error);
        }
      }
    } finally {
      // Sempre limpar dados locais
      this.clearAuthData();
    }
  }

  /**
   * Verifica saúde do sistema de autenticação
   */
  async checkAuthHealth(): Promise<{ status: string; supabase_connected: boolean }> {
    try {
      const response = await fetch(`${apiClient.baseURL}/api/v1/auth/health`);
      return await response.json();
    } catch (error) {
      console.error("Erro ao verificar saúde da auth:", error);
      return { status: 'unhealthy', supabase_connected: false };
    }
  }

  /**
   * Salva dados de autenticação no localStorage
   */
  private saveAuthData(authData: AuthResponse): void {
    localStorage.setItem(AuthService.TOKEN_KEY, authData.access_token);
    localStorage.setItem(AuthService.USER_KEY, JSON.stringify(authData.user_info));
  }

  /**
   * Remove dados de autenticação do localStorage
   */
  private clearAuthData(): void {
    localStorage.removeItem(AuthService.TOKEN_KEY);
    localStorage.removeItem(AuthService.USER_KEY);
  }
}

// Instância singleton
export const authService = new AuthService(); 