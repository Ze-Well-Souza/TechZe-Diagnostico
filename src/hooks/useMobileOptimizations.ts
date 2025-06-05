import { useState, useEffect, useCallback, useRef } from 'react'

interface MobileOptimizations {
  // Device detection
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
  orientation: 'portrait' | 'landscape'
  
  // PWA features
  isStandalone: boolean
  canInstall: boolean
  installPrompt: () => void
  
  // Touch optimizations
  isKeyboardVisible: boolean
  safeAreaInsets: {
    top: number
    bottom: number
    left: number
    right: number
  }
  
  // Performance
  isLowEndDevice: boolean
  connectionType: string
  
  // Accessibility
  prefersReducedMotion: boolean
  highContrast: boolean
  
  // Gestures
  swipeHandlers: {
    onSwipeLeft: () => void
    onSwipeRight: () => void
    onPullToRefresh: () => void
  }
  
  // Haptics
  hapticFeedback: (type?: 'light' | 'medium' | 'heavy') => void
}

export function useMobileOptimizations(): MobileOptimizations {
  // Device detection
  const [deviceInfo, setDeviceInfo] = useState({
    isMobile: false,
    isTablet: false,
    isDesktop: true,
    orientation: 'portrait' as 'portrait' | 'landscape'
  })

  // PWA state
  const [pwaState, setPwaState] = useState({
    isStandalone: false,
    canInstall: false
  })

  // Install prompt
  const deferredPrompt = useRef<any>(null)

  // Touch optimizations
  const [touchState, setTouchState] = useState({
    isKeyboardVisible: false,
    safeAreaInsets: { top: 0, bottom: 0, left: 0, right: 0 }
  })

  // Performance detection
  const [performance, setPerformance] = useState({
    isLowEndDevice: false,
    connectionType: 'unknown'
  })

  // Accessibility
  const [accessibility, setAccessibility] = useState({
    prefersReducedMotion: false,
    highContrast: false
  })

  // Device detection effect
  useEffect(() => {
    const updateDeviceInfo = () => {
      const userAgent = navigator.userAgent
      const width = window.innerWidth
      const height = window.innerHeight

      setDeviceInfo({
        isMobile: width <= 768 || /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent),
        isTablet: width > 768 && width <= 1024,
        isDesktop: width > 1024,
        orientation: height > width ? 'portrait' : 'landscape'
      })
    }

    updateDeviceInfo()
    window.addEventListener('resize', updateDeviceInfo)
    window.addEventListener('orientationchange', updateDeviceInfo)

    return () => {
      window.removeEventListener('resize', updateDeviceInfo)
      window.removeEventListener('orientationchange', updateDeviceInfo)
    }
  }, [])

  // PWA detection
  useEffect(() => {
    // Standalone detection
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches ||
                        (window.navigator as any).standalone ||
                        document.referrer.includes('android-app://')

    setPwaState(prev => ({ ...prev, isStandalone }))

    // Install prompt handler
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault()
      deferredPrompt.current = e
      setPwaState(prev => ({ ...prev, canInstall: true }))
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt)

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt)
    }
  }, [])

  // Keyboard detection
  useEffect(() => {
    const handleResize = () => {
      if (window.visualViewport) {
        const viewportHeight = window.visualViewport.height
        const windowHeight = window.innerHeight
        setTouchState(prev => ({
          ...prev,
          isKeyboardVisible: viewportHeight < windowHeight * 0.8
        }))
      }
    }

    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', handleResize)
      return () => window.visualViewport?.removeEventListener('resize', handleResize)
    }
  }, [])

  // Safe area insets detection
  useEffect(() => {
    const updateSafeAreas = () => {
      const style = getComputedStyle(document.documentElement)
      setTouchState(prev => ({
        ...prev,
        safeAreaInsets: {
          top: parseInt(style.getPropertyValue('env(safe-area-inset-top)') || '0'),
          bottom: parseInt(style.getPropertyValue('env(safe-area-inset-bottom)') || '0'),
          left: parseInt(style.getPropertyValue('env(safe-area-inset-left)') || '0'),
          right: parseInt(style.getPropertyValue('env(safe-area-inset-right)') || '0')
        }
      }))
    }

    updateSafeAreas()
    window.addEventListener('resize', updateSafeAreas)
    return () => window.removeEventListener('resize', updateSafeAreas)
  }, [])

  // Performance detection
  useEffect(() => {
    // Device memory detection
    const deviceMemory = (navigator as any).deviceMemory || 4
    const hardwareConcurrency = navigator.hardwareConcurrency || 2
    
    const isLowEndDevice = deviceMemory <= 2 || hardwareConcurrency <= 2

    // Connection detection
    const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection
    const connectionType = connection ? connection.effectiveType || 'unknown' : 'unknown'

    setPerformance({ isLowEndDevice, connectionType })
  }, [])

  // Accessibility detection
  useEffect(() => {
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    const highContrast = window.matchMedia('(prefers-contrast: high)').matches

    setAccessibility({ prefersReducedMotion, highContrast })
  }, [])

  // Install prompt function
  const installPrompt = useCallback(async () => {
    if (deferredPrompt.current) {
      deferredPrompt.current.prompt()
      const { outcome } = await deferredPrompt.current.userChoice
      
      if (outcome === 'accepted') {
        setPwaState(prev => ({ ...prev, canInstall: false }))
      }
      
      deferredPrompt.current = null
    }
  }, [])

  // Haptic feedback
  const hapticFeedback = useCallback((type: 'light' | 'medium' | 'heavy' = 'light') => {
    if ('vibrate' in navigator) {
      const patterns = {
        light: [10],
        medium: [50],
        heavy: [100]
      }
      navigator.vibrate(patterns[type])
    }
  }, [])

  // Swipe gesture handlers
  const swipeHandlers = {
    onSwipeLeft: useCallback(() => {
      hapticFeedback('light')
      // Implement navigation or action
    }, [hapticFeedback]),

    onSwipeRight: useCallback(() => {
      hapticFeedback('light')
      // Implement navigation or action
    }, [hapticFeedback]),

    onPullToRefresh: useCallback(() => {
      hapticFeedback('medium')
      // Implement refresh logic
      window.location.reload()
    }, [hapticFeedback])
  }

  return {
    // Device info
    ...deviceInfo,
    
    // PWA features
    ...pwaState,
    installPrompt,
    
    // Touch optimizations
    ...touchState,
    
    // Performance
    ...performance,
    
    // Accessibility
    ...accessibility,
    
    // Gestures
    swipeHandlers,
    
    // Haptics
    hapticFeedback
  }
}

