import { ReactNode } from 'react';

// Tipos básicos de campo de formulário
export type FormFieldType = 
  | 'text'
  | 'email'
  | 'password'
  | 'number'
  | 'tel'
  | 'url'
  | 'textarea'
  | 'select'
  | 'multiselect'
  | 'checkbox'
  | 'radio'
  | 'date'
  | 'datetime'
  | 'time'
  | 'file'
  | 'image'
  | 'color'
  | 'range'
  | 'switch'
  | 'rating'
  | 'currency'
  | 'cpf'
  | 'cnpj'
  | 'phone'
  | 'cep';

// Regras de validação
export interface FormValidationRule {
  type: 'required' | 'min' | 'max' | 'minLength' | 'maxLength' | 'pattern' | 'email' | 'url' | 'custom';
  value?: any;
  message: string;
  validator?: (value: any, formData?: FormData) => boolean | Promise<boolean>;
}

// Opções para campos select/radio
export interface FormFieldOption {
  value: string | number;
  label: string;
  disabled?: boolean;
  icon?: ReactNode;
  description?: string;
}

// Configuração de campo de formulário
export interface FormFieldConfig {
  name: string;
  type: FormFieldType;
  label: string;
  placeholder?: string;
  description?: string;
  required?: boolean;
  disabled?: boolean;
  readonly?: boolean;
  hidden?: boolean;
  defaultValue?: any;
  options?: FormFieldOption[];
  validation?: FormValidationRule[];
  dependencies?: string[]; // Campos que afetam este campo
  conditional?: {
    field: string;
    value: any;
    operator?: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than';
  };
  props?: Record<string, any>; // Props específicas do tipo de campo
  className?: string;
  containerClassName?: string;
  labelClassName?: string;
  grid?: {
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
}

// Schema completo do formulário
export interface FormSchema {
  id: string;
  title?: string;
  description?: string;
  sections?: FormSectionConfig[];
  fields: FormFieldConfig[];
  validation?: {
    mode?: 'onChange' | 'onBlur' | 'onSubmit';
    reValidateMode?: 'onChange' | 'onBlur';
  };
  layout?: {
    type: 'single' | 'grid' | 'tabs' | 'wizard';
    columns?: number;
    spacing?: 'sm' | 'md' | 'lg';
  };
  actions?: FormActionConfig[];
}

// Configuração de seção
export interface FormSectionConfig {
  id: string;
  title: string;
  description?: string;
  collapsible?: boolean;
  defaultExpanded?: boolean;
  fields: string[]; // IDs dos campos
  conditional?: {
    field: string;
    value: any;
    operator?: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than';
  };
  className?: string;
}

// Configuração de ações
export interface FormActionConfig {
  id: string;
  type: 'submit' | 'reset' | 'button' | 'link';
  label: string;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  disabled?: boolean;
  loading?: boolean;
  icon?: ReactNode;
  onClick?: (formData: FormData, form: any) => void | Promise<void>;
  conditional?: {
    field: string;
    value: any;
    operator?: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than';
  };
  className?: string;
}

// Dados do formulário
export interface FormData {
  [key: string]: any;
}

// Estado de validação
export interface FormValidationState {
  isValid: boolean;
  errors: Record<string, string[]>;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  isValidating: boolean;
}

// Props dos componentes
export interface FormFieldProps {
  config: FormFieldConfig;
  value?: any;
  onChange: (value: any) => void;
  onBlur?: () => void;
  error?: string[];
  touched?: boolean;
  disabled?: boolean;
  formData?: FormData;
  className?: string;
}

export interface FormSectionProps {
  config: FormSectionConfig;
  fields: FormFieldConfig[];
  formData: FormData;
  errors: Record<string, string[]>;
  touched: Record<string, boolean>;
  onChange: (field: string, value: any) => void;
  onBlur: (field: string) => void;
  disabled?: boolean;
  className?: string;
}

export interface FormActionsProps {
  actions: FormActionConfig[];
  formData: FormData;
  validationState: FormValidationState;
  onAction: (actionId: string) => void;
  className?: string;
}

export interface FormValidationProps {
  schema: FormSchema;
  data: FormData;
  mode?: 'onChange' | 'onBlur' | 'onSubmit';
  onValidationChange: (state: FormValidationState) => void;
}

export interface DynamicFormProps {
  schema: FormSchema;
  initialData?: FormData;
  onSubmit: (data: FormData) => void | Promise<void>;
  onCancel?: () => void;
  onChange?: (data: FormData) => void;
  onValidationChange?: (state: FormValidationState) => void;
  disabled?: boolean;
  loading?: boolean;
  className?: string;
}

export interface FileUploadProps {
  accept?: string;
  multiple?: boolean;
  maxSize?: number; // em bytes
  maxFiles?: number;
  onUpload: (files: File[]) => void | Promise<void>;
  onError?: (error: string) => void;
  preview?: boolean;
  dragAndDrop?: boolean;
  disabled?: boolean;
  className?: string;
}

export interface DatePickerProps {
  value?: Date;
  onChange: (date: Date | undefined) => void;
  placeholder?: string;
  format?: string;
  locale?: string;
  minDate?: Date;
  maxDate?: Date;
  disabled?: boolean;
  showTime?: boolean;
  timeFormat?: string;
  className?: string;
}

export interface SearchableSelectProps {
  options: FormFieldOption[];
  value?: string | string[];
  onChange: (value: string | string[]) => void;
  placeholder?: string;
  searchPlaceholder?: string;
  multiple?: boolean;
  clearable?: boolean;
  disabled?: boolean;
  loading?: boolean;
  onSearch?: (query: string) => void;
  renderOption?: (option: FormFieldOption) => ReactNode;
  className?: string;
}

export interface FormWizardProps {
  steps: FormWizardStep[];
  initialStep?: number;
  onComplete: (data: FormData) => void | Promise<void>;
  onCancel?: () => void;
  onStepChange?: (step: number, data: FormData) => void;
  allowStepNavigation?: boolean;
  showProgress?: boolean;
  className?: string;
}

export interface FormWizardStep {
  id: string;
  title: string;
  description?: string;
  schema: FormSchema;
  validation?: (data: FormData) => boolean | Promise<boolean>;
  onNext?: (data: FormData) => void | Promise<void>;
  onPrevious?: (data: FormData) => void | Promise<void>;
  optional?: boolean;
}

export interface FormBuilderProps {
  schema?: FormSchema;
  onSchemaChange: (schema: FormSchema) => void;
  onPreview?: (schema: FormSchema) => void;
  onSave?: (schema: FormSchema) => void;
  availableFields?: FormFieldType[];
  customComponents?: Record<string, React.ComponentType<any>>;
  className?: string;
}

// Contexto do formulário
export interface FormContextValue {
  schema: FormSchema;
  data: FormData;
  validationState: FormValidationState;
  setValue: (field: string, value: any) => void;
  setError: (field: string, error: string[]) => void;
  clearError: (field: string) => void;
  validateField: (field: string) => Promise<boolean>;
  validateForm: () => Promise<boolean>;
  reset: (data?: FormData) => void;
  submit: () => Promise<void>;
}

// Hooks
export interface UseFormOptions {
  schema: FormSchema;
  initialData?: FormData;
  onSubmit?: (data: FormData) => void | Promise<void>;
  onChange?: (data: FormData) => void;
  onValidationChange?: (state: FormValidationState) => void;
  mode?: 'onChange' | 'onBlur' | 'onSubmit';
}

export interface UseFormReturn {
  data: FormData;
  validationState: FormValidationState;
  setValue: (field: string, value: any) => void;
  getValue: (field: string) => any;
  setError: (field: string, error: string[]) => void;
  clearError: (field: string) => void;
  validateField: (field: string) => Promise<boolean>;
  validateForm: () => Promise<boolean>;
  reset: (data?: FormData) => void;
  submit: () => Promise<void>;
  isDirty: boolean;
  isValid: boolean;
  canSubmit: boolean;
}

// Utilitários
export interface FormFieldValidator {
  validate: (value: any, rule: FormValidationRule, formData?: FormData) => boolean | Promise<boolean>;
  getMessage: (rule: FormValidationRule, value: any) => string;
}

export interface FormFieldRenderer {
  type: FormFieldType;
  component: React.ComponentType<FormFieldProps>;
  defaultProps?: Partial<FormFieldProps>;
}

export interface FormTheme {
  colors: {
    primary: string;
    secondary: string;
    success: string;
    warning: string;
    error: string;
    background: string;
    foreground: string;
    muted: string;
    border: string;
  };
  spacing: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
  };
  fontSize: {
    xs: string;
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
}