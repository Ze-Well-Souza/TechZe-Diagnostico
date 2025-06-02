-- =============================================================================
-- POLÍTICAS RLS PARA TECHZE DIAGNÓSTICO 
-- Execute este script no SQL Editor do Supabase
-- =============================================================================

-- 1. TABELA DIAGNOSTICS
-- Remover políticas existentes se houver
DROP POLICY IF EXISTS "Users can view own diagnostics" ON diagnostics;
DROP POLICY IF EXISTS "Users can insert own diagnostics" ON diagnostics;
DROP POLICY IF EXISTS "Users can update own diagnostics" ON diagnostics;
DROP POLICY IF EXISTS "Admins can view all diagnostics" ON diagnostics;

-- Criar novas políticas para diagnostics
CREATE POLICY "Users can view own diagnostics" ON diagnostics
    FOR SELECT USING (
        auth.uid() = user_id OR 
        EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.raw_user_meta_data->>'role' = 'admin')
    );

CREATE POLICY "Users can insert own diagnostics" ON diagnostics
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own diagnostics" ON diagnostics
    FOR UPDATE USING (
        auth.uid() = user_id OR 
        EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.raw_user_meta_data->>'role' = 'admin')
    );

CREATE POLICY "Admins can delete diagnostics" ON diagnostics
    FOR DELETE USING (
        EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.raw_user_meta_data->>'role' = 'admin')
    );

-- 2. TABELA DEVICES
-- Remover políticas existentes se houver
DROP POLICY IF EXISTS "Users can view own devices" ON devices;
DROP POLICY IF EXISTS "Users can insert own devices" ON devices;
DROP POLICY IF EXISTS "Users can update own devices" ON devices;
DROP POLICY IF EXISTS "Admins can view all devices" ON devices;

-- Criar novas políticas para devices
CREATE POLICY "Users can view own devices" ON devices
    FOR SELECT USING (
        auth.uid() = user_id OR 
        EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.raw_user_meta_data->>'role' = 'admin')
    );

CREATE POLICY "Users can insert own devices" ON devices
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own devices" ON devices
    FOR UPDATE USING (
        auth.uid() = user_id OR 
        EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.raw_user_meta_data->>'role' = 'admin')
    );

CREATE POLICY "Admins can delete devices" ON devices
    FOR DELETE USING (
        EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.raw_user_meta_data->>'role' = 'admin')
    );

-- 3. TABELA REPORTS
-- Remover políticas existentes se houver
DROP POLICY IF EXISTS "Users can view own reports" ON reports;
DROP POLICY IF EXISTS "Users can insert own reports" ON reports;
DROP POLICY IF EXISTS "Admins can view all reports" ON reports;

-- Criar novas políticas para reports
CREATE POLICY "Users can view own reports" ON reports
    FOR SELECT USING (
        auth.uid() = user_id OR 
        EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.raw_user_meta_data->>'role' = 'admin')
    );

CREATE POLICY "Users can insert own reports" ON reports
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Admins can delete reports" ON reports
    FOR DELETE USING (
        EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.raw_user_meta_data->>'role' = 'admin')
    );

-- 4. TABELA USERS (perfil público)
-- Remover políticas existentes se houver
DROP POLICY IF EXISTS "Users can view own profile" ON users;
DROP POLICY IF EXISTS "Users can update own profile" ON users;
DROP POLICY IF EXISTS "Admins can view all users" ON users;

-- Criar novas políticas para users
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (
        auth.uid() = id OR 
        EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.raw_user_meta_data->>'role' = 'admin')
    );

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Admins can manage all users" ON users
    FOR ALL USING (
        EXISTS (SELECT 1 FROM auth.users WHERE auth.users.id = auth.uid() AND auth.users.raw_user_meta_data->>'role' = 'admin')
    );

-- 5. MANTER POLÍTICAS EXISTENTES PARA COMPANIES E COMPANY_USERS (já estão configuradas)

-- =============================================================================
-- HABILITAR RLS EM TODAS AS TABELAS
-- =============================================================================

-- Habilitar RLS nas tabelas principais
ALTER TABLE diagnostics ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Verificar se as políticas foram criadas
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check 
FROM pg_policies 
WHERE schemaname = 'public' 
ORDER BY tablename, policyname;

-- =============================================================================
-- CRIAR FUNÇÕES AUXILIARES PARA AUTORIZAÇÃO
-- =============================================================================

-- Função para verificar se o usuário é admin
CREATE OR REPLACE FUNCTION is_admin()
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1 FROM auth.users 
        WHERE auth.users.id = auth.uid() 
        AND auth.users.raw_user_meta_data->>'role' = 'admin'
    );
$$;

-- Função para verificar se o usuário é técnico
CREATE OR REPLACE FUNCTION is_technician()
RETURNS BOOLEAN
LANGUAGE sql
SECURITY DEFINER
STABLE
AS $$
    SELECT EXISTS (
        SELECT 1 FROM auth.users 
        WHERE auth.users.id = auth.uid() 
        AND (
            auth.users.raw_user_meta_data->>'role' = 'admin' OR
            auth.users.raw_user_meta_data->>'role' = 'technician'
        )
    );
$$;

-- =============================================================================
-- INSERIR DADOS DE TESTE (OPCIONAL)
-- =============================================================================

-- Inserir usuário admin de teste (executar apenas se necessário)
-- INSERT INTO auth.users (id, email, raw_user_meta_data) 
-- VALUES (
--     gen_random_uuid(),
--     'admin@techze.com',
--     '{"role": "admin", "name": "Administrador"}'::jsonb
-- );

-- =============================================================================
-- VERIFICAÇÃO FINAL
-- =============================================================================

-- Verificar todas as políticas criadas
SELECT 
    tablename,
    policyname,
    cmd as operation,
    CASE 
        WHEN cmd = 'SELECT' THEN 'Ver/Listar'
        WHEN cmd = 'INSERT' THEN 'Criar'
        WHEN cmd = 'UPDATE' THEN 'Atualizar'
        WHEN cmd = 'DELETE' THEN 'Deletar'
        WHEN cmd = 'ALL' THEN 'Todas as operações'
    END as descricao
FROM pg_policies 
WHERE schemaname = 'public' 
AND tablename IN ('diagnostics', 'devices', 'reports', 'users')
ORDER BY tablename, cmd;

-- Verificar se RLS está habilitado
SELECT 
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
AND tablename IN ('diagnostics', 'devices', 'reports', 'users', 'companies', 'company_users');

COMMENT ON FUNCTION is_admin() IS 'Verifica se o usuário atual tem permissões de administrador';
COMMENT ON FUNCTION is_technician() IS 'Verifica se o usuário atual tem permissões de técnico ou superior'; 