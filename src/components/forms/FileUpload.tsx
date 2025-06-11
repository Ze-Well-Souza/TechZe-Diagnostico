import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Upload, 
  File, 
  Image, 
  X, 
  CheckCircle, 
  AlertCircle,
  FileText,
  FileImage,
  FileVideo,
  FileAudio,
  Download
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  value?: File[];
  onChange?: (files: File[]) => void;
  accept?: string;
  maxFiles?: number;
  maxSize?: number; // em bytes
  multiple?: boolean;
  disabled?: boolean;
  className?: string;
  placeholder?: string;
  showPreview?: boolean;
  allowedTypes?: string[];
  onError?: (error: string) => void;
}

interface UploadedFile {
  file: File;
  id: string;
  progress: number;
  status: 'uploading' | 'success' | 'error';
  preview?: string;
  error?: string;
}

const FileUpload: React.FC<FileUploadProps> = ({
  value = [],
  onChange,
  accept,
  maxFiles = 5,
  maxSize = 5 * 1024 * 1024, // 5MB
  multiple = true,
  disabled = false,
  className,
  placeholder = "Arraste arquivos aqui ou clique para selecionar",
  showPreview = true,
  allowedTypes = [],
  onError
}) => {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isDragActive, setIsDragActive] = useState(false);

  const validateFile = (file: File): string | null => {
    // Validar tamanho
    if (file.size > maxSize) {
      return `Arquivo muito grande. Tamanho máximo: ${formatFileSize(maxSize)}`;
    }

    // Validar tipo
    if (allowedTypes.length > 0) {
      const fileExtension = file.name.split('.').pop()?.toLowerCase();
      if (!fileExtension || !allowedTypes.includes(fileExtension)) {
        return `Tipo de arquivo não permitido. Tipos aceitos: ${allowedTypes.join(', ')}`;
      }
    }

    return null;
  };

  const onDrop = useCallback((acceptedFiles: File[], rejectedFiles: any[]) => {
    // Processar arquivos rejeitados
    rejectedFiles.forEach(({ file, errors }) => {
      const errorMessage = errors.map((e: any) => e.message).join(', ');
      onError?.(errorMessage);
    });

    // Processar arquivos aceitos
    const validFiles: File[] = [];
    const newUploadedFiles: UploadedFile[] = [];

    acceptedFiles.forEach(file => {
      const validationError = validateFile(file);
      
      if (validationError) {
        onError?.(validationError);
        return;
      }

      // Verificar limite de arquivos
      if (value.length + validFiles.length >= maxFiles) {
        onError?.(`Máximo de ${maxFiles} arquivos permitidos`);
        return;
      }

      validFiles.push(file);
      
      const uploadedFile: UploadedFile = {
        file,
        id: `${Date.now()}-${Math.random()}`,
        progress: 0,
        status: 'uploading'
      };

      // Gerar preview para imagens
      if (file.type.startsWith('image/') && showPreview) {
        const reader = new FileReader();
        reader.onload = (e) => {
          uploadedFile.preview = e.target?.result as string;
          setUploadedFiles(prev => 
            prev.map(f => f.id === uploadedFile.id ? { ...f, preview: uploadedFile.preview } : f)
          );
        };
        reader.readAsDataURL(file);
      }

      newUploadedFiles.push(uploadedFile);
    });

    if (validFiles.length > 0) {
      setUploadedFiles(prev => [...prev, ...newUploadedFiles]);
      
      // Simular upload
      newUploadedFiles.forEach(uploadedFile => {
        simulateUpload(uploadedFile.id);
      });

      // Atualizar valor
      onChange?.([...value, ...validFiles]);
    }
  }, [value, onChange, maxFiles, maxSize, allowedTypes, onError, showPreview]);

  const simulateUpload = (fileId: string) => {
    const interval = setInterval(() => {
      setUploadedFiles(prev => 
        prev.map(file => {
          if (file.id === fileId) {
            const newProgress = Math.min(file.progress + 10, 100);
            const newStatus = newProgress === 100 ? 'success' : 'uploading';
            
            if (newProgress === 100) {
              clearInterval(interval);
            }
            
            return { ...file, progress: newProgress, status: newStatus };
          }
          return file;
        })
      );
    }, 200);
  };

  const removeFile = (fileId: string) => {
    const fileToRemove = uploadedFiles.find(f => f.id === fileId);
    if (fileToRemove) {
      const newValue = value.filter(f => f !== fileToRemove.file);
      onChange?.(newValue);
      setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
    }
  };

  const { getRootProps, getInputProps, isDragActive: dropzoneActive } = useDropzone({
    onDrop,
    accept: accept ? { [accept]: [] } : undefined,
    multiple,
    disabled,
    maxFiles,
    maxSize,
    onDragEnter: () => setIsDragActive(true),
    onDragLeave: () => setIsDragActive(false)
  });

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (file: File) => {
    const type = file.type;
    
    if (type.startsWith('image/')) return <FileImage className="h-4 w-4" />;
    if (type.startsWith('video/')) return <FileVideo className="h-4 w-4" />;
    if (type.startsWith('audio/')) return <FileAudio className="h-4 w-4" />;
    if (type.includes('pdf')) return <FileText className="h-4 w-4" />;
    
    return <File className="h-4 w-4" />;
  };

  const getStatusIcon = (status: UploadedFile['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return null;
    }
  };

  return (
    <div className={cn("space-y-4", className)}>
      {/* Área de Upload */}
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors",
          "hover:border-primary/50 hover:bg-primary/5",
          isDragActive && "border-primary bg-primary/10",
          disabled && "opacity-50 cursor-not-allowed",
          "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2"
        )}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center gap-2">
          <Upload className={cn(
            "h-8 w-8 text-muted-foreground",
            isDragActive && "text-primary"
          )} />
          
          <div className="space-y-1">
            <p className="text-sm font-medium">
              {isDragActive ? "Solte os arquivos aqui" : placeholder}
            </p>
            <p className="text-xs text-muted-foreground">
              Máximo {maxFiles} arquivo(s), até {formatFileSize(maxSize)} cada
            </p>
            {allowedTypes.length > 0 && (
              <p className="text-xs text-muted-foreground">
                Tipos aceitos: {allowedTypes.join(', ')}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Lista de Arquivos */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium">Arquivos ({uploadedFiles.length})</h4>
          
          <div className="space-y-2">
            {uploadedFiles.map((uploadedFile) => (
              <div
                key={uploadedFile.id}
                className="flex items-center gap-3 p-3 border rounded-lg bg-card"
              >
                {/* Preview ou Ícone */}
                <div className="flex-shrink-0">
                  {uploadedFile.preview ? (
                    <img
                      src={uploadedFile.preview}
                      alt={uploadedFile.file.name}
                      className="w-10 h-10 object-cover rounded"
                    />
                  ) : (
                    <div className="w-10 h-10 bg-muted rounded flex items-center justify-center">
                      {getFileIcon(uploadedFile.file)}
                    </div>
                  )}
                </div>

                {/* Informações do Arquivo */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium truncate">
                      {uploadedFile.file.name}
                    </p>
                    {getStatusIcon(uploadedFile.status)}
                  </div>
                  
                  <div className="flex items-center gap-2 mt-1">
                    <p className="text-xs text-muted-foreground">
                      {formatFileSize(uploadedFile.file.size)}
                    </p>
                    
                    {uploadedFile.status === 'uploading' && (
                      <>
                        <span className="text-xs text-muted-foreground">•</span>
                        <p className="text-xs text-muted-foreground">
                          {uploadedFile.progress}%
                        </p>
                      </>
                    )}
                  </div>

                  {/* Barra de Progresso */}
                  {uploadedFile.status === 'uploading' && (
                    <Progress 
                      value={uploadedFile.progress} 
                      className="h-1 mt-2"
                    />
                  )}

                  {/* Erro */}
                  {uploadedFile.status === 'error' && uploadedFile.error && (
                    <Alert className="mt-2">
                      <AlertCircle className="h-4 w-4" />
                      <AlertDescription className="text-xs">
                        {uploadedFile.error}
                      </AlertDescription>
                    </Alert>
                  )}
                </div>

                {/* Ações */}
                <div className="flex items-center gap-1">
                  {uploadedFile.status === 'success' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        const url = URL.createObjectURL(uploadedFile.file);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = uploadedFile.file.name;
                        a.click();
                        URL.revokeObjectURL(url);
                      }}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                  )}
                  
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(uploadedFile.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Informações Adicionais */}
      {value.length > 0 && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <Badge variant="outline">
            {value.length} de {maxFiles} arquivo(s)
          </Badge>
          
          <span>•</span>
          
          <span>
            Total: {formatFileSize(value.reduce((total, file) => total + file.size, 0))}
          </span>
        </div>
      )}
    </div>
  );
};

export { FileUpload };