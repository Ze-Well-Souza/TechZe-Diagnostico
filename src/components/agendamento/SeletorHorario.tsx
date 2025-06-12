import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Clock, CheckCircle2 } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface SeletorHorarioProps {
  dataSelecionada: Date;
  horarioSelecionado?: string | null;
  onSelecionarHorario: (horario: string) => void;
  horariosDisponíveis?: string[];
  className?: string;
}

export const SeletorHorario: React.FC<SeletorHorarioProps> = ({
  dataSelecionada,
  horarioSelecionado,
  onSelecionarHorario,
  horariosDisponíveis = [
    '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
    '11:00', '11:30', '13:00', '13:30', '14:00', '14:30',
    '15:00', '15:30', '16:00', '16:30', '17:00', '17:30'
  ],
  className = ''
}) => {
  
  // Organizar horários por período
  const horariosManha = horariosDisponíveis.filter(h => {
    const hora = parseInt(h.split(':')[0]);
    return hora >= 8 && hora < 12;
  });

  const horariosTarde = horariosDisponíveis.filter(h => {
    const hora = parseInt(h.split(':')[0]);
    return hora >= 13 && hora < 18;
  });

  const renderBotaoHorario = (horario: string) => {
    const isSelected = horarioSelecionado === horario;
    
    return (
      <Button
        key={horario}
        variant={isSelected ? "default" : "outline"}
        size="sm"
        onClick={() => onSelecionarHorario(horario)}
        className={`
          relative h-10 px-4 transition-all duration-200
          ${isSelected ? 'bg-blue-600 text-white' : 'hover:bg-blue-50 hover:border-blue-300'}
        `}
      >
        <span className="flex items-center gap-2">
          <Clock className="w-3 h-3" />
          {horario}
          {isSelected && <CheckCircle2 className="w-3 h-3" />}
        </span>
      </Button>
    );
  };

  return (
    <Card className={`w-full max-w-md ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2">
          <Clock className="w-5 h-5" />
          Selecionar Horário
        </CardTitle>
        <p className="text-sm text-gray-600">
          {format(dataSelecionada, "dd 'de' MMMM 'de' yyyy", { locale: ptBR })}
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Período da Manhã */}
        {horariosManha.length > 0 && (
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-700 flex items-center gap-2">
              🌅 Manhã
            </h4>
            <div className="grid grid-cols-3 gap-2">
              {horariosManha.map(renderBotaoHorario)}
            </div>
          </div>
        )}

        {/* Período da Tarde */}
        {horariosTarde.length > 0 && (
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-gray-700 flex items-center gap-2">
              ☀️ Tarde
            </h4>
            <div className="grid grid-cols-3 gap-2">
              {horariosTarde.map(renderBotaoHorario)}
            </div>
          </div>
        )}

        {/* Horário selecionado */}
        {horarioSelecionado && (
          <div className="mt-4 p-3 bg-green-50 rounded-md border border-green-200">
            <p className="text-sm text-green-700 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4" />
              <strong>Horário selecionado:</strong> {horarioSelecionado}
            </p>
          </div>
        )}

        {/* Mensagem quando não há horários */}
        {horariosDisponíveis.length === 0 && (
          <div className="text-center py-8">
            <Clock className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 text-sm">
              Não há horários disponíveis para esta data.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}; 