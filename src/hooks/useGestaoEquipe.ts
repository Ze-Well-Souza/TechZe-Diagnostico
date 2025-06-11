import { useState, useEffect } from 'react';
import { useToast } from './use-toast';

interface Funcionario {
  id: string;
  nome: string;
  email: string;
  telefone: string;
  funcao: string;
  salario: string;
  dataAdmissao: string;
  endereco: string;
  observacoes: string;
  status: 'ativo' | 'inativo' | 'ferias' | 'licenca';
  avatar?: string;
  permissoes: {
    vendas: boolean;
    estoque: boolean;
    financeiro: boolean;
    relatorios: boolean;
    configuracoes: boolean;
    admin: boolean;
  };
  criadoEm: string;
  atualizadoEm: string;
}

interface NovoFuncionario {
  nome: string;
  email: string;
  telefone: string;
  funcao: string;
  salario: string;
  dataAdmissao: string;
  endereco: string;
  observacoes: string;
  permissoes: {
    vendas: boolean;
    estoque: boolean;
    financeiro: boolean;
    relatorios: boolean;
    configuracoes: boolean;
    admin: boolean;
  };
}

interface Estatisticas {
  total: number;
  ativos: number;
  inativos: number;
  ausentes: number;
  folhaPagamento: string;
}

interface AtividadeHistorico {
  id: string;
  funcionarioId: string;
  funcionarioNome: string;
  acao: string;
  descricao: string;
  data: string;
  tipo: 'admissao' | 'demissao' | 'promocao' | 'alteracao' | 'ferias' | 'licenca';
}

