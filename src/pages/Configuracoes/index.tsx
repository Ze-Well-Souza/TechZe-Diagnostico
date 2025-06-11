import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Settings, 
  Store, 
  Users, 
  Bell, 
  Palette, 
  Shield, 
  Database,
  Save,
  Upload,
  Download,
  RefreshCw,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle,
  FileText,
  Globe,
  Smartphone,
  Mail,
  CreditCard,
  Clock
} from 'lucide-react';
import { useConfiguracoes } from '@/hooks/useConfiguracoes';
import { useToast } from '@/hooks/use-toast';
import { validarArquivoLogo } from '@/services/configAPI';
import { ConfiguracaoGeral } from './components/ConfiguracaoGeral';
import { ConfiguracaoIntegracao } from './components/ConfiguracaoIntegracao';

// Interface removida - agora usando a do hook useConfiguracoes

const diasSemana = [
  { id: 'segunda', label: 'Segunda-feira' },
  { id: 'terca', label: 'Terça-feira' },
  { id: 'quarta', label: 'Quarta-feira' },
  { id: 'quinta', label: 'Quinta-feira' },
  { id: 'sexta', label: 'Sexta-feira' },
  { id: 'sabado', label: 'Sábado' },
  { id: 'domingo', label: 'Domingo' }
];

const temas = [
  { value: 'light', label: 'Claro' },
  { value: 'dark', label: 'Escuro' },
  { value: 'auto', label: 'Automático' }
];

const frequenciasBackup = [
  { value: 'diario', label: 'Diário' },
  { value: 'semanal', label: 'Semanal' },
  { value: 'mensal', label: 'Mensal' }
];

