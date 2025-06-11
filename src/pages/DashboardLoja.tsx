import React, { useState, useEffect } from 'react';
import { GlassCard } from '../components/ui/GlassCard';
import { GlobalStats } from '../components/dashboard/GlobalStats';
import { ProgressRing } from '../components/ui/ProgressRing';
import { 
  Store, 
  Users, 
  Smartphone, 
  TrendingUp, 
  Calendar,
  Bell,
  Settings,
  BarChart3
} from 'lucide-react';
import { useAuth } from '../hooks/useAuth';

export const DashboardLoja: React.FC = () => {
  const { user } = useAuth();
  const [lojaStats, setLojaStats] = useState({
    totalClientes: 45,
    totalDiagnosticos: 128,
    avgHealthScore: 78,
    diagnosticosHoje: 8,
    clientesAtivos: 42,
    ticketsAbertos: 12
  });

  const recentActivities = [
    { id: 1, cliente: 'João Silva', acao: 'Novo diagnóstico', tempo: '5 min atrás', tipo: 'diagnostico' },
    { id: 2, cliente: 'Maria Santos', acao: 'Cliente cadastrado', tempo: '15 min atrás', tipo: 'cliente' },
    { id: 3, cliente: 'Pedro Costa', acao: 'Diagnóstico concluído', tempo: '32 min atrás', tipo: 'concluido' },
    { id: 4, cliente: 'Ana Oliveira', acao: 'Health score atualizado', tempo: '1h atrás', tipo: 'update' }
  ];

  const quickActions = [
    { icon: Users, label: 'Gestão de Clientes', path: '/clientes', color: 'from-blue-500 to-cyan-500' },
    { icon: Smartphone, label: 'Novo Diagnóstico', path: '/diagnostic', color: 'from-green-500 to-emerald-500' },
    { icon: BarChart3, label: 'Relatórios', path: '/relatorios', color: 'from-purple-500 to-violet-500' },
    { icon: Settings, label: 'Configurações', path: '/configuracoes', color: 'from-orange-500 to-amber-500' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Dashboard da Loja
            </h1>
            <p className="text-gray-300">
              Bem-vindo, {user?.nome} • Gestão da sua unidade
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <button className="p-2 text-gray-300 hover:text-white transition-colors">
              <Bell className="w-6 h-6" />
            </button>
            <button className="p-2 text-gray-300 hover:text-white transition-colors">
              <Settings className="w-6 h-6" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <GlassCard className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Total de Clientes</p>
              <p className="text-3xl font-bold text-white">{lojaStats.totalClientes}</p>
              <p className="text-green-400 text-sm flex items-center mt-1">
                <TrendingUp className="w-4 h-4 mr-1" />
                +8% este mês
              </p>
            </div>
            <div className="p-3 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-xl">
              <Users className="w-8 h-8 text-white" />
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Diagnósticos</p>
              <p className="text-3xl font-bold text-white">{lojaStats.totalDiagnosticos}</p>
              <p className="text-green-400 text-sm flex items-center mt-1">
                <TrendingUp className="w-4 h-4 mr-1" />
                +12% este mês
              </p>
            </div>
            <div className="p-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl">
              <Smartphone className="w-8 h-8 text-white" />
            </div>
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Health Score Médio</p>
              <p className="text-3xl font-bold text-white">{lojaStats.avgHealthScore}%</p>
              <p className="text-orange-400 text-sm flex items-center mt-1">
                <TrendingUp className="w-4 h-4 mr-1" />
                -3% este mês
              </p>
            </div>
            <ProgressRing 
              progress={lojaStats.avgHealthScore} 
              size="lg"
              className="w-16 h-16"
            />
          </div>
        </GlassCard>

        <GlassCard className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Diagnósticos Hoje</p>
              <p className="text-3xl font-bold text-white">{lojaStats.diagnosticosHoje}</p>
              <p className="text-blue-400 text-sm flex items-center mt-1">
                <Calendar className="w-4 h-4 mr-1" />
                {lojaStats.ticketsAbertos} em andamento
              </p>
            </div>
            <div className="p-3 bg-gradient-to-r from-purple-500 to-violet-500 rounded-xl">
              <BarChart3 className="w-8 h-8 text-white" />
            </div>
          </div>
        </GlassCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Quick Actions */}
        <GlassCard className="p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Ações Rápidas</h2>
          <div className="grid grid-cols-2 gap-4">
            {quickActions.map((action, index) => (
              <button
                key={index}
                className="group p-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl transition-all duration-200 text-left"
              >
                <div className={`inline-flex p-3 bg-gradient-to-r ${action.color} rounded-lg mb-3 group-hover:scale-110 transition-transform`}>
                  <action.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-white font-medium text-sm">{action.label}</h3>
              </button>
            ))}
          </div>
        </GlassCard>

        {/* Recent Activities */}
        <GlassCard className="p-6">
          <h2 className="text-xl font-semibold text-white mb-6">Atividades Recentes</h2>
          <div className="space-y-4">
            {recentActivities.map((activity) => (
              <div key={activity.id} className="flex items-center space-x-4 p-3 bg-white/5 rounded-lg">
                <div className={`w-2 h-2 rounded-full ${
                  activity.tipo === 'diagnostico' ? 'bg-blue-400' :
                  activity.tipo === 'cliente' ? 'bg-green-400' :
                  activity.tipo === 'concluido' ? 'bg-purple-400' :
                  'bg-orange-400'
                }`}></div>
                <div className="flex-1">
                  <p className="text-white text-sm font-medium">{activity.cliente}</p>
                  <p className="text-gray-300 text-xs">{activity.acao}</p>
                </div>
                <span className="text-gray-400 text-xs">{activity.tempo}</span>
              </div>
            ))}
          </div>
        </GlassCard>
      </div>
    </div>
  );
}; 