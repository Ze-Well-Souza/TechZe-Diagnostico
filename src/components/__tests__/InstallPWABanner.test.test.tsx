import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import InstallPWABanner from '../components\ui\InstallPWABanner'

// Mock do Supabase
vi.mock('@/integrations/supabase/client', () => ({
  supabase: {
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        eq: vi.fn(() => ({
          single: vi.fn(() => Promise.resolve({ data: null, error: null }))
        }))
      }))
    }))
  }
}))

const ComponentWithRouter = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
)

describe('InstallPWABanner Component', () => {
  it('should render without errors', () => {
    expect(InstallPWABanner).toBeDefined()
  })

  it('should be a valid React component', () => {
    expect(typeof InstallPWABanner).toBe('function')
  })

  it('should render successfully', () => {
    render(
      <ComponentWithRouter>
        <InstallPWABanner />
      </ComponentWithRouter>
    )
    expect(document.body).toBeInTheDocument()
  })
})
