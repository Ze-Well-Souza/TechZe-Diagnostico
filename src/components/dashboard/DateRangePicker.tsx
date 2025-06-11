import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { format, subDays, subWeeks, subMonths, startOfDay, endOfDay } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { Calendar as CalendarIcon, ChevronDown } from 'lucide-react';
import { DateRange } from '@/hooks/useCharts';

export interface DateRangePickerProps {
  value: DateRange;
  onChange: (range: DateRange) => void;
  className?: string;
  disabled?: boolean;
}

interface PresetRange {
  label: string;
  value: string;
  range: DateRange;
}

const getPresetRanges = (): PresetRange[] => {
  const today = new Date();
  
  return [
    {
      label: 'Hoje',
      value: 'today',
      range: {
        start: startOfDay(today),
        end: endOfDay(today),
      },
    },
    {
      label: 'Últimos 7 dias',
      value: 'last7days',
      range: {
        start: startOfDay(subDays(today, 6)),
        end: endOfDay(today),
      },
    },
    {
      label: 'Últimos 15 dias',
      value: 'last15days',
      range: {
        start: startOfDay(subDays(today, 14)),
        end: endOfDay(today),
      },
    },
    {
      label: 'Últimos 30 dias',
      value: 'last30days',
      range: {
        start: startOfDay(subDays(today, 29)),
        end: endOfDay(today),
      },
    },
    {
      label: 'Última semana',
      value: 'lastweek',
      range: {
        start: startOfDay(subWeeks(today, 1)),
        end: endOfDay(subDays(today, 1)),
      },
    },
    {
      label: 'Último mês',
      value: 'lastmonth',
      range: {
        start: startOfDay(subMonths(today, 1)),
        end: endOfDay(today),
      },
    },
    {
      label: 'Últimos 3 meses',
      value: 'last3months',
      range: {
        start: startOfDay(subMonths(today, 3)),
        end: endOfDay(today),
      },
    },
  ];
};

export const DateRangePicker: React.FC<DateRangePickerProps> = ({
  value,
  onChange,
  className,
  disabled = false,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedPreset, setSelectedPreset] = useState<string>('');
  const [customRange, setCustomRange] = useState<{ from?: Date; to?: Date }>({});
  
  const presetRanges = getPresetRanges();

  // Verificar se o range atual corresponde a algum preset
  const getCurrentPreset = () => {
    const current = presetRanges.find(preset => 
      preset.range.start.getTime() === value.start.getTime() &&
      preset.range.end.getTime() === value.end.getTime()
    );
    return current?.value || 'custom';
  };

  const handlePresetChange = (presetValue: string) => {
    const preset = presetRanges.find(p => p.value === presetValue);
    if (preset) {
      onChange(preset.range);
      setSelectedPreset(presetValue);
      setIsOpen(false);
    }
  };

  const handleCustomRangeChange = (range: { from?: Date; to?: Date }) => {
    setCustomRange(range);
    
    if (range.from && range.to) {
      onChange({
        start: startOfDay(range.from),
        end: endOfDay(range.to),
      });
      setSelectedPreset('custom');
      setIsOpen(false);
    }
  };

  const formatDateRange = (range: DateRange): string => {
    const startFormatted = format(range.start, 'dd/MM/yyyy', { locale: ptBR });
    const endFormatted = format(range.end, 'dd/MM/yyyy', { locale: ptBR });
    
    if (startFormatted === endFormatted) {
      return startFormatted;
    }
    
    return `${startFormatted} - ${endFormatted}`;
  };

  const getDaysDifference = (range: DateRange): number => {
    const diffTime = range.end.getTime() - range.start.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
  };

  const currentPreset = getCurrentPreset();
  const isCustom = currentPreset === 'custom';
  const daysDiff = getDaysDifference(value);

  return (
    <div className={cn('flex items-center space-x-2', className)}>
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className={cn(
              'justify-start text-left font-normal min-w-[280px]',
              !value && 'text-muted-foreground'
            )}
            disabled={disabled}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            <span className="flex-1">
              {formatDateRange(value)}
            </span>
            <ChevronDown className="ml-2 h-4 w-4 opacity-50" />
          </Button>
        </PopoverTrigger>
        
        <PopoverContent className="w-auto p-0" align="start">
          <div className="flex">
            {/* Lista de presets */}
            <div className="border-r p-3 space-y-1 min-w-[160px]">
              <div className="text-sm font-medium text-gray-900 mb-2">
                Períodos
              </div>
              
              {presetRanges.map((preset) => (
                <Button
                  key={preset.value}
                  variant={currentPreset === preset.value ? 'default' : 'ghost'}
                  size="sm"
                  className="w-full justify-start text-sm"
                  onClick={() => handlePresetChange(preset.value)}
                >
                  {preset.label}
                </Button>
              ))}
              
              <Button
                variant={isCustom ? 'default' : 'ghost'}
                size="sm"
                className="w-full justify-start text-sm"
                onClick={() => setSelectedPreset('custom')}
              >
                Personalizado
              </Button>
            </div>
            
            {/* Calendário */}
            <div className="p-3">
              <Calendar
                mode="range"
                defaultMonth={value.start}
                selected={{
                  from: value.start,
                  to: value.end,
                }}
                onSelect={(range) => {
                  if (range?.from && range?.to) {
                    handleCustomRangeChange({
                      from: range.from,
                      to: range.to,
                    });
                  } else if (range?.from) {
                    setCustomRange({ from: range.from });
                  }
                }}
                numberOfMonths={2}
                locale={ptBR}
                className="rounded-md"
              />
            </div>
          </div>
          
          {/* Rodapé com informações */}
          <div className="border-t p-3 bg-gray-50">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>
                Período selecionado: {daysDiff} {daysDiff === 1 ? 'dia' : 'dias'}
              </span>
              
              {isCustom && (
                <Badge variant="secondary">
                  Personalizado
                </Badge>
              )}
            </div>
          </div>
        </PopoverContent>
      </Popover>
      
      {/* Indicador visual do período */}
      <div className="flex items-center space-x-1">
        <Badge 
          variant={daysDiff <= 7 ? 'default' : daysDiff <= 30 ? 'secondary' : 'outline'}
          className="text-xs"
        >
          {daysDiff}d
        </Badge>
      </div>
    </div>
  );
};

// Componente simplificado para seleção rápida
export interface QuickDateSelectorProps {
  value: DateRange;
  onChange: (range: DateRange) => void;
  className?: string;
}

export const QuickDateSelector: React.FC<QuickDateSelectorProps> = ({
  value,
  onChange,
  className,
}) => {
  const presetRanges = getPresetRanges().slice(1, 5); // Apenas os mais comuns
  
  const getCurrentPreset = () => {
    const current = presetRanges.find(preset => 
      preset.range.start.getTime() === value.start.getTime() &&
      preset.range.end.getTime() === value.end.getTime()
    );
    return current?.value || '';
  };

  return (
    <Select
      value={getCurrentPreset()}
      onValueChange={(presetValue) => {
        const preset = presetRanges.find(p => p.value === presetValue);
        if (preset) {
          onChange(preset.range);
        }
      }}
    >
      <SelectTrigger className={cn('w-[180px]', className)}>
        <SelectValue placeholder="Selecionar período" />
      </SelectTrigger>
      <SelectContent>
        {presetRanges.map((preset) => (
          <SelectItem key={preset.value} value={preset.value}>
            {preset.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};