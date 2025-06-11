import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useNotifications } from '@/hooks/useNotifications';
import { useCharts } from '@/hooks/useCharts';
import { MainLayout } from '@/components/layout/MainLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { DateRangePicker } from '@/components/dashboard/DateRangePicker';
import { ChartContainer } from '@/components/dashboard/ChartContainer';
import { MetricCard } from '@/components/dashboard/MetricCard';
import {
  BarChart3,
  PieChart,
  TrendingUp,
  Download,
  Filter,
  Calendar,
  FileText,
  DollarSign,
  Users,
  Wrench,
  Package,
  Clock,
  Target,
  Eye,
  Settings,
  Share,
  Printer,
  Mail,
} from 'lucide-react';
import { subDays, format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface RelatorioFiltros {
  periodo: {
    inicio: Date;
    fim: Date;
  };
  tipo: 'financeiro' | 'operacional' | 'clientes' | 'estoque' | 'todos';
  loja?: string;
  tecnico?: string;
  cliente?: string;
  status?: string;
}

interface DadosRelatorio {
  financeiro: {
    receita: number;
    lucro: number;
    ticketMedio: number;
    receitaPorDia: Array<{ data: string; valor: number }>;
    receitaPorCategoria: Array<{ categoria: string; valor: number }>;
  };
  operacional: {
    osAbertas: number;
    osConcluidas: number;
    tempoMedioReparo: number;
    satisfacaoCliente: number;
    produtividadeTecnicos: Array<{ tecnico: string; os: number; tempo: number }>;
    statusOS: Array<{ status: string; quantidade: number }>;
  };
  clientes: {
    novosClientes: number;
    clientesRecorrentes: number;
    taxaRetencao: number;
    nps: number;
    clientesPorRegiao: Array<{ regiao: string; quantidade: number }>;
    avaliacoes: Array<{ nota: number; quantidade: number }>;
  };
  estoque: {
    valorTotal: number;
    itensEmFalta: number;
    giroEstoque: number;
    margemLucro: number;
    itensMaisVendidos: Array<{ item: string; quantidade: number; valor: number }>;
    movimentacoes: Array<{ data: string; entrada: number; saida: number }>;
  };
}

const TIPOS_RELATORIO = [
  { value: 'todos', label: 'Todos os Relatórios', icon: BarChart3 },
  { value: 'financeiro', label: 'Financeiro', icon: DollarSign },
  { value: 'operacional', label: 'Operacional', icon: Wrench },
  { value: 'clientes', label: 'Clientes', icon: Users },
  { value: 'estoque', label: 'Estoque', icon: Package },
];

const FORMATOS_EXPORT = [
  { value: 'pdf', label: 'PDF', icon: FileText },
  { value: 'excel', label: 'Excel', icon: FileText },
  { value: 'csv', label: 'CSV', icon: FileText },
];

const PERIODOS_PRESET = [
  { value: '7d', label: 'Últimos 7 dias', dias: 7 },
  { value: '30d', label: 'Últimos 30 dias', dias: 30 },
  { value: '90d', label: 'Últimos 90 dias', dias: 90 },
  { value: '1y', label: 'Último ano', dias: 365 },
];

export default function Relatorios() {
  const { user, company } = useAuth();
  const { addNotification } = useNotifications();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isLoading, setIsLoading] = useState(false);
  const [filtros, setFiltros] = useState<RelatorioFiltros>({
    periodo: {
      inicio: subDays(new Date(), 30),
      fim: new Date(),
    },
    tipo: 'todos',
  });
  
  const [dados, setDados] = useState<DadosRelatorio>({
    financeiro: {
      receita: 45680.50,
      lucro: 13704.15,
      ticketMedio: 285.40,
      receitaPorDia: [],
      receitaPorCategoria: [
        { categoria: 'Reparos', valor: 28500 },
        { categoria: 'Peças', valor: 12300 },
        { categoria: 'Consultoria', valor: 4880 },
      ],
    },
    operacional: {
      osAbertas: 23,
      osConcluidas: 156,
      tempoMedioReparo: 2.5,
      satisfacaoCliente: 4.7,
      produtividadeTecnicos: [
        { tecnico: 'João Silva', os: 45, tempo: 2.2 },
        { tecnico: 'Maria Santos', os: 38, tempo: 2.8 },
        { tecnico: 'Pedro Costa', os: 42, tempo: 2.4 },
      ],
      statusOS: [
        { status: 'Aguardando Peças', quantidade: 8 },
        { status: 'Em Reparo', quantidade: 12 },
        { status: 'Aguardando Cliente', quantidade: 3 },
      ],
    },
    clientes: {
      novosClientes: 34,
      clientesRecorrentes: 89,
      taxaRetencao: 72.5,
      nps: 8.4,
      clientesPorRegiao: [
        { regiao: 'Centro', quantidade: 45 },
        { regiao: 'Norte', quantidade: 32 },
        { regiao: 'Sul', quantidade: 28 },
        { regiao: 'Leste', quantidade: 18 },
      ],
      avaliacoes: [
        { nota: 5, quantidade: 89 },
        { nota: 4, quantidade: 34 },
        { nota: 3, quantidade: 12 },
        { nota: 2, quantidade: 3 },
        { nota: 1, quantidade: 1 },
      ],
    },
    estoque: {
      valorTotal: 89450.30,
      itensEmFalta: 7,
      giroEstoque: 4.2,
      margemLucro: 32.5,
      itensMaisVendidos: [
        { item: 'Memória RAM 8GB', quantidade: 45, valor: 6750 },
        { item: 'SSD 240GB', quantidade: 38, valor: 5700 },
        { item: 'Fonte 500W', quantidade: 32, valor: 3200 },
      ],
      movimentacoes: [],
    },
  });

  const { charts } = useCharts({
    dateRange: filtros.periodo,
    autoRefresh: false,
  });

  useEffect(() => {
    carregarDados();
  }, [filtros]);

  const carregarDados = async () => {
    setIsLoading(true);
    try {
      // Simular carregamento de dados
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Gerar dados de receita por dia
      const receitaPorDia = [];
      const diasPeriodo = Math.ceil((filtros.periodo.fim.getTime() - filtros.periodo.inicio.getTime()) / (1000 * 60 * 60 * 24));
      
      for (let i = 0; i < diasPeriodo; i++) {
        const data = new Date(filtros.periodo.inicio);
        data.setDate(data.getDate() + i);
        receitaPorDia.push({
          data: format(data, 'dd/MM'),
          valor: Math.random() * 2000 + 500,
        });
      }
      
      // Gerar dados de movimentação de estoque
      const movimentacoes = [];
      for (let i = 0; i < diasPeriodo; i++) {
        const data = new Date(filtros.periodo.inicio);
        data.setDate(data.getDate() + i);
        movimentacoes.push({
          data: format(data, 'dd/MM'),
          entrada: Math.floor(Math.random() * 20),
          saida: Math.floor(Math.random() * 15),
        });
      }
      
      setDados(prev => ({
        ...prev,
        financeiro: {
          ...prev.financeiro,
          receitaPorDia,
        },
        estoque: {
          ...prev.estoque,
          movimentacoes,
        },
      }));
    } catch (error) {
      addNotification({
        type: 'error',
        title: 'Erro ao carregar dados',
        message: 'Não foi possível carregar os dados do relatório.',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const aplicarFiltros = () => {
    carregarDados();
    addNotification({
      type: 'success',
      title: 'Filtros aplicados',
      message: 'Os relatórios foram atualizados com os novos filtros.',
    });
  };

  const exportarRelatorio = (formato: string) => {
    addNotification({
      type: 'info',
      title: 'Exportação iniciada',
      message: `O relatório será gerado em formato ${formato.toUpperCase()} e enviado por email.`,
    });
  };

  const compartilharRelatorio = () => {
    addNotification({
      type: 'info',
      title: 'Link gerado',
      message: 'Link de compartilhamento copiado para a área de transferência.',
    });
  };

  const agendarRelatorio = () => {
    addNotification({
      type: 'success',
      title: 'Relatório agendado',
      message: 'O relatório será enviado automaticamente conforme configurado.',
    });
  };

  const setPeriodoPreset = (preset: string) => {
    const config = PERIODOS_PRESET.find(p => p.value === preset);
    if (config) {
      setFiltros({
        ...filtros,
        periodo: {
          inicio: subDays(new Date(), config.dias),
          fim: new Date(),
        },
      });
    }
  };

  return (
    <MainLayout>
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Relatórios</h1>
            <p className="text-muted-foreground">
              Análises detalhadas e insights do seu negócio
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={compartilharRelatorio}>
              <Share className="h-4 w-4 mr-2" />
              Compartilhar
            </Button>
            <Select onValueChange={exportarRelatorio}>
              <SelectTrigger className="w-32">
                <Download className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Exportar" />
              </SelectTrigger>
              <SelectContent>
                {FORMATOS_EXPORT.map((formato) => (
                  <SelectItem key={formato.value} value={formato.value}>
                    <div className="flex items-center gap-2">
                      <formato.icon className="h-4 w-4" />
                      {formato.label}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Filtros */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Filtros
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <Label>Período</Label>
                <div className="flex gap-2">
                  {PERIODOS_PRESET.map((preset) => (
                    <Button
                      key={preset.value}
                      variant="outline"
                      size="sm"
                      onClick={() => setPeriodoPreset(preset.value)}
                      className="text-xs"
                    >
                      {preset.label}
                    </Button>
                  ))}
                </div>
                <DateRangePicker
                  value={filtros.periodo}
                  onChange={(periodo) => setFiltros({ ...filtros, periodo })}
                />
              </div>
              
              <div className="space-y-2">
                <Label>Tipo de Relatório</Label>
                <Select
                  value={filtros.tipo}
                  onValueChange={(value: any) => setFiltros({ ...filtros, tipo: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {TIPOS_RELATORIO.map((tipo) => (
                      <SelectItem key={tipo.value} value={tipo.value}>
                        <div className="flex items-center gap-2">
                          <tipo.icon className="h-4 w-4" />
                          {tipo.label}
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label>Loja</Label>
                <Select
                  value={filtros.loja}
                  onValueChange={(value) => setFiltros({ ...filtros, loja: value })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Todas as lojas" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="centro">Loja Centro</SelectItem>
                    <SelectItem value="norte">Loja Norte</SelectItem>
                    <SelectItem value="sul">Loja Sul</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex items-end">
                <Button onClick={aplicarFiltros} disabled={isLoading}>
                  {isLoading ? 'Carregando...' : 'Aplicar Filtros'}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="dashboard" className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Dashboard
            </TabsTrigger>
            <TabsTrigger value="financeiro" className="flex items-center gap-2">
              <DollarSign className="h-4 w-4" />
              Financeiro
            </TabsTrigger>
            <TabsTrigger value="operacional" className="flex items-center gap-2">
              <Wrench className="h-4 w-4" />
              Operacional
            </TabsTrigger>
            <TabsTrigger value="clientes" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              Clientes
            </TabsTrigger>
            <TabsTrigger value="estoque" className="flex items-center gap-2">
              <Package className="h-4 w-4" />
              Estoque
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Geral */}
          <TabsContent value="dashboard" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Receita Total"
                value={dados.financeiro.receita}
                format="currency"
                trend={12.5}
                icon={DollarSign}
                description="Últimos 30 dias"
              />
              <MetricCard
                title="OS Concluídas"
                value={dados.operacional.osConcluidas}
                format="number"
                trend={8.2}
                icon={Wrench}
                description="Últimos 30 dias"
              />
              <MetricCard
                title="Novos Clientes"
                value={dados.clientes.novosClientes}
                format="number"
                trend={15.3}
                icon={Users}
                description="Últimos 30 dias"
              />
              <MetricCard
                title="Valor Estoque"
                value={dados.estoque.valorTotal}
                format="currency"
                trend={-2.1}
                icon={Package}
                description="Valor atual"
              />
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ChartContainer
                title="Receita por Dia"
                type="line"
                data={{
                  labels: dados.financeiro.receitaPorDia.map(d => d.data),
                  datasets: [{
                    label: 'Receita',
                    data: dados.financeiro.receitaPorDia.map(d => d.valor),
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                  }],
                }}
              />
              
              <ChartContainer
                title="Status das OS"
                type="doughnut"
                data={{
                  labels: dados.operacional.statusOS.map(s => s.status),
                  datasets: [{
                    data: dados.operacional.statusOS.map(s => s.quantidade),
                    backgroundColor: [
                      '#3b82f6',
                      '#10b981',
                      '#f59e0b',
                      '#ef4444',
                    ],
                  }],
                }}
              />
            </div>
          </TabsContent>

          {/* Relatório Financeiro */}
          <TabsContent value="financeiro" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard
                title="Receita Total"
                value={dados.financeiro.receita}
                format="currency"
                trend={12.5}
                icon={DollarSign}
              />
              <MetricCard
                title="Lucro Líquido"
                value={dados.financeiro.lucro}
                format="currency"
                trend={18.3}
                icon={TrendingUp}
              />
              <MetricCard
                title="Ticket Médio"
                value={dados.financeiro.ticketMedio}
                format="currency"
                trend={5.7}
                icon={Target}
              />
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ChartContainer
                title="Receita por Dia"
                type="line"
                data={{
                  labels: dados.financeiro.receitaPorDia.map(d => d.data),
                  datasets: [{
                    label: 'Receita',
                    data: dados.financeiro.receitaPorDia.map(d => d.valor),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                  }],
                }}
              />
              
              <ChartContainer
                title="Receita por Categoria"
                type="pie"
                data={{
                  labels: dados.financeiro.receitaPorCategoria.map(c => c.categoria),
                  datasets: [{
                    data: dados.financeiro.receitaPorCategoria.map(c => c.valor),
                    backgroundColor: [
                      '#3b82f6',
                      '#10b981',
                      '#f59e0b',
                    ],
                  }],
                }}
              />
            </div>
            
            <Card>
              <CardHeader>
                <CardTitle>Detalhamento Financeiro</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {dados.financeiro.receitaPorCategoria.map((categoria, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                      <div>
                        <h4 className="font-medium">{categoria.categoria}</h4>
                        <p className="text-sm text-muted-foreground">
                          {((categoria.valor / dados.financeiro.receita) * 100).toFixed(1)}% da receita total
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold text-lg">
                          {new Intl.NumberFormat('pt-BR', {
                            style: 'currency',
                            currency: 'BRL',
                          }).format(categoria.valor)}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Relatório Operacional */}
          <TabsContent value="operacional" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <MetricCard
                title="OS Abertas"
                value={dados.operacional.osAbertas}
                format="number"
                trend={-5.2}
                icon={Clock}
              />
              <MetricCard
                title="OS Concluídas"
                value={dados.operacional.osConcluidas}
                format="number"
                trend={8.2}
                icon={Wrench}
              />
              <MetricCard
                title="Tempo Médio"
                value={dados.operacional.tempoMedioReparo}
                format="decimal"
                suffix=" dias"
                trend={-12.1}
                icon={Clock}
              />
              <MetricCard
                title="Satisfação"
                value={dados.operacional.satisfacaoCliente}
                format="decimal"
                suffix="/5"
                trend={3.4}
                icon={Target}
              />
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Produtividade dos Técnicos</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {dados.operacional.produtividadeTecnicos.map((tecnico, index) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <h4 className="font-medium">{tecnico.tecnico}</h4>
                          <p className="text-sm text-muted-foreground">
                            Tempo médio: {tecnico.tempo} dias
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-lg">{tecnico.os} OS</p>
                          <Badge variant={tecnico.os > 40 ? 'default' : 'secondary'}>
                            {tecnico.os > 40 ? 'Alto' : 'Médio'}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
              
              <ChartContainer
                title="Status das Ordens de Serviço"
                type="bar"
                data={{
                  labels: dados.operacional.statusOS.map(s => s.status),
                  datasets: [{
                    label: 'Quantidade',
                    data: dados.operacional.statusOS.map(s => s.quantidade),
                    backgroundColor: '#3b82f6',
                  }],
                }}
              />
            </div>
          </TabsContent>

          {/* Relatório de Clientes */}
          <TabsContent value="clientes" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <MetricCard
                title="Novos Clientes"
                value={dados.clientes.novosClientes}
                format="number"
                trend={15.3}
                icon={Users}
              />
              <MetricCard
                title="Recorrentes"
                value={dados.clientes.clientesRecorrentes}
                format="number"
                trend={8.7}
                icon={Users}
              />
              <MetricCard
                title="Taxa Retenção"
                value={dados.clientes.taxaRetencao}
                format="percentage"
                trend={2.1}
                icon={Target}
              />
              <MetricCard
                title="NPS"
                value={dados.clientes.nps}
                format="decimal"
                suffix="/10"
                trend={5.2}
                icon={TrendingUp}
              />
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ChartContainer
                title="Clientes por Região"
                type="bar"
                data={{
                  labels: dados.clientes.clientesPorRegiao.map(r => r.regiao),
                  datasets: [{
                    label: 'Clientes',
                    data: dados.clientes.clientesPorRegiao.map(r => r.quantidade),
                    backgroundColor: '#10b981',
                  }],
                }}
              />
              
              <ChartContainer
                title="Distribuição de Avaliações"
                type="bar"
                data={{
                  labels: dados.clientes.avaliacoes.map(a => `${a.nota} estrelas`),
                  datasets: [{
                    label: 'Avaliações',
                    data: dados.clientes.avaliacoes.map(a => a.quantidade),
                    backgroundColor: [
                      '#ef4444',
                      '#f59e0b',
                      '#eab308',
                      '#22c55e',
                      '#10b981',
                    ],
                  }],
                }}
              />
            </div>
          </TabsContent>

          {/* Relatório de Estoque */}
          <TabsContent value="estoque" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <MetricCard
                title="Valor Total"
                value={dados.estoque.valorTotal}
                format="currency"
                trend={-2.1}
                icon={Package}
              />
              <MetricCard
                title="Itens em Falta"
                value={dados.estoque.itensEmFalta}
                format="number"
                trend={-15.3}
                icon={Package}
              />
              <MetricCard
                title="Giro do Estoque"
                value={dados.estoque.giroEstoque}
                format="decimal"
                suffix="x"
                trend={8.2}
                icon={TrendingUp}
              />
              <MetricCard
                title="Margem Lucro"
                value={dados.estoque.margemLucro}
                format="percentage"
                trend={3.1}
                icon={DollarSign}
              />
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Itens Mais Vendidos</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {dados.estoque.itensMaisVendidos.map((item, index) => (
                      <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <h4 className="font-medium">{item.item}</h4>
                          <p className="text-sm text-muted-foreground">
                            {item.quantidade} unidades vendidas
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-lg">
                            {new Intl.NumberFormat('pt-BR', {
                              style: 'currency',
                              currency: 'BRL',
                            }).format(item.valor)}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
              
              <ChartContainer
                title="Movimentação de Estoque"
                type="line"
                data={{
                  labels: dados.estoque.movimentacoes.map(m => m.data),
                  datasets: [
                    {
                      label: 'Entrada',
                      data: dados.estoque.movimentacoes.map(m => m.entrada),
                      borderColor: '#10b981',
                      backgroundColor: 'rgba(16, 185, 129, 0.1)',
                      tension: 0.4,
                    },
                    {
                      label: 'Saída',
                      data: dados.estoque.movimentacoes.map(m => m.saida),
                      borderColor: '#ef4444',
                      backgroundColor: 'rgba(239, 68, 68, 0.1)',
                      tension: 0.4,
                    },
                  ],
                }}
              />
            </div>
          </TabsContent>
        </Tabs>

        {/* Ações Rápidas */}
        <Card>
          <CardHeader>
            <CardTitle>Ações Rápidas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              <Button variant="outline" onClick={() => exportarRelatorio('pdf')}>
                <Printer className="h-4 w-4 mr-2" />
                Imprimir Relatório
              </Button>
              <Button variant="outline" onClick={agendarRelatorio}>
                <Calendar className="h-4 w-4 mr-2" />
                Agendar Envio
              </Button>
              <Button variant="outline" onClick={() => exportarRelatorio('email')}>
                <Mail className="h-4 w-4 mr-2" />
                Enviar por Email
              </Button>
              <Button variant="outline">
                <Settings className="h-4 w-4 mr-2" />
                Configurar Relatório
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </MainLayout>
  );
}