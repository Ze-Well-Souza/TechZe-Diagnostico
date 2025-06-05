import React, { useState, useEffect, useCallback } from 'react'
import { Bars3Icon, XMarkIcon, BellIcon, CogIcon } from '@heroicons/react/24/outline'

interface MobileOptimizedProps {
  children: React.ReactNode
}

interface NotificationBadge {
  count: number
  hasUnread: boolean
}

export default function MobileOptimized({ children }: MobileOptimizedProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  const [isKeyboardVisible, setIsKeyboardVisible] = useState(false)
  const [notificationBadge, setNotificationBadge] = useState<NotificationBadge>({
    count: 0,
    hasUnread: false
  })
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>('portrait')
  const [isStandalone, setIsStandalone] = useState(false)

  // Detectar modo PWA standalone
  useEffect(() => {
    const isStandalonePWA = window.matchMedia('(display-mode: standalone)').matches ||
                           (window.navigator as any).standalone ||
                           document.referrer.includes('android-app://')
    setIsStandalone(isStandalonePWA)
  }, [])

  // Detectar orientação
  useEffect(() => {
    const updateOrientation = () => {
      setOrientation(window.innerHeight > window.innerWidth ? 'portrait' : 'landscape')
    }

    updateOrientation()
    window.addEventListener('resize', updateOrientation)
    window.addEventListener('orientationchange', updateOrientation)

    return () => {
      window.removeEventListener('resize', updateOrientation)
      window.removeEventListener('orientationchange', updateOrientation)
    }
  }, [])

  // Detectar teclado virtual
  useEffect(() => {
    const handleResize = () => {
      const viewportHeight = window.visualViewport?.height || window.innerHeight
      const windowHeight = window.innerHeight
      setIsKeyboardVisible(viewportHeight < windowHeight * 0.8)
    }

    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', handleResize)
      return () => window.visualViewport?.removeEventListener('resize', handleResize)
    }
  }, [])

  // Gestão de notificações
  useEffect(() => {
    // Simular dados de notificação
    const updateNotifications = () => {
      setNotificationBadge({
        count: Math.floor(Math.random() * 10),
        hasUnread: Math.random() > 0.5
      })
    }

    updateNotifications()
    const interval = setInterval(updateNotifications, 30000) // Update every 30s

    return () => clearInterval(interval)
  }, [])

  // Fechar menu ao clicar fora
  const handleMenuToggle = useCallback(() => {
    setIsMenuOpen(!isMenuOpen)
  }, [isMenuOpen])

  // Haptic feedback para PWA
  const triggerHapticFeedback = useCallback(() => {
    if ('vibrate' in navigator) {
      navigator.vibrate(50) // Vibração leve de 50ms
    }
  }, [])

  // Pull-to-refresh gesture
  const [pullDistance, setPullDistance] = useState(0)
  const [isPulling, setIsPulling] = useState(false)

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    if (window.scrollY === 0) {
      setIsPulling(true)
    }
  }, [])

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (isPulling && window.scrollY === 0) {
      const touch = e.touches[0]
      const distance = Math.max(0, touch.clientY - 50)
      setPullDistance(Math.min(distance, 100))
    }
  }, [isPulling])

  const handleTouchEnd = useCallback(() => {
    if (isPulling && pullDistance > 60) {
      triggerHapticFeedback()
      // Trigger refresh
      window.location.reload()
    }
    setIsPulling(false)
    setPullDistance(0)
  }, [isPulling, pullDistance, triggerHapticFeedback])

  return (
    <div 
      className={`
        min-h-screen bg-gray-50 dark:bg-gray-900 
        ${isStandalone ? 'pt-safe-top pb-safe-bottom' : ''}
        ${orientation === 'landscape' ? 'landscape-mode' : 'portrait-mode'}
        ${isKeyboardVisible ? 'keyboard-visible' : ''}
      `}
      onTouchStart={handleTouchStart}
      onTouchMove={handleTouchMove}
      onTouchEnd={handleTouchEnd}
    >
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
              handleMenuToggle()
              triggerHapticFeedback()
            }}
            className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            data-testid="mobile-menu-button"
            aria-label="Abrir menu"
          >
            {isMenuOpen ? (
              <XMarkIcon className="h-6 w-6" />
            ) : (
              <Bars3Icon className="h-6 w-6" />
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
              className="relative p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              onClick={triggerHapticFeedback}
              aria-label="Notificações"
            >
              <BellIcon className="h-6 w-6" />
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
              className="p-2 rounded-md text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              onClick={triggerHapticFeedback}
              aria-label="Configurações"
            >
              <CogIcon className="h-6 w-6" />
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
                className="flex items-center space-x-3 p-3 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                onClick={() => {
                  setIsMenuOpen(false)
                  triggerHapticFeedback()
                }}
              >
                <span className="text-xl">{item.icon}</span>
                <span className="font-medium">{item.name}</span>
              </a>
            ))}
          </div>
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
                className="flex flex-col items-center justify-center p-2 space-y-1 text-gray-600 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                onClick={triggerHapticFeedback}
              >
                <span className="text-xl">{item.icon}</span>
                <span className="text-xs font-medium">{item.name}</span>
              </a>
            ))}
          </div>
        </nav>
      )}
    </div>
  )
}

// CSS adicional para safe areas e orientação
const mobileStyles = `
  .safe-top { padding-top: env(safe-area-inset-top); }
  .safe-bottom { padding-bottom: env(safe-area-inset-bottom); }
  .safe-left { padding-left: env(safe-area-inset-left); }
  .safe-right { padding-right: env(safe-area-inset-right); }
  
  .pt-safe-top { padding-top: env(safe-area-inset-top); }
  .pb-safe-bottom { padding-bottom: env(safe-area-inset-bottom); }
  .h-safe-top { height: env(safe-area-inset-top); }
  
  .landscape-mode .bottom-nav { 
    height: 60px; 
  }
  
  .portrait-mode .bottom-nav { 
    height: 80px; 
  }
  
  .keyboard-visible {
    height: 100vh;
    overflow: hidden;
  }
  
  @media (hover: none) and (pointer: coarse) {
    .touch-optimized {
      min-height: 44px;
      min-width: 44px;
    }
  }
`

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style')
  styleSheet.textContent = mobileStyles
  document.head.appendChild(styleSheet)
} 