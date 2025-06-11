import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { diagnosticApiService } from '@/services/diagnosticApiService';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Zap, 
  Monitor, 
  Users, 
  TrendingUp, 
  Activity,
  Plus,
  LogOut,
  Building2,
  Calendar,
  Clock,
  DollarSign,
  AlertTriangle,
  CheckCircle2,
  BarChart3,
  FileText,
  Settings,
  Printer
} from 'lucide-react';

interface DashboardStats {
  totalDiagnostics: number;
  totalDevices: number;
  avgHealthScore: number;
  recentDiagnostics: any[];
  todayDiagnostics: number;
  weekDiagnostics: number;
  monthDiagnostics: number;
  criticalDevices: number;
  warningDevices: number;
  healthyDevices: number;
}

export default function Dashboard() {
  const { user, company, signOut } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalDiagnostics: 0,
    totalDevices: 0,
    avgHealthScore: 0,
    recentDiagnostics: [],
    todayDiagnostics: 0,
    weekDiagnostics: 0,
    monthDiagnostics: 0,
    criticalDevices: 0,
    warningDevices: 0,
    healthyDevices: 0
  });
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState<'today' | 'week' | 'month'>('today');

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 30000); // Atualizar a cada 30 segundos
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const [diagnostics, devices] = await Promise.all([
        diagnosticApiService.getDiagnostics(),
        diagnosticApiService.getDevices()
      ]);

      const now = new Date();
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      const weekAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
      const monthAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

      const todayDiagnostics = diagnostics.filter(d => 
        new Date(d.created_at) >= today
      ).length;

      const weekDiagnostics = diagnostics.filter(d => 
        new Date(d.created_at) >= weekAgo
      ).length;

      const monthDiagnostics = diagnostics.filter(d => 
        new Date(d.created_at) >= monthAgo
      ).length;

      const avgHealth = diagnostics.length > 0 
        ? diagnostics.reduce((sum, d) => sum + (d.health_score || 0), 0) / diagnostics.length
        : 0;

      // Categorizar dispositivos por saúde
      const criticalDevices = diagnostics.filter(d => (d.health_score || 0) < 40).length;
      const warningDevices = diagnostics.filter(d => {
        const score = d.health_score || 0;
        return score >= 40 && score < 80;
      }).length;
      const healthyDevices = diagnostics.filter(d => (d.health_score || 0) >= 80).length;

      setStats({
        totalDiagnostics: diagnostics.length,
        totalDevices: devices.length,
        avgHealthScore: Math.round(avgHealth),
        recentDiagnostics: diagnostics
          .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
          .slice(0, 8),
        todayDiagnostics,
        weekDiagnostics,
        monthDiagnostics,
        criticalDevices,
        warningDevices,
        healthyDevices
      });
    } catch (error) {
      console.error('Erro ao carregar dados do dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getHealthBadge = (score: number) => {
    if (score >= 80) return { text: 'Excelente', color: 'bg-green-400/20 text-green-400 border-green-400/30' };
    if (score >= 60) return { text: 'Bom', color: 'bg-yellow-400/20 text-yellow-400 border-yellow-400/30' };
    if (score >= 40) return { text: 'Regular', color: 'bg-orange-400/20 text-orange-400 border-orange-400/30' };
    return { text: 'Crítico', color: 'bg-red-400/20 text-red-400 border-red-400/30' };
  };

  const getCurrentPeriodStats = () => {
    switch (selectedPeriod) {
      case 'today':
        return {
          count: stats.todayDiagnostics,
          label: 'Hoje',
          comparison: stats.todayDiagnostics > 0 ? '+' + stats.todayDiagnostics : '0'
        };
      case 'week':
        return {
          count: stats.weekDiagnostics,
          label: 'Esta Semana',
          comparison: stats.weekDiagnostics > stats.todayDiagnostics ? '+' + (stats.weekDiagnostics - stats.todayDiagnostics) : '0'
        };
      case 'month':
        return {
          count: stats.monthDiagnostics,
          label: 'Este Mês',
          comparison: stats.monthDiagnostics > stats.weekDiagnostics ? '+' + (stats.monthDiagnostics - stats.weekDiagnostics) : '0'
        };
    }
  };

  const currentStats = getCurrentPeriodStats();

  return (
    <div className="min-h-screen bg-gradient-to-br from-tech-darker to-tech-dark">
      {/* Header Otimizado */}
      <header className="border-b border-primary/20 backdrop-blur-md bg-tech-darker/50">
        <div className="container-responsive py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-primary/10 electric-glow">
                  <Monitor className="h-6 w-6 text-electric" />
                </div>
                <div>
                  <h1 className="tech-font text-xl font-bold neon-text">
                    TechZe Diagnóstico
                  </h1>
                  {company && (
                    <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                      <Building2 className="h-3 w-3" />
                      <span>{company.name}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-muted-foreground text-right">
                <p className="font-medium text-white">Gerente: {user?.email?.split('@')[0]}</p>
                <p className="text-xs">{new Date().toLocaleDateString('pt-BR', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}</p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={signOut}
                className="electric-border"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Sair
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container-responsive py-8">
        {/* Quick Actions - Mais visível */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-4">
            <Link to="/dashboard-global">
              <Button className="btn-electric tech-font font-semibold" size="lg">
                <BarChart3 className="mr-2 h-5 w-5" />
                Dashboard Global
              </Button>
            </Link>
            <Link to="/diagnostic">
              <Button className="btn-electric tech-font font-semibold" size="lg">
                <Plus className="mr-2 h-5 w-5" />
                Novo Diagnóstico
              </Button>
            </Link>
            <Link to="/clientes">
              <Button variant="outline" className="electric-border" size="lg">
                <Users className="mr-2 h-5 w-5" />
                Clientes
              </Button>
            </Link>
            <Link to="/admin/lojas">
              <Button variant="outline" className="electric-border" size="lg">
                <Building2 className="mr-2 h-5 w-5" />
                Gestão de Lojas
              </Button>
            </Link>
            <Button variant="outline" className="electric-border" size="lg">
              <FileText className="mr-2 h-5 w-5" />
              Relatórios
            </Button>
            <Button variant="outline" className="electric-border" size="lg">
              <Settings className="mr-2 h-5 w-5" />
              Configurações
            </Button>
          </div>
        </div>

        {/* Seletor de Período */}
        <div className="mb-6">
          <div className="flex space-x-2">
            {(['today', 'week', 'month'] as const).map((period) => (
              <Button
                key={period}
                variant={selectedPeriod === period ? "default" : "outline"}
                size="sm"
                onClick={() => setSelectedPeriod(period)}
                className={selectedPeriod === period ? "btn-electric" : "electric-border"}
              >
                {period === 'today' ? 'Hoje' : period === 'week' ? 'Semana' : 'Mês'}
              </Button>
            ))}
          </div>
        </div>

        {/* Stats Cards - Layout Otimizado */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="card-electric">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Diagnósticos {currentStats.label}</CardTitle>
              <Activity className="h-4 w-4 text-electric" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-electric">{currentStats.count}</div>
              <p className="text-xs text-muted-foreground">
                {currentStats.comparison} novos
              </p>
            </CardContent>
          </Card>

          <Card className="card-electric">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Equipamentos</CardTitle>
              <Monitor className="h-4 w-4 text-electric" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.totalDevices}</div>
              <p className="text-xs text-muted-foreground">
                Total cadastrados
              </p>
            </CardContent>
          </Card>

          <Card className="card-electric">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Saúde Média</CardTitle>
              <TrendingUp className="h-4 w-4 text-electric" />
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${getHealthColor(stats.avgHealthScore)}`}>
                {stats.avgHealthScore}%
              </div>
              <p className="text-xs text-muted-foreground">
                Score geral da loja
              </p>
            </CardContent>
          </Card>

          <Card className="card-electric">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Status da Loja</CardTitle>
              <Users className="h-4 w-4 text-electric" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">Operacional</div>
              <p className="text-xs text-muted-foreground">
                Sistema funcionando
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Status dos Equipamentos */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <Card className="card-electric">
            <CardHeader>
              <CardTitle className="flex items-center text-green-400">
                <CheckCircle2 className="h-5 w-5 mr-2" />
                Equipamentos Saudáveis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-green-400 mb-2">{stats.healthyDevices}</div>
              <p className="text-sm text-muted-foreground">
                Funcionando perfeitamente (80%+)
              </p>
            </CardContent>
          </Card>

          <Card className="card-electric">
            <CardHeader>
              <CardTitle className="flex items-center text-yellow-400">
                <AlertTriangle className="h-5 w-5 mr-2" />
                Precisam de Atenção
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-yellow-400 mb-2">{stats.warningDevices}</div>
              <p className="text-sm text-muted-foreground">
                Requerem manutenção (40-79%)
              </p>
            </CardContent>
          </Card>

          <Card className="card-electric">
            <CardHeader>
              <CardTitle className="flex items-center text-red-400">
                <AlertTriangle className="h-5 w-5 mr-2" />
                Estado Crítico
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-4xl font-bold text-red-400 mb-2">{stats.criticalDevices}</div>
              <p className="text-sm text-muted-foreground">
                Precisam reparo urgente (&lt;40%)
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Diagnostics - Melhorado */}
        <Card className="card-electric">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-electric" />
              <span>Diagnósticos Recentes</span>
            </CardTitle>
            <CardDescription>
              Últimas análises realizadas na loja - Atualização em tempo real
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-electric"></div>
              </div>
            ) : stats.recentDiagnostics.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Monitor className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Nenhum diagnóstico realizado ainda</p>
                <p className="text-sm">Clique em "Novo Diagnóstico" para começar</p>
              </div>
            ) : (
              <div className="space-y-4">
                {stats.recentDiagnostics.map((diagnostic, index) => {
                  const healthBadge = getHealthBadge(diagnostic.health_score || 0);
                  return (
                    <div
                      key={diagnostic.id}
                      className="flex items-center justify-between p-4 rounded-lg bg-muted/5 border border-muted/10 hover:border-electric/30 transition-colors"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="p-2 rounded-lg bg-primary/10">
                          <Monitor className="h-5 w-5 text-electric" />
                        </div>
                        <div>
                          <p className="font-medium">
                            {diagnostic.client_name || 'Cliente não informado'}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            {diagnostic.device?.name || 'Dispositivo'} • {formatDate(diagnostic.created_at)}
                          </p>
                          {diagnostic.client_phone && (
                            <p className="text-xs text-muted-foreground">
                              📞 {diagnostic.client_phone}
                            </p>
                          )}
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-3">
                        <div className="text-right">
                          <div className={`text-2xl font-bold ${getHealthColor(diagnostic.health_score || 0)}`}>
                            {diagnostic.health_score || 0}%
                          </div>
                          <div className={`px-2 py-1 rounded text-xs border ${healthBadge.color}`}>
                            {healthBadge.text}
                          </div>
                        </div>
                        
                        <Button variant="outline" size="sm" className="electric-border">
                          <FileText className="h-4 w-4 mr-1" />
                          Ver
                        </Button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Footer com informações da loja */}
        <div className="mt-8 text-center text-sm text-muted-foreground">
          <p>Sistema TechZe Diagnóstico - Versão 3.0</p>
          <p>Última atualização: {new Date().toLocaleTimeString('pt-BR')}</p>
        </div>
      </div>
    </div>
  );
}
