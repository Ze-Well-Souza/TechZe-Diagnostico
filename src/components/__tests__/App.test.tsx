import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from '../../App'

// Mock do Supabase
vi.mock('@/integrations/supabase/client', () => ({
  supabase: {
    auth: {
      onAuthStateChange: vi.fn(() => ({ data: { subscription: { unsubscribe: vi.fn() } } })),
      getSession: vi.fn(() => Promise.resolve({ data: { session: null }, error: null })),
      signInWithPassword: vi.fn(),
      signUp: vi.fn(),
      signOut: vi.fn()
    },
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        eq: vi.fn(() => ({
          single: vi.fn(() => Promise.resolve({ data: null, error: null }))
        }))
      }))
    }))
  }
}))

// Mock do Background Sync Service
vi.mock('@/services/backgroundSyncService', () => ({
  getBackgroundSyncService: vi.fn(() => ({
    getQueueStatus: vi.fn(() => ({ pending: 0, failed: 0 })),
    forceSync: vi.fn(() => Promise.resolve())
  }))
}))

// Mock do react-router-dom para testes
const AppWithRouter = () => (
  <BrowserRouter>
    <App />
  </BrowserRouter>
)

describe('App Component', () => {
  it('should import without errors', () => {
    expect(App).toBeDefined()
  })

  it('should be a valid React component', () => {
    expect(typeof App).toBe('function')
  })
})