import React, { useState } from 'react';
import { usePWA } from '../contexts/PWAContext';
import { useOfflineOperations } from '../hooks/useOfflineOperations';
import {
  Wifi,
  WifiOff,
  Download,
  RefreshCw,
  CheckCircle,
  AlertCircle,
  Clock,
  HardDrive,
  Smartphone,
  Monitor,
  Battery,
  Signal,
  ChevronDown,
  ChevronUp,
  Trash2,
  RotateCcw
} from 'lucide-react';

interface PWAStatusProps {
  className?: string;
  compact?: boolean;
}

const PWAStatus: React.FC<PWAStatusProps> = ({ className = '', compact = false }) => {
  const {
    isOnline,
    isInstallable,
    isInstalled,
    isUpdateAvailable,
    promptInstall,
    updateApp,
    syncStatus,
    pendingOperations,
    cacheStatus,
    networkType,
    isLowDataMode
  } = usePWA();

  const {
    pendingOperations: detailedOperations,
    isProcessing,
    lastSyncTime,
    syncErrors,
    retryAllFailed,
    clearCompleted,
    forceSync,
    getFailedOperations,
    getTotalSize
  } = useOfflineOperations();

  const [isExpanded, setIsExpanded] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  const getNetworkIcon = () => {
    if (!isOnline) return <WifiOff className="w-4 h-4 text-red-500" />;
    
    switch (networkType) {
      case '4g':
      case 'fast':
        return <Signal className="w-4 h-4 text-green-500" />;
      case '3g':
      case 'slow':
        return <Signal className="w-4 h-4 text-yellow-500" />;
      case '2g':
      case 'very-slow':
        return <Signal className="w-4 h-4 text-orange-500" />;
      default:
        return <Wifi className="w-4 h-4 text-blue-500" />;
    }
  };

  const getSyncStatusIcon = () => {
    switch (syncStatus) {
      case 'syncing':
        return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getCacheStatusIcon = () => {
    switch (cacheStatus) {
      case 'ready':
        return <HardDrive className="w-4 h-4 text-green-500" />;
      case 'loading':
        return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <HardDrive className="w-4 h-4 text-gray-500" />;
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTime = (date: Date | null) => {
    if (!date) return 'Nunca';
    return new Intl.DateTimeFormat('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date);
  };

  const failedOperations = getFailedOperations();
  const totalSize = getTotalSize();

  if (compact) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        {getNetworkIcon()}
        {pendingOperations > 0 && (
          <div className="flex items-center space-x-1">
            <Clock className="w-3 h-3 text-orange-500" />
            <span className="text-xs text-orange-500">{pendingOperations}</span>
          </div>
        )}
        {getSyncStatusIcon()}
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Header */}
      <div 
        className="p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2">
              {isInstalled ? (
                <Smartphone className="w-5 h-5 text-green-500" />
              ) : (
                <Monitor className="w-5 h-5 text-blue-500" />
              )}
              <h3 className="font-semibold text-gray-900 dark:text-white">
                Status PWA
              </h3>
            </div>
            
            <div className="flex items-center space-x-2">
              {getNetworkIcon()}
              {getSyncStatusIcon()}
              {getCacheStatusIcon()}
              
              {isLowDataMode && (
                <Battery className="w-4 h-4 text-orange-500" title="Modo de dados baixos" />
              )}
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {pendingOperations > 0 && (
              <span className="bg-orange-100 text-orange-800 text-xs px-2 py-1 rounded-full">
                {pendingOperations} pendente(s)
              </span>
            )}
            
            {isExpanded ? (
              <ChevronUp className="w-5 h-5 text-gray-500" />
            ) : (
              <ChevronDown className="w-5 h-5 text-gray-500" />
            )}
          </div>
        </div>
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div className="border-t border-gray-200 dark:border-gray-700">
          {/* Status Grid */}
          <div className="p-4 grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="flex justify-center mb-2">
                {isOnline ? (
                  <Wifi className="w-6 h-6 text-green-500" />
                ) : (
                  <WifiOff className="w-6 h-6 text-red-500" />
                )}
              </div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {isOnline ? 'Online' : 'Offline'}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {networkType !== 'unknown' ? networkType.toUpperCase() : 'Rede'}
              </p>
            </div>

            <div className="text-center">
              <div className="flex justify-center mb-2">
                {getSyncStatusIcon()}
              </div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Sincronização
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {syncStatus === 'idle' ? 'Inativa' : 
                 syncStatus === 'syncing' ? 'Ativa' :
                 syncStatus === 'completed' ? 'Concluída' : 'Erro'}
              </p>
            </div>

            <div className="text-center">
              <div className="flex justify-center mb-2">
                {getCacheStatusIcon()}
              </div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Cache
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {cacheStatus === 'ready' ? 'Pronto' :
                 cacheStatus === 'loading' ? 'Carregando' : 'Erro'}
              </p>
            </div>

            <div className="text-center">
              <div className="flex justify-center mb-2">
                <Clock className="w-6 h-6 text-blue-500" />
              </div>
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                Última Sync
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {formatTime(lastSyncTime)}
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex flex-wrap gap-2">
              {isInstallable && (
                <button
                  onClick={promptInstall}
                  className="flex items-center space-x-2 bg-green-500 hover:bg-green-600 text-white px-3 py-2 rounded-lg text-sm transition-colors duration-200"
                >
                  <Download className="w-4 h-4" />
                  <span>Instalar App</span>
                </button>
              )}
              
              {isUpdateAvailable && (
                <button
                  onClick={updateApp}
                  className="flex items-center space-x-2 bg-blue-500 hover:bg-blue-600 text-white px-3 py-2 rounded-lg text-sm transition-colors duration-200"
                >
                  <RefreshCw className="w-4 h-4" />
                  <span>Atualizar</span>
                </button>
              )}
              
              <button
                onClick={forceSync}
                disabled={!isOnline || isProcessing}
                className="flex items-center space-x-2 bg-purple-500 hover:bg-purple-600 disabled:bg-gray-400 text-white px-3 py-2 rounded-lg text-sm transition-colors duration-200"
              >
                <RefreshCw className={`w-4 h-4 ${isProcessing ? 'animate-spin' : ''}`} />
                <span>Sincronizar</span>
              </button>
              
              {failedOperations.length > 0 && (
                <button
                  onClick={retryAllFailed}
                  className="flex items-center space-x-2 bg-orange-500 hover:bg-orange-600 text-white px-3 py-2 rounded-lg text-sm transition-colors duration-200"
                >
                  <RotateCcw className="w-4 h-4" />
                  <span>Tentar Novamente</span>
                </button>
              )}
              
              <button
                onClick={clearCompleted}
                className="flex items-center space-x-2 bg-gray-500 hover:bg-gray-600 text-white px-3 py-2 rounded-lg text-sm transition-colors duration-200"
              >
                <Trash2 className="w-4 h-4" />
                <span>Limpar</span>
              </button>
              
              <button
                onClick={() => setShowDetails(!showDetails)}
                className="flex items-center space-x-2 bg-indigo-500 hover:bg-indigo-600 text-white px-3 py-2 rounded-lg text-sm transition-colors duration-200"
              >
                <span>Detalhes</span>
                {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Detailed Information */}
          {showDetails && (
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
              <div className="space-y-4">
                {/* Statistics */}
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-2">Estatísticas</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Total de Operações:</span>
                      <span className="ml-2 font-medium text-gray-900 dark:text-white">
                        {detailedOperations.length}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Falhadas:</span>
                      <span className="ml-2 font-medium text-red-600">
                        {failedOperations.length}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Tamanho Total:</span>
                      <span className="ml-2 font-medium text-gray-900 dark:text-white">
                        {formatBytes(totalSize)}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Modo Dados:</span>
                      <span className="ml-2 font-medium text-gray-900 dark:text-white">
                        {isLowDataMode ? 'Baixo' : 'Normal'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Errors */}
                {syncErrors.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Erros Recentes</h4>
                    <div className="space-y-1">
                      {syncErrors.slice(-3).map((error, index) => (
                        <div key={index} className="text-sm text-red-600 bg-red-50 dark:bg-red-900/20 p-2 rounded">
                          {error}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Pending Operations */}
                {detailedOperations.length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Operações Pendentes</h4>
                    <div className="space-y-2 max-h-40 overflow-y-auto">
                      {detailedOperations.slice(0, 5).map((operation) => (
                        <div key={operation.id} className="flex items-center justify-between text-sm bg-white dark:bg-gray-800 p-2 rounded border">
                          <div>
                            <span className="font-medium">{operation.type}</span>
                            <span className="ml-2 text-gray-500 dark:text-gray-400">
                              {new Date(operation.timestamp).toLocaleTimeString('pt-BR')}
                            </span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              operation.status === 'completed' ? 'bg-green-100 text-green-800' :
                              operation.status === 'failed' ? 'bg-red-100 text-red-800' :
                              operation.status === 'processing' ? 'bg-blue-100 text-blue-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {operation.status}
                            </span>
                            {operation.retries > 0 && (
                              <span className="text-xs text-orange-600">
                                {operation.retries} tentativas
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                      {detailedOperations.length > 5 && (
                        <div className="text-center text-sm text-gray-500 dark:text-gray-400">
                          +{detailedOperations.length - 5} mais operações...
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PWAStatus;