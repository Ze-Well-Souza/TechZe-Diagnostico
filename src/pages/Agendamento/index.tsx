import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Calendar,
  Clock,
  MapPin,
  Phone,
  CheckCircle2,
  AlertCircle,
  User,
  Wrench,
  CalendarDays
} from 'lucide-react';
import { useAgendamento } from '@/hooks/useAgendamento';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { CalendarioAgendamento } from '@/components/agendamento/CalendarioAgendamento';
import { SeletorHorario } from '@/components/agendamento/SeletorHorario';
import { FormularioAgendamento } from '@/components/agendamento/FormularioAgendamento';
import { ConfirmacaoAgendamento } from '@/components/agendamento/ConfirmacaoAgendamento';

interface AgendamentoPageProps {}

type EtapaAgendamento = 'data' | 'horario' | 'dados' | 'confirmacao';

const AgendamentoPage: React.FC<AgendamentoPageProps> = () => {
  const {
    disponibilidade,
    agendamentos,
    loading,
    error,
    carregarDisponibilidade,
    criarAgendamento,
    confirmarAgendamento
  } = useAgendamento();

  const [etapaAtual, setEtapaAtual] = useState<EtapaAgendamento>('data');
  const [dataSelecionada, setDataSelecionada] = useState<Date | null>(null);
  const [horarioSelecionado, setHorarioSelecionado] = useState<string | null>(null);
  const [dadosCliente, setDadosCliente] = useState({
    nome: '',
    email: '',
    telefone: '',
    tipoServico: '',
    descricaoProblema: '',
    equipamento: {
      tipo: '',
      marca: '',
      modelo: ''
    }
  });
  const [agendamentoCriado, setAgendamentoCriado] = useState<any>(null);

  useEffect(() => {
    carregarDisponibilidade();
  }, [carregarDisponibilidade]);

  const handleSelecionarData = (data: Date) => {
    setDataSelecionada(data);
    setEtapaAtual('horario');
  };

  const handleSelecionarHorario = (horario: string) => {
    setHorarioSelecionado(horario);
    setEtapaAtual('dados');
  };

  const handleSubmitDados = async (dados: typeof dadosCliente) => {
    setDadosCliente(dados);
    
    try {
      const agendamento = await criarAgendamento({
        data: dataSelecionada!,
        horario: horarioSelecionado!,
        ...dados
      });
      
      setAgendamentoCriado(agendamento);
      setEtapaAtual('confirmacao');
    } catch (err) {
      console.error('Erro ao criar agendamento:', err);
    }
  };

  const handleVoltar = () => {
    switch (etapaAtual) {
      case 'horario':
        setEtapaAtual('data');
        setHorarioSelecionado(null);
        break;
      case 'dados':
        setEtapaAtual('horario');
        break;
      case 'confirmacao':
        setEtapaAtual('dados');
        break;
    }
  };

  const handleNovoAgendamento = () => {
    setEtapaAtual('data');
    setDataSelecionada(null);
    setHorarioSelecionado(null);
    setDadosCliente({
      nome: '',
      email: '',
      telefone: '',
      tipoServico: '',
      descricaoProblema: '',
      equipamento: {
        tipo: '',
        marca: '',
        modelo: ''
      }
    });
    setAgendamentoCriado(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando disponibilidade...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Alert className="max-w-md">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <div className="flex items-center space-x-3">
              <CalendarDays className="w-8 h-8 text-blue-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Agendar Atendimento
                </h1>
                <p className="text-gray-600">
                  Escolha a melhor data e horário para seu atendimento
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-4">
            <div className="flex items-center justify-between">
              {[
                { key: 'data', label: 'Data', icon: Calendar },
                { key: 'horario', label: 'Horário', icon: Clock },
                { key: 'dados', label: 'Dados', icon: User },
                { key: 'confirmacao', label: 'Confirmação', icon: CheckCircle2 }
              ].map((step, index) => {
                const isActive = step.key === etapaAtual;
                const isCompleted = [
                  'data',
                  etapaAtual === 'horario' || etapaAtual === 'dados' || etapaAtual === 'confirmacao' ? 'horario' : null,
                  etapaAtual === 'dados' || etapaAtual === 'confirmacao' ? 'dados' : null,
                  etapaAtual === 'confirmacao' ? 'confirmacao' : null
                ].includes(step.key);
                
                const Icon = step.icon;
                
                return (
                  <div key={step.key} className="flex items-center">
                    <div className={`flex items-center space-x-2 ${
                      isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-400'
                    }`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        isActive ? 'bg-blue-100' : isCompleted ? 'bg-green-100' : 'bg-gray-100'
                      }`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <span className="font-medium">{step.label}</span>
                    </div>
                    {index < 3 && (
                      <div className={`w-12 h-0.5 mx-4 ${
                        isCompleted ? 'bg-green-300' : 'bg-gray-200'
                      }`} />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {etapaAtual === 'data' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Calendar className="w-5 h-5" />
                <span>Selecione a Data</span>
              </CardTitle>
              <CardDescription>
                Escolha uma data disponível para seu atendimento
              </CardDescription>
            </CardHeader>
            <CardContent>
              <CalendarioAgendamento
                disponibilidade={disponibilidade}
                onSelecionarData={handleSelecionarData}
                dataSelecionada={dataSelecionada}
              />
            </CardContent>
          </Card>
        )}

        {etapaAtual === 'horario' && dataSelecionada && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Clock className="w-5 h-5" />
                <span>Selecione o Horário</span>
              </CardTitle>
              <CardDescription>
                Data selecionada: {dataSelecionada.toLocaleDateString('pt-BR', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric'
                })}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <SeletorHorario
                data={dataSelecionada}
                disponibilidade={disponibilidade}
                onSelecionarHorario={handleSelecionarHorario}
                horarioSelecionado={horarioSelecionado}
              />
              <div className="flex justify-between mt-6">
                <Button variant="outline" onClick={handleVoltar}>
                  Voltar
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {etapaAtual === 'dados' && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <User className="w-5 h-5" />
                <span>Seus Dados</span>
              </CardTitle>
              <CardDescription>
                Preencha suas informações para finalizar o agendamento
              </CardDescription>
            </CardHeader>
            <CardContent>
              <FormularioAgendamento
                dadosIniciais={dadosCliente}
                onSubmit={handleSubmitDados}
                onVoltar={handleVoltar}
                dataSelecionada={dataSelecionada}
                horarioSelecionado={horarioSelecionado}
              />
            </CardContent>
          </Card>
        )}

        {etapaAtual === 'confirmacao' && agendamentoCriado && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2 text-green-600">
                <CheckCircle2 className="w-5 h-5" />
                <span>Agendamento Confirmado!</span>
              </CardTitle>
              <CardDescription>
                Seu atendimento foi agendado com sucesso
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ConfirmacaoAgendamento
                agendamento={agendamentoCriado}
                onNovoAgendamento={handleNovoAgendamento}
              />
            </CardContent>
          </Card>
        )}
      </div>

      {/* Informações de Contato */}
      <div className="bg-white border-t mt-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <MapPin className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900">Endereço</h3>
              <p className="text-sm text-gray-600">
                Rua das Tecnologias, 123<br />
                Centro - São Paulo/SP
              </p>
            </div>
            <div className="text-center">
              <Phone className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900">Telefone</h3>
              <p className="text-sm text-gray-600">
                (11) 9999-9999<br />
                (11) 3333-3333
              </p>
            </div>
            <div className="text-center">
              <Clock className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <h3 className="font-medium text-gray-900">Horário</h3>
              <p className="text-sm text-gray-600">
                Segunda a Sexta: 8h às 18h<br />
                Sábado: 8h às 12h
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgendamentoPage;