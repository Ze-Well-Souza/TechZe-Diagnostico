
import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { 
  Clock, 
  Search, 
  Filter, 
  Calendar,
  User,
  Monitor,
  TrendingUp,
  TrendingDown,
  Eye,
  Download,
  RefreshCw
} from "lucide-react";

const History = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [customerFilter, setCustomerFilter] = useState("");

  const diagnosticHistory = [
    {
      id: 1,
      deviceName: "PC-VENDAS-01",
      customer: "José Silva",
      date: "2024-01-28 14:30",
      healthScore: 85,
      previousScore: 78,
      issues: 2,
      status: "completed",
      duration: "12 min",
      technician: "Carlos Tech"
    },
    {
      id: 2,
      deviceName: "NOTEBOOK-ADM",
      customer: "Maria Santos",
      date: "2024-01-27 09:15",
      healthScore: 72,
      previousScore: 85,
      issues: 4,
      status: "completed", 
      duration: "18 min",
      technician: "Ana Tech"
    },
    {
      id: 3,
      deviceName: "PC-CAIXA-02",
      customer: "Carlos Oliveira",
      date: "2024-01-26 16:45",
      healthScore: 93,
      previousScore: 91,
      issues: 0,
      status: "completed",
      duration: "8 min",
      technician: "Carlos Tech"
    },
    {
      id: 4,
      deviceName: "NOTEBOOK-RH",
      customer: "Ana Paula",
      date: "2024-01-25 11:20",
      healthScore: 67,
      previousScore: 72,
      issues: 6,
      status: "completed",
      duration: "25 min",
      technician: "Roberto Tech"
    },
    {
      id: 5,
      deviceName: "PC-DESIGN-01",
      customer: "Design Studio",
      date: "2024-01-24 13:10",
      healthScore: 89,
      previousScore: 85,
      issues: 1,
      status: "completed",
      duration: "15 min",
      technician: "Ana Tech"
    }
  ];

  const getHealthTrend = (current: number, previous: number) => {
    if (current > previous) {
      return {
        icon: <TrendingUp className="w-4 h-4 text-green-400" />,
        color: "text-green-400",
        text: `+${current - previous}`
      };
    } else if (current < previous) {
      return {
        icon: <TrendingDown className="w-4 h-4 text-red-400" />,
        color: "text-red-400", 
        text: `${current - previous}`
      };
    } else {
      return {
        icon: <RefreshCw className="w-4 h-4 text-gray-400" />,
        color: "text-gray-400",
        text: "0"
      };
    }
  };

  const getHealthScoreColor = (score: number) => {
    if (score >= 90) return "text-green-400";
    if (score >= 70) return "text-yellow-400";
    return "text-red-400";
  };

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

  const filteredHistory = diagnosticHistory.filter(item => {
    const matchesSearch = item.deviceName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.customer.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCustomer = !customerFilter || item.customer.toLowerCase().includes(customerFilter.toLowerCase());
    const matchesDateFrom = !dateFrom || item.date >= dateFrom;
    const matchesDateTo = !dateTo || item.date <= dateTo;
    
    return matchesSearch && matchesCustomer && matchesDateFrom && matchesDateTo;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Histórico de Diagnósticos
          </h1>
          <p className="text-gray-200">Acompanhe o histórico completo de todos os diagnósticos realizados</p>
        </div>

        {/* Filtros */}
        <Card className="bg-black/40 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Filter className="w-6 h-6" />
              Filtros de Pesquisa
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              <div className="space-y-2">
                <Label htmlFor="search" className="text-white">Pesquisar</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="search"
                    placeholder="Dispositivo ou cliente..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-white/10 border-white/30 text-white placeholder:text-white/50"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="customer" className="text-white">Cliente</Label>
                <Input
                  id="customer"
                  placeholder="Nome do cliente..."
                  value={customerFilter}
                  onChange={(e) => setCustomerFilter(e.target.value)}
                  className="bg-white/10 border-white/30 text-white placeholder:text-white/50"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="dateFrom" className="text-white">Data Inicial</Label>
                <Input
                  id="dateFrom"
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="bg-white/10 border-white/30 text-white"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="dateTo" className="text-white">Data Final</Label>
                <Input
                  id="dateTo"
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="bg-white/10 border-white/30 text-white"
                />
              </div>

              <div className="space-y-2 flex items-end">
                <Button 
                  variant="outline" 
                  className="w-full border-white/30 text-white hover:bg-white/10"
                  onClick={() => {
                    setSearchTerm("");
                    setCustomerFilter("");
                    setDateFrom("");
                    setDateTo("");
                  }}
                >
                  Limpar Filtros
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Estatísticas Rápidas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="bg-black/40 backdrop-blur-md border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-200 text-sm">Total de Diagnósticos</p>
                  <p className="text-3xl font-bold text-white">{diagnosticHistory.length}</p>
                </div>
                <Monitor className="w-8 h-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-black/40 backdrop-blur-md border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-200 text-sm">Média de Saúde</p>
                  <p className="text-3xl font-bold text-yellow-400">
                    {Math.round(diagnosticHistory.reduce((acc, item) => acc + item.healthScore, 0) / diagnosticHistory.length)}%
                  </p>
                </div>
                <TrendingUp className="w-8 h-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-black/40 backdrop-blur-md border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-200 text-sm">Problemas Encontrados</p>
                  <p className="text-3xl font-bold text-red-400">
                    {diagnosticHistory.reduce((acc, item) => acc + item.issues, 0)}
                  </p>
                </div>
                <TrendingDown className="w-8 h-8 text-red-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-black/40 backdrop-blur-md border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-200 text-sm">Tempo Médio</p>
                  <p className="text-3xl font-bold text-blue-400">15m</p>
                </div>
                <Clock className="w-8 h-8 text-blue-400" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Lista do Histórico */}
        <Card className="bg-black/40 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Clock className="w-6 h-6" />
              Histórico Completo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredHistory.length === 0 ? (
                <div className="text-center py-8">
                  <Clock className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-400 text-lg">Nenhum diagnóstico encontrado</p>
                  <p className="text-gray-500">Tente ajustar os filtros de pesquisa</p>
                </div>
              ) : (
                filteredHistory.map((item) => {
                  const trend = getHealthTrend(item.healthScore, item.previousScore);
                  
                  return (
                    <div 
                      key={item.id}
                      className="bg-black/20 p-4 rounded-lg border border-white/10 flex flex-wrap gap-4 items-center justify-between"
                    >
                      <div className="flex-grow">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg text-white font-medium">{item.deviceName}</h3>
                          {getStatusBadge(item.status)}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-300">
                          <span className="flex items-center gap-1">
                            <User className="w-4 h-4" />
                            {item.customer}
                          </span>
                          <span className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {item.date}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-4 h-4" />
                            {item.duration}
                          </span>
                          <span className="text-gray-400">por {item.technician}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-6">
                        <div className="text-center">
                          <div className="flex items-center gap-2 justify-center mb-1">
                            <p className={`text-2xl font-bold ${getHealthScoreColor(item.healthScore)}`}>
                              {item.healthScore}%
                            </p>
                            <div className="flex items-center gap-1">
                              {trend.icon}
                              <span className={`text-sm ${trend.color}`}>{trend.text}</span>
                            </div>
                          </div>
                          <p className="text-xs text-gray-400">Saúde</p>
                        </div>
                        
                        <div className="text-center">
                          <p className="text-lg font-medium text-red-400">{item.issues}</p>
                          <p className="text-xs text-gray-400">Problemas</p>
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
                })
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default History;