export const useGestaoEquipe = () => {
  const [funcionarios, setFuncionarios] = useState<Funcionario[]>([]);
  const [carregando, setCarregando] = useState(true);
  const { toast } = useToast();

  // Dados simulados para demonstração
  const funcionariosIniciais: Funcionario[] = [
    {
      id: '1',
      nome: 'João Silva',
      email: 'joao.silva@techze.com.br',
      telefone: '(11) 99999-1111',
      funcao: 'Técnico',
      salario: 'R$ 3.500,00',
      dataAdmissao: '2023-01-15',
      endereco: 'Rua das Flores, 123, São Paulo, SP',
      observacoes: 'Especialista em smartphones e tablets',
      status: 'ativo',
      avatar: '',
      permissoes: {
        vendas: true,
        estoque: true,
        financeiro: false,
        relatorios: false,
        configuracoes: false,
        admin: false
      },
      criadoEm: '2023-01-15T10:00:00Z',
      atualizadoEm: '2024-01-15T10:00:00Z'
    },
    {
      id: '2',
      nome: 'Maria Santos',
      email: 'maria.santos@techze.com.br',
      telefone: '(11) 99999-2222',
      funcao: 'Vendedor',
      salario: 'R$ 2.800,00',
      dataAdmissao: '2023-03-20',
      endereco: 'Av. Paulista, 456, São Paulo, SP',
      observacoes: 'Excelente relacionamento com clientes',
      status: 'ativo',
      avatar: '',
      permissoes: {
        vendas: true,
        estoque: false,
        financeiro: false,
        relatorios: true,
        configuracoes: false,
        admin: false
      },
      criadoEm: '2023-03-20T10:00:00Z',
      atualizadoEm: '2024-01-15T10:00:00Z'
    },
    {
      id: '3',
      nome: 'Carlos Oliveira',
      email: 'carlos.oliveira@techze.com.br',
      telefone: '(11) 99999-3333',
      funcao: 'Gerente',
      salario: 'R$ 5.500,00',
      dataAdmissao: '2022-08-10',
      endereco: 'Rua Augusta, 789, São Paulo, SP',
      observacoes: 'Responsável pela gestão da equipe',
      status: 'ativo',
      avatar: '',
      permissoes: {
        vendas: true,
        estoque: true,
        financeiro: true,
        relatorios: true,
        configuracoes: true,
        admin: false
      },
      criadoEm: '2022-08-10T10:00:00Z',
      atualizadoEm: '2024-01-15T10:00:00Z'
    },
    {
      id: '4',
      nome: 'Ana Costa',
      email: 'ana.costa@techze.com.br',
      telefone: '(11) 99999-4444',
      funcao: 'Atendente',
      salario: 'R$ 2.200,00',
      dataAdmissao: '2023-06-05',
      endereco: 'Rua da Consolação, 321, São Paulo, SP',
      observacoes: 'Responsável pelo atendimento ao cliente',
      status: 'ferias',
      avatar: '',
      permissoes: {
        vendas: false,
        estoque: false,
        financeiro: false,
        relatorios: false,
        configuracoes: false,
        admin: false
      },
      criadoEm: '2023-06-05T10:00:00Z',
      atualizadoEm: '2024-01-15T10:00:00Z'
    },
    {
      id: '5',
      nome: 'Pedro Almeida',
      email: 'pedro.almeida@techze.com.br',
      telefone: '(11) 99999-5555',
      funcao: 'Administrador',
      salario: 'R$ 6.000,00',
      dataAdmissao: '2022-01-01',
      endereco: 'Rua Frei Caneca, 654, São Paulo, SP',
      observacoes: 'Administrador do sistema',
      status: 'ativo',
      avatar: '',
      permissoes: {
        vendas: true,
        estoque: true,
        financeiro: true,
        relatorios: true,
        configuracoes: true,
        admin: true
      },
      criadoEm: '2022-01-01T10:00:00Z',
      atualizadoEm: '2024-01-15T10:00:00Z'
    }
  ];

  useEffect(() => {
    // Simular carregamento dos dados
    const carregarFuncionarios = async () => {
      setCarregando(true);
      
      // Simular delay de API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Carregar dados do localStorage ou usar dados iniciais
      const dadosSalvos = localStorage.getItem('techze-funcionarios');
      if (dadosSalvos) {
        setFuncionarios(JSON.parse(dadosSalvos));
      } else {
        setFuncionarios(funcionariosIniciais);
        localStorage.setItem('techze-funcionarios', JSON.stringify(funcionariosIniciais));
      }
      
      setCarregando(false);
    };

    carregarFuncionarios();
  }, []);

  const salvarNoLocalStorage = (novosFuncionarios: Funcionario[]) => {
    localStorage.setItem('techze-funcionarios', JSON.stringify(novosFuncionarios));
  };

  const adicionarFuncionario = async (novoFuncionario: NovoFuncionario): Promise<void> => {
    return new Promise((resolve, reject) => {
      try {
        const funcionario: Funcionario = {
          ...novoFuncionario,
          id: Date.now().toString(),
          status: 'ativo',
          avatar: '',
          criadoEm: new Date().toISOString(),
          atualizadoEm: new Date().toISOString()
        };

        const novosFuncionarios = [...funcionarios, funcionario];
        setFuncionarios(novosFuncionarios);
        salvarNoLocalStorage(novosFuncionarios);
        
        // Registrar atividade
        registrarAtividade(funcionario.id, funcionario.nome, 'admissao', `${funcionario.nome} foi adicionado à equipe como ${funcionario.funcao}`);
        
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  };

  const editarFuncionario = async (id: string, dadosAtualizados: Partial<NovoFuncionario>): Promise<void> => {
    return new Promise((resolve, reject) => {
      try {
        const novosFuncionarios = funcionarios.map(funcionario => {
          if (funcionario.id === id) {
            const funcionarioAtualizado = {
              ...funcionario,
              ...dadosAtualizados,
              atualizadoEm: new Date().toISOString()
            };
            
            // Registrar atividade
            registrarAtividade(id, funcionarioAtualizado.nome, 'alteracao', `Informações de ${funcionarioAtualizado.nome} foram atualizadas`);
            
            return funcionarioAtualizado;
          }
          return funcionario;
        });

        setFuncionarios(novosFuncionarios);
        salvarNoLocalStorage(novosFuncionarios);
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  };

  const removerFuncionario = async (id: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      try {
        const funcionario = funcionarios.find(f => f.id === id);
        if (!funcionario) {
          reject(new Error('Funcionário não encontrado'));
          return;
        }

        const novosFuncionarios = funcionarios.filter(f => f.id !== id);
        setFuncionarios(novosFuncionarios);
        salvarNoLocalStorage(novosFuncionarios);
        
        // Registrar atividade
        registrarAtividade(id, funcionario.nome, 'demissao', `${funcionario.nome} foi removido da equipe`);
        
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  };

  const alterarStatus = async (id: string, novoStatus: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      try {
        const novosFuncionarios = funcionarios.map(funcionario => {
          if (funcionario.id === id) {
            const funcionarioAtualizado = {
              ...funcionario,
              status: novoStatus as Funcionario['status'],
              atualizadoEm: new Date().toISOString()
            };
            
            // Registrar atividade
            const acoes = {
              ativo: 'ativação',
              inativo: 'inativação',
              ferias: 'férias',
              licenca: 'licença'
            };
            
            registrarAtividade(
              id, 
              funcionarioAtualizado.nome, 
              novoStatus as AtividadeHistorico['tipo'], 
              `Status de ${funcionarioAtualizado.nome} alterado para ${acoes[novoStatus as keyof typeof acoes]}`
            );
            
            return funcionarioAtualizado;
          }
          return funcionario;
        });

        setFuncionarios(novosFuncionarios);
        salvarNoLocalStorage(novosFuncionarios);
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  };

  const obterEstatisticas = (): Estatisticas => {
    const total = funcionarios.length;
    const ativos = funcionarios.filter(f => f.status === 'ativo').length;
    const inativos = funcionarios.filter(f => f.status === 'inativo').length;
    const ausentes = funcionarios.filter(f => ['ferias', 'licenca'].includes(f.status)).length;
    
    // Calcular folha de pagamento (simulado)
    const totalSalarios = funcionarios
      .filter(f => f.status === 'ativo')
      .reduce((total, funcionario) => {
        const salario = parseFloat(funcionario.salario.replace(/[R$\s.,]/g, '').replace(',', '.')) || 0;
        return total + salario;
      }, 0);
    
    const folhaPagamento = new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(totalSalarios);

    return {
      total,
      ativos,
      inativos,
      ausentes,
      folhaPagamento
    };
  };

  const registrarAtividade = (funcionarioId: string, funcionarioNome: string, tipo: AtividadeHistorico['tipo'], descricao: string) => {
    const atividade: AtividadeHistorico = {
      id: Date.now().toString(),
      funcionarioId,
      funcionarioNome,
      acao: tipo,
      descricao,
      data: new Date().toISOString(),
      tipo
    };

    // Salvar no localStorage
    const atividadesExistentes = JSON.parse(localStorage.getItem('techze-atividades-funcionarios') || '[]');
    const novasAtividades = [atividade, ...atividadesExistentes].slice(0, 100); // Manter apenas as últimas 100
    localStorage.setItem('techze-atividades-funcionarios', JSON.stringify(novasAtividades));
  };

  const obterHistoricoAtividades = (): AtividadeHistorico[] => {
    const atividades = JSON.parse(localStorage.getItem('techze-atividades-funcionarios') || '[]');
    return atividades.slice(0, 20); // Retornar apenas as últimas 20 atividades
  };

  const obterFuncionarioPorId = (id: string): Funcionario | undefined => {
    return funcionarios.find(f => f.id === id);
  };

  const obterFuncionariosPorFuncao = (funcao: string): Funcionario[] => {
    return funcionarios.filter(f => f.funcao === funcao);
  };

  const obterFuncionariosPorStatus = (status: string): Funcionario[] => {
    return funcionarios.filter(f => f.status === status);
  };

  const validarPermissoes = (funcionarioId: string, permissao: keyof Funcionario['permissoes']): boolean => {
    const funcionario = obterFuncionarioPorId(funcionarioId);
    return funcionario?.permissoes[permissao] || false;
  };

  const exportarDados = (): string => {
    const dados = {
      funcionarios,
      estatisticas: obterEstatisticas(),
      atividades: obterHistoricoAtividades(),
      exportadoEm: new Date().toISOString()
    };
    
    return JSON.stringify(dados, null, 2);
  };

  const importarDados = async (dadosJson: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      try {
        const dados = JSON.parse(dadosJson);
        
        if (dados.funcionarios && Array.isArray(dados.funcionarios)) {
          setFuncionarios(dados.funcionarios);
          salvarNoLocalStorage(dados.funcionarios);
          
          if (dados.atividades) {
            localStorage.setItem('techze-atividades-funcionarios', JSON.stringify(dados.atividades));
          }
          
          resolve();
        } else {
          reject(new Error('Formato de dados inválido'));
        }
      } catch (error) {
        reject(error);
      }
    });
  };

  return {
    funcionarios,
    carregando,
    adicionarFuncionario,
    editarFuncionario,
    removerFuncionario,
    alterarStatus,
    obterEstatisticas,
    obterHistoricoAtividades,
    obterFuncionarioPorId,
    obterFuncionariosPorFuncao,
    obterFuncionariosPorStatus,
    validarPermissoes,
    exportarDados,
    importarDados
  };
};