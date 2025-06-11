-- Criação da tabela de auditoria para o TechZe Diagnóstico
-- Esta tabela armazena logs de auditoria para todas as ações importantes no sistema

-- Cria o schema public se não existir (normalmente já existe)
CREATE SCHEMA IF NOT EXISTS public;

-- Cria a tabela de auditoria
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    user_id UUID,
    session_id TEXT,
    ip_address TEXT,
    user_agent TEXT,
    endpoint TEXT,
    method TEXT,
    resource_id TEXT,
    resource_type TEXT,
    action TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    duration_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Comentários para documentação
COMMENT ON TABLE public.audit_logs IS 'Logs de auditoria para rastreamento de ações no sistema';
COMMENT ON COLUMN public.audit_logs.id IS 'Identificador único do log de auditoria';
COMMENT ON COLUMN public.audit_logs.timestamp IS 'Data e hora em que o evento ocorreu';
COMMENT ON COLUMN public.audit_logs.event_type IS 'Tipo de evento (login, diagnóstico, etc.)';
COMMENT ON COLUMN public.audit_logs.severity IS 'Severidade do evento (low, medium, high, critical)';
COMMENT ON COLUMN public.audit_logs.user_id IS 'ID do usuário que realizou a ação (se autenticado)';
COMMENT ON COLUMN public.audit_logs.session_id IS 'ID da sessão do usuário';
COMMENT ON COLUMN public.audit_logs.ip_address IS 'Endereço IP de origem';
COMMENT ON COLUMN public.audit_logs.user_agent IS 'Navegador/aplicativo do usuário';
COMMENT ON COLUMN public.audit_logs.endpoint IS 'Endpoint da API acessado';
COMMENT ON COLUMN public.audit_logs.method IS 'Método HTTP (GET, POST, etc.)';
COMMENT ON COLUMN public.audit_logs.resource_id IS 'ID do recurso afetado pela ação';
COMMENT ON COLUMN public.audit_logs.resource_type IS 'Tipo de recurso afetado (user, diagnostic, etc.)';
COMMENT ON COLUMN public.audit_logs.action IS 'Ação realizada';
COMMENT ON COLUMN public.audit_logs.details IS 'Detalhes adicionais em formato JSON';
COMMENT ON COLUMN public.audit_logs.success IS 'Indica se a ação foi bem-sucedida';
COMMENT ON COLUMN public.audit_logs.error_message IS 'Mensagem de erro, se houver';
COMMENT ON COLUMN public.audit_logs.duration_ms IS 'Duração da operação em milissegundos';
COMMENT ON COLUMN public.audit_logs.created_at IS 'Data e hora em que o log foi criado no banco';

-- Cria índices para consultas eficientes
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON public.audit_logs (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON public.audit_logs (event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type ON public.audit_logs (resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_success ON public.audit_logs (success);
CREATE INDEX IF NOT EXISTS idx_audit_logs_severity ON public.audit_logs (severity);
CREATE INDEX IF NOT EXISTS idx_audit_logs_ip_address ON public.audit_logs (ip_address);

-- Habilita Row Level Security
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Políticas de RLS para auditoria
-- Somente administradores podem ver todos os logs
CREATE POLICY admin_audit_policy ON public.audit_logs
    FOR ALL
    TO authenticated
    USING (auth.jwt() ->> 'role' = 'admin');

-- Usuários podem ver apenas seus próprios logs de auditoria
CREATE POLICY user_audit_policy ON public.audit_logs
    FOR SELECT
    TO authenticated
    USING (user_id::text = (auth.uid())::text);

-- Função para pesquisa de logs de auditoria
CREATE OR REPLACE FUNCTION search_audit_logs(
    p_user_id UUID DEFAULT NULL,
    p_event_type TEXT DEFAULT NULL,
    p_start_date TIMESTAMPTZ DEFAULT NULL,
    p_end_date TIMESTAMPTZ DEFAULT NULL,
    p_resource_type TEXT DEFAULT NULL,
    p_success BOOLEAN DEFAULT NULL,
    p_severity TEXT DEFAULT NULL,
    p_limit INTEGER DEFAULT 100,
    p_offset INTEGER DEFAULT 0
) 
RETURNS SETOF audit_logs
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT *
    FROM audit_logs
    WHERE 
        (p_user_id IS NULL OR user_id = p_user_id) AND
        (p_event_type IS NULL OR event_type = p_event_type) AND
        (p_start_date IS NULL OR timestamp >= p_start_date) AND
        (p_end_date IS NULL OR timestamp <= p_end_date) AND
        (p_resource_type IS NULL OR resource_type = p_resource_type) AND
        (p_success IS NULL OR success = p_success) AND
        (p_severity IS NULL OR severity = p_severity)
    ORDER BY timestamp DESC
    LIMIT p_limit
    OFFSET p_offset;
END;
$$; 