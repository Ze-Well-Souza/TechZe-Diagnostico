import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DeviceCard from './DeviceCard';
import { Device, DiagnosticResult } from '@/types/diagnostic';

// Mock dos dados de teste
const mockDevice: Device = {
  id: 'test-device-id',
  user_id: 'test-user-id',
  name: 'Notebook Dell XPS',
  type: 'laptop',
  os: 'Windows',
  os_version: '11',
  processor: 'Intel Core i7-1165G7',
  ram: '16GB',
  storage: '512GB SSD',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-15T10:30:00Z'
};

const mockDiagnostic: DiagnosticResult = {
  id: 'test-diagnostic-id',
  device_id: 'test-device-id',
  user_id: 'test-user-id',
  status: 'completed',
  health_score: 85.5,
  cpu_status: 'good',
  memory_status: 'good',
  disk_status: 'good',
  network_status: 'good',
  antivirus_status: 'good',
  driver_status: 'good',
  cpu_metrics: {
    usage_percent: 25.2,
    temperature: 45.0,
    cores: 8
  },
  memory_metrics: {
    usage_percent: 48.5,
    total_gb: 16,
    available_gb: 8.2
  },
  disk_metrics: {
    usage_percent: 55.3,
    total_gb: 512,
    available_gb: 228.5
  },
  network_metrics: {
    latency_ms: 15.3,
    download_speed_mbps: 120.5,
    upload_speed_mbps: 65.2
  },
  created_at: '2024-01-15T10:30:00Z',
  updated_at: '2024-01-15T10:35:00Z'
};

// Mock para o componente DropdownMenu que usa o portal do React
jest.mock('@/components/ui/dropdown-menu', () => {
  return {
    DropdownMenu: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
    DropdownMenuTrigger: ({ children }: { children: React.ReactNode }) => <div data-testid="dropdown-trigger">{children}</div>,
    DropdownMenuContent: ({ children }: { children: React.ReactNode }) => <div data-testid="dropdown-content">{children}</div>,
    DropdownMenuItem: ({ children, onClick }: { children: React.ReactNode, onClick?: () => void }) => 
      <button data-testid={`dropdown-item-${children}`} onClick={onClick}>{children}</button>,
  };
});

