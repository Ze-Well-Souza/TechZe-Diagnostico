import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { PWAProvider } from '@/contexts/PWAContext';
import { AuthProvider } from '@/contexts/AuthContext';
import { NotificationProvider } from '@/contexts/NotificationContext';
import ProtectedRoute from '@/components/ProtectedRoute';
import PWANotification from '@/components/PWANotification';

// Componentes críticos carregados imediatamente
import Index from '@/pages/Index';
import Auth from '@/pages/Auth';
import NotFound from '@/pages/NotFound';

// Lazy loading para páginas não críticas
const Dashboard = lazy(() => import('@/pages/Dashboard'));
const DashboardGlobal = lazy(() => import('@/pages/DashboardGlobal'));
const ClientesManagement = lazy(() => import('@/pages/ClientesManagement'));
const LoginAdmin = lazy(() => import('@/pages/LoginAdmin').then(module => ({ default: module.LoginAdmin })));
const GestaoLojas = lazy(() => import('@/pages/GestaoLojas').then(module => ({ default: module.GestaoLojas })));
const Diagnostic = lazy(() => import('@/pages/Diagnostic'));
const Orcamentos = lazy(() => import('@/pages/Orcamentos'));
const NovoOrcamento = lazy(() => import('@/pages/Orcamentos/NovoOrcamento'));
const DetalhesOrcamento = lazy(() => import('@/pages/Orcamentos/DetalhesOrcamento'));
const PortalCliente = lazy(() => import('@/pages/PortalCliente'));
const Agendamento = lazy(() => import('@/pages/Agendamento'));
const Estoque = lazy(() => import('@/pages/Estoque'));
const Configuracoes = lazy(() => import('@/pages/Configuracoes'));
const Relatorios = lazy(() => import('@/pages/Relatorios'));

// Componente de loading customizado
const PageLoader = () => (
  <div className="min-h-screen bg-background flex items-center justify-center">
    <div className="flex flex-col items-center space-y-4">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      <p className="text-sm text-muted-foreground">Carregando...</p>
    </div>
  </div>
);

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
              <Suspense fallback={<PageLoader />}>
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
              </Suspense>
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
