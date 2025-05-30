
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Users, Calendar, Eye, Download } from "lucide-react";

interface DiagnosticData {
  id: number;
  deviceName: string;
  customer: string;
  date: string;
  status: string;
  healthScore: number;
  issues: number;
  recommendations: number;
}

interface DiagnosticItemProps {
  diagnostic: DiagnosticData;
}

export const DiagnosticItem = ({ diagnostic }: DiagnosticItemProps) => {
  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-500/20 text-green-300">Concluído</Badge>;
      case "in_progress":
        return <Badge className="bg-yellow-500/20 text-yellow-300">Em Andamento</Badge>;
      case "failed":
        return <Badge className="bg-red-500/20 text-red-300">Falhou</Badge>;
      default:
        return <Badge className="bg-gray-500/20 text-gray-300">Pendente</Badge>;
    }
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 90) return "text-green-400";
    if (score >= 70) return "text-yellow-400";
    return "text-red-400";
  };

  return (
    <div className="bg-black/20 p-4 rounded-lg border border-white/10 flex flex-wrap gap-4 items-center justify-between">
      <div className="flex-grow">
        <div className="flex items-center gap-3 mb-2">
          <h3 className="text-lg text-white font-medium">{diagnostic.deviceName}</h3>
          {getStatusBadge(diagnostic.status)}
        </div>
        <div className="flex items-center gap-4 text-sm text-gray-300">
          <span className="flex items-center gap-1">
            <Users className="w-4 h-4" />
            {diagnostic.customer}
          </span>
          <span className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            {diagnostic.date}
          </span>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="text-center">
          <p className={`text-2xl font-bold ${getHealthScoreColor(diagnostic.healthScore)}`}>
            {diagnostic.healthScore}%
          </p>
          <p className="text-xs text-gray-400">Saúde</p>
        </div>
        
        <div className="text-center">
          <p className="text-lg font-medium text-red-400">{diagnostic.issues}</p>
          <p className="text-xs text-gray-400">Problemas</p>
        </div>
        
        <div className="text-center">
          <p className="text-lg font-medium text-blue-400">{diagnostic.recommendations}</p>
          <p className="text-xs text-gray-400">Recomendações</p>
        </div>

        <div className="flex gap-2">
          <Button size="sm" variant="outline" className="border-white/30 text-white hover:bg-white/10">
            <Eye className="w-4 h-4" />
          </Button>
          <Button size="sm" variant="outline" className="border-white/30 text-white hover:bg-white/10">
            <Download className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};
