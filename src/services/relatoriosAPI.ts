import { supabase } from '@/lib/supabase';

export interface RelatorioExportacao {
  id: string;
  formato: 'pdf' | 'excel' | 'csv';
  dados: any;
  configuracoes?: {
    incluirGraficos?: boolean;
    incluirResumo?: boolean;
    template?: string;
  };
}

export interface RelatorioSalvo {
  id: string;
  nome: string;
  tipo: string;
  filtros: any;
  dados: any;
  criadoEm: Date;
  atualizadoEm: Date;
  usuario: string;
}

class RelatoriosAPI {
  private baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

  async exportar(relatorioId: string, formato: string): Promise<Blob> {
    try {
      // Simular exportação - em produção seria uma chamada real para a API
      const response = await this.simularExportacao(relatorioId, formato);
      return response;
    } catch (error) {
      console.error('Erro ao exportar relatório:', error);
      throw new Error('Falha na exportação do relatório');
    }
  }

  async salvar(relatorio: any): Promise<RelatorioSalvo> {
    try {
      const { data, error } = await supabase
        .from('relatorios_salvos')
        .insert({
          nome: relatorio.titulo,
          tipo: relatorio.tipo,
          filtros: relatorio.filtros || {},
          dados: relatorio.dados,
          usuario: 'usuario_atual' // Em produção, pegar do contexto de auth
        })
        .select()
        .single();

      if (error) throw error;
      return data;
    } catch (error) {
      console.error('Erro ao salvar relatório:', error);
      throw new Error('Falha ao salvar relatório');
    }
  }

  async listarSalvos(): Promise<RelatorioSalvo[]> {
    try {
      const { data, error } = await supabase
        .from('relatorios_salvos')
        .select('*')
        .order('criado_em', { ascending: false });

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('Erro ao listar relatórios salvos:', error);
      throw new Error('Falha ao carregar relatórios salvos');
    }
  }

