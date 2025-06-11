import { useState, useEffect, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { supabase } from '@/lib/supabase';
import { format, subDays, startOfDay, endOfDay } from 'date-fns';
import { ptBR } from 'date-fns/locale';

export interface ChartDataPoint {
  label: string;
  value: number;
  date?: Date;
  color?: string;
}

export interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'doughnut' | 'area';
  title: string;
  data: ChartDataPoint[];
  options?: any;
}

export interface DashboardMetrics {
  totalOrcamentos: number;
  orcamentosAprovados: number;
  taxaAprovacao: number;
  faturamentoMensal: number;
  ticketMedio: number;
  osAbertas: number;
  osConcluidas: number;
  tempoMedioReparo: number;
  satisfacaoCliente: number;
  estoqueAlerta: number;
}

export interface DateRange {
  start: Date;
  end: Date;
}

interface UseChartsOptions {
  dateRange?: DateRange;
  refreshInterval?: number;
  autoRefresh?: boolean;
}

interface UseChartsReturn {
  metrics: DashboardMetrics | null;
  charts: {
    faturamento: ChartConfig;
    orcamentos: ChartConfig;
    ordemServico: ChartConfig;
    satisfacao: ChartConfig;
    estoque: ChartConfig;
  };
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
  updateDateRange: (range: DateRange) => void;
}

const DEFAULT_DATE_RANGE: DateRange = {
  start: subDays(new Date(), 30),
  end: new Date(),
};

export const useCharts = (options: UseChartsOptions = {}): UseChartsReturn => {
  const {
    dateRange = DEFAULT_DATE_RANGE,
    refreshInterval = 5 * 60 * 1000, // 5 minutos
    autoRefresh = true,
  } = options;

  const [currentDateRange, setCurrentDateRange] = useState<DateRange>(dateRange);

  // Query para métricas gerais
  const {
    data: metricsData,
    isLoading: metricsLoading,
    error: metricsError,
    refetch: refetchMetrics,
  } = useQuery({
    queryKey: ['dashboard-metrics', currentDateRange],
    queryFn: () => fetchDashboardMetrics(currentDateRange),
    refetchInterval: autoRefresh ? refreshInterval : false,
    staleTime: 2 * 60 * 1000, // 2 minutos
  });

  // Query para dados de faturamento
  const {
    data: faturamentoData,
    isLoading: faturamentoLoading,
    refetch: refetchFaturamento,
  } = useQuery({
    queryKey: ['faturamento-chart', currentDateRange],
    queryFn: () => fetchFaturamentoData(currentDateRange),
    refetchInterval: autoRefresh ? refreshInterval : false,
  });

  // Query para dados de orçamentos
  const {
    data: orcamentosData,
    isLoading: orcamentosLoading,
    refetch: refetchOrcamentos,
  } = useQuery({
    queryKey: ['orcamentos-chart', currentDateRange],
    queryFn: () => fetchOrcamentosData(currentDateRange),
    refetchInterval: autoRefresh ? refreshInterval : false,
  });

  // Query para dados de ordem de serviço
  const {
    data: osData,
    isLoading: osLoading,
    refetch: refetchOS,
  } = useQuery({
    queryKey: ['os-chart', currentDateRange],
    queryFn: () => fetchOrdemServicoData(currentDateRange),
    refetchInterval: autoRefresh ? refreshInterval : false,
  });

  // Query para dados de satisfação
  const {
    data: satisfacaoData,
    isLoading: satisfacaoLoading,
    refetch: refetchSatisfacao,
  } = useQuery({
    queryKey: ['satisfacao-chart', currentDateRange],
    queryFn: () => fetchSatisfacaoData(currentDateRange),
    refetchInterval: autoRefresh ? refreshInterval : false,
  });

  // Query para dados de estoque
  const {
    data: estoqueData,
    isLoading: estoqueLoading,
    refetch: refetchEstoque,
  } = useQuery({
    queryKey: ['estoque-chart'],
    queryFn: fetchEstoqueData,
    refetchInterval: autoRefresh ? refreshInterval : false,
  });

  const isLoading = metricsLoading || faturamentoLoading || orcamentosLoading || osLoading || satisfacaoLoading || estoqueLoading;
  const error = metricsError || null;

  // Configurações dos gráficos
  const charts = useMemo(() => ({
    faturamento: {
      type: 'line' as const,
      title: 'Faturamento Mensal',
      data: faturamentoData || [],
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top' as const,
          },
          title: {
            display: true,
            text: 'Evolução do Faturamento',
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              callback: (value: any) => `R$ ${value.toLocaleString('pt-BR')}`,
            },
          },
        },
      },
    },
    orcamentos: {
      type: 'doughnut' as const,
      title: 'Status dos Orçamentos',
      data: orcamentosData || [],
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom' as const,
          },
        },
      },
    },
    ordemServico: {
      type: 'bar' as const,
      title: 'Ordens de Serviço',
      data: osData || [],
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top' as const,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    },
    satisfacao: {
      type: 'line' as const,
      title: 'Satisfação do Cliente',
      data: satisfacaoData || [],
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'top' as const,
          },
        },
        scales: {
          y: {
            min: 0,
            max: 5,
            ticks: {
              stepSize: 1,
            },
          },
        },
      },
    },
    estoque: {
      type: 'bar' as const,
      title: 'Status do Estoque',
      data: estoqueData || [],
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
          },
        },
      },
    },
  }), [faturamentoData, orcamentosData, osData, satisfacaoData, estoqueData]);

  const refetch = () => {
    refetchMetrics();
    refetchFaturamento();
    refetchOrcamentos();
    refetchOS();
    refetchSatisfacao();
    refetchEstoque();
  };

  const updateDateRange = (range: DateRange) => {
    setCurrentDateRange(range);
  };

  return {
    metrics: metricsData || null,
    charts,
    isLoading,
    error,
    refetch,
    updateDateRange,
  };
};

