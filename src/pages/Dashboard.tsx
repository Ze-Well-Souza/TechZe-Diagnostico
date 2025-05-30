
import { useState, useEffect } from "react";
import { 
  Monitor, 
  Activity, 
  AlertTriangle, 
  TrendingUp
} from "lucide-react";
import { StatCard } from "@/components/dashboard/StatCard";
import { HealthTrendChart } from "@/components/dashboard/HealthTrendChart";
import { RecentDiagnosticsList } from "@/components/dashboard/RecentDiagnosticsList";
import { ComponentProblemsCard } from "@/components/dashboard/ComponentProblemsCard";
import { QuickStatusCard } from "@/components/dashboard/QuickStatusCard";

const Dashboard = () => {
  const [diagnostics, setDiagnostics] = useState<any[]>([]);
  const [stats, setStats] = useState<any>({});
  const [healthTrend, setHealthTrend] = useState<any[]>([]);

  useEffect(() => {
    // Simular carregamento de dados
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Dashboard de Diagnósticos
          </h1>
          <p className="text-gray-200">Visão geral dos diagnósticos e métricas do sistema</p>
        </div>

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
