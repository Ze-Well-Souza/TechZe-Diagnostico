
import React, { createContext, useContext, useEffect, useState } from 'react';
import { User, Session } from '@supabase/supabase-js';
import { supabase } from '@/integrations/supabase/client';

interface Company {
  id: string;
  name: string;
  code: string;
  logo_url?: string;
  primary_color: string;
  subdomain: string;
}

interface AuthContextType {
  user: User | null;
  session: Session | null;
  company: Company | null;
  loading: boolean;
  signIn: (email: string, password: string) => Promise<{ error: any }>;
  signUp: (email: string, password: string, fullName: string) => Promise<{ error: any }>;
  signOut: () => Promise<void>;
  selectCompany: (companyId: string) => Promise<void>;
  refreshSession: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Set up auth state listener FIRST
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.id);
        setSession(session);
        setUser(session?.user ?? null);
        
        if (session?.user) {
          // Defer company loading with setTimeout
          setTimeout(() => {
            loadUserCompany(session.user.id);
          }, 0);
        } else {
          setCompany(null);
        }
        
        setLoading(false);
      }
    );

    // THEN check for existing session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setUser(session?.user ?? null);
      
      if (session?.user) {
        loadUserCompany(session.user.id);
      }
      
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const loadUserCompany = async (userId: string) => {
    try {
      const { data: profile } = await supabase
        .from('profiles')
        .select(`
          current_company_id,
          company_users!inner(
            company:companies(*)
          )
        `)
        .eq('id', userId)
        .single();

      if (profile?.current_company_id && profile.company_users?.[0]?.company) {
        setCompany(profile.company_users[0].company as Company);
      } else {
        // Se não tem empresa atual, buscar a primeira empresa do usuário
        const { data: companies } = await supabase
          .from('company_users')
          .select(`
            company:companies(*)
          `)
          .eq('user_id', userId)
          .eq('is_active', true)
          .limit(1);

        if (companies?.[0]?.company) {
          const firstCompany = companies[0].company as Company;
          setCompany(firstCompany);
          
          // Atualizar como empresa atual
          await supabase
            .from('profiles')
            .update({ current_company_id: firstCompany.id })
            .eq('id', userId);
        }
      }
    } catch (error) {
      console.error('Erro ao carregar empresa do usuário:', error);
    }
  };

  const signIn = async (email: string, password: string) => {
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });
      return { error };
    } catch (error) {
      return { error };
    }
  };

  const signUp = async (email: string, password: string, fullName: string) => {
    try {
      const redirectUrl = `${window.location.origin}/`;
      
      const { error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          emailRedirectTo: redirectUrl,
          data: {
            full_name: fullName,
          }
        }
      });
      return { error };
    } catch (error) {
      return { error };
    }
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    setCompany(null);
  };

  const selectCompany = async (companyId: string) => {
    if (!user) return;
    
    try {
      // Verificar se o usuário tem acesso à empresa
      const { data: companyUser } = await supabase
        .from('company_users')
        .select(`
          company:companies(*)
        `)
        .eq('user_id', user.id)
        .eq('company_id', companyId)
        .eq('is_active', true)
        .single();

      if (companyUser?.company) {
        setCompany(companyUser.company as Company);
        
        // Atualizar empresa atual no perfil
        await supabase
          .from('profiles')
          .update({ current_company_id: companyId })
          .eq('id', user.id);
      }
    } catch (error) {
      console.error('Erro ao selecionar empresa:', error);
    }
  };

  const refreshSession = async () => {
    const { data: { session } } = await supabase.auth.refreshSession();
    setSession(session);
    setUser(session?.user ?? null);
  };

  const value: AuthContextType = {
    user,
    session,
    company,
    loading,
    signIn,
    signUp,
    signOut,
    selectCompany,
    refreshSession,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
