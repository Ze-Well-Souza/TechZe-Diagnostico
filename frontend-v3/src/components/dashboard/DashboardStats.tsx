import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  Monitor, 
  Activity, 
  AlertTriangle, 
  CheckCircle,
  TrendingUp,
  TrendingDown
} from 'lucide-react';

interface DashboardStatsProps {
  totalDevices: number;
  totalDiagnostics: number;
  healthyDevices: number;
  criticalDevices: number;
}

export const DashboardStats: React.FC<DashboardStatsProps> = ({
  totalDevices,
  totalDiagnostics,
  healthyDevices,
  criticalDevices
}) => {
  const warningDevices = totalDevices - healthyDevices - criticalDevices;
  const healthyPercentage = totalDevices > 0 ? (healthyDevices / totalDevices) * 100 : 0;
  const criticalPercentage = totalDevices > 0 ? (criticalDevices / totalDevices) * 100 : 0;

  const stats = [
    {
      title: "Total de Dispositivos",
      value: totalDevices,
      description: "Dispositivos cadastrados",
      icon: Monitor,
      color: "text-blue-600",
      bgColor: "bg-blue-100"
    },
    {
      title: "Diagnósticos Realizados",
      value: totalDiagnostics,
      description: "Total de diagnósticos",
      icon: Activity,
      color: "text-purple-600",
      bgColor: "bg-purple-100"
    },
    {
      title: "Dispositivos Saudáveis",
      value: healthyDevices,
      description: `${healthyPercentage.toFixed(1)}% do total`,
      icon: CheckCircle,
      color: "text-green-600",
      bgColor: "bg-green-100",
      trend: healthyPercentage >= 70 ? "up" : "down"
    },
    {
      title: "Dispositivos Críticos",
      value: criticalDevices,
      description: `${criticalPercentage.toFixed(1)}% do total`,
      icon: AlertTriangle,
      color: "text-red-600",
      bgColor: "bg-red-100",
      trend: criticalPercentage <= 10 ? "up" : "down"
    }
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {stats.map((stat, index) => (
        <Card key={index}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {stat.title}
            </CardTitle>
            <div className={`p-2 rounded-lg ${stat.bgColor}`}>
              <stat.icon className={`h-4 w-4 ${stat.color}`} />
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  {stat.description}
                </p>
              </div>
              {stat.trend && (
                <div className={`flex items-center ${
                  stat.trend === "up" ? "text-green-600" : "text-red-600"
                }`}>
                  {stat.trend === "up" ? (
                    <TrendingUp className="h-4 w-4" />
                  ) : (
                    <TrendingDown className="h-4 w-4" />
                  )}
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
};