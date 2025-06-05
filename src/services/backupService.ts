
import { supabase } from '@/integrations/supabase/client';
import { AuditService } from './auditService';

export class BackupService {
  static async createBackup(companyId: string): Promise<string> {
    try {
      console.log(`Iniciando backup para empresa ${companyId}`);

      // Backup dos dados principais
      const [devices, diagnostics, reports] = await Promise.all([
        this.exportTable('devices', companyId),
        this.exportTable('diagnostics', companyId),
        this.exportTable('reports', companyId)
      ]);

      const backupData = {
        timestamp: new Date().toISOString(),
        company_id: companyId,
        data: {
          devices,
          diagnostics,
          reports
        },
        metadata: {
          version: '1.0.0',
          total_records: devices.length + diagnostics.length + reports.length
        }
      };

      // Salvar backup no Supabase Storage (se configurado)
      const backupFileName = `backup_${companyId}_${Date.now()}.json`;
      const { data, error } = await supabase.storage
        .from('backups')
        .upload(backupFileName, JSON.stringify(backupData, null, 2));

      if (error) {
        console.warn('Storage não configurado, salvando backup localmente');
        this.downloadBackup(backupFileName, backupData);
      }

      await AuditService.logAction('BACKUP_CREATED', 'COMPANY', companyId, {
        fileName: backupFileName,
        recordCount: backupData.metadata.total_records
      });

      return backupFileName;

    } catch (error) {
      console.error('Erro ao criar backup:', error);
      throw error;
    }
  }

  private static async exportTable(tableName: string, companyId: string): Promise<any[]> {
    const { data, error } = await supabase
      .from(tableName)
      .select('*')
      .eq('company_id', companyId);

    if (error) {
      console.error(`Erro ao exportar tabela ${tableName}:`, error);
      return [];
    }

    return data || [];
  }

  private static downloadBackup(fileName: string, data: any): void {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  static async scheduleAutomaticBackups(companyId: string, intervalHours: number = 24): Promise<void> {
    // Registrar tarefa de backup automático
    if ('serviceWorker' in navigator && 'sync' in window) {
      const registration = await navigator.serviceWorker.ready;
      
      if ('sync' in registration) {
        await registration.sync.register(`auto-backup-${companyId}`);
        console.log(`Backup automático agendado para empresa ${companyId} a cada ${intervalHours}h`);
      }
    }

    // Fallback: usar setInterval no navegador
    setInterval(async () => {
      try {
        await this.createBackup(companyId);
        console.log(`Backup automático executado para empresa ${companyId}`);
      } catch (error) {
        console.error('Erro no backup automático:', error);
      }
    }, intervalHours * 60 * 60 * 1000);
  }
}
