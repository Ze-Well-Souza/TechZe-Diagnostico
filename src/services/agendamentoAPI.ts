import { supabase } from '@/lib/supabase';

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

class AgendamentoAPI {
  private formatDate(date: Date): string {
    return date.toISOString().split('T')[0];
  }

  private parseDate(dateString: string): Date {
    return new Date(dateString + 'T00:00:00.000Z');
  }

  private gerarNumeroAgendamento(): string {
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.random().toString(36).substring(2, 5).toUpperCase();
    return `AG${timestamp}${random}`;
  }

  async obterDisponibilidade(
    dataInicio: Date,
    dataFim: Date
  ): Promise<DisponibilidadeData[]> {
    try {
      const { data: agendamentos, error: agendamentosError } = await supabase
        .from('agendamentos')
        .select('data, horario, tecnico_id, tecnicos(nome)')
        .gte('data', this.formatDate(dataInicio))
        .lte('data', this.formatDate(dataFim))
        .in('status', ['agendado', 'confirmado', 'em_andamento']);

      if (agendamentosError) {
        throw new Error(`Erro ao buscar agendamentos: ${agendamentosError.message}`);
      }

      const { data: configuracao, error: configError } = await supabase
        .from('configuracao_agendamento')
        .select('*')
        .single();

      if (configError) {
        console.warn('Configuração de agendamento não encontrada, usando padrões');
      }

      // Horários padrão (8h às 18h, intervalos de 1h)
      const horariosDisponiveis = configuracao?.horarios_disponiveis || [
        '08:00', '09:00', '10:00', '11:00',
        '13:00', '14:00', '15:00', '16:00', '17:00'
      ];

      const disponibilidade: DisponibilidadeData[] = [];
      const dataAtual = new Date(dataInicio);

      while (dataAtual <= dataFim) {
        const dataStr = this.formatDate(dataAtual);
        
        // Pular fins de semana (sábado = 6, domingo = 0)
        if (dataAtual.getDay() === 0 || dataAtual.getDay() === 6) {
          dataAtual.setDate(dataAtual.getDate() + 1);
          continue;
        }

        // Pular datas passadas
        const hoje = new Date();
        hoje.setHours(0, 0, 0, 0);
        if (dataAtual < hoje) {
          dataAtual.setDate(dataAtual.getDate() + 1);
          continue;
        }

        const agendamentosData = agendamentos?.filter(a => a.data === dataStr) || [];
        const horariosOcupados = agendamentosData.map(a => a.horario);

        const horarios: DisponibilidadeHorario[] = horariosDisponiveis.map(horario => {
          const agendamento = agendamentosData.find(a => a.horario === horario);
          return {
            horario,
            disponivel: !horariosOcupados.includes(horario),
            tecnicoId: agendamento?.tecnico_id,
            tecnicoNome: agendamento?.tecnicos?.nome
          };
        });

        disponibilidade.push({
          data: dataStr,
          horarios,
          totalDisponivel: horarios.filter(h => h.disponivel).length
        });

        dataAtual.setDate(dataAtual.getDate() + 1);
      }

      return disponibilidade;
    } catch (error) {
      console.error('Erro ao obter disponibilidade:', error);
      throw error;
    }
  }

  async listarAgendamentos(): Promise<Agendamento[]> {
    try {
      const { data, error } = await supabase
        .from('agendamentos')
        .select(`
          *,
          tecnicos(nome)
        `)
        .order('data', { ascending: true })
        .order('horario', { ascending: true });

      if (error) {
        throw new Error(`Erro ao listar agendamentos: ${error.message}`);
      }

      return data?.map(item => ({
        id: item.id,
        numero: item.numero,
        clienteNome: item.cliente_nome,
        clienteEmail: item.cliente_email,
        clienteTelefone: item.cliente_telefone,
        data: this.parseDate(item.data),
        horario: item.horario,
        tipoServico: item.tipo_servico,
        descricaoProblema: item.descricao_problema,
        equipamento: item.equipamento,
        status: item.status,
        tecnicoId: item.tecnico_id,
        tecnicoNome: item.tecnicos?.nome,
        criadoEm: new Date(item.created_at)
      })) || [];
    } catch (error) {
      console.error('Erro ao listar agendamentos:', error);
      throw error;
    }
  }

