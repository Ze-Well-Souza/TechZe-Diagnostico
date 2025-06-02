import { useState, useEffect } from "react";
import { 
  Monitor, 
  Activity, 
  AlertTriangle, 
  TrendingUp,
  Wifi,
  WifiOff
} from "lucide-react";
import { StatCard } from "@/components/dashboard/StatCard";
import { HealthTrendChart } from "@/components/dashboard/HealthTrendChart";
import { RecentDiagnosticsList } from "@/components/dashboard/RecentDiagnosticsList";
import { ComponentProblemsCard } from "@/components/dashboard/ComponentProblemsCard";
import { QuickStatusCard } from "@/components/dashboard/QuickStatusCard";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

const Dashboard = () => {
  const [diagnostics, setDiagnostics] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({});
  const [healthTrend, setHealthTrend] = useState<any[]>([]);
  const [apiStatus, setApiStatus] = useState<'loading' | 'connected' | 'disconnected'>('loading');
  const [apiInfo, setApiInfo] = useState<any>(null);
  const { toast } = useToast();

  // Função para testar conexão com a API
  const testApiConnection = async () => {
    setApiStatus('loading');
    try {
      const response = await fetch('https://techze-diagnostic-api.onrender.com/', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const data = await response.json();
        setApiInfo(data);
        setApiStatus('connected');
        toast({
          title: "✅ API Conectada",
          description: `Microserviço funcionando - ${data.version}`,
        });
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Erro ao conectar com API:', error);
      setApiStatus('disconnected');
      toast({
        title: "❌ API Desconectada",
        description: "Não foi possível conectar com o microserviço",
        variant: "destructive",
      });
    }
  };

  // Função para executar diagnóstico rápido
  const runQuickDiagnostic = async () => {
    try {
      toast({
        title: "🔍 Executando Diagnóstico",
        description: "Iniciando diagnóstico rápido do sistema...",
      });
      
      const response = await fetch('https://techze-diagnostic-api.onrender.com/api/v1/diagnostic/quick', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('Resultado do diagnóstico:', result);
        
        // Atualizar stats com dados reais
        if (result.health_score) {
          setStats(prev => ({
            ...prev,
            avgHealthScore: result.health_score,
            lastDiagnostic: new Date().toISOString(),
          }));
        }
        
        toast({
          title: "✅ Diagnóstico Concluído",
          description: `Health Score: ${result.health_score || 'N/A'}`,
        });
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Erro ao executar diagnóstico:', error);
      toast({
        title: "❌ Erro no Diagnóstico",
        description: "Não foi possível executar o diagnóstico",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    // Testar conexão da API na inicialização
    testApiConnection();
    
    // Simular dados iniciais (será substituído por dados reais)
    const mockDiagnostics = [
      {
        id: 1,
        deviceName: "PC-VENDAS-01",
        customer: "José Silva",
        date: "2024-01-28",
        status: "completed",
        healthScore: 85,
        issues: 2,
        recommendations: 3
      },
      {
        id: 2,
        deviceName: "NOTEBOOK-ADM",
        customer: "Maria Santos",
        date: "2024-01-27",
        status: "in_progress",
        healthScore: 72,
        issues: 4,
        recommendations: 5
      },
      {
        id: 3,
        deviceName: "PC-CAIXA-02",
        customer: "Carlos Oliveira",
        date: "2024-01-26",
        status: "completed",
        healthScore: 93,
        issues: 0,
        recommendations: 1
      }
    ];

    const mockStats = {
      totalDiagnostics: 156,
      todayDiagnostics: 8,
      avgHealthScore: 78,
      criticalIssues: 12,
      completedToday: 6,
      inProgress: 2
    };

    const mockHealthTrend = [
      { date: "Jan 22", score: 75 },
      { date: "Jan 23", score: 78 },
      { date: "Jan 24", score: 82 },
      { date: "Jan 25", score: 79 },
      { date: "Jan 26", score: 85 },
      { date: "Jan 27", score: 83 },
      { date: "Jan 28", score: 78 }
    ];

    setDiagnostics(mockDiagnostics);
    setStats(mockStats);
    setHealthTrend(mockHealthTrend);
  }, []);

  const getHealthScoreColor = (score: number) => {
    if (score >= 90) return "text-green-400";
    if (score >= 70) return "text-yellow-400";
    return "text-red-400";
  };

  const getApiStatusBadge = () => {
    switch (apiStatus) {
      case 'loading':
        return <Badge variant="secondary" className="animate-pulse bg-gray-700 text-gray-300">🔄 Conectando...</Badge>;
      case 'connected':
        return <Badge className="bg-green-900 text-green-300 border-green-700">✅ API Online</Badge>;
      case 'disconnected':
        return <Badge variant="destructive" className="bg-red-900 text-red-300 border-red-700">❌ API Offline</Badge>;
      default:
        return <Badge variant="secondary" className="bg-gray-700 text-gray-300">❓ Desconhecido</Badge>;
    }
  };

  return (
    <div className="min-h-screen bg-black p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Dashboard de Diagnósticos
          </h1>
          <p className="text-gray-400">Visão geral dos diagnósticos e métricas do sistema</p>
        </div>

        {/* Status da API */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-3">
              {apiStatus === 'connected' ? <Wifi className="w-6 h-6 text-green-400" /> : <WifiOff className="w-6 h-6 text-red-400" />}
              Status do Microserviço
              {getApiStatusBadge()}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap items-center gap-4">
              {apiInfo && (
                <div className="text-sm text-gray-300 grid grid-cols-2 md:grid-cols-4 gap-4 flex-1">
                  <div>
                    <span className="font-semibold text-white">Versão:</span> {apiInfo.version}
                  </div>
                  <div>
                    <span className="font-semibold text-white">Ambiente:</span> {apiInfo.environment}
                  </div>
                  <div>
                    <span className="font-semibold text-white">Status:</span> {apiInfo.status}
                  </div>
                  <div>
                    <span className="font-semibold text-white">API:</span> {apiInfo.api}
                  </div>
                </div>
              )}
              <div className="flex gap-2">
                <Button 
                  onClick={testApiConnection}
                  variant="outline"
                  size="sm"
                  className="border-gray-700 text-gray-300 hover:bg-gray-800 hover:text-white"
                >
                  🔄 Testar Conexão
                </Button>
                <Button 
                  onClick={runQuickDiagnostic}
                  disabled={apiStatus !== 'connected'}
                  size="sm"
                  className="bg-white text-black hover:bg-gray-100 disabled:bg-gray-700 disabled:text-gray-500"
                >
                  🔍 Diagnóstico Rápido
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Cards de Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard 
            title="Total de Diagnósticos" 
            value={stats.totalDiagnostics} 
            icon={Monitor} 
          />
          <StatCard 
            title="Hoje" 
            value={stats.todayDiagnostics} 
            icon={Activity} 
          />
          <StatCard 
            title="Saúde Média" 
            value={`${stats.avgHealthScore}%`} 
            icon={TrendingUp}
            valueClassName={getHealthScoreColor(stats.avgHealthScore)}
          />
          <StatCard 
            title="Problemas Críticos" 
            value={stats.criticalIssues} 
            icon={AlertTriangle}
            valueClassName="text-red-400"
          />
        </div>

        {/* Gráfico de Tendência de Saúde */}
        <HealthTrendChart data={healthTrend} />

        {/* Lista de Diagnósticos Recentes */}
        <RecentDiagnosticsList diagnostics={diagnostics} />

        {/* Componentes Mais Problemáticos e Status Rápido */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ComponentProblemsCard />
          <QuickStatusCard 
            completedToday={stats.completedToday}
            inProgress={stats.inProgress}
            criticalIssues={stats.criticalIssues}
          />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
