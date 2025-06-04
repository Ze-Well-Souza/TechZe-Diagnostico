
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Header } from "./components/layout/Header";
import { CompanyProvider } from "./contexts/CompanyContext";
import { AuthProvider } from "./hooks/useAuth";
import { ProtectedRoute } from "./components/ProtectedRoute";
import Landing from "./pages/Landing";
import Auth from "./pages/Auth";
import { Dashboard } from "./pages/Dashboard";
import Diagnostic from "./pages/Diagnostic";
import History from "./pages/History";
import Reports from "./pages/Reports";
import AdminCompanies from "./pages/AdminCompanies";
import AdminEmployees from "./pages/AdminEmployees";
import FileConverter from "./pages/FileConverter";
import Marketplace from "./pages/Marketplace";
import WhatsAppConfig from "./pages/WhatsAppConfig";
import NotFound from "./pages/NotFound";
import { InstallPWABanner } from './components/ui/InstallPWABanner';
import { OfflineIndicator } from './components/ui/OfflineIndicator';

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <CompanyProvider>
        <AuthProvider>
          <OfflineIndicator />
          <InstallPWABanner />
          <Toaster />
          <Sonner />
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Landing />} />
              <Route path="/auth" element={<Auth />} />
              <Route path="/dashboard" element={
                <ProtectedRoute>
                  <Header />
                  <Dashboard />
                </ProtectedRoute>
              } />
              <Route path="/diagnostic" element={
                <ProtectedRoute>
                  <Header />
                  <Diagnostic />
                </ProtectedRoute>
              } />
              <Route path="/history" element={
                <ProtectedRoute>
                  <Header />
                  <History />
                </ProtectedRoute>
              } />
              <Route path="/reports" element={
                <ProtectedRoute>
                  <Header />
                  <Reports />
                </ProtectedRoute>
              } />
              <Route path="/admin/companies" element={
                <ProtectedRoute>
                  <Header />
                  <AdminCompanies />
                </ProtectedRoute>
              } />
              <Route path="/admin/employees" element={
                <ProtectedRoute>
                  <Header />
                  <AdminEmployees />
                </ProtectedRoute>
              } />
              <Route path="/file-converter" element={
                <ProtectedRoute>
                  <Header />
                  <FileConverter />
                </ProtectedRoute>
              } />
              <Route path="/marketplace" element={
                <ProtectedRoute>
                  <Header />
                  <Marketplace />
                </ProtectedRoute>
              } />
              <Route path="/whatsapp-config" element={
                <ProtectedRoute>
                  <Header />
                  <WhatsAppConfig />
                </ProtectedRoute>
              } />
              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </CompanyProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
