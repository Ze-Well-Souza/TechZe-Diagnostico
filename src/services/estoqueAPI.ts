import { supabase } from '@/lib/supabase';

interface ItemEstoque {
  id: string;
  nome: string;
  descricao?: string;
  categoria: string;
  codigo: string;
  preco_custo: number;
  preco_venda: number;
  quantidade_atual: number;
  quantidade_minima: number;
  fornecedor?: string;
  localizacao?: string;
  status: 'disponivel' | 'baixo_estoque' | 'esgotado' | 'descontinuado';
  criadoEm: Date;
  atualizadoEm: Date;
}

interface FormularioItem {
  nome: string;
  descricao?: string;
  categoria: string;
  codigo: string;
  preco_custo: number;
  preco_venda: number;
  quantidade_atual: number;
  quantidade_minima: number;
  fornecedor?: string;
  localizacao?: string;
}

interface MovimentacaoEstoque {
  id: string;
  item_id: string;
  tipo: 'entrada' | 'saida';
  quantidade: number;
  quantidade_anterior: number;
  quantidade_nova: number;
  motivo: string;
  observacoes?: string;
  usuario_id: string;
  criadoEm: Date;
}

interface EstatisticasEstoque {
  totalItens: number;
  itensAtivos: number;
  valorTotal: number;
  itensBaixoEstoque: number;
  itensEsgotados: number;
  movimentacoesMes: number;
  valorMovimentacoesMes: number;
}

class EstoqueAPI {
  private determinarStatus(quantidadeAtual: number, quantidadeMinima: number): ItemEstoque['status'] {
    if (quantidadeAtual === 0) {
      return 'esgotado';
    } else if (quantidadeAtual <= quantidadeMinima) {
      return 'baixo_estoque';
    }
    return 'disponivel';
  }

  private mapearItemDB(item: any): ItemEstoque {
    return {
      id: item.id,
      nome: item.nome,
      descricao: item.descricao,
      categoria: item.categoria,
      codigo: item.codigo,
      preco_custo: item.preco_custo,
      preco_venda: item.preco_venda,
      quantidade_atual: item.quantidade_atual,
      quantidade_minima: item.quantidade_minima,
      fornecedor: item.fornecedor,
      localizacao: item.localizacao,
      status: item.status || this.determinarStatus(item.quantidade_atual, item.quantidade_minima),
      criadoEm: new Date(item.created_at),
      atualizadoEm: new Date(item.updated_at)
    };
  }

  private mapearMovimentacaoDB(movimentacao: any): MovimentacaoEstoque {
    return {
      id: movimentacao.id,
      item_id: movimentacao.item_id,
      tipo: movimentacao.tipo,
      quantidade: movimentacao.quantidade,
      quantidade_anterior: movimentacao.quantidade_anterior,
      quantidade_nova: movimentacao.quantidade_nova,
      motivo: movimentacao.motivo,
      observacoes: movimentacao.observacoes,
      usuario_id: movimentacao.usuario_id,
      criadoEm: new Date(movimentacao.created_at)
    };
  }

  async listarItens(): Promise<ItemEstoque[]> {
    try {
      const { data, error } = await supabase
        .from('estoque_itens')
        .select('*')
        .order('nome', { ascending: true });

      if (error) {
        throw new Error(`Erro ao listar itens: ${error.message}`);
      }

      return data?.map(item => this.mapearItemDB(item)) || [];
    } catch (error) {
      console.error('Erro ao listar itens:', error);
      throw error;
    }
  }

  async buscarPorCodigo(codigo: string): Promise<ItemEstoque | null> {
    try {
      const { data, error } = await supabase
        .from('estoque_itens')
        .select('*')
        .eq('codigo', codigo)
        .single();

      if (error) {
        if (error.code === 'PGRST116') {
          return null; // Item não encontrado
        }
        throw new Error(`Erro ao buscar item: ${error.message}`);
      }

      return this.mapearItemDB(data);
    } catch (error) {
      console.error('Erro ao buscar item por código:', error);
      throw error;
    }
  }

  async obterDetalhes(itemId: string): Promise<ItemEstoque> {
    try {
      const { data, error } = await supabase
        .from('estoque_itens')
        .select('*')
        .eq('id', itemId)
        .single();

      if (error) {
        throw new Error(`Erro ao obter detalhes: ${error.message}`);
      }

      return this.mapearItemDB(data);
    } catch (error) {
      console.error('Erro ao obter detalhes do item:', error);
      throw error;
    }
  }

