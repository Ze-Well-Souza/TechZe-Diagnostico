import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  TrendingUp,
  Clock,
  CheckCircle,
  CheckCircle2,
  XCircle,
  DollarSign,
  AlertCircle,
  Calendar,
  FileText,
  Send,
  Download
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { Orcamento, OrcamentoStatus } from '@/types/shared';
import { useOrcamentos } from '@/hooks/useOrcamentos';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface OrcamentosPageProps {}

const statusConfig: Record<OrcamentoStatus, { label: string; color: string; icon: React.ReactNode }> = {
  pendente: {
    label: 'Pendente',
    color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    icon: <Clock className="w-3 h-3" />
  },
  aprovado: {
    label: 'Aprovado',
    color: 'bg-green-100 text-green-800 border-green-200',
    icon: <CheckCircle2 className="w-3 h-3" />
  },
  rejeitado: {
    label: 'Rejeitado',
    color: 'bg-red-100 text-red-800 border-red-200',
    icon: <XCircle className="w-3 h-3" />
  },
  expirado: {
    label: 'Expirado',
    color: 'bg-gray-100 text-gray-800 border-gray-200',
    icon: <Calendar className="w-3 h-3" />
  }
};

const OrcamentosPage: React.FC<OrcamentosPageProps> = () => {
  const navigate = useNavigate();
  const {
    orcamentos,
    carregando,
    erro,
    estatisticas,
    carregarOrcamentos,
    atualizarStatus,
    excluirOrcamento,
    reenviarOrcamento
  } = useOrcamentos();

  const [termoBusca, setTermoBusca] = useState('');
  const [filtroStatus, setFiltroStatus] = useState<OrcamentoStatus | 'todos'>('todos');

  const filteredOrcamentos = orcamentos.filter(orcamento => {
    const matchesStatus = filtroStatus === 'todos' || orcamento.status === filtroStatus;
    const matchesSearch = !termoBusca || 
      orcamento.numero.toLowerCase().includes(termoBusca.toLowerCase()) ||
      orcamento.cliente?.nome.toLowerCase().includes(termoBusca.toLowerCase());
    
    return matchesStatus && matchesSearch;
  });

  const handleStatusChange = async (id: string, novoStatus: OrcamentoStatus) => {
    try {
      await atualizarStatus(id, novoStatus);
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Tem certeza que deseja excluir este orçamento?')) {
      try {
        await excluirOrcamento(id);
      } catch (error) {
        console.error('Erro ao excluir orçamento:', error);
      }
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    }).format(new Date(date));
  };

  const isExpiringSoon = (validadeAte: Date) => {
    const today = new Date();
    const diffTime = new Date(validadeAte).getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays <= 2 && diffDays > 0;
  };

  const isExpired = (validadeAte: Date) => {
    const today = new Date();
    return new Date(validadeAte) < today;
  };

  const getStatusVariant = (status: OrcamentoStatus): "default" | "secondary" | "destructive" | "outline" => {
    switch (status) {
      case 'aprovado':
        return 'default';
      case 'pendente':
        return 'secondary';
      case 'rejeitado':
      case 'expirado':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const getStatusLabel = (status: OrcamentoStatus): string => {
    switch (status) {
      case 'rascunho':
        return 'Rascunho';
      case 'pendente':
        return 'Pendente';
      case 'aprovado':
        return 'Aprovado';
      case 'rejeitado':
        return 'Rejeitado';
      case 'expirado':
        return 'Expirado';
      default:
        return status;
    }
  };

  const statusConfig = {
    rascunho: {
      label: 'Rascunho',
      color: 'bg-gray-100 text-gray-800 border-gray-200',
      icon: <Edit className="w-3 h-3" />
    },
    pendente: {
      label: 'Pendente',
      color: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      icon: <Clock className="w-3 h-3" />
    },
    aprovado: {
      label: 'Aprovado',
      color: 'bg-green-100 text-green-800 border-green-200',
      icon: <CheckCircle className="w-3 h-3" />
    },
    rejeitado: {
      label: 'Rejeitado',
      color: 'bg-red-100 text-red-800 border-red-200',
      icon: <XCircle className="w-3 h-3" />
    },
    expirado: {
      label: 'Expirado',
      color: 'bg-red-100 text-red-800 border-red-200',
      icon: <XCircle className="w-3 h-3" />
    }
  };

  if (carregando) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Orçamentos</h1>
          <p className="text-gray-600">Gerencie todos os orçamentos da sua empresa</p>
        </div>
        <Link to="/orcamentos/novo">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            Novo Orçamento
          </Button>
        </Link>
      </div>

      {erro && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{erro}</AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      {estatisticas && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Orçamentos</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{estatisticas.total}</div>
              <p className="text-xs text-muted-foreground">Todos os orçamentos</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pendentes</CardTitle>
              <Clock className="h-4 w-4 text-yellow-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-600">{estatisticas.pendentes}</div>
              <p className="text-xs text-muted-foreground">Aguardando aprovação</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Aprovados</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{estatisticas.aprovados}</div>
              <p className="text-xs text-muted-foreground">Confirmados pelo cliente</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Valor Aprovado</CardTitle>
              <DollarSign className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{formatCurrency(estatisticas.valorAprovado)}</div>
              <p className="text-xs text-muted-foreground">Total em orçamentos aprovados</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Buscar por número do orçamento..."
                  value={termoBusca}
                  onChange={(e) => setTermoBusca(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="sm:w-48">
              <select
                value={filtroStatus}
                onChange={(e) => setFiltroStatus(e.target.value as OrcamentoStatus | 'todos')}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="todos">Todos os status</option>
                <option value="pendente">Pendente</option>
                <option value="aprovado">Aprovado</option>
                <option value="rejeitado">Rejeitado</option>
                <option value="expirado">Expirado</option>
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Orçamentos List */}
      <div className="space-y-4">
        {filteredOrcamentos.length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-8">
                <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Nenhum orçamento encontrado</h3>
                <p className="text-gray-500 mb-4">
                  {termoBusca || filtroStatus !== 'todos' 
                    ? 'Tente ajustar os filtros de busca'
                    : 'Comece criando seu primeiro orçamento'
                  }
                </p>
                {!termoBusca && filtroStatus === 'todos' && (
                  <Link to="/orcamentos/novo">
                    <Button>
                      <Plus className="w-4 h-4 mr-2" />
                      Criar Primeiro Orçamento
                    </Button>
                  </Link>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (
          filteredOrcamentos.map((orcamento) => {
            const config = statusConfig[orcamento.status];
            const expiringSoon = isExpiringSoon(orcamento.validadeAte);
            const expired = isExpired(orcamento.validadeAte);
            
            return (
              <Card key={orcamento.id} className="hover:shadow-md transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex flex-col lg:flex-row lg:items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {orcamento.numero}
                        </h3>
                        <Badge className={`${config.color} flex items-center gap-1`}>
                          {config.icon}
                          {config.label}
                        </Badge>
                        {expiringSoon && (
                          <Badge className="bg-orange-100 text-orange-800 border-orange-200">
                            <Calendar className="w-3 h-3 mr-1" />
                            Expira em breve
                          </Badge>
                        )}
                        {expired && (
                          <Badge className="bg-red-100 text-red-800 border-red-200">
                            <Calendar className="w-3 h-3 mr-1" />
                            Expirado
                          </Badge>
                        )}
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div>
                          <span className="font-medium">Valor Total:</span>
                          <div className="text-lg font-bold text-gray-900">
                            {formatCurrency(orcamento.valorTotal)}
                          </div>
                        </div>
                        <div>
                          <span className="font-medium">Criado em:</span>
                          <div>{formatDate(orcamento.criadoEm)}</div>
                        </div>
                        <div>
                          <span className="font-medium">Válido até:</span>
                          <div className={expired ? 'text-red-600 font-medium' : expiringSoon ? 'text-orange-600 font-medium' : ''}>
                            {formatDate(orcamento.validadeAte)}
                          </div>
                        </div>
                      </div>
                      
                      <div className="mt-3">
                        <span className="font-medium text-sm text-gray-600">Itens:</span>
                        <div className="text-sm text-gray-700 mt-1">
                          {orcamento.itens.length} item(s) - 
                          Peças: {formatCurrency(orcamento.valorPecas)} | 
                          Serviços: {formatCurrency(orcamento.valorServicos)}
                          {orcamento.valorDesconto > 0 && (
                            <span className="text-green-600"> | Desconto: {formatCurrency(orcamento.valorDesconto)}</span>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-2 mt-4 lg:mt-0">
                      <Link to={`/orcamentos/${orcamento.id}`}>
                        <Button variant="outline" size="sm">
                          <Eye className="w-4 h-4 mr-1" />
                          Ver
                        </Button>
                      </Link>
                      
                      {orcamento.status === 'pendente' && (
                        <Link to={`/orcamentos/${orcamento.id}/editar`}>
                          <Button variant="outline" size="sm">
                            <Edit className="w-4 h-4 mr-1" />
                            Editar
                          </Button>
                        </Link>
                      )}
                      
                      <Button variant="outline" size="sm">
                        <Download className="w-4 h-4 mr-1" />
                        PDF
                      </Button>
                      
                      {orcamento.status === 'pendente' && (
                        <Button variant="outline" size="sm">
                          <Send className="w-4 h-4 mr-1" />
                          Enviar
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}