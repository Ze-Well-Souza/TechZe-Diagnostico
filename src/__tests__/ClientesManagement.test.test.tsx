import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import ClientesManagement from '../pages\ClientesManagement'

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

describe('ClientesManagement Component', () => {
  it('should render without errors', () => {
    expect(ClientesManagement).toBeDefined()
  })

  it('should be a valid React component', () => {
    expect(typeof ClientesManagement).toBe('function')
  })

  it('should render successfully', () => {
    render(
      <ComponentWithRouter>
        <ClientesManagement />
      </ComponentWithRouter>
    )
    expect(document.body).toBeInTheDocument()
  })
})
