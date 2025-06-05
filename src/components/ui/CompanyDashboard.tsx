
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { diagnosticApiService } from '@/services/diagnosticApiService';
import { multiTenantService } from '@/services/multiTenantService';

export function CompanyDashboard() {
  const currentCompany = multiTenantService.getCurrentTenant();

  const { data: metrics, isLoading } = useQuery({
    queryKey: ['company-metrics', currentCompany],
    queryFn: async () => {
      const diagnostics = await diagnosticApiService.getDiagnostics();
      const devices = await diagnosticApiService.getDevices();
      
      return {
        totalDevices: devices.length,
        totalDiagnostics: diagnostics.length,
        avgHealthScore: diagnostics.reduce((acc, d) => acc + (d.health_score || 0), 0) / diagnostics.length,
        statusDistribution: diagnostics.reduce((acc, d) => {
          acc[d.status] = (acc[d.status] || 0) + 1;
          return acc;
        }, {} as Record<string, number>)
      };
    },
    enabled: !!currentCompany
  });

  if (isLoading) {
    return <div>Carregando métricas...</div>;
  }

  const chartData = Object.entries(metrics?.statusDistribution || {}).map(([status, count]) => ({
    status,
    count
  }));

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <Card>
        <CardHeader>
          <CardTitle>Total de Dispositivos</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">{metrics?.totalDevices || 0}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Diagnósticos Realizados</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">{metrics?.totalDiagnostics || 0}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Score Médio de Saúde</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-3xl font-bold">{(metrics?.avgHealthScore || 0).toFixed(1)}%</p>
        </CardContent>
      </Card>

      <Card className="col-span-full md:col-span-2 lg:col-span-1">
        <CardHeader>
          <CardTitle>Status dos Diagnósticos</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="status" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
