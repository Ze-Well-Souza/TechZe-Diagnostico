import { supabase } from '@/integrations/supabase/client';
import { 
  Orcamento, 
  FormularioOrcamento, 
  OrcamentoStatus,
  OrcamentoAPI,
  Cliente,
  Equipamento
} from '@/types/shared';

class OrcamentoService implements OrcamentoAPI {
  async listar(filtros?: {
    status?: OrcamentoStatus;
    clienteId?: string;
    dataInicio?: Date;
    dataFim?: Date;
  }): Promise<Orcamento[]> {
    try {
      let query = supabase
        .from('orcamentos')
        .select(`
          *,
          cliente:clientes(*),
          equipamento:equipamentos(*),
          itens:orcamento_itens(*)
        `);

      if (filtros?.status) {
        query = query.eq('status', filtros.status);
      }

      if (filtros?.clienteId) {
        query = query.eq('cliente_id', filtros.clienteId);
      }

      if (filtros?.dataInicio) {
        query = query.gte('criado_em', filtros.dataInicio.toISOString());
      }

      if (filtros?.dataFim) {
        query = query.lte('criado_em', filtros.dataFim.toISOString());
      }

      const { data, error } = await query.order('criado_em', { ascending: false });

      if (error) {
        throw new Error(`Erro ao listar orçamentos: ${error.message}`);
      }

      return this.transformarDados(data || []);
    } catch (error) {
      console.error('Erro no serviço de orçamentos:', error);
      throw error;
    }
  }

  async buscarPorId(id: string): Promise<Orcamento | null> {
    try {
      const { data, error } = await supabase
        .from('orcamentos')
        .select(`
          *,
          cliente:clientes(*),
          equipamento:equipamentos(*),
          itens:orcamento_itens(*)
        `)
        .eq('id', id)
        .single();

      if (error) {
        if (error.code === 'PGRST116') {
          return null; // Não encontrado
        }
        throw new Error(`Erro ao buscar orçamento: ${error.message}`);
      }

      return this.transformarDado(data);
    } catch (error) {
      console.error('Erro ao buscar orçamento:', error);
      throw error;
    }
  }

  async criar(dados: FormularioOrcamento): Promise<Orcamento> {
    try {
      // Gerar número do orçamento
      const numero = await this.gerarNumeroOrcamento();

      // Calcular valores
      const valorPecas = dados.itens
        .filter(item => item.tipo === 'peca')
        .reduce((sum, item) => sum + (item.quantidade * item.valorUnitario), 0);
      
      const valorServicos = dados.itens
        .filter(item => item.tipo === 'servico')
        .reduce((sum, item) => sum + (item.quantidade * item.valorUnitario), 0);
      
      const valorTotal = valorPecas + valorServicos - dados.valorDesconto;

      // Criar orçamento
      const { data: orcamento, error: orcamentoError } = await supabase
        .from('orcamentos')
        .insert({
          numero,
          cliente_id: dados.clienteId,
          equipamento_id: dados.equipamentoId,
          status: 'pendente',
          valor_pecas: valorPecas,
          valor_servicos: valorServicos,
          valor_desconto: dados.valorDesconto,
          valor_total: valorTotal,
          observacoes: dados.observacoes,
          validade_ate: dados.validadeAte
        })
        .select()
        .single();

      if (orcamentoError) {
        throw new Error(`Erro ao criar orçamento: ${orcamentoError.message}`);
      }

      // Criar itens do orçamento
      const itensParaInserir = dados.itens.map(item => ({
        orcamento_id: orcamento.id,
        tipo: item.tipo,
        peca_id: item.pecaId,
        descricao: item.descricao,
        quantidade: item.quantidade,
        valor_unitario: item.valorUnitario
      }));

      const { error: itensError } = await supabase
        .from('orcamento_itens')
        .insert(itensParaInserir);

      if (itensError) {
        // Reverter criação do orçamento em caso de erro
        await supabase.from('orcamentos').delete().eq('id', orcamento.id);
        throw new Error(`Erro ao criar itens do orçamento: ${itensError.message}`);
      }

      // Buscar orçamento completo criado
      const orcamentoCompleto = await this.buscarPorId(orcamento.id);
      if (!orcamentoCompleto) {
        throw new Error('Erro ao recuperar orçamento criado');
      }

      return orcamentoCompleto;
    } catch (error) {
      console.error('Erro ao criar orçamento:', error);
      throw error;
    }
  }

