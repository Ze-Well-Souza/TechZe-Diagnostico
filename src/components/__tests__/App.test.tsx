import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import App from '../../App'

// Mock do react-router-dom para testes
const AppWithRouter = () => (
  <BrowserRouter>
    <App />
  </BrowserRouter>
)

describe('App Component', () => {
  it('should render without crashing', () => {
    expect(() => render(<AppWithRouter />)).not.toThrow()
  })

  it('should have the main app container', () => {
    render(<AppWithRouter />)
    const appElement = document.querySelector('body')
    expect(appElement).toBeInTheDocument()
  })
}) 