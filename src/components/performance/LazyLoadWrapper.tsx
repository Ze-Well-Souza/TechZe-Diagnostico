
import React, { Suspense, lazy, ComponentType } from 'react';
import { Skeleton } from '@/components/ui/skeleton';

interface LazyLoadWrapperProps {
  factory: () => Promise<{ default: ComponentType<any> }>;
  fallback?: React.ReactNode;
  errorFallback?: React.ReactNode;
}

class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Erro no lazy loading:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback;
    }

    return this.props.children;
  }
}

export const LazyLoadWrapper: React.FC<LazyLoadWrapperProps> = ({
  factory,
  fallback,
  errorFallback
}) => {
  const LazyComponent = lazy(factory);

  const defaultFallback = (
    <div className="space-y-4 p-4">
      <Skeleton className="h-8 w-full" />
      <Skeleton className="h-32 w-full" />
      <Skeleton className="h-8 w-3/4" />
    </div>
  );

  const defaultErrorFallback = (
    <div className="p-4 text-center">
      <p className="text-red-500">Erro ao carregar componente</p>
      <button 
        onClick={() => window.location.reload()}
        className="mt-2 px-4 py-2 bg-blue-500 text-white rounded"
      >
        Recarregar
      </button>
    </div>
  );

  return (
    <ErrorBoundary fallback={errorFallback || defaultErrorFallback}>
      <Suspense fallback={fallback || defaultFallback}>
        <LazyComponent />
      </Suspense>
    </ErrorBoundary>
  );
};

// HOC para lazy loading de páginas
export const withLazyLoading = <P extends object>(
  componentFactory: () => Promise<{ default: ComponentType<P> }>,
  loadingComponent?: React.ReactNode
) => {
  return (props: P) => (
    <LazyLoadWrapper 
      factory={componentFactory}
      fallback={loadingComponent}
    />
  );
};

// Componentes lazy-loaded para páginas principais
export const LazyDashboard = withLazyLoading(
  () => import('@/pages/Dashboard'),
  <div className="p-8">
    <Skeleton className="h-12 w-64 mb-6" />
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: 6 }).map((_, i) => (
        <Skeleton key={i} className="h-48 w-full" />
      ))}
    </div>
  </div>
);

export const LazyDiagnostic = withLazyLoading(
  () => import('@/pages/Diagnostic')
);

export const LazyReports = withLazyLoading(
  () => import('@/pages/Reports')
);

export const LazyHistory = withLazyLoading(
  () => import('@/pages/History')
);
