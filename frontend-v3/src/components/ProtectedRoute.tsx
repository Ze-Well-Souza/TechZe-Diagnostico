import { ReactNode, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

interface ProtectedRouteProps {
  children: ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  useEffect(() => {
    if (!loading && !user) {
      console.log('Acesso não autorizado à rota protegida:', location.pathname);
    }
  }, [loading, user, location.pathname]);

  if (loading) {
    // Exibir um indicador de carregamento enquanto verifica a autenticação
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-electric"></div>
      </div>
    );
  }

  // Redirecionar para a página de login se não estiver autenticado
  if (!user) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  // Renderizar o conteúdo protegido se estiver autenticado
  return <>{children}</>;
};