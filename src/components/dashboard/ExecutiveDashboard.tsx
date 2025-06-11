import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { cn } from '@/lib/utils';
import {
  RefreshCw,
  Download,
  Settings,
  TrendingUp,
  AlertCircle,
  Calendar,
  BarChart3,
  PieChart,
  Users,
  DollarSign,
} from 'lucide-react';
import { useCharts, DateRange } from '@/hooks/useCharts';
import { useNotifications } from '@/hooks/useNotifications';
import { MetricGrid, useFormattedMetrics } from './MetricCard';
import { ChartContainer, ChartGrid } from './ChartContainer';
import { DateRangePicker, QuickDateSelector } from './DateRangePicker';
import { subDays } from 'date-fns';

export interface ExecutiveDashboardProps {
  className?: string;
}

const DEFAULT_DATE_RANGE: DateRange = {
  start: subDays(new Date(), 30),
  end: new Date(),
};

export const ExecutiveDashboard: React.FC<ExecutiveDashboardProps> = ({
  className,
}) => {
  const [dateRange, setDateRange] = useState<DateRange>(DEFAULT_DATE_RANGE);
  const [activeTab, setActiveTab] = useState('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);
  
  const { addNotification } = useNotifications();
  
  const {
    metrics,
    charts,
    isLoading,
    error,
    refetch,
    updateDateRange,
  } = useCharts({
    dateRange,
    autoRefresh,
    refreshInterval: 5 * 60 * 1000, // 5 minutos
  });

  const formattedMetrics = useFormattedMetrics(metrics);

  const handleDateRangeChange = (newRange: DateRange) => {
    setDateRange(newRange);
    updateDateRange(newRange);
    
    addNotification({
      type: 'info',
      title: 'Período atualizado',
      message: 'Os dados do dashboard foram atualizados para o novo período.',
    });
  };

  const handleRefresh = () => {
    refetch();
    addNotification({
      type: 'success',
      title: 'Dashboard atualizado',
      message: 'Os dados foram atualizados com sucesso.',
    });
  };

  const handleExport = () => {
    // Implementar exportação de dados
    addNotification({
      type: 'info',
      title: 'Exportação iniciada',
      message: 'O relatório será gerado e enviado por email.',
    });
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
    addNotification({
      type: 'info',
      title: autoRefresh ? 'Auto-atualização desativada' : 'Auto-atualização ativada',
      message: autoRefresh 
        ? 'Os dados não serão mais atualizados automaticamente.' 
        : 'Os dados serão atualizados a cada 5 minutos.',
    });
  };

  // Alertas baseados nas métricas
  const getAlerts = () => {
    if (!metrics) return [];
    
    const alerts = [];
    
    if (metrics.taxaAprovacao < 50) {
      alerts.push({
        type: 'error' as const,
        title: 'Taxa de aprovação baixa',
        message: `Taxa atual: ${metrics.taxaAprovacao.toFixed(1)}%`,
      });
    }
    
    if (metrics.osAbertas > 20) {
      alerts.push({
        type: 'warning' as const,
        title: 'Muitas OS abertas',
        message: `${metrics.osAbertas} ordens de serviço pendentes`,
      });
    }
    
    if (metrics.estoqueAlerta > 10) {
      alerts.push({
        type: 'warning' as const,
        title: 'Estoque baixo',
        message: `${metrics.estoqueAlerta} itens com estoque baixo`,
      });
    }
    
    if (metrics.tempoMedioReparo > 7) {
      alerts.push({
        type: 'error' as const,
        title: 'Tempo de reparo alto',
        message: `Média atual: ${metrics.tempoMedioReparo.toFixed(1)} dias`,
      });
    }
    
    return alerts;
  };

  const alerts = getAlerts();

  if (error) {
    return (
      <div className={cn('p-6', className)}>
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 text-red-600">
              <AlertCircle className="h-5 w-5" />
              <span className="font-medium">Erro ao carregar dashboard</span>
            </div>
            <p className="text-sm text-red-500 mt-2">
              {error.message || 'Ocorreu um erro inesperado'}
            </p>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              className="mt-4"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Tentar novamente
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={cn('space-y-6 p-6', className)}>
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Dashboard Executivo
          </h1>
          <p className="text-gray-600 mt-1">
            Visão geral do desempenho da empresa
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
          <DateRangePicker
            value={dateRange}
            onChange={handleDateRangeChange}
            disabled={isLoading}
          />
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={toggleAutoRefresh}
              className={cn(
                autoRefresh && 'bg-green-50 border-green-200 text-green-700'
              )}
            >
              <RefreshCw className={cn(
                'h-4 w-4 mr-2',
                autoRefresh && 'text-green-600'
              )} />
              Auto-refresh
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={isLoading}
            >
              <RefreshCw className={cn(
                'h-4 w-4 mr-2',
                isLoading && 'animate-spin'
              )} />
              Atualizar
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={handleExport}
            >
              <Download className="h-4 w-4 mr-2" />
              Exportar
            </Button>
          </div>
        </div>
      </div>

      {/* Alertas */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          {alerts.map((alert, index) => (
            <Card 
              key={index}
              className={cn(
                'border-l-4',
                alert.type === 'error' && 'border-l-red-500 bg-red-50',
                alert.type === 'warning' && 'border-l-yellow-500 bg-yellow-50'
              )}
            >
              <CardContent className="pt-4">
                <div className="flex items-center space-x-2">
                  <AlertCircle className={cn(
                    'h-4 w-4',
                    alert.type === 'error' && 'text-red-500',
                    alert.type === 'warning' && 'text-yellow-500'
                  )} />
                  <span className="font-medium">{alert.title}</span>
                  <Badge variant="secondary">{alert.message}</Badge>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Conteúdo principal */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>Visão Geral</span>
          </TabsTrigger>
          <TabsTrigger value="financial" className="flex items-center space-x-2">
            <DollarSign className="h-4 w-4" />
            <span>Financeiro</span>
          </TabsTrigger>
          <TabsTrigger value="operations" className="flex items-center space-x-2">
            <Settings className="h-4 w-4" />
            <span>Operações</span>
          </TabsTrigger>
          <TabsTrigger value="customers" className="flex items-center space-x-2">
            <Users className="h-4 w-4" />
            <span>Clientes</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Métricas principais */}
          <MetricGrid
            metrics={formattedMetrics}
            loading={isLoading}
            columns={4}
          />
          
          {/* Gráficos principais */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ChartContainer
              config={charts.faturamento}
              loading={isLoading}
              onRefresh={handleRefresh}
              height={350}
            />
            
            <ChartContainer
              config={charts.orcamentos}
              loading={isLoading}
              onRefresh={handleRefresh}
              height={350}
            />
          </div>
        </TabsContent>

        <TabsContent value="financial" className="space-y-6">
          {/* Métricas financeiras */}
          <MetricGrid
            metrics={formattedMetrics.filter(m => 
              ['Faturamento Mensal', 'Ticket Médio', 'Taxa de Aprovação'].includes(m.title)
            )}
            loading={isLoading}
            columns={3}
          />
          
          {/* Gráficos financeiros */}
          <ChartContainer
            config={charts.faturamento}
            loading={isLoading}
            onRefresh={handleRefresh}
            height={400}
          />
        </TabsContent>

        <TabsContent value="operations" className="space-y-6">
          {/* Métricas operacionais */}
          <MetricGrid
            metrics={formattedMetrics.filter(m => 
              ['OS Abertas', 'Tempo Médio Reparo', 'Estoque em Alerta'].includes(m.title)
            )}
            loading={isLoading}
            columns={3}
          />
          
          {/* Gráficos operacionais */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ChartContainer
              config={charts.ordemServico}
              loading={isLoading}
              onRefresh={handleRefresh}
              height={350}
            />
            
            <ChartContainer
              config={charts.estoque}
              loading={isLoading}
              onRefresh={handleRefresh}
              height={350}
            />
          </div>
        </TabsContent>

        <TabsContent value="customers" className="space-y-6">
          {/* Métricas de clientes */}
          <MetricGrid
            metrics={formattedMetrics.filter(m => 
              ['Satisfação Cliente'].includes(m.title)
            )}
            loading={isLoading}
            columns={1}
          />
          
          {/* Gráfico de satisfação */}
          <ChartContainer
            config={charts.satisfacao}
            loading={isLoading}
            onRefresh={handleRefresh}
            height={400}
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};