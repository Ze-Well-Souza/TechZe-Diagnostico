import { OrdemServico, Orcamento } from '@/types/shared';
import { supabase } from '@/lib/supabase';

interface AvaliacaoServico {
  nota: number;
  comentario?: string;
}

class PortalClienteAPI {
  async obterOrdensAtivas(clienteId: string): Promise<OrdemServico[]> {
    try {
      const { data, error } = await supabase
        .from('ordens_servico')
        .select(`
          *,
          cliente:clientes(*),
          equipamento:equipamentos(*),
          tecnico:tecnicos(*),
          orcamento:orcamentos(*),
          diagnostico:diagnosticos(*)
        `)
        .eq('cliente_id', clienteId)
        .neq('status', 'concluido')
        .order('criado_em', { ascending: false });

      if (error) {
        throw new Error(`Erro ao buscar ordens ativas: ${error.message}`);
      }

      return data || [];
    } catch (error) {
      console.error('Erro na API - obterOrdensAtivas:', error);
      throw error;
    }
  }

  async obterHistorico(clienteId: string): Promise<OrdemServico[]> {
    try {
      const { data, error } = await supabase
        .from('ordens_servico')
        .select(`
          *,
          cliente:clientes(*),
          equipamento:equipamentos(*),
          tecnico:tecnicos(*),
          orcamento:orcamentos(*),
          diagnostico:diagnosticos(*),
          avaliacao:avaliacoes(*)
        `)
        .eq('cliente_id', clienteId)
        .eq('status', 'concluido')
        .order('atualizado_em', { ascending: false })
        .limit(50); // Limitar a 50 registros mais recentes

      if (error) {
        throw new Error(`Erro ao buscar histórico: ${error.message}`);
      }

      return data || [];
    } catch (error) {
      console.error('Erro na API - obterHistorico:', error);
      throw error;
    }
  }

  async obterDetalhesOS(osId: string): Promise<OrdemServico> {
    try {
      const { data, error } = await supabase
        .from('ordens_servico')
        .select(`
          *,
          cliente:clientes(*),
          equipamento:equipamentos(*),
          tecnico:tecnicos(*),
          orcamento:orcamentos(*),
          diagnostico:diagnosticos(*),
          avaliacao:avaliacoes(*),
          observacoes:observacoes_os(*)
        `)
        .eq('id', osId)
        .single();

      if (error) {
        throw new Error(`Erro ao buscar detalhes da OS: ${error.message}`);
      }

      if (!data) {
        throw new Error('Ordem de serviço não encontrada');
      }

      return data;
    } catch (error) {
      console.error('Erro na API - obterDetalhesOS:', error);
      throw error;
    }
  }

