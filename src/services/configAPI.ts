import { LojaConfig, BackupInfo } from '@/hooks/useConfiguracoes';

// Tipos para as requisições da API
export interface ConfigUpdateRequest {
  config: LojaConfig;
}

export interface ConfigResponse {
  success: boolean;
  data: LojaConfig;
  message?: string;
}

export interface BackupResponse {
  success: boolean;
  data: BackupInfo;
  message?: string;
}

export interface BackupCreateResponse {
  success: boolean;
  data: {
    backupId: string;
    filename: string;
    size: string;
    createdAt: Date;
  };
  message?: string;
}

export interface BackupListResponse {
  success: boolean;
  data: {
    backups: Array<{
      id: string;
      filename: string;
      size: string;
      createdAt: Date;
      type: 'manual' | 'automatico';
    }>;
    total: number;
  };
  message?: string;
}

class ConfigAPI {
  private baseURL = '/api/configuracoes';

  // Buscar configurações atuais
  async buscar(): Promise<ConfigResponse> {
    try {
      const response = await fetch(`${this.baseURL}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao buscar configurações:', error);
      throw new Error('Falha ao carregar configurações da loja');
    }
  }

  // Atualizar configurações
  async atualizar(config: LojaConfig): Promise<ConfigResponse> {
    try {
      const response = await fetch(`${this.baseURL}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ config })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao atualizar configurações:', error);
      throw new Error('Falha ao salvar configurações da loja');
    }
  }

  // Resetar configurações para padrão
  async resetar(): Promise<ConfigResponse> {
    try {
      const response = await fetch(`${this.baseURL}/reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao resetar configurações:', error);
      throw new Error('Falha ao resetar configurações');
    }
  }

  // Validar configurações
  async validar(config: LojaConfig): Promise<{ valid: boolean; errors: string[] }> {
    try {
      const response = await fetch(`${this.baseURL}/validar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ config })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao validar configurações:', error);
      throw new Error('Falha ao validar configurações');
    }
  }

  // Upload de logo
  async uploadLogo(file: File): Promise<{ success: boolean; url: string }> {
    try {
      const formData = new FormData();
      formData.append('logo', file);

      const response = await fetch(`${this.baseURL}/logo`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao fazer upload da logo:', error);
      throw new Error('Falha ao fazer upload da logo');
    }
  }

  // Remover logo
  async removerLogo(): Promise<{ success: boolean }> {
    try {
      const response = await fetch(`${this.baseURL}/logo`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao remover logo:', error);
      throw new Error('Falha ao remover logo');
    }
  }
}

class BackupAPI {
  private baseURL = '/api/backup';

  // Buscar informações de backup
  async buscarInfo(): Promise<BackupResponse> {
    try {
      const response = await fetch(`${this.baseURL}/info`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao buscar informações de backup:', error);
      throw new Error('Falha ao carregar informações de backup');
    }
  }

  // Criar backup manual
  async criarManual(): Promise<BackupCreateResponse> {
    try {
      const response = await fetch(`${this.baseURL}/manual`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao criar backup manual:', error);
      throw new Error('Falha ao criar backup manual');
    }
  }

  // Listar backups disponíveis
  async listar(page = 1, limit = 10): Promise<BackupListResponse> {
    try {
      const response = await fetch(`${this.baseURL}?page=${page}&limit=${limit}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao listar backups:', error);
      throw new Error('Falha ao listar backups');
    }
  }

  // Download de backup
  async download(backupId: string): Promise<Blob> {
    try {
      const response = await fetch(`${this.baseURL}/${backupId}/download`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      return blob;
    } catch (error) {
      console.error('Erro ao fazer download do backup:', error);
      throw new Error('Falha ao fazer download do backup');
    }
  }

  // Restaurar backup
  async restaurar(backupId: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseURL}/${backupId}/restaurar`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao restaurar backup:', error);
      throw new Error('Falha ao restaurar backup');
    }
  }

  // Upload de backup para restauração
  async uploadRestore(file: File): Promise<{ success: boolean; message: string }> {
    try {
      const formData = new FormData();
      formData.append('backup', file);

      const response = await fetch(`${this.baseURL}/upload-restore`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao fazer upload do backup:', error);
      throw new Error('Falha ao fazer upload do backup');
    }
  }

  // Deletar backup
  async deletar(backupId: string): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseURL}/${backupId}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao deletar backup:', error);
      throw new Error('Falha ao deletar backup');
    }
  }

  // Configurar backup automático
  async configurarAutomatico(config: {
    ativo: boolean;
    frequencia: 'diario' | 'semanal' | 'mensal';
    retencao: number;
    horario?: string;
  }): Promise<{ success: boolean; message: string }> {
    try {
      const response = await fetch(`${this.baseURL}/automatico`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(config)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Erro ao configurar backup automático:', error);
      throw new Error('Falha ao configurar backup automático');
    }
  }
}

// Instâncias das APIs
export const configAPI = new ConfigAPI();
export const backupAPI = new BackupAPI();

// Funções utilitárias
export const formatarTamanhoArquivo = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const formatarDataBackup = (date: Date): string => {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date));
};

export const validarArquivoBackup = (file: File): { valid: boolean; error?: string } => {
  // Verificar extensão
  if (!file.name.endsWith('.backup') && !file.name.endsWith('.sql') && !file.name.endsWith('.json')) {
    return {
      valid: false,
      error: 'Arquivo deve ter extensão .backup, .sql ou .json'
    };
  }
  
  // Verificar tamanho (máximo 100MB)
  const maxSize = 100 * 1024 * 1024; // 100MB
  if (file.size > maxSize) {
    return {
      valid: false,
      error: 'Arquivo muito grande. Tamanho máximo: 100MB'
    };
  }
  
  return { valid: true };
};

export const validarArquivoLogo = (file: File): { valid: boolean; error?: string } => {
  // Verificar tipo
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/svg+xml'];
  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Arquivo deve ser uma imagem (JPG, PNG ou SVG)'
    };
  }
  
  // Verificar tamanho (máximo 2MB)
  const maxSize = 2 * 1024 * 1024; // 2MB
  if (file.size > maxSize) {
    return {
      valid: false,
      error: 'Imagem muito grande. Tamanho máximo: 2MB'
    };
  }
  
  return { valid: true };
};

// Mock data para desenvolvimento
export const mockConfigData: LojaConfig = {
  nome: 'TechZe Diagnóstico',
  cnpj: '12.345.678/0001-90',
  endereco: 'Rua das Tecnologias, 123 - Centro, São Paulo - SP',
  telefone: '(11) 99999-9999',
  email: 'contato@techze.com.br',
  website: 'https://www.techze.com.br',
  horarioAbertura: '08:00',
  horarioFechamento: '18:00',
  diasFuncionamento: ['segunda', 'terca', 'quarta', 'quinta', 'sexta'],
  tempoMedioReparo: 24,
  notificacaoEmail: true,
  notificacaoSMS: false,
  notificacaoWhatsApp: true,
  tema: 'light',
  corPrimaria: '#3b82f6',
  corSecundaria: '#64748b',
  logo: '',
  autenticacao2FA: false,
  sessaoTimeout: 30,
  logAuditoria: true,
  backupAutomatico: true,
  frequenciaBackup: 'diario',
  retencaoBackup: 30
};

export const mockBackupInfo: BackupInfo = {
  ultimoBackup: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 dia atrás
  proximoBackup: new Date(Date.now() + 24 * 60 * 60 * 1000), // 1 dia à frente
  totalBackups: 15,
  espacoUtilizado: '2.3 GB',
  status: 'ativo'
};