  async excluirSalvo(id: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('relatorios_salvos')
        .delete()
        .eq('id', id);

      if (error) throw error;
    } catch (error) {
      console.error('Erro ao excluir relatório:', error);
      throw new Error('Falha ao excluir relatório');
    }
  }

  async obterDadosFinanceiros(filtros: any): Promise<any[]> {
    try {
      // Em produção, fazer chamadas reais para o backend
      const response = await fetch(`${this.baseUrl}/relatorios/financeiro`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(filtros)
      });

      if (!response.ok) {
        // Fallback para dados simulados se a API não estiver disponível
        return this.gerarDadosFinanceirosMock(filtros);
      }

      return await response.json();
    } catch (error) {
      console.warn('API não disponível, usando dados simulados:', error);
      return this.gerarDadosFinanceirosMock(filtros);
    }
  }

  async obterDadosOperacionais(filtros: any): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/relatorios/operacional`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(filtros)
      });

      if (!response.ok) {
        return this.gerarDadosOperacionaisMock(filtros);
      }

      return await response.json();
    } catch (error) {
      console.warn('API não disponível, usando dados simulados:', error);
      return this.gerarDadosOperacionaisMock(filtros);
    }
  }

  async obterDadosClientes(filtros: any): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/relatorios/clientes`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(filtros)
      });

      if (!response.ok) {
        return this.gerarDadosClientesMock(filtros);
      }

      return await response.json();
    } catch (error) {
      console.warn('API não disponível, usando dados simulados:', error);
      return this.gerarDadosClientesMock(filtros);
    }
  }

  async obterDadosEstoque(filtros: any): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/relatorios/estoque`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(filtros)
      });

      if (!response.ok) {
        return this.gerarDadosEstoqueMock(filtros);
      }

      return await response.json();
    } catch (error) {
      console.warn('API não disponível, usando dados simulados:', error);
      return this.gerarDadosEstoqueMock(filtros);
    }
  }

  // Métodos privados para simulação de dados
  private async simularExportacao(relatorioId: string, formato: string): Promise<Blob> {
    // Simular delay de processamento
    await new Promise(resolve => setTimeout(resolve, 2000));

    let conteudo = '';
    let mimeType = '';

    switch (formato) {
      case 'pdf':
        conteudo = '%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n';
        mimeType = 'application/pdf';
        break;
      case 'excel':
        conteudo = 'Nome,Valor,Data\nExemplo 1,100,2024-01-01\nExemplo 2,200,2024-01-02';
        mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
        break;
      case 'csv':
        conteudo = 'Nome,Valor,Data\nExemplo 1,100,2024-01-01\nExemplo 2,200,2024-01-02';
        mimeType = 'text/csv';
        break;
      default:
        throw new Error('Formato não suportado');
    }

    return new Blob([conteudo], { type: mimeType });
  }

  private gerarDadosFinanceirosMock(filtros: any): any[] {
    const meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho'];
    return meses.map(mes => ({
      mes,
      receitas: Math.floor(Math.random() * 20000) + 10000,
      despesas: Math.floor(Math.random() * 10000) + 5000,
      lucro: Math.floor(Math.random() * 15000) + 5000
    }));
  }

  private gerarDadosOperacionaisMock(filtros: any): any[] {
    const tecnicos = ['João Silva', 'Maria Santos', 'Pedro Costa', 'Ana Oliveira'];
    return tecnicos.map(tecnico => ({
      tecnico,
      osCompletas: Math.floor(Math.random() * 30) + 20,
      tempoMedio: Math.random() * 2 + 2,
      satisfacao: Math.random() * 1 + 4
    }));
  }

  private gerarDadosClientesMock(filtros: any): any[] {
    const clientes = ['TechCorp Ltda', 'InfoSys Solutions', 'Digital Works', 'Cyber Tech'];
    return clientes.map(nome => ({
      nome,
      osTotal: Math.floor(Math.random() * 20) + 10,
      valorTotal: Math.floor(Math.random() * 15000) + 5000,
      ultimaVisita: new Date(2024, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1).toISOString().split('T')[0]
    }));
  }

  private gerarDadosEstoqueMock(filtros: any): any[] {
    const itens = [
      { item: 'HD 1TB', categoria: 'Armazenamento', valorUnitario: 250 },
      { item: 'Memória RAM 8GB', categoria: 'Memória', valorUnitario: 180 },
      { item: 'Fonte 500W', categoria: 'Alimentação', valorUnitario: 120 },
      { item: 'Placa Mãe ATX', categoria: 'Placa Mãe', valorUnitario: 350 }
    ];
    
    return itens.map(item => ({
      ...item,
      quantidade: Math.floor(Math.random() * 20) + 5
    }));
  }

  // Métodos para integração com Google API (se necessário)
  async integrarGoogleSheets(relatorioId: string, sheetId: string): Promise<void> {
    try {
      const apiKey = import.meta.env.VITE_GOOGLE_API_KEY;
      if (!apiKey) {
        throw new Error('Google API Key não configurada');
      }

      // Implementar integração com Google Sheets API
      console.log('Integrando com Google Sheets:', { relatorioId, sheetId, apiKey });
      
      // Por enquanto, apenas log - implementar conforme necessário
    } catch (error) {
      console.error('Erro na integração com Google Sheets:', error);
      throw error;
    }
  }

  async enviarPorEmail(relatorioId: string, destinatarios: string[]): Promise<void> {
    try {
      // Implementar envio por email usando Google API ou outro serviço
      console.log('Enviando relatório por email:', { relatorioId, destinatarios });
      
      // Simular envio
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (error) {
      console.error('Erro ao enviar relatório por email:', error);
      throw error;
    }
  }

  async agendarRelatorio(configuracao: any): Promise<void> {
    try {
      // Implementar agendamento de relatórios
      console.log('Agendando relatório:', configuracao);
      
      // Salvar configuração de agendamento
      const { error } = await supabase
        .from('relatorios_agendados')
        .insert(configuracao);

      if (error) throw error;
    } catch (error) {
      console.error('Erro ao agendar relatório:', error);
      throw error;
    }
  }
}

export const relatoriosAPI = new RelatoriosAPI();