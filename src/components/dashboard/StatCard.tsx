
import { Card, CardContent } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  valueClassName?: string;
}

export const StatCard = ({ title, value, icon: Icon, valueClassName = "text-white" }: StatCardProps) => {
  return (
    <Card className="bg-black/40 backdrop-blur-md border-white/20">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-gray-200 text-sm">{title}</p>
            <p className={`text-3xl font-bold ${valueClassName}`}>{value}</p>
          </div>
          <Icon className="w-8 h-8 text-gray-400" />
        </div>
      </CardContent>
    </Card>
  );
};