  async atualizar(id: string, dados: Partial<FormularioOrcamento>): Promise<Orcamento> {
    try {
      const dadosAtualizacao: any = {
        atualizado_em: new Date().toISOString()
      };

      if (dados.clienteId) dadosAtualizacao.cliente_id = dados.clienteId;
      if (dados.equipamentoId) dadosAtualizacao.equipamento_id = dados.equipamentoId;
      if (dados.valorDesconto !== undefined) dadosAtualizacao.valor_desconto = dados.valorDesconto;
      if (dados.observacoes !== undefined) dadosAtualizacao.observacoes = dados.observacoes;
      if (dados.validadeAte) dadosAtualizacao.validade_ate = dados.validadeAte;

      // Se há itens para atualizar, recalcular valores
      if (dados.itens) {
        const valorPecas = dados.itens
          .filter(item => item.tipo === 'peca')
          .reduce((sum, item) => sum + (item.quantidade * item.valorUnitario), 0);
        
        const valorServicos = dados.itens
          .filter(item => item.tipo === 'servico')
          .reduce((sum, item) => sum + (item.quantidade * item.valorUnitario), 0);
        
        const valorTotal = valorPecas + valorServicos - (dados.valorDesconto || 0);

        dadosAtualizacao.valor_pecas = valorPecas;
        dadosAtualizacao.valor_servicos = valorServicos;
        dadosAtualizacao.valor_total = valorTotal;

        // Atualizar itens
        await supabase.from('orcamento_itens').delete().eq('orcamento_id', id);
        
        const itensParaInserir = dados.itens.map(item => ({
          orcamento_id: id,
          tipo: item.tipo,
          peca_id: item.pecaId,
          descricao: item.descricao,
          quantidade: item.quantidade,
          valor_unitario: item.valorUnitario
        }));

        const { error: itensError } = await supabase
          .from('orcamento_itens')
          .insert(itensParaInserir);

        if (itensError) {
          throw new Error(`Erro ao atualizar itens: ${itensError.message}`);
        }
      }

      const { error } = await supabase
        .from('orcamentos')
        .update(dadosAtualizacao)
        .eq('id', id);

      if (error) {
        throw new Error(`Erro ao atualizar orçamento: ${error.message}`);
      }

      const orcamentoAtualizado = await this.buscarPorId(id);
      if (!orcamentoAtualizado) {
        throw new Error('Erro ao recuperar orçamento atualizado');
      }

      return orcamentoAtualizado;
    } catch (error) {
      console.error('Erro ao atualizar orçamento:', error);
      throw error;
    }
  }

