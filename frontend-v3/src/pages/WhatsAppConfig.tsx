import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  MessageCircle, 
  Phone, 
  Settings, 
  CheckCircle, 
  AlertCircle,
  Send,
  QrCode,
  Smartphone,
  Building2,
  Plus,
  Edit,
  Trash2,
  Save
} from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useCompany } from '@/contexts/CompanyContext';

interface WhatsAppAccount {
  id: string;
  name: string;
  phone: string;
  type: 'business' | 'personal';
  status: 'connected' | 'disconnected' | 'pending';
  qrCode?: string;
  accessToken?: string;
}

export default function WhatsAppConfig() {
  const { selectedCompany } = useCompany();
  const { toast } = useToast();
  const [accounts, setAccounts] = useState<WhatsAppAccount[]>([
    {
      id: '1',
      name: 'UlyTech Business',
      phone: '+5511999999999',
      type: 'business',
      status: 'connected',
      accessToken: 'EAAxxxxxxxxxxxxxxx'
    },
    {
      id: '2',
      name: 'WhatsApp Pessoal',
      phone: '+5511888888888',
      type: 'personal',
      status: 'disconnected'
    }
  ]);

  const [newAccount, setNewAccount] = useState({
    name: '',
    phone: '',
    type: 'business' as 'business' | 'personal'
  });

  const [autoReply, setAutoReply] = useState({
    enabled: true,
    message: 'Olá! Obrigado pelo contato. Nossa equipe retornará em breve.'
  });

  const [templates, setTemplates] = useState([
    {
      id: '1',
      name: 'Orçamento Aprovado',
      message: 'Olá {{cliente}}! Seu orçamento foi aprovado. Valor: R$ {{valor}}. Prazo: {{prazo}} dias úteis.'
    },
    {
      id: '2',
      name: 'Equipamento Pronto',
      message: 'Oi {{cliente}}! Seu {{equipamento}} está pronto para retirada. Horário: 8h às 18h.'
    },
    {
      id: '3',
      name: 'Lembrete de Pagamento',
      message: 'Olá {{cliente}}! Lembramos que o vencimento do seu orçamento é {{data}}.'
    }
  ]);

  const [newTemplate, setNewTemplate] = useState({
    name: '',
    message: ''
  });

  const handleConnectAccount = (accountId: string) => {
    setAccounts(prev => prev.map(acc => 
      acc.id === accountId 
        ? { ...acc, status: 'pending', qrCode: 'mock-qr-code-data' }
        : acc
    ));

    // Simular conexão
    setTimeout(() => {
      setAccounts(prev => prev.map(acc => 
        acc.id === accountId 
          ? { ...acc, status: 'connected', qrCode: undefined }
          : acc
      ));
      
      toast({
        title: "WhatsApp conectado",
        description: "Conta conectada com sucesso!",
      });
    }, 3000);
  };

  const handleDisconnectAccount = (accountId: string) => {
    setAccounts(prev => prev.map(acc => 
      acc.id === accountId 
        ? { ...acc, status: 'disconnected', qrCode: undefined, accessToken: undefined }
        : acc
    ));
    
    toast({
      title: "WhatsApp desconectado",
      description: "Conta desconectada com sucesso.",
    });
  };

  const handleAddAccount = () => {
    if (!newAccount.name || !newAccount.phone) {
      toast({
        title: "Erro",
        description: "Por favor, preencha todos os campos.",
        variant: "destructive",
      });
      return;
    }

    const account: WhatsAppAccount = {
      id: Date.now().toString(),
      ...newAccount,
      status: 'disconnected'
    };

    setAccounts(prev => [...prev, account]);
    setNewAccount({ name: '', phone: '', type: 'business' });
    
    toast({
      title: "Conta adicionada",
      description: "Nova conta WhatsApp foi adicionada.",
    });
  };

  const handleSaveAutoReply = () => {
    toast({
      title: "Configurações salvas",
      description: "Resposta automática atualizada com sucesso.",
    });
  };

  const handleAddTemplate = () => {
    if (!newTemplate.name || !newTemplate.message) {
      toast({
        title: "Erro",
        description: "Por favor, preencha todos os campos.",
        variant: "destructive",
      });
      return;
    }

    const template = {
      id: Date.now().toString(),
      ...newTemplate
    };

    setTemplates(prev => [...prev, template]);
    setNewTemplate({ name: '', message: '' });
    
    toast({
      title: "Template adicionado",
      description: "Novo template foi criado com sucesso.",
    });
  };

  const getStatusIcon = (status: WhatsAppAccount['status']) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case 'pending':
        return <AlertCircle className="h-4 w-4 text-yellow-400" />;
      default:
        return <AlertCircle className="h-4 w-4 text-red-400" />;
    }
  };

  const getStatusColor = (status: WhatsAppAccount['status']) => {
    switch (status) {
      case 'connected': return 'bg-green-500';
      case 'pending': return 'bg-yellow-500';
      default: return 'bg-red-500';
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-8 pt-24">
      <div className="container mx-auto max-w-4xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold gradient-text mb-2">
            Configurações WhatsApp
          </h1>
          <p className="text-gray-400">
            Configure suas contas do WhatsApp Business e Pessoal
          </p>
        </div>

        <Tabs defaultValue="accounts" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-darker">
            <TabsTrigger value="accounts" className="data-[state=active]:bg-electric data-[state=active]:text-black">
              Contas
            </TabsTrigger>
            <TabsTrigger value="templates" className="data-[state=active]:bg-electric data-[state=active]:text-black">
              Templates
            </TabsTrigger>
            <TabsTrigger value="auto-reply" className="data-[state=active]:bg-electric data-[state=active]:text-black">
              Resposta Automática
            </TabsTrigger>
            <TabsTrigger value="settings" className="data-[state=active]:bg-electric data-[state=active]:text-black">
              Configurações
            </TabsTrigger>
          </TabsList>

          <TabsContent value="accounts">
            <div className="space-y-6">
              {/* Add New Account */}
              <Card className="glass-effect border-white/10">
                <CardHeader>
                  <CardTitle className="text-white flex items-center">
                    <Plus className="mr-2 h-5 w-5 text-electric" />
                    Adicionar Conta WhatsApp
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid md:grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="name" className="text-white">Nome da Conta</Label>
                      <Input
                        id="name"
                        value={newAccount.name}
                        onChange={(e) => setNewAccount({ ...newAccount, name: e.target.value })}
                        placeholder="Ex: WhatsApp Business"
                        className="bg-darker border-white/20 text-white"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="phone" className="text-white">Telefone</Label>
                      <Input
                        id="phone"
                        value={newAccount.phone}
                        onChange={(e) => setNewAccount({ ...newAccount, phone: e.target.value })}
                        placeholder="+55 11 99999-9999"
                        className="bg-darker border-white/20 text-white"
                      />
                    </div>
                    
                    <div>
                      <Label className="text-white">Tipo</Label>
                      <div className="flex space-x-4 mt-2">
                        <label className="flex items-center space-x-2">
                          <input
                            type="radio"
                            value="business"
                            checked={newAccount.type === 'business'}
                            onChange={(e) => setNewAccount({ ...newAccount, type: e.target.value as 'business' | 'personal' })}
                            className="text-electric"
                          />
                          <span className="text-white">Business</span>
                        </label>
                        <label className="flex items-center space-x-2">
                          <input
                            type="radio"
                            value="personal"
                            checked={newAccount.type === 'personal'}
                            onChange={(e) => setNewAccount({ ...newAccount, type: e.target.value as 'business' | 'personal' })}
                            className="text-electric"
                          />
                          <span className="text-white">Pessoal</span>
                        </label>
                      </div>
                    </div>
                  </div>
                  
                  <Button
                    onClick={handleAddAccount}
                    className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80"
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    Adicionar Conta
                  </Button>
                </CardContent>
              </Card>

              {/* Existing Accounts */}
              <div className="space-y-4">
                {accounts.map((account) => (
                  <Card key={account.id} className="glass-effect border-white/10">
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-green-600 rounded-full flex items-center justify-center">
                            {account.type === 'business' ? (
                              <Building2 className="h-6 w-6 text-white" />
                            ) : (
                              <Smartphone className="h-6 w-6 text-white" />
                            )}
                          </div>
                          
                          <div>
                            <h3 className="text-white font-semibold">{account.name}</h3>
                            <p className="text-gray-400">{account.phone}</p>
                            <div className="flex items-center space-x-2 mt-1">
                              <Badge variant={account.type === 'business' ? 'default' : 'secondary'}>
                                {account.type === 'business' ? 'Business' : 'Pessoal'}
                              </Badge>
                              <Badge className={getStatusColor(account.status)}>
                                {getStatusIcon(account.status)}
                                <span className="ml-1 capitalize">{account.status}</span>
                              </Badge>
                            </div>
                          </div>
                        </div>
                        
                        <div className="flex space-x-2">
                          {account.status === 'disconnected' && (
                            <Button
                              onClick={() => handleConnectAccount(account.id)}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              <MessageCircle className="mr-2 h-4 w-4" />
                              Conectar
                            </Button>
                          )}
                          
                          {account.status === 'connected' && (
                            <Button
                              onClick={() => handleDisconnectAccount(account.id)}
                              variant="outline"
                              className="border-red-500/20 text-red-400 hover:bg-red-500/10"
                            >
                              Desconectar
                            </Button>
                          )}
                          
                          {account.status === 'pending' && (
                            <div className="text-center">
                              <div className="w-32 h-32 bg-white rounded-lg flex items-center justify-center mb-2">
                                <QrCode className="h-16 w-16 text-black" />
                              </div>
                              <p className="text-xs text-gray-400">Escaneie o QR Code</p>
                            </div>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="templates">
            <div className="space-y-6">
              {/* Add Template */}
              <Card className="glass-effect border-white/10">
                <CardHeader>
                  <CardTitle className="text-white">Criar Template</CardTitle>
                  <CardDescription className="text-gray-400">
                    Crie templates de mensagens para facilitar o envio
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="templateName" className="text-white">Nome do Template</Label>
                    <Input
                      id="templateName"
                      value={newTemplate.name}
                      onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                      placeholder="Ex: Orçamento Aprovado"
                      className="bg-darker border-white/20 text-white"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="templateMessage" className="text-white">Mensagem</Label>
                    <Textarea
                      id="templateMessage"
                      value={newTemplate.message}
                      onChange={(e) => setNewTemplate({ ...newTemplate, message: e.target.value })}
                      placeholder="Use {{variavel}} para campos dinâmicos"
                      className="bg-darker border-white/20 text-white h-24"
                    />
                    <p className="text-xs text-gray-400 mt-1">
                      Variáveis disponíveis: {{cliente}}, {{valor}}, {{prazo}}, {{equipamento}}, {{data}}
                    </p>
                  </div>
                  
                  <Button
                    onClick={handleAddTemplate}
                    className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80"
                  >
                    <Plus className="mr-2 h-4 w-4" />
                    Criar Template
                  </Button>
                </CardContent>
              </Card>

              {/* Templates List */}
              <div className="space-y-4">
                {templates.map((template) => (
                  <Card key={template.id} className="glass-effect border-white/10">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="text-white font-semibold mb-2">{template.name}</h3>
                          <p className="text-gray-400 text-sm">{template.message}</p>
                        </div>
                        
                        <div className="flex space-x-2">
                          <Button size="sm" variant="outline" className="border-white/20 text-white hover:bg-white/10">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button size="sm" variant="outline" className="border-red-500/20 text-red-400 hover:bg-red-500/10">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="auto-reply">
            <Card className="glass-effect border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Resposta Automática</CardTitle>
                <CardDescription className="text-gray-400">
                  Configure mensagens automáticas para novos contatos
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={autoReply.enabled}
                    onCheckedChange={(checked) => setAutoReply({ ...autoReply, enabled: checked })}
                  />
                  <Label className="text-white">Ativar resposta automática</Label>
                </div>
                
                {autoReply.enabled && (
                  <div>
                    <Label htmlFor="autoMessage" className="text-white">Mensagem Automática</Label>
                    <Textarea
                      id="autoMessage"
                      value={autoReply.message}
                      onChange={(e) => setAutoReply({ ...autoReply, message: e.target.value })}
                      className="bg-darker border-white/20 text-white h-24"
                    />
                  </div>
                )}
                
                <Button
                  onClick={handleSaveAutoReply}
                  className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80"
                >
                  <Save className="mr-2 h-4 w-4" />
                  Salvar Configurações
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="settings">
            <Card className="glass-effect border-white/10">
              <CardHeader>
                <CardTitle className="text-white">Configurações Avançadas</CardTitle>
                <CardDescription className="text-gray-400">
                  Configurações adicionais do WhatsApp
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-white">Logs de mensagens</Label>
                      <p className="text-gray-400 text-sm">Manter registro de todas as mensagens enviadas</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-white">Confirmação de leitura</Label>
                      <p className="text-gray-400 text-sm">Solicitar confirmação quando mensagens forem lidas</p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-white">Limite de mensagens por hora</Label>
                      <p className="text-gray-400 text-sm">Definir limite para evitar spam</p>
                    </div>
                    <Input
                      type="number"
                      defaultValue={100}
                      className="w-20 bg-darker border-white/20 text-white"
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
