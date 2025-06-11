import { useState, useEffect, useCallback } from 'react';
import { 
  Orcamento, 
  FormularioOrcamento, 
  OrcamentoStatus 
} from '@/types/shared';
import { orcamentoAPI } from '@/services/orcamentoAPI';

interface UseOrcamentosOptions {
  autoLoad?: boolean;
  filtros?: {
    status?: OrcamentoStatus;
    clienteId?: string;
    dataInicio?: Date;
    dataFim?: Date;
  };
}

interface UseOrcamentosReturn {
  orcamentos: Orcamento[];
  loading: boolean;
  error: string | null;
  estatisticas: {
    total: number;
    pendentes: number;
    aprovados: number;
    rejeitados: number;
    valorTotal: number;
  } | null;
  // Funções
  carregarOrcamentos: () => Promise<void>;
  criarOrcamento: (dados: FormularioOrcamento) => Promise<Orcamento>;
  atualizarOrcamento: (id: string, dados: Partial<FormularioOrcamento>) => Promise<Orcamento>;
  atualizarStatus: (id: string, status: OrcamentoStatus) => Promise<void>;
  excluirOrcamento: (id: string) => Promise<void>;
  reenviarOrcamento: (id: string) => Promise<void>;
  carregarEstatisticas: () => Promise<void>;
}

export function useOrcamentos(options: UseOrcamentosOptions = {}): UseOrcamentosReturn {
  const { autoLoad = true, filtros } = options;
  
  const [orcamentos, setOrcamentos] = useState<Orcamento[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [estatisticas, setEstatisticas] = useState<{
    total: number;
    pendentes: number;
    aprovados: number;
    rejeitados: number;
    valorTotal: number;
  } | null>(null);

  const carregarOrcamentos = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const dados = await orcamentoAPI.listar(filtros);
      setOrcamentos(dados);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar orçamentos';
      setError(errorMessage);
      console.error('Erro ao carregar orçamentos:', err);
    } finally {
      setLoading(false);
    }
  }, [filtros]);

  const carregarEstatisticas = useCallback(async () => {
    try {
      const stats = await orcamentoAPI.obterEstatisticas();
      setEstatisticas(stats);
    } catch (err) {
      console.error('Erro ao carregar estatísticas:', err);
    }
  }, []);

  const criarOrcamento = useCallback(async (dados: FormularioOrcamento): Promise<Orcamento> => {
    try {
      setError(null);
      
      const novoOrcamento = await orcamentoAPI.criar(dados);
      
      // Atualizar lista local
      setOrcamentos(prev => [novoOrcamento, ...prev]);
      
      // Recarregar estatísticas
      await carregarEstatisticas();
      
      return novoOrcamento;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao criar orçamento';
      setError(errorMessage);
      throw err;
    }
  }, [carregarEstatisticas]);

  const atualizarOrcamento = useCallback(async (
    id: string, 
    dados: Partial<FormularioOrcamento>
  ): Promise<Orcamento> => {
    try {
      setError(null);
      
      const orcamentoAtualizado = await orcamentoAPI.atualizar(id, dados);
      
      // Atualizar lista local
      setOrcamentos(prev => 
        prev.map(orc => orc.id === id ? orcamentoAtualizado : orc)
      );
      
      // Recarregar estatísticas
      await carregarEstatisticas();
      
      return orcamentoAtualizado;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar orçamento';
      setError(errorMessage);
      throw err;
    }
  }, [carregarEstatisticas]);

  const atualizarStatus = useCallback(async (id: string, status: OrcamentoStatus): Promise<void> => {
    try {
      setError(null);
      
      await orcamentoAPI.atualizarStatus(id, status);
      
      // Atualizar lista local
      setOrcamentos(prev => 
        prev.map(orc => 
          orc.id === id 
            ? { ...orc, status, atualizadoEm: new Date() }
            : orc
        )
      );
      
      // Recarregar estatísticas
      await carregarEstatisticas();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar status';
      setError(errorMessage);
      throw err;
    }
  }, [carregarEstatisticas]);

  const excluirOrcamento = useCallback(async (id: string): Promise<void> => {
    try {
      setError(null);
      
      await orcamentoAPI.excluir(id);
      
      // Remover da lista local
      setOrcamentos(prev => prev.filter(orc => orc.id !== id));
      
      // Recarregar estatísticas
      await carregarEstatisticas();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao excluir orçamento';
      setError(errorMessage);
      throw err;
    }
  }, [carregarEstatisticas]);

  const reenviarOrcamento = useCallback(async (id: string): Promise<void> => {
    try {
      setError(null);
      
      await orcamentoAPI.reenviar(id);
      
      // Atualizar timestamp local (se necessário)
      setOrcamentos(prev => 
        prev.map(orc => 
          orc.id === id 
            ? { ...orc, atualizadoEm: new Date() }
            : orc
        )
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao reenviar orçamento';
      setError(errorMessage);
      throw err;
    }
  }, []);

  // Carregar dados iniciais
  useEffect(() => {
    if (autoLoad) {
      carregarOrcamentos();
      carregarEstatisticas();
    }
  }, [autoLoad, carregarOrcamentos, carregarEstatisticas]);

  return {
    orcamentos,
    loading,
    error,
    estatisticas,
    carregarOrcamentos,
    criarOrcamento,
    atualizarOrcamento,
    atualizarStatus,
    excluirOrcamento,
    reenviarOrcamento,
    carregarEstatisticas
  };
}

// Hook específico para um orçamento individual
export function useOrcamento(id: string | undefined) {
  const [orcamento, setOrcamento] = useState<Orcamento | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const carregarOrcamento = useCallback(async () => {
    if (!id) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const dados = await orcamentoAPI.buscarPorId(id);
      setOrcamento(dados);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar orçamento';
      setError(errorMessage);
      console.error('Erro ao carregar orçamento:', err);
    } finally {
      setLoading(false);
    }
  }, [id]);

  const atualizarStatus = useCallback(async (status: OrcamentoStatus): Promise<void> => {
    if (!id || !orcamento) return;
    
    try {
      setError(null);
      
      await orcamentoAPI.atualizarStatus(id, status);
      
      // Atualizar estado local
      setOrcamento(prev => 
        prev ? { ...prev, status, atualizadoEm: new Date() } : null
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao atualizar status';
      setError(errorMessage);
      throw err;
    }
  }, [id, orcamento]);

  const reenviar = useCallback(async (): Promise<void> => {
    if (!id) return;
    
    try {
      setError(null);
      
      await orcamentoAPI.reenviar(id);
      
      // Atualizar timestamp local
      setOrcamento(prev => 
        prev ? { ...prev, atualizadoEm: new Date() } : null
      );
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao reenviar orçamento';
      setError(errorMessage);
      throw err;
    }
  }, [id]);

  const gerarPDF = useCallback(async (): Promise<Blob | null> => {
    if (!id) return null;
    
    try {
      setError(null);
      
      const pdf = await orcamentoAPI.gerarPDF(id);
      return pdf;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao gerar PDF';
      setError(errorMessage);
      throw err;
    }
  }, [id]);

  useEffect(() => {
    carregarOrcamento();
  }, [carregarOrcamento]);

  return {
    orcamento,
    loading,
    error,
    carregarOrcamento,
    atualizarStatus,
    reenviar,
    gerarPDF
  };
}

export default useOrcamentos;