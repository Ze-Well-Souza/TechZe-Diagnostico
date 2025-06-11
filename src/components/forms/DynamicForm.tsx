import React, { useState, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { DynamicFormProps, FormData, FormValidationState, FormFieldConfig } from './types';
import { FormField } from './FormField';
import { FormSection } from './FormSection';
import { FormActions } from './FormActions';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useForm } from './hooks/useForm';
import { validateField, validateForm } from './utils/validation';

const DynamicForm: React.FC<DynamicFormProps> = ({
  schema,
  initialData = {},
  onSubmit,
  onCancel,
  onChange,
  onValidationChange,
  disabled = false,
  loading = false,
  className
}) => {
  const [formData, setFormData] = useState<FormData>(initialData);
  const [validationState, setValidationState] = useState<FormValidationState>({
    isValid: true,
    errors: {},
    touched: {},
    isSubmitting: false,
    isValidating: false
  });

  // Atualizar dados quando initialData mudar
  useEffect(() => {
    setFormData(initialData);
  }, [initialData]);

  // Notificar mudanças
  useEffect(() => {
    onChange?.(formData);
  }, [formData, onChange]);

  useEffect(() => {
    onValidationChange?.(validationState);
  }, [validationState, onValidationChange]);

  // Função para atualizar valor de campo
  const handleFieldChange = useCallback(async (fieldName: string, value: any) => {
    const newFormData = { ...formData, [fieldName]: value };
    setFormData(newFormData);

    // Validação em tempo real se configurada
    if (schema.validation?.mode === 'onChange') {
      const field = schema.fields.find(f => f.name === fieldName);
      if (field) {
        setValidationState(prev => ({ ...prev, isValidating: true }));
        
        try {
          const fieldErrors = await validateField(field, value, newFormData);
          setValidationState(prev => ({
            ...prev,
            errors: {
              ...prev.errors,
              [fieldName]: fieldErrors
            },
            isValidating: false
          }));
        } catch (error) {
          console.error('Erro na validação:', error);
          setValidationState(prev => ({ ...prev, isValidating: false }));
        }
      }
    }
  }, [formData, schema]);

  // Função para marcar campo como tocado
  const handleFieldBlur = useCallback(async (fieldName: string) => {
    setValidationState(prev => ({
      ...prev,
      touched: { ...prev.touched, [fieldName]: true }
    }));

    // Validação no blur se configurada
    if (schema.validation?.mode === 'onBlur' || schema.validation?.reValidateMode === 'onBlur') {
      const field = schema.fields.find(f => f.name === fieldName);
      if (field) {
        setValidationState(prev => ({ ...prev, isValidating: true }));
        
        try {
          const fieldErrors = await validateField(field, formData[fieldName], formData);
          setValidationState(prev => ({
            ...prev,
            errors: {
              ...prev.errors,
              [fieldName]: fieldErrors
            },
            isValidating: false
          }));
        } catch (error) {
          console.error('Erro na validação:', error);
          setValidationState(prev => ({ ...prev, isValidating: false }));
        }
      }
    }
  }, [formData, schema]);

  // Função para submeter formulário
  const handleSubmit = useCallback(async (e?: React.FormEvent) => {
    e?.preventDefault();
    
    setValidationState(prev => ({ ...prev, isSubmitting: true }));

    try {
      // Validar formulário completo
      const formErrors = await validateForm(schema, formData);
      const hasErrors = Object.values(formErrors).some(errors => errors.length > 0);

      setValidationState(prev => ({
        ...prev,
        errors: formErrors,
        isValid: !hasErrors,
        touched: schema.fields.reduce((acc, field) => ({ ...acc, [field.name]: true }), {})
      }));

      if (!hasErrors) {
        await onSubmit(formData);
      }
    } catch (error) {
      console.error('Erro no submit:', error);
    } finally {
      setValidationState(prev => ({ ...prev, isSubmitting: false }));
    }
  }, [schema, formData, onSubmit]);

  // Função para resetar formulário
  const handleReset = useCallback(() => {
    setFormData(initialData);
    setValidationState({
      isValid: true,
      errors: {},
      touched: {},
      isSubmitting: false,
      isValidating: false
    });
  }, [initialData]);

  // Função para lidar com ações
  const handleAction = useCallback(async (actionId: string) => {
    const action = schema.actions?.find(a => a.id === actionId);
    if (!action) return;

    switch (action.type) {
      case 'submit':
        await handleSubmit();
        break;
      case 'reset':
        handleReset();
        break;
      case 'button':
      case 'link':
        if (action.onClick) {
          await action.onClick(formData, { handleSubmit, handleReset });
        }
        break;
    }
  }, [schema.actions, formData, handleSubmit, handleReset]);

  // Filtrar campos visíveis baseado em condições
  const getVisibleFields = useCallback((fields: FormFieldConfig[]) => {
    return fields.filter(field => {
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
            return Array.isArray(fieldValue) ? fieldValue.includes(condValue) : String(fieldValue).includes(String(condValue));
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
  }, [formData]);

  // Renderizar campos em grid
  const renderFieldsGrid = useCallback((fields: FormFieldConfig[]) => {
    const visibleFields = getVisibleFields(fields);
    const columns = schema.layout?.columns || 1;
    
    return (
      <div 
        className={cn(
          'grid gap-4',
          columns === 1 && 'grid-cols-1',
          columns === 2 && 'grid-cols-1 md:grid-cols-2',
          columns === 3 && 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
          columns === 4 && 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
        )}
      >
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
                id={schema.id}
                config={field}
                value={formData[field.name]}
                onChange={(value) => handleFieldChange(field.name, value)}
                onBlur={() => handleFieldBlur(field.name)}
                error={validationState.errors[field.name]}
                touched={validationState.touched[field.name]}
                disabled={disabled || field.disabled}
                formData={formData}
              />
            </div>
          );
        })}
      </div>
    );
  }, [schema, formData, validationState, disabled, getVisibleFields, handleFieldChange, handleFieldBlur]);

  // Renderizar seções
  const renderSections = useCallback(() => {
    if (!schema.sections || schema.sections.length === 0) {
      return renderFieldsGrid(schema.fields);
    }

    return (
      <div className="space-y-6">
        {schema.sections.map((section) => {
          const sectionFields = schema.fields.filter(field => 
            section.fields.includes(field.name)
          );
          
          return (
            <FormSection
              key={section.id}
              config={section}
              fields={sectionFields}
              formData={formData}
              errors={validationState.errors}
              touched={validationState.touched}
              onChange={handleFieldChange}
              onBlur={handleFieldBlur}
              disabled={disabled}
            />
          );
        })}
        
        {/* Campos que não estão em nenhuma seção */}
        {(() => {
          const fieldsInSections = schema.sections.flatMap(s => s.fields);
          const orphanFields = schema.fields.filter(f => !fieldsInSections.includes(f.name));
          
          if (orphanFields.length > 0) {
            return (
              <div className="space-y-4">
                <h3 className="text-lg font-medium">Outros campos</h3>
                {renderFieldsGrid(orphanFields)}
              </div>
            );
          }
          
          return null;
        })()}
      </div>
    );
  }, [schema, formData, validationState, disabled, renderFieldsGrid, handleFieldChange, handleFieldBlur]);

  // Renderizar tabs
  const renderTabs = useCallback(() => {
    if (!schema.sections || schema.sections.length === 0) {
      return renderFieldsGrid(schema.fields);
    }

    return (
      <Tabs defaultValue={schema.sections[0]?.id} className="w-full">
        <TabsList className="grid w-full" style={{ gridTemplateColumns: `repeat(${schema.sections.length}, 1fr)` }}>
          {schema.sections.map((section) => (
            <TabsTrigger key={section.id} value={section.id}>
              {section.title}
            </TabsTrigger>
          ))}
        </TabsList>
        
        {schema.sections.map((section) => {
          const sectionFields = schema.fields.filter(field => 
            section.fields.includes(field.name)
          );
          
          return (
            <TabsContent key={section.id} value={section.id} className="mt-6">
              <div className="space-y-4">
                {section.description && (
                  <p className="text-sm text-muted-foreground">
                    {section.description}
                  </p>
                )}
                {renderFieldsGrid(sectionFields)}
              </div>
            </TabsContent>
          );
        })}
      </Tabs>
    );
  }, [schema, renderFieldsGrid]);

  // Renderizar conteúdo baseado no layout
  const renderContent = useCallback(() => {
    switch (schema.layout?.type) {
      case 'tabs':
        return renderTabs();
      case 'grid':
      case 'single':
      default:
        return renderSections();
    }
  }, [schema.layout?.type, renderTabs, renderSections]);

  return (
    <Card className={cn('w-full', className)}>
      {(schema.title || schema.description) && (
        <CardHeader>
          {schema.title && (
            <CardTitle>{schema.title}</CardTitle>
          )}
          {schema.description && (
            <CardDescription>{schema.description}</CardDescription>
          )}
        </CardHeader>
      )}
      
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {renderContent()}
          
          {schema.actions && schema.actions.length > 0 && (
            <FormActions
              actions={schema.actions}
              formData={formData}
              validationState={validationState}
              onAction={handleAction}
              className="pt-6 border-t"
            />
          )}
        </form>
      </CardContent>
    </Card>
  );
};

export { DynamicForm };