-- Script para configuração inicial do banco Supabase
-- Execute este script no SQL Editor do Supabase

-- 1. Tabela de Lojas (criar primeiro para referências)
CREATE TABLE IF NOT EXISTS lojas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    endereco TEXT,
    cidade VARCHAR(100),
    estado VARCHAR(2),
    telefone VARCHAR(20),
    email VARCHAR(255),
    admin_id UUID,
    status VARCHAR(20) DEFAULT 'ativa' CHECK (status IN ('ativa', 'inativa', 'manutencao')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Tabela de Usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('master_admin', 'admin_loja', 'tecnico')),
    loja_id UUID REFERENCES lojas(id) ON DELETE SET NULL,
    ativo BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Tabela de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefone VARCHAR(20),
    empresa VARCHAR(255),
    endereco TEXT,
    loja_id UUID REFERENCES lojas(id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'ativo' CHECK (status IN ('ativo', 'inativo', 'pendente')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Tabela de Diagnósticos
CREATE TABLE IF NOT EXISTS diagnosticos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    cliente_id UUID REFERENCES clientes(id) ON DELETE CASCADE,
    loja_id UUID REFERENCES lojas(id) ON DELETE CASCADE,
    dispositivo_tipo VARCHAR(100),
    dispositivo_modelo VARCHAR(100),
    problemas JSONB,
    health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
    status VARCHAR(20) DEFAULT 'em_andamento' CHECK (status IN ('em_andamento', 'concluido', 'cancelado')),
    tecnico_id UUID REFERENCES usuarios(id) ON DELETE SET NULL,
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Adicionando Foreign Key para admin_id em lojas
ALTER TABLE lojas ADD CONSTRAINT fk_lojas_admin 
    FOREIGN KEY (admin_id) REFERENCES usuarios(id) ON DELETE SET NULL;

-- 6. Criando índices para performance
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios(tipo);
CREATE INDEX IF NOT EXISTS idx_usuarios_loja ON usuarios(loja_id);
CREATE INDEX IF NOT EXISTS idx_clientes_loja ON clientes(loja_id);
CREATE INDEX IF NOT EXISTS idx_clientes_status ON clientes(status);
CREATE INDEX IF NOT EXISTS idx_diagnosticos_loja ON diagnosticos(loja_id);
CREATE INDEX IF NOT EXISTS idx_diagnosticos_cliente ON diagnosticos(cliente_id);
CREATE INDEX IF NOT EXISTS idx_diagnosticos_status ON diagnosticos(status);
CREATE INDEX IF NOT EXISTS idx_diagnosticos_created ON diagnosticos(created_at);

-- 7. Inserindo dados iniciais
INSERT INTO lojas (nome, endereco, cidade, estado, telefone, email, status) VALUES
('TechRepair Centro', 'Av. Paulista, 1000', 'São Paulo', 'SP', '(11) 9999-1111', 'centro@techrepair.com', 'ativa'),
('TechRepair Norte', 'Rua das Flores, 500', 'São Paulo', 'SP', '(11) 9999-2222', 'norte@techrepair.com', 'ativa'),
('TechRepair Sul', 'Av. dos Estados, 200', 'São Paulo', 'SP', '(11) 9999-3333', 'sul@techrepair.com', 'ativa');

-- 8. Inserindo usuário administrador master
INSERT INTO usuarios (email, nome, tipo, ativo) VALUES
('admin@techrepair.com', 'Administrador Master', 'master_admin', true);

-- 9. Inserindo administradores de loja
INSERT INTO usuarios (email, nome, tipo, loja_id, ativo) 
SELECT 
    'admin.' || LOWER(REPLACE(l.nome, ' ', '')) || '@techrepair.com',
    'Admin ' || l.nome,
    'admin_loja',
    l.id,
    true
FROM lojas l;

-- 10. Atualizando admin_id nas lojas
UPDATE lojas SET admin_id = (
    SELECT u.id FROM usuarios u 
    WHERE u.loja_id = lojas.id AND u.tipo = 'admin_loja' 
    LIMIT 1
);

-- 11. Inserindo clientes de exemplo
INSERT INTO clientes (nome, email, telefone, empresa, loja_id, status) 
SELECT 
    'Cliente ' || generate_series(1, 10),
    'cliente' || generate_series(1, 10) || '@email.com',
    '(11) 9999-' || LPAD(generate_series(1, 10)::text, 4, '0'),
    'Empresa ' || generate_series(1, 10),
    l.id,
    CASE 
        WHEN generate_series(1, 10) % 10 = 0 THEN 'pendente'
        WHEN generate_series(1, 10) % 8 = 0 THEN 'inativo'
        ELSE 'ativo'
    END
FROM lojas l, generate_series(1, 10);

-- 12. Inserindo diagnósticos de exemplo
INSERT INTO diagnosticos (cliente_id, loja_id, dispositivo_tipo, dispositivo_modelo, problemas, health_score, status, tecnico_id)
SELECT 
    c.id,
    c.loja_id,
    'Smartphone',
    'iPhone 12',
    '["Tela quebrada", "Bateria viciada"]'::jsonb,
    (RANDOM() * 100)::integer,
    CASE 
        WHEN RANDOM() > 0.8 THEN 'concluido'
        WHEN RANDOM() > 0.9 THEN 'cancelado'
        ELSE 'em_andamento'
    END,
    u.id
FROM clientes c
JOIN usuarios u ON u.loja_id = c.loja_id AND u.tipo = 'admin_loja'
WHERE RANDOM() > 0.3; -- 70% dos clientes têm diagnósticos

-- 13. Função para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 14. Triggers para atualizar updated_at
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_lojas_updated_at BEFORE UPDATE ON lojas 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clientes_updated_at BEFORE UPDATE ON clientes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_diagnosticos_updated_at BEFORE UPDATE ON diagnosticos 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 15. Configurações de segurança (RLS - Row Level Security)
ALTER TABLE usuarios ENABLE ROW LEVEL SECURITY;
ALTER TABLE lojas ENABLE ROW LEVEL SECURITY;
ALTER TABLE clientes ENABLE ROW LEVEL SECURITY;
ALTER TABLE diagnosticos ENABLE ROW LEVEL SECURITY;

-- 16. Políticas de segurança básicas
-- Política para usuários: podem ver apenas seus próprios dados
CREATE POLICY "Users can view own data" ON usuarios 
    FOR SELECT USING (auth.uid()::text = id::text);

-- Política para lojas: admins podem ver suas lojas
CREATE POLICY "Admins can view their stores" ON lojas 
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM usuarios 
            WHERE usuarios.id::text = auth.uid()::text 
            AND (usuarios.tipo = 'master_admin' OR usuarios.loja_id = lojas.id)
        )
    );

