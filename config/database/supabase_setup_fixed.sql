-- =====================================================
-- SETUP COMPLETO SUPABASE - POSTGRESQL SYNTAX CORRIGIDO
-- =====================================================

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- TABELAS PRINCIPAIS
-- =====================================================

-- Tabela de usuários
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de dispositivos
CREATE TABLE IF NOT EXISTS public.devices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50),
    os_info TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de diagnósticos
CREATE TABLE IF NOT EXISTS public.diagnostics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    device_id UUID REFERENCES public.devices(id) ON DELETE CASCADE,
    diagnostic_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de relatórios
CREATE TABLE IF NOT EXISTS public.reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    diagnostic_id UUID NOT NULL REFERENCES public.diagnostics(id) ON DELETE CASCADE,
    report_type VARCHAR(20) NOT NULL,
    file_path TEXT,
    file_size INTEGER DEFAULT 0,
    content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- HABILITAR ROW LEVEL SECURITY
-- =====================================================

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.diagnostics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- POLÍTICAS DE SEGURANÇA
-- =====================================================

-- Políticas para diagnósticos
CREATE POLICY "users_can_view_own_diagnostics" 
    ON public.diagnostics FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "users_can_create_diagnostics" 
    ON public.diagnostics FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "users_can_update_own_diagnostics" 
    ON public.diagnostics FOR UPDATE 
    USING (auth.uid() = user_id);

-- Políticas para dispositivos
CREATE POLICY "users_can_view_own_devices" 
    ON public.devices FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "users_can_create_devices" 
    ON public.devices FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "users_can_update_own_devices" 
    ON public.devices FOR UPDATE 
    USING (auth.uid() = user_id);

-- Políticas para relatórios
CREATE POLICY "users_can_view_own_reports" 
    ON public.reports FOR SELECT 
    USING (
        EXISTS (
            SELECT 1 FROM public.diagnostics 
            WHERE diagnostics.id = reports.diagnostic_id 
            AND diagnostics.user_id = auth.uid()
        )
    );

CREATE POLICY "users_can_create_reports" 
    ON public.reports FOR INSERT 
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.diagnostics 
            WHERE diagnostics.id = reports.diagnostic_id 
            AND diagnostics.user_id = auth.uid()
        )
    );

-- Políticas para usuários
CREATE POLICY "users_can_view_own_profile" 
    ON public.users FOR SELECT 
    USING (auth.uid() = id);

CREATE POLICY "users_can_update_own_profile" 
    ON public.users FOR UPDATE 
    USING (auth.uid() = id);

-- =====================================================
-- ÍNDICES PARA PERFORMANCE
-- =====================================================

CREATE INDEX IF NOT EXISTS idx_devices_user_id ON public.devices(user_id);
CREATE INDEX IF NOT EXISTS idx_diagnostics_user_id ON public.diagnostics(user_id);
CREATE INDEX IF NOT EXISTS idx_diagnostics_device_id ON public.diagnostics(device_id);
CREATE INDEX IF NOT EXISTS idx_diagnostics_status ON public.diagnostics(status);
CREATE INDEX IF NOT EXISTS idx_reports_diagnostic_id ON public.reports(diagnostic_id);
CREATE INDEX IF NOT EXISTS idx_diagnostics_created_at ON public.diagnostics(created_at);

-- =====================================================
-- TRIGGERS PARA UPDATED_AT
-- =====================================================

-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualizar updated_at automaticamente
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON public.users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_devices_updated_at 
    BEFORE UPDATE ON public.devices 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_diagnostics_updated_at 
    BEFORE UPDATE ON public.diagnostics 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- DADOS DE EXEMPLO (OPCIONAL)
-- =====================================================

-- Inserir usuário de teste (apenas se não existir)
INSERT INTO public.users (id, email) 
VALUES ('00000000-0000-0000-0000-000000000001', 'test@techreparo.com')
ON CONFLICT (email) DO NOTHING;

-- =====================================================
-- VERIFICAÇÃO FINAL
-- =====================================================

-- Verificar se todas as tabelas foram criadas
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
        RAISE EXCEPTION 'Tabela users não foi criada';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'devices') THEN
        RAISE EXCEPTION 'Tabela devices não foi criada';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'diagnostics') THEN
        RAISE EXCEPTION 'Tabela diagnostics não foi criada';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'reports') THEN
        RAISE EXCEPTION 'Tabela reports não foi criada';
    END IF;
    
    RAISE NOTICE 'Setup do banco de dados concluído com sucesso!';
END $$;