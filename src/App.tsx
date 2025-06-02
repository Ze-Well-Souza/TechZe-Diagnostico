import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/hooks/useAuth";
import ProtectedRoute from "@/components/ProtectedRoute";
import Navbar from "@/components/Navbar";
import Index from "./pages/Index";
import Auth from "./pages/Auth";
import Welcome from "./pages/Welcome";
import Dashboard from "./pages/Dashboard";
import Diagnostic from "./pages/Diagnostic";
import Reports from "./pages/Reports";
import History from "./pages/History";
import Admin from "./pages/Admin";
import FileConverter from "./pages/FileConverter";
import Marketplace from "./pages/Marketplace";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

// Layout wrapper para páginas protegidas
const ProtectedLayout = ({ children }: { children: React.ReactNode }) => (
  <ProtectedRoute>
    <Navbar />
    {children}
  </ProtectedRoute>
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Rotas públicas */}
            <Route path="/" element={<Index />} />
            <Route path="/auth" element={<Auth />} />
            
            {/* Rotas protegidas com layout */}
            <Route path="/welcome" element={
              <ProtectedRoute>
                <Welcome />
              </ProtectedRoute>
            } />
            
            <Route path="/dashboard" element={
              <ProtectedLayout>
                <Dashboard />
              </ProtectedLayout>
            } />
            
            <Route path="/diagnostic" element={
              <ProtectedLayout>
                <Diagnostic />
              </ProtectedLayout>
            } />
            
            <Route path="/reports" element={
              <ProtectedLayout>
                <Reports />
              </ProtectedLayout>
            } />
            
            <Route path="/history" element={
              <ProtectedLayout>
                <History />
              </ProtectedLayout>
            } />
            
            <Route path="/admin" element={
              <ProtectedLayout>
                <Admin />
              </ProtectedLayout>
            } />
            
            <Route path="/file-converter" element={
              <ProtectedLayout>
                <FileConverter />
              </ProtectedLayout>
            } />
            
            <Route path="/marketplace" element={
              <ProtectedLayout>
                <Marketplace />
              </ProtectedLayout>
            } />
            
            {/* Catch-all route para 404 */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
