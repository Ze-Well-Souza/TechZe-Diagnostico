import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Smartphone, 
  Mail, 
  CreditCard, 
  Database, 
  Cloud, 
  Zap, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Settings,
  Key,
  Webhook
} from 'lucide-react';

interface ConfiguracaoIntegracaoProps {
  integracoes: any;
  onSave: (integracoes: any) => void;
}

const ConfiguracaoIntegracao: React.FC<ConfiguracaoIntegracaoProps> = ({ integracoes, onSave }) => {
  const [config, setConfig] = React.useState(integracoes);

  const handleSave = () => {
    onSave(config);
  };

  const updateIntegracao = (tipo: string, key: string, value: any) => {
    setConfig((prev: any) => ({
      ...prev,
      [tipo]: {
        ...prev[tipo],
        [key]: value
      }
    }));
  };

  const testarConexao = async (tipo: string) => {
    // Simular teste de conexão
    updateIntegracao(tipo, 'testando', true);
    
    setTimeout(() => {
      updateIntegracao(tipo, 'testando', false);
      updateIntegracao(tipo, 'status', Math.random() > 0.3 ? 'conectado' : 'erro');
      updateIntegracao(tipo, 'ultimoTeste', new Date().toISOString());
    }, 2000);
  };

  const StatusBadge = ({ status }: { status: string }) => {
    const statusConfig = {
      conectado: { icon: CheckCircle, color: 'bg-green-500', text: 'Conectado' },
      erro: { icon: XCircle, color: 'bg-red-500', text: 'Erro' },
      desconectado: { icon: XCircle, color: 'bg-gray-500', text: 'Desconectado' },
      configurando: { icon: Settings, color: 'bg-yellow-500', text: 'Configurando' }
    };

    const { icon: Icon, color, text } = statusConfig[status as keyof typeof statusConfig] || statusConfig.desconectado;

    return (
      <Badge variant="outline" className="flex items-center gap-1">
        <div className={`w-2 h-2 rounded-full ${color}`} />
        <Icon className="h-3 w-3" />
        {text}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <Tabs defaultValue="whatsapp" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="whatsapp">WhatsApp</TabsTrigger>
          <TabsTrigger value="email">E-mail</TabsTrigger>
          <TabsTrigger value="pagamento">Pagamento</TabsTrigger>
          <TabsTrigger value="outros">Outros</TabsTrigger>
        </TabsList>

        {/* WhatsApp Integration */}
        <TabsContent value="whatsapp" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Smartphone className="h-5 w-5" />
                Integração WhatsApp Business
                <StatusBadge status={config.whatsapp?.status || 'desconectado'} />
              </CardTitle>
              <CardDescription>
                Configure a integração com WhatsApp Business API para envio automático de mensagens
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Ativar Integração WhatsApp</Label>
                  <p className="text-sm text-muted-foreground">
                    Habilitar envio de mensagens via WhatsApp
                  </p>
                </div>
                <Switch
                  checked={config.whatsapp?.ativo || false}
                  onCheckedChange={(checked) => updateIntegracao('whatsapp', 'ativo', checked)}
                />
              </div>

              {config.whatsapp?.ativo && (
                <>
                  <Separator />
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="whatsapp-token">Token da API</Label>
                      <Input
                        id="whatsapp-token"
                        type="password"
                        value={config.whatsapp?.token || ''}
                        onChange={(e) => updateIntegracao('whatsapp', 'token', e.target.value)}
                        placeholder="Insira o token da WhatsApp Business API"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="whatsapp-numero">Número do WhatsApp</Label>
                      <Input
                        id="whatsapp-numero"
                        value={config.whatsapp?.numero || ''}
                        onChange={(e) => updateIntegracao('whatsapp', 'numero', e.target.value)}
                        placeholder="(11) 99999-9999"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="whatsapp-webhook">Webhook URL</Label>
                    <Input
                      id="whatsapp-webhook"
                      value={config.whatsapp?.webhook || ''}
                      onChange={(e) => updateIntegracao('whatsapp', 'webhook', e.target.value)}
                      placeholder="https://sua-api.com/webhook/whatsapp"
                    />
                  </div>

                  <Alert>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertDescription>
                      Para usar a integração WhatsApp, você precisa ter uma conta WhatsApp Business verificada e acesso à API oficial.
                    </AlertDescription>
                  </Alert>

                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      onClick={() => testarConexao('whatsapp')}
                      disabled={config.whatsapp?.testando}
                    >
                      {config.whatsapp?.testando ? 'Testando...' : 'Testar Conexão'}
                    </Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Email Integration */}
        <TabsContent value="email" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Configuração de E-mail
                <StatusBadge status={config.email?.status || 'desconectado'} />
              </CardTitle>
              <CardDescription>
                Configure o servidor SMTP para envio de e-mails automáticos
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Ativar Envio de E-mail</Label>
                  <p className="text-sm text-muted-foreground">
                    Habilitar envio automático de e-mails
                  </p>
                </div>
                <Switch
                  checked={config.email?.ativo || false}
                  onCheckedChange={(checked) => updateIntegracao('email', 'ativo', checked)}
                />
              </div>

              {config.email?.ativo && (
                <>
                  <Separator />
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="smtp-host">Servidor SMTP</Label>
                      <Input
                        id="smtp-host"
                        value={config.email?.smtpHost || ''}
                        onChange={(e) => updateIntegracao('email', 'smtpHost', e.target.value)}
                        placeholder="smtp.gmail.com"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="smtp-port">Porta</Label>
                      <Input
                        id="smtp-port"
                        type="number"
                        value={config.email?.smtpPort || 587}
                        onChange={(e) => updateIntegracao('email', 'smtpPort', parseInt(e.target.value))}
                        placeholder="587"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="smtp-user">Usuário</Label>
                      <Input
                        id="smtp-user"
                        type="email"
                        value={config.email?.smtpUser || ''}
                        onChange={(e) => updateIntegracao('email', 'smtpUser', e.target.value)}
                        placeholder="seu-email@gmail.com"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="smtp-password">Senha</Label>
                      <Input
                        id="smtp-password"
                        type="password"
                        value={config.email?.smtpPassword || ''}
                        onChange={(e) => updateIntegracao('email', 'smtpPassword', e.target.value)}
                        placeholder="Senha ou App Password"
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="email-remetente">E-mail Remetente</Label>
                    <Input
                      id="email-remetente"
                      type="email"
                      value={config.email?.remetente || ''}
                      onChange={(e) => updateIntegracao('email', 'remetente', e.target.value)}
                      placeholder="noreply@techze.com.br"
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Usar SSL/TLS</Label>
                      <p className="text-sm text-muted-foreground">
                        Conexão segura com o servidor SMTP
                      </p>
                    </div>
                    <Switch
                      checked={config.email?.ssl || true}
                      onCheckedChange={(checked) => updateIntegracao('email', 'ssl', checked)}
                    />
                  </div>

                  <div className="flex gap-2">
                    <Button 
                      variant="outline" 
                      onClick={() => testarConexao('email')}
                      disabled={config.email?.testando}
                    >
                      {config.email?.testando ? 'Testando...' : 'Testar Conexão'}
                    </Button>
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Payment Integration */}
        <TabsContent value="pagamento" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CreditCard className="h-5 w-5" />
                Gateways de Pagamento
              </CardTitle>
              <CardDescription>
                Configure os métodos de pagamento aceitos
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Mercado Pago */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base font-medium">Mercado Pago</Label>
                    <p className="text-sm text-muted-foreground">
                      Aceitar pagamentos via Mercado Pago
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={config.mercadoPago?.status || 'desconectado'} />
                    <Switch
                      checked={config.mercadoPago?.ativo || false}
                      onCheckedChange={(checked) => updateIntegracao('mercadoPago', 'ativo', checked)}
                    />
                  </div>
                </div>

                {config.mercadoPago?.ativo && (
                  <div className="ml-4 space-y-3 border-l-2 border-muted pl-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="mp-public-key">Public Key</Label>
                        <Input
                          id="mp-public-key"
                          value={config.mercadoPago?.publicKey || ''}
                          onChange={(e) => updateIntegracao('mercadoPago', 'publicKey', e.target.value)}
                          placeholder="APP_USR-xxxxxxxx"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="mp-access-token">Access Token</Label>
                        <Input
                          id="mp-access-token"
                          type="password"
                          value={config.mercadoPago?.accessToken || ''}
                          onChange={(e) => updateIntegracao('mercadoPago', 'accessToken', e.target.value)}
                          placeholder="APP_USR-xxxxxxxx"
                        />
                      </div>
                    </div>
                  </div>
                )}
              </div>

              <Separator />

              {/* PIX */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base font-medium">PIX</Label>
                    <p className="text-sm text-muted-foreground">
                      Aceitar pagamentos via PIX
                    </p>
                  </div>
                  <Switch
                    checked={config.pix?.ativo || false}
                    onCheckedChange={(checked) => updateIntegracao('pix', 'ativo', checked)}
                  />
                </div>

                {config.pix?.ativo && (
                  <div className="ml-4 space-y-3 border-l-2 border-muted pl-4">
                    <div className="space-y-2">
                      <Label htmlFor="pix-chave">Chave PIX</Label>
                      <Input
                        id="pix-chave"
                        value={config.pix?.chave || ''}
                        onChange={(e) => updateIntegracao('pix', 'chave', e.target.value)}
                        placeholder="email@exemplo.com ou CPF/CNPJ"
                      />
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Other Integrations */}
        <TabsContent value="outros" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Outras Integrações
              </CardTitle>
              <CardDescription>
                Configure integrações adicionais e webhooks
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Google Sheets */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base font-medium flex items-center gap-2">
                      <Database className="h-4 w-4" />
                      Google Sheets
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Sincronizar dados com planilhas do Google
                    </p>
                  </div>
                  <Switch
                    checked={config.googleSheets?.ativo || false}
                    onCheckedChange={(checked) => updateIntegracao('googleSheets', 'ativo', checked)}
                  />
                </div>

                {config.googleSheets?.ativo && (
                  <div className="ml-4 space-y-3 border-l-2 border-muted pl-4">
                    <div className="space-y-2">
                      <Label htmlFor="sheets-id">ID da Planilha</Label>
                      <Input
                        id="sheets-id"
                        value={config.googleSheets?.planilhaId || ''}
                        onChange={(e) => updateIntegracao('googleSheets', 'planilhaId', e.target.value)}
                        placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
                      />
                    </div>
                  </div>
                )}
              </div>

              <Separator />

              {/* Webhooks */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label className="text-base font-medium flex items-center gap-2">
                      <Webhook className="h-4 w-4" />
                      Webhooks Personalizados
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      Configurar webhooks para integrações customizadas
                    </p>
                  </div>
                  <Switch
                    checked={config.webhooks?.ativo || false}
                    onCheckedChange={(checked) => updateIntegracao('webhooks', 'ativo', checked)}
                  />
                </div>

                {config.webhooks?.ativo && (
                  <div className="ml-4 space-y-3 border-l-2 border-muted pl-4">
                    <div className="space-y-2">
                      <Label htmlFor="webhook-url">URL do Webhook</Label>
                      <Input
                        id="webhook-url"
                        value={config.webhooks?.url || ''}
                        onChange={(e) => updateIntegracao('webhooks', 'url', e.target.value)}
                        placeholder="https://sua-api.com/webhook"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="webhook-secret">Secret Key</Label>
                      <Input
                        id="webhook-secret"
                        type="password"
                        value={config.webhooks?.secret || ''}
                        onChange={(e) => updateIntegracao('webhooks', 'secret', e.target.value)}
                        placeholder="Chave secreta para validação"
                      />
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Botões de Ação */}
      <div className="flex justify-end gap-2">
        <Button variant="outline" onClick={() => setConfig(integracoes)}>
          Cancelar
        </Button>
        <Button onClick={handleSave}>
          Salvar Integrações
        </Button>
      </div>
    </div>
  );
};

export { ConfiguracaoIntegracao };