export default function Configuracoes() {
  const {
    config,
    setConfig,
    loading,
    saving,
    errors,
    backupInfo,
    salvarConfiguracoes,
    exportarConfiguracoes,
    importarConfiguracoes,
    criarBackupManual,
    hasErrors,
    getFieldError,
    isFieldValid
  } = useConfiguracoes();
  
  const [showPassword, setShowPassword] = useState(false);

  const handleImportarConfiguracoes = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      importarConfiguracoes(file);
      // Limpar o input para permitir reimportar o mesmo arquivo
      event.target.value = '';
    }
  };

  const handleUploadLogo = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    
    const validation = validarArquivoLogo(file);
    if (!validation.valid) {
      // Toast seria mostrado pelo hook
      return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = e.target?.result as string;
      setConfig({ ...config, logo: result });
    };
    reader.readAsDataURL(file);
    
    // Limpar o input
    event.target.value = '';
  };

  const handleDiaFuncionamentoChange = (dia: string, checked: boolean) => {
    if (checked) {
      setConfig({
        ...config,
        diasFuncionamento: [...config.diasFuncionamento, dia]
      });
    } else {
      setConfig({
        ...config,
        diasFuncionamento: config.diasFuncionamento.filter(d => d !== dia)
      });
    }
  };

  if (loading && !config.nome) {
    return (
      <div className="flex items-center justify-center h-96">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Carregando configurações...</span>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Settings className="h-8 w-8" />
            Configurações da Loja
          </h1>
          <p className="text-muted-foreground mt-2">
            Gerencie as configurações gerais do sistema
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={exportarConfiguracoes}>
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
          
          <div className="relative">
            <input
              type="file"
              accept=".json"
              onChange={handleImportarConfiguracoes}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <Button variant="outline">
              <Upload className="h-4 w-4 mr-2" />
              Importar
            </Button>
          </div>
          
          <Button onClick={salvarConfiguracoes} disabled={saving}>
            {saving ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Salvar
          </Button>
        </div>
      </div>

      {/* Alertas de Erro */}
      {hasErrors && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {errors.length} erro(s) encontrado(s). Verifique os campos destacados abaixo.
          </AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="geral" className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="geral" className="flex items-center gap-2">
            <Store className="h-4 w-4" />
            Geral
          </TabsTrigger>
          <TabsTrigger value="notificacoes" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Notificações
          </TabsTrigger>
          <TabsTrigger value="aparencia" className="flex items-center gap-2">
            <Palette className="h-4 w-4" />
            Aparência
          </TabsTrigger>
          <TabsTrigger value="seguranca" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Segurança
          </TabsTrigger>
          <TabsTrigger value="integracoes" className="flex items-center gap-2">
            <Globe className="h-4 w-4" />
            Integrações
          </TabsTrigger>
          <TabsTrigger value="backup" className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            Backup
          </TabsTrigger>
        </TabsList>

        {/* Aba Geral */}
        <TabsContent value="geral" className="space-y-6">
          <ConfiguracaoGeral 
            config={config}
            setConfig={setConfig}
            errors={errors}
            getFieldError={getFieldError}
            isFieldValid={isFieldValid}
            diasSemana={diasSemana}
            handleDiaFuncionamentoChange={handleDiaFuncionamentoChange}
          />
        </TabsContent>

        {/* Aba Notificações */}
        <TabsContent value="notificacoes" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Configurações de Notificação</CardTitle>
              <CardDescription>
                Configure como você deseja receber notificações
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Notificações por E-mail</Label>
                    <p className="text-sm text-muted-foreground">
                      Receba notificações importantes por e-mail
                    </p>
                  </div>
                  <Switch
                    checked={config.notificacaoEmail}
                    onCheckedChange={(checked) => setConfig({ ...config, notificacaoEmail: checked })}
                  />
                </div>
                
                <Separator />
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Notificações por SMS</Label>
                    <p className="text-sm text-muted-foreground">
                      Receba notificações urgentes por SMS
                    </p>
                  </div>
                  <Switch
                    checked={config.notificacaoSMS}
                    onCheckedChange={(checked) => setConfig({ ...config, notificacaoSMS: checked })}
                  />
                </div>
                
                <Separator />
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Notificações por WhatsApp</Label>
                    <p className="text-sm text-muted-foreground">
                      Receba notificações e atualizações via WhatsApp
                    </p>
                  </div>
                  <Switch
                    checked={config.notificacaoWhatsApp}
                    onCheckedChange={(checked) => setConfig({ ...config, notificacaoWhatsApp: checked })}
                  />
                </div>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Tipos de Notificação</h4>
                <div className="space-y-1 text-sm text-blue-800">
                  <p>• Novos orçamentos e aprovações</p>
                  <p>• Atualizações de ordem de serviço</p>
                  <p>• Alertas de estoque baixo</p>
                  <p>• Lembretes de agendamento</p>
                  <p>• Relatórios financeiros</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba Aparência */}
        <TabsContent value="aparencia" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Personalização Visual</CardTitle>
              <CardDescription>
                Customize a aparência do sistema
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Tema</Label>
                    <div className="grid grid-cols-3 gap-2">
                      {temas.map((tema) => (
                        <Button
                          key={tema.value}
                          variant={config.tema === tema.value ? "default" : "outline"}
                          onClick={() => setConfig({ ...config, tema: tema.value as any })}
                          className="h-12"
                        >
                          {tema.label}
                        </Button>
                      ))}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="corPrimaria">Cor Primária</Label>
                    <div className="flex gap-2">
                      <Input
                        id="corPrimaria"
                        type="color"
                        value={config.corPrimaria}
                        onChange={(e) => setConfig({ ...config, corPrimaria: e.target.value })}
                        className="w-16 h-10 p-1"
                      />
                      <Input
                        value={config.corPrimaria}
                        onChange={(e) => setConfig({ ...config, corPrimaria: e.target.value })}
                        placeholder="#3b82f6"
                      />
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="corSecundaria">Cor Secundária</Label>
                    <div className="flex gap-2">
                      <Input
                        id="corSecundaria"
                        type="color"
                        value={config.corSecundaria}
                        onChange={(e) => setConfig({ ...config, corSecundaria: e.target.value })}
                        className="w-16 h-10 p-1"
                      />
                      <Input
                        value={config.corSecundaria}
                        onChange={(e) => setConfig({ ...config, corSecundaria: e.target.value })}
                        placeholder="#64748b"
                      />
                    </div>
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Logo da Loja</Label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center relative">
                      {config.logo ? (
                        <div className="space-y-2">
                          <img src={config.logo} alt="Logo" className="mx-auto h-16 object-contain" />
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setConfig({ ...config, logo: '' })}
                          >
                            Remover Logo
                          </Button>
                        </div>
                      ) : (
                        <div className="space-y-2">
                          <Upload className="mx-auto h-8 w-8 text-gray-400" />
                          <p className="text-sm text-gray-500">Clique para fazer upload da logo</p>
                          <p className="text-xs text-gray-400">PNG, JPG, SVG até 2MB</p>
                          <input
                            type="file"
                            accept="image/*"
                            onChange={handleUploadLogo}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                          />
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium mb-2">Preview</h4>
                    <div 
                      className="p-4 rounded border"
                      style={{ 
                        backgroundColor: config.tema === 'dark' ? '#1f2937' : '#ffffff',
                        color: config.tema === 'dark' ? '#ffffff' : '#000000',
                        borderColor: config.corPrimaria
                      }}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <div 
                          className="w-4 h-4 rounded"
                          style={{ backgroundColor: config.corPrimaria }}
                        />
                        <span className="font-medium">{config.nome}</span>
                      </div>
                      <p className="text-sm opacity-75">Exemplo de como ficará a interface</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba Segurança */}
        <TabsContent value="seguranca" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Configurações de Segurança</CardTitle>
              <CardDescription>
                Configure as opções de segurança do sistema
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Autenticação de Dois Fatores (2FA)</Label>
                    <p className="text-sm text-muted-foreground">
                      Adicione uma camada extra de segurança
                    </p>
                  </div>
                  <Switch
                    checked={config.autenticacao2FA}
                    onCheckedChange={(checked) => setConfig({ ...config, autenticacao2FA: checked })}
                  />
                </div>
                
                <Separator />
                
                <div className="space-y-2">
                  <Label htmlFor="sessaoTimeout">Timeout de Sessão (minutos)</Label>
                  <Input
                    id="sessaoTimeout"
                    type="number"
                    value={config.sessaoTimeout}
                    onChange={(e) => setConfig({ ...config, sessaoTimeout: parseInt(e.target.value) })}
                    min="5"
                    max="480"
                  />
                  <p className="text-sm text-muted-foreground">
                    Tempo limite para logout automático por inatividade
                  </p>
                </div>
                
                <Separator />
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Log de Auditoria</Label>
                    <p className="text-sm text-muted-foreground">
                      Registrar todas as ações dos usuários
                    </p>
                  </div>
                  <Switch
                    checked={config.logAuditoria}
                    onCheckedChange={(checked) => setConfig({ ...config, logAuditoria: checked })}
                  />
                </div>
              </div>
              
              <div className="bg-yellow-50 p-4 rounded-lg">
                <h4 className="font-medium text-yellow-900 mb-2">⚠️ Importante</h4>
                <div className="space-y-1 text-sm text-yellow-800">
                  <p>• Mantenha sempre o 2FA ativado para maior segurança</p>
                  <p>• Configure um timeout adequado para seu ambiente</p>
                  <p>• O log de auditoria ajuda a rastrear atividades suspeitas</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Aba Integrações */}
        <TabsContent value="integracoes" className="space-y-6">
          <ConfiguracaoIntegracao 
            integracoes={config.integracoes}
            onSave={(integracoes) => setConfig({ ...config, integracoes })}
          />
        </TabsContent>

        {/* Aba Backup */}
        <TabsContent value="backup" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Configurações de Backup</CardTitle>
              <CardDescription>
                Configure o backup automático dos dados
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Backup Automático</Label>
                    <p className="text-sm text-muted-foreground">
                      Ativar backup automático dos dados
                    </p>
                  </div>
                  <Switch
                    checked={config.backupAutomatico}
                    onCheckedChange={(checked) => setConfig({ ...config, backupAutomatico: checked })}
                  />
                </div>
                
                {config.backupAutomatico && (
                  <>
                    <Separator />
                    
                    <div className="space-y-2">
                      <Label>Frequência do Backup</Label>
                      <div className="grid grid-cols-3 gap-2">
                        {frequenciasBackup.map((freq) => (
                          <Button
                            key={freq.value}
                            variant={config.frequenciaBackup === freq.value ? "default" : "outline"}
                            onClick={() => setConfig({ ...config, frequenciaBackup: freq.value as any })}
                          >
                            {freq.label}
                          </Button>
                        ))}
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="retencaoBackup">Retenção de Backup (dias)</Label>
                      <Input
                        id="retencaoBackup"
                        type="number"
                        value={config.retencaoBackup}
                        onChange={(e) => setConfig({ ...config, retencaoBackup: parseInt(e.target.value) })}
                        min="7"
                        max="365"
                      />
                      <p className="text-sm text-muted-foreground">
                        Por quanto tempo manter os backups armazenados
                      </p>
                    </div>
                  </>
                )}
              </div>
              
              <div className="space-y-4">
                <Separator />
                <h4 className="font-medium">Ações de Backup</h4>
                
                <div className="grid grid-cols-2 gap-4">
                  <Button 
                    variant="outline" 
                    className="h-20 flex-col"
                    onClick={criarBackupManual}
                    disabled={loading}
                  >
                    {loading ? (
                      <RefreshCw className="h-6 w-6 mb-2 animate-spin" />
                    ) : (
                      <Download className="h-6 w-6 mb-2" />
                    )}
                    <span>Backup Manual</span>
                    <span className="text-xs text-muted-foreground">Criar backup agora</span>
                  </Button>
                  
                  <div className="relative">
                    <input
                      type="file"
                      accept=".backup,.sql,.json"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          // Aqui seria implementada a restauração
                          console.log('Restaurar backup:', file.name);
                          e.target.value = '';
                        }
                      }}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <Button variant="outline" className="h-20 flex-col w-full">
                      <Upload className="h-6 w-6 mb-2" />
                      <span>Restaurar Backup</span>
                      <span className="text-xs text-muted-foreground">Restaurar dados</span>
                    </Button>
                  </div>
                </div>
              </div>
              
              <div className={`p-4 rounded-lg ${
                backupInfo.status === 'ativo' ? 'bg-green-50' : 
                backupInfo.status === 'erro' ? 'bg-red-50' : 'bg-gray-50'
              }`}>
                <h4 className={`font-medium mb-2 ${
                  backupInfo.status === 'ativo' ? 'text-green-900' : 
                  backupInfo.status === 'erro' ? 'text-red-900' : 'text-gray-900'
                }`}>
                  {backupInfo.status === 'ativo' ? '✅' : 
                   backupInfo.status === 'erro' ? '❌' : '⏸️'} Status do Backup
                </h4>
                <div className={`space-y-1 text-sm ${
                  backupInfo.status === 'ativo' ? 'text-green-800' : 
                  backupInfo.status === 'erro' ? 'text-red-800' : 'text-gray-800'
                }`}>
                  <p>• Último backup: {backupInfo.ultimoBackup ? 
                    new Intl.DateTimeFormat('pt-BR', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    }).format(backupInfo.ultimoBackup) : 'Nunca'
                  }</p>
                  <p>• Próximo backup: {backupInfo.proximoBackup ? 
                    new Intl.DateTimeFormat('pt-BR', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    }).format(backupInfo.proximoBackup) : 'Não agendado'
                  }</p>
                  <p>• Backups armazenados: {backupInfo.totalBackups} arquivos</p>
                  <p>• Espaço utilizado: {backupInfo.espacoUtilizado}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}