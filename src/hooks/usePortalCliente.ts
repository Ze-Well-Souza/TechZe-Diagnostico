import { useState, useCallback } from 'react';
import { OrdemServico, Orcamento } from '@/types/shared';
import { portalClienteAPI } from '@/services/portalClienteAPI';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from '@/hooks/use-toast';

interface UsePortalClienteOptions {
  autoLoad?: boolean;
}

interface UsePortalClienteReturn {
  ordensServico: OrdemServico[];
  historico: OrdemServico[];
  loading: boolean;
  error: string | null;
  // Funções
  carregarDados: () => Promise<void>;
  avaliarServico: (osId: string, avaliacao: {
    nota: number;
    comentario?: string;
  }) => Promise<void>;
  baixarOrcamento: (orcamentoId: string) => Promise<void>;
  aprovarOrcamento: (orcamentoId: string) => Promise<void>;
  rejeitarOrcamento: (orcamentoId: string, motivo?: string) => Promise<void>;
  acompanharOS: (osId: string) => Promise<OrdemServico>;
}

export function usePortalCliente(options: UsePortalClienteOptions = {}): UsePortalClienteReturn {
  const { autoLoad = true } = options;
  const { user } = useAuth();
  
  const [ordensServico, setOrdensServico] = useState<OrdemServico[]>([]);
  const [historico, setHistorico] = useState<OrdemServico[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const carregarDados = useCallback(async () => {
    if (!user?.id) {
      setError('Usuário não autenticado');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const [ordensAtivas, ordensHistorico] = await Promise.all([
        portalClienteAPI.obterOrdensAtivas(user.id),
        portalClienteAPI.obterHistorico(user.id)
      ]);
      
      setOrdensServico(ordensAtivas);
      setHistorico(ordensHistorico);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar dados';
      setError(errorMessage);
      console.error('Erro ao carregar dados do portal:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  }, [user?.id]);

  const avaliarServico = useCallback(async (
    osId: string, 
    avaliacao: { nota: number; comentario?: string }
  ) => {
    try {
      await portalClienteAPI.avaliarServico(osId, avaliacao);
      
      // Atualizar a OS no estado local
      setHistorico(prev => 
        prev.map(os => 
          os.id === osId 
            ? { ...os, avaliacao: { ...avaliacao, criadaEm: new Date() } }
            : os
        )
      );
      
      toast({
        title: 'Sucesso',
        description: 'Avaliação enviada com sucesso!'
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao enviar avaliação';
      console.error('Erro ao avaliar serviço:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
    }
  }, []);

  const baixarOrcamento = useCallback(async (orcamentoId: string) => {
    try {
      const blob = await portalClienteAPI.baixarOrcamento(orcamentoId);
      
      // Criar URL temporária e fazer download
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `orcamento-${orcamentoId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast({
        title: 'Sucesso',
        description: 'Orçamento baixado com sucesso!'
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao baixar orçamento';
      console.error('Erro ao baixar orçamento:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
    }
  }, []);

  const aprovarOrcamento = useCallback(async (orcamentoId: string) => {
    try {
      await portalClienteAPI.aprovarOrcamento(orcamentoId);
      
      // Atualizar o status do orçamento no estado local
      setOrdensServico(prev => 
        prev.map(os => 
          os.orcamento?.id === orcamentoId 
            ? { 
                ...os, 
                orcamento: { ...os.orcamento, status: 'aprovado' as const },
                status: 'em_reparo'
              }
            : os
        )
      );
      
      toast({
        title: 'Sucesso',
        description: 'Orçamento aprovado! O reparo será iniciado em breve.'
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao aprovar orçamento';
      console.error('Erro ao aprovar orçamento:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
    }
  }, []);

  const rejeitarOrcamento = useCallback(async (orcamentoId: string, motivo?: string) => {
    try {
      await portalClienteAPI.rejeitarOrcamento(orcamentoId, motivo);
      
      // Atualizar o status do orçamento no estado local
      setOrdensServico(prev => 
        prev.map(os => 
          os.orcamento?.id === orcamentoId 
            ? { 
                ...os, 
                orcamento: { ...os.orcamento, status: 'rejeitado' as const }
              }
            : os
        )
      );
      
      toast({
        title: 'Orçamento rejeitado',
        description: 'O orçamento foi rejeitado. Entraremos em contato para discutir alternativas.'
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao rejeitar orçamento';
      console.error('Erro ao rejeitar orçamento:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
    }
  }, []);

  const acompanharOS = useCallback(async (osId: string): Promise<OrdemServico> => {
    try {
      const os = await portalClienteAPI.obterDetalhesOS(osId);
      
      // Atualizar a OS no estado local se ela existir
      setOrdensServico(prev => 
        prev.map(item => item.id === osId ? os : item)
      );
      
      return os;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar detalhes da OS';
      console.error('Erro ao acompanhar OS:', err);
      
      toast({
        title: 'Erro',
        description: errorMessage,
        variant: 'destructive'
      });
      
      throw err;
    }
  }, []);

  return {
    ordensServico,
    historico,
    loading,
    error,
    carregarDados,
    avaliarServico,
    baixarOrcamento,
    aprovarOrcamento,
    rejeitarOrcamento,
    acompanharOS
  };
}