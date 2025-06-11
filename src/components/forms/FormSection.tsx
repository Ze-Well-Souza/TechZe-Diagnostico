import React, { useState } from 'react';
import { cn } from '@/lib/utils';
import { FormSectionProps } from './types';
import { FormField } from './FormField';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

const FormSection: React.FC<FormSectionProps> = ({
  config,
  fields,
  formData,
  errors,
  touched,
  onChange,
  onBlur,
  disabled = false,
  className
}) => {
  const [isExpanded, setIsExpanded] = useState(
    config.defaultExpanded !== undefined ? config.defaultExpanded : true
  );

  // Verificar se a seção deve ser visível baseado em condições
  const isVisible = () => {
    if (!config.conditional) return true;
    
    const { field, value, operator = 'equals' } = config.conditional;
    const fieldValue = formData[field];
    
    switch (operator) {
      case 'equals':
        return fieldValue === value;
      case 'not_equals':
        return fieldValue !== value;
      case 'contains':
        return Array.isArray(fieldValue) 
          ? fieldValue.includes(value) 
          : String(fieldValue).includes(String(value));
      case 'greater_than':
        return Number(fieldValue) > Number(value);
      case 'less_than':
        return Number(fieldValue) < Number(value);
      default:
        return true;
    }
  };

  // Filtrar campos visíveis
  const visibleFields = fields.filter(field => {
    if (field.hidden) return false;
    
    if (field.conditional) {
      const { field: condField, value: condValue, operator = 'equals' } = field.conditional;
      const fieldValue = formData[condField];
      
      switch (operator) {
        case 'equals':
          return fieldValue === condValue;
        case 'not_equals':
          return fieldValue !== condValue;
        case 'contains':
          return Array.isArray(fieldValue) 
            ? fieldValue.includes(condValue) 
            : String(fieldValue).includes(String(condValue));
        case 'greater_than':
          return Number(fieldValue) > Number(condValue);
        case 'less_than':
          return Number(fieldValue) < Number(condValue);
        default:
          return true;
      }
    }
    
    return true;
  });

  // Renderizar campos em grid
  const renderFields = () => {
    return (
      <div className="grid gap-4 grid-cols-1 md:grid-cols-2">
        {visibleFields.map((field) => {
          const gridClasses = field.grid ? [
            field.grid.xs && `col-span-${field.grid.xs}`,
            field.grid.sm && `sm:col-span-${field.grid.sm}`,
            field.grid.md && `md:col-span-${field.grid.md}`,
            field.grid.lg && `lg:col-span-${field.grid.lg}`,
            field.grid.xl && `xl:col-span-${field.grid.xl}`
          ].filter(Boolean).join(' ') : '';
          
          return (
            <div key={field.name} className={gridClasses}>
              <FormField
                id={config.id}
                config={field}
                value={formData[field.name]}
                onChange={(value) => onChange(field.name, value)}
                onBlur={() => onBlur(field.name)}
                error={errors[field.name]}
                touched={touched[field.name]}
                disabled={disabled || field.disabled}
                formData={formData}
              />
            </div>
          );
        })}
      </div>
    );
  };

  // Se a seção não deve ser visível, não renderizar
  if (!isVisible()) {
    return null;
  }

  // Se não é colapsível, renderizar como card simples
  if (!config.collapsible) {
    return (
      <Card className={cn('w-full', config.className, className)}>
        <CardHeader>
          <CardTitle className="text-lg">{config.title}</CardTitle>
          {config.description && (
            <CardDescription>{config.description}</CardDescription>
          )}
        </CardHeader>
        <CardContent>
          {renderFields()}
        </CardContent>
      </Card>
    );
  }

  // Renderizar como seção colapsível
  return (
    <Card className={cn('w-full', config.className, className)}>
      <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
        <CollapsibleTrigger asChild>
          <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <CardTitle className="text-lg flex items-center gap-2">
                  {config.title}
                  {/* Indicador visual se há erros na seção */}
                  {visibleFields.some(field => 
                    errors[field.name] && errors[field.name].length > 0 && touched[field.name]
                  ) && (
                    <span className="inline-flex h-2 w-2 rounded-full bg-red-500" />
                  )}
                </CardTitle>
                {config.description && (
                  <CardDescription>{config.description}</CardDescription>
                )}
              </div>
              <Button variant="ghost" size="sm" className="p-1">
                {isExpanded ? (
                  <ChevronDown className="h-4 w-4" />
                ) : (
                  <ChevronRight className="h-4 w-4" />
                )}
              </Button>
            </div>
          </CardHeader>
        </CollapsibleTrigger>
        
        <CollapsibleContent>
          <CardContent className="pt-0">
            {renderFields()}
          </CardContent>
        </CollapsibleContent>
      </Collapsible>
    </Card>
  );
};

export { FormSection };