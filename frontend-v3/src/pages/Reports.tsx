import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { SendQuoteModal } from '@/components/SendQuoteModal';
import { 
  FileText, 
  Download, 
  Send, 
  DollarSign, 
  Search,
  Filter,
  TrendingUp,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';

export default function Reports() {
  const [searchTerm, setSearchTerm] = useState('');

  const reports = [
    {
      id: 1,
      clientName: 'João Silva',
      company: 'Empresa A',
      device: 'PC Gaming - Intel i7',
      date: '2024-06-02',
      status: 'Concluído',
      overallScore: 78,
      problems: ['HD com setores defeituosos', 'Driver de vídeo desatualizado', 'Memória RAM com velocidade baixa'],
      estimatedCost: 450.00
    },
    {
      id: 2,
      clientName: 'Maria Santos',
      company: 'Empresa B', 
      device: 'Laptop Dell Inspiron',
      date: '2024-06-01',
      status: 'Em Andamento',
      overallScore: 65,
      problems: ['Bateria com baixa capacidade', 'Sistema superaquecendo', 'Antivírus desatualizado', 'Fragmentação de disco', 'Driver de rede desatualizado'],
      estimatedCost: 680.00
    },
    {
      id: 3,
      clientName: 'Carlos Oliveira',
      company: 'Empresa C',
      device: 'Workstation HP',
      date: '2024-05-30',
      status: 'Orçamento Enviado',
      overallScore: 82,
      problems: ['Limpeza necessária', 'Troca de pasta térmica'],
      estimatedCost: 320.00
    }
  ];

  const stats = [
    {
      title: 'Relatórios Gerados',
      value: '156',
      change: '+12%',
      icon: <FileText className="h-4 w-4" />,
      trend: 'up'
    },
    {
      title: 'Orçamentos Enviados',
      value: '89',
      change: '+23%',
      icon: <DollarSign className="h-4 w-4" />,
      trend: 'up'
    },
    {
      title: 'Taxa de Aprovação',
      value: '76%',
      change: '+8%',
      icon: <CheckCircle className="h-4 w-4" />,
      trend: 'up'
    },
    {
      title: 'Valor Médio',
      value: 'R$ 485',
      change: '+15%',
      icon: <TrendingUp className="h-4 w-4" />,
      trend: 'up'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Concluído':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'Em Andamento':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'Orçamento Enviado':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const filteredReports = reports.filter(report =>
    report.clientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    report.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
    report.device.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-black">
      <main className="pt-20 pb-10 px-4 sm:px-6 lg:px-8">
        <div className="container mx-auto max-w-7xl">
          
          
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Relatórios e Orçamentos</h1>
              <p className="text-gray-400">Gerencie relatórios de diagnóstico e orçamentos para clientes</p>
            </div>
            <div className="flex gap-3 mt-4 md:mt-0">
              <Button variant="outline" className="border-electric/50 text-electric hover:bg-electric/10">
                <Filter className="mr-2 h-4 w-4" />
                Filtros
              </Button>
              <Button className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80 text-black">
                <FileText className="mr-2 h-4 w-4" />
                Novo Relatório
              </Button>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, index) => (
              <Card key={index} className="bg-dark/50 border-white/10 hover:border-electric/30 transition-all duration-300">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-gray-400">
                    {stat.title}
                  </CardTitle>
                  <div className="text-electric">
                    {stat.icon}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-white mb-1">
                    {stat.value}
                  </div>
                  <p className={`text-xs flex items-center ${
                    stat.trend === 'up' ? 'text-green-400' : 'text-red-400'
                  }`}>
                    <TrendingUp className="mr-1 h-3 w-3" />
                    {stat.change} vs último mês
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Search */}
          <Card className="bg-dark/50 border-white/10 mb-8">
            <CardContent className="p-6">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <Label htmlFor="search" className="text-white mb-2 block">Buscar Relatórios</Label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                    <Input
                      id="search"
                      placeholder="Buscar por cliente, empresa ou dispositivo..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10 bg-darker border-white/20 text-white"
                    />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Reports List */}
          <div className="grid gap-6">
            {filteredReports.map((report) => (
              <Card key={report.id} className="bg-dark/50 border-white/10 hover:border-electric/30 transition-all duration-300">
                <CardContent className="p-6">
                  <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-3">
                        <h3 className="text-xl font-semibold text-white">{report.clientName}</h3>
                        <Badge className={getStatusColor(report.status)}>
                          {report.status}
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-gray-400">Empresa:</span>
                          <span className="text-white ml-2">{report.company}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Dispositivo:</span>
                          <span className="text-white ml-2">{report.device}</span>
                        </div>
                        <div>
                          <span className="text-gray-400">Data:</span>
                          <span className="text-white ml-2">{new Date(report.date).toLocaleDateString('pt-BR')}</span>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-6 mt-4">
                        <div className="flex items-center gap-2">
                          <span className="text-gray-400">Score:</span>
                          <span className={`font-bold ${getScoreColor(report.overallScore)}`}>
                            {report.overallScore}%
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4 text-red-400" />
                          <span className="text-white">{report.problems.length} problemas</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <DollarSign className="h-4 w-4 text-green-400" />
                          <span className="text-white">R$ {report.estimatedCost.toFixed(2)}</span>
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-col sm:flex-row gap-3">
                      <Button 
                        variant="outline" 
                        size="sm"
                        className="border-electric/50 text-electric hover:bg-electric/10"
                      >
                        <FileText className="mr-2 h-4 w-4" />
                        Ver Relatório
                      </Button>
                      <Button 
                        variant="outline" 
                        size="sm"
                        className="border-white/20 text-white hover:bg-white/10"
                      >
                        <Download className="mr-2 h-4 w-4" />
                        Download PDF
                      </Button>
                      <SendQuoteModal
                        clientName={report.clientName}
                        deviceInfo={report.device}
                        estimatedCost={report.estimatedCost}
                        problems={report.problems}
                        trigger={
                          <Button 
                            size="sm"
                            className="bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 text-white"
                          >
                            <Send className="mr-2 h-4 w-4" />
                            Enviar Orçamento
                          </Button>
                        }
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredReports.length === 0 && (
            <Card className="bg-dark/50 border-white/10">
              <CardContent className="text-center p-12">
                <FileText className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">Nenhum relatório encontrado</h3>
                <p className="text-gray-400 mb-6">
                  {searchTerm ? 'Tente ajustar os filtros de busca.' : 'Comece criando seu primeiro relatório de diagnóstico.'}
                </p>
                <Button className="bg-gradient-to-r from-electric to-tech hover:from-electric/80 hover:to-tech/80 text-black">
                  <FileText className="mr-2 h-4 w-4" />
                  Criar Primeiro Relatório
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </main>
    </div>
  );
}