  async atualizarStatus(id: string, status: OrcamentoStatus): Promise<void> {
    try {
      const { error } = await supabase
        .from('orcamentos')
        .update({ 
          status, 
          atualizado_em: new Date().toISOString() 
        })
        .eq('id', id);

      if (error) {
        throw new Error(`Erro ao atualizar status: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro ao atualizar status:', error);
      throw error;
    }
  }

  async excluir(id: string): Promise<void> {
    try {
      // Excluir itens primeiro (devido à foreign key)
      await supabase.from('orcamento_itens').delete().eq('orcamento_id', id);
      
      // Excluir orçamento
      const { error } = await supabase
        .from('orcamentos')
        .delete()
        .eq('id', id);

      if (error) {
        throw new Error(`Erro ao excluir orçamento: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro ao excluir orçamento:', error);
      throw error;
    }
  }

  async reenviar(id: string): Promise<void> {
    try {
      // TODO: Implementar lógica de reenvio (email, WhatsApp, etc.)
      console.log(`Reenviando orçamento ${id}`);
      
      // Atualizar timestamp de último envio
      const { error } = await supabase
        .from('orcamentos')
        .update({ 
          ultimo_envio: new Date().toISOString(),
          atualizado_em: new Date().toISOString() 
        })
        .eq('id', id);

      if (error) {
        throw new Error(`Erro ao registrar reenvio: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro ao reenviar orçamento:', error);
      throw error;
    }
  }

  async gerarPDF(id: string): Promise<Blob> {
    try {
      // TODO: Implementar geração de PDF
      // Por enquanto, retorna um blob vazio
      return new Blob(['PDF do orçamento'], { type: 'application/pdf' });
    } catch (error) {
      console.error('Erro ao gerar PDF:', error);
      throw error;
    }
  }

  async obterEstatisticas(): Promise<{
    total: number;
    pendentes: number;
    aprovados: number;
    rejeitados: number;
    valorTotal: number;
  }> {
    try {
      const { data, error } = await supabase
        .from('orcamentos')
        .select('status, valor_total');

      if (error) {
        throw new Error(`Erro ao obter estatísticas: ${error.message}`);
      }

      const stats = {
        total: data.length,
        pendentes: data.filter(o => o.status === 'pendente').length,
        aprovados: data.filter(o => o.status === 'aprovado').length,
        rejeitados: data.filter(o => o.status === 'rejeitado').length,
        valorTotal: data.reduce((sum, o) => sum + (o.valor_total || 0), 0)
      };

      return stats;
    } catch (error) {
      console.error('Erro ao obter estatísticas:', error);
      throw error;
    }
  }

  private async gerarNumeroOrcamento(): Promise<string> {
    const ano = new Date().getFullYear();
    const { count } = await supabase
      .from('orcamentos')
      .select('*', { count: 'exact', head: true })
      .gte('criado_em', `${ano}-01-01`)
      .lt('criado_em', `${ano + 1}-01-01`);

    const proximoNumero = (count || 0) + 1;
    return `ORC-${ano}-${proximoNumero.toString().padStart(3, '0')}`;
  }

  private transformarDados(dados: any[]): Orcamento[] {
    return dados.map(item => this.transformarDado(item));
  }

  private transformarDado(item: any): Orcamento {
    return {
      id: item.id,
      numero: item.numero,
      clienteId: item.cliente_id,
      equipamentoId: item.equipamento_id,
      status: item.status,
      itens: item.itens?.map((itemOrcamento: any) => ({
        tipo: itemOrcamento.tipo,
        pecaId: itemOrcamento.peca_id,
        descricao: itemOrcamento.descricao,
        quantidade: itemOrcamento.quantidade,
        valorUnitario: itemOrcamento.valor_unitario
      })) || [],
      valorPecas: item.valor_pecas,
      valorServicos: item.valor_servicos,
      valorDesconto: item.valor_desconto,
      valorTotal: item.valor_total,
      observacoes: item.observacoes,
      validadeAte: new Date(item.validade_ate),
      criadoEm: new Date(item.criado_em),
      atualizadoEm: new Date(item.atualizado_em),
      cliente: item.cliente ? {
        id: item.cliente.id,
        nome: item.cliente.nome,
        email: item.cliente.email,
        telefone: item.cliente.telefone,
        cpf: item.cliente.cpf,
        criadoEm: new Date(item.cliente.criado_em),
        atualizadoEm: new Date(item.cliente.atualizado_em)
      } : undefined,
      equipamento: item.equipamento ? {
        id: item.equipamento.id,
        clienteId: item.equipamento.cliente_id,
        tipo: item.equipamento.tipo,
        marca: item.equipamento.marca,
        modelo: item.equipamento.modelo,
        numeroSerie: item.equipamento.numero_serie,
        descricaoProblema: item.equipamento.descricao_problema,
        criadoEm: new Date(item.equipamento.criado_em),
        atualizadoEm: new Date(item.equipamento.atualizado_em)
      } : undefined
    };
  }
}

export const orcamentoAPI = new OrcamentoService();
export default orcamentoAPI;