-- Política para clientes: podem ser vistos por usuários da mesma loja
CREATE POLICY "Store users can view store clients" ON clientes 
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM usuarios 
            WHERE usuarios.id::text = auth.uid()::text 
            AND (usuarios.tipo = 'master_admin' OR usuarios.loja_id = clientes.loja_id)
        )
    );

-- Política para diagnósticos: podem ser vistos por usuários da mesma loja
CREATE POLICY "Store users can view store diagnostics" ON diagnosticos 
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM usuarios 
            WHERE usuarios.id::text = auth.uid()::text 
            AND (usuarios.tipo = 'master_admin' OR usuarios.loja_id = diagnosticos.loja_id)
        )
    );

-- 17. Views para estatísticas
CREATE OR REPLACE VIEW v_estatisticas_globais AS
SELECT 
    (SELECT COUNT(*) FROM lojas WHERE status = 'ativa') as total_lojas_ativas,
    (SELECT COUNT(*) FROM clientes WHERE status = 'ativo') as total_clientes_ativos,
    (SELECT COUNT(*) FROM diagnosticos) as total_diagnosticos,
    (SELECT ROUND(AVG(health_score)) FROM diagnosticos WHERE health_score IS NOT NULL) as health_score_medio,
    (SELECT COUNT(*) FROM diagnosticos WHERE created_at >= CURRENT_DATE) as diagnosticos_hoje,
    (SELECT COUNT(*) FROM diagnosticos WHERE created_at >= CURRENT_DATE - INTERVAL '7 days') as diagnosticos_semana,
    (SELECT COUNT(*) FROM diagnosticos WHERE created_at >= CURRENT_DATE - INTERVAL '30 days') as diagnosticos_mes;

-- Mensagem de sucesso
SELECT 'Configuração básica concluída!' as status; 