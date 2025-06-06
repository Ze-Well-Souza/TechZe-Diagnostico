
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
  Building2
} from 'lucide-react';

interface DashboardStats {
  totalDiagnostics: number;
  totalDevices: number;
  avgHealthScore: number;
  recentDiagnostics: any[];
}

export default function Dashboard() {
  const { user, company, signOut } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalDiagnostics: 0,
    totalDevices: 0,
    avgHealthScore: 0,
    recentDiagnostics: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [diagnostics, devices] = await Promise.all([
        diagnosticApiService.getDiagnostics(),
        diagnosticApiService.getDevices()
      ]);

      const avgHealth = diagnostics.length > 0 
        ? diagnostics.reduce((sum, d) => sum + (d.health_score || 0), 0) / diagnostics.length
        : 0;

      setStats({
        totalDiagnostics: diagnostics.length,
        totalDevices: devices.length,
        avgHealthScore: Math.round(avgHealth),
        recentDiagnostics: diagnostics.slice(0, 5)
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-tech-darker to-tech-dark">
      {/* Header */}
      <header className="border-b border-primary/20 backdrop-blur-md">
        <div className="container-responsive py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-lg bg-primary/10 electric-glow">
                  <Monitor className="h-6 w-6 text-electric" />
                </div>
                <div>
                  <h1 className="tech-font text-lg font-bold neon-text">TechRepair</h1>
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
              <span className="text-sm text-muted-foreground">
                Olá, {user?.email}
              </span>
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
        {/* Quick Actions */}
        <div className="mb-8">
          <Link to="/diagnostic">
            <Button className="btn-electric tech-font font-semibold" size="lg">
              <Plus className="mr-2 h-5 w-5" />
              Novo Diagnóstico
            </Button>
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="card-electric">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total de Diagnósticos</CardTitle>
              <Activity className="h-4 w-4 text-electric" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalDiagnostics}</div>
              <p className="text-xs text-muted-foreground">
                Análises realizadas
              </p>
            </CardContent>
          </Card>

          <Card className="card-electric">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Dispositivos</CardTitle>
              <Monitor className="h-4 w-4 text-electric" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalDevices}</div>
              <p className="text-xs text-muted-foreground">
                Equipamentos cadastrados
              </p>
            </CardContent>
          </Card>

          <Card className="card-electric">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Saúde Média</CardTitle>
              <TrendingUp className="h-4 w-4 text-electric" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getHealthColor(stats.avgHealthScore)}`}>
                {stats.avgHealthScore}%
              </div>
              <p className="text-xs text-muted-foreground">
                Score de saúde geral
              </p>
            </CardContent>
          </Card>

          <Card className="card-electric">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Técnico Ativo</CardTitle>
              <Users className="h-4 w-4 text-electric" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">Online</div>
              <p className="text-xs text-muted-foreground">
                {user?.email?.split('@')[0]}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Diagnostics */}
        <Card className="card-electric">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5 text-electric" />
              <span>Diagnósticos Recentes</span>
            </CardTitle>
            <CardDescription>
              Últimas análises realizadas no sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin h-8 w-8 border-4 border-electric border-t-transparent rounded-full"></div>
              </div>
            ) : stats.recentDiagnostics.length > 0 ? (
              <div className="space-y-4">
                {stats.recentDiagnostics.map((diagnostic) => (
                  <div 
                    key={diagnostic.id}
                    className="flex items-center justify-between p-4 rounded-lg bg-muted/20 electric-border"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="p-2 rounded bg-primary/10">
                        <Monitor className="h-4 w-4 text-electric" />
                      </div>
                      <div>
                        <p className="font-medium">Dispositivo ID: {diagnostic.device_id.slice(0, 8)}...</p>
                        <p className="text-sm text-muted-foreground">
                          {formatDate(diagnostic.created_at)}
                        </p>
                      </div>
                    </div>
                    
                    <div className="text-right">
                      <p className={`font-bold ${getHealthColor(diagnostic.health_score || 0)}`}>
                        {diagnostic.health_score || 0}%
                      </p>
                      <p className="text-sm text-muted-foreground capitalize">
                        {diagnostic.status}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Monitor className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground mb-4">
                  Nenhum diagnóstico realizado ainda
                </p>
                <Link to="/diagnostic">
                  <Button className="btn-electric">
                    <Plus className="mr-2 h-4 w-4" />
                    Realizar Primeiro Diagnóstico
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
