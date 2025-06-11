import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { PWAProvider } from '@/contexts/PWAContext';
import { AuthProvider } from '@/contexts/AuthContext';
import { NotificationProvider } from '@/contexts/NotificationContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import PWANotification from '@/components/PWANotification';
import Index from '@/pages/Index';
import Auth from '@/pages/Auth';
import Dashboard from '@/pages/Dashboard';
import DashboardGlobal from '@/pages/DashboardGlobal';
import ClientesManagement from '@/pages/ClientesManagement';
import { LoginAdmin } from '@/pages/LoginAdmin';
import { GestaoLojas } from '@/pages/GestaoLojas';
import Diagnostic from '@/pages/Diagnostic';
import NotFound from '@/pages/NotFound';
import Orcamentos from '@/pages/Orcamentos';
import NovoOrcamento from '@/pages/Orcamentos/NovoOrcamento';
import DetalhesOrcamento from '@/pages/Orcamentos/DetalhesOrcamento';
import PortalCliente from '@/pages/PortalCliente';
import Agendamento from '@/pages/Agendamento';
import Estoque from '@/pages/Estoque';
import Configuracoes from '@/pages/Configuracoes';
import Relatorios from '@/pages/Relatorios';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutos
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <NotificationProvider>
          <PWAProvider>
            <Router>
            <div className="min-h-screen bg-background">
              <Routes>
                <Route path="/" element={<Index />} />
                <Route path="/auth" element={<Auth />} />
                <Route path="/admin-login" element={<LoginAdmin />} />
                <Route 
                  path="/dashboard" 
                  element={
                    <ProtectedRoute>
                      <Dashboard />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/dashboard-global" 
                  element={
                    <ProtectedRoute>
                      <DashboardGlobal />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/clientes" 
                  element={
                    <ProtectedRoute>
                      <ClientesManagement />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/admin/lojas" 
                  element={
                    <ProtectedRoute>
                      <GestaoLojas />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/orcamentos" 
                  element={
                    <ProtectedRoute>
                      <Orcamentos />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/orcamentos/novo" 
                  element={
                    <ProtectedRoute>
                      <NovoOrcamento />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/orcamentos/:id" 
                  element={
                    <ProtectedRoute>
                      <DetalhesOrcamento />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/diagnostic" 
                  element={
                    <ProtectedRoute>
                      <Diagnostic />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/portal-cliente" 
                  element={
                    <ProtectedRoute>
                      <PortalCliente />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/agendamento" 
                  element={
                    <ProtectedRoute>
                      <Agendamento />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/estoque" 
                  element={
                    <ProtectedRoute>
                      <Estoque />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/configuracoes" 
                  element={
                    <ProtectedRoute>
                      <Configuracoes />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/relatorios" 
                  element={
                    <ProtectedRoute>
                      <Relatorios />
                    </ProtectedRoute>
                  } 
                />
                <Route path="*" element={<NotFound />} />
              </Routes>
              <Toaster />
            </div>
          </Router>
        </PWAProvider>
      </NotificationProvider>
    </AuthProvider>
  </QueryClientProvider>
  );
}

export default App;
