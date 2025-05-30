
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { HardDrive, MemoryStick, Cpu } from "lucide-react";

export const ComponentProblemsCard = () => {
  return (
    <Card className="bg-black/40 backdrop-blur-md border-white/20">
      <CardHeader>
        <CardTitle className="text-white">Componentes Mais Problemáticos</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <HardDrive className="w-6 h-6 text-red-400" />
              <span className="text-white">Armazenamento</span>
            </div>
            <span className="text-red-400 font-medium">32%</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <MemoryStick className="w-6 h-6 text-yellow-400" />
              <span className="text-white">Memória RAM</span>
            </div>
            <span className="text-yellow-400 font-medium">24%</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Cpu className="w-6 h-6 text-green-400" />
              <span className="text-white">Processador</span>
            </div>
            <span className="text-green-400 font-medium">12%</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};
