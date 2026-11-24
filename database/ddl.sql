-- ============================================================================
-- PROJETO OSCAR TRACKER (IMD0401 - Banco de Dados - UFRN)
-- ESQUEMA RELACIONAL DDL (PostgreSQL 16)
--
-- Normalização: Todas as relações estão na Terceira Forma Normal (3FN).
-- Atributos multivalorados foram decompostos em relações auxiliares (1FN).
-- Todas as dependências funcionais partem exclusivamente de chaves candidatas.
-- ============================================================================

-- Limpeza de objetos existentes (ordem reversa de dependências)
DROP TABLE IF EXISTS candidatura CASCADE;
DROP TABLE IF EXISTS credito CASCADE;
DROP TABLE IF EXISTS profissional CASCADE;
DROP TABLE IF EXISTS disponibilidade CASCADE;
DROP TABLE IF EXISTS plataforma CASCADE;
DROP TABLE IF EXISTS filme_genero CASCADE;
DROP TABLE IF EXISTS genero CASCADE;
DROP TABLE IF EXISTS filme_pais_origem CASCADE;
DROP TABLE IF EXISTS filme CASCADE;
DROP TABLE IF EXISTS edicao CASCADE;

-- ============================================================================
-- 1. TABELA: edicao
-- Representa a temporada anual da premiação com sua janela de elegibilidade.
-- Regras atendidas: RN8, RN14.
-- ============================================================================
CREATE TABLE edicao (
    ano_edicao INT PRIMARY KEY,
    inicio_elegibilidade DATE NOT NULL,
    fim_elegibilidade DATE NOT NULL,
    data_cerimonia DATE NOT NULL,
    CONSTRAINT chk_edicao_ordem_datas CHECK (
        inicio_elegibilidade < fim_elegibilidade AND 
        fim_elegibilidade < data_cerimonia
    )
);

COMMENT ON TABLE edicao IS 'Temporada anual do Oscar com janela de elegibilidade e data da cerimônia.';
COMMENT ON COLUMN edicao.ano_edicao IS 'Ano de referência da premiação (ex: 2026).';

-- ============================================================================
-- 2. TABELA: filme
-- Longa-metragem elegível à edição do Oscar monitorada.
-- Regras atendidas: RN1, RN7, RN8, RN14, RN15.
-- 3FN: Todos os atributos não-chave dependem exclusivamente de tmdb_id.
-- Atributo multivalorado 'paises_origem' decomposto em filme_pais_origem.
-- Atributo 'status_lancamento' é derivado (release_date x CURRENT_DATE).
-- ============================================================================
CREATE TABLE filme (
    tmdb_id INT PRIMARY KEY,
    imdb_id VARCHAR(20) UNIQUE,
    titulo VARCHAR(255) NOT NULL,
    titulo_original VARCHAR(255) NOT NULL,
    sinopse TEXT,
    poster_path VARCHAR(255),
    release_date DATE NOT NULL,
    duracao_min INT CHECK (duracao_min > 0),
    popularidade NUMERIC(10, 3) NOT NULL DEFAULT 0.000 CHECK (popularidade >= 0),
    imdb_rating NUMERIC(3, 1) CHECK (imdb_rating BETWEEN 0.0 AND 10.0),
    metascore INT CHECK (metascore BETWEEN 0 AND 100),
    premios_texto TEXT,
    oscar_buzz_score NUMERIC(5, 2) NOT NULL DEFAULT 0.00 CHECK (oscar_buzz_score BETWEEN 0.00 AND 100.00),
    ano_edicao INT NOT NULL,
    CONSTRAINT fk_filme_edicao FOREIGN KEY (ano_edicao)
        REFERENCES edicao (ano_edicao)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);

COMMENT ON TABLE filme IS 'Longas-metragens participantes ou cotados para a temporada do Oscar.';
COMMENT ON COLUMN filme.release_date IS 'Data de estreia comercial nos EUA utilizada pela Academia para elegibilidade.';
COMMENT ON COLUMN filme.oscar_buzz_score IS 'Atributo derivado e materializado para fins de ordenação de consultas frequentes (0.00 a 100.00).';

-- ============================================================================
-- 3. TABELA: filme_pais_origem
-- Decomposição do atributo multivalorado paises_origem (garante 1FN e 3FN).
-- ============================================================================
CREATE TABLE filme_pais_origem (
    tmdb_id INT NOT NULL,
    codigo_pais VARCHAR(10) NOT NULL,
    PRIMARY KEY (tmdb_id, codigo_pais),
    CONSTRAINT fk_filme_pais_filme FOREIGN KEY (tmdb_id)
        REFERENCES filme (tmdb_id)
        ON DELETE CASCADE
);

