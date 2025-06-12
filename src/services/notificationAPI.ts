import { supabase } from '@/lib/supabase';
import { Notification as CustomNotification } from '@/hooks/useNotifications';

export interface PushNotificationPayload {
  title: string;
  body: string;
  icon?: string;
  badge?: string;
  tag?: string;
  data?: any;
}

export interface NotificationPreferences {
  userId: string;
  emailNotifications: boolean;
  pushNotifications: boolean;
  smsNotifications: boolean;
  categories: {
    orcamentos: boolean;
    ordemServico: boolean;
    estoque: boolean;
    agendamentos: boolean;
    financeiro: boolean;
  };
}

class NotificationService {
  private swRegistration: ServiceWorkerRegistration | null = null;

  constructor() {
    this.initializeServiceWorker();
  }

  // Inicializar Service Worker para Push Notifications
  private async initializeServiceWorker() {
    if ('serviceWorker' in navigator && 'PushManager' in window) {
      try {
        const registration = await navigator.serviceWorker.register('/sw.js');
        this.swRegistration = registration;
        console.log('Service Worker registrado com sucesso');
      } catch (error) {
        console.error('Erro ao registrar Service Worker:', error);
      }
    }
  }

  // Solicitar permissão para notificações
  async requestNotificationPermission(): Promise<boolean> {
    if (!('Notification' in window)) {
      console.warn('Este navegador não suporta notificações');
      return false;
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    if (Notification.permission === 'denied') {
      return false;
    }

    const permission = await Notification.requestPermission();
    return permission === 'granted';
  }

  // Enviar notificação push local
  async sendLocalNotification(payload: PushNotificationPayload): Promise<void> {
    const hasPermission = await this.requestNotificationPermission();
    
    if (!hasPermission) {
      console.warn('Permissão para notificações negada');
      return;
    }

    const notification = new Notification(payload.title, {
      body: payload.body,
      icon: payload.icon || '/icon-192x192.png',
      badge: payload.badge || '/icon-72x72.png',
      tag: payload.tag,
      data: payload.data,
      requireInteraction: true,
    });

    notification.onclick = () => {
      window.focus();
      notification.close();
      
      // Navegar para página específica se houver dados
      if (payload.data?.url) {
        window.location.href = payload.data.url;
      }
    };
  }

  // Subscrever para push notifications do servidor
  async subscribeToPushNotifications(userId: string): Promise<boolean> {
    if (!this.swRegistration) {
      console.error('Service Worker não está registrado');
      return false;
    }

    try {
      const subscription = await this.swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: this.urlBase64ToUint8Array(
          process.env.VITE_VAPID_PUBLIC_KEY || ''
        ),
      });

      // Salvar subscription no banco de dados
      const { error } = await supabase
        .from('push_subscriptions')
        .upsert({
          user_id: userId,
          subscription: JSON.stringify(subscription),
          created_at: new Date().toISOString(),
        });

      if (error) {
        console.error('Erro ao salvar subscription:', error);
        return false;
      }

      return true;
    } catch (error) {
      console.error('Erro ao subscrever para push notifications:', error);
      return false;
    }
  }

  // Converter VAPID key
  private urlBase64ToUint8Array(base64String: string): Uint8Array {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding)
      .replace(/-/g, '+')
      .replace(/_/g, '/');

    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);

    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }

  // Buscar notificações do usuário
  async getUserNotifications(userId: string): Promise<CustomNotification[]> {
    try {
      const { data, error } = await supabase
        .from('notifications')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(50);

      if (error) {
        console.error('Erro ao buscar notificações:', error);
        return [];
      }

      return data.map(item => ({
        id: item.id,
        type: item.type,
        title: item.title,
        message: item.message,
        createdAt: new Date(item.created_at),
        persistent: item.persistent || false,
      }));
    } catch (error) {
      console.error('Erro ao buscar notificações:', error);
      return [];
    }
  }

  // Marcar notificação como lida
  async markNotificationAsRead(notificationId: string): Promise<boolean> {
    try {
      const { error } = await supabase
        .from('notifications')
        .update({ read_at: new Date().toISOString() })
        .eq('id', notificationId);

      return !error;
    } catch (error) {
      console.error('Erro ao marcar notificação como lida:', error);
      return false;
    }
  }

  // Buscar preferências de notificação
  async getNotificationPreferences(userId: string): Promise<NotificationPreferences | null> {
    try {
      const { data, error } = await supabase
        .from('notification_preferences')
        .select('*')
        .eq('user_id', userId)
        .single();

      if (error && error.code !== 'PGRST116') {
        console.error('Erro ao buscar preferências:', error);
        return null;
      }

      return data || {
        userId,
        emailNotifications: true,
        pushNotifications: true,
        smsNotifications: false,
        categories: {
          orcamentos: true,
          ordemServico: true,
          estoque: true,
          agendamentos: true,
          financeiro: true,
        },
      };
    } catch (error) {
      console.error('Erro ao buscar preferências:', error);
      return null;
    }
  }

  // Atualizar preferências de notificação
  async updateNotificationPreferences(
    preferences: NotificationPreferences
  ): Promise<boolean> {
    try {
      const { error } = await supabase
        .from('notification_preferences')
        .upsert({
          user_id: preferences.userId,
          email_notifications: preferences.emailNotifications,
          push_notifications: preferences.pushNotifications,
          sms_notifications: preferences.smsNotifications,
          categories: preferences.categories,
          updated_at: new Date().toISOString(),
        });

      return !error;
    } catch (error) {
      console.error('Erro ao atualizar preferências:', error);
      return false;
    }
  }

  // Enviar notificação específica do sistema
  async sendSystemNotification(
    type: 'orcamento_aprovado' | 'os_concluida' | 'estoque_baixo' | 'agendamento_confirmado',
    data: any
  ): Promise<void> {
    const templates = {
      orcamento_aprovado: {
        title: 'Orçamento Aprovado! 🎉',
        body: `Orçamento #${data.numero} foi aprovado pelo cliente`,
        icon: '/icons/success.png',
        tag: 'orcamento',
        data: { url: `/orcamentos/${data.id}` },
      },
      os_concluida: {
        title: 'Ordem de Serviço Concluída ✅',
        body: `OS #${data.numero} foi finalizada com sucesso`,
        icon: '/icons/completed.png',
        tag: 'ordem_servico',
        data: { url: `/ordem-servico/${data.id}` },
      },
      estoque_baixo: {
        title: 'Estoque Baixo ⚠️',
        body: `${data.item} está com estoque baixo (${data.quantidade} unidades)`,
        icon: '/icons/warning.png',
        tag: 'estoque',
        data: { url: '/estoque' },
      },
      agendamento_confirmado: {
        title: 'Agendamento Confirmado 📅',
        body: `Agendamento para ${data.data} às ${data.hora} confirmado`,
        icon: '/icons/calendar.png',
        tag: 'agendamento',
        data: { url: '/agendamento' },
      },
    };

    const template = templates[type];
    if (template) {
      await this.sendLocalNotification(template);
    }
  }
}

export const notificationService = new NotificationService();
export default notificationService;