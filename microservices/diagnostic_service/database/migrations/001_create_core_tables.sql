-- Criação das tabelas principais do TechZe Diagnóstico
-- Data: 2025-01-06
-- Versão: 1.0.0

-- Habilitar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Criar esquemas
CREATE SCHEMA IF NOT EXISTS techze;

-- ===========================
-- TABELAS DE CONFIGURAÇÃO
-- ===========================

-- Tabela de configurações da loja
CREATE TABLE techze.configuracoes_loja (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_loja VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18),
    endereco JSONB,
    telefone VARCHAR(20),
    email VARCHAR(255),
    logo_url VARCHAR(500),
    configuracoes JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================
-- TABELAS DE USUÁRIOS E RBAC
-- ===========================

-- Tabela de usuários (técnicos, administradores)
CREATE TABLE techze.usuarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    telefone VARCHAR(20),
    role VARCHAR(50) DEFAULT 'tecnico',
    permissions JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    ultimo_login TIMESTAMP WITH TIME ZONE,
    configuracoes JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================
-- TABELAS DE CLIENTES
-- ===========================

-- Tabela de clientes
CREATE TABLE techze.clientes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    cpf VARCHAR(14),
    cnpj VARCHAR(18),
    email VARCHAR(255),
    telefone VARCHAR(20) NOT NULL,
    endereco JSONB,
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================
-- TABELAS DE ESTOQUE
-- ===========================

-- Tabela de fornecedores
CREATE TABLE techze.fornecedores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome VARCHAR(255) NOT NULL,
    cnpj VARCHAR(18),
    email VARCHAR(255),
    telefone VARCHAR(20),
    endereco JSONB,
    contato_principal VARCHAR(255),
    observacoes TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de itens de estoque
CREATE TABLE techze.estoque_itens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    codigo VARCHAR(100) UNIQUE NOT NULL,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) NOT NULL, -- 'peca', 'ferramenta', 'consumivel'
    categoria VARCHAR(100),
    marca VARCHAR(100),
    modelo VARCHAR(100),
    fornecedor_id UUID REFERENCES techze.fornecedores(id),
    quantidade_atual INTEGER DEFAULT 0,
    quantidade_minima INTEGER DEFAULT 0,
    quantidade_maxima INTEGER DEFAULT 1000,
    unidade_medida VARCHAR(20) DEFAULT 'unidade',
    preco_custo DECIMAL(10,2),
    preco_venda DECIMAL(10,2),
    margem_lucro DECIMAL(5,2),
    localizacao VARCHAR(100),
    data_validade DATE,
    observacoes TEXT,
    status VARCHAR(50) DEFAULT 'ativo', -- 'ativo', 'inativo', 'descontinuado'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de movimentações de estoque
CREATE TABLE techze.estoque_movimentacoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id UUID NOT NULL REFERENCES techze.estoque_itens(id),
    tipo VARCHAR(50) NOT NULL, -- 'entrada', 'saida', 'ajuste', 'transferencia'
    quantidade INTEGER NOT NULL,
    motivo VARCHAR(255),
    origem VARCHAR(255),
    destino VARCHAR(255),
    documento VARCHAR(100),
    valor_unitario DECIMAL(10,2),
    valor_total DECIMAL(10,2),
    usuario_id UUID REFERENCES techze.usuarios(id),
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================
-- TABELAS DE ORÇAMENTOS
-- ===========================

