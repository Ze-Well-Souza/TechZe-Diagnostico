
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, Activity, AlertTriangle } from "lucide-react";

interface QuickStatusCardProps {
  completedToday: number;
  inProgress: number;
  criticalIssues: number;
}

export const QuickStatusCard = ({ completedToday, inProgress, criticalIssues }: QuickStatusCardProps) => {
  return (
    <Card className="bg-black/40 backdrop-blur-md border-white/20">
      <CardHeader>
        <CardTitle className="text-white">Status Rápido</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-gray-200">Concluídos Hoje</span>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-400" />
              <span className="text-white font-medium">{completedToday}</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-200">Em Progresso</span>
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-yellow-400" />
              <span className="text-white font-medium">{inProgress}</span>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-gray-200">Problemas Críticos</span>
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              <span className="text-white font-medium">{criticalIssues}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
