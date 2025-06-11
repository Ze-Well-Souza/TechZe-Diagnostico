import React from 'react';
import { GlassCard } from '../ui/GlassCard';
import { 
  Monitor, 
  Users, 
  Activity, 
  AlertTriangle, 
  TrendingUp,
  Zap
} from 'lucide-react';

interface GlobalStatsData {
  dispositivos: number;
  usuarios: number;
  saude: number;
  diagnosticos_hoje: number;
  alertas_criticos: number;
}

interface GlobalStatsProps {
  data: GlobalStatsData;
}

interface StatCardProps {
  title: string;
  value: number;
  icon: React.ReactNode;
  color: 'blue' | 'green' | 'purple' | 'red' | 'yellow';
  trend?: number;
  suffix?: string;
}

const StatCard: React.FC<StatCardProps> = ({ 
  title, 
  value, 
  icon, 
  color, 
  trend,
  suffix = ''
}) => {
  const colorMap = {
    blue: 'text-blue-400 bg-blue-400/10 border-blue-400/20',
    green: 'text-green-400 bg-green-400/10 border-green-400/20',
    purple: 'text-purple-400 bg-purple-400/10 border-purple-400/20',
    red: 'text-red-400 bg-red-400/10 border-red-400/20',
    yellow: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20'
  };

  return (
    <GlassCard className="p-6 hover:scale-105 transition-all duration-300">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className={`w-12 h-12 rounded-xl ${colorMap[color]} flex items-center justify-center mb-4`}>
            {icon}
          </div>
          <h3 className="text-sm font-medium text-slate-400 mb-2">
            {title}
          </h3>
          <div className="flex items-end space-x-2">
            <span className="text-3xl font-bold text-white">
              {value.toLocaleString('pt-BR')}
            </span>
            {suffix && (
              <span className="text-lg text-slate-400 mb-1">
                {suffix}
              </span>
            )}
          </div>
          {trend !== undefined && (
            <div className={`flex items-center mt-2 text-sm ${
              trend >= 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              <TrendingUp className={`w-4 h-4 mr-1 ${trend < 0 ? 'rotate-180' : ''}`} />
              <span>{Math.abs(trend)}% vs. ontem</span>
            </div>
          )}
        </div>
      </div>
    </GlassCard>
  );
};

export const GlobalStats: React.FC<GlobalStatsProps> = ({ data }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
      <StatCard
        title="Total de Dispositivos"
        value={data.dispositivos}
        icon={<Monitor className="w-6 h-6" />}
        color="blue"
        trend={12}
      />
      
      <StatCard
        title="Usuários Ativos"
        value={data.usuarios}
        icon={<Users className="w-6 h-6" />}
        color="green"
        trend={8}
      />
      
      <StatCard
        title="Saúde Média"
        value={data.saude}
        icon={<Zap className="w-6 h-6" />}
        color="purple"
        suffix="%"
        trend={5}
      />
      
      <StatCard
        title="Diagnósticos Hoje"
        value={data.diagnosticos_hoje}
        icon={<Activity className="w-6 h-6" />}
        color="yellow"
        trend={-3}
      />
      
      <StatCard
        title="Alertas Críticos"
        value={data.alertas_criticos}
        icon={<AlertTriangle className="w-6 h-6" />}
        color="red"
        trend={-15}
      />
    </div>
  );
};

export default GlobalStats; 