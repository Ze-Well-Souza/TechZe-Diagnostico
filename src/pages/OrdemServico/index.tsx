import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import { 
  Plus, 
  Search, 
  Filter, 
  Edit, 
  Trash2, 
  Eye, 
  Clock, 
  CheckCircle, 
  XCircle,
  AlertCircle,
  User,
  Smartphone,
  Calendar,
  DollarSign,
  FileText,
  Settings,
  Download,
  Print,
  Send
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface OrdemServico {
  id: string;
  numero: string;
  cliente: {
    nome: string;
    telefone: string;
    email: string;
  };
  equipamento: {
    tipo: string;
    marca: string;
    modelo: string;
    numeroSerie?: string;
  };
  problema: string;
  descricao: string;
  status: 'aguardando' | 'em_andamento' | 'aguardando_peca' | 'aguardando_aprovacao' | 'concluida' | 'cancelada';
  prioridade: 'baixa' | 'media' | 'alta' | 'urgente';
  tecnico?: string;
  dataAbertura: string;
  dataPrevisao?: string;
  dataConclusao?: string;
  valorOrcamento?: number;
  valorFinal?: number;
  observacoes?: string;
  pecas: Array<{
    id: string;
    nome: string;
    quantidade: number;
    valor: number;
  }>;
  servicos: Array<{
    id: string;
    descricao: string;
    valor: number;
  }>;
}

const OrdemServico: React.FC = () => {
  const { toast } = useToast();
  const [ordens, setOrdens] = useState<OrdemServico[]>([
    {
      id: '1',
      numero: 'OS-2024-001',
      cliente: {
        nome: 'João Silva',
        telefone: '(11) 99999-9999',
        email: 'joao@email.com'
      },
      equipamento: {
        tipo: 'Smartphone',
        marca: 'Samsung',
        modelo: 'Galaxy S21',
        numeroSerie: 'SN123456789'
      },
      problema: 'Tela quebrada',
      descricao: 'Cliente relatou que o aparelho caiu e a tela rachou',
      status: 'em_andamento',
      prioridade: 'media',
      tecnico: 'Carlos Santos',
      dataAbertura: '2024-01-15',
      dataPrevisao: '2024-01-20',
      valorOrcamento: 250.00,
      pecas: [
        { id: '1', nome: 'Tela LCD Samsung S21', quantidade: 1, valor: 180.00 }
      ],
      servicos: [
        { id: '1', descricao: 'Troca de tela', valor: 70.00 }
      ]
    },
    {
      id: '2',
      numero: 'OS-2024-002',
      cliente: {
        nome: 'Maria Oliveira',
        telefone: '(11) 88888-8888',
        email: 'maria@email.com'
      },
      equipamento: {
        tipo: 'Notebook',
        marca: 'Dell',
        modelo: 'Inspiron 15',
        numeroSerie: 'DL987654321'
      },
      problema: 'Não liga',
      descricao: 'Equipamento não apresenta sinais de vida',
      status: 'aguardando_peca',
      prioridade: 'alta',
      tecnico: 'Ana Costa',
      dataAbertura: '2024-01-16',
      dataPrevisao: '2024-01-25',
      valorOrcamento: 450.00,
      pecas: [
        { id: '2', nome: 'Fonte Dell 65W', quantidade: 1, valor: 120.00 },
        { id: '3', nome: 'Bateria Dell Inspiron', quantidade: 1, valor: 180.00 }
      ],
      servicos: [
        { id: '2', descricao: 'Diagnóstico completo', valor: 50.00 },
        { id: '3', descricao: 'Troca de fonte e bateria', valor: 100.00 }
      ]
    }
  ]);

  const [filtros, setFiltros] = useState({
    busca: '',
    status: '',
    prioridade: '',
    tecnico: ''
  });

  const [ordemSelecionada, setOrdemSelecionada] = useState<OrdemServico | null>(null);
  const [dialogAberto, setDialogAberto] = useState(false);
  const [modoEdicao, setModoEdicao] = useState(false);

  // Filtrar ordens
  const ordensFiltradas = useMemo(() => {
    return ordens.filter(ordem => {
      const matchBusca = !filtros.busca || 
        ordem.numero.toLowerCase().includes(filtros.busca.toLowerCase()) ||
        ordem.cliente.nome.toLowerCase().includes(filtros.busca.toLowerCase()) ||
        ordem.equipamento.marca.toLowerCase().includes(filtros.busca.toLowerCase()) ||
        ordem.equipamento.modelo.toLowerCase().includes(filtros.busca.toLowerCase());
      
      const matchStatus = !filtros.status || ordem.status === filtros.status;
      const matchPrioridade = !filtros.prioridade || ordem.prioridade === filtros.prioridade;
      const matchTecnico = !filtros.tecnico || ordem.tecnico === filtros.tecnico;
      
      return matchBusca && matchStatus && matchPrioridade && matchTecnico;
    });
  }, [ordens, filtros]);

  // Estatísticas
  const estatisticas = useMemo(() => {
    const total = ordens.length;
    const aguardando = ordens.filter(o => o.status === 'aguardando').length;
    const emAndamento = ordens.filter(o => o.status === 'em_andamento').length;
    const concluidas = ordens.filter(o => o.status === 'concluida').length;
    const valorTotal = ordens.reduce((acc, o) => acc + (o.valorFinal || o.valorOrcamento || 0), 0);
    
    return { total, aguardando, emAndamento, concluidas, valorTotal };
  }, [ordens]);

  // Obter cor do status
  const getStatusColor = (status: OrdemServico['status']) => {
    const colors = {
      aguardando: 'bg-yellow-100 text-yellow-800',
      em_andamento: 'bg-blue-100 text-blue-800',
      aguardando_peca: 'bg-orange-100 text-orange-800',
      aguardando_aprovacao: 'bg-purple-100 text-purple-800',
      concluida: 'bg-green-100 text-green-800',
      cancelada: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  // Obter cor da prioridade
  const getPrioridadeColor = (prioridade: OrdemServico['prioridade']) => {
    const colors = {
      baixa: 'bg-green-100 text-green-800',
      media: 'bg-yellow-100 text-yellow-800',
      alta: 'bg-orange-100 text-orange-800',
      urgente: 'bg-red-100 text-red-800'
    };
    return colors[prioridade] || 'bg-gray-100 text-gray-800';
  };

  // Obter ícone do status
  const getStatusIcon = (status: OrdemServico['status']) => {
    const icons = {
      aguardando: Clock,
      em_andamento: Settings,
      aguardando_peca: AlertCircle,
      aguardando_aprovacao: FileText,
      concluida: CheckCircle,
      cancelada: XCircle
    };
    const Icon = icons[status] || Clock;
    return <Icon className="h-4 w-4" />;
  };

  // Abrir dialog de nova ordem
  const abrirNovaOrdem = () => {
    setOrdemSelecionada(null);
    setModoEdicao(true);
    setDialogAberto(true);
  };

  // Visualizar ordem
  const visualizarOrdem = (ordem: OrdemServico) => {
    setOrdemSelecionada(ordem);
    setModoEdicao(false);
    setDialogAberto(true);
  };

  // Editar ordem
  const editarOrdem = (ordem: OrdemServico) => {
    setOrdemSelecionada(ordem);
    setModoEdicao(true);
    setDialogAberto(true);
  };

  // Excluir ordem
  const excluirOrdem = (id: string) => {
    setOrdens(prev => prev.filter(o => o.id !== id));
    toast({
      title: "Ordem excluída",
      description: "A ordem de serviço foi excluída com sucesso."
    });
  };

  // Alterar status
  const alterarStatus = (id: string, novoStatus: OrdemServico['status']) => {
    setOrdens(prev => prev.map(o => 
      o.id === id ? { ...o, status: novoStatus } : o
    ));
    toast({
      title: "Status atualizado",
      description: "O status da ordem foi atualizado com sucesso."
    });
  };

  return (
    <div className="space-y-6">
      {/* Cabeçalho */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Ordem de Serviço</h1>
          <p className="text-muted-foreground">
            Gerencie as ordens de serviço da sua assistência técnica
          </p>
        </div>
        <Button onClick={abrirNovaOrdem}>
          <Plus className="h-4 w-4 mr-2" />
          Nova Ordem
        </Button>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <FileText className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm font-medium">Total</span>
            </div>
            <p className="text-2xl font-bold">{estatisticas.total}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-yellow-600" />
              <span className="text-sm font-medium">Aguardando</span>
            </div>
            <p className="text-2xl font-bold">{estatisticas.aguardando}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Settings className="h-4 w-4 text-blue-600" />
              <span className="text-sm font-medium">Em Andamento</span>
            </div>
            <p className="text-2xl font-bold">{estatisticas.emAndamento}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium">Concluídas</span>
            </div>
            <p className="text-2xl font-bold">{estatisticas.concluidas}</p>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <DollarSign className="h-4 w-4 text-green-600" />
              <span className="text-sm font-medium">Valor Total</span>
            </div>
            <p className="text-2xl font-bold">
              {new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL'
              }).format(estatisticas.valorTotal)}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card>
        <CardContent className="p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <Label htmlFor="busca">Buscar</Label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="busca"
                  placeholder="Número, cliente, equipamento..."
                  value={filtros.busca}
                  onChange={(e) => setFiltros(prev => ({ ...prev, busca: e.target.value }))}
                  className="pl-10"
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select value={filtros.status} onValueChange={(value) => setFiltros(prev => ({ ...prev, status: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos os status</SelectItem>
                  <SelectItem value="aguardando">Aguardando</SelectItem>
                  <SelectItem value="em_andamento">Em Andamento</SelectItem>
                  <SelectItem value="aguardando_peca">Aguardando Peça</SelectItem>
                  <SelectItem value="aguardando_aprovacao">Aguardando Aprovação</SelectItem>
                  <SelectItem value="concluida">Concluída</SelectItem>
                  <SelectItem value="cancelada">Cancelada</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="prioridade">Prioridade</Label>
              <Select value={filtros.prioridade} onValueChange={(value) => setFiltros(prev => ({ ...prev, prioridade: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Todas as prioridades" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todas as prioridades</SelectItem>
                  <SelectItem value="baixa">Baixa</SelectItem>
                  <SelectItem value="media">Média</SelectItem>
                  <SelectItem value="alta">Alta</SelectItem>
                  <SelectItem value="urgente">Urgente</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="tecnico">Técnico</Label>
              <Select value={filtros.tecnico} onValueChange={(value) => setFiltros(prev => ({ ...prev, tecnico: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Todos os técnicos" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">Todos os técnicos</SelectItem>
                  <SelectItem value="Carlos Santos">Carlos Santos</SelectItem>
                  <SelectItem value="Ana Costa">Ana Costa</SelectItem>
                  <SelectItem value="Pedro Lima">Pedro Lima</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Lista de Ordens */}
      <Card>
        <CardHeader>
          <CardTitle>Ordens de Serviço ({ordensFiltradas.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Número</TableHead>
                <TableHead>Cliente</TableHead>
                <TableHead>Equipamento</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Prioridade</TableHead>
                <TableHead>Técnico</TableHead>
                <TableHead>Data Abertura</TableHead>
                <TableHead>Valor</TableHead>
                <TableHead>Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {ordensFiltradas.map((ordem) => (
                <TableRow key={ordem.id}>
                  <TableCell className="font-medium">{ordem.numero}</TableCell>
                  <TableCell>
                    <div>
                      <p className="font-medium">{ordem.cliente.nome}</p>
                      <p className="text-sm text-muted-foreground">{ordem.cliente.telefone}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <p className="font-medium">{ordem.equipamento.marca} {ordem.equipamento.modelo}</p>
                      <p className="text-sm text-muted-foreground">{ordem.equipamento.tipo}</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={cn("flex items-center gap-1 w-fit", getStatusColor(ordem.status))}>
                      {getStatusIcon(ordem.status)}
                      {ordem.status.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={cn("w-fit", getPrioridadeColor(ordem.prioridade))}>
                      {ordem.prioridade.toUpperCase()}
                    </Badge>
                  </TableCell>
                  <TableCell>{ordem.tecnico || '-'}</TableCell>
                  <TableCell>
                    {new Date(ordem.dataAbertura).toLocaleDateString('pt-BR')}
                  </TableCell>
                  <TableCell>
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: 'BRL'
                    }).format(ordem.valorFinal || ordem.valorOrcamento || 0)}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => visualizarOrdem(ordem)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => editarOrdem(ordem)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Confirmar exclusão</AlertDialogTitle>
                            <AlertDialogDescription>
                              Tem certeza que deseja excluir a ordem {ordem.numero}? Esta ação não pode ser desfeita.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancelar</AlertDialogCancel>
                            <AlertDialogAction onClick={() => excluirOrdem(ordem.id)}>
                              Excluir
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Dialog de Ordem */}
      <Dialog open={dialogAberto} onOpenChange={setDialogAberto}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {modoEdicao ? (ordemSelecionada ? 'Editar Ordem' : 'Nova Ordem') : 'Visualizar Ordem'}
            </DialogTitle>
          </DialogHeader>
          
          {ordemSelecionada && (
            <Tabs defaultValue="geral" className="space-y-4">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="geral">Geral</TabsTrigger>
                <TabsTrigger value="pecas">Peças</TabsTrigger>
                <TabsTrigger value="servicos">Serviços</TabsTrigger>
                <TabsTrigger value="historico">Histórico</TabsTrigger>
              </TabsList>
              
              <TabsContent value="geral" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Número da Ordem</Label>
                    <Input value={ordemSelecionada.numero} readOnly={!modoEdicao} />
                  </div>
                  <div className="space-y-2">
                    <Label>Status</Label>
                    <Select value={ordemSelecionada.status} disabled={!modoEdicao}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="aguardando">Aguardando</SelectItem>
                        <SelectItem value="em_andamento">Em Andamento</SelectItem>
                        <SelectItem value="aguardando_peca">Aguardando Peça</SelectItem>
                        <SelectItem value="aguardando_aprovacao">Aguardando Aprovação</SelectItem>
                        <SelectItem value="concluida">Concluída</SelectItem>
                        <SelectItem value="cancelada">Cancelada</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                
                <Separator />
                
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Informações do Cliente</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Nome</Label>
                      <Input value={ordemSelecionada.cliente.nome} readOnly={!modoEdicao} />
                    </div>
                    <div className="space-y-2">
                      <Label>Telefone</Label>
                      <Input value={ordemSelecionada.cliente.telefone} readOnly={!modoEdicao} />
                    </div>
                    <div className="space-y-2 col-span-2">
                      <Label>E-mail</Label>
                      <Input value={ordemSelecionada.cliente.email} readOnly={!modoEdicao} />
                    </div>
                  </div>
                </div>
                
                <Separator />
                
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Informações do Equipamento</h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Tipo</Label>
                      <Input value={ordemSelecionada.equipamento.tipo} readOnly={!modoEdicao} />
                    </div>
                    <div className="space-y-2">
                      <Label>Marca</Label>
                      <Input value={ordemSelecionada.equipamento.marca} readOnly={!modoEdicao} />
                    </div>
                    <div className="space-y-2">
                      <Label>Modelo</Label>
                      <Input value={ordemSelecionada.equipamento.modelo} readOnly={!modoEdicao} />
                    </div>
                    <div className="space-y-2">
                      <Label>Número de Série</Label>
                      <Input value={ordemSelecionada.equipamento.numeroSerie || ''} readOnly={!modoEdicao} />
                    </div>
                  </div>
                </div>
                
                <Separator />
                
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Problema e Descrição</h3>
                  <div className="space-y-2">
                    <Label>Problema Relatado</Label>
                    <Input value={ordemSelecionada.problema} readOnly={!modoEdicao} />
                  </div>
                  <div className="space-y-2">
                    <Label>Descrição Detalhada</Label>
                    <Textarea value={ordemSelecionada.descricao} readOnly={!modoEdicao} rows={3} />
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="pecas" className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Peças Utilizadas</h3>
                  {modoEdicao && (
                    <Button size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Adicionar Peça
                    </Button>
                  )}
                </div>
                
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Peça</TableHead>
                      <TableHead>Quantidade</TableHead>
                      <TableHead>Valor Unitário</TableHead>
                      <TableHead>Total</TableHead>
                      {modoEdicao && <TableHead>Ações</TableHead>}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {ordemSelecionada.pecas.map((peca) => (
                      <TableRow key={peca.id}>
                        <TableCell>{peca.nome}</TableCell>
                        <TableCell>{peca.quantidade}</TableCell>
                        <TableCell>
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          }).format(peca.valor)}
                        </TableCell>
                        <TableCell>
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          }).format(peca.valor * peca.quantidade)}
                        </TableCell>
                        {modoEdicao && (
                          <TableCell>
                            <Button variant="ghost" size="sm">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TabsContent>
              
              <TabsContent value="servicos" className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Serviços Realizados</h3>
                  {modoEdicao && (
                    <Button size="sm">
                      <Plus className="h-4 w-4 mr-2" />
                      Adicionar Serviço
                    </Button>
                  )}
                </div>
                
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Descrição</TableHead>
                      <TableHead>Valor</TableHead>
                      {modoEdicao && <TableHead>Ações</TableHead>}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {ordemSelecionada.servicos.map((servico) => (
                      <TableRow key={servico.id}>
                        <TableCell>{servico.descricao}</TableCell>
                        <TableCell>
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL'
                          }).format(servico.valor)}
                        </TableCell>
                        {modoEdicao && (
                          <TableCell>
                            <Button variant="ghost" size="sm">
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </TableCell>
                        )}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TabsContent>
              
              <TabsContent value="historico" className="space-y-4">
                <h3 className="text-lg font-semibold">Histórico da Ordem</h3>
                <div className="space-y-3">
                  <div className="flex items-start gap-3 p-3 border rounded-lg">
                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Ordem criada</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(ordemSelecionada.dataAbertura).toLocaleString('pt-BR')}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start gap-3 p-3 border rounded-lg">
                    <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Status alterado para: Em Andamento</p>
                      <p className="text-xs text-muted-foreground">
                        Técnico: {ordemSelecionada.tecnico}
                      </p>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          )}
          
          <div className="flex items-center justify-between pt-4">
            <div className="flex items-center gap-2">
              {!modoEdicao && ordemSelecionada && (
                <>
                  <Button variant="outline" size="sm">
                    <Print className="h-4 w-4 mr-2" />
                    Imprimir
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    PDF
                  </Button>
                  <Button variant="outline" size="sm">
                    <Send className="h-4 w-4 mr-2" />
                    Enviar
                  </Button>
                </>
              )}
            </div>
            
            <div className="flex items-center gap-2">
              <Button variant="outline" onClick={() => setDialogAberto(false)}>
                {modoEdicao ? 'Cancelar' : 'Fechar'}
              </Button>
              {modoEdicao && (
                <Button onClick={() => {
                  toast({
                    title: "Ordem salva",
                    description: "A ordem de serviço foi salva com sucesso."
                  });
                  setDialogAberto(false);
                }}>
                  Salvar
                </Button>
              )}
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default OrdemServico;