
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { TechButton } from '@/components/ui/tech-button';
import { 
  Wrench, 
  Home, 
  Activity, 
  FileText, 
  History, 
  Settings,
  Menu,
  X,
  LogOut,
  User
} from 'lucide-react';

export const TechNavbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, signOut } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: Home },
    { path: '/diagnostic', label: 'Diagnóstico', icon: Activity },
    { path: '/reports', label: 'Relatórios', icon: FileText },
    { path: '/history', label: 'Histórico', icon: History },
    { path: '/admin', label: 'Admin', icon: Settings },
  ];

  const handleLogout = async () => {
    await signOut();
    navigate('/auth');
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <motion.nav 
      className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-white/10"
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.div 
            className="flex items-center gap-3 cursor-pointer"
            onClick={() => navigate(user ? '/dashboard' : '/')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <div className="p-2 bg-gradient-to-r from-blue-600 to-green-600 rounded-lg">
              <Wrench className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-white font-display">TechRepair</span>
          </motion.div>

          {/* Desktop Navigation */}
          {user && (
            <div className="hidden md:flex items-center gap-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <motion.button
                    key={item.path}
                    onClick={() => navigate(item.path)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive(item.path)
                        ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                        : 'text-gray-300 hover:text-white hover:bg-white/10'
                    }`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </motion.button>
                );
              })}
            </div>
          )}

          {/* User Menu / Auth Button */}
          <div className="flex items-center gap-4">
            {user ? (
              <>
                <div className="hidden md:flex items-center gap-2 text-white">
                  <User className="w-4 h-4" />
                  <span className="text-sm">{user.email}</span>
                </div>
                <TechButton
                  variant="outline"
                  size="sm"
                  icon={LogOut}
                  onClick={handleLogout}
                >
                  Sair
                </TechButton>
              </>
            ) : (
              <TechButton
                variant="primary"
                size="sm"
                onClick={() => navigate('/auth')}
              >
                Acessar Sistema
              </TechButton>
            )}

            {/* Mobile Menu Button */}
            {user && (
              <button
                className="md:hidden p-2 text-white hover:bg-white/10 rounded-lg"
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            )}
          </div>
        </div>

        {/* Mobile Menu */}
        {user && mobileMenuOpen && (
          <motion.div
            className="md:hidden py-4 border-t border-white/10"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <div className="flex flex-col gap-2">
              {navItems.map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.path}
                    onClick={() => {
                      navigate(item.path);
                      setMobileMenuOpen(false);
                    }}
                    className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      isActive(item.path)
                        ? 'bg-blue-600/20 text-blue-400'
                        : 'text-gray-300 hover:text-white hover:bg-white/10'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {item.label}
                  </button>
                );
              })}
              <div className="flex items-center gap-2 px-3 py-2 text-gray-400 text-sm border-t border-white/10 mt-2 pt-4">
                <User className="w-4 h-4" />
                {user.email}
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </motion.nav>
  );
};
