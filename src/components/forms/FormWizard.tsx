import React, { useState, useCallback, useMemo } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  ChevronLeft, 
  ChevronRight, 
  Check, 
  AlertCircle,
  Info,
  CheckCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { DynamicForm } from './DynamicForm';
import { FormSchema, FormData, ValidationState } from './types';
import { validateForm } from './utils/validation';

interface WizardStep {
  id: string;
  title: string;
  description?: string;
  schema: FormSchema;
  optional?: boolean;
  condition?: (data: FormData) => boolean;
}

interface FormWizardProps {
  steps: WizardStep[];
  initialData?: FormData;
  onComplete?: (data: FormData) => void | Promise<void>;
  onStepChange?: (stepIndex: number, stepId: string) => void;
  onCancel?: () => void;
  className?: string;
  showProgress?: boolean;
  showStepList?: boolean;
  allowSkipOptional?: boolean;
  validateOnStepChange?: boolean;
  saveProgress?: boolean;
  storageKey?: string;
}

interface WizardState {
  currentStep: number;
  completedSteps: Set<number>;
  stepData: Record<string, FormData>;
  stepValidation: Record<string, ValidationState>;
  isSubmitting: boolean;
}

const FormWizard: React.FC<FormWizardProps> = ({
  steps,
  initialData = {},
  onComplete,
  onStepChange,
  onCancel,
  className,
  showProgress = true,
  showStepList = true,
  allowSkipOptional = true,
  validateOnStepChange = true,
  saveProgress = false,
  storageKey = 'form-wizard-progress'
}) => {
  // Estado do wizard
  const [wizardState, setWizardState] = useState<WizardState>(() => {
    let savedState: Partial<WizardState> = {};
    
    if (saveProgress && storageKey) {
      try {
        const saved = localStorage.getItem(storageKey);
        if (saved) {
          savedState = JSON.parse(saved);
        }
      } catch (error) {
        console.warn('Erro ao carregar progresso salvo:', error);
      }
    }

    return {
      currentStep: savedState.currentStep || 0,
      completedSteps: new Set(savedState.completedSteps || []),
      stepData: savedState.stepData || { '0': initialData },
      stepValidation: savedState.stepValidation || {},
      isSubmitting: false
    };
  });

  // Filtrar etapas visíveis baseado em condições
  const visibleSteps = useMemo(() => {
    return steps.filter((step, index) => {
      if (!step.condition) return true;
      
      // Combinar dados de todas as etapas anteriores
      const allData = Object.values(wizardState.stepData).reduce(
        (acc, data) => ({ ...acc, ...data }),
        {}
      );
      
      return step.condition(allData);
    });
  }, [steps, wizardState.stepData]);

  const currentStepData = visibleSteps[wizardState.currentStep];
  const isFirstStep = wizardState.currentStep === 0;
  const isLastStep = wizardState.currentStep === visibleSteps.length - 1;
  const progressPercentage = ((wizardState.currentStep + 1) / visibleSteps.length) * 100;

  // Salvar progresso
  const saveProgressToStorage = useCallback((state: WizardState) => {
    if (saveProgress && storageKey) {
      try {
        const dataToSave = {
          currentStep: state.currentStep,
          completedSteps: Array.from(state.completedSteps),
          stepData: state.stepData,
          stepValidation: state.stepValidation
        };
        localStorage.setItem(storageKey, JSON.stringify(dataToSave));
      } catch (error) {
        console.warn('Erro ao salvar progresso:', error);
      }
    }
  }, [saveProgress, storageKey]);

  // Atualizar dados da etapa
  const handleStepDataChange = useCallback((data: FormData) => {
    setWizardState(prev => {
      const newState = {
        ...prev,
        stepData: {
          ...prev.stepData,
          [wizardState.currentStep]: data
        }
      };
      saveProgressToStorage(newState);
      return newState;
    });
  }, [wizardState.currentStep, saveProgressToStorage]);

  // Validar etapa atual
  const validateCurrentStep = useCallback((): boolean => {
    if (!currentStepData) return false;
    
    const stepData = wizardState.stepData[wizardState.currentStep] || {};
    const validation = validateForm(currentStepData.schema, stepData);
    
    setWizardState(prev => ({
      ...prev,
      stepValidation: {
        ...prev.stepValidation,
        [wizardState.currentStep]: validation
      }
    }));

    return validation.isValid;
  }, [currentStepData, wizardState.stepData, wizardState.currentStep]);

  // Navegar para próxima etapa
  const goToNextStep = useCallback(async () => {
    if (isLastStep) {
      // Submeter formulário
      if (validateOnStepChange && !validateCurrentStep()) {
        return;
      }

      setWizardState(prev => ({ ...prev, isSubmitting: true }));
      
      try {
        // Combinar dados de todas as etapas
        const allData = Object.values(wizardState.stepData).reduce(
          (acc, data) => ({ ...acc, ...data }),
          {}
        );
        
        await onComplete?.(allData);
        
        // Limpar progresso salvo após conclusão
        if (saveProgress && storageKey) {
          localStorage.removeItem(storageKey);
        }
      } catch (error) {
        console.error('Erro ao submeter formulário:', error);
      } finally {
        setWizardState(prev => ({ ...prev, isSubmitting: false }));
      }
      return;
    }

    // Validar etapa se necessário
    if (validateOnStepChange && !currentStepData?.optional) {
      if (!validateCurrentStep()) {
        return;
      }
    }

    // Marcar etapa como concluída
    const newCurrentStep = wizardState.currentStep + 1;
    
    setWizardState(prev => {
      const newState = {
        ...prev,
        currentStep: newCurrentStep,
        completedSteps: new Set([...prev.completedSteps, wizardState.currentStep])
      };
      saveProgressToStorage(newState);
      return newState;
    });

    onStepChange?.(newCurrentStep, visibleSteps[newCurrentStep]?.id);
  }, [isLastStep, validateOnStepChange, validateCurrentStep, currentStepData, wizardState, onComplete, onStepChange, visibleSteps, saveProgress, storageKey]);

  // Navegar para etapa anterior
  const goToPreviousStep = useCallback(() => {
    if (isFirstStep) return;
    
    const newCurrentStep = wizardState.currentStep - 1;
    
    setWizardState(prev => {
      const newState = {
        ...prev,
        currentStep: newCurrentStep
      };
      saveProgressToStorage(newState);
      return newState;
    });

    onStepChange?.(newCurrentStep, visibleSteps[newCurrentStep]?.id);
  }, [isFirstStep, wizardState.currentStep, onStepChange, visibleSteps, saveProgressToStorage]);

  // Navegar para etapa específica
  const goToStep = useCallback((stepIndex: number) => {
    if (stepIndex < 0 || stepIndex >= visibleSteps.length) return;
    if (stepIndex > wizardState.currentStep && !wizardState.completedSteps.has(stepIndex - 1)) {
      return; // Não pode pular etapas não concluídas
    }
    
    setWizardState(prev => {
      const newState = {
        ...prev,
        currentStep: stepIndex
      };
      saveProgressToStorage(newState);
      return newState;
    });

    onStepChange?.(stepIndex, visibleSteps[stepIndex]?.id);
  }, [visibleSteps, wizardState.currentStep, wizardState.completedSteps, onStepChange, saveProgressToStorage]);

  // Obter status da etapa
  const getStepStatus = (stepIndex: number): 'completed' | 'current' | 'pending' | 'error' => {
    if (stepIndex < wizardState.currentStep || wizardState.completedSteps.has(stepIndex)) {
      return 'completed';
    }
    if (stepIndex === wizardState.currentStep) {
      const validation = wizardState.stepValidation[stepIndex];
      if (validation && !validation.isValid) {
        return 'error';
      }
      return 'current';
    }
    return 'pending';
  };

  // Renderizar indicador de etapa
  const renderStepIndicator = (step: WizardStep, index: number) => {
    const status = getStepStatus(index);
    const isClickable = index <= wizardState.currentStep || wizardState.completedSteps.has(index);

    return (
      <div
        key={step.id}
        className={cn(
          "flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors",
          isClickable && "hover:bg-muted/50",
          !isClickable && "opacity-50 cursor-not-allowed",
          status === 'current' && "bg-primary/10 border border-primary/20"
        )}
        onClick={() => isClickable && goToStep(index)}
      >
        {/* Ícone da etapa */}
        <div className={cn(
          "flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium",
          status === 'completed' && "bg-green-500 text-white",
          status === 'current' && "bg-primary text-primary-foreground",
          status === 'error' && "bg-red-500 text-white",
          status === 'pending' && "bg-muted text-muted-foreground"
        )}>
          {status === 'completed' ? (
            <Check className="h-4 w-4" />
          ) : status === 'error' ? (
            <AlertCircle className="h-4 w-4" />
          ) : (
            index + 1
          )}
        </div>

        {/* Informações da etapa */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <p className={cn(
              "text-sm font-medium truncate",
              status === 'current' && "text-primary"
            )}>
              {step.title}
            </p>
            {step.optional && (
              <Badge variant="outline" className="text-xs">
                Opcional
              </Badge>
            )}
          </div>
          {step.description && (
            <p className="text-xs text-muted-foreground truncate">
              {step.description}
            </p>
          )}
        </div>
      </div>
    );
  };

  if (!currentStepData) {
    return (
      <Alert>
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>
          Nenhuma etapa válida encontrada.
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Cabeçalho com progresso */}
      {showProgress && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              Etapa {wizardState.currentStep + 1} de {visibleSteps.length}
            </h2>
            <Badge variant="outline">
              {Math.round(progressPercentage)}% concluído
            </Badge>
          </div>
          <Progress value={progressPercentage} className="h-2" />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Lista de etapas */}
        {showStepList && (
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Etapas</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {visibleSteps.map((step, index) => renderStepIndicator(step, index))}
              </CardContent>
            </Card>
          </div>
        )}

        {/* Conteúdo da etapa atual */}
        <div className={cn(
          showStepList ? "lg:col-span-3" : "lg:col-span-4"
        )}>
          <Card>
            <CardHeader>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <CardTitle>{currentStepData.title}</CardTitle>
                  {currentStepData.optional && (
                    <Badge variant="outline">Opcional</Badge>
                  )}
                </div>
                {currentStepData.description && (
                  <p className="text-sm text-muted-foreground">
                    {currentStepData.description}
                  </p>
                )}
              </div>
            </CardHeader>
            
            <CardContent>
              {/* Formulário da etapa */}
              <DynamicForm
                schema={currentStepData.schema}
                data={wizardState.stepData[wizardState.currentStep] || {}}
                onChange={handleStepDataChange}
                validation={wizardState.stepValidation[wizardState.currentStep]}
                showActions={false}
              />

              <Separator className="my-6" />

              {/* Ações do wizard */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  {!isFirstStep && (
                    <Button
                      variant="outline"
                      onClick={goToPreviousStep}
                      disabled={wizardState.isSubmitting}
                    >
                      <ChevronLeft className="h-4 w-4 mr-2" />
                      Anterior
                    </Button>
                  )}
                  
                  {onCancel && (
                    <Button
                      variant="ghost"
                      onClick={onCancel}
                      disabled={wizardState.isSubmitting}
                    >
                      Cancelar
                    </Button>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  {currentStepData.optional && allowSkipOptional && !isLastStep && (
                    <Button
                      variant="outline"
                      onClick={goToNextStep}
                      disabled={wizardState.isSubmitting}
                    >
                      Pular
                    </Button>
                  )}
                  
                  <Button
                    onClick={goToNextStep}
                    disabled={wizardState.isSubmitting}
                    className="min-w-[100px]"
                  >
                    {wizardState.isSubmitting ? (
                      "Processando..."
                    ) : isLastStep ? (
                      "Concluir"
                    ) : (
                      <>
                        Próximo
                        <ChevronRight className="h-4 w-4 ml-2" />
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export { FormWizard, type WizardStep };