describe('DeviceCard', () => {
  it('deve renderizar as informações básicas do dispositivo', () => {
    render(<DeviceCard device={mockDevice} />);
    
    // Verifica se o nome do dispositivo é exibido
    expect(screen.getByText('Notebook Dell XPS')).toBeInTheDocument();
    
    // Verifica se o tipo e sistema operacional são exibidos
    expect(screen.getByText('laptop • Windows')).toBeInTheDocument();
    
    // Verifica se as especificações são exibidas
    expect(screen.getByText('Processador:')).toBeInTheDocument();
    expect(screen.getByText('Intel Core i7-1165G7')).toBeInTheDocument();
    expect(screen.getByText('Memória:')).toBeInTheDocument();
    expect(screen.getByText('16GB')).toBeInTheDocument();
    expect(screen.getByText('Armazenamento:')).toBeInTheDocument();
    expect(screen.getByText('512GB SSD')).toBeInTheDocument();
    expect(screen.getByText('Versão SO:')).toBeInTheDocument();
    expect(screen.getByText('11')).toBeInTheDocument();
  });

  it('deve exibir "Sem dados" quando não há diagnóstico', () => {
    render(<DeviceCard device={mockDevice} />);
    
    expect(screen.getByText('Sem dados')).toBeInTheDocument();
  });

  it('deve exibir o health score e status quando há diagnóstico', () => {
    render(<DeviceCard device={mockDevice} lastDiagnostic={mockDiagnostic} />);
    
    // Verifica se o status de saúde é exibido
    expect(screen.getByText('Saudável')).toBeInTheDocument();
    
    // Verifica se o health score é exibido
    expect(screen.getByText('Health Score')).toBeInTheDocument();
    expect(screen.getByText('85.5%')).toBeInTheDocument();
    
    // Verifica se a data do último diagnóstico é exibida
    expect(screen.getByText(/Último diagnóstico:/)).toBeInTheDocument();
    expect(screen.getByText(/15\/01\/2024/)).toBeInTheDocument();
  });

  it('deve chamar onRunDiagnostic quando o botão é clicado', () => {
    const mockOnRunDiagnostic = jest.fn();
    render(
      <DeviceCard 
        device={mockDevice} 
        onRunDiagnostic={mockOnRunDiagnostic} 
      />
    );
    
    const runDiagnosticButton = screen.getByText('Executar Diagnóstico');
    fireEvent.click(runDiagnosticButton);
    
    expect(mockOnRunDiagnostic).toHaveBeenCalledWith(mockDevice.id);
  });

  it('deve desabilitar o botão de diagnóstico quando isRunningDiagnostic=true', () => {
    render(
      <DeviceCard 
        device={mockDevice} 
        onRunDiagnostic={() => {}} 
        isRunningDiagnostic={true}
      />
    );
    
    const runDiagnosticButton = screen.getByText('Executando...');
    expect(runDiagnosticButton).toBeDisabled();
  });

  it('deve chamar onViewDiagnostics quando o botão é clicado', () => {
    const mockOnViewDiagnostics = jest.fn();
    render(
      <DeviceCard 
        device={mockDevice} 
        onViewDiagnostics={mockOnViewDiagnostics} 
      />
    );
    
    const viewHistoryButton = screen.getByText('Ver Histórico');
    fireEvent.click(viewHistoryButton);
    
    expect(mockOnViewDiagnostics).toHaveBeenCalledWith(mockDevice.id);
  });

  it('deve renderizar o dropdown menu quando onEditDevice ou onDeleteDevice são fornecidos', () => {
    const mockOnEditDevice = jest.fn();
    const mockOnDeleteDevice = jest.fn();
    
    render(
      <DeviceCard 
        device={mockDevice} 
        onEditDevice={mockOnEditDevice}
        onDeleteDevice={mockOnDeleteDevice}
      />
    );
    
    // Verifica se o trigger do dropdown está presente
    expect(screen.getByTestId('dropdown-trigger')).toBeInTheDocument();
    
    // Verifica se os itens do dropdown estão presentes
    expect(screen.getByTestId('dropdown-item-Editar')).toBeInTheDocument();
    expect(screen.getByTestId('dropdown-item-Excluir')).toBeInTheDocument();
  });

  it('deve chamar onEditDevice quando o item de edição é clicado', () => {
    const mockOnEditDevice = jest.fn();
    
    render(
      <DeviceCard 
        device={mockDevice} 
        onEditDevice={mockOnEditDevice}
      />
    );
    
    const editButton = screen.getByTestId('dropdown-item-Editar');
    fireEvent.click(editButton);
    
    expect(mockOnEditDevice).toHaveBeenCalledWith(mockDevice);
  });

  it('deve chamar onDeleteDevice quando o item de exclusão é clicado', () => {
    const mockOnDeleteDevice = jest.fn();
    
    render(
      <DeviceCard 
        device={mockDevice} 
        onDeleteDevice={mockOnDeleteDevice}
      />
    );
    
    const deleteButton = screen.getByTestId('dropdown-item-Excluir');
    fireEvent.click(deleteButton);
    
    expect(mockOnDeleteDevice).toHaveBeenCalledWith(mockDevice.id);
  });

  it('deve exibir status de atenção quando health score está entre 60 e 80', () => {
    const warningDiagnostic = {
      ...mockDiagnostic,
      health_score: 65.5
    };
    
    render(<DeviceCard device={mockDevice} lastDiagnostic={warningDiagnostic} />);
    
    expect(screen.getByText('Atenção')).toBeInTheDocument();
  });

  it('deve exibir status crítico quando health score está abaixo de 60', () => {
    const criticalDiagnostic = {
      ...mockDiagnostic,
      health_score: 45.5
    };
    
    render(<DeviceCard device={mockDevice} lastDiagnostic={criticalDiagnostic} />);
    
    expect(screen.getByText('Crítico')).toBeInTheDocument();
  });
});