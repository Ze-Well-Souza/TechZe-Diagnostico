import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Building2, Clock, Globe, Palette, Bell, Shield } from 'lucide-react';

interface ConfiguracaoGeralProps {
  configuracoes: any;
  onSave: (config: any) => void;
}

const ConfiguracaoGeral: React.FC<ConfiguracaoGeralProps> = ({ configuracoes, onSave }) => {
  const [config, setConfig] = React.useState(configuracoes);

  const handleSave = () => {
    onSave(config);
  };

  const updateConfig = (key: string, value: any) => {
    setConfig((prev: any) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="space-y-6">
      {/* Informações da Loja */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Building2 className="h-5 w-5" />
            Informações da Loja
          </CardTitle>
          <CardDescription>
            Configure as informações básicas da sua loja
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="nome-loja">Nome da Loja</Label>
              <Input
                id="nome-loja"
                value={config.nomeLoja || ''}
                onChange={(e) => updateConfig('nomeLoja', e.target.value)}
                placeholder="TechZe Diagnóstico"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="cnpj">CNPJ</Label>
              <Input
                id="cnpj"
                value={config.cnpj || ''}
                onChange={(e) => updateConfig('cnpj', e.target.value)}
                placeholder="00.000.000/0000-00"
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="endereco">Endereço Completo</Label>
            <Textarea
              id="endereco"
              value={config.endereco || ''}
              onChange={(e) => updateConfig('endereco', e.target.value)}
              placeholder="Rua, número, bairro, cidade, CEP"
              rows={3}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="telefone">Telefone</Label>
              <Input
                id="telefone"
                value={config.telefone || ''}
                onChange={(e) => updateConfig('telefone', e.target.value)}
                placeholder="(11) 99999-9999"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">E-mail</Label>
              <Input
                id="email"
                type="email"
                value={config.email || ''}
                onChange={(e) => updateConfig('email', e.target.value)}
                placeholder="contato@techze.com.br"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Configurações de Funcionamento */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Horário de Funcionamento
          </CardTitle>
          <CardDescription>
            Configure os horários de atendimento da loja
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="horario-abertura">Horário de Abertura</Label>
              <Input
                id="horario-abertura"
                type="time"
                value={config.horarioAbertura || '08:00'}
                onChange={(e) => updateConfig('horarioAbertura', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="horario-fechamento">Horário de Fechamento</Label>
              <Input
                id="horario-fechamento"
                type="time"
                value={config.horarioFechamento || '18:00'}
                onChange={(e) => updateConfig('horarioFechamento', e.target.value)}
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label>Dias de Funcionamento</Label>
            <div className="flex flex-wrap gap-2">
              {['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'].map((dia, index) => {
                const isActive = config.diasFuncionamento?.includes(index) || false;
                return (
                  <Badge
                    key={dia}
                    variant={isActive ? 'default' : 'outline'}
                    className="cursor-pointer"
                    onClick={() => {
                      const dias = config.diasFuncionamento || [];
                      const newDias = isActive 
                        ? dias.filter((d: number) => d !== index)
                        : [...dias, index];
                      updateConfig('diasFuncionamento', newDias);
                    }}
                  >
                    {dia}
                  </Badge>
                );
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Configurações do Sistema */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Globe className="h-5 w-5" />
            Configurações do Sistema
          </CardTitle>
          <CardDescription>
            Configure preferências gerais do sistema
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="idioma">Idioma</Label>
              <Select
                value={config.idioma || 'pt-BR'}
                onValueChange={(value) => updateConfig('idioma', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o idioma" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="pt-BR">Português (Brasil)</SelectItem>
                  <SelectItem value="en-US">English (US)</SelectItem>
                  <SelectItem value="es-ES">Español</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="timezone">Fuso Horário</Label>
              <Select
                value={config.timezone || 'America/Sao_Paulo'}
                onValueChange={(value) => updateConfig('timezone', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o fuso horário" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="America/Sao_Paulo">Brasília (GMT-3)</SelectItem>
                  <SelectItem value="America/New_York">New York (GMT-5)</SelectItem>
                  <SelectItem value="Europe/London">London (GMT+0)</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="moeda">Moeda</Label>
              <Select
                value={config.moeda || 'BRL'}
                onValueChange={(value) => updateConfig('moeda', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione a moeda" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="BRL">Real (R$)</SelectItem>
                  <SelectItem value="USD">Dólar ($)</SelectItem>
                  <SelectItem value="EUR">Euro (€)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="formato-data">Formato de Data</Label>
              <Select
                value={config.formatoData || 'DD/MM/YYYY'}
                onValueChange={(value) => updateConfig('formatoData', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o formato" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="DD/MM/YYYY">DD/MM/YYYY</SelectItem>
                  <SelectItem value="MM/DD/YYYY">MM/DD/YYYY</SelectItem>
                  <SelectItem value="YYYY-MM-DD">YYYY-MM-DD</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Configurações de Aparência */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Palette className="h-5 w-5" />
            Aparência
          </CardTitle>
          <CardDescription>
            Personalize a aparência do sistema
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="tema">Tema</Label>
              <Select
                value={config.tema || 'light'}
                onValueChange={(value) => updateConfig('tema', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o tema" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">Claro</SelectItem>
                  <SelectItem value="dark">Escuro</SelectItem>
                  <SelectItem value="system">Sistema</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="cor-primaria">Cor Primária</Label>
              <div className="flex gap-2">
                <Input
                  id="cor-primaria"
                  type="color"
                  value={config.corPrimaria || '#3b82f6'}
                  onChange={(e) => updateConfig('corPrimaria', e.target.value)}
                  className="w-16 h-10"
                />
                <Input
                  value={config.corPrimaria || '#3b82f6'}
                  onChange={(e) => updateConfig('corPrimaria', e.target.value)}
                  placeholder="#3b82f6"
                  className="flex-1"
                />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Configurações de Notificações */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Notificações
          </CardTitle>
          <CardDescription>
            Configure as preferências de notificações
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Notificações por E-mail</Label>
                <p className="text-sm text-muted-foreground">
                  Receber notificações importantes por e-mail
                </p>
              </div>
              <Switch
                checked={config.notificacoesEmail || false}
                onCheckedChange={(checked) => updateConfig('notificacoesEmail', checked)}
              />
            </div>
            
            <Separator />
            
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Notificações Push</Label>
                <p className="text-sm text-muted-foreground">
                  Receber notificações push no navegador
                </p>
              </div>
              <Switch
                checked={config.notificacoesPush || false}
                onCheckedChange={(checked) => updateConfig('notificacoesPush', checked)}
              />
            </div>
            
            <Separator />
            
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Notificações de WhatsApp</Label>
                <p className="text-sm text-muted-foreground">
                  Enviar atualizações para clientes via WhatsApp
                </p>
              </div>
              <Switch
                checked={config.notificacoesWhatsApp || false}
                onCheckedChange={(checked) => updateConfig('notificacoesWhatsApp', checked)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Configurações de Segurança */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Segurança
          </CardTitle>
          <CardDescription>
            Configure as opções de segurança do sistema
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Autenticação de Dois Fatores</Label>
                <p className="text-sm text-muted-foreground">
                  Adicionar uma camada extra de segurança
                </p>
              </div>
              <Switch
                checked={config.autenticacao2FA || false}
                onCheckedChange={(checked) => updateConfig('autenticacao2FA', checked)}
              />
            </div>
            
            <Separator />
            
            <div className="space-y-2">
              <Label htmlFor="tempo-sessao">Tempo de Sessão (minutos)</Label>
              <Input
                id="tempo-sessao"
                type="number"
                value={config.tempoSessao || 60}
                onChange={(e) => updateConfig('tempoSessao', parseInt(e.target.value))}
                min={15}
                max={480}
              />
            </div>
            
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Backup Automático</Label>
                <p className="text-sm text-muted-foreground">
                  Realizar backup automático dos dados
                </p>
              </div>
              <Switch
                checked={config.backupAutomatico || false}
                onCheckedChange={(checked) => updateConfig('backupAutomatico', checked)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Botões de Ação */}
      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={() => setConfig(configuracoes)}>
          Cancelar
        </Button>
        <Button onClick={handleSave}>
          Salvar Configurações
        </Button>
      </div>
    </div>
  );
};

export { ConfiguracaoGeral };