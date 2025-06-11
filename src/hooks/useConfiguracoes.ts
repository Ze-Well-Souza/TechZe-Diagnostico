import { useState, useEffect, useCallback } from 'react';
import { useToast } from '@/components/ui/use-toast';
import { useNotifications } from './useNotifications';

export interface LojaConfig {
  // Informações Básicas
  nome: string;
  cnpj: string;
  endereco: string;
  telefone: string;
  email: string;
  website: string;
  
  // Configurações de Funcionamento
  horarioAbertura: string;
  horarioFechamento: string;
  diasFuncionamento: string[];
  tempoMedioReparo: number;
  
  // Configurações de Notificação
  notificacaoEmail: boolean;
  notificacaoSMS: boolean;
  notificacaoWhatsApp: boolean;
  
  // Configurações Visuais
  tema: 'light' | 'dark' | 'auto';
  corPrimaria: string;
  corSecundaria: string;
  logo: string;
  
  // Configurações de Segurança
  autenticacao2FA: boolean;
  sessaoTimeout: number;
  logAuditoria: boolean;
  
  // Configurações de Backup
  backupAutomatico: boolean;
  frequenciaBackup: 'diario' | 'semanal' | 'mensal';
  retencaoBackup: number;
}

export interface BackupInfo {
  ultimoBackup: Date | null;
  proximoBackup: Date | null;
  totalBackups: number;
  espacoUtilizado: string;
  status: 'ativo' | 'inativo' | 'erro';
}

export interface ValidationError {
  field: string;
  message: string;
}

