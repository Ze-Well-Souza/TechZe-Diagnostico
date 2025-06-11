import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  ArrowLeft, 
  Plus, 
  Trash2, 
  Search, 
  Calculator,
  Save,
  Send,
  AlertCircle
} from 'lucide-react';
import { Cliente, Equipamento, Peca, FormularioOrcamento, TipoPeca } from '@/types/shared';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useOrcamentos } from '@/hooks/useOrcamentos';

interface NovoOrcamentoProps {}

interface ItemOrcamento {
  id: string;
  tipo: 'peca' | 'servico';
  pecaId?: string;
  descricao: string;
  quantidade: number;
  valorUnitario: number;
  valorTotal: number;
}

export default function NovoOrcamento() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { criarOrcamento } = useOrcamentos();
  const [loading, setLoading] = useState(false);
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [equipamentos, setEquipamentos] = useState<Equipamento[]>([]);
  const [pecas, setPecas] = useState<Peca[]>([]);
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const [formulario, setFormulario] = useState<FormularioOrcamento>({
    clienteId: '',
    equipamentoId: '',
    itens: [],
    valorDesconto: 0,
    observacoes: '',
    validadeAte: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
  });
  
  const [itens, setItens] = useState<ItemOrcamento[]>([]);
  const [novoItem, setNovoItem] = useState<Partial<ItemOrcamento>>({
    tipo: 'peca',
    descricao: '',
    quantidade: 1,
    valorUnitario: 0
  });
  
  const [showPecaSearch, setShowPecaSearch] = useState(false);
  const [pecaSearchTerm, setPecaSearchTerm] = useState('');

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    if (formulario.clienteId) {
      loadEquipamentos(formulario.clienteId);
    }
  }, [formulario.clienteId]);

  const loadInitialData = async () => {
    try {
      // TODO: Implementar chamadas reais para as APIs
      // const [clientesData, pecasData] = await Promise.all([
      //   clienteAPI.listar(),
      //   pecaAPI.listar()
      // ]);
      
      // Mock data para desenvolvimento
      const mockClientes: Cliente[] = [
        {
          id: 'cliente-1',
          nome: 'João Silva',
          email: 'joao@email.com',
          telefone: '(11) 99999-9999',
          cpf: '123.456.789-00',
          criadoEm: new Date(),
          atualizadoEm: new Date()
        },
        {
          id: 'cliente-2',
          nome: 'Maria Santos',
          email: 'maria@email.com',
          telefone: '(11) 88888-8888',
          cpf: '987.654.321-00',
          criadoEm: new Date(),
          atualizadoEm: new Date()
        }
      ];
      
      const mockPecas: Peca[] = [
        {
          id: 'peca-1',
          nome: 'Memória RAM 8GB DDR4',
          tipo: 'memoria',
          marca: 'Kingston',
          modelo: 'ValueRAM',
          descricao: 'Memória RAM 8GB DDR4 2400MHz',
          preco: 250.00,
          quantidadeEstoque: 15,
          estoqueMinimo: 5,
          ativa: true,
          criadaEm: new Date(),
          atualizadaEm: new Date()
        },
        {
          id: 'peca-2',
          nome: 'SSD 500GB',
          tipo: 'ssd',
          marca: 'Samsung',
          modelo: '980 EVO',
          descricao: 'SSD NVMe 500GB Samsung 980 EVO',
          preco: 350.00,
          quantidadeEstoque: 8,
          estoqueMinimo: 3,
          ativa: true,
          criadaEm: new Date(),
          atualizadaEm: new Date()
        },
        {
          id: 'peca-3',
          nome: 'Fonte 500W',
          tipo: 'fonte',
          marca: 'Corsair',
          modelo: 'CV500',
          descricao: 'Fonte 500W 80+ Bronze',
          preco: 280.00,
          quantidadeEstoque: 12,
          estoqueMinimo: 4,
          ativa: true,
          criadaEm: new Date(),
          atualizadaEm: new Date()
        }
      ];
      
      setClientes(mockClientes);
      setPecas(mockPecas);
    } catch (error) {
      console.error('Erro ao carregar dados iniciais:', error);
    }
  };

  const loadEquipamentos = async (clienteId: string) => {
    try {
      // TODO: Implementar chamada real para API
      // const equipamentosData = await equipamentoAPI.listarPorCliente(clienteId);
      
      // Mock data
      const mockEquipamentos: Equipamento[] = [
        {
          id: 'equip-1',
          clienteId: clienteId,
          tipo: 'notebook',
          marca: 'Dell',
          modelo: 'Inspiron 15',
          numeroSerie: 'DL123456',
          descricaoProblema: 'Lentidão e travamentos',
          criadoEm: new Date(),
          atualizadoEm: new Date()
        },
        {
          id: 'equip-2',
          clienteId: clienteId,
          tipo: 'desktop',
          marca: 'HP',
          modelo: 'Pavilion',
          numeroSerie: 'HP789012',
          descricaoProblema: 'Não liga',
          criadoEm: new Date(),
          atualizadoEm: new Date()
        }
      ];
      
      setEquipamentos(mockEquipamentos);
    } catch (error) {
      console.error('Erro ao carregar equipamentos:', error);
    }
  };

  const adicionarItem = () => {
    if (!novoItem.descricao || !novoItem.quantidade || !novoItem.valorUnitario) {
      setErrors({ ...errors, novoItem: 'Preencha todos os campos do item' });
      return;
    }

    const item: ItemOrcamento = {
      id: Date.now().toString(),
      tipo: novoItem.tipo || 'peca',
      pecaId: novoItem.pecaId,
      descricao: novoItem.descricao || '',
      quantidade: novoItem.quantidade || 1,
      valorUnitario: novoItem.valorUnitario || 0,
      valorTotal: (novoItem.quantidade || 1) * (novoItem.valorUnitario || 0)
    };

    setItens([...itens, item]);
    setNovoItem({
      tipo: 'peca',
      descricao: '',
      quantidade: 1,
      valorUnitario: 0
    });
    setShowPecaSearch(false);
    setPecaSearchTerm('');
    
    // Limpar erro
    const newErrors = { ...errors };
    delete newErrors.novoItem;
    setErrors(newErrors);
  };

  const removerItem = (itemId: string) => {
    setItens(itens.filter(item => item.id !== itemId));
  };

  const selecionarPeca = (peca: Peca) => {
    setNovoItem({
      ...novoItem,
      pecaId: peca.id,
      descricao: peca.nome,
      valorUnitario: peca.preco
    });
    setShowPecaSearch(false);
    setPecaSearchTerm('');
  };

  const calcularTotais = () => {
    const valorPecas = itens
      .filter(item => item.tipo === 'peca')
      .reduce((sum, item) => sum + item.valorTotal, 0);
    
    const valorServicos = itens
      .filter(item => item.tipo === 'servico')
      .reduce((sum, item) => sum + item.valorTotal, 0);
    
    const subtotal = valorPecas + valorServicos;
    const valorTotal = subtotal - formulario.valorDesconto;
    
    return { valorPecas, valorServicos, subtotal, valorTotal };
  };

  const validarFormulario = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formulario.clienteId) {
      newErrors.clienteId = 'Selecione um cliente';
    }
    
    if (!formulario.equipamentoId) {
      newErrors.equipamentoId = 'Selecione um equipamento';
    }
    
    if (itens.length === 0) {
      newErrors.itens = 'Adicione pelo menos um item ao orçamento';
    }
    
    if (!formulario.validadeAte) {
      newErrors.validadeAte = 'Defina a data de validade';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const salvarOrcamento = async (enviar = false) => {
    if (!validarFormulario()) {
      return;
    }

    try {
      setLoading(true);
      
      const { valorPecas, valorServicos, valorTotal } = calcularTotais();
      
      const dadosOrcamento = {
        clienteId: formulario.clienteId,
        equipamentoId: formulario.equipamentoId,
        itens: itens.map(item => ({
          tipo: item.tipo,
          pecaId: item.pecaId,
          descricao: item.descricao,
          quantidade: item.quantidade,
          valorUnitario: item.valorUnitario
        })),
        observacoes: formulario.observacoes,
        valorDesconto: formulario.valorDesconto,
        validadeAte: new Date(formulario.validadeAte),
        valorPecas,
        valorServicos,
        valorTotal
      };
      
      await criarOrcamento(dadosOrcamento);
      
      if (enviar) {
        // TODO: Implementar envio do orçamento
        console.log('Enviando orçamento para o cliente...');
      }
      
      navigate('/orcamentos');
    } catch (error) {
      console.error('Erro ao salvar orçamento:', error);
      setErrors({ ...errors, submit: 'Erro ao salvar orçamento. Tente novamente.' });
    } finally {
      setLoading(false);
    }
  };

  const pecasFiltradas = pecas.filter(peca => 
    peca.ativa && 
    (peca.nome.toLowerCase().includes(pecaSearchTerm.toLowerCase()) ||
     peca.marca?.toLowerCase().includes(pecaSearchTerm.toLowerCase()) ||
     peca.modelo?.toLowerCase().includes(pecaSearchTerm.toLowerCase()))
  );

  const { valorPecas, valorServicos, subtotal, valorTotal } = calcularTotais();

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-8">
        <Button variant="outline" onClick={() => navigate('/orcamentos')}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Voltar
        </Button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Novo Orçamento</h1>
          <p className="text-gray-600">Crie um novo orçamento para seu cliente</p>
        </div>
      </div>

      {errors.submit && (
        <Alert className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{errors.submit}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Formulário Principal */}
        <div className="lg:col-span-2 space-y-6">
          {/* Dados do Cliente e Equipamento */}
          <Card>
            <CardHeader>
              <CardTitle>Cliente e Equipamento</CardTitle>
              <CardDescription>Selecione o cliente e equipamento para este orçamento</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="cliente">Cliente *</Label>
                  <select
                    id="cliente"
                    value={formulario.clienteId}
                    onChange={(e) => setFormulario({ ...formulario, clienteId: e.target.value, equipamentoId: '' })}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      errors.clienteId ? 'border-red-500' : 'border-gray-300'
                    }`}
                  >
                    <option value="">Selecione um cliente</option>
                    {clientes.map(cliente => (
                      <option key={cliente.id} value={cliente.id}>
                        {cliente.nome} - {cliente.telefone}
                      </option>
                    ))}
                  </select>
                  {errors.clienteId && (
                    <p className="text-red-500 text-sm mt-1">{errors.clienteId}</p>
                  )}
                </div>
                
                <div>
                  <Label htmlFor="equipamento">Equipamento *</Label>
                  <select
                    id="equipamento"
                    value={formulario.equipamentoId}
                    onChange={(e) => setFormulario({ ...formulario, equipamentoId: e.target.value })}
                    disabled={!formulario.clienteId}
                    className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                      errors.equipamentoId ? 'border-red-500' : 'border-gray-300'
                    } ${!formulario.clienteId ? 'bg-gray-100' : ''}`}
                  >
                    <option value="">Selecione um equipamento</option>
                    {equipamentos.map(equipamento => (
                      <option key={equipamento.id} value={equipamento.id}>
                        {equipamento.marca} {equipamento.modelo} - {equipamento.tipo}
                      </option>
                    ))}
                  </select>
                  {errors.equipamentoId && (
                    <p className="text-red-500 text-sm mt-1">{errors.equipamentoId}</p>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Itens do Orçamento */}
          <Card>
            <CardHeader>
              <CardTitle>Itens do Orçamento</CardTitle>
              <CardDescription>Adicione peças e serviços ao orçamento</CardDescription>
            </CardHeader>
            <CardContent>
              {/* Adicionar Novo Item */}
              <div className="border rounded-lg p-4 mb-4 bg-gray-50">
                <h4 className="font-medium mb-3">Adicionar Item</h4>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                  <div>
                    <Label htmlFor="tipo">Tipo</Label>
                    <select
                      id="tipo"
                      value={novoItem.tipo}
                      onChange={(e) => setNovoItem({ ...novoItem, tipo: e.target.value as 'peca' | 'servico' })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="peca">Peça</option>
                      <option value="servico">Serviço</option>
                    </select>
                  </div>
                  
                  <div className="md:col-span-2">
                    <Label htmlFor="descricao">Descrição</Label>
                    <div className="relative">
                      <Input
                        id="descricao"
                        value={novoItem.descricao}
                        onChange={(e) => setNovoItem({ ...novoItem, descricao: e.target.value })}
                        placeholder={novoItem.tipo === 'peca' ? 'Digite ou busque uma peça' : 'Descrição do serviço'}
                      />
                      {novoItem.tipo === 'peca' && (
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          className="absolute right-1 top-1 h-8"
                          onClick={() => setShowPecaSearch(!showPecaSearch)}
                        >
                          <Search className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                    
                    {/* Busca de Peças */}
                    {showPecaSearch && novoItem.tipo === 'peca' && (
                      <div className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto">
                        <div className="p-2">
                          <Input
                            placeholder="Buscar peças..."
                            value={pecaSearchTerm}
                            onChange={(e) => setPecaSearchTerm(e.target.value)}
                          />
                        </div>
                        <div className="max-h-48 overflow-auto">
                          {pecasFiltradas.map(peca => (
                            <div
                              key={peca.id}
                              className="p-2 hover:bg-gray-100 cursor-pointer border-b"
                              onClick={() => selecionarPeca(peca)}
                            >
                              <div className="font-medium">{peca.nome}</div>
                              <div className="text-sm text-gray-600">
                                {peca.marca} {peca.modelo} - R$ {peca.preco.toFixed(2)}
                              </div>
                              <div className="text-xs text-gray-500">
                                Estoque: {peca.quantidadeEstoque} unidades
                              </div>
                            </div>
                          ))}
                          {pecasFiltradas.length === 0 && (
                            <div className="p-4 text-center text-gray-500">
                              Nenhuma peça encontrada
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div>
                    <Label htmlFor="quantidade">Qtd</Label>
                    <Input
                      id="quantidade"
                      type="number"
                      min="1"
                      value={novoItem.quantidade}
                      onChange={(e) => setNovoItem({ ...novoItem, quantidade: parseInt(e.target.value) || 1 })}
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="valor">Valor Unit.</Label>
                    <Input
                      id="valor"
                      type="number"
                      step="0.01"
                      min="0"
                      value={novoItem.valorUnitario}
                      onChange={(e) => setNovoItem({ ...novoItem, valorUnitario: parseFloat(e.target.value) || 0 })}
                    />
                  </div>
                </div>
                
                {errors.novoItem && (
                  <p className="text-red-500 text-sm mt-2">{errors.novoItem}</p>
                )}
                
                <Button onClick={adicionarItem} className="mt-3">
                  <Plus className="w-4 h-4 mr-2" />
                  Adicionar Item
                </Button>
              </div>

              {/* Lista de Itens */}
              {itens.length > 0 && (
                <div className="space-y-2">
                  <h4 className="font-medium">Itens Adicionados</h4>
                  {itens.map((item, index) => (
                    <div key={item.id} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">
                            {index + 1}. {item.descricao}
                          </span>
                          <span className={`px-2 py-1 text-xs rounded ${
                            item.tipo === 'peca' ? 'bg-blue-100 text-blue-800' : 'bg-green-100 text-green-800'
                          }`}>
                            {item.tipo === 'peca' ? 'Peça' : 'Serviço'}
                          </span>
                        </div>
                        <div className="text-sm text-gray-600">
                          Qtd: {item.quantidade} × R$ {item.valorUnitario.toFixed(2)} = R$ {item.valorTotal.toFixed(2)}
                        </div>
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => removerItem(item.id)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
              
              {errors.itens && (
                <p className="text-red-500 text-sm mt-2">{errors.itens}</p>
              )}
            </CardContent>
          </Card>

          {/* Observações e Validade */}
          <Card>
            <CardHeader>
              <CardTitle>Informações Adicionais</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="observacoes">Observações</Label>
                <textarea
                  id="observacoes"
                  value={formulario.observacoes}
                  onChange={(e) => setFormulario({ ...formulario, observacoes: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  placeholder="Observações sobre o orçamento..."
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="validade">Válido até *</Label>
                  <Input
                    id="validade"
                    type="date"
                    value={formulario.validadeAte}
                    onChange={(e) => setFormulario({ ...formulario, validadeAte: e.target.value })}
                    className={errors.validadeAte ? 'border-red-500' : ''}
                  />
                  {errors.validadeAte && (
                    <p className="text-red-500 text-sm mt-1">{errors.validadeAte}</p>
                  )}
                </div>
                
                <div>
                  <Label htmlFor="desconto">Desconto (R$)</Label>
                  <Input
                    id="desconto"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formulario.valorDesconto}
                    onChange={(e) => setFormulario({ ...formulario, valorDesconto: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Resumo do Orçamento */}
        <div className="lg:col-span-1">
          <Card className="sticky top-4">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calculator className="w-5 h-5" />
                Resumo do Orçamento
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Peças:</span>
                  <span>R$ {valorPecas.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Serviços:</span>
                  <span>R$ {valorServicos.toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Subtotal:</span>
                  <span>R$ {subtotal.toFixed(2)}</span>
                </div>
                {formulario.valorDesconto > 0 && (
                  <div className="flex justify-between text-sm text-green-600">
                    <span>Desconto:</span>
                    <span>- R$ {formulario.valorDesconto.toFixed(2)}</span>
                  </div>
                )}
                <hr />
                <div className="flex justify-between font-bold text-lg">
                  <span>Total:</span>
                  <span>R$ {valorTotal.toFixed(2)}</span>
                </div>
              </div>
              
              <div className="space-y-2 pt-4">
                <Button 
                  onClick={() => salvarOrcamento(false)} 
                  disabled={loading}
                  className="w-full"
                  variant="outline"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {loading ? 'Salvando...' : 'Salvar Rascunho'}
                </Button>
                
                <Button 
                  onClick={() => salvarOrcamento(true)} 
                  disabled={loading}
                  className="w-full"
                >
                  <Send className="w-4 h-4 mr-2" />
                  {loading ? 'Enviando...' : 'Salvar e Enviar'}
                </Button>
              </div>
              
              <div className="text-xs text-gray-500 pt-2">
                <p>• O orçamento será salvo como pendente</p>
                <p>• Cliente receberá por email e WhatsApp</p>
                <p>• Validade: {formulario.validadeAte ? new Date(formulario.validadeAte).toLocaleDateString('pt-BR') : 'Não definida'}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}