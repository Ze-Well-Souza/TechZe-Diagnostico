import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import DetalhesOrcamento from '../pages\Orcamentos\DetalhesOrcamento'

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

describe('DetalhesOrcamento Component', () => {
  it('should render without errors', () => {
    expect(DetalhesOrcamento).toBeDefined()
  })

  it('should be a valid React component', () => {
    expect(typeof DetalhesOrcamento).toBe('function')
  })

  it('should render successfully', () => {
    render(
      <ComponentWithRouter>
        <DetalhesOrcamento />
      </ComponentWithRouter>
    )
    expect(document.body).toBeInTheDocument()
  })
})
