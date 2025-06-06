
import React, { useState, useEffect, useCallback, memo } from 'react';
import { useIsMobile } from '../../hooks/use-mobile';
import { useInstallPWA } from '../../hooks/useInstallPWA';
import { useOfflineStatus } from '../../hooks/useOfflineStatus';
import { usePWAOptimization } from '../../hooks/usePWAOptimization';

interface MobileOptimizedProps {
  children: React.ReactNode;
}

interface NotificationBadge {
  count: number;
  hasUnread: boolean;
}

/**
 * Componente que otimiza a interface para dispositivos móveis
 * Inclui detecção de teclado, orientação, pull-to-refresh e navegação adaptativa
 * Utiliza o hook usePWAOptimization para implementar otimizações avançadas de desempenho
 */
const MobileOptimized = memo(({ children }: MobileOptimizedProps) => {
  const isMobile = useIsMobile();
  const { isOnline } = useOfflineStatus();
  const { isInstallable, promptInstall } = useInstallPWA();
  const { isLowEndDevice, metrics, applyMobileOptimizations } = usePWAOptimization({
    prefetchAssets: true,
    lazyLoadImages: true,
    monitorPerformance: true,
    cacheFirstStrategy: true
  });
  
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isKeyboardVisible, setIsKeyboardVisible] = useState(false);
  const [notificationBadge, setNotificationBadge] = useState<NotificationBadge>({
    count: 0,
    hasUnread: false
  });
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>('portrait');
  const [isStandalone, setIsStandalone] = useState(false);

  // Aplicar otimizações mobile
  useEffect(() => {
    if (isMobile) {
      const cleanup = applyMobileOptimizations();
      return cleanup;
    }
  }, [isMobile, applyMobileOptimizations]);

  // Detectar modo PWA standalone
  useEffect(() => {
    const isStandalonePWA = window.matchMedia('(display-mode: standalone)').matches ||
                           (window.navigator as any).standalone ||
                           document.referrer.includes('android-app://');
    setIsStandalone(isStandalonePWA);
  }, []);

  // Detectar orientação
  useEffect(() => {
    const updateOrientation = () => {
      setOrientation(window.innerHeight > window.innerWidth ? 'portrait' : 'landscape');
    };

    updateOrientation();
    window.addEventListener('resize', updateOrientation, { passive: true });
    window.addEventListener('orientationchange', updateOrientation, { passive: true });

    return () => {
      window.removeEventListener('resize', updateOrientation);
      window.removeEventListener('orientationchange', updateOrientation);
    };
  }, []);

  // Detectar teclado virtual
  useEffect(() => {
    const handleResize = () => {
      const viewportHeight = window.visualViewport?.height || window.innerHeight;
      const windowHeight = window.innerHeight;
      setIsKeyboardVisible(viewportHeight < windowHeight * 0.8);
    };

    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', handleResize, { passive: true });
      return () => window.visualViewport?.removeEventListener('resize', handleResize);
    }
  }, []);

  // Gestão de notificações
  useEffect(() => {
    // Simular dados de notificação
    const updateNotifications = () => {
      setNotificationBadge({
        count: Math.floor(Math.random() * 10),
        hasUnread: Math.random() > 0.5
      });
    };

    updateNotifications();
    const interval = setInterval(updateNotifications, 30000); // Update every 30s

    return () => clearInterval(interval);
  }, []);

  // Fechar menu ao clicar fora
  const handleMenuToggle = useCallback(() => {
    setIsMenuOpen(!isMenuOpen);
  }, [isMenuOpen]);

  // Haptic feedback para PWA
  const triggerHapticFeedback = useCallback(() => {
    if ('vibrate' in navigator) {
      navigator.vibrate(50); // Vibração leve de 50ms
    }
  }, []);

  // Pull-to-refresh gesture
  const [pullDistance, setPullDistance] = useState(0);
  const [isPulling, setIsPulling] = useState(false);

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    if (window.scrollY === 0) {
      setIsPulling(true);
    }
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (isPulling && window.scrollY === 0) {
      const touch = e.touches[0];
      const distance = Math.max(0, touch.clientY - 50);
      setPullDistance(Math.min(distance, 100));
    }
  }, [isPulling]);

  const handleTouchEnd = useCallback(() => {
    if (isPulling && pullDistance > 60) {
      triggerHapticFeedback();
      // Trigger refresh
      window.location.reload();
    }
    setIsPulling(false);
    setPullDistance(0);
  }, [isPulling, pullDistance, triggerHapticFeedback]);

  // Se não for mobile, apenas renderiza o conteúdo sem otimizações
  if (!isMobile) {
    return <>{children}</>;
  }

  return (
    <div 
      className={`
        min-h-screen bg-gray-50 dark:bg-gray-900 
        ${isStandalone ? 'pt-safe-top pb-safe-bottom' : ''}
        ${orientation === 'landscape' ? 'landscape-mode' : 'portrait-mode'}
        ${isKeyboardVisible ? 'keyboard-visible' : ''}
        ${isLowEndDevice ? 'low-end-device reduce-motion' : ''}
      `}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
      {/* Performance metrics debug (apenas em desenvolvimento) */}
      {process.env.NODE_ENV === 'development' && metrics.lcp && (
        <div className="fixed bottom-24 right-2 bg-black bg-opacity-70 text-white text-xs p-2 rounded z-50">
          <div>FCP: {metrics.fcp ? `${Math.round(metrics.fcp)}ms` : 'N/A'}</div>
          <div>LCP: {metrics.lcp ? `${Math.round(metrics.lcp)}ms` : 'N/A'}</div>
          <div>FID: {metrics.fid ? `${Math.round(metrics.fid)}ms` : 'N/A'}</div>
          <div>CLS: {metrics.cls?.toFixed(3) || 'N/A'}</div>
        </div>
      )}

      {/* Pull to refresh indicator */}
      {isPulling && (
        <div 
          className="fixed top-0 left-0 right-0 z-50 flex justify-center pt-4"
          style={{ transform: `translateY(${pullDistance - 50}px)` }}
        >
          <div className="bg-white dark:bg-gray-800 rounded-full p-2 shadow-lg">
            <div 
              className={`w-6 h-6 border-2 border-blue-500 rounded-full animate-spin ${
                pullDistance > 60 ? 'border-t-transparent' : ''
              }`}
            />
          </div>
        </div>
      )}

      {/* Status bar for PWA */}
      {isStandalone && (
        <div className="fixed top-0 left-0 right-0 h-safe-top bg-blue-600 z-50" />
      )}

      {/* Mobile Header */}
      <header className="sticky top-0 z-40 bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between px-4 py-3">
          {/* Menu Toggle */}
          <button
            onClick={() => {
              handleMenuToggle();
              triggerHapticFeedback();
            }}
            className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors touch-optimized"
            data-testid="mobile-menu-button"
            aria-label="Abrir menu"
          >
            {isMenuOpen ? (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>

          {/* Logo/Title */}
          <div className="flex-1 text-center">
            <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
              TechZe Diagnóstico
            </h1>
          </div>

          {/* Notifications */}
          <div className="flex items-center space-x-2">
            <button
              className="relative p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors touch-optimized"
              onClick={triggerHapticFeedback}
              aria-label="Notificações"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              {notificationBadge.hasUnread && (
                <span className="absolute -top-1 -right-1 h-3 w-3 bg-red-500 rounded-full animate-pulse" />
              )}
              {notificationBadge.count > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {notificationBadge.count > 9 ? '9+' : notificationBadge.count}
                </span>
              )}
            </button>

            <button
              className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors touch-optimized"
              onClick={triggerHapticFeedback}
              aria-label="Configurações"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Slide-out Navigation Menu */}
      <div className={`
        fixed inset-0 z-50 transform transition-transform duration-300 ease-in-out
        ${isMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        {/* Backdrop */}
        <div 
          className="absolute inset-0 bg-black bg-opacity-50"
          onClick={handleMenuToggle}
        />
        
        {/* Menu Panel */}
        <nav className="relative max-w-xs w-full bg-white dark:bg-gray-800 h-full shadow-xl">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Menu Principal
            </h2>
          </div>
          
          <div className="p-4 space-y-2">
            {[
              { name: 'Dashboard', href: '/dashboard', icon: '📊' },
              { name: 'Diagnósticos', href: '/diagnostics', icon: '🔧' },
              { name: 'Dispositivos', href: '/devices', icon: '💻' },
              { name: 'Relatórios', href: '/reports', icon: '📈' },
              { name: 'IA/ML', href: '/ai', icon: '🤖' },
              { name: 'Configurações', href: '/settings', icon: '⚙️' }
            ].map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="flex items-center space-x-3 p-3 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors touch-optimized"
                onClick={() => {
                  setIsMenuOpen(false);
                  triggerHapticFeedback();
                }}
              >
                <span className="text-xl">{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </a>
            ))}
          </div>

          {/* Instalação do PWA */}
          {isInstallable && (
            <div className="p-4 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={() => {
                  promptInstall();
                  triggerHapticFeedback();
                }}
                className="w-full flex items-center justify-center space-x-2 p-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors touch-optimized"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                <span>Instalar Aplicativo</span>
              </button>
            </div>
          )}
        </nav>
      </div>

      {/* Main Content */}
      <main 
        className={`
          transition-all duration-300 ease-in-out min-h-screen
          ${isKeyboardVisible ? 'pb-0' : 'pb-16'}
          ${isStandalone ? 'pb-safe-bottom' : ''}
        `}
        data-testid="main-content"
      >
        {children}
      </main>

      {/* Bottom Navigation - Hidden when keyboard is visible */}
      {!isKeyboardVisible && (
        <nav className={`
          fixed bottom-0 left-0 right-0 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700
          ${isStandalone ? 'pb-safe-bottom' : ''}
        `}>
          <div className="flex justify-around py-2">
            {[
              { name: 'Início', icon: '🏠', href: '/' },
              { name: 'Diagnósticos', icon: '🔧', href: '/diagnostics' },
              { name: 'IA', icon: '🤖', href: '/ai' },
              { name: 'Perfil', icon: '👤', href: '/profile' }
            ].map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="flex flex-col items-center justify-center p-2 space-y-1 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors touch-optimized"
                onClick={triggerHapticFeedback}
              >
                <span className="text-xl">{item.icon}</span>
                <span className="text-xs font-medium">{item.name}</span>
              </a>
            ))}
          </div>
        </nav>
      )}

      {/* Indicador de status offline */}
      {!isOnline && (
        <div className="fixed bottom-16 left-0 right-0 p-2 bg-yellow-500 text-white text-center z-40">
          <div className="flex items-center justify-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span className="font-medium">Você está offline. Algumas funcionalidades podem estar limitadas.</span>
          </div>
        </div>
      )}
    </div>
  );
});

MobileOptimized.displayName = 'MobileOptimized';

export default MobileOptimized;