// Funções auxiliares para buscar dados
async function fetchDashboardMetrics(dateRange: DateRange): Promise<DashboardMetrics> {
  const { start, end } = dateRange;
  
  try {
    // Buscar dados de orçamentos
    const { data: orcamentos } = await supabase
      .from('orcamentos')
      .select('*')
      .gte('created_at', start.toISOString())
      .lte('created_at', end.toISOString());

    // Buscar dados de ordens de serviço
    const { data: ordemServico } = await supabase
      .from('ordem_servico')
      .select('*')
      .gte('created_at', start.toISOString())
      .lte('created_at', end.toISOString());

    // Buscar dados de estoque
    const { data: estoque } = await supabase
      .from('estoque')
      .select('*')
      .lt('quantidade', 10); // Itens com estoque baixo

    const totalOrcamentos = orcamentos?.length || 0;
    const orcamentosAprovados = orcamentos?.filter(o => o.status === 'aprovado').length || 0;
    const taxaAprovacao = totalOrcamentos > 0 ? (orcamentosAprovados / totalOrcamentos) * 100 : 0;
    
    const faturamentoMensal = orcamentos
      ?.filter(o => o.status === 'aprovado')
      .reduce((sum, o) => sum + (o.valor_total || 0), 0) || 0;
    
    const ticketMedio = orcamentosAprovados > 0 ? faturamentoMensal / orcamentosAprovados : 0;
    
    const osAbertas = ordemServico?.filter(os => ['aberta', 'em_andamento'].includes(os.status)).length || 0;
    const osConcluidas = ordemServico?.filter(os => os.status === 'concluida').length || 0;
    
    // Calcular tempo médio de reparo (em dias)
    const osComTempo = ordemServico?.filter(os => os.status === 'concluida' && os.data_conclusao) || [];
    const tempoMedioReparo = osComTempo.length > 0 
      ? osComTempo.reduce((sum, os) => {
          const inicio = new Date(os.created_at);
          const fim = new Date(os.data_conclusao);
          return sum + (fim.getTime() - inicio.getTime()) / (1000 * 60 * 60 * 24);
        }, 0) / osComTempo.length
      : 0;

    return {
      totalOrcamentos,
      orcamentosAprovados,
      taxaAprovacao,
      faturamentoMensal,
      ticketMedio,
      osAbertas,
      osConcluidas,
      tempoMedioReparo,
      satisfacaoCliente: 4.2, // Mock - implementar avaliações
      estoqueAlerta: estoque?.length || 0,
    };
  } catch (error) {
    console.error('Erro ao buscar métricas:', error);
    throw error;
  }
}

async function fetchFaturamentoData(dateRange: DateRange): Promise<ChartDataPoint[]> {
  // Implementar busca de dados de faturamento por período
  // Por enquanto, retornar dados mock
  return [
    { label: 'Jan', value: 15000 },
    { label: 'Fev', value: 18000 },
    { label: 'Mar', value: 22000 },
    { label: 'Abr', value: 19000 },
    { label: 'Mai', value: 25000 },
    { label: 'Jun', value: 28000 },
  ];
}

async function fetchOrcamentosData(dateRange: DateRange): Promise<ChartDataPoint[]> {
  try {
    const { data } = await supabase
      .from('orcamentos')
      .select('status')
      .gte('created_at', dateRange.start.toISOString())
      .lte('created_at', dateRange.end.toISOString());

    const statusCount = data?.reduce((acc, item) => {
      acc[item.status] = (acc[item.status] || 0) + 1;
      return acc;
    }, {} as Record<string, number>) || {};

    return [
      { label: 'Pendente', value: statusCount.pendente || 0, color: '#fbbf24' },
      { label: 'Aprovado', value: statusCount.aprovado || 0, color: '#10b981' },
      { label: 'Rejeitado', value: statusCount.rejeitado || 0, color: '#ef4444' },
    ];
  } catch (error) {
    console.error('Erro ao buscar dados de orçamentos:', error);
    return [];
  }
}

async function fetchOrdemServicoData(dateRange: DateRange): Promise<ChartDataPoint[]> {
  // Implementar busca de dados de OS
  return [
    { label: 'Abertas', value: 12, color: '#3b82f6' },
    { label: 'Em Andamento', value: 8, color: '#f59e0b' },
    { label: 'Concluídas', value: 25, color: '#10b981' },
  ];
}

async function fetchSatisfacaoData(dateRange: DateRange): Promise<ChartDataPoint[]> {
  // Implementar busca de dados de satisfação
  return [
    { label: 'Jan', value: 4.1 },
    { label: 'Fev', value: 4.3 },
    { label: 'Mar', value: 4.2 },
    { label: 'Abr', value: 4.5 },
    { label: 'Mai', value: 4.4 },
    { label: 'Jun', value: 4.6 },
  ];
}

async function fetchEstoqueData(): Promise<ChartDataPoint[]> {
  try {
    const { data } = await supabase
      .from('estoque')
      .select('nome, quantidade, estoque_minimo')
      .lt('quantidade', 20) // Itens com estoque baixo
      .limit(10);

    return data?.map(item => ({
      label: item.nome,
      value: item.quantidade,
      color: item.quantidade <= item.estoque_minimo ? '#ef4444' : '#f59e0b',
    })) || [];
  } catch (error) {
    console.error('Erro ao buscar dados de estoque:', error);
    return [];
  }
}