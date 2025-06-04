import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DiagnosticCard from './DiagnosticCard';
import { DiagnosticResult, Device } from '@/types/diagnostic';

// Mock dos dados de teste
const mockDiagnostic: DiagnosticResult = {
  id: 'test-diagnostic-id',
  device_id: 'test-device-id',
  user_id: 'test-user-id',
  status: 'completed',
  health_score: 85.5,
  cpu_status: 'good',
  memory_status: 'warning',
  disk_status: 'good',
  network_status: 'good',
  antivirus_status: 'good',
  driver_status: 'critical',
  cpu_metrics: {
    usage_percent: 45.2,
    temperature: 65.0,
    cores: 8
  },
  memory_metrics: {
    usage_percent: 78.5,
    total_gb: 16,
    available_gb: 3.4
  },
  disk_metrics: {
    usage_percent: 65.3,
    total_gb: 500,
    available_gb: 173.5
  },
  network_metrics: {
    latency_ms: 25.3,
    download_speed_mbps: 100.5,
    upload_speed_mbps: 50.2
  },
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:35:00Z'
};

const mockDevice: Device = {
  id: 'test-device-id',
  user_id: 'test-user-id',
  name: 'Notebook Dell Inspiron',
  type: 'laptop',
  os: 'Windows',
  os_version: '11',
  processor: 'Intel Core i7',
  ram: '16GB',
  storage: '500GB SSD',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T10:30:00Z'
};

describe('DiagnosticCard', () => {
  it('deve renderizar o componente com dados básicos', () => {
    render(<DiagnosticCard diagnostic={mockDiagnostic} />);
    
    // Verifica se o ID do dispositivo é exibido quando não há device
    expect(screen.getByText(/Dispositivo test-dev/)).toBeInTheDocument();
    
    // Verifica se o status é exibido
    expect(screen.getByText('Concluído')).toBeInTheDocument();
    
    // Verifica se a data é exibida
    expect(screen.getByText(/Executado em/)).toBeInTheDocument();
  });

  it('deve renderizar o nome do dispositivo quando fornecido', () => {
    render(<DiagnosticCard diagnostic={mockDiagnostic} device={mockDevice} />);
    
    expect(screen.getByText('Notebook Dell Inspiron')).toBeInTheDocument();
  });

  it('deve exibir o health score corretamente', () => {
    render(<DiagnosticCard diagnostic={mockDiagnostic} />);
    
    expect(screen.getByText('Health Score')).toBeInTheDocument();
    expect(screen.getByText('85.5%')).toBeInTheDocument();
  });

  it('deve exibir os status dos componentes', () => {
    render(<DiagnosticCard diagnostic={mockDiagnostic} />);
    
    // Verifica se os componentes são exibidos
    expect(screen.getByText('CPU')).toBeInTheDocument();
    expect(screen.getByText('RAM')).toBeInTheDocument();
    expect(screen.getByText('Disco')).toBeInTheDocument();
    expect(screen.getByText('Rede')).toBeInTheDocument();
    expect(screen.getByText('Segurança')).toBeInTheDocument();
    expect(screen.getByText('Drivers')).toBeInTheDocument();
  });

  it('deve exibir métricas dos componentes', () => {
    render(<DiagnosticCard diagnostic={mockDiagnostic} />);
    
    // Verifica se as métricas são exibidas
    expect(screen.getByText('45.2%')).toBeInTheDocument(); // CPU usage
    expect(screen.getByText('78.5%')).toBeInTheDocument(); // Memory usage
    expect(screen.getByText('65.3%')).toBeInTheDocument(); // Disk usage
    expect(screen.getByText('25ms')).toBeInTheDocument(); // Network latency
  });

  it('deve chamar onViewDetails quando o botão é clicado', () => {
    const mockOnViewDetails = jest.fn();
    render(
      <DiagnosticCard 
        diagnostic={mockDiagnostic} 
        onViewDetails={mockOnViewDetails} 
      />
    );
    
    const viewDetailsButton = screen.getByText('Ver Detalhes');
    fireEvent.click(viewDetailsButton);
    
    expect(mockOnViewDetails).toHaveBeenCalledWith(mockDiagnostic);
  });

  it('deve chamar onRunNewDiagnostic quando o botão é clicado', () => {
    const mockOnRunNewDiagnostic = jest.fn();
    render(
      <DiagnosticCard 
        diagnostic={mockDiagnostic} 
        onRunNewDiagnostic={mockOnRunNewDiagnostic} 
      />
    );
    
    const newDiagnosticButton = screen.getByText('Novo Diagnóstico');
    fireEvent.click(newDiagnosticButton);
    
    expect(mockOnRunNewDiagnostic).toHaveBeenCalledWith(mockDiagnostic.device_id);
  });

  it('deve exibir mensagem de erro quando presente', () => {
    const diagnosticWithError = {
      ...mockDiagnostic,
      error_message: 'Erro durante o diagnóstico'
    };
    
    render(<DiagnosticCard diagnostic={diagnosticWithError} />);
    
    expect(screen.getByText('Erro durante o diagnóstico')).toBeInTheDocument();
  });

  it('deve determinar o status geral corretamente', () => {
    // Teste com status crítico
    const criticalDiagnostic = {
      ...mockDiagnostic,
      cpu_status: 'critical' as const
    };
    
    render(<DiagnosticCard diagnostic={criticalDiagnostic} />);
    
    // Verifica se o badge tem a classe de cor vermelha (crítico)
    const badge = screen.getByText('Concluído');
    expect(badge).toHaveClass('bg-red-100');
  });

  it('deve formatar a data corretamente', () => {
    render(<DiagnosticCard diagnostic={mockDiagnostic} />);
    
    // Verifica se a data está formatada em português brasileiro
    expect(screen.getByText(/15\/01\/2024/)).toBeInTheDocument();
  });

  it('deve renderizar sem health_score quando não fornecido', () => {
    const diagnosticWithoutScore = {
      ...mockDiagnostic,
      health_score: undefined
    };
    
    render(<DiagnosticCard diagnostic={diagnosticWithoutScore} />);
    
    expect(screen.queryByText('Health Score')).not.toBeInTheDocument();
  });
});