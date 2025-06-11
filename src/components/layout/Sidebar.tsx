import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  Package, 
  ClipboardList, 
  Calendar, 
  Settings, 
  LogOut,
  Stethoscope,
  BarChart3
} from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

interface MenuItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path: string;
  badge?: string;
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: <LayoutDashboard className="w-5 h-5" />,
    path: '/dashboard'
  },
  {
    id: 'clients',
    label: 'Clientes',
    icon: <Users className="w-5 h-5" />,
    path: '/clients'
  },
  {
    id: 'orcamentos',
    label: 'Orçamentos',
    icon: <FileText className="w-5 h-5" />,
    path: '/orcamentos'
  },
  {
    id: 'estoque',
    label: 'Estoque',
    icon: <Package className="w-5 h-5" />,
    path: '/estoque',
    badge: 'Em breve'
  },
  {
    id: 'ordens',
    label: 'Ordens de Serviço',
    icon: <ClipboardList className="w-5 h-5" />,
    path: '/ordens',
    badge: 'Em breve'
  },
  {
    id: 'agendamentos',
    label: 'Agendamentos',
    icon: <Calendar className="w-5 h-5" />,
    path: '/agendamentos',
    badge: 'Em breve'
  },
  {
    id: 'diagnostic',
    label: 'Diagnóstico',
    icon: <Stethoscope className="w-5 h-5" />,
    path: '/diagnostic'
  },
  {
    id: 'relatorios',
    label: 'Relatórios',
    icon: <BarChart3 className="w-5 h-5" />,
    path: '/relatorios'
  }
];

export default function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const location = useLocation();
  const { user, signOut } = useAuth();

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      console.error('Erro ao fazer logout:', error);
    }
  };

  const isActiveRoute = (path: string) => {
    if (path === '/dashboard') {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  return (
    <>
      {/* Overlay para mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}
      
      {/* Sidebar */}
      <div className={`
        fixed top-0 left-0 h-full bg-white border-r border-gray-200 z-50
        transform transition-transform duration-300 ease-in-out
        ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:z-auto
        w-64 flex flex-col
      `}>
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <Stethoscope className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">TechZe</h1>
              <p className="text-sm text-gray-600">Diagnóstico</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item) => {
            const isActive = isActiveRoute(item.path);
            const isDisabled = item.badge === 'Em breve';
            
            if (isDisabled) {
              return (
                <div
                  key={item.id}
                  className="flex items-center justify-between px-3 py-2 text-gray-400 cursor-not-allowed"
                >
                  <div className="flex items-center gap-3">
                    {item.icon}
                    <span className="font-medium">{item.label}</span>
                  </div>
                  {item.badge && (
                    <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </div>
              );
            }
            
            return (
              <Link
                key={item.id}
                to={item.path}
                onClick={onClose}
                className={`
                  flex items-center justify-between px-3 py-2 rounded-lg transition-colors
                  ${isActive 
                    ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-700' 
                    : 'text-gray-700 hover:bg-gray-50'
                  }
                `}
              >
                <div className="flex items-center gap-3">
                  {item.icon}
                  <span className="font-medium">{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`
                    px-2 py-1 text-xs rounded-full
                    ${isActive 
                      ? 'bg-blue-100 text-blue-800' 
                      : 'bg-gray-100 text-gray-600'
                    }
                  `}>
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* User Section */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-gray-700">
                {user?.email?.charAt(0).toUpperCase()}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.email}
              </p>
              <p className="text-xs text-gray-600">Técnico</p>
            </div>
          </div>
          
          <div className="space-y-2">
            <Link
              to="/configuracoes"
              className="flex items-center gap-3 px-3 py-2 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
              onClick={onClose}
            >
              <Settings className="w-4 h-4" />
              <span className="text-sm">Configurações</span>
            </Link>
            
            <Button
              variant="ghost"
              onClick={handleSignOut}
              className="w-full justify-start gap-3 px-3 py-2 text-gray-700 hover:bg-gray-50"
            >
              <LogOut className="w-4 h-4" />
              <span className="text-sm">Sair</span>
            </Button>
          </div>
        </div>
      </div>
    </>
  );
}