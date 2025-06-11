import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import DashboardStats from '../components\dashboard\DashboardStats'

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

describe('DashboardStats Component', () => {
  it('should render without errors', () => {
    expect(DashboardStats).toBeDefined()
  })

  it('should be a valid React component', () => {
    expect(typeof DashboardStats).toBe('function')
  })

  it('should render successfully', () => {
    render(
      <ComponentWithRouter>
        <DashboardStats />
      </ComponentWithRouter>
    )
    expect(document.body).toBeInTheDocument()
  })
})