const configPadrao: LojaConfig = {
  nome: 'TechZe Diagnóstico',
  cnpj: '',
  endereco: '',
  telefone: '',
  email: '',
  website: '',
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

export function useConfiguracoes() {
  const { toast } = useToast();
  const { addNotification } = useNotifications();
  
  const [config, setConfig] = useState<LojaConfig>(configPadrao);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [backupInfo, setBackupInfo] = useState<BackupInfo>({
    ultimoBackup: new Date(),
    proximoBackup: new Date(Date.now() + 24 * 60 * 60 * 1000),
    totalBackups: 15,
    espacoUtilizado: '2.3 GB',
    status: 'ativo'
  });
  const [errors, setErrors] = useState<ValidationError[]>([]);

  // Carregar configurações
  const carregarConfiguracoes = useCallback(async () => {
    try {
      setLoading(true);
      setErrors([]);
      
      // Simular delay da API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Aqui seria feita a chamada real para a API
      // const response = await configAPI.buscar();
      // setConfig(response.data);
      
      // Por enquanto, usar dados do localStorage se existirem
      const savedConfig = localStorage.getItem('loja-config');
      if (savedConfig) {
        const parsedConfig = JSON.parse(savedConfig);
        setConfig({ ...configPadrao, ...parsedConfig });
      }
      
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
      toast({
        title: "Erro",
        description: "Erro ao carregar configurações da loja",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  }, [toast]);

  // Validar configurações
  const validarConfiguracoes = useCallback((configToValidate: LojaConfig): ValidationError[] => {
    const newErrors: ValidationError[] = [];

    // Validações obrigatórias
    if (!configToValidate.nome.trim()) {
      newErrors.push({ field: 'nome', message: 'Nome da loja é obrigatório' });
    }

    // Validação de CNPJ (formato básico)
    if (configToValidate.cnpj && !/^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/.test(configToValidate.cnpj)) {
      newErrors.push({ field: 'cnpj', message: 'CNPJ deve estar no formato 00.000.000/0000-00' });
    }

    // Validação de email
    if (configToValidate.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(configToValidate.email)) {
      newErrors.push({ field: 'email', message: 'E-mail deve ter um formato válido' });
    }

    // Validação de telefone (formato básico)
    if (configToValidate.telefone && !/^\(\d{2}\)\s\d{4,5}-\d{4}$/.test(configToValidate.telefone)) {
      newErrors.push({ field: 'telefone', message: 'Telefone deve estar no formato (00) 00000-0000' });
    }

    // Validação de website
    if (configToValidate.website && !/^https?:\/\/.+/.test(configToValidate.website)) {
      newErrors.push({ field: 'website', message: 'Website deve começar com http:// ou https://' });
    }

    // Validação de horários
    if (configToValidate.horarioAbertura >= configToValidate.horarioFechamento) {
      newErrors.push({ field: 'horarioFechamento', message: 'Horário de fechamento deve ser após o de abertura' });
    }

    // Validação de dias de funcionamento
    if (configToValidate.diasFuncionamento.length === 0) {
      newErrors.push({ field: 'diasFuncionamento', message: 'Selecione pelo menos um dia de funcionamento' });
    }

    // Validação de tempo médio de reparo
    if (configToValidate.tempoMedioReparo < 1 || configToValidate.tempoMedioReparo > 168) {
      newErrors.push({ field: 'tempoMedioReparo', message: 'Tempo médio deve estar entre 1 e 168 horas' });
    }

    // Validação de cores (formato hex)
    if (!/^#[0-9A-F]{6}$/i.test(configToValidate.corPrimaria)) {
      newErrors.push({ field: 'corPrimaria', message: 'Cor primária deve estar no formato #RRGGBB' });
    }

    if (!/^#[0-9A-F]{6}$/i.test(configToValidate.corSecundaria)) {
      newErrors.push({ field: 'corSecundaria', message: 'Cor secundária deve estar no formato #RRGGBB' });
    }

    // Validação de timeout de sessão
    if (configToValidate.sessaoTimeout < 5 || configToValidate.sessaoTimeout > 480) {
      newErrors.push({ field: 'sessaoTimeout', message: 'Timeout deve estar entre 5 e 480 minutos' });
    }

    // Validação de retenção de backup
    if (configToValidate.retencaoBackup < 7 || configToValidate.retencaoBackup > 365) {
      newErrors.push({ field: 'retencaoBackup', message: 'Retenção deve estar entre 7 e 365 dias' });
    }

    return newErrors;
  }, []);

  // Salvar configurações
  const salvarConfiguracoes = useCallback(async (configToSave?: LojaConfig) => {
    const configParaSalvar = configToSave || config;
    
    try {
      setSaving(true);
      
      // Validar antes de salvar
      const validationErrors = validarConfiguracoes(configParaSalvar);
      if (validationErrors.length > 0) {
        setErrors(validationErrors);
        toast({
          title: "Erro de Validação",
          description: `${validationErrors.length} erro(s) encontrado(s). Verifique os campos destacados.`,
          variant: "destructive"
        });
        return false;
      }
      
      setErrors([]);
      
      // Simular delay da API
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Aqui seria feita a chamada real para a API
      // await configAPI.atualizar(configParaSalvar);
      
      // Por enquanto, salvar no localStorage
      localStorage.setItem('loja-config', JSON.stringify(configParaSalvar));
      
      // Aplicar tema se mudou
      if (configParaSalvar.tema !== config.tema) {
        aplicarTema(configParaSalvar.tema);
      }
      
      // Aplicar cores se mudaram
      if (configParaSalvar.corPrimaria !== config.corPrimaria || 
          configParaSalvar.corSecundaria !== config.corSecundaria) {
        aplicarCores(configParaSalvar.corPrimaria, configParaSalvar.corSecundaria);
      }
      
      setConfig(configParaSalvar);
      
      toast({
        title: "Sucesso",
        description: "Configurações salvas com sucesso"
      });
      
      addNotification({
        type: 'success',
        title: 'Configurações Atualizadas',
        message: 'As configurações da loja foram salvas com sucesso.',
        timestamp: new Date()
      });
      
      return true;
      
    } catch (error) {
      console.error('Erro ao salvar configurações:', error);
      toast({
        title: "Erro",
        description: "Erro ao salvar configurações",
        variant: "destructive"
      });
      return false;
    } finally {
      setSaving(false);
    }
  }, [config, validarConfiguracoes, toast, addNotification]);

  // Aplicar tema
  const aplicarTema = useCallback((tema: 'light' | 'dark' | 'auto') => {
    const root = document.documentElement;
    
    if (tema === 'auto') {
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', prefersDark);
    } else {
      root.classList.toggle('dark', tema === 'dark');
    }
  }, []);

  // Aplicar cores personalizadas
  const aplicarCores = useCallback((corPrimaria: string, corSecundaria: string) => {
    const root = document.documentElement;
    
    // Converter hex para HSL para criar variações
    const hexToHsl = (hex: string) => {
      const r = parseInt(hex.slice(1, 3), 16) / 255;
      const g = parseInt(hex.slice(3, 5), 16) / 255;
      const b = parseInt(hex.slice(5, 7), 16) / 255;
      
      const max = Math.max(r, g, b);
      const min = Math.min(r, g, b);
      let h = 0, s = 0, l = (max + min) / 2;
      
      if (max !== min) {
        const d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        
        switch (max) {
          case r: h = (g - b) / d + (g < b ? 6 : 0); break;
          case g: h = (b - r) / d + 2; break;
          case b: h = (r - g) / d + 4; break;
        }
        h /= 6;
      }
      
      return [Math.round(h * 360), Math.round(s * 100), Math.round(l * 100)];
    };
    
    const [h, s, l] = hexToHsl(corPrimaria);
    
    root.style.setProperty('--primary', `${h} ${s}% ${l}%`);
    root.style.setProperty('--primary-foreground', l > 50 ? '0 0% 0%' : '0 0% 100%');
  }, []);

  // Exportar configurações
  const exportarConfiguracoes = useCallback(async () => {
    try {
      const dataStr = JSON.stringify(config, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = `configuracoes-loja-${new Date().toISOString().split('T')[0]}.json`;
      link.click();
      
      URL.revokeObjectURL(url);
      
      toast({
        title: "Sucesso",
        description: "Configurações exportadas com sucesso"
      });
      
      addNotification({
        type: 'info',
        title: 'Configurações Exportadas',
        message: 'Arquivo de configurações baixado com sucesso.',
        timestamp: new Date()
      });
      
    } catch (error) {
      console.error('Erro ao exportar configurações:', error);
      toast({
        title: "Erro",
        description: "Erro ao exportar configurações",
        variant: "destructive"
      });
    }
  }, [config, toast, addNotification]);

  // Importar configurações
  const importarConfiguracoes = useCallback(async (file: File) => {
    try {
      const text = await file.text();
      const importedConfig = JSON.parse(text);
      
      // Validar configurações importadas
      const validationErrors = validarConfiguracoes({ ...configPadrao, ...importedConfig });
      if (validationErrors.length > 0) {
        setErrors(validationErrors);
        toast({
          title: "Erro de Validação",
          description: "Arquivo contém configurações inválidas",
          variant: "destructive"
        });
        return false;
      }
      
      setConfig({ ...configPadrao, ...importedConfig });
      setErrors([]);
      
      toast({
        title: "Sucesso",
        description: "Configurações importadas com sucesso"
      });
      
      addNotification({
        type: 'success',
        title: 'Configurações Importadas',
        message: 'Configurações carregadas do arquivo com sucesso.',
        timestamp: new Date()
      });
      
      return true;
      
    } catch (error) {
      console.error('Erro ao importar configurações:', error);
      toast({
        title: "Erro",
        description: "Arquivo de configuração inválido",
        variant: "destructive"
      });
      return false;
    }
  }, [validarConfiguracoes, toast, addNotification]);

  // Resetar configurações
  const resetarConfiguracoes = useCallback(() => {
    setConfig(configPadrao);
    setErrors([]);
    localStorage.removeItem('loja-config');
    
    toast({
      title: "Configurações Resetadas",
      description: "Todas as configurações foram restauradas para os valores padrão"
    });
  }, [toast]);

  // Criar backup manual
  const criarBackupManual = useCallback(async () => {
    try {
      setLoading(true);
      
      // Simular criação de backup
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Aqui seria feita a chamada real para a API
      // await backupAPI.criarManual();
      
      setBackupInfo(prev => ({
        ...prev,
        ultimoBackup: new Date(),
        totalBackups: prev.totalBackups + 1
      }));
      
      toast({
        title: "Sucesso",
        description: "Backup criado com sucesso"
      });
      
      addNotification({
        type: 'success',
        title: 'Backup Criado',
        message: 'Backup manual dos dados foi criado com sucesso.',
        timestamp: new Date()
      });
      
    } catch (error) {
      console.error('Erro ao criar backup:', error);
      toast({
        title: "Erro",
        description: "Erro ao criar backup",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  }, [toast, addNotification]);

  // Carregar configurações na inicialização
  useEffect(() => {
    carregarConfiguracoes();
  }, [carregarConfiguracoes]);

  // Aplicar tema na inicialização
  useEffect(() => {
    aplicarTema(config.tema);
  }, [config.tema, aplicarTema]);

  return {
    // Estado
    config,
    loading,
    saving,
    errors,
    backupInfo,
    
    // Ações
    setConfig,
    carregarConfiguracoes,
    salvarConfiguracoes,
    validarConfiguracoes,
    exportarConfiguracoes,
    importarConfiguracoes,
    resetarConfiguracoes,
    criarBackupManual,
    aplicarTema,
    aplicarCores,
    
    // Utilitários
    hasErrors: errors.length > 0,
    getFieldError: (field: string) => errors.find(e => e.field === field)?.message,
    isFieldValid: (field: string) => !errors.some(e => e.field === field)
  };
}