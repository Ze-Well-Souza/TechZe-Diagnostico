import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { 
  TrendingUp, 
  TrendingDown, 
  Minus,
  DollarSign,
  Users,
  ShoppingCart,
  Clock,
  Star,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';

export interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
    period?: string;
  };
  icon?: 'dollar' | 'users' | 'cart' | 'clock' | 'star' | 'alert' | 'check' | 'x';
  variant?: 'default' | 'success' | 'warning' | 'error';
  loading?: boolean;
  className?: string;
  onClick?: () => void;
}

const iconMap = {
  dollar: DollarSign,
  users: Users,
  cart: ShoppingCart,
  clock: Clock,
  star: Star,
  alert: AlertTriangle,
  check: CheckCircle,
  x: XCircle,
};

const variantStyles = {
  default: 'border-gray-200 bg-white',
  success: 'border-green-200 bg-green-50',
  warning: 'border-yellow-200 bg-yellow-50',
  error: 'border-red-200 bg-red-50',
};

const iconVariantStyles = {
  default: 'text-gray-600',
  success: 'text-green-600',
  warning: 'text-yellow-600',
  error: 'text-red-600',
};

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  trend,
  icon,
  variant = 'default',
  loading = false,
  className,
  onClick,
}) => {
  const IconComponent = icon ? iconMap[icon] : null;
  
  const formatValue = (val: string | number): string => {
    if (typeof val === 'number') {
      // Formatação específica baseada no tipo de métrica
      if (title.toLowerCase().includes('faturamento') || title.toLowerCase().includes('ticket')) {
        return new Intl.NumberFormat('pt-BR', {
          style: 'currency',
          currency: 'BRL',
        }).format(val);
      }
      
      if (title.toLowerCase().includes('taxa') || title.toLowerCase().includes('%')) {
        return `${val.toFixed(1)}%`;
      }
      
      if (title.toLowerCase().includes('tempo') && title.toLowerCase().includes('dia')) {
        return `${val.toFixed(1)} dias`;
      }
      
      if (title.toLowerCase().includes('satisfação')) {
        return `${val.toFixed(1)}/5`;
      }
      
      return val.toLocaleString('pt-BR');
    }
    
    return val.toString();
  };

  const getTrendIcon = () => {
    if (!trend) return null;
    
    switch (trend.direction) {
      case 'up':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'down':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      case 'neutral':
        return <Minus className="h-4 w-4 text-gray-600" />;
      default:
        return null;
    }
  };

  const getTrendColor = () => {
    if (!trend) return 'text-gray-600';
    
    switch (trend.direction) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      case 'neutral':
        return 'text-gray-600';
      default:
        return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <Card className={cn(variantStyles[variant], className)}>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium text-gray-600">
            {title}
          </CardTitle>
          {IconComponent && (
            <div className="h-4 w-4 bg-gray-200 rounded animate-pulse" />
          )}
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="h-8 bg-gray-200 rounded animate-pulse" />
            {subtitle && (
              <div className="h-4 bg-gray-200 rounded animate-pulse w-3/4" />
            )}
            {trend && (
              <div className="h-4 bg-gray-200 rounded animate-pulse w-1/2" />
            )}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card 
      className={cn(
        variantStyles[variant],
        onClick && 'cursor-pointer hover:shadow-md transition-shadow',
        className
      )}
      onClick={onClick}
    >
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">
          {title}
        </CardTitle>
        {IconComponent && (
          <IconComponent className={cn('h-4 w-4', iconVariantStyles[variant])} />
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-1">
          <div className="text-2xl font-bold text-gray-900">
            {formatValue(value)}
          </div>
          
          {subtitle && (
            <p className="text-xs text-gray-600">
              {subtitle}
            </p>
          )}
          
          {trend && (
            <div className="flex items-center space-x-1">
              {getTrendIcon()}
              <span className={cn('text-xs font-medium', getTrendColor())}>
                {trend.value > 0 ? '+' : ''}{trend.value.toFixed(1)}%
              </span>
              {trend.period && (
                <span className="text-xs text-gray-500">
                  vs {trend.period}
                </span>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

// Componente para grid de métricas
export interface MetricGridProps {
  metrics: MetricCardProps[];
  columns?: 1 | 2 | 3 | 4;
  loading?: boolean;
  className?: string;
}

export const MetricGrid: React.FC<MetricGridProps> = ({
  metrics,
  columns = 4,
  loading = false,
  className,
}) => {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4',
  };

  return (
    <div className={cn('grid gap-4', gridCols[columns], className)}>
      {metrics.map((metric, index) => (
        <MetricCard
          key={`${metric.title}-${index}`}
          {...metric}
          loading={loading}
        />
      ))}
    </div>
  );
};

// Hook para criar métricas formatadas
export const useFormattedMetrics = (metrics: any) => {
  return React.useMemo(() => {
    if (!metrics) return [];

    return [
      {
        title: 'Faturamento Mensal',
        value: metrics.faturamentoMensal,
        subtitle: 'Receita do período',
        icon: 'dollar' as const,
        variant: 'success' as const,
        trend: {
          value: 12.5,
          direction: 'up' as const,
          period: 'mês anterior',
        },
      },
      {
        title: 'Taxa de Aprovação',
        value: metrics.taxaAprovacao,
        subtitle: `${metrics.orcamentosAprovados}/${metrics.totalOrcamentos} orçamentos`,
        icon: 'check' as const,
        variant: metrics.taxaAprovacao >= 70 ? 'success' : metrics.taxaAprovacao >= 50 ? 'warning' : 'error',
        trend: {
          value: 5.2,
          direction: 'up' as const,
          period: 'mês anterior',
        },
      },
      {
        title: 'Ticket Médio',
        value: metrics.ticketMedio,
        subtitle: 'Valor médio por orçamento',
        icon: 'cart' as const,
        variant: 'default' as const,
        trend: {
          value: -2.1,
          direction: 'down' as const,
          period: 'mês anterior',
        },
      },
      {
        title: 'OS Abertas',
        value: metrics.osAbertas,
        subtitle: `${metrics.osConcluidas} concluídas`,
        icon: 'clock' as const,
        variant: metrics.osAbertas > 20 ? 'warning' : 'default',
      },
      {
        title: 'Tempo Médio Reparo',
        value: metrics.tempoMedioReparo,
        subtitle: 'Dias para conclusão',
        icon: 'clock' as const,
        variant: metrics.tempoMedioReparo <= 3 ? 'success' : metrics.tempoMedioReparo <= 7 ? 'warning' : 'error',
      },
      {
        title: 'Satisfação Cliente',
        value: metrics.satisfacaoCliente,
        subtitle: 'Avaliação média',
        icon: 'star' as const,
        variant: metrics.satisfacaoCliente >= 4 ? 'success' : metrics.satisfacaoCliente >= 3 ? 'warning' : 'error',
      },
      {
        title: 'Estoque em Alerta',
        value: metrics.estoqueAlerta,
        subtitle: 'Itens com estoque baixo',
        icon: 'alert' as const,
        variant: metrics.estoqueAlerta === 0 ? 'success' : metrics.estoqueAlerta <= 5 ? 'warning' : 'error',
      },
    ];
  }, [metrics]);
};