import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  ArrowLeft, 
  Edit, 
  Send, 
  Download, 
  Printer, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertCircle,
  User,
  Laptop,
  Calendar,
  DollarSign,
  FileText,
  Phone,
  Mail
} from 'lucide-react';
import { Orcamento, OrcamentoStatus } from '@/types/shared';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface DetalhesOrcamentoProps {}

export default function DetalhesOrcamento() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [orcamento, setOrcamento] = useState<Orcamento | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadOrcamento(id);
    }
  }, [id]);

  const loadOrcamento = async (orcamentoId: string) => {
    try {
      setLoading(true);
      // TODO: Implementar chamada real para API
      // const orcamentoData = await orcamentoAPI.buscarPorId(orcamentoId);
      
      // Mock data para desenvolvimento
      const mockOrcamento: Orcamento = {
        id: orcamentoId,
        numero: 'ORC-2024-001',
        clienteId: 'cliente-1',
        equipamentoId: 'equip-1',
        status: 'pendente',
        itens: [
          {
            tipo: 'peca',
            pecaId: 'peca-1',
            descricao: 'Memória RAM 8GB DDR4',
            quantidade: 1,
            valorUnitario: 250.00
          },
          {
            tipo: 'peca',
            pecaId: 'peca-2',
            descricao: 'SSD 500GB Samsung 980 EVO',
            quantidade: 1,
            valorUnitario: 350.00
          },
          {
            tipo: 'servico',
            descricao: 'Instalação e configuração',
            quantidade: 1,
            valorUnitario: 80.00
          }
        ],
        valorPecas: 600.00,
        valorServicos: 80.00,
        valorDesconto: 30.00,
        valorTotal: 650.00,
        observacoes: 'Upgrade de memória e armazenamento para melhorar performance do notebook.',
        validadeAte: new Date('2024-02-15'),
        criadoEm: new Date('2024-02-01'),
        atualizadoEm: new Date('2024-02-01'),
        // Dados relacionados (normalmente viriam de joins ou chamadas separadas)
        cliente: {
          id: 'cliente-1',
          nome: 'João Silva',
          email: 'joao@email.com',
          telefone: '(11) 99999-9999',
          cpf: '123.456.789-00',
          criadoEm: new Date(),
          atualizadoEm: new Date()
        },
        equipamento: {
          id: 'equip-1',
          clienteId: 'cliente-1',
          tipo: 'notebook',
          marca: 'Dell',
          modelo: 'Inspiron 15',
          numeroSerie: 'DL123456',
          descricaoProblema: 'Lentidão e travamentos',
          criadoEm: new Date(),
          atualizadoEm: new Date()
        }
      };
      
      setOrcamento(mockOrcamento);
    } catch (error) {
      console.error('Erro ao carregar orçamento:', error);
      setError('Erro ao carregar orçamento. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const atualizarStatus = async (novoStatus: OrcamentoStatus) => {
    if (!orcamento) return;
    
    try {
      setActionLoading(novoStatus);
      // TODO: Implementar chamada real para API
      // await orcamentoAPI.atualizarStatus(orcamento.id, novoStatus);
      
      setOrcamento({
        ...orcamento,
        status: novoStatus,
        atualizadoEm: new Date()
      });
      
      console.log(`Status atualizado para: ${novoStatus}`);
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      setError('Erro ao atualizar status. Tente novamente.');
    } finally {
      setActionLoading(null);
    }
  };

  const reenviarOrcamento = async () => {
    if (!orcamento) return;
    
    try {
      setActionLoading('reenviar');
      // TODO: Implementar chamada real para API
      // await orcamentoAPI.reenviar(orcamento.id);
      
      console.log('Orçamento reenviado');
    } catch (error) {
      console.error('Erro ao reenviar orçamento:', error);
      setError('Erro ao reenviar orçamento. Tente novamente.');
    } finally {
      setActionLoading(null);
    }
  };

  const gerarPDF = async () => {
    if (!orcamento) return;
    
    try {
      setActionLoading('pdf');
      // TODO: Implementar geração de PDF
      console.log('Gerando PDF do orçamento...');
    } catch (error) {
      console.error('Erro ao gerar PDF:', error);
      setError('Erro ao gerar PDF. Tente novamente.');
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusColor = (status: OrcamentoStatus) => {
    switch (status) {
      case 'pendente':
        return 'bg-yellow-100 text-yellow-800';
      case 'aprovado':
        return 'bg-green-100 text-green-800';
      case 'rejeitado':
        return 'bg-red-100 text-red-800';
      case 'expirado':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status: OrcamentoStatus) => {
    switch (status) {
      case 'pendente':
        return <Clock className="w-4 h-4" />;
      case 'aprovado':
        return <CheckCircle className="w-4 h-4" />;
      case 'rejeitado':
        return <XCircle className="w-4 h-4" />;
      case 'expirado':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const isExpired = orcamento && new Date() > orcamento.validadeAte;
  const canEdit = orcamento && ['pendente'].includes(orcamento.status) && !isExpired;
  const canApprove = orcamento && orcamento.status === 'pendente' && !isExpired;

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Carregando orçamento...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !orcamento) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center gap-4 mb-8">
          <Button variant="outline" onClick={() => navigate('/orcamentos')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar
          </Button>
        </div>
        <Alert>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error || 'Orçamento não encontrado.'}
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={() => navigate('/orcamentos')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Voltar
          </Button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Orçamento {orcamento.numero}
            </h1>
            <p className="text-gray-600">
              Criado em {orcamento.criadoEm.toLocaleDateString('pt-BR')}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Badge className={`${getStatusColor(orcamento.status)} flex items-center gap-1`}>
            {getStatusIcon(orcamento.status)}
            {orcamento.status.charAt(0).toUpperCase() + orcamento.status.slice(1)}
          </Badge>
          
          {isExpired && orcamento.status === 'pendente' && (
            <Badge className="bg-red-100 text-red-800">
              <AlertCircle className="w-4 h-4 mr-1" />
              Expirado
            </Badge>
          )}
        </div>
      </div>

      {error && (
        <Alert className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Conteúdo Principal */}
        <div className="lg:col-span-2 space-y-6">
          {/* Informações do Cliente e Equipamento */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="w-5 h-5" />
                  Cliente
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="font-medium text-lg">{orcamento.cliente?.nome}</p>
                  <p className="text-gray-600">{orcamento.cliente?.cpf}</p>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-sm">
                    <Phone className="w-4 h-4 text-gray-500" />
                    <span>{orcamento.cliente?.telefone}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Mail className="w-4 h-4 text-gray-500" />
                    <span>{orcamento.cliente?.email}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Laptop className="w-5 h-5" />
                  Equipamento
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="font-medium text-lg">
                    {orcamento.equipamento?.marca} {orcamento.equipamento?.modelo}
                  </p>
                  <p className="text-gray-600 capitalize">{orcamento.equipamento?.tipo}</p>
                </div>
                <div className="space-y-1">
                  <div className="text-sm">
                    <span className="text-gray-500">Série:</span> {orcamento.equipamento?.numeroSerie}
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-500">Problema:</span> {orcamento.equipamento?.descricaoProblema}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Itens do Orçamento */}
          <Card>
            <CardHeader>
              <CardTitle>Itens do Orçamento</CardTitle>
              <CardDescription>
                {orcamento.itens.length} {orcamento.itens.length === 1 ? 'item' : 'itens'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {orcamento.itens.map((item, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{item.descricao}</span>
                        <Badge 
                          variant="outline" 
                          className={item.tipo === 'peca' ? 'text-blue-600' : 'text-green-600'}
                        >
                          {item.tipo === 'peca' ? 'Peça' : 'Serviço'}
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        Quantidade: {item.quantidade} × R$ {item.valorUnitario.toFixed(2)}
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">
                        R$ {(item.quantidade * item.valorUnitario).toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Observações */}
          {orcamento.observacoes && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Observações
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 whitespace-pre-wrap">{orcamento.observacoes}</p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Sidebar - Resumo e Ações */}
        <div className="lg:col-span-1 space-y-6">
          {/* Resumo Financeiro */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="w-5 h-5" />
                Resumo Financeiro
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Peças:</span>
                  <span>R$ {orcamento.valorPecas.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Serviços:</span>
                  <span>R$ {orcamento.valorServicos.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Subtotal:</span>
                  <span>R$ {(orcamento.valorPecas + orcamento.valorServicos).toFixed(2)}</span>
                </div>
                {orcamento.valorDesconto > 0 && (
                  <div className="flex justify-between text-sm text-green-600">
                    <span>Desconto:</span>
                    <span>- R$ {orcamento.valorDesconto.toFixed(2)}</span>
                  </div>
                )}
                <hr />
                <div className="flex justify-between font-bold text-lg">
                  <span>Total:</span>
                  <span>R$ {orcamento.valorTotal.toFixed(2)}</span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Informações de Validade */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                Validade
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-sm">
                  <span className="text-gray-500">Válido até:</span>
                  <div className={`font-medium ${
                    isExpired ? 'text-red-600' : 'text-gray-900'
                  }`}>
                    {orcamento.validadeAte.toLocaleDateString('pt-BR')}
                  </div>
                </div>
                
                {isExpired && (
                  <div className="text-sm text-red-600">
                    <AlertCircle className="w-4 h-4 inline mr-1" />
                    Orçamento expirado
                  </div>
                )}
                
                <div className="text-sm">
                  <span className="text-gray-500">Última atualização:</span>
                  <div className="font-medium">
                    {orcamento.atualizadoEm.toLocaleDateString('pt-BR')} às {orcamento.atualizadoEm.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Ações */}
          <Card>
            <CardHeader>
              <CardTitle>Ações</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Ações de Status */}
              {canApprove && (
                <div className="space-y-2">
                  <Button 
                    onClick={() => atualizarStatus('aprovado')}
                    disabled={actionLoading === 'aprovado'}
                    className="w-full bg-green-600 hover:bg-green-700"
                  >
                    <CheckCircle className="w-4 h-4 mr-2" />
                    {actionLoading === 'aprovado' ? 'Aprovando...' : 'Aprovar'}
                  </Button>
                  
                  <Button 
                    onClick={() => atualizarStatus('rejeitado')}
                    disabled={actionLoading === 'rejeitado'}
                    variant="outline"
                    className="w-full text-red-600 border-red-600 hover:bg-red-50"
                  >
                    <XCircle className="w-4 h-4 mr-2" />
                    {actionLoading === 'rejeitado' ? 'Rejeitando...' : 'Rejeitar'}
                  </Button>
                </div>
              )}
              
              {/* Ações Gerais */}
              <div className="space-y-2">
                {canEdit && (
                  <Button 
                    onClick={() => navigate(`/orcamentos/${orcamento.id}/editar`)}
                    variant="outline"
                    className="w-full"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Editar
                  </Button>
                )}
                
                <Button 
                  onClick={reenviarOrcamento}
                  disabled={actionLoading === 'reenviar'}
                  variant="outline"
                  className="w-full"
                >
                  <Send className="w-4 h-4 mr-2" />
                  {actionLoading === 'reenviar' ? 'Enviando...' : 'Reenviar'}
                </Button>
                
                <Button 
                  onClick={gerarPDF}
                  disabled={actionLoading === 'pdf'}
                  variant="outline"
                  className="w-full"
                >
                  <Download className="w-4 h-4 mr-2" />
                  {actionLoading === 'pdf' ? 'Gerando...' : 'Baixar PDF'}
                </Button>
                
                <Button 
                  onClick={() => window.print()}
                  variant="outline"
                  className="w-full"
                >
                  <Printer className="w-4 h-4 mr-2" />
                  Imprimir
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}