// Hook para gestos de toque
export function useSwipeGestures(
  onSwipeLeft?: () => void,
  onSwipeRight?: () => void,
  onSwipeUp?: () => void,
  onSwipeDown?: () => void
) {
  const startTouch = useRef<{ x: number; y: number } | null>(null)
  const minSwipeDistance = 50

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    const touch = e.touches[0]
    startTouch.current = { x: touch.clientX, y: touch.clientY }
  }, [])

  const handleTouchEnd = useCallback((e: React.TouchEvent) => {
    if (!startTouch.current) return

    const touch = e.changedTouches[0]
    const deltaX = touch.clientX - startTouch.current.x
    const deltaY = touch.clientY - startTouch.current.y

    const absDeltaX = Math.abs(deltaX)
    const absDeltaY = Math.abs(deltaY)

    if (Math.max(absDeltaX, absDeltaY) < minSwipeDistance) return

    if (absDeltaX > absDeltaY) {
      // Horizontal swipe
      if (deltaX > 0) {
        onSwipeRight?.()
      } else {
        onSwipeLeft?.()
      }
    } else {
      // Vertical swipe
      if (deltaY > 0) {
        onSwipeDown?.()
      } else {
        onSwipeUp?.()
      }
    }

    startTouch.current = null
  }, [onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown])

  return {
    onTouchStart: handleTouchStart,
    onTouchEnd: handleTouchEnd
  }
}

// Hook para pull-to-refresh
export function usePullToRefresh(onRefresh: () => void) {
  const [isPulling, setIsPulling] = useState(false)
  const [pullDistance, setPullDistance] = useState(0)
  const startY = useRef(0)
  const maxPullDistance = 100
  const refreshThreshold = 60

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    if (window.scrollY === 0) {
      startY.current = e.touches[0].clientY
      setIsPulling(true)
    }
  }, [])

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    if (isPulling && window.scrollY === 0) {
      const currentY = e.touches[0].clientY
      const distance = Math.max(0, currentY - startY.current)
      setPullDistance(Math.min(distance, maxPullDistance))
    }
  }, [isPulling, maxPullDistance])

  const handleTouchEnd = useCallback(() => {
    if (isPulling) {
      if (pullDistance >= refreshThreshold) {
        onRefresh()
      }
      setIsPulling(false)
      setPullDistance(0)
    }
  }, [isPulling, pullDistance, refreshThreshold, onRefresh])

  return {
    isPulling,
    pullDistance,
    pullProgress: pullDistance / refreshThreshold,
    onTouchStart: handleTouchStart,
    onTouchMove: handleTouchMove,
    onTouchEnd: handleTouchEnd
  }
} 