import React, { useState } from 'react';
import { Store, Plus, Edit, Trash2, MapPin, Users, Activity } from 'lucide-react';
import { GlassCard } from '../components/ui/GlassCard';

interface Loja {
  id: string;
  nome: string;
  endereco: string;
  cidade: string;
  telefone: string;
  email: string;
  administrador: string;
  status: 'Ativa' | 'Inativa' | 'Manutenção';
  dispositivos: number;
  usuarios: number;
  saude: number;
}

export const GestaoLojas: React.FC = () => {
  const [lojas] = useState<Loja[]>([
    {
      id: '1',
      nome: 'TechRepair Centro',
      endereco: 'Av. Paulista, 1000',
      cidade: 'São Paulo - SP',
      telefone: '(11) 9999-1111',
      email: 'centro@techrepair.com',
      administrador: 'João Silva',
      status: 'Ativa',
      dispositivos: 45,
      usuarios: 23,
      saude: 89
    },
    {
      id: '2',
      nome: 'TechRepair Norte',
      endereco: 'Rua das Flores, 500',
      cidade: 'São Paulo - SP', 
      telefone: '(11) 9999-2222',
      email: 'norte@techrepair.com',
      administrador: 'Maria Santos',
      status: 'Ativa',
      dispositivos: 32,
      usuarios: 18,
      saude: 91
    }
  ]);

  const [searchTerm, setSearchTerm] = useState('');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Ativa': return 'bg-green-500/20 text-green-300 border-green-500/30';
      case 'Inativa': return 'bg-red-500/20 text-red-300 border-red-500/30';
      case 'Manutenção': return 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30';
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/30';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Gestão de Lojas</h1>
          <p className="text-gray-300">Gerencie todas as lojas da rede TechRepair</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          {lojas.map((loja) => (
            <GlassCard key={loja.id} className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg">
                    <Store className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">{loja.nome}</h3>
                    <span className={`px-3 py-1 rounded-full text-xs border ${getStatusColor(loja.status)}`}>
                      {loja.status}
                    </span>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex items-center space-x-2 text-gray-300">
                  <MapPin className="w-4 h-4" />
                  <span className="text-sm">{loja.endereco}</span>
                </div>
                <div className="text-gray-300 text-sm">{loja.cidade}</div>
                <div className="text-gray-300 text-sm">
                  <strong>Admin:</strong> {loja.administrador}
                </div>
                
                <div className="grid grid-cols-3 gap-4 pt-4 border-t border-white/10">
                  <div className="text-center">
                    <div className="text-lg font-semibold text-white">{loja.dispositivos}</div>
                    <div className="text-xs text-gray-400">Dispositivos</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-white">{loja.usuarios}</div>
                    <div className="text-xs text-gray-400">Usuários</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-green-400">{loja.saude}%</div>
                    <div className="text-xs text-gray-400">Saúde</div>
                  </div>
                </div>
              </div>
            </GlassCard>
          ))}
        </div>
      </div>
    </div>
  );
}; 