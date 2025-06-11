import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Package,
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Edit,
  Trash2,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Package2,
  ShoppingCart,
  BarChart3,
  Download,
  Upload
} from 'lucide-react';
import { useEstoque } from '@/hooks/useEstoque';
import { toast } from '@/hooks/use-toast';

const statusConfig = {
  disponivel: {
    label: 'Disponível',
    color: 'bg-green-500',
    variant: 'default' as const
  },
  baixo_estoque: {
    label: 'Baixo Estoque',
    color: 'bg-yellow-500',
    variant: 'secondary' as const
  },
  esgotado: {
    label: 'Esgotado',
    color: 'bg-red-500',
    variant: 'destructive' as const
  },
  descontinuado: {
    label: 'Descontinuado',
    color: 'bg-gray-500',
    variant: 'outline' as const
  }
};

const categorias = [
  'Peças de Reposição',
  'Ferramentas',
  'Acessórios',
  'Componentes Eletrônicos',
  'Materiais de Limpeza',
  'Outros'
];

export default function EstoquePage() {
  const navigate = useNavigate();
  const {
    itens,
    estatisticas,
    loading,
    error,
    carregarItens,
    criarItem,
    atualizarItem,
    excluirItem,
    ajustarEstoque,
    carregarEstatisticas
  } = useEstoque();

  const [busca, setBusca] = useState('');
  const [categoriaFiltro, setCategoriaFiltro] = useState<string>('todos');
  const [statusFiltro, setStatusFiltro] = useState<string>('todos');
  const [dialogAberto, setDialogAberto] = useState(false);
  const [itemEditando, setItemEditando] = useState<any>(null);
  const [dialogAjuste, setDialogAjuste] = useState(false);
  const [itemAjuste, setItemAjuste] = useState<any>(null);

  const [formulario, setFormulario] = useState({
    nome: '',
    descricao: '',
    categoria: '',
    codigo: '',
    preco_custo: '',
    preco_venda: '',
    quantidade_atual: '',
    quantidade_minima: '',
    fornecedor: '',
    localizacao: ''
  });

  const [ajusteForm, setAjusteForm] = useState({
    tipo: 'entrada' as 'entrada' | 'saida',
    quantidade: '',
    motivo: '',
    observacoes: ''
  });

  useEffect(() => {
    carregarItens();
    carregarEstatisticas();
  }, [carregarItens, carregarEstatisticas]);

  const itensFiltrados = itens.filter(item => {
    const matchBusca = item.nome.toLowerCase().includes(busca.toLowerCase()) ||
                     item.codigo.toLowerCase().includes(busca.toLowerCase());
    const matchCategoria = categoriaFiltro === 'todos' || item.categoria === categoriaFiltro;
    const matchStatus = statusFiltro === 'todos' || item.status === statusFiltro;
    
    return matchBusca && matchCategoria && matchStatus;
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const dados = {
        ...formulario,
        preco_custo: parseFloat(formulario.preco_custo),
        preco_venda: parseFloat(formulario.preco_venda),
        quantidade_atual: parseInt(formulario.quantidade_atual),
        quantidade_minima: parseInt(formulario.quantidade_minima)
      };

      if (itemEditando) {
        await atualizarItem(itemEditando.id, dados);
        toast({
          title: 'Sucesso',
          description: 'Item atualizado com sucesso!'
        });
      } else {
        await criarItem(dados);
        toast({
          title: 'Sucesso',
          description: 'Item criado com sucesso!'
        });
      }

      setDialogAberto(false);
      resetFormulario();
    } catch (error) {
      console.error('Erro ao salvar item:', error);
    }
  };

  const handleAjusteEstoque = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await ajustarEstoque(
        itemAjuste.id,
        ajusteForm.tipo,
        parseInt(ajusteForm.quantidade),
        ajusteForm.motivo,
        ajusteForm.observacoes
      );

      toast({
        title: 'Sucesso',
        description: 'Estoque ajustado com sucesso!'
      });

      setDialogAjuste(false);
      setAjusteForm({
        tipo: 'entrada',
        quantidade: '',
        motivo: '',
        observacoes: ''
      });
    } catch (error) {
      console.error('Erro ao ajustar estoque:', error);
    }
  };

  const resetFormulario = () => {
    setFormulario({
      nome: '',
      descricao: '',
      categoria: '',
      codigo: '',
      preco_custo: '',
      preco_venda: '',
      quantidade_atual: '',
      quantidade_minima: '',
      fornecedor: '',
      localizacao: ''
    });
    setItemEditando(null);
  };

  const abrirEdicao = (item: any) => {
    setItemEditando(item);
    setFormulario({
      nome: item.nome,
      descricao: item.descricao || '',
      categoria: item.categoria,
      codigo: item.codigo,
      preco_custo: item.preco_custo.toString(),
      preco_venda: item.preco_venda.toString(),
      quantidade_atual: item.quantidade_atual.toString(),
      quantidade_minima: item.quantidade_minima.toString(),
      fornecedor: item.fornecedor || '',
      localizacao: item.localizacao || ''
    });
    setDialogAberto(true);
  };

  const abrirAjuste = (item: any) => {
    setItemAjuste(item);
    setDialogAjuste(true);
  };

  const handleExcluir = async (itemId: string) => {
    if (confirm('Tem certeza que deseja excluir este item?')) {
      try {
        await excluirItem(itemId);
        toast({
          title: 'Sucesso',
          description: 'Item excluído com sucesso!'
        });
      } catch (error) {
        console.error('Erro ao excluir item:', error);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Gestão de Estoque</h1>
          <p className="text-muted-foreground">
            Gerencie o inventário de peças e materiais
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Exportar
          </Button>
          <Button variant="outline" size="sm">
            <Upload className="h-4 w-4 mr-2" />
            Importar
          </Button>
          <Dialog open={dialogAberto} onOpenChange={setDialogAberto}>
            <DialogTrigger asChild>
              <Button onClick={resetFormulario}>
                <Plus className="h-4 w-4 mr-2" />
                Novo Item
              </Button>
            </DialogTrigger>
          </Dialog>
        </div>
      </div>

      {/* Estatísticas */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Itens</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{estatisticas?.totalItens || 0}</div>
            <p className="text-xs text-muted-foreground">
              {estatisticas?.itensAtivos || 0} ativos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Valor Total</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              R$ {(estatisticas?.valorTotal || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
            </div>
            <p className="text-xs text-muted-foreground">
              Valor do inventário
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Baixo Estoque</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {estatisticas?.itensBaixoEstoque || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Itens com estoque baixo
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Esgotados</CardTitle>
            <Package2 className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {estatisticas?.itensEsgotados || 0}
            </div>
            <p className="text-xs text-muted-foreground">
              Itens sem estoque
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle>Filtros</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Buscar por nome ou código..."
                  value={busca}
                  onChange={(e) => setBusca(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <Select value={categoriaFiltro} onValueChange={setCategoriaFiltro}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="Categoria" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todas as categorias</SelectItem>
                {categorias.map(categoria => (
                  <SelectItem key={categoria} value={categoria}>
                    {categoria}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={statusFiltro} onValueChange={setStatusFiltro}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="todos">Todos os status</SelectItem>
                <SelectItem value="disponivel">Disponível</SelectItem>
                <SelectItem value="baixo_estoque">Baixo Estoque</SelectItem>
                <SelectItem value="esgotado">Esgotado</SelectItem>
                <SelectItem value="descontinuado">Descontinuado</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabela de Itens */}
      <Card>
        <CardHeader>
          <CardTitle>Itens do Estoque</CardTitle>
          <CardDescription>
            {itensFiltrados.length} itens encontrados
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Código</TableHead>
                <TableHead>Nome</TableHead>
                <TableHead>Categoria</TableHead>
                <TableHead>Quantidade</TableHead>
                <TableHead>Preço</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Ações</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {itensFiltrados.map((item) => (
                <TableRow key={item.id}>
                  <TableCell className="font-mono">{item.codigo}</TableCell>
                  <TableCell>
                    <div>
                      <div className="font-medium">{item.nome}</div>
                      {item.descricao && (
                        <div className="text-sm text-muted-foreground">
                          {item.descricao}
                        </div>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>{item.categoria}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <span className={item.quantidade_atual <= item.quantidade_minima ? 'text-red-600 font-medium' : ''}>
                        {item.quantidade_atual}
                      </span>
                      <span className="text-muted-foreground">/ {item.quantidade_minima}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    R$ {item.preco_venda.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </TableCell>
                  <TableCell>
                    <Badge variant={statusConfig[item.status as keyof typeof statusConfig]?.variant}>
                      {statusConfig[item.status as keyof typeof statusConfig]?.label}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Ações</DropdownMenuLabel>
                        <DropdownMenuItem onClick={() => abrirEdicao(item)}>
                          <Edit className="mr-2 h-4 w-4" />
                          Editar
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => abrirAjuste(item)}>
                          <Package className="mr-2 h-4 w-4" />
                          Ajustar Estoque
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem 
                          onClick={() => handleExcluir(item.id)}
                          className="text-red-600"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Excluir
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Dialog Criar/Editar Item */}
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>
            {itemEditando ? 'Editar Item' : 'Novo Item'}
          </DialogTitle>
          <DialogDescription>
            {itemEditando ? 'Edite as informações do item.' : 'Adicione um novo item ao estoque.'}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="nome">Nome *</Label>
                <Input
                  id="nome"
                  value={formulario.nome}
                  onChange={(e) => setFormulario(prev => ({ ...prev, nome: e.target.value }))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="codigo">Código *</Label>
                <Input
                  id="codigo"
                  value={formulario.codigo}
                  onChange={(e) => setFormulario(prev => ({ ...prev, codigo: e.target.value }))}
                  required
                />
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="descricao">Descrição</Label>
              <Textarea
                id="descricao"
                value={formulario.descricao}
                onChange={(e) => setFormulario(prev => ({ ...prev, descricao: e.target.value }))}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="categoria">Categoria *</Label>
                <Select
                  value={formulario.categoria}
                  onValueChange={(value) => setFormulario(prev => ({ ...prev, categoria: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione uma categoria" />
                  </SelectTrigger>
                  <SelectContent>
                    {categorias.map(categoria => (
                      <SelectItem key={categoria} value={categoria}>
                        {categoria}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="fornecedor">Fornecedor</Label>
                <Input
                  id="fornecedor"
                  value={formulario.fornecedor}
                  onChange={(e) => setFormulario(prev => ({ ...prev, fornecedor: e.target.value }))}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="preco_custo">Preço de Custo *</Label>
                <Input
                  id="preco_custo"
                  type="number"
                  step="0.01"
                  value={formulario.preco_custo}
                  onChange={(e) => setFormulario(prev => ({ ...prev, preco_custo: e.target.value }))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="preco_venda">Preço de Venda *</Label>
                <Input
                  id="preco_venda"
                  type="number"
                  step="0.01"
                  value={formulario.preco_venda}
                  onChange={(e) => setFormulario(prev => ({ ...prev, preco_venda: e.target.value }))}
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="quantidade_atual">Quantidade Atual *</Label>
                <Input
                  id="quantidade_atual"
                  type="number"
                  value={formulario.quantidade_atual}
                  onChange={(e) => setFormulario(prev => ({ ...prev, quantidade_atual: e.target.value }))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="quantidade_minima">Quantidade Mínima *</Label>
                <Input
                  id="quantidade_minima"
                  type="number"
                  value={formulario.quantidade_minima}
                  onChange={(e) => setFormulario(prev => ({ ...prev, quantidade_minima: e.target.value }))}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="localizacao">Localização</Label>
                <Input
                  id="localizacao"
                  value={formulario.localizacao}
                  onChange={(e) => setFormulario(prev => ({ ...prev, localizacao: e.target.value }))}
                  placeholder="Ex: A1-B2"
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setDialogAberto(false)}>
              Cancelar
            </Button>
            <Button type="submit">
              {itemEditando ? 'Atualizar' : 'Criar'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>

      {/* Dialog Ajuste de Estoque */}
      <Dialog open={dialogAjuste} onOpenChange={setDialogAjuste}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Ajustar Estoque</DialogTitle>
            <DialogDescription>
              Ajuste o estoque do item: {itemAjuste?.nome}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleAjusteEstoque}>
            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label>Tipo de Ajuste</Label>
                <Select
                  value={ajusteForm.tipo}
                  onValueChange={(value: 'entrada' | 'saida') => 
                    setAjusteForm(prev => ({ ...prev, tipo: value }))
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="entrada">
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-green-600" />
                        Entrada (+)
                      </div>
                    </SelectItem>
                    <SelectItem value="saida">
                      <div className="flex items-center gap-2">
                        <TrendingDown className="h-4 w-4 text-red-600" />
                        Saída (-)
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="quantidade">Quantidade *</Label>
                <Input
                  id="quantidade"
                  type="number"
                  min="1"
                  value={ajusteForm.quantidade}
                  onChange={(e) => setAjusteForm(prev => ({ ...prev, quantidade: e.target.value }))}
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="motivo">Motivo *</Label>
                <Input
                  id="motivo"
                  value={ajusteForm.motivo}
                  onChange={(e) => setAjusteForm(prev => ({ ...prev, motivo: e.target.value }))}
                  placeholder="Ex: Compra, Venda, Perda, Correção"
                  required
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="observacoes">Observações</Label>
                <Textarea
                  id="observacoes"
                  value={ajusteForm.observacoes}
                  onChange={(e) => setAjusteForm(prev => ({ ...prev, observacoes: e.target.value }))}
                  placeholder="Informações adicionais sobre o ajuste"
                />
              </div>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setDialogAjuste(false)}>
                Cancelar
              </Button>
              <Button type="submit">
                Confirmar Ajuste
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}