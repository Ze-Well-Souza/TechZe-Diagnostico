import React from 'react';
import { useDiagnostics } from '@/hooks/useDiagnostics';
import { DashboardStats } from '@/components/dashboard/DashboardStats';
import DeviceCard from '@/components/diagnostic/DeviceCard';
import DiagnosticCard from '@/components/diagnostic/DiagnosticCard';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Plus, RefreshCw } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';

export const Dashboard: React.FC = () => {
  const {
    devices,
    diagnostics,
    statistics,
    isLoadingDevices,
    isLoadingDiagnostics,
    isRunningDiagnostic,
    executeFullDiagnostic,
    refetchDevices,
    refetchDiagnostics,
    getLastDiagnosticForDevice
  } = useDiagnostics();

  const handleRunDiagnostic = (deviceId: string) => {
    executeFullDiagnostic(deviceId);
  };

  const handleRefresh = () => {
    refetchDevices();
    refetchDiagnostics();
  };

  // Últimos diagnósticos (5 mais recentes)
  const recentDiagnostics = diagnostics
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5);

  if (isLoadingDevices || isLoadingDiagnostics) {
    return (
      <div className="container mx-auto p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">
              Visão geral dos seus dispositivos e diagnósticos
            </p>
          </div>
        </div>

        {/* Loading Stats */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[...Array(4)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-4 w-32" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-8 w-16 mb-2" />
                <Skeleton className="h-3 w-24" />
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Loading Content */}
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-24 w-full" />
                ))}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-24 w-full" />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Visão geral dos seus dispositivos e diagnósticos
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Atualizar
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Novo Dispositivo
          </Button>
        </div>
      </div>

      {/* Stats */}
      <DashboardStats
        totalDevices={statistics.totalDevices}
        totalDiagnostics={statistics.totalDiagnostics}
        healthyDevices={statistics.healthyDevices}
        criticalDevices={statistics.criticalDevices}
      />

      {/* Main Content */}
      <Tabs defaultValue="devices" className="space-y-4">
        <TabsList>
          <TabsTrigger value="devices">Dispositivos</TabsTrigger>
          <TabsTrigger value="diagnostics">Diagnósticos Recentes</TabsTrigger>
        </TabsList>

        <TabsContent value="devices" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Seus Dispositivos</CardTitle>
              <CardDescription>
                Gerencie e monitore todos os seus dispositivos
              </CardDescription>
            </CardHeader>
            <CardContent>
              {devices.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">
                    Nenhum dispositivo cadastrado ainda.
                  </p>
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Cadastrar Primeiro Dispositivo
                  </Button>
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                  {devices.map((device) => (
                    <DeviceCard
                      key={device.id}
                      device={device}
                      lastDiagnostic={getLastDiagnosticForDevice(device.id)}
                      onRunDiagnostic={handleRunDiagnostic}
                      isRunningDiagnostic={isRunningDiagnostic}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="diagnostics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Diagnósticos Recentes</CardTitle>
              <CardDescription>
                Últimos diagnósticos executados nos seus dispositivos
              </CardDescription>
            </CardHeader>
            <CardContent>
              {recentDiagnostics.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">
                    Nenhum diagnóstico executado ainda.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Execute um diagnóstico em um dos seus dispositivos para ver os resultados aqui.
                  </p>
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {recentDiagnostics.map((diagnostic) => (
                    <DiagnosticCard
                      key={diagnostic.id}
                      diagnostic={diagnostic}
                      device={devices.find(d => d.id === diagnostic.device_id)}
                      onRunNewDiagnostic={handleRunDiagnostic}
                    />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};