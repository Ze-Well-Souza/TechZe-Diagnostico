import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler,
} from 'chart.js';
import {
  Line,
  Bar,
  Doughnut,
  Pie,
} from 'react-chartjs-2';
import { 
  Download, 
  Maximize2, 
  RefreshCw,
  TrendingUp,
  TrendingDown,
  BarChart3,
  PieChart,
  LineChart,
} from 'lucide-react';
import { ChartConfig, ChartDataPoint } from '@/hooks/useCharts';

// Registrar componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
);

export interface ChartContainerProps {
  config: ChartConfig;
  loading?: boolean;
  error?: string | null;
  className?: string;
  showHeader?: boolean;
  showActions?: boolean;
  onRefresh?: () => void;
  onDownload?: () => void;
  onExpand?: () => void;
  height?: number;
}

const chartTypeIcons = {
  line: LineChart,
  bar: BarChart3,
  pie: PieChart,
  doughnut: PieChart,
  area: LineChart,
};

const defaultColors = [
  '#3b82f6', // blue
  '#10b981', // green
  '#f59e0b', // yellow
  '#ef4444', // red
  '#8b5cf6', // purple
  '#06b6d4', // cyan
  '#f97316', // orange
  '#84cc16', // lime
];

export const ChartContainer: React.FC<ChartContainerProps> = ({
  config,
  loading = false,
  error = null,
  className,
  showHeader = true,
  showActions = true,
  onRefresh,
  onDownload,
  onExpand,
  height = 300,
}) => {
  const IconComponent = chartTypeIcons[config.type];

  // Preparar dados para o gráfico
  const chartData = useMemo(() => {
    if (!config.data || config.data.length === 0) {
      return {
        labels: [],
        datasets: [],
      };
    }

    const labels = config.data.map(item => item.label);
    const values = config.data.map(item => item.value);
    const colors = config.data.map((item, index) => 
      item.color || defaultColors[index % defaultColors.length]
    );

    if (config.type === 'pie' || config.type === 'doughnut') {
      return {
        labels,
        datasets: [
          {
            data: values,
            backgroundColor: colors,
            borderColor: colors.map(color => color),
            borderWidth: 2,
          },
        ],
      };
    }

    return {
      labels,
      datasets: [
        {
          label: config.title,
          data: values,
          backgroundColor: config.type === 'area' 
            ? colors[0] + '20' // Transparência para área
            : colors,
          borderColor: colors[0],
          borderWidth: 2,
          fill: config.type === 'area',
          tension: config.type === 'line' || config.type === 'area' ? 0.4 : 0,
        },
      ],
    };
  }, [config]);

  // Opções padrão do gráfico
  const defaultOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 20,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleColor: 'white',
        bodyColor: 'white',
        borderColor: 'rgba(255, 255, 255, 0.1)',
        borderWidth: 1,
        cornerRadius: 8,
        displayColors: true,
        callbacks: {
          label: (context: any) => {
            const label = context.dataset.label || '';
            const value = context.parsed.y || context.parsed;
            
            // Formatação específica baseada no tipo de dados
            if (config.title.toLowerCase().includes('faturamento')) {
              return `${label}: ${new Intl.NumberFormat('pt-BR', {
                style: 'currency',
                currency: 'BRL',
              }).format(value)}`;
            }
            
            if (config.title.toLowerCase().includes('satisfação')) {
              return `${label}: ${value.toFixed(1)}/5`;
            }
            
            return `${label}: ${value.toLocaleString('pt-BR')}`;
          },
        },
      },
    },
    scales: config.type !== 'pie' && config.type !== 'doughnut' ? {
      x: {
        grid: {
          display: false,
        },
      },
      y: {
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
        beginAtZero: true,
      },
    } : undefined,
  };

  // Mesclar opções personalizadas
  const mergedOptions = {
    ...defaultOptions,
    ...config.options,
  };

  const renderChart = () => {
    if (loading) {
      return (
        <div 
          className="flex items-center justify-center bg-gray-50 rounded-lg"
          style={{ height }}
        >
          <div className="flex flex-col items-center space-y-2">
            <RefreshCw className="h-8 w-8 text-gray-400 animate-spin" />
            <span className="text-sm text-gray-500">Carregando gráfico...</span>
          </div>
        </div>
      );
    }

    if (error) {
      return (
        <div 
          className="flex items-center justify-center bg-red-50 rounded-lg border border-red-200"
          style={{ height }}
        >
          <div className="flex flex-col items-center space-y-2 text-center p-4">
            <div className="h-8 w-8 text-red-400">
              ⚠️
            </div>
            <span className="text-sm text-red-600 font-medium">Erro ao carregar gráfico</span>
            <span className="text-xs text-red-500">{error}</span>
            {onRefresh && (
              <Button
                variant="outline"
                size="sm"
                onClick={onRefresh}
                className="mt-2"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Tentar novamente
              </Button>
            )}
          </div>
        </div>
      );
    }

    if (!config.data || config.data.length === 0) {
      return (
        <div 
          className="flex items-center justify-center bg-gray-50 rounded-lg"
          style={{ height }}
        >
          <div className="flex flex-col items-center space-y-2 text-center p-4">
            <IconComponent className="h-8 w-8 text-gray-400" />
            <span className="text-sm text-gray-500">Nenhum dado disponível</span>
            <span className="text-xs text-gray-400">Os dados serão exibidos quando disponíveis</span>
          </div>
        </div>
      );
    }

    const chartProps = {
      data: chartData,
      options: mergedOptions,
      height,
    };

    switch (config.type) {
      case 'line':
      case 'area':
        return <Line {...chartProps} />;
      case 'bar':
        return <Bar {...chartProps} />;
      case 'pie':
        return <Pie {...chartProps} />;
      case 'doughnut':
        return <Doughnut {...chartProps} />;
      default:
        return <Line {...chartProps} />;
    }
  };

  // Calcular estatísticas do gráfico
  const stats = useMemo(() => {
    if (!config.data || config.data.length === 0) return null;

    const values = config.data.map(item => item.value);
    const total = values.reduce((sum, val) => sum + val, 0);
    const max = Math.max(...values);
    const min = Math.min(...values);
    const avg = total / values.length;

    return { total, max, min, avg };
  }, [config.data]);

  return (
    <Card className={cn('w-full', className)}>
      {showHeader && (
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
          <div className="flex items-center space-x-2">
            <IconComponent className="h-5 w-5 text-gray-600" />
            <CardTitle className="text-lg font-semibold">
              {config.title}
            </CardTitle>
            {stats && (
              <Badge variant="secondary" className="ml-2">
                {config.data?.length || 0} itens
              </Badge>
            )}
          </div>
          
          {showActions && (
            <div className="flex items-center space-x-2">
              {onRefresh && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onRefresh}
                  disabled={loading}
                >
                  <RefreshCw className={cn('h-4 w-4', loading && 'animate-spin')} />
                </Button>
              )}
              
              {onDownload && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onDownload}
                >
                  <Download className="h-4 w-4" />
                </Button>
              )}
              
              {onExpand && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onExpand}
                >
                  <Maximize2 className="h-4 w-4" />
                </Button>
              )}
            </div>
          )}
        </CardHeader>
      )}
      
      <CardContent>
        <div style={{ height }}>
          {renderChart()}
        </div>
        
        {stats && !loading && !error && (
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
            <div className="text-center">
              <div className="text-sm text-gray-500">Total</div>
              <div className="text-lg font-semibold">
                {stats.total.toLocaleString('pt-BR')}
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-500">Máximo</div>
              <div className="text-lg font-semibold text-green-600">
                {stats.max.toLocaleString('pt-BR')}
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-500">Mínimo</div>
              <div className="text-lg font-semibold text-red-600">
                {stats.min.toLocaleString('pt-BR')}
              </div>
            </div>
            <div className="text-center">
              <div className="text-sm text-gray-500">Média</div>
              <div className="text-lg font-semibold text-blue-600">
                {stats.avg.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

// Componente para grid de gráficos
export interface ChartGridProps {
  charts: ChartConfig[];
  loading?: boolean;
  error?: string | null;
  columns?: 1 | 2;
  className?: string;
  onRefresh?: () => void;
}

export const ChartGrid: React.FC<ChartGridProps> = ({
  charts,
  loading = false,
  error = null,
  columns = 2,
  className,
  onRefresh,
}) => {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 lg:grid-cols-2',
  };

  return (
    <div className={cn('grid gap-6', gridCols[columns], className)}>
      {charts.map((chart, index) => (
        <ChartContainer
          key={`${chart.title}-${index}`}
          config={chart}
          loading={loading}
          error={error}
          onRefresh={onRefresh}
          height={350}
        />
      ))}
    </div>
  );
};