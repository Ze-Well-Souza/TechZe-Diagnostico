import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import {
  Clock,
  CheckCircle2,
  AlertCircle,
  Phone,
  Mail,
  Calendar,
  FileText,
  Download,
  Eye,
  MessageSquare,
  Star,
  History
} from 'lucide-react';
import { OrdemServico, OrcamentoStatus } from '@/types/shared';
import { usePortalCliente } from '@/hooks/usePortalCliente';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

interface PortalClienteProps {}

const statusConfig = {
  'aguardando_diagnostico': {
    label: 'Aguardando Diagnóstico',
    color: 'bg-blue-100 text-blue-800',
    progress: 20,
    icon: <Clock className="w-4 h-4" />
  },
  'diagnostico_concluido': {
    label: 'Diagnóstico Concluído',
    color: 'bg-yellow-100 text-yellow-800',
    progress: 40,
    icon: <FileText className="w-4 h-4" />
  },
  'aguardando_aprovacao': {
    label: 'Aguardando Aprovação',
    color: 'bg-orange-100 text-orange-800',
    progress: 50,
    icon: <AlertCircle className="w-4 h-4" />
  },
  'em_reparo': {
    label: 'Em Reparo',
    color: 'bg-purple-100 text-purple-800',
    progress: 75,
    icon: <Clock className="w-4 h-4" />
  },
  'concluido': {
    label: 'Concluído',
    color: 'bg-green-100 text-green-800',
    progress: 100,
    icon: <CheckCircle2 className="w-4 h-4" />
  }
};

