import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { Filter, Search, ChevronLeft, ChevronRight, Calendar, Laptop } from 'lucide-react';

// Components
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Calendar as CalendarComponent } from '@/components/ui/calendar';

// Services
import { diagnosticApiService } from '../services/diagnosticApiService';

// Types
import { DiagnosticResult, Device } from '../types/diagnostic';

const History = () => {
  // Estado para armazenar os diagnósticos e dispositivos
  const [devices, setDevices] = useState<Device[]>([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  // Estado para paginação
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(10);

  // Estado para filtros
  const [searchTerm, setSearchTerm] = useState('');
  const [deviceFilter, setDeviceFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [dateFilter, setDateFilter] = useState<Date | undefined>(undefined);

  // Buscar histórico de diagnósticos com filtros e paginação
  const { data: diagnosticsResponse, isLoading: isLoadingDiagnostics, refetch } = useQuery({
    queryKey: ['diagnostic-history', currentPage, itemsPerPage, deviceFilter, statusFilter, dateFilter],
    queryFn: async () => {
      try {
        const response = await diagnosticApiService.getDiagnosticHistory({
          page: currentPage,
          limit: itemsPerPage,
          device_id: deviceFilter !== 'all' ? deviceFilter : undefined,
          status: statusFilter !== 'all' ? statusFilter : undefined,
          start_date: dateFilter ? dateFilter.toISOString().split('T')[0] : undefined,
          end_date: dateFilter ? dateFilter.toISOString().split('T')[0] : undefined,
        });
        
        // Atualizar estados de paginação
        setTotalItems(response.total);
        setTotalPages(response.pages);
        
        return response;
      } catch (error) {
        console.error('Erro ao buscar diagnósticos:', error);
        return { data: [], total: 0, page: 1, limit: itemsPerPage, pages: 1 };
      }
    },
  });

  // Buscar dispositivos
  const { data: devicesData, isLoading: isLoadingDevices } = useQuery({
    queryKey: ['devices'],
    queryFn: async () => {
      try {
        const data = await diagnosticApiService.getDevices();
        setDevices(data);
        return data;
      } catch (error) {
        console.error('Erro ao buscar dispositivos:', error);
        return [];
      }
    },
  });

  // Extrair dados da resposta
  const diagnostics = diagnosticsResponse?.data || [];

  // Aplicar filtro de busca local (apenas para ID e device_id)
  const filteredDiagnostics = diagnostics.filter((diagnostic) => {
    if (searchTerm === '') return true;
    return diagnostic.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
           diagnostic.device_id.toLowerCase().includes(searchTerm.toLowerCase());
  });

  const currentItems = filteredDiagnostics;

  // Refetch quando filtros mudarem
  useEffect(() => {
    refetch();
  }, [deviceFilter, statusFilter, dateFilter, refetch]);

  // Função para obter nome do dispositivo
  const getDeviceName = (deviceId: string) => {
    const device = devices?.find(d => d.id === deviceId);
    return device ? device.name : 'Dispositivo desconhecido';
  };

  // Função para formatar data
  const formatDate = (dateString: string) => {
    return format(new Date(dateString), "dd 'de' MMMM 'de' yyyy, HH:mm", { locale: ptBR });
  };

  // Função para obter cor do status
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 text-green-500 hover:bg-green-500/30';
      case 'running':
        return 'bg-blue-500/20 text-blue-500 hover:bg-blue-500/30';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-500 hover:bg-yellow-500/30';
      case 'failed':
        return 'bg-red-500/20 text-red-500 hover:bg-red-500/30';
      default:
        return 'bg-gray-500/20 text-gray-500 hover:bg-gray-500/30';
    }
  };

  // Função para traduzir status
  const translateStatus = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Concluído';
      case 'running':
        return 'Em execução';
      case 'pending':
        return 'Pendente';
      case 'failed':
        return 'Falhou';
      default:
        return status;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 pt-24">
      <div className="flex flex-col space-y-8">
        {/* Cabeçalho */}
        <div className="flex flex-col space-y-2">
          <h1 className="text-3xl font-bold tracking-tight">Histórico de Diagnósticos</h1>
          <p className="text-muted-foreground">
            Visualize e analise o histórico completo de diagnósticos realizados em seus dispositivos.
          </p>
        </div>

        {/* Filtros */}
        <div className="flex flex-col md:flex-row gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Buscar por ID..."
              className="pl-8"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <Select
            value={deviceFilter}
            onValueChange={setDeviceFilter}
          >
            <SelectTrigger className="w-full md:w-[200px]">
              <SelectValue placeholder="Filtrar por dispositivo" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os dispositivos</SelectItem>
              {devices?.map((device) => (
                <SelectItem key={device.id} value={device.id}>
                  {device.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Select
            value={statusFilter}
            onValueChange={setStatusFilter}
          >
            <SelectTrigger className="w-full md:w-[180px]">
              <SelectValue placeholder="Filtrar por status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos os status</SelectItem>
              <SelectItem value="completed">Concluído</SelectItem>
              <SelectItem value="running">Em execução</SelectItem>
              <SelectItem value="pending">Pendente</SelectItem>
              <SelectItem value="failed">Falhou</SelectItem>
            </SelectContent>
          </Select>
          
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className="w-full md:w-[240px] justify-start text-left font-normal"
              >
                <Calendar className="mr-2 h-4 w-4" />
                {dateFilter ? (
                  format(dateFilter, "dd 'de' MMMM 'de' yyyy", { locale: ptBR })
                ) : (
                  <span>Filtrar por data</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <CalendarComponent
                mode="single"
                selected={dateFilter}
                onSelect={setDateFilter}
                initialFocus
              />
              {dateFilter && (
                <div className="p-3 border-t border-border">
                  <Button
                    variant="ghost"
                    className="w-full"
                    onClick={() => setDateFilter(undefined)}
                  >
                    Limpar filtro
                  </Button>
                </div>
              )}
            </PopoverContent>
          </Popover>
        </div>

        {/* Lista de diagnósticos */}
        <div className="space-y-4">
          {isLoadingDiagnostics || isLoadingDevices ? (
            // Esqueleto de carregamento
            Array.from({ length: 5 }).map((_, index) => (
              <Card key={index} className="bg-card/50">
                <CardHeader className="pb-2">
                  <Skeleton className="h-6 w-1/3" />
                  <Skeleton className="h-4 w-1/4" />
                </CardHeader>
                <CardContent>
                  <div className="flex justify-between">
                    <Skeleton className="h-4 w-1/5" />
                    <Skeleton className="h-6 w-24" />
                  </div>
                </CardContent>
              </Card>
            ))
          ) : currentItems.length > 0 ? (
            currentItems.map((diagnostic) => (
              <Card key={diagnostic.id} className="bg-card/50 hover:bg-card/80 transition-colors">
                <CardHeader className="pb-2">
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">
                        <div className="flex items-center gap-2">
                          <Laptop className="h-4 w-4" />
                          {getDeviceName(diagnostic.device_id)}
                        </div>
                      </CardTitle>
                      <CardDescription>
                        {formatDate(diagnostic.created_at)}
                      </CardDescription>
                    </div>
                    <Badge className={getStatusColor(diagnostic.status)}>
                      {translateStatus(diagnostic.status)}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium">ID do Diagnóstico</p>
                      <p className="text-sm text-muted-foreground">{diagnostic.id}</p>
                    </div>
                    {diagnostic.health_score !== undefined && (
                      <div>
                        <p className="text-sm font-medium">Pontuação de Saúde</p>
                        <p className="text-sm text-muted-foreground">{diagnostic.health_score}/100</p>
                      </div>
                    )}
                  </div>
                </CardContent>
                <CardFooter>
                  <Button variant="outline" className="w-full">
                    Ver Detalhes
                  </Button>
                </CardFooter>
              </Card>
            ))
          ) : (
            <Card className="bg-card/50">
              <CardContent className="flex flex-col items-center justify-center py-8">
                <p className="text-muted-foreground text-center">
                  Nenhum diagnóstico encontrado com os filtros selecionados.
                </p>
                <Button
                    variant="outline"
                    className="mt-4"
                    onClick={() => {
                      setSearchTerm('');
                      setDeviceFilter('all');
                      setStatusFilter('all');
                      setDateFilter(undefined);
                      setCurrentPage(1);
                    }}
                  >
                    Limpar filtros
                  </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Paginação */}
        {totalItems > 0 && (
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Mostrando {((currentPage - 1) * itemsPerPage) + 1}-{Math.min(currentPage * itemsPerPage, totalItems)} de {totalItems} resultados
            </p>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="icon"
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1 || isLoadingDiagnostics}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <div className="text-sm">
                Página {currentPage} de {totalPages || 1}
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages || totalPages === 0 || isLoadingDiagnostics}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default History;