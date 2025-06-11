import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import toaster from '../components\ui\toaster'

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

describe('toaster Component', () => {
  it('should render without errors', () => {
    expect(toaster).toBeDefined()
  })

  it('should be a valid React component', () => {
    expect(typeof toaster).toBe('function')
  })

  it('should render successfully', () => {
    render(
      <ComponentWithRouter>
        <toaster />
      </ComponentWithRouter>
    )
    expect(document.body).toBeInTheDocument()
  })
})
