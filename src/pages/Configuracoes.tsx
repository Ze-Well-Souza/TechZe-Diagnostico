import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useNotifications } from '@/hooks/useNotifications';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Settings,
  Store,
  Users,
  Bell,
  Palette,
  Shield,
  Database,
  Mail,
  Phone,
  MapPin,
  Clock,
  DollarSign,
  Printer,
  Wifi,
  Save,
  RefreshCw,
  Upload,
  Download,
} from 'lucide-react';

interface LojaConfig {
  nome: string;
  cnpj: string;
  endereco: string;
  telefone: string;
  email: string;
  horarioFuncionamento: {
    abertura: string;
    fechamento: string;
    diasSemana: string[];
  };
  configuracoesTecnicas: {
    tempoGarantia: number;
    margemLucro: number;
    alertaEstoqueBaixo: number;
    backupAutomatico: boolean;
    notificacoesPush: boolean;
  };
  personalizacao: {
    tema: 'light' | 'dark' | 'auto';
    corPrimaria: string;
    logo: string;
    favicon: string;
  };
  integracao: {
    whatsapp: {
      ativo: boolean;
      numero: string;
      token: string;
    };
    email: {
      ativo: boolean;
      servidor: string;
      porta: number;
      usuario: string;
      senha: string;
    };
    impressora: {
      ativo: boolean;
      modelo: string;
      ip: string;
    };
  };
}

const DIAS_SEMANA = [
  { value: 'segunda', label: 'Segunda-feira' },
  { value: 'terca', label: 'Terça-feira' },
  { value: 'quarta', label: 'Quarta-feira' },
  { value: 'quinta', label: 'Quinta-feira' },
  { value: 'sexta', label: 'Sexta-feira' },
  { value: 'sabado', label: 'Sábado' },
  { value: 'domingo', label: 'Domingo' },
];

const TEMAS = [
  { value: 'light', label: 'Claro' },
  { value: 'dark', label: 'Escuro' },
  { value: 'auto', label: 'Automático' },
];

const CORES_PRIMARIAS = [
  { value: '#3b82f6', label: 'Azul', color: '#3b82f6' },
  { value: '#10b981', label: 'Verde', color: '#10b981' },
  { value: '#f59e0b', label: 'Amarelo', color: '#f59e0b' },
  { value: '#ef4444', label: 'Vermelho', color: '#ef4444' },
  { value: '#8b5cf6', label: 'Roxo', color: '#8b5cf6' },
  { value: '#06b6d4', label: 'Ciano', color: '#06b6d4' },
];

