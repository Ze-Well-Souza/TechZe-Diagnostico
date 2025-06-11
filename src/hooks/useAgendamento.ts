import { useState, useCallback } from 'react';
import { agendamentoAPI } from '@/services/agendamentoAPI';
import { toast } from '@/hooks/use-toast';

interface DisponibilidadeHorario {
  horario: string;
  disponivel: boolean;
  tecnicoId?: string;
  tecnicoNome?: string;
}

interface DisponibilidadeData {
  data: string;
  horarios: DisponibilidadeHorario[];
  totalDisponivel: number;
}

interface Agendamento {
  id: string;
  numero: string;
  clienteNome: string;
  clienteEmail: string;
  clienteTelefone: string;
  data: Date;
  horario: string;
  tipoServico: string;
  descricaoProblema: string;
  equipamento: {
    tipo: string;
    marca: string;
    modelo: string;
  };
  status: 'agendado' | 'confirmado' | 'em_andamento' | 'concluido' | 'cancelado';
  tecnicoId?: string;
  tecnicoNome?: string;
  criadoEm: Date;
}

interface FormularioAgendamento {
  data: Date;
  horario: string;
  nome: string;
  email: string;
  telefone: string;
  tipoServico: string;
  descricaoProblema: string;
  equipamento: {
    tipo: string;
    marca: string;
    modelo: string;
  };
}

interface UseAgendamentoOptions {
  autoLoad?: boolean;
  diasAntecedencia?: number;
}

interface UseAgendamentoReturn {
  disponibilidade: DisponibilidadeData[];
  agendamentos: Agendamento[];
  loading: boolean;
  error: string | null;
  // Funções
  carregarDisponibilidade: (dataInicio?: Date, dataFim?: Date) => Promise<void>;
  carregarAgendamentos: () => Promise<void>;
  criarAgendamento: (dados: FormularioAgendamento) => Promise<Agendamento>;
  confirmarAgendamento: (agendamentoId: string) => Promise<void>;
  cancelarAgendamento: (agendamentoId: string, motivo?: string) => Promise<void>;
  reagendarAgendamento: (agendamentoId: string, novaData: Date, novoHorario: string) => Promise<void>;
  verificarDisponibilidade: (data: Date, horario: string) => Promise<boolean>;
}

export function useAgendamento(options: UseAgendamentoOptions = {}): UseAgendamentoReturn {
  const { autoLoad = true, diasAntecedencia = 30 } = options;
  
  const [disponibilidade, setDisponibilidade] = useState<DisponibilidadeData[]>([]);
  const [agendamentos, setAgendamentos] = useState<Agendamento[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const carregarDisponibilidade = useCallback(async (
    dataInicio?: Date,
    dataFim?: Date
  ) => {
    try {
      setLoading(true);
      setError(null);
      
      const inicio = dataInicio || new Date();
      const fim = dataFim || new Date(Date.now() + diasAntecedencia * 24 * 60 * 60 * 1000);
      
      const dados = await agendamentoAPI.obterDisponibilidade(inicio, fim);
      setDisponibilidade(dados);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar disponibilidade';
      setError(errorMessage);
      console.error('Erro ao carregar disponibilidade:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, [diasAntecedencia]);

  const carregarAgendamentos = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const dados = await agendamentoAPI.listarAgendamentos();
      setAgendamentos(dados);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar agendamentos';
      setError(errorMessage);
      console.error('Erro ao carregar agendamentos:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const criarAgendamento = useCallback(async (dados: FormularioAgendamento): Promise<Agendamento> => {
    try {
      setError(null);
      
      // Verificar disponibilidade antes de criar
      const disponivel = await agendamentoAPI.verificarDisponibilidade(
        dados.data,
        dados.horario
      );
      
      if (!disponivel) {
        throw new Error('Horário não está mais disponível. Por favor, escolha outro horário.');
      }
      
      const novoAgendamento = await agendamentoAPI.criar(dados);
      
      // Atualizar lista local
      setAgendamentos(prev => [novoAgendamento, ...prev]);
      
      // Recarregar disponibilidade
      await carregarDisponibilidade();
      
      toast({
        title: 'Sucesso!',
        description: 'Agendamento criado com sucesso!'
      });
      
      return novoAgendamento;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar agendamento';
      setError(errorMessage);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
      
      throw err;
    }
  }, [carregarDisponibilidade]);

  const confirmarAgendamento = useCallback(async (agendamentoId: string) => {
    try {
      await agendamentoAPI.confirmar(agendamentoId);
      
      // Atualizar status no estado local
      setAgendamentos(prev => 
        prev.map(agendamento => 
          agendamento.id === agendamentoId 
            ? { ...agendamento, status: 'confirmado' as const }
            : agendamento
        )
      );
      
      toast({
        title: 'Sucesso',
        description: 'Agendamento confirmado!'
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao confirmar agendamento';
      console.error('Erro ao confirmar agendamento:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
    }
  }, []);

  const cancelarAgendamento = useCallback(async (agendamentoId: string, motivo?: string) => {
    try {
      await agendamentoAPI.cancelar(agendamentoId, motivo);
      
      // Atualizar status no estado local
      setAgendamentos(prev => 
        prev.map(agendamento => 
          agendamento.id === agendamentoId 
            ? { ...agendamento, status: 'cancelado' as const }
            : agendamento
        )
      );
      
      // Recarregar disponibilidade
      await carregarDisponibilidade();
      
      toast({
        title: 'Agendamento cancelado',
        description: 'O agendamento foi cancelado com sucesso.'
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao cancelar agendamento';
      console.error('Erro ao cancelar agendamento:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
    }
  }, [carregarDisponibilidade]);

  const reagendarAgendamento = useCallback(async (
    agendamentoId: string,
    novaData: Date,
    novoHorario: string
  ) => {
    try {
      // Verificar disponibilidade do novo horário
      const disponivel = await agendamentoAPI.verificarDisponibilidade(
        novaData,
        novoHorario
      );
      
      if (!disponivel) {
        throw new Error('Novo horário não está disponível. Por favor, escolha outro horário.');
      }
      
      await agendamentoAPI.reagendar(agendamentoId, novaData, novoHorario);
      
      // Atualizar agendamento no estado local
      setAgendamentos(prev => 
        prev.map(agendamento => 
          agendamento.id === agendamentoId 
            ? { 
                ...agendamento, 
                data: novaData, 
                horario: novoHorario,
                status: 'agendado' as const
              }
            : agendamento
        )
      );
      
      // Recarregar disponibilidade
      await carregarDisponibilidade();
      
      toast({
        title: 'Sucesso',
        description: 'Agendamento reagendado com sucesso!'
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao reagendar';
      console.error('Erro ao reagendar agendamento:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
    }
  }, [carregarDisponibilidade]);

  const verificarDisponibilidade = useCallback(async (
    data: Date,
    horario: string
  ): Promise<boolean> => {
    try {
      return await agendamentoAPI.verificarDisponibilidade(data, horario);
    } catch (err) {
      console.error('Erro ao verificar disponibilidade:', err);
      return false;
    }
  }, []);

  return {
    disponibilidade,
    agendamentos,
    loading,
    error,
    carregarDisponibilidade,
    carregarAgendamentos,
    criarAgendamento,
    confirmarAgendamento,
    cancelarAgendamento,
    reagendarAgendamento,
    verificarDisponibilidade
  };
}