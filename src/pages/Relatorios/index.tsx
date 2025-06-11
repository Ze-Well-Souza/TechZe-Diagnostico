import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { DateRangePicker } from '@/components/dashboard/DateRangePicker';
import { ChartContainer } from '@/components/dashboard/ChartContainer';
import { 
  FileText, 
  Download, 
  Filter, 
  Calendar, 
  TrendingUp, 
  TrendingDown,
  DollarSign,
  Users,
  Package,
  Wrench,
  BarChart3,
  PieChart,
  LineChart,
  RefreshCw,
  Eye,
  Printer,
  Mail,
  Share2
} from 'lucide-react';
import { useRelatorios } from '@/hooks/useRelatorios';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface FiltroRelatorio {
  dataInicio: Date;
  dataFim: Date;
  tipoRelatorio: string;
  categoria: string;
  status: string;
  cliente?: string;
  tecnico?: string;
}

interface DadosRelatorio {
  id: string;
  titulo: string;
  tipo: string;
  dados: any[];
  metadados: {
    total: number;
    periodo: string;
    geradoEm: Date;
  };
}

const tiposRelatorio = [
  { value: 'financeiro', label: 'Financeiro', icon: DollarSign },
  { value: 'operacional', label: 'Operacional', icon: Wrench },
  { value: 'clientes', label: 'Clientes', icon: Users },
  { value: 'estoque', label: 'Estoque', icon: Package },
  { value: 'performance', label: 'Performance', icon: TrendingUp }
];

const categoriasFinanceiro = [
  { value: 'receitas', label: 'Receitas' },
  { value: 'despesas', label: 'Despesas' },
  { value: 'lucro', label: 'Lucro/Prejuízo' },
  { value: 'fluxo-caixa', label: 'Fluxo de Caixa' }
];

const categoriasOperacional = [
  { value: 'os-status', label: 'Status das OS' },
  { value: 'tempo-medio', label: 'Tempo Médio de Reparo' },
  { value: 'produtividade', label: 'Produtividade por Técnico' },
  { value: 'tipos-servico', label: 'Tipos de Serviço' }
];

const statusOptions = [
  { value: 'todos', label: 'Todos' },
  { value: 'ativo', label: 'Ativo' },
  { value: 'concluido', label: 'Concluído' },
  { value: 'cancelado', label: 'Cancelado' }
];

const formatosExportacao = [
  { value: 'pdf', label: 'PDF', icon: FileText },
  { value: 'excel', label: 'Excel', icon: Download },
  { value: 'csv', label: 'CSV', icon: Download }
];

