import { createClient } from '@supabase/supabase-js';

const supabaseUrl = 'https://waxnnwpsvitmeeivkwkn.supabase.co';
const supabaseAnonKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndheG5ud3Bzdml0bWVlaXZrd2tuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg2MTA1MDcsImV4cCI6MjA2NDE4NjUwN30.faxEG4xqXXW9eJv6MLkLl6UEU6dayz336Qqak_1nlII';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Tipos para o banco de dados
export interface Usuario {
  id: string;
  email: string;
  nome: string;
  tipo: 'master_admin' | 'admin_loja' | 'tecnico';
  loja_id?: string;
  ativo: boolean;
  created_at: string;
  updated_at: string;
}

export interface Loja {
  id: string;
  nome: string;
  endereco: string;
  cidade: string;
  estado: string;
  telefone: string;
  email: string;
  admin_id: string;
  status: 'ativa' | 'inativa' | 'manutencao';
  created_at: string;
  updated_at: string;
}

export interface Cliente {
  id: string;
  nome: string;
  email: string;
  telefone: string;
  empresa?: string;
  endereco?: string;
  loja_id: string;
  status: 'ativo' | 'inativo' | 'pendente';
  created_at: string;
  updated_at: string;
}

export interface Diagnostico {
  id: string;
  cliente_id: string;
  loja_id: string;
  dispositivo_tipo: string;
  dispositivo_modelo: string;
  problemas: string[];
  health_score: number;
  status: 'em_andamento' | 'concluido' | 'cancelado';
  tecnico_id: string;
  observacoes?: string;
  created_at: string;
  updated_at: string;
}

// Serviços de autenticação
export const authService = {
  async signIn(email: string, password: string) {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });
    return { data, error };
  },

  async signOut() {
    const { error } = await supabase.auth.signOut();
    return { error };
  },

  async getCurrentUser() {
    const { data: { user }, error } = await supabase.auth.getUser();
    return { user, error };
  },

  async getUserProfile(userId: string): Promise<{ data: Usuario | null, error: any }> {
    const { data, error } = await supabase
      .from('usuarios')
      .select('*')
      .eq('id', userId)
      .single();
    return { data, error };
  }
};

// Serviços de lojas
export const lojasService = {
  async getLojas(): Promise<{ data: Loja[] | null, error: any }> {
    const { data, error } = await supabase
      .from('lojas')
      .select('*')
      .order('nome');
    return { data, error };
  },

  async createLoja(loja: Omit<Loja, 'id' | 'created_at' | 'updated_at'>) {
    const { data, error } = await supabase
      .from('lojas')
      .insert(loja)
      .select()
      .single();
    return { data, error };
  },

  async updateLoja(id: string, updates: Partial<Loja>) {
    const { data, error } = await supabase
      .from('lojas')
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq('id', id)
      .select()
      .single();
    return { data, error };
  },

  async deleteLoja(id: string) {
    const { error } = await supabase
      .from('lojas')
      .delete()
      .eq('id', id);
    return { error };
  }
};

// Serviços de clientes
export const clientesService = {
  async getClientes(lojaId?: string): Promise<{ data: Cliente[] | null, error: any }> {
    let query = supabase
      .from('clientes')
      .select('*')
      .order('nome');
      
    if (lojaId) {
      query = query.eq('loja_id', lojaId);
    }
    
    const { data, error } = await query;
    return { data, error };
  },

  async createCliente(cliente: Omit<Cliente, 'id' | 'created_at' | 'updated_at'>) {
    const { data, error } = await supabase
      .from('clientes')
      .insert(cliente)
      .select()
      .single();
    return { data, error };
  },

  async updateCliente(id: string, updates: Partial<Cliente>) {
    const { data, error } = await supabase
      .from('clientes')
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq('id', id)
      .select()
      .single();
    return { data, error };
  },

  async deleteCliente(id: string) {
    const { error } = await supabase
      .from('clientes')
      .delete()
      .eq('id', id);
    return { error };
  }
};

// Serviços de diagnósticos
export const diagnosticosService = {
  async getDiagnosticos(lojaId?: string): Promise<{ data: Diagnostico[] | null, error: any }> {
    let query = supabase
      .from('diagnosticos')
      .select(`
        *,
        cliente:clientes(nome, email, telefone),
        loja:lojas(nome),
        tecnico:usuarios(nome)
      `)
      .order('created_at', { ascending: false });
      
    if (lojaId) {
      query = query.eq('loja_id', lojaId);
    }
    
    const { data, error } = await query;
    return { data, error };
  },

  async createDiagnostico(diagnostico: Omit<Diagnostico, 'id' | 'created_at' | 'updated_at'>) {
    const { data, error } = await supabase
      .from('diagnosticos')
      .insert(diagnostico)
      .select()
      .single();
    return { data, error };
  },

  async updateDiagnostico(id: string, updates: Partial<Diagnostico>) {
    const { data, error } = await supabase
      .from('diagnosticos')
      .update({ ...updates, updated_at: new Date().toISOString() })
      .eq('id', id)
      .select()
      .single();
    return { data, error };
  }
};

// Estatísticas globais
export const statsService = {
  async getGlobalStats() {
    // Buscar contagens de cada tabela
    const [lojasCount, clientesCount, diagnosticosCount] = await Promise.all([
      supabase.from('lojas').select('id', { count: 'exact', head: true }),
      supabase.from('clientes').select('id', { count: 'exact', head: true }),
      supabase.from('diagnosticos').select('id', { count: 'exact', head: true })
    ]);

    // Buscar health scores para calcular média
    const { data: diagnosticos } = await supabase
      .from('diagnosticos')
      .select('health_score');

    const avgHealthScore = diagnosticos && diagnosticos.length > 0
      ? diagnosticos.reduce((sum, d) => sum + (d.health_score || 0), 0) / diagnosticos.length
      : 0;

    return {
      totalLojas: lojasCount.count || 0,
      totalClientes: clientesCount.count || 0,
      totalDiagnosticos: diagnosticosCount.count || 0,
      avgHealthScore: Math.round(avgHealthScore)
    };
  },

  async getLojaStats(lojaId: string) {
    const [clientesCount, diagnosticosCount] = await Promise.all([
      supabase.from('clientes').select('id', { count: 'exact', head: true }).eq('loja_id', lojaId),
      supabase.from('diagnosticos').select('id', { count: 'exact', head: true }).eq('loja_id', lojaId)
    ]);

    const { data: diagnosticos } = await supabase
      .from('diagnosticos')
      .select('health_score')
      .eq('loja_id', lojaId);

    const avgHealthScore = diagnosticos && diagnosticos.length > 0
      ? diagnosticos.reduce((sum, d) => sum + (d.health_score || 0), 0) / diagnosticos.length
      : 0;

    return {
      totalClientes: clientesCount.count || 0,
      totalDiagnosticos: diagnosticosCount.count || 0,
      avgHealthScore: Math.round(avgHealthScore)
    };
  }
}; 