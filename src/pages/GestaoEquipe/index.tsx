import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from '@/components/ui/alert-dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Switch } from '@/components/ui/switch';
import { Textarea } from '@/components/ui/textarea';
import { 
  Users, 
  UserPlus, 
  Search, 
  Filter, 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  Shield, 
  ShieldCheck, 
  Clock, 
  Mail, 
  Phone, 
  MapPin,
  Calendar,
  Award,
  TrendingUp,
  Activity,
  CheckCircle,
  XCircle,
  AlertTriangle
} from 'lucide-react';
import { useGestaoEquipe } from '@/hooks/useGestaoEquipe';
import { useToast } from '@/hooks/use-toast';

const GestaoEquipe: React.FC = () => {
  const { 
    funcionarios, 
    carregando, 
    adicionarFuncionario, 
    editarFuncionario, 
    removerFuncionario, 
    alterarStatus,
    obterEstatisticas,
    obterHistoricoAtividades
  } = useGestaoEquipe();
  
  const { toast } = useToast();
  const [busca, setBusca] = React.useState('');
  const [filtroStatus, setFiltroStatus] = React.useState('todos');
  const [filtroFuncao, setFiltroFuncao] = React.useState('todos');
  const [dialogAberto, setDialogAberto] = React.useState(false);
  const [funcionarioEditando, setFuncionarioEditando] = React.useState<any>(null);
  const [novoFuncionario, setNovoFuncionario] = React.useState({
    nome: '',
    email: '',
    telefone: '',
    funcao: '',
    salario: '',
    dataAdmissao: '',
    endereco: '',
    observacoes: '',
    permissoes: {
      vendas: false,
      estoque: false,
      financeiro: false,
      relatorios: false,
      configuracoes: false,
      admin: false
    }
  });

  const estatisticas = React.useMemo(() => obterEstatisticas(), [funcionarios]);
  const historicoAtividades = React.useMemo(() => obterHistoricoAtividades(), [funcionarios]);

  const funcionariosFiltrados = React.useMemo(() => {
    return funcionarios.filter(funcionario => {
      const matchBusca = funcionario.nome.toLowerCase().includes(busca.toLowerCase()) ||
                        funcionario.email.toLowerCase().includes(busca.toLowerCase());
      const matchStatus = filtroStatus === 'todos' || funcionario.status === filtroStatus;
      const matchFuncao = filtroFuncao === 'todos' || funcionario.funcao === filtroFuncao;
      
      return matchBusca && matchStatus && matchFuncao;
    });
  }, [funcionarios, busca, filtroStatus, filtroFuncao]);

  const handleSalvarFuncionario = async () => {
    try {
      if (funcionarioEditando) {
        await editarFuncionario(funcionarioEditando.id, novoFuncionario);
        toast({
          title: "Funcionário atualizado",
          description: "As informações foram atualizadas com sucesso."
        });
      } else {
        await adicionarFuncionario(novoFuncionario);
        toast({
          title: "Funcionário adicionado",
          description: "Novo funcionário foi adicionado à equipe."
        });
      }
      
      setDialogAberto(false);
      setFuncionarioEditando(null);
      setNovoFuncionario({
        nome: '',
        email: '',
        telefone: '',
        funcao: '',
        salario: '',
        dataAdmissao: '',
        endereco: '',
        observacoes: '',
        permissoes: {
          vendas: false,
          estoque: false,
          financeiro: false,
          relatorios: false,
          configuracoes: false,
          admin: false
        }
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Não foi possível salvar as informações do funcionário.",
        variant: "destructive"
      });
    }
  };

  const handleEditarFuncionario = (funcionario: any) => {
    setFuncionarioEditando(funcionario);
    setNovoFuncionario(funcionario);
    setDialogAberto(true);
  };

  const handleRemoverFuncionario = async (id: string) => {
    try {
      await removerFuncionario(id);
      toast({
        title: "Funcionário removido",
        description: "O funcionário foi removido da equipe."
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Não foi possível remover o funcionário.",
        variant: "destructive"
      });
    }
  };

  const handleAlterarStatus = async (id: string, novoStatus: string) => {
    try {
      await alterarStatus(id, novoStatus);
      toast({
        title: "Status atualizado",
        description: "O status do funcionário foi atualizado."
      });
    } catch (error) {
      toast({
        title: "Erro",
        description: "Não foi possível atualizar o status.",
        variant: "destructive"
      });
    }
  };

  const StatusBadge = ({ status }: { status: string }) => {
    const statusConfig = {
      ativo: { color: 'bg-green-500', text: 'Ativo', icon: CheckCircle },
      inativo: { color: 'bg-red-500', text: 'Inativo', icon: XCircle },
      ferias: { color: 'bg-blue-500', text: 'Férias', icon: Calendar },
      licenca: { color: 'bg-yellow-500', text: 'Licença', icon: AlertTriangle }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.inativo;
    const Icon = config.icon;

    return (
      <Badge variant="outline" className="flex items-center gap-1">
        <div className={`w-2 h-2 rounded-full ${config.color}`} />
        <Icon className="h-3 w-3" />
        {config.text}
      </Badge>
    );
  };

  const FuncaoBadge = ({ funcao }: { funcao: string }) => {
    const cores = {
      'Técnico': 'bg-blue-100 text-blue-800',
      'Vendedor': 'bg-green-100 text-green-800',
      'Gerente': 'bg-purple-100 text-purple-800',
      'Atendente': 'bg-orange-100 text-orange-800',
      'Administrador': 'bg-red-100 text-red-800'
    };

    return (
      <Badge className={cores[funcao as keyof typeof cores] || 'bg-gray-100 text-gray-800'}>
        {funcao}
      </Badge>
    );
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestão de Equipe</h1>
          <p className="text-muted-foreground">
            Gerencie funcionários, permissões e acompanhe o desempenho da equipe
          </p>
        </div>
        
        <Dialog open={dialogAberto} onOpenChange={setDialogAberto}>
          <DialogTrigger asChild>
            <Button className="flex items-center gap-2">
              <UserPlus className="h-4 w-4" />
              Adicionar Funcionário
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {funcionarioEditando ? 'Editar Funcionário' : 'Adicionar Novo Funcionário'}
              </DialogTitle>
              <DialogDescription>
                Preencha as informações do funcionário e configure suas permissões.
              </DialogDescription>
            </DialogHeader>
            
            <div className="space-y-4">
              {/* Informações Básicas */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="nome">Nome Completo *</Label>
                  <Input
                    id="nome"
                    value={novoFuncionario.nome}
                    onChange={(e) => setNovoFuncionario({ ...novoFuncionario, nome: e.target.value })}
                    placeholder="João Silva"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">E-mail *</Label>
                  <Input
                    id="email"
                    type="email"
                    value={novoFuncionario.email}
                    onChange={(e) => setNovoFuncionario({ ...novoFuncionario, email: e.target.value })}
                    placeholder="joao@techze.com.br"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="telefone">Telefone</Label>
                  <Input
                    id="telefone"
                    value={novoFuncionario.telefone}
                    onChange={(e) => setNovoFuncionario({ ...novoFuncionario, telefone: e.target.value })}
                    placeholder="(11) 99999-9999"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="funcao">Função *</Label>
                  <Select
                    value={novoFuncionario.funcao}
                    onValueChange={(value) => setNovoFuncionario({ ...novoFuncionario, funcao: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Selecione a função" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Técnico">Técnico</SelectItem>
                      <SelectItem value="Vendedor">Vendedor</SelectItem>
                      <SelectItem value="Atendente">Atendente</SelectItem>
                      <SelectItem value="Gerente">Gerente</SelectItem>
                      <SelectItem value="Administrador">Administrador</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="salario">Salário</Label>
                  <Input
                    id="salario"
                    value={novoFuncionario.salario}
                    onChange={(e) => setNovoFuncionario({ ...novoFuncionario, salario: e.target.value })}
                    placeholder="R$ 2.500,00"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="dataAdmissao">Data de Admissão</Label>
                  <Input
                    id="dataAdmissao"
                    type="date"
                    value={novoFuncionario.dataAdmissao}
                    onChange={(e) => setNovoFuncionario({ ...novoFuncionario, dataAdmissao: e.target.value })}
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="endereco">Endereço</Label>
                <Input
                  id="endereco"
                  value={novoFuncionario.endereco}
                  onChange={(e) => setNovoFuncionario({ ...novoFuncionario, endereco: e.target.value })}
                  placeholder="Rua, número, bairro, cidade, CEP"
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="observacoes">Observações</Label>
                <Textarea
                  id="observacoes"
                  value={novoFuncionario.observacoes}
                  onChange={(e) => setNovoFuncionario({ ...novoFuncionario, observacoes: e.target.value })}
                  placeholder="Informações adicionais sobre o funcionário"
                  rows={3}
                />
              </div>
              
              {/* Permissões */}
              <div className="space-y-3">
                <Label className="text-base font-medium">Permissões do Sistema</Label>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries({
                    vendas: 'Vendas',
                    estoque: 'Estoque',
                    financeiro: 'Financeiro',
                    relatorios: 'Relatórios',
                    configuracoes: 'Configurações',
                    admin: 'Administrador'
                  }).map(([key, label]) => (
                    <div key={key} className="flex items-center justify-between p-3 border rounded-lg">
                      <Label htmlFor={key} className="text-sm font-medium">
                        {label}
                      </Label>
                      <Switch
                        id={key}
                        checked={novoFuncionario.permissoes[key as keyof typeof novoFuncionario.permissoes]}
                        onCheckedChange={(checked) => 
                          setNovoFuncionario({
                            ...novoFuncionario,
                            permissoes: {
                              ...novoFuncionario.permissoes,
                              [key]: checked
                            }
                          })
                        }
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogAberto(false)}>
                Cancelar
              </Button>
              <Button onClick={handleSalvarFuncionario}>
                {funcionarioEditando ? 'Atualizar' : 'Adicionar'} Funcionário
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total de Funcionários</p>
                <p className="text-2xl font-bold">{estatisticas.total}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Funcionários Ativos</p>
                <p className="text-2xl font-bold text-green-600">{estatisticas.ativos}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Em Férias/Licença</p>
                <p className="text-2xl font-bold text-yellow-600">{estatisticas.ausentes}</p>
              </div>
              <Calendar className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Folha de Pagamento</p>
                <p className="text-2xl font-bold">{estatisticas.folhaPagamento}</p>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filtros e Busca */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Buscar funcionários..."
                  value={busca}
                  onChange={(e) => setBusca(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            
            <Select value={filtroStatus} onValueChange={setFiltroStatus}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos os Status</SelectItem>
                <SelectItem value="ativo">Ativo</SelectItem>
                <SelectItem value="inativo">Inativo</SelectItem>
                <SelectItem value="ferias">Férias</SelectItem>
                <SelectItem value="licenca">Licença</SelectItem>
              </SelectContent>
            </Select>
            
            <Select value={filtroFuncao} onValueChange={setFiltroFuncao}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Função" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todas as Funções</SelectItem>
                <SelectItem value="Técnico">Técnico</SelectItem>
                <SelectItem value="Vendedor">Vendedor</SelectItem>
                <SelectItem value="Atendente">Atendente</SelectItem>
                <SelectItem value="Gerente">Gerente</SelectItem>
                <SelectItem value="Administrador">Administrador</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Funcionários */}
      <Card>
        <CardHeader>
          <CardTitle>Lista de Funcionários</CardTitle>
          <CardDescription>
            {funcionariosFiltrados.length} funcionário(s) encontrado(s)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Funcionário</TableHead>
                <TableHead>Função</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Contato</TableHead>
                <TableHead>Admissão</TableHead>
                <TableHead>Permissões</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {funcionariosFiltrados.map((funcionario) => (
                <TableRow key={funcionario.id}>
                  <TableCell>
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarImage src={funcionario.avatar} />
                        <AvatarFallback>
                          {funcionario.nome.split(' ').map(n => n[0]).join('').toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{funcionario.nome}</p>
                        <p className="text-sm text-muted-foreground">{funcionario.email}</p>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <FuncaoBadge funcao={funcionario.funcao} />
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={funcionario.status} />
                  </TableCell>
                  <TableCell>
                    <div className="space-y-1">
                      {funcionario.telefone && (
                        <div className="flex items-center gap-1 text-sm">
                          <Phone className="h-3 w-3" />
                          {funcionario.telefone}
                        </div>
                      )}
                      <div className="flex items-center gap-1 text-sm">
                        <Mail className="h-3 w-3" />
                        {funcionario.email}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1 text-sm">
                      <Calendar className="h-3 w-3" />
                      {new Date(funcionario.dataAdmissao).toLocaleDateString('pt-BR')}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(funcionario.permissoes)
                        .filter(([_, value]) => value)
                        .slice(0, 2)
                        .map(([key]) => (
                          <Badge key={key} variant="outline" className="text-xs">
                            {key}
                          </Badge>
                        ))
                      }
                      {Object.values(funcionario.permissoes).filter(Boolean).length > 2 && (
                        <Badge variant="outline" className="text-xs">
                          +{Object.values(funcionario.permissoes).filter(Boolean).length - 2}
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleEditarFuncionario(funcionario)}
                      >
                        <Edit className="h-4 w-4" />
                      </Button>
                      
                      <Select
                        value={funcionario.status}
                        onValueChange={(value) => handleAlterarStatus(funcionario.id, value)}
                      >
                        <SelectTrigger className="w-[100px] h-8">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="ativo">Ativo</SelectItem>
                          <SelectItem value="inativo">Inativo</SelectItem>
                          <SelectItem value="ferias">Férias</SelectItem>
                          <SelectItem value="licenca">Licença</SelectItem>
                        </SelectContent>
                      </Select>
                      
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button variant="ghost" size="sm" className="text-red-600">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Remover Funcionário</AlertDialogTitle>
                            <AlertDialogDescription>
                              Tem certeza que deseja remover {funcionario.nome} da equipe? 
                              Esta ação não pode ser desfeita.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancelar</AlertDialogCancel>
                            <AlertDialogAction 
                              onClick={() => handleRemoverFuncionario(funcionario.id)}
                              className="bg-red-600 hover:bg-red-700"
                            >
                              Remover
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
          
          {funcionariosFiltrados.length === 0 && (
            <div className="text-center py-8">
              <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <p className="text-muted-foreground">
                Nenhum funcionário encontrado com os filtros aplicados.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default GestaoEquipe;