COMMENT ON TABLE filme_pais_origem IS 'Países de origem do filme (decomposição 1FN do atributo multivalorado).';

-- ============================================================================
-- 4. TABELA: genero
-- Gêneros cinematográficos e peso de afinidade com o histórico da Academia.
-- Regras atendidas: RN2.
-- ============================================================================
CREATE TABLE genero (
    id_genero INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tmdb_genre_id INT UNIQUE,
    nome VARCHAR(50) NOT NULL UNIQUE,
    peso_academia NUMERIC(3, 2) NOT NULL DEFAULT 0.50 CHECK (peso_academia BETWEEN 0.00 AND 1.00)
);

COMMENT ON TABLE genero IS 'Classificação cinematográfica e peso de afinidade histórica com o Oscar.';
COMMENT ON COLUMN genero.tmdb_genre_id IS 'Identificador do gênero na TMDB (nulo apenas para Biografia, oriundo da OMDb).';

-- ============================================================================
-- 5. TABELA: filme_genero
-- Relacionamento N:M "Classificado em" entre FILME e GÊNERO.
-- Regras atendidas: RN2 (todo filme deve ter no mínimo 1 gênero).
-- ============================================================================
CREATE TABLE filme_genero (
    tmdb_id INT NOT NULL,
    id_genero INT NOT NULL,
    PRIMARY KEY (tmdb_id, id_genero),
    CONSTRAINT fk_filme_genero_filme FOREIGN KEY (tmdb_id)
        REFERENCES filme (tmdb_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_filme_genero_genero FOREIGN KEY (id_genero)
        REFERENCES genero (id_genero)
        ON DELETE RESTRICT
);

COMMENT ON TABLE filme_genero IS 'Vínculo N:M entre filmes e gêneros cinematográficos.';

-- ============================================================================
-- 6. TABELA: plataforma
-- Provedores de streaming atuantes no mercado brasileiro.
-- Regras atendidas: RN3, RN4.
-- ============================================================================
CREATE TABLE plataforma (
    provider_id INT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    logo_path VARCHAR(255)
);

COMMENT ON TABLE plataforma IS 'Serviços de streaming disponíveis no Brasil cadastrados no TMDB/JustWatch.';

-- ============================================================================
-- 7. TABELA: disponibilidade
-- Entidade associativa / fraca entre FILME e PLATAFORMA.
-- Representa a oferta atual no catálogo brasileiro em determinada modalidade.
-- Regras atendidas: RN3, RN4.
-- 3FN: Identificada por (tmdb_id, provider_id, modalidade).
-- ============================================================================
CREATE TABLE disponibilidade (
    tmdb_id INT NOT NULL,
    provider_id INT NOT NULL,
    modalidade VARCHAR(20) NOT NULL,
    data_coleta DATE NOT NULL DEFAULT CURRENT_DATE,
    PRIMARY KEY (tmdb_id, provider_id, modalidade),
    CONSTRAINT chk_disponibilidade_modalidade CHECK (
        modalidade IN ('ASSINATURA', 'ALUGUEL', 'COMPRA')
    ),
    CONSTRAINT fk_disp_filme FOREIGN KEY (tmdb_id)
        REFERENCES filme (tmdb_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_disp_plataforma FOREIGN KEY (provider_id)
        REFERENCES plataforma (provider_id)
        ON DELETE RESTRICT
);

COMMENT ON TABLE disponibilidade IS 'Oferta atual de um filme em uma plataforma de streaming no Brasil.';

-- ============================================================================
-- 8. TABELA: profissional
-- Integrantes do elenco ou da equipe técnica (diretores, roteiristas, etc.).
-- Regras atendidas: RN9.
-- ============================================================================
CREATE TABLE profissional (
    tmdb_person_id INT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    profile_path VARCHAR(255),
    known_for_department VARCHAR(100)
);

COMMENT ON TABLE profissional IS 'Profissionais do meio cinematográfico registrados na base.';

-- ============================================================================
-- 9. TABELA: credito
-- Entidade fraca dependente de FILME e PROFISSIONAL.
-- Regras atendidas: RN10, RN11.
-- Restrição: character_name obrigatório para ELENCO e proibido para as demais.
-- ============================================================================
CREATE TABLE credito (
    tmdb_id INT NOT NULL,
    tmdb_person_id INT NOT NULL,
    funcao VARCHAR(30) NOT NULL,
    character_name VARCHAR(255),
    credit_id VARCHAR(50),
    ordem_elenco INT,
    PRIMARY KEY (tmdb_id, tmdb_person_id, funcao),
    CONSTRAINT chk_credito_funcao CHECK (
        funcao IN (
            'ELENCO',
            'DIRETOR',
            'ROTEIRISTA',
            'PRODUTOR',
            'COMPOSITOR',
            'DIRETOR_FOTOGRAFIA',
            'MONTADOR'
        )
    ),
    CONSTRAINT chk_credito_personagem_elenco CHECK (
        (funcao = 'ELENCO' AND character_name IS NOT NULL) OR 
        (funcao <> 'ELENCO' AND character_name IS NULL)
    ),
    CONSTRAINT fk_credito_filme FOREIGN KEY (tmdb_id)
        REFERENCES filme (tmdb_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_credito_profissional FOREIGN KEY (tmdb_person_id)
        REFERENCES profissional (tmdb_person_id)
        ON DELETE RESTRICT
);

COMMENT ON TABLE credito IS 'Participação de um profissional em uma obra exercendo função técnica ou artística.';

-- ============================================================================
-- 10. TABELA: categoria
-- Categorias oficiais da premiação do Oscar acompanhadas pelo sistema.
-- Regras atendidas: RN12, RN15.
-- Restrição: escopo INDIVIDUAL exige funcao_exigida; escopo FILME exige nulo.
-- ============================================================================
CREATE TABLE categoria (
    id_categoria INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    escopo VARCHAR(15) NOT NULL,
    funcao_exigida VARCHAR(30),
    CONSTRAINT chk_categoria_escopo CHECK (
        escopo IN ('FILME', 'INDIVIDUAL')
    ),
    CONSTRAINT chk_categoria_funcao_valida CHECK (
        funcao_exigida IS NULL OR funcao_exigida IN (
            'ELENCO',
            'DIRETOR',
            'ROTEIRISTA',
            'PRODUTOR',
            'COMPOSITOR',
            'DIRETOR_FOTOGRAFIA',
            'MONTADOR'
        )
    ),
    CONSTRAINT chk_categoria_coerencia_escopo CHECK (
        (escopo = 'INDIVIDUAL' AND funcao_exigida IS NOT NULL) OR
        (escopo = 'FILME' AND funcao_exigida IS NULL)
    )
);

COMMENT ON TABLE categoria IS 'Categorias da premiação classificadas por escopo (FILME ou INDIVIDUAL).';

-- ============================================================================
-- 11. TABELA: candidatura
-- Entidade fraca dependente de FILME e CATEGORIA (com profissional opcional).
-- Regras atendidas: RN5, RN6, RN13.
-- Unicidade parcial:
--   - Escopo FILME: par (tmdb_id, id_categoria) é único.
--   - Escopo INDIVIDUAL: tripla (tmdb_id, id_categoria, tmdb_person_id) é única.
-- ============================================================================
CREATE TABLE candidatura (
    tmdb_id INT NOT NULL,
    id_categoria INT NOT NULL,
    seq_candidatura INT NOT NULL CHECK (seq_candidatura > 0),
    tmdb_person_id INT,
    status VARCHAR(15) NOT NULL DEFAULT 'COTADO',
    PRIMARY KEY (tmdb_id, id_categoria, seq_candidatura),
    CONSTRAINT chk_candidatura_status CHECK (
        status IN ('COTADO', 'INDICADO', 'VENCEDOR')
    ),
    CONSTRAINT fk_candidatura_filme FOREIGN KEY (tmdb_id)
        REFERENCES filme (tmdb_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_candidatura_categoria FOREIGN KEY (id_categoria)
        REFERENCES categoria (id_categoria)
        ON DELETE RESTRICT,
    CONSTRAINT fk_candidatura_profissional FOREIGN KEY (tmdb_person_id)
        REFERENCES profissional (tmdb_person_id)
        ON DELETE RESTRICT
);

-- Restrições de Unicidade Parciais (Seção 3.5 do projeto de dados)
CREATE UNIQUE INDEX uq_candidatura_filme 
    ON candidatura (tmdb_id, id_categoria) 
    WHERE tmdb_person_id IS NULL;

CREATE UNIQUE INDEX uq_candidatura_individual 
    ON candidatura (tmdb_id, id_categoria, tmdb_person_id) 
    WHERE tmdb_person_id IS NOT NULL;

COMMENT ON TABLE candidatura IS 'Posição competitiva de um filme ou profissional em uma categoria da premiação.';
