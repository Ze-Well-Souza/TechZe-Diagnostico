import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar, ChevronLeft, ChevronRight } from 'lucide-react';
import { format, startOfMonth, endOfMonth, startOfWeek, endOfWeek, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths, isToday, isBefore } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface CalendarioAgendamentoProps {
  dataSelecionada?: Date | null;
  onSelecionarData: (data: Date) => void;
  datasDisponíveis?: Date[];
  className?: string;
}

export const CalendarioAgendamento: React.FC<CalendarioAgendamentoProps> = ({
  dataSelecionada,
  onSelecionarData,
  datasDisponíveis = [],
  className = ''
}) => {
  const [mesAtual, setMesAtual] = useState(new Date());

  const inicioMes = startOfMonth(mesAtual);
  const fimMes = endOfMonth(mesAtual);
  const inicioCalendario = startOfWeek(inicioMes, { weekStartsOn: 0 });
  const fimCalendario = endOfWeek(fimMes, { weekStartsOn: 0 });

  const diasCalendario = eachDayOfInterval({
    start: inicioCalendario,
    end: fimCalendario
  });

  const proximoMes = () => {
    setMesAtual(addMonths(mesAtual, 1));
  };

  const mesAnterior = () => {
    setMesAtual(subMonths(mesAtual, 1));
  };

  const isDiaDisponivel = (dia: Date) => {
    // Se não há datas específicas disponíveis, considera todos os dias futuros
    if (datasDisponíveis.length === 0) {
      return !isBefore(dia, new Date()) || isToday(dia);
    }
    
    // Verifica se o dia está na lista de datas disponíveis
    return datasDisponíveis.some(dataDisponivel => 
      isSameDay(dia, dataDisponivel)
    );
  };

  const isDiaSelecionado = (dia: Date) => {
    return dataSelecionada ? isSameDay(dia, dataSelecionada) : false;
  };

  const handleSelecionarDia = (dia: Date) => {
    if (isDiaDisponivel(dia) && isSameMonth(dia, mesAtual)) {
      onSelecionarData(dia);
    }
  };

  const diasSemana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

  return (
    <Card className={`w-full max-w-md ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <span className="flex items-center gap-2">
            <Calendar className="w-5 h-5" />
            Selecionar Data
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Header do calendário */}
        <div className="flex items-center justify-between">
          <Button
            variant="outline"
            size="sm"
            onClick={mesAnterior}
            className="h-8 w-8 p-0"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          
          <h3 className="font-semibold text-sm">
            {format(mesAtual, 'MMMM yyyy', { locale: ptBR })}
          </h3>
          
          <Button
            variant="outline"
            size="sm"
            onClick={proximoMes}
            className="h-8 w-8 p-0"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        {/* Dias da semana */}
        <div className="grid grid-cols-7 gap-1">
          {diasSemana.map((dia) => (
            <div
              key={dia}
              className="h-8 flex items-center justify-center text-xs font-medium text-gray-500"
            >
              {dia}
            </div>
          ))}
        </div>

        {/* Dias do mês */}
        <div className="grid grid-cols-7 gap-1">
          {diasCalendario.map((dia) => {
            const isCurrentMonth = isSameMonth(dia, mesAtual);
            const isAvailable = isDiaDisponivel(dia);
            const isSelected = isDiaSelecionado(dia);
            const isCurrentDay = isToday(dia);

            return (
              <button
                key={dia.toISOString()}
                onClick={() => handleSelecionarDia(dia)}
                disabled={!isAvailable || !isCurrentMonth}
                className={`
                  h-8 w-8 text-xs rounded-md transition-colors
                  ${!isCurrentMonth ? 'text-gray-300' : ''}
                  ${isCurrentDay ? 'bg-blue-100 text-blue-600 font-semibold' : ''}
                  ${isSelected ? 'bg-blue-600 text-white font-semibold' : ''}
                  ${isAvailable && isCurrentMonth && !isSelected && !isCurrentDay ? 'hover:bg-gray-100' : ''}
                  ${!isAvailable || !isCurrentMonth ? 'cursor-not-allowed opacity-50' : 'cursor-pointer'}
                `}
              >
                {format(dia, 'd')}
              </button>
            );
          })}
        </div>

        {dataSelecionada && (
          <div className="mt-4 p-3 bg-blue-50 rounded-md">
            <p className="text-sm text-blue-700">
              <strong>Data selecionada:</strong> {format(dataSelecionada, "dd 'de' MMMM 'de' yyyy", { locale: ptBR })}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}; 