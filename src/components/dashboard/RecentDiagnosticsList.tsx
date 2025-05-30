
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Calendar } from "lucide-react";
import { DiagnosticItem } from "./DiagnosticItem";

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

interface RecentDiagnosticsListProps {
  diagnostics: DiagnosticData[];
}

export const RecentDiagnosticsList = ({ diagnostics }: RecentDiagnosticsListProps) => {
  return (
    <Card className="bg-black/40 backdrop-blur-md border-white/20">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Calendar className="w-6 h-6" />
          Diagnósticos Recentes
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {diagnostics.map((diagnostic) => (
            <DiagnosticItem key={diagnostic.id} diagnostic={diagnostic} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
