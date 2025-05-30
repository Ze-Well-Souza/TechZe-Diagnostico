import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { 
  FileText, 
  Download, 
  Filter, 
  Search, 
  Calendar,
  User,
  Monitor,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  FileJson,
  Globe
} from "lucide-react";

const Reports = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [dateFilter, setDateFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const reports = [
    {
      id: 1,
      title: "Diagnóstico PC-VENDAS-01",
      customer: "José Silva",
      date: "2024-01-28",
      format: "PDF",
      status: "completed",
      healthScore: 85,
      issues: 2,
      size: "2.3 MB"
    },
    {
      id: 2,
      title: "Relatório Mensal - Janeiro 2024",
      customer: "Sistema",
      date: "2024-01-28",
      format: "HTML",
      status: "generated",
      healthScore: null,
      issues: null,
      size: "1.8 MB"
    },
    {
      id: 3,
      title: "Diagnóstico NOTEBOOK-ADM",
      customer: "Maria Santos",
      date: "2024-01-27",
      format: "JSON",
      status: "processing",
      healthScore: 72,
      issues: 4,
      size: "892 KB"
    },
    {
      id: 4,
      title: "Análise de Tendências Q1",
      customer: "Sistema",
      date: "2024-01-26",
      format: "PDF",
      status: "completed",
      healthScore: null,
      issues: null,
      size: "5.2 MB"
    }
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-500/20 text-green-300">Concluído</Badge>;
      case "generated":
        return <Badge className="bg-blue-500/20 text-blue-300">Gerado</Badge>;
      case "processing":
        return <Badge className="bg-yellow-500/20 text-yellow-300">Processando</Badge>;
      case "failed":
        return <Badge className="bg-red-500/20 text-red-300">Falhou</Badge>;
      default:
        return <Badge className="bg-gray-500/20 text-gray-300">Pendente</Badge>;
    }
  };

  const getFormatIcon = (format: string) => {
    switch (format) {
      case "PDF":
        return <FileText className="w-5 h-5 text-red-400" />;
      case "JSON":
        return <FileJson className="w-5 h-5 text-blue-400" />;
      case "HTML":
        return <Globe className="w-5 h-5 text-green-400" />;
      default:
        return <FileText className="w-5 h-5 text-gray-400" />;
    }
  };

  const generateReport = (type: string) => {
    console.log(`Gerando relatório tipo: ${type}`);
    // Implementar lógica de geração de relatório
  };

  const filteredReports = reports.filter(report => {
    const matchesSearch = report.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         report.customer.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesDate = !dateFilter || report.date.includes(dateFilter);
    const matchesStatus = statusFilter === "all" || report.status === statusFilter;
    
    return matchesSearch && matchesDate && matchesStatus;
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-gray-900 to-black p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Relatórios de Diagnóstico
          </h1>
          <p className="text-gray-200">Visualize, gere e exporte relatórios detalhados</p>
        </div>

        {/* Ações Rápidas */}
        <Card className="bg-black/40 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white">Gerar Novo Relatório</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Button 
                onClick={() => generateReport('diagnostic')}
                className="bg-gradient-to-r from-gray-600 to-gray-800 hover:from-gray-700 hover:to-gray-900 flex items-center gap-2"
              >
                <Monitor className="w-5 h-5" />
                Relatório de Diagnóstico
              </Button>
              <Button 
                onClick={() => generateReport('summary')}
                className="bg-gradient-to-r from-slate-600 to-slate-800 hover:from-slate-700 hover:to-slate-900 flex items-center gap-2"
              >
                <TrendingUp className="w-5 h-5" />
                Resumo Executivo
              </Button>
              <Button 
                onClick={() => generateReport('trends')}
                className="bg-gradient-to-r from-zinc-600 to-zinc-800 hover:from-zinc-700 hover:to-zinc-900 flex items-center gap-2"
              >
                <Calendar className="w-5 h-5" />
                Análise de Tendências
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Filtros */}
        <Card className="bg-black/40 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <Filter className="w-6 h-6" />
              Filtros
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="space-y-2">
                <Label htmlFor="search" className="text-white">Pesquisar</Label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                  <Input
                    id="search"
                    placeholder="Nome do relatório..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10 bg-white/10 border-white/30 text-white placeholder:text-white/50"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="date" className="text-white">Data</Label>
                <Input
                  id="date"
                  type="date"
                  value={dateFilter}
                  onChange={(e) => setDateFilter(e.target.value)}
                  className="bg-white/10 border-white/30 text-white"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="status" className="text-white">Status</Label>
                <select
                  id="status"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="w-full p-2 bg-white/10 border border-white/30 rounded-md text-white"
                >
                  <option value="all">Todos</option>
                  <option value="completed">Concluído</option>
                  <option value="generated">Gerado</option>
                  <option value="processing">Processando</option>
                  <option value="failed">Falhou</option>
                </select>
              </div>

              <div className="space-y-2 flex items-end">
                <Button 
                  variant="outline" 
                  className="w-full border-white/30 text-white hover:bg-white/10"
                  onClick={() => {
                    setSearchTerm("");
                    setDateFilter("");
                    setStatusFilter("all");
                  }}
                >
                  Limpar Filtros
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Lista de Relatórios */}
        <Card className="bg-black/40 backdrop-blur-md border-white/20">
          <CardHeader>
            <CardTitle className="text-white flex items-center gap-2">
              <FileText className="w-6 h-6" />
              Relatórios Disponíveis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {filteredReports.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-400 text-lg">Nenhum relatório encontrado</p>
                  <p className="text-gray-500">Tente ajustar os filtros ou gerar um novo relatório</p>
                </div>
              ) : (
                filteredReports.map((report) => (
                  <div 
                    key={report.id}
                    className="bg-black/20 p-4 rounded-lg border border-white/10 flex flex-wrap gap-4 items-center justify-between"
                  >
                    <div className="flex items-center gap-4 flex-grow">
                      {getFormatIcon(report.format)}
                      <div className="flex-grow">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg text-white font-medium">{report.title}</h3>
                          {getStatusBadge(report.status)}
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-300">
                          <span className="flex items-center gap-1">
                            <User className="w-4 h-4" />
                            {report.customer}
                          </span>
                          <span className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {report.date}
                          </span>
                          <span className="text-gray-400">{report.size}</span>
                        </div>
                      </div>
                    </div>
                    
                    {report.healthScore !== null && (
                      <div className="flex items-center gap-4">
                        <div className="text-center">
                          <p className={`text-lg font-bold ${
                            report.healthScore >= 90 ? 'text-green-400' :
                            report.healthScore >= 70 ? 'text-yellow-400' : 'text-red-400'
                          }`}>
                            {report.healthScore}%
                          </p>
                          <p className="text-xs text-gray-400">Saúde</p>
                        </div>
                        
                        <div className="text-center">
                          <p className="text-lg font-medium text-red-400">{report.issues}</p>
                          <p className="text-xs text-gray-400">Problemas</p>
                        </div>
                      </div>
                    )}

                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="border-white/30 text-white hover:bg-white/10"
                        disabled={report.status === "processing"}
                      >
                        <Download className="w-4 h-4 mr-1" />
                        Download
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Estatísticas dos Relatórios */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="bg-black/40 backdrop-blur-md border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-200 text-sm">Total de Relatórios</p>
                  <p className="text-3xl font-bold text-white">{reports.length}</p>
                </div>
                <FileText className="w-8 h-8 text-gray-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-black/40 backdrop-blur-md border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-200 text-sm">Concluídos</p>
                  <p className="text-3xl font-bold text-green-400">
                    {reports.filter(r => r.status === 'completed').length}
                  </p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-400" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-black/40 backdrop-blur-md border-white/20">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-200 text-sm">Em Processamento</p>
                  <p className="text-3xl font-bold text-yellow-400">
                    {reports.filter(r => r.status === 'processing').length}
                  </p>
                </div>
                <AlertTriangle className="w-8 h-8 text-yellow-400" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default Reports;
