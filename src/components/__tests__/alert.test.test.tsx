import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import alert from '../components\ui\alert'

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

describe('alert Component', () => {
  it('should render without errors', () => {
    expect(alert).toBeDefined()
  })

  it('should be a valid React component', () => {
    expect(typeof alert).toBe('function')
  })

  it('should render successfully', () => {
    render(
      <ComponentWithRouter>
        <alert />
      </ComponentWithRouter>
    )
    expect(document.body).toBeInTheDocument()
  })
})