  async criar(dados: FormularioAgendamento): Promise<Agendamento> {
    try {
      // Verificar disponibilidade antes de criar
      const disponivel = await this.verificarDisponibilidade(dados.data, dados.horario);
      if (!disponivel) {
        throw new Error('Horário não está mais disponível');
      }

      const agendamentoData = {
        numero: this.gerarNumeroAgendamento(),
        cliente_nome: dados.nome,
        cliente_email: dados.email,
        cliente_telefone: dados.telefone,
        data: this.formatDate(dados.data),
        horario: dados.horario,
        tipo_servico: dados.tipoServico,
        descricao_problema: dados.descricaoProblema,
        equipamento: dados.equipamento,
        status: 'agendado'
      };

      const { data, error } = await supabase
        .from('agendamentos')
        .insert(agendamentoData)
        .select(`
          *,
          tecnicos(nome)
        `)
        .single();

      if (error) {
        throw new Error(`Erro ao criar agendamento: ${error.message}`);
      }

      // Enviar notificação por email (opcional)
      try {
        await this.enviarNotificacaoAgendamento(data);
      } catch (emailError) {
        console.warn('Erro ao enviar notificação por email:', emailError);
      }

      return {
        id: data.id,
        numero: data.numero,
        clienteNome: data.cliente_nome,
        clienteEmail: data.cliente_email,
        clienteTelefone: data.cliente_telefone,
        data: this.parseDate(data.data),
        horario: data.horario,
        tipoServico: data.tipo_servico,
        descricaoProblema: data.descricao_problema,
        equipamento: data.equipamento,
        status: data.status,
        tecnicoId: data.tecnico_id,
        tecnicoNome: data.tecnicos?.nome,
        criadoEm: new Date(data.created_at)
      };
    } catch (error) {
      console.error('Erro ao criar agendamento:', error);
      throw error;
    }
  }

  async confirmar(agendamentoId: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('agendamentos')
        .update({ 
          status: 'confirmado',
          confirmado_em: new Date().toISOString()
        })
        .eq('id', agendamentoId);

      if (error) {
        throw new Error(`Erro ao confirmar agendamento: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro ao confirmar agendamento:', error);
      throw error;
    }
  }

  async cancelar(agendamentoId: string, motivo?: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('agendamentos')
        .update({ 
          status: 'cancelado',
          motivo_cancelamento: motivo,
          cancelado_em: new Date().toISOString()
        })
        .eq('id', agendamentoId);

      if (error) {
        throw new Error(`Erro ao cancelar agendamento: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro ao cancelar agendamento:', error);
      throw error;
    }
  }

  async reagendar(
    agendamentoId: string,
    novaData: Date,
    novoHorario: string
  ): Promise<void> {
    try {
      // Verificar disponibilidade do novo horário
      const disponivel = await this.verificarDisponibilidade(novaData, novoHorario);
      if (!disponivel) {
        throw new Error('Novo horário não está disponível');
      }

      const { error } = await supabase
        .from('agendamentos')
        .update({ 
          data: this.formatDate(novaData),
          horario: novoHorario,
          status: 'agendado',
          reagendado_em: new Date().toISOString()
        })
        .eq('id', agendamentoId);

      if (error) {
        throw new Error(`Erro ao reagendar: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro ao reagendar agendamento:', error);
      throw error;
    }
  }

  async verificarDisponibilidade(data: Date, horario: string): Promise<boolean> {
    try {
      const { data: agendamentos, error } = await supabase
        .from('agendamentos')
        .select('id')
        .eq('data', this.formatDate(data))
        .eq('horario', horario)
        .in('status', ['agendado', 'confirmado', 'em_andamento']);

      if (error) {
        throw new Error(`Erro ao verificar disponibilidade: ${error.message}`);
      }

      return !agendamentos || agendamentos.length === 0;
    } catch (error) {
      console.error('Erro ao verificar disponibilidade:', error);
      throw error;
    }
  }

  async obterDetalhes(agendamentoId: string): Promise<Agendamento> {
    try {
      const { data, error } = await supabase
        .from('agendamentos')
        .select(`
          *,
          tecnicos(nome)
        `)
        .eq('id', agendamentoId)
        .single();

      if (error) {
        throw new Error(`Erro ao obter detalhes: ${error.message}`);
      }

      return {
        id: data.id,
        numero: data.numero,
        clienteNome: data.cliente_nome,
        clienteEmail: data.cliente_email,
        clienteTelefone: data.cliente_telefone,
        data: this.parseDate(data.data),
        horario: data.horario,
        tipoServico: data.tipo_servico,
        descricaoProblema: data.descricao_problema,
        equipamento: data.equipamento,
        status: data.status,
        tecnicoId: data.tecnico_id,
        tecnicoNome: data.tecnicos?.nome,
        criadoEm: new Date(data.created_at)
      };
    } catch (error) {
      console.error('Erro ao obter detalhes do agendamento:', error);
      throw error;
    }
  }

  private async enviarNotificacaoAgendamento(agendamento: any): Promise<void> {
    // Implementação futura para envio de notificações
    // Pode usar Supabase Edge Functions ou serviço de email
    console.log('Notificação de agendamento:', {
      email: agendamento.cliente_email,
      numero: agendamento.numero,
      data: agendamento.data,
      horario: agendamento.horario
    });
  }
}

export const agendamentoAPI = new AgendamentoAPI();