-- Tabela principal de orçamentos
CREATE TABLE techze.orcamentos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero VARCHAR(20) UNIQUE NOT NULL,
    cliente_id UUID NOT NULL REFERENCES techze.clientes(id),
    dados_cliente JSONB NOT NULL,
    dados_equipamento JSONB NOT NULL,
    problema_relatado TEXT,
    diagnostico_tecnico TEXT,
    observacoes TEXT,
    valor_pecas DECIMAL(10,2) DEFAULT 0,
    valor_servicos DECIMAL(10,2) DEFAULT 0,
    valor_desconto DECIMAL(10,2) DEFAULT 0,
    valor_total DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pendente', -- 'pendente', 'aprovado', 'rejeitado', 'vencido'
    data_validade DATE,
    data_aprovacao TIMESTAMP WITH TIME ZONE,
    assinatura_digital TEXT,
    ip_aprovacao INET,
    condicoes_pagamento JSONB,
    prioridade VARCHAR(50) DEFAULT 'normal', -- 'baixa', 'normal', 'alta', 'urgente'
    tempo_estimado INTEGER, -- em horas
    garantia_dias INTEGER DEFAULT 90,
    usuario_id UUID REFERENCES techze.usuarios(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de itens de orçamento (serviços)
CREATE TABLE techze.orcamento_itens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    orcamento_id UUID NOT NULL REFERENCES techze.orcamentos(id) ON DELETE CASCADE,
    tipo VARCHAR(50) NOT NULL, -- 'servico', 'diagnostico'
    descricao VARCHAR(500) NOT NULL,
    quantidade INTEGER DEFAULT 1,
    valor_unitario DECIMAL(10,2) NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    tempo_estimado INTEGER, -- em minutos
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de peças de orçamento
CREATE TABLE techze.orcamento_pecas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    orcamento_id UUID NOT NULL REFERENCES techze.orcamentos(id) ON DELETE CASCADE,
    item_estoque_id UUID REFERENCES techze.estoque_itens(id),
    codigo_peca VARCHAR(100),
    nome_peca VARCHAR(255) NOT NULL,
    quantidade INTEGER NOT NULL,
    valor_unitario DECIMAL(10,2) NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================
-- TABELAS DE ORDEM DE SERVIÇO
-- ===========================

-- Tabela principal de ordens de serviço
CREATE TABLE techze.ordens_servico (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero VARCHAR(20) UNIQUE NOT NULL,
    cliente_id UUID NOT NULL REFERENCES techze.clientes(id),
    orcamento_id UUID REFERENCES techze.orcamentos(id),
    tecnico_id UUID REFERENCES techze.usuarios(id),
    dados_cliente JSONB NOT NULL,
    dados_equipamento JSONB NOT NULL,
    problema_relatado TEXT NOT NULL,
    diagnostico TEXT,
    solucao_aplicada TEXT,
    status VARCHAR(50) DEFAULT 'nova', -- 'nova', 'em_andamento', 'aguardando_peca', 'aguardando_cliente', 'finalizada', 'cancelada'
    prioridade VARCHAR(50) DEFAULT 'normal', -- 'baixa', 'normal', 'alta', 'urgente'
    data_entrada TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    data_inicio TIMESTAMP WITH TIME ZONE,
    data_conclusao TIMESTAMP WITH TIME ZONE,
    data_entrega TIMESTAMP WITH TIME ZONE,
    valor_total DECIMAL(10,2) DEFAULT 0,
    status_pagamento VARCHAR(50) DEFAULT 'pendente', -- 'pendente', 'pago', 'parcial'
    garantia_dias INTEGER DEFAULT 90,
    data_vencimento_garantia DATE,
    avaliacao_cliente INTEGER, -- 1 a 5
    comentario_cliente TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de serviços prestados na OS
CREATE TABLE techze.os_servicos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ordem_servico_id UUID NOT NULL REFERENCES techze.ordens_servico(id) ON DELETE CASCADE,
    descricao VARCHAR(500) NOT NULL,
    quantidade INTEGER DEFAULT 1,
    valor_unitario DECIMAL(10,2) NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    tempo_gasto INTEGER, -- em minutos
    tecnico_id UUID REFERENCES techze.usuarios(id),
    data_execucao TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de peças utilizadas na OS
CREATE TABLE techze.os_pecas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ordem_servico_id UUID NOT NULL REFERENCES techze.ordens_servico(id) ON DELETE CASCADE,
    item_estoque_id UUID REFERENCES techze.estoque_itens(id),
    codigo_peca VARCHAR(100),
    nome_peca VARCHAR(255) NOT NULL,
    quantidade INTEGER NOT NULL,
    valor_unitario DECIMAL(10,2) NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    observacoes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de anotações da OS
CREATE TABLE techze.os_anotacoes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ordem_servico_id UUID NOT NULL REFERENCES techze.ordens_servico(id) ON DELETE CASCADE,
    usuario_id UUID NOT NULL REFERENCES techze.usuarios(id),
    tipo VARCHAR(50) DEFAULT 'observacao', -- 'observacao', 'diagnostico', 'solucao'
    conteudo TEXT NOT NULL,
    is_private BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabela de fotos da OS
CREATE TABLE techze.os_fotos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ordem_servico_id UUID NOT NULL REFERENCES techze.ordens_servico(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    descricao VARCHAR(255),
    tipo VARCHAR(50) DEFAULT 'geral', -- 'antes', 'durante', 'depois', 'problema', 'solucao'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ===========================
-- ÍNDICES PARA PERFORMANCE
-- ===========================

-- Índices para clientes
CREATE INDEX idx_clientes_email ON techze.clientes(email);
CREATE INDEX idx_clientes_telefone ON techze.clientes(telefone);
CREATE INDEX idx_clientes_nome ON techze.clientes(nome);

-- Índices para usuários
CREATE INDEX idx_usuarios_email ON techze.usuarios(email);
CREATE INDEX idx_usuarios_role ON techze.usuarios(role);

-- Índices para estoque
CREATE INDEX idx_estoque_codigo ON techze.estoque_itens(codigo);
CREATE INDEX idx_estoque_nome ON techze.estoque_itens(nome);
CREATE INDEX idx_estoque_fornecedor ON techze.estoque_itens(fornecedor_id);
CREATE INDEX idx_movimentacoes_item ON techze.estoque_movimentacoes(item_id);
CREATE INDEX idx_movimentacoes_data ON techze.estoque_movimentacoes(created_at);

-- Índices para orçamentos
CREATE INDEX idx_orcamentos_numero ON techze.orcamentos(numero);
CREATE INDEX idx_orcamentos_cliente ON techze.orcamentos(cliente_id);
CREATE INDEX idx_orcamentos_status ON techze.orcamentos(status);
CREATE INDEX idx_orcamentos_data ON techze.orcamentos(created_at);

-- Índices para ordens de serviço
CREATE INDEX idx_os_numero ON techze.ordens_servico(numero);
CREATE INDEX idx_os_cliente ON techze.ordens_servico(cliente_id);
CREATE INDEX idx_os_tecnico ON techze.ordens_servico(tecnico_id);
CREATE INDEX idx_os_status ON techze.ordens_servico(status);
CREATE INDEX idx_os_data_entrada ON techze.ordens_servico(data_entrada);

-- ===========================
-- TRIGGERS PARA UPDATED_AT
-- ===========================

-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para tabelas com updated_at
CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON techze.usuarios
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_clientes_updated_at BEFORE UPDATE ON techze.clientes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fornecedores_updated_at BEFORE UPDATE ON techze.fornecedores
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_estoque_itens_updated_at BEFORE UPDATE ON techze.estoque_itens
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_orcamentos_updated_at BEFORE UPDATE ON techze.orcamentos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ordens_servico_updated_at BEFORE UPDATE ON techze.ordens_servico
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ===========================
-- VIEWS ÚTEIS
-- ===========================

-- View para estoque com informações do fornecedor
CREATE OR REPLACE VIEW techze.vw_estoque_completo AS
SELECT 
    ei.*,
    f.nome as fornecedor_nome,
    f.telefone as fornecedor_telefone,
    CASE 
        WHEN ei.quantidade_atual <= ei.quantidade_minima THEN 'critico'
        WHEN ei.quantidade_atual <= (ei.quantidade_minima * 1.5) THEN 'baixo'
        ELSE 'normal'
    END as status_estoque
FROM techze.estoque_itens ei
LEFT JOIN techze.fornecedores f ON ei.fornecedor_id = f.id;

-- View para orçamentos com dados do cliente
CREATE OR REPLACE VIEW techze.vw_orcamentos_completos AS
SELECT 
    o.*,
    c.nome as cliente_nome,
    c.telefone as cliente_telefone,
    c.email as cliente_email,
    u.nome as usuario_nome
FROM techze.orcamentos o
JOIN techze.clientes c ON o.cliente_id = c.id
LEFT JOIN techze.usuarios u ON o.usuario_id = u.id;

-- View para ordens de serviço completas
CREATE OR REPLACE VIEW techze.vw_os_completas AS
SELECT 
    os.*,
    c.nome as cliente_nome,
    c.telefone as cliente_telefone,
    t.nome as tecnico_nome,
    o.numero as orcamento_numero
FROM techze.ordens_servico os
JOIN techze.clientes c ON os.cliente_id = c.id
LEFT JOIN techze.usuarios t ON os.tecnico_id = t.id
LEFT JOIN techze.orcamentos o ON os.orcamento_id = o.id;

-- ===========================
-- DADOS INICIAIS
-- ===========================

-- Configuração inicial da loja
INSERT INTO techze.configuracoes_loja (nome_loja, configuracoes) VALUES 
('TechZe Diagnóstico', '{"timezone": "America/Sao_Paulo", "moeda": "BRL", "idioma": "pt-BR"}');

-- Usuário administrador padrão
INSERT INTO techze.usuarios (email, nome, role, permissions, is_active) VALUES 
('admin@techze.com', 'Administrador', 'admin', '["*"]', true);

-- Comentários nas tabelas
COMMENT ON TABLE techze.clientes IS 'Cadastro de clientes da loja';
COMMENT ON TABLE techze.usuarios IS 'Usuários do sistema (técnicos, admin)';
COMMENT ON TABLE techze.estoque_itens IS 'Itens do estoque (peças, ferramentas, consumíveis)';
COMMENT ON TABLE techze.orcamentos IS 'Orçamentos gerados para os clientes';
COMMENT ON TABLE techze.ordens_servico IS 'Ordens de serviço para reparos';

COMMIT; 