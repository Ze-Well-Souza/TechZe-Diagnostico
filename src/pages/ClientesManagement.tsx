import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { GlassCard } from '@/components/ui/GlassCard';
import { 
  Users, 
  Plus, 
  Search, 
  Filter,
  Star,
  MapPin,
  Phone,
  Mail,
  ArrowLeft,
  LogOut,
  Building2
} from 'lucide-react';

interface Cliente {
  id: number;
  nome: string;
  empresa: string;
  email: string;
  telefone: string;
  status: 'Ativo' | 'Inativo' | 'Pendente';
  loja: string;
  ultima_atividade: string;
  satisfacao: number | null;
}

export default function ClientesManagement() {
  const { user, signOut } = useAuth();
  const [clientes] = useState<Cliente[]>([
    {
      id: 1,
      nome: "João Silva",
      empresa: "TechCorp Ltda",
      email: "joao@techcorp.com",
      telefone: "(11) 99999-1234",
      status: "Ativo",
      loja: "Centro",
      ultima_atividade: "2025-01-09",
      satisfacao: 4.8
    },
    {
      id: 2,
      nome: "Maria Santos",
      empresa: "Digital Solutions",
      email: "maria@digital.com",
      telefone: "(11) 88888-5678",
      status: "Ativo",
      loja: "Norte",
      ultima_atividade: "2025-01-08",
      satisfacao: 4.9
    }
  ]);

  const [filtros, setFiltros] = useState({
    busca: '',
    status: 'todos',
    loja: 'todas'
  });

  const estatisticas = {
    total_clientes: clientes.length,
    novos_mes: 23,
    tickets_abertos: 15,
    satisfacao_media: 4.7
  };

  const clientesFiltrados = clientes.filter(cliente => {
    const matchBusca = cliente.nome.toLowerCase().includes(filtros.busca.toLowerCase());
    const matchStatus = filtros.status === 'todos' || cliente.status === filtros.status;
    const matchLoja = filtros.loja === 'todas' || cliente.loja === filtros.loja;
    return matchBusca && matchStatus && matchLoja;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Ativo': return 'text-green-400 bg-green-400/10 border-green-400/20';
      case 'Inativo': return 'text-red-400 bg-red-400/10 border-red-400/20';
      case 'Pendente': return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20';
      default: return 'text-slate-400 bg-slate-400/10 border-slate-400/20';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="p-6">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link to="/dashboard-global">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Dashboard Global
                </Button>
              </Link>
              <div className="flex items-center space-x-3">
                <div className="p-2 rounded-lg bg-blue-500/20 border border-blue-500/30">
                  <Users className="h-6 w-6 text-blue-400" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-white">
                    Gestão de Clientes
                  </h1>
                  <p className="text-slate-400">
                    Gerencie todos os clientes do sistema
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm" onClick={signOut}>
                <LogOut className="h-4 w-4 mr-2" />
                Sair
              </Button>
            </div>
          </div>
        </header>

        {/* Estatísticas */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <GlassCard className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Total de Clientes</p>
                <p className="text-3xl font-bold text-white">{estatisticas.total_clientes}</p>
              </div>
              <Users className="w-8 h-8 text-blue-400" />
            </div>
          </GlassCard>

          <GlassCard className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Novos este Mês</p>
                <p className="text-3xl font-bold text-white">{estatisticas.novos_mes}</p>
              </div>
              <Plus className="w-8 h-8 text-green-400" />
            </div>
          </GlassCard>

          <GlassCard className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Tickets Abertos</p>
                <p className="text-3xl font-bold text-white">{estatisticas.tickets_abertos}</p>
              </div>
              <Building2 className="w-8 h-8 text-yellow-400" />
            </div>
          </GlassCard>

          <GlassCard className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-400">Satisfação Média</p>
                <p className="text-3xl font-bold text-white">{estatisticas.satisfacao_media}</p>
              </div>
              <Star className="w-8 h-8 text-purple-400" />
            </div>
          </GlassCard>
        </div>

        {/* Filtros e Busca */}
        <GlassCard className="p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Buscar clientes..."
                  value={filtros.busca}
                  onChange={(e) => setFiltros(prev => ({ ...prev, busca: e.target.value }))}
                  className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
                />
              </div>
            </div>
            
            <select
              value={filtros.status}
              onChange={(e) => setFiltros(prev => ({ ...prev, status: e.target.value }))}
              className="px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="todos">Todos os Status</option>
              <option value="Ativo">Ativo</option>
              <option value="Inativo">Inativo</option>
              <option value="Pendente">Pendente</option>
            </select>

            <select
              value={filtros.loja}
              onChange={(e) => setFiltros(prev => ({ ...prev, loja: e.target.value }))}
              className="px-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="todas">Todas as Lojas</option>
              <option value="Centro">Centro</option>
              <option value="Norte">Norte</option>
              <option value="Sul">Sul</option>
            </select>

            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Novo Cliente
            </Button>
          </div>
        </GlassCard>

        {/* Grid de Clientes */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clientesFiltrados.map(cliente => (
            <GlassCard key={cliente.id} className="p-6 hover:scale-105 transition-all duration-300">
              <div className="space-y-4">
                {/* Header do Card */}
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-white">{cliente.nome}</h3>
                    <p className="text-sm text-slate-400">{cliente.empresa}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs border ${getStatusColor(cliente.status)}`}>
                    {cliente.status}
                  </span>
                </div>

                {/* Informações de Contato */}
                <div className="space-y-2">
                  <div className="flex items-center space-x-2 text-sm text-slate-300">
                    <Mail className="w-4 h-4 text-slate-400" />
                    <span>{cliente.email}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-slate-300">
                    <Phone className="w-4 h-4 text-slate-400" />
                    <span>{cliente.telefone}</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-slate-300">
                    <MapPin className="w-4 h-4 text-slate-400" />
                    <span>Loja {cliente.loja}</span>
                  </div>
                </div>

                {/* Satisfação e Última Atividade */}
                <div className="flex items-center justify-between pt-4 border-t border-slate-700/50">
                  <div className="text-sm text-slate-400">
                    Última atividade: {new Date(cliente.ultima_atividade).toLocaleDateString('pt-BR')}
                  </div>
                  {cliente.satisfacao && (
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="text-sm text-yellow-400">{cliente.satisfacao}</span>
                    </div>
                  )}
                </div>

                {/* Ações */}
                <div className="flex space-x-2 pt-2">
                  <Button variant="outline" size="sm" className="flex-1">
                    Editar
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    Contatar
                  </Button>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>

        {clientesFiltrados.length === 0 && (
          <div className="text-center py-12">
            <Users className="w-16 h-16 text-slate-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-400 mb-2">
              Nenhum cliente encontrado
            </h3>
            <p className="text-slate-500">
              Tente ajustar os filtros ou adicione um novo cliente
            </p>
          </div>
        )}
      </div>
    </div>
  );
} 