  async criar(dados: FormularioItem): Promise<ItemEstoque> {
    try {
      const status = this.determinarStatus(dados.quantidade_atual, dados.quantidade_minima);
      
      const itemData = {
        nome: dados.nome,
        descricao: dados.descricao,
        categoria: dados.categoria,
        codigo: dados.codigo,
        preco_custo: dados.preco_custo,
        preco_venda: dados.preco_venda,
        quantidade_atual: dados.quantidade_atual,
        quantidade_minima: dados.quantidade_minima,
        fornecedor: dados.fornecedor,
        localizacao: dados.localizacao,
        status
      };

      const { data, error } = await supabase
        .from('estoque_itens')
        .insert(itemData)
        .select()
        .single();

      if (error) {
        throw new Error(`Erro ao criar item: ${error.message}`);
      }

      // Registrar movimentação inicial
      if (dados.quantidade_atual > 0) {
        await this.registrarMovimentacao(
          data.id,
          'entrada',
          dados.quantidade_atual,
          0,
          dados.quantidade_atual,
          'Estoque inicial'
        );
      }

      return this.mapearItemDB(data);
    } catch (error) {
      console.error('Erro ao criar item:', error);
      throw error;
    }
  }

  async atualizar(itemId: string, dados: Partial<FormularioItem>): Promise<void> {
    try {
      const updateData: any = { ...dados };
      
      // Se a quantidade foi alterada, recalcular o status
      if (dados.quantidade_atual !== undefined || dados.quantidade_minima !== undefined) {
        const itemAtual = await this.obterDetalhes(itemId);
        const novaQuantidadeAtual = dados.quantidade_atual ?? itemAtual.quantidade_atual;
        const novaQuantidadeMinima = dados.quantidade_minima ?? itemAtual.quantidade_minima;
        
        updateData.status = this.determinarStatus(novaQuantidadeAtual, novaQuantidadeMinima);
      }

      const { error } = await supabase
        .from('estoque_itens')
        .update(updateData)
        .eq('id', itemId);

      if (error) {
        throw new Error(`Erro ao atualizar item: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro ao atualizar item:', error);
      throw error;
    }
  }

  async excluir(itemId: string): Promise<void> {
    try {
      // Verificar se há movimentações associadas
      const { data: movimentacoes, error: movError } = await supabase
        .from('estoque_movimentacoes')
        .select('id')
        .eq('item_id', itemId)
        .limit(1);

      if (movError) {
        throw new Error(`Erro ao verificar movimentações: ${movError.message}`);
      }

      if (movimentacoes && movimentacoes.length > 0) {
        // Se há movimentações, apenas marcar como descontinuado
        await this.atualizar(itemId, { status: 'descontinuado' } as any);
        return;
      }

      // Se não há movimentações, pode excluir fisicamente
      const { error } = await supabase
        .from('estoque_itens')
        .delete()
        .eq('id', itemId);

      if (error) {
        throw new Error(`Erro ao excluir item: ${error.message}`);
      }
    } catch (error) {
      console.error('Erro ao excluir item:', error);
      throw error;
    }
  }

  async ajustarEstoque(
    itemId: string,
    tipo: 'entrada' | 'saida',
    quantidade: number,
    motivo: string,
    observacoes?: string
  ): Promise<MovimentacaoEstoque> {
    try {
      // Obter item atual
      const item = await this.obterDetalhes(itemId);
      
      // Calcular nova quantidade
      const quantidadeAnterior = item.quantidade_atual;
      const quantidadeNova = tipo === 'entrada' 
        ? quantidadeAnterior + quantidade
        : quantidadeAnterior - quantidade;

      // Validar se a saída não resulta em quantidade negativa
      if (quantidadeNova < 0) {
        throw new Error('Quantidade insuficiente em estoque');
      }

      // Determinar novo status
      const novoStatus = this.determinarStatus(quantidadeNova, item.quantidade_minima);

      // Atualizar item
      await supabase
        .from('estoque_itens')
        .update({
          quantidade_atual: quantidadeNova,
          status: novoStatus
        })
        .eq('id', itemId);

      // Registrar movimentação
      const movimentacao = await this.registrarMovimentacao(
        itemId,
        tipo,
        quantidade,
        quantidadeAnterior,
        quantidadeNova,
        motivo,
        observacoes
      );

      return movimentacao;
    } catch (error) {
      console.error('Erro ao ajustar estoque:', error);
      throw error;
    }
  }

  private async registrarMovimentacao(
    itemId: string,
    tipo: 'entrada' | 'saida',
    quantidade: number,
    quantidadeAnterior: number,
    quantidadeNova: number,
    motivo: string,
    observacoes?: string
  ): Promise<MovimentacaoEstoque> {
    try {
      // Obter usuário atual (implementar conforme sistema de auth)
      const { data: { user } } = await supabase.auth.getUser();
      
      const movimentacaoData = {
        item_id: itemId,
        tipo,
        quantidade,
        quantidade_anterior: quantidadeAnterior,
        quantidade_nova: quantidadeNova,
        motivo,
        observacoes,
        usuario_id: user?.id || 'sistema'
      };

      const { data, error } = await supabase
        .from('estoque_movimentacoes')
        .insert(movimentacaoData)
        .select()
        .single();

      if (error) {
        throw new Error(`Erro ao registrar movimentação: ${error.message}`);
      }

      return this.mapearMovimentacaoDB(data);
    } catch (error) {
      console.error('Erro ao registrar movimentação:', error);
      throw error;
    }
  }

  async listarMovimentacoes(itemId?: string): Promise<MovimentacaoEstoque[]> {
    try {
      let query = supabase
        .from('estoque_movimentacoes')
        .select(`
          *,
          estoque_itens(nome, codigo)
        `)
        .order('created_at', { ascending: false });

      if (itemId) {
        query = query.eq('item_id', itemId);
      }

      const { data, error } = await query;

      if (error) {
        throw new Error(`Erro ao listar movimentações: ${error.message}`);
      }

      return data?.map(mov => this.mapearMovimentacaoDB(mov)) || [];
    } catch (error) {
      console.error('Erro ao listar movimentações:', error);
      throw error;
    }
  }

  async listarBaixoEstoque(): Promise<ItemEstoque[]> {
    try {
      const { data, error } = await supabase
        .from('estoque_itens')
        .select('*')
        .or('status.eq.baixo_estoque,status.eq.esgotado')
        .order('quantidade_atual', { ascending: true });

      if (error) {
        throw new Error(`Erro ao listar itens com baixo estoque: ${error.message}`);
      }

      return data?.map(item => this.mapearItemDB(item)) || [];
    } catch (error) {
      console.error('Erro ao listar itens com baixo estoque:', error);
      throw error;
    }
  }

  async obterEstatisticas(): Promise<EstatisticasEstoque> {
    try {
      // Estatísticas dos itens
      const { data: itens, error: itensError } = await supabase
        .from('estoque_itens')
        .select('quantidade_atual, preco_custo, status');

      if (itensError) {
        throw new Error(`Erro ao obter estatísticas de itens: ${itensError.message}`);
      }

      // Movimentações do mês atual
      const inicioMes = new Date();
      inicioMes.setDate(1);
      inicioMes.setHours(0, 0, 0, 0);

      const { data: movimentacoes, error: movError } = await supabase
        .from('estoque_movimentacoes')
        .select(`
          quantidade,
          tipo,
          estoque_itens(preco_custo)
        `)
        .gte('created_at', inicioMes.toISOString());

      if (movError) {
        throw new Error(`Erro ao obter movimentações: ${movError.message}`);
      }

      // Calcular estatísticas
      const totalItens = itens?.length || 0;
      const itensAtivos = itens?.filter(item => item.status !== 'descontinuado').length || 0;
      const valorTotal = itens?.reduce((total, item) => 
        total + (item.quantidade_atual * item.preco_custo), 0
      ) || 0;
      const itensBaixoEstoque = itens?.filter(item => item.status === 'baixo_estoque').length || 0;
      const itensEsgotados = itens?.filter(item => item.status === 'esgotado').length || 0;
      const movimentacoesMes = movimentacoes?.length || 0;
      const valorMovimentacoesMes = movimentacoes?.reduce((total, mov) => {
        const valorUnitario = mov.estoque_itens?.preco_custo || 0;
        return total + (mov.quantidade * valorUnitario);
      }, 0) || 0;

      return {
        totalItens,
        itensAtivos,
        valorTotal,
        itensBaixoEstoque,
        itensEsgotados,
        movimentacoesMes,
        valorMovimentacoesMes
      };
    } catch (error) {
      console.error('Erro ao obter estatísticas:', error);
      throw error;
    }
  }

  async exportarItens(): Promise<Blob> {
    try {
      const itens = await this.listarItens();
      
      // Converter para CSV
      const headers = [
        'Código',
        'Nome',
        'Descrição',
        'Categoria',
        'Quantidade Atual',
        'Quantidade Mínima',
        'Preço Custo',
        'Preço Venda',
        'Fornecedor',
        'Localização',
        'Status'
      ];
      
      const csvContent = [
        headers.join(','),
        ...itens.map(item => [
          item.codigo,
          `"${item.nome}"`,
          `"${item.descricao || ''}"`,
          item.categoria,
          item.quantidade_atual,
          item.quantidade_minima,
          item.preco_custo,
          item.preco_venda,
          `"${item.fornecedor || ''}"`,
          `"${item.localizacao || ''}"`,
          item.status
        ].join(','))
      ].join('\n');
      
      return new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    } catch (error) {
      console.error('Erro ao exportar itens:', error);
      throw error;
    }
  }
}

export const estoqueAPI = new EstoqueAPI();