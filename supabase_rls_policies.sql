-- SEÇÃO 1: Habilitar RLS para todas as tabelas
ALTER TABLE diagnostics ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- SEÇÃO 2: Políticas para diagnósticos
CREATE POLICY "Usuários podem ver seus próprios diagnósticos" 
    ON diagnostics FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Usuários podem criar diagnósticos" 
    ON diagnostics FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários podem atualizar seus próprios diagnósticos" 
    ON diagnostics FOR UPDATE 
    USING (auth.uid() = user_id);

-- SEÇÃO 3: Políticas para dispositivos
CREATE POLICY "Usuários podem ver seus próprios dispositivos" 
    ON devices FOR SELECT 
    USING (auth.uid() = user_id);

CREATE POLICY "Usuários podem criar dispositivos" 
    ON devices FOR INSERT 
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Usuários podem atualizar seus próprios dispositivos" 
    ON devices FOR UPDATE 
    USING (auth.uid() = user_id);

-- SEÇÃO 4: Políticas para relatórios
CREATE POLICY "Usuários podem ver seus próprios relatórios" 
    ON reports FOR SELECT 
    USING (EXISTS (
        SELECT 1 FROM diagnostics 
        WHERE diagnostics.id = reports.diagnostic_id 
        AND diagnostics.user_id = auth.uid()
    ));

CREATE POLICY "Usuários podem criar relatórios para seus diagnósticos" 
    ON reports FOR INSERT 
    WITH CHECK (EXISTS (
        SELECT 1 FROM diagnostics 
        WHERE diagnostics.id = reports.diagnostic_id 
        AND diagnostics.user_id = auth.uid()
    ));

-- SEÇÃO 5: Políticas para usuários
CREATE POLICY "Usuários podem ver apenas seus próprios dados" 
    ON users FOR SELECT 
    USING (auth.uid() = id);

CREATE POLICY "Usuários podem atualizar apenas seus próprios dados" 
    ON users FOR UPDATE 
    USING (auth.uid() = id);

-- SEÇÃO 6: Verificar políticas aplicadas
SELECT tablename, policyname, permissive, roles, cmd, qual, with_check 
FROM pg_policies 
WHERE schemaname = 'public' 
ORDER BY tablename, policyname;