import React from 'react';
import { cn } from '@/lib/utils';
import { FormActionsProps } from './types';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

const FormActions: React.FC<FormActionsProps> = ({
  actions,
  formData,
  validationState,
  onAction,
  className
}) => {
  // Filtrar ações visíveis baseado em condições
  const visibleActions = actions.filter(action => {
    if (!action.conditional) return true;
    
    const { field, value, operator = 'equals' } = action.conditional;
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
  });

  // Determinar se uma ação deve estar desabilitada
  const isActionDisabled = (action: typeof actions[0]) => {
    if (action.disabled) return true;
    
    // Para ações de submit, verificar se o formulário é válido
    if (action.type === 'submit') {
      return !validationState.isValid || validationState.isSubmitting;
    }
    
    return false;
  };

  // Determinar se uma ação deve mostrar loading
  const isActionLoading = (action: typeof actions[0]) => {
    if (action.loading) return true;
    
    // Para ações de submit, mostrar loading durante submissão
    if (action.type === 'submit' && validationState.isSubmitting) {
      return true;
    }
    
    return false;
  };

  // Renderizar ação individual
  const renderAction = (action: typeof actions[0]) => {
    const disabled = isActionDisabled(action);
    const loading = isActionLoading(action);
    
    const buttonProps = {
      variant: action.variant || 'default',
      size: action.size || 'default',
      disabled,
      className: cn(action.className),
      onClick: () => onAction(action.id)
    };

    // Para ações de link, renderizar como link
    if (action.type === 'link') {
      return (
        <Button
          key={action.id}
          {...buttonProps}
          variant="link"
          type="button"
        >
          {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {!loading && action.icon && (
            <span className="mr-2">{action.icon}</span>
          )}
          {action.label}
        </Button>
      );
    }

    // Para outras ações, renderizar como botão
    return (
      <Button
        key={action.id}
        {...buttonProps}
        type={action.type === 'submit' ? 'submit' : 'button'}
      >
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {!loading && action.icon && (
          <span className="mr-2">{action.icon}</span>
        )}
        {action.label}
      </Button>
    );
  };

  // Se não há ações visíveis, não renderizar nada
  if (visibleActions.length === 0) {
    return null;
  }

  return (
    <div className={cn('flex items-center justify-end gap-2 flex-wrap', className)}>
      {visibleActions.map(renderAction)}
    </div>
  );
};

export { FormActions };