const PortalCliente: React.FC<PortalClienteProps> = () => {
  const { user } = useAuth();
  const {
    ordensServico,
    historico,
    loading,
    error,
    carregarDados,
    avaliarServico,
    baixarOrcamento
  } = usePortalCliente();

  const [activeTab, setActiveTab] = useState('atual');

  useEffect(() => {
    carregarDados();
  }, [carregarDados]);

  const ordensAtivas = ordensServico.filter(os => os.status !== 'concluido');
  const ordensConcluidas = ordensServico.filter(os => os.status === 'concluido');

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando seus dados...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Alert className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Olá, {user?.nome || 'Cliente'}!
              </h1>
              <p className="text-gray-600">
                Acompanhe o status dos seus equipamentos
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                <Phone className="w-4 h-4 mr-2" />
                Contato
              </Button>
              <Button variant="outline" size="sm">
                <MessageSquare className="w-4 h-4 mr-2" />
                Suporte
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="atual">Serviços Atuais ({ordensAtivas.length})</TabsTrigger>
            <TabsTrigger value="historico">Histórico ({ordensConcluidas.length})</TabsTrigger>
            <TabsTrigger value="perfil">Meu Perfil</TabsTrigger>
          </TabsList>

          {/* Serviços Atuais */}
          <TabsContent value="atual" className="space-y-6">
            {ordensAtivas.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <CheckCircle2 className="w-12 h-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Nenhum serviço em andamento
                  </h3>
                  <p className="text-gray-600 text-center">
                    Você não possui equipamentos em manutenção no momento.
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6">
                {ordensAtivas.map((os) => {
                  const config = statusConfig[os.status as keyof typeof statusConfig];
                  return (
                    <Card key={os.id} className="overflow-hidden">
                      <CardHeader>
                        <div className="flex justify-between items-start">
                          <div>
                            <CardTitle className="text-lg">
                              OS #{os.numero}
                            </CardTitle>
                            <CardDescription>
                              {os.equipamento?.tipo} - {os.equipamento?.marca} {os.equipamento?.modelo}
                            </CardDescription>
                          </div>
                          <Badge className={config?.color}>
                            {config?.icon}
                            <span className="ml-1">{config?.label}</span>
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        {/* Progress Bar */}
                        <div className="space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Progresso</span>
                            <span className="font-medium">{config?.progress}%</span>
                          </div>
                          <Progress value={config?.progress} className="h-2" />
                        </div>

                        {/* Informações */}
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="text-gray-600">Data de Entrada:</span>
                            <p className="font-medium">
                              {new Date(os.criadoEm).toLocaleDateString('pt-BR')}
                            </p>
                          </div>
                          <div>
                            <span className="text-gray-600">Técnico:</span>
                            <p className="font-medium">
                              {os.tecnico?.nome || 'Não atribuído'}
                            </p>
                          </div>
                        </div>

                        {/* Diagnóstico */}
                        {os.diagnostico && (
                          <div className="bg-gray-50 p-4 rounded-lg">
                            <h4 className="font-medium mb-2">Diagnóstico:</h4>
                            <p className="text-sm text-gray-700">
                              {os.diagnostico.descricao}
                            </p>
                          </div>
                        )}

                        {/* Orçamento */}
                        {os.orcamento && (
                          <div className="bg-blue-50 p-4 rounded-lg">
                            <div className="flex justify-between items-center">
                              <div>
                                <h4 className="font-medium">Orçamento</h4>
                                <p className="text-lg font-bold text-blue-600">
                                  R$ {os.orcamento.valorTotal.toFixed(2)}
                                </p>
                              </div>
                              <div className="flex space-x-2">
                                <Button size="sm" variant="outline" onClick={() => baixarOrcamento(os.orcamento!.id)}>
                                  <Download className="w-4 h-4 mr-1" />
                                  Baixar
                                </Button>
                                {os.orcamento.status === 'pendente' && (
                                  <Button size="sm">
                                    Aprovar
                                  </Button>
                                )}
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Ações */}
                        <div className="flex justify-between items-center pt-4 border-t">
                          <Button variant="outline" size="sm">
                            <Eye className="w-4 h-4 mr-2" />
                            Ver Detalhes
                          </Button>
                          <Button variant="outline" size="sm">
                            <MessageSquare className="w-4 h-4 mr-2" />
                            Conversar
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            )}
          </TabsContent>

          {/* Histórico */}
          <TabsContent value="historico" className="space-y-6">
            {ordensConcluidas.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <History className="w-12 h-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Nenhum histórico encontrado
                  </h3>
                  <p className="text-gray-600 text-center">
                    Você ainda não possui serviços concluídos.
                  </p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4">
                {ordensConcluidas.map((os) => (
                  <Card key={os.id}>
                    <CardContent className="p-6">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-medium">OS #{os.numero}</h3>
                          <p className="text-sm text-gray-600">
                            {os.equipamento?.tipo} - {os.equipamento?.marca} {os.equipamento?.modelo}
                          </p>
                          <p className="text-sm text-gray-500 mt-1">
                            Concluído em {new Date(os.atualizadoEm).toLocaleDateString('pt-BR')}
                          </p>
                        </div>
                        <div className="flex items-center space-x-2">
                          {!os.avaliacao && (
                            <Button size="sm" variant="outline" onClick={() => avaliarServico(os.id)}>
                              <Star className="w-4 h-4 mr-1" />
                              Avaliar
                            </Button>
                          )}
                          <Button size="sm" variant="outline">
                            <Eye className="w-4 h-4 mr-1" />
                            Ver
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>

          {/* Perfil */}
          <TabsContent value="perfil">
            <Card>
              <CardHeader>
                <CardTitle>Meus Dados</CardTitle>
                <CardDescription>
                  Mantenha suas informações sempre atualizadas
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium text-gray-700">Nome</label>
                    <p className="mt-1 text-sm text-gray-900">{user?.nome}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Email</label>
                    <p className="mt-1 text-sm text-gray-900">{user?.email}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">Telefone</label>
                    <p className="mt-1 text-sm text-gray-900">{user?.telefone}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-700">CPF</label>
                    <p className="mt-1 text-sm text-gray-900">{user?.cpf}</p>
                  </div>
                </div>
                <div className="pt-4">
                  <Button variant="outline">
                    Editar Informações
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default PortalCliente;