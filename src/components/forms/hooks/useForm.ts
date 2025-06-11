import { useState, useCallback, useEffect, useRef } from 'react';
import {
  UseFormOptions,
  UseFormReturn,
  FormData,
  FormValidationState,
  FormFieldConfig
} from '../types';
import {
  validateField,
  validateForm,
  sanitizeFormData,
  hasFormChanges,
  resetValidationState
} from '../utils/validation';

export const useForm = (options: UseFormOptions): UseFormReturn => {
  const {
    schema,
    initialData = {},
    onSubmit,
    onChange,
    onValidationChange,
    mode = 'onSubmit'
  } = options;

  // Estados
  const [data, setData] = useState<FormData>(initialData);
  const [validationState, setValidationState] = useState<FormValidationState>(resetValidationState());
  const [isDirty, setIsDirty] = useState(false);
  
  // Refs para evitar re-renders desnecessários
  const initialDataRef = useRef(initialData);
  const submitTimeoutRef = useRef<NodeJS.Timeout>();

  // Atualizar dados iniciais quando mudarem
  useEffect(() => {
    if (JSON.stringify(initialData) !== JSON.stringify(initialDataRef.current)) {
      initialDataRef.current = initialData;
      setData(initialData);
      setIsDirty(false);
      setValidationState(resetValidationState());
    }
  }, [initialData]);

  // Verificar se há mudanças
  useEffect(() => {
    const hasChanges = hasFormChanges(initialDataRef.current, data);
    setIsDirty(hasChanges);
  }, [data]);

  // Notificar mudanças
  useEffect(() => {
    onChange?.(data);
  }, [data, onChange]);

  useEffect(() => {
    onValidationChange?.(validationState);
  }, [validationState, onValidationChange]);

  // Função para definir valor de campo
  const setValue = useCallback(async (fieldName: string, value: any) => {
    const newData = { ...data, [fieldName]: value };
    setData(newData);

    // Validação em tempo real se configurada
    if (mode === 'onChange') {
      const field = schema.fields.find(f => f.name === fieldName);
      if (field) {
        setValidationState(prev => ({ ...prev, isValidating: true }));
        
        try {
          const fieldErrors = await validateField(field, value, newData);
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
  }, [data, schema, mode]);

  // Função para obter valor de campo
  const getValue = useCallback((fieldName: string) => {
    return data[fieldName];
  }, [data]);

  // Função para definir erro de campo
  const setError = useCallback((fieldName: string, errors: string[]) => {
    setValidationState(prev => ({
      ...prev,
      errors: {
        ...prev.errors,
        [fieldName]: errors
      }
    }));
  }, []);

  // Função para limpar erro de campo
  const clearError = useCallback((fieldName: string) => {
    setValidationState(prev => {
      const newErrors = { ...prev.errors };
      delete newErrors[fieldName];
      return {
        ...prev,
        errors: newErrors
      };
    });
  }, []);

  // Função para validar campo específico
  const validateFieldFn = useCallback(async (fieldName: string): Promise<boolean> => {
    const field = schema.fields.find(f => f.name === fieldName);
    if (!field) return true;

    setValidationState(prev => ({ ...prev, isValidating: true }));

    try {
      const fieldErrors = await validateField(field, data[fieldName], data);
      const isValid = fieldErrors.length === 0;

      setValidationState(prev => ({
        ...prev,
        errors: {
          ...prev.errors,
          [fieldName]: fieldErrors
        },
        touched: {
          ...prev.touched,
          [fieldName]: true
        },
        isValidating: false
      }));

      return isValid;
    } catch (error) {
      console.error('Erro na validação do campo:', error);
      setValidationState(prev => ({ ...prev, isValidating: false }));
      return false;
    }
  }, [schema, data]);

  // Função para validar formulário completo
  const validateFormFn = useCallback(async (): Promise<boolean> => {
    setValidationState(prev => ({ ...prev, isValidating: true }));

    try {
      const formErrors = await validateForm(schema, data);
      const isValid = Object.values(formErrors).every(errors => errors.length === 0);

      // Marcar todos os campos como tocados
      const allTouched = schema.fields.reduce(
        (acc, field) => ({ ...acc, [field.name]: true }),
        {}
      );

      setValidationState(prev => ({
        ...prev,
        errors: formErrors,
        touched: { ...prev.touched, ...allTouched },
        isValid,
        isValidating: false
      }));

      return isValid;
    } catch (error) {
      console.error('Erro na validação do formulário:', error);
      setValidationState(prev => ({
        ...prev,
        isValidating: false,
        isValid: false
      }));
      return false;
    }
  }, [schema, data]);

  // Função para resetar formulário
  const reset = useCallback((newData?: FormData) => {
    const resetData = newData || initialDataRef.current;
    setData(resetData);
    setValidationState(resetValidationState());
    setIsDirty(false);
    
    if (newData) {
      initialDataRef.current = newData;
    }
  }, []);

  // Função para submeter formulário
  const submit = useCallback(async () => {
    // Limpar timeout anterior se existir
    if (submitTimeoutRef.current) {
      clearTimeout(submitTimeoutRef.current);
    }

    setValidationState(prev => ({ ...prev, isSubmitting: true }));

    try {
      // Validar formulário
      const isValid = await validateFormFn();
      
      if (isValid && onSubmit) {
        // Sanitizar dados antes de enviar
        const sanitizedData = sanitizeFormData(data);
        await onSubmit(sanitizedData);
        
        // Resetar estado de dirty após submit bem-sucedido
        setIsDirty(false);
        initialDataRef.current = sanitizedData;
      }
    } catch (error) {
      console.error('Erro no submit:', error);
      
      // Adicionar erro geral se não houver erros específicos
      if (Object.keys(validationState.errors).length === 0) {
        setValidationState(prev => ({
          ...prev,
          errors: {
            _form: ['Erro ao enviar formulário. Tente novamente.']
          }
        }));
      }
    } finally {
      // Usar timeout para evitar mudanças de estado muito rápidas
      submitTimeoutRef.current = setTimeout(() => {
        setValidationState(prev => ({ ...prev, isSubmitting: false }));
      }, 100);
    }
  }, [data, onSubmit, validateFormFn, validationState.errors]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (submitTimeoutRef.current) {
        clearTimeout(submitTimeoutRef.current);
      }
    };
  }, []);

  // Calcular propriedades derivadas
  const isValid = Object.values(validationState.errors).every(errors => errors.length === 0);
  const canSubmit = isValid && !validationState.isSubmitting && !validationState.isValidating;

  return {
    data,
    validationState: {
      ...validationState,
      isValid
    },
    setValue,
    getValue,
    setError,
    clearError,
    validateField: validateFieldFn,
    validateForm: validateFormFn,
    reset,
    submit,
    isDirty,
    isValid,
    canSubmit
  };
};

// Hook para validação de campo individual
export const useFieldValidation = (
  field: FormFieldConfig,
  value: any,
  formData?: FormData
) => {
  const [errors, setErrors] = useState<string[]>([]);
  const [isValidating, setIsValidating] = useState(false);

  const validate = useCallback(async () => {
    setIsValidating(true);
    try {
      const fieldErrors = await validateField(field, value, formData);
      setErrors(fieldErrors);
      return fieldErrors.length === 0;
    } catch (error) {
      console.error('Erro na validação do campo:', error);
      setErrors(['Erro na validação']);
      return false;
    } finally {
      setIsValidating(false);
    }
  }, [field, value, formData]);

  useEffect(() => {
    validate();
  }, [validate]);

  return {
    errors,
    isValidating,
    isValid: errors.length === 0,
    validate
  };
};

// Hook para debounce de validação
export const useDebouncedValidation = (
  validateFn: () => Promise<boolean>,
  delay: number = 300
) => {
  const [isValidating, setIsValidating] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const debouncedValidate = useCallback(async () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    setIsValidating(true);

    return new Promise<boolean>((resolve) => {
      timeoutRef.current = setTimeout(async () => {
        try {
          const result = await validateFn();
          resolve(result);
        } catch (error) {
          console.error('Erro na validação debounced:', error);
          resolve(false);
        } finally {
          setIsValidating(false);
        }
      }, delay);
    });
  }, [validateFn, delay]);

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return {
    debouncedValidate,
    isValidating
  };
};