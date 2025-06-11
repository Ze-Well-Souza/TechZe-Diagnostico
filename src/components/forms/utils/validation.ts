import { FormFieldConfig, FormValidationRule, FormSchema, FormData } from '../types';

// Validadores básicos
const validators = {
  required: (value: any): boolean => {
    if (value === null || value === undefined) return false;
    if (typeof value === 'string') return value.trim().length > 0;
    if (Array.isArray(value)) return value.length > 0;
    if (typeof value === 'boolean') return true;
    return Boolean(value);
  },

  min: (value: any, minValue: number): boolean => {
    const num = Number(value);
    return !isNaN(num) && num >= minValue;
  },

  max: (value: any, maxValue: number): boolean => {
    const num = Number(value);
    return !isNaN(num) && num <= maxValue;
  },

  minLength: (value: any, minLength: number): boolean => {
    const str = String(value || '');
    return str.length >= minLength;
  },

  maxLength: (value: any, maxLength: number): boolean => {
    const str = String(value || '');
    return str.length <= maxLength;
  },

  pattern: (value: any, pattern: string | RegExp): boolean => {
    if (!value) return true; // Pattern validation is optional if field is empty
    const regex = typeof pattern === 'string' ? new RegExp(pattern) : pattern;
    return regex.test(String(value));
  },

  email: (value: any): boolean => {
    if (!value) return true; // Email validation is optional if field is empty
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(String(value));
  },

  url: (value: any): boolean => {
    if (!value) return true; // URL validation is optional if field is empty
    try {
      new URL(String(value));
      return true;
    } catch {
      return false;
    }
  },

  cpf: (value: any): boolean => {
    if (!value) return true;
    const cpf = String(value).replace(/\D/g, '');
    
    if (cpf.length !== 11) return false;
    if (/^(\d)\1{10}$/.test(cpf)) return false; // Todos os dígitos iguais
    
    // Validação dos dígitos verificadores
    let sum = 0;
    for (let i = 0; i < 9; i++) {
      sum += parseInt(cpf.charAt(i)) * (10 - i);
    }
    let digit1 = 11 - (sum % 11);
    if (digit1 > 9) digit1 = 0;
    
    sum = 0;
    for (let i = 0; i < 10; i++) {
      sum += parseInt(cpf.charAt(i)) * (11 - i);
    }
    let digit2 = 11 - (sum % 11);
    if (digit2 > 9) digit2 = 0;
    
    return parseInt(cpf.charAt(9)) === digit1 && parseInt(cpf.charAt(10)) === digit2;
  },

  cnpj: (value: any): boolean => {
    if (!value) return true;
    const cnpj = String(value).replace(/\D/g, '');
    
    if (cnpj.length !== 14) return false;
    if (/^(\d)\1{13}$/.test(cnpj)) return false; // Todos os dígitos iguais
    
    // Validação dos dígitos verificadores
    const weights1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    const weights2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2];
    
    let sum = 0;
    for (let i = 0; i < 12; i++) {
      sum += parseInt(cnpj.charAt(i)) * weights1[i];
    }
    let digit1 = sum % 11;
    digit1 = digit1 < 2 ? 0 : 11 - digit1;
    
    sum = 0;
    for (let i = 0; i < 13; i++) {
      sum += parseInt(cnpj.charAt(i)) * weights2[i];
    }
    let digit2 = sum % 11;
    digit2 = digit2 < 2 ? 0 : 11 - digit2;
    
    return parseInt(cnpj.charAt(12)) === digit1 && parseInt(cnpj.charAt(13)) === digit2;
  },

  phone: (value: any): boolean => {
    if (!value) return true;
    const phone = String(value).replace(/\D/g, '');
    return phone.length >= 10 && phone.length <= 11;
  },

  cep: (value: any): boolean => {
    if (!value) return true;
    const cep = String(value).replace(/\D/g, '');
    return cep.length === 8;
  },

  currency: (value: any): boolean => {
    if (!value) return true;
    const currencyRegex = /^\d+([,.]\d{1,2})?$/;
    return currencyRegex.test(String(value).replace(/[R$\s]/g, ''));
  }
};

// Função para validar uma regra específica
export const validateRule = async (
  rule: FormValidationRule,
  value: any,
  formData?: FormData
): Promise<boolean> => {
  try {
    switch (rule.type) {
      case 'required':
        return validators.required(value);
      
      case 'min':
        return validators.min(value, rule.value);
      
      case 'max':
        return validators.max(value, rule.value);
      
      case 'minLength':
        return validators.minLength(value, rule.value);
      
      case 'maxLength':
        return validators.maxLength(value, rule.value);
      
      case 'pattern':
        return validators.pattern(value, rule.value);
      
      case 'email':
        return validators.email(value);
      
      case 'url':
        return validators.url(value);
      
      case 'custom':
        if (rule.validator) {
          return await rule.validator(value, formData);
        }
        return true;
      
      default:
        return true;
    }
  } catch (error) {
    console.error('Erro na validação da regra:', error);
    return false;
  }
};

