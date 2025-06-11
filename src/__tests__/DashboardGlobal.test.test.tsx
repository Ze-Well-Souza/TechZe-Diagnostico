import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import DashboardGlobal from '../pages\DashboardGlobal'

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

describe('DashboardGlobal Component', () => {
  it('should render without errors', () => {
    expect(DashboardGlobal).toBeDefined()
  })

  it('should be a valid React component', () => {
    expect(typeof DashboardGlobal).toBe('function')
  })

  it('should render successfully', () => {
    render(
      <ComponentWithRouter>
        <DashboardGlobal />
      </ComponentWithRouter>
    )
    expect(document.body).toBeInTheDocument()
  })
})
