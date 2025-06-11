// Componentes principais
export { DynamicForm } from './DynamicForm';
export { FormField } from './FormField';
export { FormSection } from './FormSection';
export { FormActions } from './FormActions';
export { FormWizard } from './FormWizard';
export { FileUpload } from './FileUpload';

// Hooks
export { useForm, useFieldValidation, useDebouncedValidation } from './hooks/useForm';

// Utilitários
export * from './utils/validation';

// Tipos
export type {
  // Tipos básicos
  FieldType,
  ValidationRule,
  FieldOption,
  FieldConfig,
  FormSchema,
  FormSection as FormSectionType,
  FormAction,
  FormData,
  ValidationState,
  FieldValidation,
  
  // Props de componentes
  DynamicFormProps,
  FormFieldProps,
  FormSectionProps,
  FormActionsProps,
  
  // Hooks
  UseFormOptions,
  UseFormReturn,
  UseFieldValidationOptions,
  UseFieldValidationReturn,
  UseDebouncedValidationOptions,
  UseDebouncedValidationReturn,
  
  // Utilitários
  ValidatorFunction,
  ValidationContext,
  
  // Temas
  FormTheme,
  FieldTheme,
  ValidationTheme
} from './types';

export type { WizardStep } from './FormWizard';

// Constantes úteis
export const FIELD_TYPES = {
  TEXT: 'text' as const,
  NUMBER: 'number' as const,
  EMAIL: 'email' as const,
  PASSWORD: 'password' as const,
  TEXTAREA: 'textarea' as const,
  SELECT: 'select' as const,
  MULTISELECT: 'multiselect' as const,
  CHECKBOX: 'checkbox' as const,
  RADIO: 'radio' as const,
  SWITCH: 'switch' as const,
  DATE: 'date' as const,
  DATETIME: 'datetime' as const,
  TIME: 'time' as const,
  FILE: 'file' as const,
  CURRENCY: 'currency' as const,
  CPF: 'cpf' as const,
  CNPJ: 'cnpj' as const,
  PHONE: 'phone' as const,
  CEP: 'cep' as const
} as const;

export const VALIDATION_RULES = {
  REQUIRED: 'required' as const,
  MIN: 'min' as const,
  MAX: 'max' as const,
  MIN_LENGTH: 'minLength' as const,
  MAX_LENGTH: 'maxLength' as const,
  PATTERN: 'pattern' as const,
  EMAIL: 'email' as const,
  URL: 'url' as const,
  CUSTOM: 'custom' as const
} as const;

// Padrões comuns
export const COMMON_PATTERNS = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE: /^\(?\d{2}\)?[\s-]?\d{4,5}[\s-]?\d{4}$/,
  CPF: /^\d{3}\.\d{3}\.\d{3}-\d{2}$/,
  CNPJ: /^\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}$/,
  CEP: /^\d{5}-?\d{3}$/,
  URL: /^https?:\/\/.+/
} as const;

// Mensagens de erro padrão
export const DEFAULT_ERROR_MESSAGES = {
  required: 'Este campo é obrigatório',
  email: 'Digite um e-mail válido',
  url: 'Digite uma URL válida',
  min: 'Valor deve ser maior ou igual a {min}',
  max: 'Valor deve ser menor ou igual a {max}',
  minLength: 'Deve ter pelo menos {minLength} caracteres',
  maxLength: 'Deve ter no máximo {maxLength} caracteres',
  pattern: 'Formato inválido',
  cpf: 'CPF inválido',
  cnpj: 'CNPJ inválido',
  phone: 'Telefone inválido',
  cep: 'CEP inválido'
} as const;

// Utilitários de formatação
export const formatters = {
  cpf: (value: string) => {
    const numbers = value.replace(/\D/g, '');
    return numbers.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
  },
  
  cnpj: (value: string) => {
    const numbers = value.replace(/\D/g, '');
    return numbers.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
  },
  
  phone: (value: string) => {
    const numbers = value.replace(/\D/g, '');
    if (numbers.length <= 10) {
      return numbers.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
    return numbers.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
  },
  
  cep: (value: string) => {
    const numbers = value.replace(/\D/g, '');
    return numbers.replace(/(\d{5})(\d{3})/, '$1-$2');
  },
  
  currency: (value: number, currency = 'BRL') => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency
    }).format(value);
  }
} as const;

// Validadores comuns
export const validators = {
  cpf: (value: string): boolean => {
    const numbers = value.replace(/\D/g, '');
    if (numbers.length !== 11) return false;
    
    // Verificar se todos os dígitos são iguais
    if (/^(\d)\1{10}$/.test(numbers)) return false;
    
    // Validar dígitos verificadores
    let sum = 0;
    for (let i = 0; i < 9; i++) {
      sum += parseInt(numbers[i]) * (10 - i);
    }
    let digit1 = 11 - (sum % 11);
    if (digit1 > 9) digit1 = 0;
    
    sum = 0;
    for (let i = 0; i < 10; i++) {
      sum += parseInt(numbers[i]) * (11 - i);
    }
    let digit2 = 11 - (sum % 11);
    if (digit2 > 9) digit2 = 0;
    
    return parseInt(numbers[9]) === digit1 && parseInt(numbers[10]) === digit2;
  },
  
  cnpj: (value: string): boolean => {
    const numbers = value.replace(/\D/g, '');
    if (numbers.length !== 14) return false;
    
    // Verificar se todos os dígitos são iguais
    if (/^(\d)\1{13}$/.test(numbers)) return false;
    
    // Validar primeiro dígito verificador
    const weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    let sum = 0;
    for (let i = 0; i < 12; i++) {
      sum += parseInt(numbers[i]) * weights1[i];
    }
    let digit1 = sum % 11;
    digit1 = digit1 < 2 ? 0 : 11 - digit1;
    
    // Validar segundo dígito verificador
    const weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    sum = 0;
    for (let i = 0; i < 13; i++) {
      sum += parseInt(numbers[i]) * weights2[i];
    }
    let digit2 = sum % 11;
    digit2 = digit2 < 2 ? 0 : 11 - digit2;
    
    return parseInt(numbers[12]) === digit1 && parseInt(numbers[13]) === digit2;
  }
} as const;