export default function Configuracoes() {
  const { user, company } = useAuth();
  const { addNotification } = useNotifications();
  const [activeTab, setActiveTab] = useState('geral');
  const [isLoading, setIsLoading] = useState(false);
  const [config, setConfig] = useState<LojaConfig>({
    nome: company?.name || '',
    cnpj: company?.cnpj || '',
    endereco: company?.address || '',
    telefone: company?.phone || '',
    email: company?.email || '',
    horarioFuncionamento: {
      abertura: '08:00',
      fechamento: '18:00',
      diasSemana: ['segunda', 'terca', 'quarta', 'quinta', 'sexta'],
    },
    configuracoesTecnicas: {
      tempoGarantia: 90,
      margemLucro: 30,
      alertaEstoqueBaixo: 5,
      backupAutomatico: true,
      notificacoesPush: true,
    },
    personalizacao: {
      tema: 'light',
      corPrimaria: '#3b82f6',
      logo: '',
      favicon: '',
    },
    integracao: {
      whatsapp: {
        ativo: false,
        numero: '',
        token: '',
      },
      email: {
        ativo: false,
        servidor: '',
        porta: 587,
        usuario: '',
        senha: '',
      },
      impressora: {
        ativo: false,
        modelo: '',
        ip: '',
      },
    },
  });

  const handleSave = async () => {
    setIsLoading(true);
    try {
      // Simular salvamento das configurações
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      addNotification({
        type: 'success',
        title: 'Configurações salvas',
        message: 'As configurações da loja foram atualizadas com sucesso.',
      });
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Erro ao salvar',
        message: 'Não foi possível salvar as configurações. Tente novamente.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    // Reset para configurações padrão
    setConfig({
      ...config,
      configuracoesTecnicas: {
        tempoGarantia: 90,
        margemLucro: 30,
        alertaEstoqueBaixo: 5,
        backupAutomatico: true,
        notificacoesPush: true,
      },
    });
    
    addNotification({
      type: 'info',
      title: 'Configurações resetadas',
      message: 'As configurações foram restauradas para os valores padrão.',
    });
  };

  const handleFileUpload = (type: 'logo' | 'favicon') => {
    // Implementar upload de arquivo
    addNotification({
      type: 'info',
      title: 'Upload iniciado',
      message: `O ${type} será processado em breve.`,
    });
  };

  const testIntegration = (type: 'whatsapp' | 'email' | 'impressora') => {
    addNotification({
      type: 'info',
      title: 'Testando integração',
      message: `Verificando conexão com ${type}...`,
    });
    
    // Simular teste de integração
    setTimeout(() => {
      addNotification({
        type: 'success',
        title: 'Teste concluído',
        message: `Integração com ${type} funcionando corretamente.`,
      });
    }, 2000);
  };

  return (
    <MainLayout>
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Configurações</h1>
            <p className="text-muted-foreground">
              Gerencie as configurações da sua loja e personalize o sistema
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleReset}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Resetar
            </Button>
            <Button onClick={handleSave} disabled={isLoading}>
              <Save className="h-4 w-4 mr-2" />
              {isLoading ? 'Salvando...' : 'Salvar'}
            </Button>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="geral" className="flex items-center gap-2">
              <Store className="h-4 w-4" />
              Geral
            </TabsTrigger>
            <TabsTrigger value="tecnicas" className="flex items-center gap-2">
              <Settings className="h-4 w-4" />
              Técnicas
            </TabsTrigger>
            <TabsTrigger value="personalizacao" className="flex items-center gap-2">
              <Palette className="h-4 w-4" />
              Visual
            </TabsTrigger>
            <TabsTrigger value="integracoes" className="flex items-center gap-2">
              <Wifi className="h-4 w-4" />
              Integrações
            </TabsTrigger>
            <TabsTrigger value="seguranca" className="flex items-center gap-2">
              <Shield className="h-4 w-4" />
              Segurança
            </TabsTrigger>
          </TabsList>

          {/* Aba Geral */}
          <TabsContent value="geral" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Store className="h-5 w-5" />
                  Informações da Loja
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="nome">Nome da Loja</Label>
                    <Input
                      id="nome"
                      value={config.nome}
                      onChange={(e) => setConfig({ ...config, nome: e.target.value })}
                      placeholder="Digite o nome da loja"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="cnpj">CNPJ</Label>
                    <Input
                      id="cnpj"
                      value={config.cnpj}
                      onChange={(e) => setConfig({ ...config, cnpj: e.target.value })}
                      placeholder="00.000.000/0000-00"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="telefone">Telefone</Label>
                    <Input
                      id="telefone"
                      value={config.telefone}
                      onChange={(e) => setConfig({ ...config, telefone: e.target.value })}
                      placeholder="(11) 99999-9999"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">E-mail</Label>
                    <Input
                      id="email"
                      type="email"
                      value={config.email}
                      onChange={(e) => setConfig({ ...config, email: e.target.value })}
                      placeholder="contato@loja.com"
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="endereco">Endereço Completo</Label>
                  <Input
                    id="endereco"
                    value={config.endereco}
                    onChange={(e) => setConfig({ ...config, endereco: e.target.value })}
                    placeholder="Rua, número, bairro, cidade - UF"
                  />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Horário de Funcionamento
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="abertura">Horário de Abertura</Label>
                    <Input
                      id="abertura"
                      type="time"
                      value={config.horarioFuncionamento.abertura}
                      onChange={(e) => setConfig({
                        ...config,
                        horarioFuncionamento: {
                          ...config.horarioFuncionamento,
                          abertura: e.target.value
                        }
                      })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="fechamento">Horário de Fechamento</Label>
                    <Input
                      id="fechamento"
                      type="time"
                      value={config.horarioFuncionamento.fechamento}
                      onChange={(e) => setConfig({
                        ...config,
                        horarioFuncionamento: {
                          ...config.horarioFuncionamento,
                          fechamento: e.target.value
                        }
                      })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Dias de Funcionamento</Label>
                  <div className="flex flex-wrap gap-2">
                    {DIAS_SEMANA.map((dia) => (
                      <Badge
                        key={dia.value}
                        variant={config.horarioFuncionamento.diasSemana.includes(dia.value) ? 'default' : 'outline'}
                        className="cursor-pointer"
                        onClick={() => {
                          const diasAtivos = config.horarioFuncionamento.diasSemana;
                          const novosDias = diasAtivos.includes(dia.value)
                            ? diasAtivos.filter(d => d !== dia.value)
                            : [...diasAtivos, dia.value];
                          
                          setConfig({
                            ...config,
                            horarioFuncionamento: {
                              ...config.horarioFuncionamento,
                              diasSemana: novosDias
                            }
                          });
                        }}
                      >
                        {dia.label}
                      </Badge>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Aba Técnicas */}
          <TabsContent value="tecnicas" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Configurações Técnicas
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="garantia">Tempo de Garantia (dias)</Label>
                    <Input
                      id="garantia"
                      type="number"
                      value={config.configuracoesTecnicas.tempoGarantia}
                      onChange={(e) => setConfig({
                        ...config,
                        configuracoesTecnicas: {
                          ...config.configuracoesTecnicas,
                          tempoGarantia: parseInt(e.target.value) || 0
                        }
                      })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="margem">Margem de Lucro (%)</Label>
                    <Input
                      id="margem"
                      type="number"
                      value={config.configuracoesTecnicas.margemLucro}
                      onChange={(e) => setConfig({
                        ...config,
                        configuracoesTecnicas: {
                          ...config.configuracoesTecnicas,
                          margemLucro: parseInt(e.target.value) || 0
                        }
                      })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="estoque">Alerta de Estoque Baixo</Label>
                    <Input
                      id="estoque"
                      type="number"
                      value={config.configuracoesTecnicas.alertaEstoqueBaixo}
                      onChange={(e) => setConfig({
                        ...config,
                        configuracoesTecnicas: {
                          ...config.configuracoesTecnicas,
                          alertaEstoqueBaixo: parseInt(e.target.value) || 0
                        }
                      })}
                    />
                  </div>
                </div>
                
                <Separator />
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Backup Automático</Label>
                      <p className="text-sm text-muted-foreground">
                        Realizar backup automático dos dados diariamente
                      </p>
                    </div>
                    <Switch
                      checked={config.configuracoesTecnicas.backupAutomatico}
                      onCheckedChange={(checked) => setConfig({
                        ...config,
                        configuracoesTecnicas: {
                          ...config.configuracoesTecnicas,
                          backupAutomatico: checked
                        }
                      })}
                    />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Notificações Push</Label>
                      <p className="text-sm text-muted-foreground">
                        Receber notificações em tempo real no navegador
                      </p>
                    </div>
                    <Switch
                      checked={config.configuracoesTecnicas.notificacoesPush}
                      onCheckedChange={(checked) => setConfig({
                        ...config,
                        configuracoesTecnicas: {
                          ...config.configuracoesTecnicas,
                          notificacoesPush: checked
                        }
                      })}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Aba Personalização */}
          <TabsContent value="personalizacao" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="h-5 w-5" />
                  Personalização Visual
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label>Tema</Label>
                    <Select
                      value={config.personalizacao.tema}
                      onValueChange={(value: 'light' | 'dark' | 'auto') => setConfig({
                        ...config,
                        personalizacao: {
                          ...config.personalizacao,
                          tema: value
                        }
                      })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {TEMAS.map((tema) => (
                          <SelectItem key={tema.value} value={tema.value}>
                            {tema.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Cor Primária</Label>
                    <div className="flex gap-2">
                      {CORES_PRIMARIAS.map((cor) => (
                        <button
                          key={cor.value}
                          className={`w-8 h-8 rounded-full border-2 ${
                            config.personalizacao.corPrimaria === cor.value
                              ? 'border-foreground'
                              : 'border-muted'
                          }`}
                          style={{ backgroundColor: cor.color }}
                          onClick={() => setConfig({
                            ...config,
                            personalizacao: {
                              ...config.personalizacao,
                              corPrimaria: cor.value
                            }
                          })}
                          title={cor.label}
                        />
                      ))}
                    </div>
                  </div>
                </div>
                
                <Separator />
                
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label>Logo da Loja</Label>
                    <div className="flex items-center gap-4">
                      <Button
                        variant="outline"
                        onClick={() => handleFileUpload('logo')}
                        className="flex items-center gap-2"
                      >
                        <Upload className="h-4 w-4" />
                        Fazer Upload
                      </Button>
                      {config.personalizacao.logo && (
                        <Badge variant="secondary">Logo carregado</Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Recomendado: PNG ou SVG, máximo 2MB
                    </p>
                  </div>
                  
                  <div className="space-y-2">
                    <Label>Favicon</Label>
                    <div className="flex items-center gap-4">
                      <Button
                        variant="outline"
                        onClick={() => handleFileUpload('favicon')}
                        className="flex items-center gap-2"
                      >
                        <Upload className="h-4 w-4" />
                        Fazer Upload
                      </Button>
                      {config.personalizacao.favicon && (
                        <Badge variant="secondary">Favicon carregado</Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Recomendado: ICO ou PNG 32x32px
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Aba Integrações */}
          <TabsContent value="integracoes" className="space-y-6">
            {/* WhatsApp */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="h-5 w-5" />
                  WhatsApp Business
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Ativar Integração WhatsApp</Label>
                    <p className="text-sm text-muted-foreground">
                      Enviar orçamentos e notificações via WhatsApp
                    </p>
                  </div>
                  <Switch
                    checked={config.integracao.whatsapp.ativo}
                    onCheckedChange={(checked) => setConfig({
                      ...config,
                      integracao: {
                        ...config.integracao,
                        whatsapp: {
                          ...config.integracao.whatsapp,
                          ativo: checked
                        }
                      }
                    })}
                  />
                </div>
                
                {config.integracao.whatsapp.ativo && (
                  <div className="space-y-4 pt-4 border-t">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="whatsapp-numero">Número do WhatsApp</Label>
                        <Input
                          id="whatsapp-numero"
                          value={config.integracao.whatsapp.numero}
                          onChange={(e) => setConfig({
                            ...config,
                            integracao: {
                              ...config.integracao,
                              whatsapp: {
                                ...config.integracao.whatsapp,
                                numero: e.target.value
                              }
                            }
                          })}
                          placeholder="5511999999999"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="whatsapp-token">Token da API</Label>
                        <Input
                          id="whatsapp-token"
                          type="password"
                          value={config.integracao.whatsapp.token}
                          onChange={(e) => setConfig({
                            ...config,
                            integracao: {
                              ...config.integracao,
                              whatsapp: {
                                ...config.integracao.whatsapp,
                                token: e.target.value
                              }
                            }
                          })}
                          placeholder="Token da API do WhatsApp"
                        />
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => testIntegration('whatsapp')}
                      className="flex items-center gap-2"
                    >
                      <Phone className="h-4 w-4" />
                      Testar Conexão
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* E-mail */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="h-5 w-5" />
                  Servidor de E-mail
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Ativar Envio de E-mail</Label>
                    <p className="text-sm text-muted-foreground">
                      Enviar orçamentos e relatórios por e-mail
                    </p>
                  </div>
                  <Switch
                    checked={config.integracao.email.ativo}
                    onCheckedChange={(checked) => setConfig({
                      ...config,
                      integracao: {
                        ...config.integracao,
                        email: {
                          ...config.integracao.email,
                          ativo: checked
                        }
                      }
                    })}
                  />
                </div>
                
                {config.integracao.email.ativo && (
                  <div className="space-y-4 pt-4 border-t">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="email-servidor">Servidor SMTP</Label>
                        <Input
                          id="email-servidor"
                          value={config.integracao.email.servidor}
                          onChange={(e) => setConfig({
                            ...config,
                            integracao: {
                              ...config.integracao,
                              email: {
                                ...config.integracao.email,
                                servidor: e.target.value
                              }
                            }
                          })}
                          placeholder="smtp.gmail.com"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="email-porta">Porta</Label>
                        <Input
                          id="email-porta"
                          type="number"
                          value={config.integracao.email.porta}
                          onChange={(e) => setConfig({
                            ...config,
                            integracao: {
                              ...config.integracao,
                              email: {
                                ...config.integracao.email,
                                porta: parseInt(e.target.value) || 587
                              }
                            }
                          })}
                          placeholder="587"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="email-usuario">Usuário</Label>
                        <Input
                          id="email-usuario"
                          value={config.integracao.email.usuario}
                          onChange={(e) => setConfig({
                            ...config,
                            integracao: {
                              ...config.integracao,
                              email: {
                                ...config.integracao.email,
                                usuario: e.target.value
                              }
                            }
                          })}
                          placeholder="seu-email@gmail.com"
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="email-senha">Senha</Label>
                        <Input
                          id="email-senha"
                          type="password"
                          value={config.integracao.email.senha}
                          onChange={(e) => setConfig({
                            ...config,
                            integracao: {
                              ...config.integracao,
                              email: {
                                ...config.integracao.email,
                                senha: e.target.value
                              }
                            }
                          })}
                          placeholder="Senha do e-mail"
                        />
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => testIntegration('email')}
                      className="flex items-center gap-2"
                    >
                      <Mail className="h-4 w-4" />
                      Testar Conexão
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Impressora */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Printer className="h-5 w-5" />
                  Impressora Térmica
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Ativar Impressão Automática</Label>
                    <p className="text-sm text-muted-foreground">
                      Imprimir orçamentos e OS automaticamente
                    </p>
                  </div>
                  <Switch
                    checked={config.integracao.impressora.ativo}
                    onCheckedChange={(checked) => setConfig({
                      ...config,
                      integracao: {
                        ...config.integracao,
                        impressora: {
                          ...config.integracao.impressora,
                          ativo: checked
                        }
                      }
                    })}
                  />
                </div>
                
                {config.integracao.impressora.ativo && (
                  <div className="space-y-4 pt-4 border-t">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="impressora-modelo">Modelo da Impressora</Label>
                        <Select
                          value={config.integracao.impressora.modelo}
                          onValueChange={(value) => setConfig({
                            ...config,
                            integracao: {
                              ...config.integracao,
                              impressora: {
                                ...config.integracao.impressora,
                                modelo: value
                              }
                            }
                          })}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione o modelo" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="epson-tm-t20">Epson TM-T20</SelectItem>
                            <SelectItem value="bematech-mp-4200">Bematech MP-4200</SelectItem>
                            <SelectItem value="daruma-dr-800">Daruma DR-800</SelectItem>
                            <SelectItem value="elgin-i9">Elgin i9</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="impressora-ip">IP da Impressora</Label>
                        <Input
                          id="impressora-ip"
                          value={config.integracao.impressora.ip}
                          onChange={(e) => setConfig({
                            ...config,
                            integracao: {
                              ...config.integracao,
                              impressora: {
                                ...config.integracao.impressora,
                                ip: e.target.value
                              }
                            }
                          })}
                          placeholder="192.168.1.100"
                        />
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => testIntegration('impressora')}
                      className="flex items-center gap-2"
                    >
                      <Printer className="h-4 w-4" />
                      Testar Impressão
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Aba Segurança */}
          <TabsContent value="seguranca" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Configurações de Segurança
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Autenticação de Dois Fatores</Label>
                      <p className="text-sm text-muted-foreground">
                        Adicionar uma camada extra de segurança
                      </p>
                    </div>
                    <Switch />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Log de Auditoria</Label>
                      <p className="text-sm text-muted-foreground">
                        Registrar todas as ações dos usuários
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Sessão Automática</Label>
                      <p className="text-sm text-muted-foreground">
                        Deslogar automaticamente após inatividade
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>
                </div>
                
                <Separator />
                
                <div className="space-y-4">
                  <h4 className="font-medium">Backup e Recuperação</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Button variant="outline" className="flex items-center gap-2">
                      <Download className="h-4 w-4" />
                      Baixar Backup
                    </Button>
                    <Button variant="outline" className="flex items-center gap-2">
                      <Upload className="h-4 w-4" />
                      Restaurar Backup
                    </Button>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Último backup: Hoje às 03:00
                  </p>
                </div>
                
                <Separator />
                
                <div className="space-y-4">
                  <h4 className="font-medium">Gerenciamento de Dados</h4>
                  <div className="space-y-2">
                    <Button variant="destructive" className="flex items-center gap-2">
                      <Database className="h-4 w-4" />
                      Limpar Cache do Sistema
                    </Button>
                    <p className="text-sm text-muted-foreground">
                      Remove dados temporários e otimiza o desempenho
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}