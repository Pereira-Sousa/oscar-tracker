-- ============================================================================
-- PROJETO OSCAR TRACKER (IMD0401 - Banco de Dados - UFRN)
-- CARGA INICIAL (SEED) DE DADOS DE REFERÊNCIA
--
-- Contém:
-- 1. Edições do Oscar (2026 e 2025 para histórico)
-- 2. Gêneros cinematográficos oficiais com TMDB IDs e Pesos da Academia (RN2)
-- 3. Categorias oficiais acompanhadas pelo sistema (RN12, RN15)
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. EDIÇÕES (Temporadas)
-- ----------------------------------------------------------------------------
INSERT INTO edicao (ano_edicao, inicio_elegibilidade, fim_elegibilidade, data_cerimonia)
VALUES 
    (2025, '2024-01-01', '2024-12-31', '2025-03-02'),
    (2026, '2025-01-01', '2025-12-31', '2026-03-08')
ON CONFLICT (ano_edicao) DO UPDATE 
SET inicio_elegibilidade = EXCLUDED.inicio_elegibilidade,
    fim_elegibilidade = EXCLUDED.fim_elegibilidade,
    data_cerimonia = EXCLUDED.data_cerimonia;

-- ----------------------------------------------------------------------------
-- 2. GÊNEROS CINEMATOGRÁFICOS E PESOS DE AFINIDADE COM O OSCAR (RN2)
-- Valores definidos na Seção 2.2 (página 9) do projeto de dados.
-- ----------------------------------------------------------------------------
INSERT INTO genero (tmdb_genre_id, nome, peso_academia)
VALUES
    (18,    'Drama',             1.00),
    (NULL,  'Biografia',         0.90), -- Origem OMDb API
    (36,    'História',          0.80),
    (10752, 'Guerra',            0.70),
    (16,    'Animação',          0.60),
    (99,    'Documentário',      0.60),
    (10402, 'Música',            0.60),
    (10749, 'Romance',           0.60),
    (80,    'Crime',             0.50),
    (9648,  'Mistério',          0.50),
    (53,    'Thriller',          0.50),
    (35,    'Comédia',           0.40),
    (878,   'Ficção científica', 0.40),
    (14,    'Fantasia',          0.40),
    (37,    'Faroeste',          0.40),
    (12,    'Aventura',          0.30),
    (10751, 'Família',           0.30),
    (28,    'Ação',              0.20),
    (27,    'Terror',            0.20),
    (10770, 'Cinema TV',         0.00)
ON CONFLICT (nome) DO UPDATE 
SET tmdb_genre_id = EXCLUDED.tmdb_genre_id,
    peso_academia = EXCLUDED.peso_academia;

-- ----------------------------------------------------------------------------
-- 3. CATEGORIAS DE PREMIAÇÃO OFICIAIS (RN12, RN15)
-- Categorias com janela padrão da temporada (Seção 4.3.1, página 33).
-- ----------------------------------------------------------------------------

-- Categorias de escopo FILME
INSERT INTO categoria (nome, escopo, funcao_exigida)
VALUES
    ('Melhor Filme',                      'FILME', NULL),
    ('Melhor Animação',                   'FILME', NULL),
    ('Melhor Documentário',               'FILME', NULL),
    ('Melhor Canção Original',            'FILME', NULL),
    ('Melhor Som',                        'FILME', NULL),
    ('Melhor Design de Produção',         'FILME', NULL),
    ('Melhor Figurino',                   'FILME', NULL),
    ('Melhor Maquiagem e Penteados',      'FILME', NULL),
    ('Melhores Efeitos Visuais',          'FILME', NULL),
    ('Melhor Escalação de Elenco',        'FILME', NULL)
ON CONFLICT (nome) DO NOTHING;

-- Categorias de escopo INDIVIDUAL (atreladas à função de crédito correspondente)
INSERT INTO categoria (nome, escopo, funcao_exigida)
VALUES
    ('Melhor Direção',                    'INDIVIDUAL', 'DIRETOR'),
    ('Melhor Ator',                       'INDIVIDUAL', 'ELENCO'),
    ('Melhor Atriz',                      'INDIVIDUAL', 'ELENCO'),
    ('Melhor Ator Coadjuvante',           'INDIVIDUAL', 'ELENCO'),
    ('Melhor Atriz Coadjuvante',          'INDIVIDUAL', 'ELENCO'),
    ('Melhor Roteiro Original',           'INDIVIDUAL', 'ROTEIRISTA'),
    ('Melhor Roteiro Adaptado',           'INDIVIDUAL', 'ROTEIRISTA'),
    ('Melhor Fotografia',                 'INDIVIDUAL', 'DIRETOR_FOTOGRAFIA'),
    ('Melhor Montagem',                   'INDIVIDUAL', 'MONTADOR'),
    ('Melhor Trilha Sonora Original',     'INDIVIDUAL', 'COMPOSITOR')
ON CONFLICT (nome) DO NOTHING;
