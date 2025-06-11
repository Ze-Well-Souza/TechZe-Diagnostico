import React from 'react';
import { cn } from '@/lib/utils';
import { FormFieldProps, FormFieldType } from './types';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { CalendarIcon, Upload, X } from 'lucide-react';
import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';

interface FormFieldComponentProps extends FormFieldProps {
  id: string;
}

const FormField: React.FC<FormFieldComponentProps> = ({
  config,
  value,
  onChange,
  onBlur,
  error,
  touched,
  disabled,
  formData,
  className,
  id
}) => {
  const hasError = error && error.length > 0 && touched;
  const fieldId = `${id}-${config.name}`;

  const renderField = () => {
    const baseProps = {
      id: fieldId,
      disabled: disabled || config.disabled,
      onBlur,
      className: cn(
        hasError && 'border-red-500 focus:border-red-500',
        config.className
      ),
      ...config.props
    };

    switch (config.type) {
      case 'text':
      case 'email':
      case 'password':
      case 'tel':
      case 'url':
        return (
          <Input
            {...baseProps}
            type={config.type}
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder={config.placeholder}
          />
        );

      case 'number':
        return (
          <Input
            {...baseProps}
            type="number"
            value={value || ''}
            onChange={(e) => onChange(e.target.valueAsNumber || e.target.value)}
            placeholder={config.placeholder}
          />
        );

      case 'textarea':
        return (
          <Textarea
            {...baseProps}
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder={config.placeholder}
            rows={config.props?.rows || 3}
          />
        );

      case 'select':
        return (
          <Select
            value={value || ''}
            onValueChange={onChange}
            disabled={baseProps.disabled}
          >
            <SelectTrigger className={baseProps.className}>
              <SelectValue placeholder={config.placeholder} />
            </SelectTrigger>
            <SelectContent>
              {config.options?.map((option) => (
                <SelectItem
                  key={option.value}
                  value={String(option.value)}
                  disabled={option.disabled}
                >
                  <div className="flex items-center gap-2">
                    {option.icon && option.icon}
                    <span>{option.label}</span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        );

      case 'checkbox':
        return (
          <div className="flex items-center space-x-2">
            <Checkbox
              id={fieldId}
              checked={value || false}
              onCheckedChange={onChange}
              disabled={baseProps.disabled}
              className={baseProps.className}
            />
            <Label
              htmlFor={fieldId}
              className={cn(
                'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
                config.labelClassName
              )}
            >
              {config.label}
            </Label>
          </div>
        );

      case 'radio':
        return (
          <RadioGroup
            value={value || ''}
            onValueChange={onChange}
            disabled={baseProps.disabled}
            className={baseProps.className}
          >
            {config.options?.map((option) => (
              <div key={option.value} className="flex items-center space-x-2">
                <RadioGroupItem
                  value={String(option.value)}
                  id={`${fieldId}-${option.value}`}
                  disabled={option.disabled}
                />
                <Label
                  htmlFor={`${fieldId}-${option.value}`}
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  <div className="flex items-center gap-2">
                    {option.icon && option.icon}
                    <span>{option.label}</span>
                  </div>
                  {option.description && (
                    <p className="text-xs text-muted-foreground mt-1">
                      {option.description}
                    </p>
                  )}
                </Label>
              </div>
            ))}
          </RadioGroup>
        );

      case 'switch':
        return (
          <div className="flex items-center space-x-2">
            <Switch
              id={fieldId}
              checked={value || false}
              onCheckedChange={onChange}
              disabled={baseProps.disabled}
              className={baseProps.className}
            />
            <Label
              htmlFor={fieldId}
              className={cn(
                'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
                config.labelClassName
              )}
            >
              {config.label}
            </Label>
          </div>
        );

      case 'date':
        return (
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant="outline"
                className={cn(
                  'w-full justify-start text-left font-normal',
                  !value && 'text-muted-foreground',
                  baseProps.className
                )}
                disabled={baseProps.disabled}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {value ? (
                  format(new Date(value), 'dd/MM/yyyy', { locale: ptBR })
                ) : (
                  <span>{config.placeholder || 'Selecione uma data'}</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0" align="start">
              <Calendar
                mode="single"
                selected={value ? new Date(value) : undefined}
                onSelect={(date) => onChange(date?.toISOString())}
                disabled={(date) => {
                  const minDate = config.props?.minDate ? new Date(config.props.minDate) : undefined;
                  const maxDate = config.props?.maxDate ? new Date(config.props.maxDate) : undefined;
                  return (
                    (minDate && date < minDate) ||
                    (maxDate && date > maxDate)
                  );
                }}
                initialFocus
                locale={ptBR}
              />
            </PopoverContent>
          </Popover>
        );

      case 'file':
        return (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Input
                {...baseProps}
                type="file"
                onChange={(e) => {
                  const files = Array.from(e.target.files || []);
                  onChange(config.props?.multiple ? files : files[0]);
                }}
                accept={config.props?.accept}
                multiple={config.props?.multiple}
                className="hidden"
              />
              <Button
                type="button"
                variant="outline"
                onClick={() => document.getElementById(fieldId)?.click()}
                disabled={baseProps.disabled}
                className={baseProps.className}
              >
                <Upload className="mr-2 h-4 w-4" />
                {config.placeholder || 'Selecionar arquivo(s)'}
              </Button>
            </div>
            {value && (
              <div className="space-y-1">
                {Array.isArray(value) ? (
                  value.map((file: File, index: number) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-muted rounded">
                      <span className="text-sm">{file.name}</span>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          const newFiles = value.filter((_: any, i: number) => i !== index);
                          onChange(newFiles.length > 0 ? newFiles : null);
                        }}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ))
                ) : (
                  <div className="flex items-center justify-between p-2 bg-muted rounded">
                    <span className="text-sm">{value.name}</span>
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => onChange(null)}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        );

      case 'currency':
        return (
          <div className="relative">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">
              R$
            </span>
            <Input
              {...baseProps}
              type="text"
              value={value || ''}
              onChange={(e) => {
                const numericValue = e.target.value.replace(/[^0-9,]/g, '');
                onChange(numericValue);
              }}
              placeholder={config.placeholder || '0,00'}
              className={cn('pl-8', baseProps.className)}
            />
          </div>
        );

      case 'cpf':
        return (
          <Input
            {...baseProps}
            type="text"
            value={value || ''}
            onChange={(e) => {
              let cpf = e.target.value.replace(/\D/g, '');
              cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
              cpf = cpf.replace(/(\d{3})(\d)/, '$1.$2');
              cpf = cpf.replace(/(\d{3})(\d{1,2})$/, '$1-$2');
              onChange(cpf);
            }}
            placeholder={config.placeholder || '000.000.000-00'}
            maxLength={14}
          />
        );

      case 'cnpj':
        return (
          <Input
            {...baseProps}
            type="text"
            value={value || ''}
            onChange={(e) => {
              let cnpj = e.target.value.replace(/\D/g, '');
              cnpj = cnpj.replace(/(\d{2})(\d)/, '$1.$2');
              cnpj = cnpj.replace(/(\d{3})(\d)/, '$1.$2');
              cnpj = cnpj.replace(/(\d{3})(\d)/, '$1/$2');
              cnpj = cnpj.replace(/(\d{4})(\d{1,2})$/, '$1-$2');
              onChange(cnpj);
            }}
            placeholder={config.placeholder || '00.000.000/0000-00'}
            maxLength={18}
          />
        );

      case 'phone':
        return (
          <Input
            {...baseProps}
            type="text"
            value={value || ''}
            onChange={(e) => {
              let phone = e.target.value.replace(/\D/g, '');
              if (phone.length <= 10) {
                phone = phone.replace(/(\d{2})(\d)/, '($1) $2');
                phone = phone.replace(/(\d{4})(\d)/, '$1-$2');
              } else {
                phone = phone.replace(/(\d{2})(\d)/, '($1) $2');
                phone = phone.replace(/(\d{5})(\d)/, '$1-$2');
              }
              onChange(phone);
            }}
            placeholder={config.placeholder || '(00) 00000-0000'}
            maxLength={15}
          />
        );

      case 'cep':
        return (
          <Input
            {...baseProps}
            type="text"
            value={value || ''}
            onChange={(e) => {
              let cep = e.target.value.replace(/\D/g, '');
              cep = cep.replace(/(\d{5})(\d)/, '$1-$2');
              onChange(cep);
            }}
            placeholder={config.placeholder || '00000-000'}
            maxLength={9}
          />
        );

      default:
        return (
          <Input
            {...baseProps}
            type="text"
            value={value || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder={config.placeholder}
          />
        );
    }
  };

  // Para campos que não precisam de label separado (checkbox, switch)
  const noLabelTypes: FormFieldType[] = ['checkbox', 'switch'];
  const showLabel = !noLabelTypes.includes(config.type);

  return (
    <div className={cn('space-y-2', config.containerClassName, className)}>
      {showLabel && (
        <Label
          htmlFor={fieldId}
          className={cn(
            'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
            config.required && 'after:content-["*"] after:ml-0.5 after:text-red-500',
            config.labelClassName
          )}
        >
          {config.label}
        </Label>
      )}
      
      {config.description && (
        <p className="text-xs text-muted-foreground">
          {config.description}
        </p>
      )}
      
      {renderField()}
      
      {hasError && (
        <div className="space-y-1">
          {error.map((errorMsg, index) => (
            <p key={index} className="text-xs text-red-500">
              {errorMsg}
            </p>
          ))}
        </div>
      )}
    </div>
  );
};

export { FormField };
export type { FormFieldComponentProps };