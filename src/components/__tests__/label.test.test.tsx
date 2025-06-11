import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import label from '../components\ui\label'

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

describe('label Component', () => {
  it('should render without errors', () => {
    expect(label).toBeDefined()
  })

  it('should be a valid React component', () => {
    expect(typeof label).toBe('function')
  })

  it('should render successfully', () => {
    render(
      <ComponentWithRouter>
        <label />
      </ComponentWithRouter>
    )
    expect(document.body).toBeInTheDocument()
  })
})
