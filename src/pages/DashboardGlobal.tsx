import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { GlassCard } from '@/components/ui/GlassCard';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { GlobalStats } from '@/components/dashboard/GlobalStats';
import { ProgressRing } from '@/components/dashboard/ProgressRing';
import { BentoGrid, BentoItem } from '@/components/dashboard/BentoGrid';
import { ExecutiveDashboard } from '@/components/dashboard';
import { 
  Monitor, 
  BarChart3, 
  Users, 
  Activity, 
  AlertTriangle, 
  TrendingUp,
  Building2,
  LogOut,
  ArrowLeft,
  Zap,
  Clock,
  MapPin,
  PieChart
} from 'lucide-react';

interface LojaData {
  dispositivos: number;
  usuarios: number;
  saude: number;
}

interface DashboardData {
  lojas: {
    centro: LojaData;
    norte: LojaData;
    sul: LojaData;
  };
  totais: {
    dispositivos: number;
    usuarios: number;
    saude: number;
    diagnosticos_hoje: number;
    alertas_criticos: number;
  };
}

export default function DashboardGlobal() {
  const { user, company, signOut } = useAuth();
  const [data, setData] = useState<DashboardData>({
    lojas: {
      centro: { dispositivos: 45, usuarios: 23, saude: 89 },
      norte: { dispositivos: 32, usuarios: 18, saude: 91 },
      sul: { dispositivos: 28, usuarios: 12, saude: 87 }
    },
    totais: {
      dispositivos: 105,
      usuarios: 53,
      saude: 89,
      diagnosticos_hoje: 131,
      alertas_criticos: 3
    }
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="p-6">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link to="/dashboard">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Dashboard
                </Button>
              </Link>
              <h1 className="text-3xl font-bold text-white">
                Dashboard Global
              </h1>
            </div>
            <Button variant="outline" size="sm" onClick={signOut}>
              <LogOut className="h-4 w-4 mr-2" />
              Sair
            </Button>
          </div>
        </header>

        {/* Tabs para diferentes visualizações */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-2 bg-slate-800/50 border border-slate-700">
            <TabsTrigger 
              value="overview" 
              className="flex items-center space-x-2 data-[state=active]:bg-slate-700 data-[state=active]:text-white"
            >
              <Monitor className="h-4 w-4" />
              <span>Visão Operacional</span>
            </TabsTrigger>
            <TabsTrigger 
              value="executive" 
              className="flex items-center space-x-2 data-[state=active]:bg-slate-700 data-[state=active]:text-white"
            >
              <PieChart className="h-4 w-4" />
              <span>Dashboard Executivo</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Stats Grid */}
            <GlobalStats data={data.totais} />

            {/* Quick Links */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Link to="/clientes">
                <GlassCard className="p-6 hover:scale-105 transition-all duration-300 cursor-pointer">
                  <div className="flex items-center space-x-4">
                    <Users className="w-8 h-8 text-blue-400" />
                    <div>
                      <h3 className="text-lg font-semibold text-white">
                        Gestão de Clientes
                      </h3>
                      <p className="text-sm text-slate-400">
                        Gerenciar todos os clientes
                      </p>
                    </div>
                  </div>
                </GlassCard>
              </Link>

              <Link to="/diagnostic">
                <GlassCard className="p-6 hover:scale-105 transition-all duration-300 cursor-pointer">
                  <div className="flex items-center space-x-4">
                    <Activity className="w-8 h-8 text-green-400" />
                    <div>
                      <h3 className="text-lg font-semibold text-white">
                        Novo Diagnóstico
                      </h3>
                      <p className="text-sm text-slate-400">
                        Iniciar diagnóstico técnico
                      </p>
                    </div>
                  </div>
                </GlassCard>
              </Link>

              <GlassCard className="p-6 hover:scale-105 transition-all duration-300 cursor-pointer">
                <div className="flex items-center space-x-4">
                  <BarChart3 className="w-8 h-8 text-purple-400" />
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      Relatórios
                    </h3>
                    <p className="text-sm text-slate-400">
                      Análises e relatórios
                    </p>
                  </div>
                </div>
              </GlassCard>
            </div>
          </TabsContent>

          <TabsContent value="executive">
            {/* Dashboard Executivo */}
            <div className="bg-white rounded-lg shadow-lg">
              <ExecutiveDashboard />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}