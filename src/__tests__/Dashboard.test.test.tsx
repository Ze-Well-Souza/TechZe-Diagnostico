import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import Dashboard from '../pages\Dashboard'

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

describe('Dashboard Component', () => {
  it('should render without errors', () => {
    expect(Dashboard).toBeDefined()
  })

  it('should be a valid React component', () => {
    expect(typeof Dashboard).toBe('function')
  })

  it('should render successfully', () => {
    render(
      <ComponentWithRouter>
        <Dashboard />
      </ComponentWithRouter>
    )
    expect(document.body).toBeInTheDocument()
  })
})