// Função para validar um campo específico
export const validateField = async (
  field: FormFieldConfig,
  value: any,
  formData?: FormData
): Promise<string[]> => {
  const errors: string[] = [];
  
  if (!field.validation || field.validation.length === 0) {
    return errors;
  }
  
  // Validações específicas por tipo de campo
  const typeValidations: FormValidationRule[] = [];
  
  switch (field.type) {
    case 'email':
      typeValidations.push({
        type: 'email',
        message: 'Digite um e-mail válido'
      });
      break;
    
    case 'url':
      typeValidations.push({
        type: 'url',
        message: 'Digite uma URL válida'
      });
      break;
    
    case 'cpf':
      typeValidations.push({
        type: 'custom',
        message: 'Digite um CPF válido',
        validator: (val) => validators.cpf(val)
      });
      break;
    
    case 'cnpj':
      typeValidations.push({
        type: 'custom',
        message: 'Digite um CNPJ válido',
        validator: (val) => validators.cnpj(val)
      });
      break;
    
    case 'phone':
      typeValidations.push({
        type: 'custom',
        message: 'Digite um telefone válido',
        validator: (val) => validators.phone(val)
      });
      break;
    
    case 'cep':
      typeValidations.push({
        type: 'custom',
        message: 'Digite um CEP válido',
        validator: (val) => validators.cep(val)
      });
      break;
    
    case 'currency':
      typeValidations.push({
        type: 'custom',
        message: 'Digite um valor monetário válido',
        validator: (val) => validators.currency(val)
      });
      break;
  }
  
  // Combinar validações do campo com validações do tipo
  const allValidations = [...field.validation, ...typeValidations];
  
  for (const rule of allValidations) {
    const isValid = await validateRule(rule, value, formData);
    if (!isValid) {
      errors.push(rule.message);
    }
  }
  
  return errors;
};

// Função para validar o formulário completo
export const validateForm = async (
  schema: FormSchema,
  formData: FormData
): Promise<Record<string, string[]>> => {
  const errors: Record<string, string[]> = {};
  
  // Validar cada campo
  for (const field of schema.fields) {
    // Pular campos ocultos
    if (field.hidden) continue;
    
    // Verificar condições de visibilidade
    if (field.conditional) {
      const { field: condField, value: condValue, operator = 'equals' } = field.conditional;
      const fieldValue = formData[condField];
      
      let isVisible = true;
      switch (operator) {
        case 'equals':
          isVisible = fieldValue === condValue;
          break;
        case 'not_equals':
          isVisible = fieldValue !== condValue;
          break;
        case 'contains':
          isVisible = Array.isArray(fieldValue) 
            ? fieldValue.includes(condValue) 
            : String(fieldValue).includes(String(condValue));
          break;
        case 'greater_than':
          isVisible = Number(fieldValue) > Number(condValue);
          break;
        case 'less_than':
          isVisible = Number(fieldValue) < Number(condValue);
          break;
      }
      
      if (!isVisible) continue;
    }
    
    const fieldErrors = await validateField(field, formData[field.name], formData);
    if (fieldErrors.length > 0) {
      errors[field.name] = fieldErrors;
    }
  }
  
  return errors;
};

// Função para obter mensagem de erro padrão
export const getDefaultErrorMessage = (rule: FormValidationRule): string => {
  switch (rule.type) {
    case 'required':
      return 'Este campo é obrigatório';
    case 'min':
      return `O valor deve ser maior ou igual a ${rule.value}`;
    case 'max':
      return `O valor deve ser menor ou igual a ${rule.value}`;
    case 'minLength':
      return `Deve ter pelo menos ${rule.value} caracteres`;
    case 'maxLength':
      return `Deve ter no máximo ${rule.value} caracteres`;
    case 'pattern':
      return 'Formato inválido';
    case 'email':
      return 'Digite um e-mail válido';
    case 'url':
      return 'Digite uma URL válida';
    default:
      return 'Valor inválido';
  }
};

// Função para limpar dados do formulário
export const sanitizeFormData = (data: FormData): FormData => {
  const sanitized: FormData = {};
  
  for (const [key, value] of Object.entries(data)) {
    if (typeof value === 'string') {
      sanitized[key] = value.trim();
    } else {
      sanitized[key] = value;
    }
  }
  
  return sanitized;
};

// Função para verificar se o formulário tem mudanças
export const hasFormChanges = (initialData: FormData, currentData: FormData): boolean => {
  const initialKeys = Object.keys(initialData);
  const currentKeys = Object.keys(currentData);
  
  if (initialKeys.length !== currentKeys.length) {
    return true;
  }
  
  for (const key of initialKeys) {
    if (initialData[key] !== currentData[key]) {
      return true;
    }
  }
  
  return false;
};

// Função para resetar erros de validação
export const resetValidationState = () => ({
  isValid: true,
  errors: {},
  touched: {},
  isSubmitting: false,
  isValidating: false
});

export { validators };