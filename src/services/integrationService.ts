
import { zendeskCircuitBreaker, notasFiscaisCircuitBreaker, emailCircuitBreaker } from '@/integrations/circuitBreaker';
import { AuditService } from './auditService';

export interface ZendeskTicket {
  subject: string;
  description: string;
  priority: 'low' | 'normal' | 'high' | 'urgent';
  type: 'problem' | 'incident' | 'question' | 'task';
  tags: string[];
  customFields?: Record<string, any>;
}

export interface NotaFiscal {
  valor: number;
  descricao: string;
  clienteId: string;
  servicoId: string;
  items: Array<{
    descricao: string;
    quantidade: number;
    valorUnitario: number;
  }>;
}

export class IntegrationService {
  // Integração com Zendesk
  static async createZendeskTicket(ticket: ZendeskTicket, diagnosticId: string): Promise<string> {
    return zendeskCircuitBreaker.execute(async () => {
      const response = await fetch('/api/zendesk/tickets', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...ticket,
          custom_fields: {
            diagnostic_id: diagnosticId,
            source: 'techze_diagnostic'
          }
        })
      });

      if (!response.ok) {
        throw new Error(`Erro Zendesk: ${response.status}`);
      }

      const result = await response.json();
      
      await AuditService.logAction('ZENDESK_TICKET_CREATED', 'DIAGNOSTIC', diagnosticId, {
        ticketId: result.ticket.id,
        subject: ticket.subject
      });

      return result.ticket.id;
    });
  }

  // Integração com sistema de Notas Fiscais
  static async emitirNotaFiscal(nota: NotaFiscal, diagnosticId: string): Promise<string> {
    return notasFiscaisCircuitBreaker.execute(async () => {
      const response = await fetch('/api/notas-fiscais', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...nota,
          metadata: {
            diagnostic_id: diagnosticId,
            origem: 'techze_diagnostic'
          }
        })
      });

      if (!response.ok) {
        throw new Error(`Erro Nota Fiscal: ${response.status}`);
      }

      const result = await response.json();

      await AuditService.logAction('NOTA_FISCAL_EMITIDA', 'DIAGNOSTIC', diagnosticId, {
        notaFiscalId: result.id,
        valor: nota.valor
      });

      return result.numero;
    });
  }

  // Envio de email
  static async sendEmail(to: string, subject: string, body: string, diagnosticId?: string): Promise<void> {
    return emailCircuitBreaker.execute(async () => {
      const response = await fetch('/api/email/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to,
          subject,
          html: body,
          metadata: diagnosticId ? { diagnostic_id: diagnosticId } : undefined
        })
      });

      if (!response.ok) {
        throw new Error(`Erro Email: ${response.status}`);
      }

      if (diagnosticId) {
        await AuditService.logAction('EMAIL_SENT', 'DIAGNOSTIC', diagnosticId, {
          to,
          subject
        });
      }
    });
  }

  // Webhooks para integração com CRMs
  static async sendWebhook(url: string, data: any, eventType: string): Promise<void> {
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-TechZe-Event': eventType,
          'X-TechZe-Signature': await this.generateSignature(data)
        },
        body: JSON.stringify({
          event: eventType,
          timestamp: new Date().toISOString(),
          data
        })
      });

      if (!response.ok) {
        throw new Error(`Webhook failed: ${response.status}`);
      }

      console.log(`Webhook enviado: ${eventType} para ${url}`);
    } catch (error) {
      console.error('Erro ao enviar webhook:', error);
      throw error;
    }
  }

  private static async generateSignature(data: any): Promise<string> {
    // Implementar assinatura HMAC para segurança
    const encoder = new TextEncoder();
    const keyData = encoder.encode(process.env.WEBHOOK_SECRET || 'default-secret');
    const message = encoder.encode(JSON.stringify(data));
    
    const key = await crypto.subtle.importKey(
      'raw',
      keyData,
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign']
    );
    
    const signature = await crypto.subtle.sign('HMAC', key, message);
    return Array.from(new Uint8Array(signature))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
  }
}
