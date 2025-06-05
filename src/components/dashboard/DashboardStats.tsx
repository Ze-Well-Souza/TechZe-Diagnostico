import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
}

const StatCard: React.FC<StatCardProps> = ({ title, value, description, icon }) => (
  <Card>
    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
      <CardTitle className="text-sm font-medium">{title}</CardTitle>
      {icon}
    </CardHeader>
    <CardContent>
      <div className="text-2xl font-bold">{value}</div>
      {description && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}
    </CardContent>
  </Card>
);

interface DashboardStatsProps {
  totalDiagnostics?: number;
  activeDiagnostics?: number;
  completedDiagnostics?: number;
  pendingDiagnostics?: number;
}

const DashboardStats: React.FC<DashboardStatsProps> = ({
  totalDiagnostics = 0,
  activeDiagnostics = 0,
  completedDiagnostics = 0,
  pendingDiagnostics = 0,
}) => {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatCard
        title="Total Diagnósticos"
        value={totalDiagnostics}
        description="Total de diagnósticos realizados"
      />
      <StatCard
        title="Ativos"
        value={activeDiagnostics}
        description="Diagnósticos em andamento"
      />
      <StatCard
        title="Concluídos"
        value={completedDiagnostics}
        description="Diagnósticos finalizados"
      />
      <StatCard
        title="Pendentes"
        value={pendingDiagnostics}
        description="Aguardando processamento"
      />
    </div>
  );
};

export default DashboardStats; 