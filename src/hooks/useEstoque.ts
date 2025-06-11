import { useState, useCallback } from 'react';
import { estoqueAPI } from '@/services/estoqueAPI';
import { toast } from '@/hooks/use-toast';

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

interface UseEstoqueOptions {
  autoLoad?: boolean;
}

interface UseEstoqueReturn {
  itens: ItemEstoque[];
  movimentacoes: MovimentacaoEstoque[];
  estatisticas: EstatisticasEstoque | null;
  loading: boolean;
  error: string | null;
  // Funções
  carregarItens: () => Promise<void>;
  carregarMovimentacoes: (itemId?: string) => Promise<void>;
  carregarEstatisticas: () => Promise<void>;
  criarItem: (dados: FormularioItem) => Promise<ItemEstoque>;
  atualizarItem: (itemId: string, dados: Partial<FormularioItem>) => Promise<void>;
  excluirItem: (itemId: string) => Promise<void>;
  ajustarEstoque: (
    itemId: string,
    tipo: 'entrada' | 'saida',
    quantidade: number,
    motivo: string,
    observacoes?: string
  ) => Promise<void>;
  buscarItem: (codigo: string) => Promise<ItemEstoque | null>;
  verificarBaixoEstoque: () => Promise<ItemEstoque[]>;
}

export function useEstoque(options: UseEstoqueOptions = {}): UseEstoqueReturn {
  const { autoLoad = true } = options;
  
  const [itens, setItens] = useState<ItemEstoque[]>([]);
  const [movimentacoes, setMovimentacoes] = useState<MovimentacaoEstoque[]>([]);
  const [estatisticas, setEstatisticas] = useState<EstatisticasEstoque | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const carregarItens = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const dados = await estoqueAPI.listarItens();
      setItens(dados);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar itens';
      setError(errorMessage);
      console.error('Erro ao carregar itens:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const carregarMovimentacoes = useCallback(async (itemId?: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const dados = await estoqueAPI.listarMovimentacoes(itemId);
      setMovimentacoes(dados);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar movimentações';
      setError(errorMessage);
      console.error('Erro ao carregar movimentações:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const carregarEstatisticas = useCallback(async () => {
    try {
      const dados = await estoqueAPI.obterEstatisticas();
      setEstatisticas(dados);
    } catch (err) {
      console.error('Erro ao carregar estatísticas:', err);
      // Não exibir toast para estatísticas, pois não é crítico
    }
  }, []);

  const criarItem = useCallback(async (dados: FormularioItem): Promise<ItemEstoque> => {
    try {
      setError(null);
      
      // Verificar se o código já existe
      const itemExistente = await estoqueAPI.buscarPorCodigo(dados.codigo);
      if (itemExistente) {
        throw new Error('Já existe um item com este código');
      }
      
      const novoItem = await estoqueAPI.criar(dados);
      
      // Atualizar lista local
      setItens(prev => [novoItem, ...prev]);
      
      // Recarregar estatísticas
      await carregarEstatisticas();
      
      return novoItem;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar item';
      setError(errorMessage);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
      
      throw err;
    }
  }, [carregarEstatisticas]);

  const atualizarItem = useCallback(async (
    itemId: string,
    dados: Partial<FormularioItem>
  ) => {
    try {
      setError(null);
      
      await estoqueAPI.atualizar(itemId, dados);
      
      // Atualizar item no estado local
      setItens(prev => 
        prev.map(item => 
          item.id === itemId 
            ? { ...item, ...dados, atualizadoEm: new Date() }
            : item
        )
      );
      
      // Recarregar estatísticas
      await carregarEstatisticas();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar item';
      setError(errorMessage);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
      
      throw err;
    }
  }, [carregarEstatisticas]);

  const excluirItem = useCallback(async (itemId: string) => {
    try {
      setError(null);
      
      await estoqueAPI.excluir(itemId);
      
      // Remover item do estado local
      setItens(prev => prev.filter(item => item.id !== itemId));
      
      // Recarregar estatísticas
      await carregarEstatisticas();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao excluir item';
      setError(errorMessage);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
      
      throw err;
    }
  }, [carregarEstatisticas]);

  const ajustarEstoque = useCallback(async (
    itemId: string,
    tipo: 'entrada' | 'saida',
    quantidade: number,
    motivo: string,
    observacoes?: string
  ) => {
    try {
      setError(null);
      
      const movimentacao = await estoqueAPI.ajustarEstoque(
        itemId,
        tipo,
        quantidade,
        motivo,
        observacoes
      );
      
      // Atualizar quantidade do item no estado local
      setItens(prev => 
        prev.map(item => {
          if (item.id === itemId) {
            const novaQuantidade = tipo === 'entrada' 
              ? item.quantidade_atual + quantidade
              : item.quantidade_atual - quantidade;
            
            // Determinar novo status baseado na quantidade
            let novoStatus: ItemEstoque['status'] = 'disponivel';
            if (novaQuantidade === 0) {
              novoStatus = 'esgotado';
            } else if (novaQuantidade <= item.quantidade_minima) {
              novoStatus = 'baixo_estoque';
            }
            
            return {
              ...item,
              quantidade_atual: novaQuantidade,
              status: novoStatus,
              atualizadoEm: new Date()
            };
          }
          return item;
        })
      );
      
      // Adicionar movimentação ao estado local
      setMovimentacoes(prev => [movimentacao, ...prev]);
      
      // Recarregar estatísticas
      await carregarEstatisticas();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao ajustar estoque';
      setError(errorMessage);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
      
      throw err;
    }
  }, [carregarEstatisticas]);

  const buscarItem = useCallback(async (codigo: string): Promise<ItemEstoque | null> => {
    try {
      return await estoqueAPI.buscarPorCodigo(codigo);
    } catch (err) {
      console.error('Erro ao buscar item:', err);
      return null;
    }
  }, []);

  const verificarBaixoEstoque = useCallback(async (): Promise<ItemEstoque[]> => {
    try {
      return await estoqueAPI.listarBaixoEstoque();
    } catch (err) {
      console.error('Erro ao verificar baixo estoque:', err);
      return [];
    }
  }, []);

  return {
    itens,
    movimentacoes,
    estatisticas,
    loading,
    error,
    carregarItens,
    carregarMovimentacoes,
    carregarEstatisticas,
    criarItem,
    atualizarItem,
    excluirItem,
    ajustarEstoque,
    buscarItem,
    verificarBaixoEstoque
  };
}