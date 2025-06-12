import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { CheckCircle2, Calendar, Clock, User, Phone, Mail } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface DadosAgendamento {
  data: Date;
  horario: string;
  cliente: {
    nome: string;
    email: string;
    telefone: string;
    descricaoProblema: string;
  };
}

interface ConfirmacaoAgendamentoProps {
  agendamento: DadosAgendamento;
  onNovoAgendamento: () => void;
  onVoltar: () => void;
  className?: string;
}

export const ConfirmacaoAgendamento: React.FC<ConfirmacaoAgendamentoProps> = ({
  agendamento,
  onNovoAgendamento,
  onVoltar,
  className = ''
}) => {
  return (
    <Card className={`w-full max-w-2xl ${className}`}>
      <CardHeader className="text-center">
        <div className="flex justify-center mb-4">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
            <CheckCircle2 className="w-8 h-8 text-green-600" />
          </div>
        </div>
        <CardTitle className="text-2xl text-green-600">
          Agendamento Confirmado!
        </CardTitle>
        <p className="text-gray-600">
          Seu agendamento foi criado com sucesso. Você receberá uma confirmação por email.
        </p>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Informações de Data e Horário */}
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Data e Horário
          </h3>
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-blue-700">
              <Calendar className="w-4 h-4" />
              <span className="font-medium">
                {format(agendamento.data, "dd 'de' MMMM 'de' yyyy", { locale: ptBR })}
              </span>
            </div>
            <div className="flex items-center gap-2 text-blue-700">
              <Clock className="w-4 h-4" />
              <span className="font-medium">{agendamento.horario}</span>
            </div>
          </div>
        </div>

        {/* Informações do Cliente */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
            <User className="w-5 h-5" />
            Dados do Cliente
          </h3>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <User className="w-4 h-4 text-gray-500" />
              <span className="text-gray-700">{agendamento.cliente.nome}</span>
            </div>
            <div className="flex items-center gap-3">
              <Mail className="w-4 h-4 text-gray-500" />
              <span className="text-gray-700">{agendamento.cliente.email}</span>
            </div>
            <div className="flex items-center gap-3">
              <Phone className="w-4 h-4 text-gray-500" />
              <span className="text-gray-700">{agendamento.cliente.telefone}</span>
            </div>
          </div>
        </div>

        {/* Descrição do Problema */}
        <div className="bg-yellow-50 rounded-lg p-4">
          <h3 className="font-semibold text-yellow-900 mb-3">
            Descrição do Problema
          </h3>
          <p className="text-yellow-700 text-sm leading-relaxed">
            {agendamento.cliente.descricaoProblema}
          </p>
        </div>

        {/* Próximos Passos */}
        <div className="bg-green-50 rounded-lg p-4">
          <h3 className="font-semibold text-green-900 mb-3">
            Próximos Passos
          </h3>
          <ul className="text-green-700 text-sm space-y-2">
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>Você receberá um email de confirmação com todos os detalhes</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>Nosso técnico entrará em contato 1 dia antes do agendamento</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>Prepare o equipamento e mantenha-o acessível</span>
            </li>
            <li className="flex items-start gap-2">
              <CheckCircle2 className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>Tenha em mãos qualquer documentação relevante do problema</span>
            </li>
          </ul>
        </div>

        {/* Botões de Ação */}
        <div className="flex gap-3 pt-4">
          <Button
            variant="outline"
            onClick={onVoltar}
            className="flex-1"
          >
            Voltar
          </Button>
          <Button
            onClick={onNovoAgendamento}
            className="flex-1"
          >
            Novo Agendamento
          </Button>
        </div>

        {/* Informações de Contato */}
        <div className="border-t pt-4 text-center">
          <p className="text-sm text-gray-600">
            Precisa alterar ou cancelar? Entre em contato conosco:
          </p>
          <div className="mt-2 space-y-1">
            <p className="text-sm font-medium text-gray-900">
              📞 (11) 99999-9999
            </p>
            <p className="text-sm font-medium text-gray-900">
              ✉️ contato@techze.com.br
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}; 