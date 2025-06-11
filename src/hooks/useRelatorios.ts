import { useState, useCallback } from 'react';
import { relatoriosAPI } from '@/services/relatoriosAPI';
import { useToast } from '@/hooks/use-toast';
import { 
  DollarSign, 
  Users, 
  Package, 
  Wrench, 
  TrendingUp,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

export interface FiltroRelatorio {
  dataInicio: Date;
  dataFim: Date;
  tipoRelatorio: string;
  categoria: string;
  status: string;
  cliente?: string;
  tecnico?: string;
}

export interface DadosRelatorio {
  id: string;
  titulo: string;
  tipo: string;
  dados: any[];
  metadados: {
    total: number;
    periodo: string;
    geradoEm: Date;
  };
}

export interface MetricaResumo {
  label: string;
  valor: string;
  variacao?: number;
  icon: any;
}

export interface DadosGrafico {
  titulo: string;
  tipo: 'line' | 'bar' | 'pie' | 'doughnut';
  dados: any;
  opcoes?: any;
}

export interface ResumoExecutivo {
  metricas: MetricaResumo[];
  insights: string[];
  recomendacoes: string[];
}

export function useRelatorios() {
  const [carregandoRelatorios, setCarregandoRelatorios] = useState(false);
  const { toast } = useToast();

  const gerarRelatorio = useCallback(async (filtros: FiltroRelatorio): Promise<DadosRelatorio> => {
    setCarregandoRelatorios(true);
    try {
      // Simular dados baseados no tipo de relatório
      const dados = await gerarDadosRelatorio(filtros);
      
      toast({
        title: "Relatório gerado com sucesso",
        description: `Relatório ${filtros.tipoRelatorio} gerado para o período selecionado.`,
      });
      
      return dados;
    } catch (error) {
      toast({
        title: "Erro ao gerar relatório",
        description: "Não foi possível gerar o relatório. Tente novamente.",
        variant: "destructive",
      });
      throw error;
    } finally {
      setCarregandoRelatorios(false);
    }
  }, [toast]);

  const exportarRelatorio = useCallback(async (relatorio: DadosRelatorio, formato: string) => {
    try {
      await relatoriosAPI.exportar(relatorio.id, formato);
      
      toast({
        title: "Relatório exportado",
        description: `Relatório exportado em formato ${formato.toUpperCase()}.`,
      });
    } catch (error) {
      toast({
        title: "Erro na exportação",
        description: "Não foi possível exportar o relatório.",
        variant: "destructive",
      });
      throw error;
    }
  }, [toast]);

  const obterDadosGraficos = useCallback((relatorio: DadosRelatorio): DadosGrafico[] => {
    switch (relatorio.tipo) {
      case 'financeiro':
        return gerarGraficosFinanceiros(relatorio.dados);
      case 'operacional':
        return gerarGraficosOperacionais(relatorio.dados);
      case 'clientes':
        return gerarGraficosClientes(relatorio.dados);
      case 'estoque':
        return gerarGraficosEstoque(relatorio.dados);
      default:
        return [];
    }
  }, []);

  const obterResumoExecutivo = useCallback((relatorio: DadosRelatorio): ResumoExecutivo => {
    switch (relatorio.tipo) {
      case 'financeiro':
        return gerarResumoFinanceiro(relatorio.dados);
      case 'operacional':
        return gerarResumoOperacional(relatorio.dados);
      case 'clientes':
        return gerarResumoClientes(relatorio.dados);
      case 'estoque':
        return gerarResumoEstoque(relatorio.dados);
      default:
        return { metricas: [], insights: [], recomendacoes: [] };
    }
  }, []);

  const salvarRelatorio = useCallback(async (relatorio: DadosRelatorio) => {
    try {
      await relatoriosAPI.salvar(relatorio);
      
      toast({
        title: "Relatório salvo",
        description: "Relatório salvo com sucesso.",
      });
    } catch (error) {
      toast({
        title: "Erro ao salvar",
        description: "Não foi possível salvar o relatório.",
        variant: "destructive",
      });
      throw error;
    }
  }, [toast]);

  return {
    gerarRelatorio,
    exportarRelatorio,
    obterDadosGraficos,
    obterResumoExecutivo,
    salvarRelatorio,
    carregandoRelatorios
  };
}

// Funções auxiliares para gerar dados simulados
async function gerarDadosRelatorio(filtros: FiltroRelatorio): Promise<DadosRelatorio> {
  // Simular delay de API
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  const id = `rel_${Date.now()}`;
  const titulo = `Relatório ${filtros.tipoRelatorio.charAt(0).toUpperCase() + filtros.tipoRelatorio.slice(1)}`;
  
  let dados: any[] = [];
  
  switch (filtros.tipoRelatorio) {
    case 'financeiro':
      dados = gerarDadosFinanceiros();
      break;
    case 'operacional':
      dados = gerarDadosOperacionais();
      break;
    case 'clientes':
      dados = gerarDadosClientes();
      break;
    case 'estoque':
      dados = gerarDadosEstoque();
      break;
    default:
      dados = [];
  }
  
  return {
    id,
    titulo,
    tipo: filtros.tipoRelatorio,
    dados,
    metadados: {
      total: dados.length,
      periodo: `${filtros.dataInicio.toLocaleDateString()} - ${filtros.dataFim.toLocaleDateString()}`,
      geradoEm: new Date()
    }
  };
}

function gerarDadosFinanceiros() {
  return [
    { mes: 'Janeiro', receitas: 15000, despesas: 8000, lucro: 7000 },
    { mes: 'Fevereiro', receitas: 18000, despesas: 9000, lucro: 9000 },
    { mes: 'Março', receitas: 22000, despesas: 10000, lucro: 12000 },
    { mes: 'Abril', receitas: 20000, despesas: 9500, lucro: 10500 },
    { mes: 'Maio', receitas: 25000, despesas: 11000, lucro: 14000 },
    { mes: 'Junho', receitas: 28000, despesas: 12000, lucro: 16000 }
  ];
}

function gerarDadosOperacionais() {
  return [
    { tecnico: 'João Silva', osCompletas: 45, tempoMedio: 2.5, satisfacao: 4.8 },
    { tecnico: 'Maria Santos', osCompletas: 38, tempoMedio: 3.2, satisfacao: 4.6 },
    { tecnico: 'Pedro Costa', osCompletas: 42, tempoMedio: 2.8, satisfacao: 4.7 },
    { tecnico: 'Ana Oliveira', osCompletas: 35, tempoMedio: 3.5, satisfacao: 4.5 }
  ];
}

function gerarDadosClientes() {
  return [
    { nome: 'TechCorp Ltda', osTotal: 25, valorTotal: 15000, ultimaVisita: '2024-01-15' },
    { nome: 'InfoSys Solutions', osTotal: 18, valorTotal: 12000, ultimaVisita: '2024-01-10' },
    { nome: 'Digital Works', osTotal: 22, valorTotal: 18000, ultimaVisita: '2024-01-20' },
    { nome: 'Cyber Tech', osTotal: 15, valorTotal: 9000, ultimaVisita: '2024-01-08' }
  ];
}

function gerarDadosEstoque() {
  return [
    { item: 'HD 1TB', quantidade: 15, valorUnitario: 250, categoria: 'Armazenamento' },
    { item: 'Memória RAM 8GB', quantidade: 8, valorUnitario: 180, categoria: 'Memória' },
    { item: 'Fonte 500W', quantidade: 12, valorUnitario: 120, categoria: 'Alimentação' },
    { item: 'Placa Mãe ATX', quantidade: 5, valorUnitario: 350, categoria: 'Placa Mãe' }
  ];
}

function gerarGraficosFinanceiros(dados: any[]): DadosGrafico[] {
  return [
    {
      titulo: 'Receitas vs Despesas',
      tipo: 'line',
      dados: {
        labels: dados.map(d => d.mes),
        datasets: [
          {
            label: 'Receitas',
            data: dados.map(d => d.receitas),
            borderColor: 'rgb(34, 197, 94)',
            backgroundColor: 'rgba(34, 197, 94, 0.1)'
          },
          {
            label: 'Despesas',
            data: dados.map(d => d.despesas),
            borderColor: 'rgb(239, 68, 68)',
            backgroundColor: 'rgba(239, 68, 68, 0.1)'
          }
        ]
      }
    },
    {
      titulo: 'Distribuição de Lucro',
      tipo: 'bar',
      dados: {
        labels: dados.map(d => d.mes),
        datasets: [
          {
            label: 'Lucro',
            data: dados.map(d => d.lucro),
            backgroundColor: 'rgba(59, 130, 246, 0.8)'
          }
        ]
      }
    }
  ];
}

function gerarGraficosOperacionais(dados: any[]): DadosGrafico[] {
  return [
    {
      titulo: 'OS Completas por Técnico',
      tipo: 'bar',
      dados: {
        labels: dados.map(d => d.tecnico),
        datasets: [
          {
            label: 'OS Completas',
            data: dados.map(d => d.osCompletas),
            backgroundColor: 'rgba(168, 85, 247, 0.8)'
          }
        ]
      }
    },
    {
      titulo: 'Tempo Médio de Reparo',
      tipo: 'line',
      dados: {
        labels: dados.map(d => d.tecnico),
        datasets: [
          {
            label: 'Tempo (horas)',
            data: dados.map(d => d.tempoMedio),
            borderColor: 'rgb(245, 158, 11)',
            backgroundColor: 'rgba(245, 158, 11, 0.1)'
          }
        ]
      }
    }
  ];
}

function gerarGraficosClientes(dados: any[]): DadosGrafico[] {
  return [
    {
      titulo: 'Valor Total por Cliente',
      tipo: 'pie',
      dados: {
        labels: dados.map(d => d.nome),
        datasets: [
          {
            data: dados.map(d => d.valorTotal),
            backgroundColor: [
              'rgba(239, 68, 68, 0.8)',
              'rgba(34, 197, 94, 0.8)',
              'rgba(59, 130, 246, 0.8)',
              'rgba(245, 158, 11, 0.8)'
            ]
          }
        ]
      }
    }
  ];
}

function gerarGraficosEstoque(dados: any[]): DadosGrafico[] {
  return [
    {
      titulo: 'Quantidade em Estoque',
      tipo: 'doughnut',
      dados: {
        labels: dados.map(d => d.item),
        datasets: [
          {
            data: dados.map(d => d.quantidade),
            backgroundColor: [
              'rgba(168, 85, 247, 0.8)',
              'rgba(236, 72, 153, 0.8)',
              'rgba(14, 165, 233, 0.8)',
              'rgba(34, 197, 94, 0.8)'
            ]
          }
        ]
      }
    }
  ];
}

function gerarResumoFinanceiro(dados: any[]): ResumoExecutivo {
  const totalReceitas = dados.reduce((acc, d) => acc + d.receitas, 0);
  const totalDespesas = dados.reduce((acc, d) => acc + d.despesas, 0);
  const totalLucro = totalReceitas - totalDespesas;
  const margemLucro = (totalLucro / totalReceitas) * 100;
  
  return {
    metricas: [
      {
        label: 'Receita Total',
        valor: `R$ ${totalReceitas.toLocaleString()}`,
        variacao: 12.5,
        icon: DollarSign
      },
      {
        label: 'Despesas Totais',
        valor: `R$ ${totalDespesas.toLocaleString()}`,
        variacao: -5.2,
        icon: TrendingUp
      },
      {
        label: 'Lucro Líquido',
        valor: `R$ ${totalLucro.toLocaleString()}`,
        variacao: 18.7,
        icon: CheckCircle
      },
      {
        label: 'Margem de Lucro',
        valor: `${margemLucro.toFixed(1)}%`,
        variacao: 3.2,
        icon: TrendingUp
      }
    ],
    insights: [
      'Crescimento consistente nas receitas nos últimos 3 meses',
      'Redução de 5% nas despesas operacionais',
      'Margem de lucro acima da média do setor'
    ],
    recomendacoes: [
      'Manter foco na redução de custos operacionais',
      'Investir em marketing para aumentar receitas',
      'Diversificar fontes de receita'
    ]
  };
}

function gerarResumoOperacional(dados: any[]): ResumoExecutivo {
  const totalOS = dados.reduce((acc, d) => acc + d.osCompletas, 0);
  const tempoMedio = dados.reduce((acc, d) => acc + d.tempoMedio, 0) / dados.length;
  const satisfacaoMedia = dados.reduce((acc, d) => acc + d.satisfacao, 0) / dados.length;
  
  return {
    metricas: [
      {
        label: 'OS Completas',
        valor: totalOS.toString(),
        variacao: 8.3,
        icon: CheckCircle
      },
      {
        label: 'Tempo Médio',
        valor: `${tempoMedio.toFixed(1)}h`,
        variacao: -12.1,
        icon: Clock
      },
      {
        label: 'Satisfação',
        valor: satisfacaoMedia.toFixed(1),
        variacao: 5.7,
        icon: Users
      },
      {
        label: 'Produtividade',
        valor: '92%',
        variacao: 4.2,
        icon: TrendingUp
      }
    ],
    insights: [
      'Aumento de 8% na produtividade geral',
      'Redução significativa no tempo médio de reparo',
      'Alta satisfação dos clientes mantida'
    ],
    recomendacoes: [
      'Implementar treinamentos para técnicos com menor performance',
      'Padronizar processos de reparo mais eficientes',
      'Investir em ferramentas que aceleram diagnósticos'
    ]
  };
}

function gerarResumoClientes(dados: any[]): ResumoExecutivo {
  const totalClientes = dados.length;
  const valorMedio = dados.reduce((acc, d) => acc + d.valorTotal, 0) / dados.length;
  const osMedio = dados.reduce((acc, d) => acc + d.osTotal, 0) / dados.length;
  
  return {
    metricas: [
      {
        label: 'Total Clientes',
        valor: totalClientes.toString(),
        variacao: 15.2,
        icon: Users
      },
      {
        label: 'Valor Médio',
        valor: `R$ ${valorMedio.toLocaleString()}`,
        variacao: 7.8,
        icon: DollarSign
      },
      {
        label: 'OS por Cliente',
        valor: osMedio.toFixed(1),
        variacao: 3.5,
        icon: Wrench
      },
      {
        label: 'Retenção',
        valor: '85%',
        variacao: 2.1,
        icon: CheckCircle
      }
    ],
    insights: [
      'Crescimento de 15% na base de clientes',
      'Aumento no valor médio por cliente',
      'Alta taxa de retenção de clientes'
    ],
    recomendacoes: [
      'Implementar programa de fidelidade',
      'Oferecer serviços premium para clientes VIP',
      'Melhorar comunicação pós-venda'
    ]
  };
}

function gerarResumoEstoque(dados: any[]): ResumoExecutivo {
  const totalItens = dados.length;
  const valorTotal = dados.reduce((acc, d) => acc + (d.quantidade * d.valorUnitario), 0);
  const quantidadeTotal = dados.reduce((acc, d) => acc + d.quantidade, 0);
  
  return {
    metricas: [
      {
        label: 'Itens em Estoque',
        valor: totalItens.toString(),
        icon: Package
      },
      {
        label: 'Valor Total',
        valor: `R$ ${valorTotal.toLocaleString()}`,
        icon: DollarSign
      },
      {
        label: 'Quantidade Total',
        valor: quantidadeTotal.toString(),
        icon: Package
      },
      {
        label: 'Itens Baixo Estoque',
        valor: '2',
        icon: AlertCircle
      }
    ],
    insights: [
      'Estoque bem diversificado por categoria',
      '2 itens com estoque baixo necessitam reposição',
      'Valor total do estoque dentro do planejado'
    ],
    recomendacoes: [
      'Reabastecer itens com estoque baixo',
      'Implementar alertas automáticos de reposição',
      'Analisar giro de estoque por categoria'
    ]
  };
}