export default function Relatorios() {
  const [filtros, setFiltros] = useState<FiltroRelatorio>({
    dataInicio: new Date(new Date().getFullYear(), new Date().getMonth(), 1),
    dataFim: new Date(),
    tipoRelatorio: 'financeiro',
    categoria: 'receitas',
    status: 'todos'
  });

  const [relatorioAtual, setRelatorioAtual] = useState<DadosRelatorio | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [formatoExportacao, setFormatoExportacao] = useState('pdf');

  const {
    gerarRelatorio,
    exportarRelatorio,
    obterDadosGraficos,
    obterResumoExecutivo,
    salvarRelatorio,
    carregandoRelatorios
  } = useRelatorios();

  const handleFiltroChange = (campo: keyof FiltroRelatorio, valor: any) => {
    setFiltros(prev => ({
      ...prev,
      [campo]: valor
    }));
  };

  const handleGerarRelatorio = async () => {
    setCarregando(true);
    try {
      const dados = await gerarRelatorio(filtros);
      setRelatorioAtual(dados);
    } catch (error) {
      console.error('Erro ao gerar relatório:', error);
    } finally {
      setCarregando(false);
    }
  };

  const handleExportar = async () => {
    if (!relatorioAtual) return;
    
    try {
      await exportarRelatorio(relatorioAtual, formatoExportacao);
    } catch (error) {
      console.error('Erro ao exportar relatório:', error);
    }
  };

  const getCategoriasPorTipo = (tipo: string) => {
    switch (tipo) {
      case 'financeiro':
        return categoriasFinanceiro;
      case 'operacional':
        return categoriasOperacional;
      default:
        return [];
    }
  };

  const renderGraficos = () => {
    if (!relatorioAtual) return null;

    const dadosGraficos = obterDadosGraficos(relatorioAtual);

    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {dadosGraficos.map((grafico, index) => (
          <ChartContainer
            key={index}
            title={grafico.titulo}
            type={grafico.tipo}
            data={grafico.dados}
            options={grafico.opcoes}
          />
        ))}
      </div>
    );
  };

  const renderResumoExecutivo = () => {
    if (!relatorioAtual) return null;

    const resumo = obterResumoExecutivo(relatorioAtual);

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {resumo.metricas.map((metrica, index) => (
          <Card key={index}>
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {metrica.label}
                  </p>
                  <p className="text-2xl font-bold">{metrica.valor}</p>
                  {metrica.variacao && (
                    <div className="flex items-center mt-1">
                      {metrica.variacao > 0 ? (
                        <TrendingUp className="h-4 w-4 text-green-500 mr-1" />
                      ) : (
                        <TrendingDown className="h-4 w-4 text-red-500 mr-1" />
                      )}
                      <span className={`text-sm ${
                        metrica.variacao > 0 ? 'text-green-500' : 'text-red-500'
                      }`}>
                        {Math.abs(metrica.variacao)}%
                      </span>
                    </div>
                  )}
                </div>
                <metrica.icon className="h-8 w-8 text-muted-foreground" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  };

  const renderTabelaDados = () => {
    if (!relatorioAtual || !relatorioAtual.dados.length) return null;

    const colunas = Object.keys(relatorioAtual.dados[0]);

    return (
      <Card>
        <CardHeader>
          <CardTitle>Dados Detalhados</CardTitle>
          <CardDescription>
            {relatorioAtual.dados.length} registros encontrados
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  {colunas.map(coluna => (
                    <th key={coluna} className="text-left p-2 font-medium">
                      {coluna.charAt(0).toUpperCase() + coluna.slice(1)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {relatorioAtual.dados.map((linha, index) => (
                  <tr key={index} className="border-b hover:bg-muted/50">
                    {colunas.map(coluna => (
                      <td key={coluna} className="p-2">
                        {linha[coluna]}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Relatórios</h1>
          <p className="text-muted-foreground">
            Gere relatórios detalhados e análises do seu negócio
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => window.location.reload()}
            disabled={carregando}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Filtros */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filtros do Relatório
          </CardTitle>
          <CardDescription>
            Configure os parâmetros para gerar seu relatório personalizado
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Período */}
            <div className="space-y-2">
              <Label>Período</Label>
              <DateRangePicker
                from={filtros.dataInicio}
                to={filtros.dataFim}
                onSelect={(range) => {
                  if (range?.from) handleFiltroChange('dataInicio', range.from);
                  if (range?.to) handleFiltroChange('dataFim', range.to);
                }}
              />
            </div>

            {/* Tipo de Relatório */}
            <div className="space-y-2">
              <Label>Tipo de Relatório</Label>
              <Select
                value={filtros.tipoRelatorio}
                onValueChange={(value) => handleFiltroChange('tipoRelatorio', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {tiposRelatorio.map(tipo => (
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

            {/* Categoria */}
            <div className="space-y-2">
              <Label>Categoria</Label>
              <Select
                value={filtros.categoria}
                onValueChange={(value) => handleFiltroChange('categoria', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {getCategoriasPorTipo(filtros.tipoRelatorio).map(categoria => (
                    <SelectItem key={categoria.value} value={categoria.value}>
                      {categoria.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Status */}
            <div className="space-y-2">
              <Label>Status</Label>
              <Select
                value={filtros.status}
                onValueChange={(value) => handleFiltroChange('status', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {statusOptions.map(status => (
                    <SelectItem key={status.value} value={status.value}>
                      {status.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex items-center gap-2 pt-4">
            <Button
              onClick={handleGerarRelatorio}
              disabled={carregando}
              className="flex-1 md:flex-none"
            >
              {carregando ? (
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <BarChart3 className="h-4 w-4 mr-2" />
              )}
              Gerar Relatório
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Relatório Gerado */}
      {relatorioAtual && (
        <div className="space-y-6">
          {/* Cabeçalho do Relatório */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>{relatorioAtual.titulo}</CardTitle>
                  <CardDescription>
                    Período: {format(filtros.dataInicio, 'dd/MM/yyyy', { locale: ptBR })} - {format(filtros.dataFim, 'dd/MM/yyyy', { locale: ptBR })}
                    <br />
                    Gerado em: {format(relatorioAtual.metadados.geradoEm, 'dd/MM/yyyy HH:mm', { locale: ptBR })}
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Select
                    value={formatoExportacao}
                    onValueChange={setFormatoExportacao}
                  >
                    <SelectTrigger className="w-32">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {formatosExportacao.map(formato => (
                        <SelectItem key={formato.value} value={formato.value}>
                          <div className="flex items-center gap-2">
                            <formato.icon className="h-4 w-4" />
                            {formato.label}
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Button onClick={handleExportar} variant="outline">
                    <Download className="h-4 w-4 mr-2" />
                    Exportar
                  </Button>
                </div>
              </div>
            </CardHeader>
          </Card>

          {/* Resumo Executivo */}
          {renderResumoExecutivo()}

          {/* Gráficos */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="h-5 w-5" />
                Análise Visual
              </CardTitle>
            </CardHeader>
            <CardContent>
              {renderGraficos()}
            </CardContent>
          </Card>

          {/* Tabela de Dados */}
          {renderTabelaDados()}
        </div>
      )}

      {/* Estado Vazio */}
      {!relatorioAtual && !carregando && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <FileText className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Nenhum relatório gerado</h3>
            <p className="text-muted-foreground text-center mb-4">
              Configure os filtros acima e clique em "Gerar Relatório" para começar
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}