  async avaliarServico(osId: string, avaliacao: AvaliacaoServico): Promise<void> {
    try {
      // Verificar se já existe uma avaliação
      const { data: avaliacaoExistente } = await supabase
        .from('avaliacoes')
        .select('id')
        .eq('ordem_servico_id', osId)
        .single();

      if (avaliacaoExistente) {
        throw new Error('Esta ordem de serviço já foi avaliada');
      }

      // Criar nova avaliação
      const { error } = await supabase
        .from('avaliacoes')
        .insert({
          ordem_servico_id: osId,
          nota: avaliacao.nota,
          comentario: avaliacao.comentario,
          criado_em: new Date().toISOString()
        });

      if (error) {
        throw new Error(`Erro ao salvar avaliação: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro na API - avaliarServico:', error);
      throw error;
    }
  }

  async baixarOrcamento(orcamentoId: string): Promise<Blob> {
    try {
      // Buscar dados do orçamento
      const { data: orcamento, error } = await supabase
        .from('orcamentos')
        .select(`
          *,
          ordem_servico:ordens_servico(
            *,
            cliente:clientes(*),
            equipamento:equipamentos(*)
          ),
          itens:orcamento_itens(*)
        `)
        .eq('id', orcamentoId)
        .single();

      if (error) {
        throw new Error(`Erro ao buscar orçamento: ${error.message}`);
      }

      if (!orcamento) {
        throw new Error('Orçamento não encontrado');
      }

      // Gerar PDF do orçamento
      const response = await fetch('/api/orcamentos/pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ orcamento })
      });

      if (!response.ok) {
        throw new Error('Erro ao gerar PDF do orçamento');
      }

      return await response.blob();
    } catch (error) {
      console.error('Erro na API - baixarOrcamento:', error);
      throw error;
    }
  }

  async aprovarOrcamento(orcamentoId: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('orcamentos')
        .update({
          status: 'aprovado',
          aprovado_em: new Date().toISOString(),
          atualizado_em: new Date().toISOString()
        })
        .eq('id', orcamentoId);

      if (error) {
        throw new Error(`Erro ao aprovar orçamento: ${error.message}`);
      }

      // Atualizar status da OS para "em_reparo"
      const { data: orcamento } = await supabase
        .from('orcamentos')
        .select('ordem_servico_id')
        .eq('id', orcamentoId)
        .single();

      if (orcamento?.ordem_servico_id) {
        await supabase
          .from('ordens_servico')
          .update({
            status: 'em_reparo',
            atualizado_em: new Date().toISOString()
          })
          .eq('id', orcamento.ordem_servico_id);
      }
    } catch (error) {
      console.error('Erro na API - aprovarOrcamento:', error);
      throw error;
    }
  }

  async rejeitarOrcamento(orcamentoId: string, motivo?: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('orcamentos')
        .update({
          status: 'rejeitado',
          motivo_rejeicao: motivo,
          rejeitado_em: new Date().toISOString(),
          atualizado_em: new Date().toISOString()
        })
        .eq('id', orcamentoId);

      if (error) {
        throw new Error(`Erro ao rejeitar orçamento: ${error.message}`);
      }

      // Adicionar observação na OS
      const { data: orcamento } = await supabase
        .from('orcamentos')
        .select('ordem_servico_id')
        .eq('id', orcamentoId)
        .single();

      if (orcamento?.ordem_servico_id) {
        await supabase
          .from('observacoes_os')
          .insert({
            ordem_servico_id: orcamento.ordem_servico_id,
            tipo: 'sistema',
            descricao: `Orçamento rejeitado pelo cliente${motivo ? `: ${motivo}` : ''}`,
            criado_em: new Date().toISOString()
          });
      }
    } catch (error) {
      console.error('Erro na API - rejeitarOrcamento:', error);
      throw error;
    }
  }

  async enviarMensagem(osId: string, mensagem: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('mensagens_os')
        .insert({
          ordem_servico_id: osId,
          remetente_tipo: 'cliente',
          mensagem,
          criado_em: new Date().toISOString()
        });

      if (error) {
        throw new Error(`Erro ao enviar mensagem: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro na API - enviarMensagem:', error);
      throw error;
    }
  }

  async obterMensagens(osId: string): Promise<any[]> {
    try {
      const { data, error } = await supabase
        .from('mensagens_os')
        .select('*')
        .eq('ordem_servico_id', osId)
        .order('criado_em', { ascending: true });

      if (error) {
        throw new Error(`Erro ao buscar mensagens: ${error.message}`);
      }

      return data || [];
    } catch (error) {
      console.error('Erro na API - obterMensagens:', error);
      throw error;
    }
  }

  async atualizarPerfil(clienteId: string, dados: {
    nome?: string;
    email?: string;
    telefone?: string;
    endereco?: string;
  }): Promise<void> {
    try {
      const { error } = await supabase
        .from('clientes')
        .update({
          ...dados,
          atualizado_em: new Date().toISOString()
        })
        .eq('id', clienteId);

      if (error) {
        throw new Error(`Erro ao atualizar perfil: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro na API - atualizarPerfil:', error);
      throw error;
    }
  }
}

export const portalClienteAPI = new PortalClienteAPI();