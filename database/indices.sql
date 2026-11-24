-- ============================================================================
-- PROJETO OSCAR TRACKER (IMD0401 - Banco de Dados - UFRN)
-- ÍNDICES DE PERFORMANCE E OTIMIZAÇÃO (PostgreSQL 16)
--
-- Projetados especificamente para suportar as consultas do catálogo de funções:
-- C1: consultar_linha_do_tempo
-- C2: obter_ficha_tecnica_filme
-- C3: listar_radar_por_categoria
-- C4: listar_opcoes_de_filtro
-- ============================================================================

-- ----------------------------------------------------------------------------
-- ÍNDICES PARA CONSULTA C1 (consultar_linha_do_tempo)
-- Consulta de alta frequência para exibição e filtragem dos cards no painel.
-- ----------------------------------------------------------------------------

-- Ordenação padrão pelo Oscar Buzz Score dentro da edição selecionada
CREATE INDEX idx_filme_edicao_buzz 
    ON filme (ano_edicao, oscar_buzz_score DESC);

-- Ordenação cronológica por data de estreia dentro da edição selecionada
CREATE INDEX idx_filme_edicao_release 
    ON filme (ano_edicao, release_date ASC);

-- Filtro combinado por plataforma de streaming e modalidade (flatrate, rent, buy)
CREATE INDEX idx_disponibilidade_provider_mod 
    ON disponibilidade (provider_id, modalidade);

-- Filtro por gênero cinematográfico
CREATE INDEX idx_filme_genero_genero 
    ON filme_genero (id_genero);

-- ----------------------------------------------------------------------------
-- ÍNDICES PARA CONSULTA C2 (obter_ficha_tecnica_filme)
-- Acionada na abertura do modal com os dados consolidados da obra.
-- ----------------------------------------------------------------------------

-- Busca de créditos e ordenação do elenco principal do filme
CREATE INDEX idx_credito_filme_funcao_ordem 
    ON credito (tmdb_id, funcao, ordem_elenco ASC NULLS LAST);

-- Busca rápida de plataformas e ofertas associadas ao filme
CREATE INDEX idx_disponibilidade_filme 
    ON disponibilidade (tmdb_id);

-- Busca das candidaturas e prêmios vinculados ao filme
CREATE INDEX idx_candidatura_filme 
    ON candidatura (tmdb_id);

-- ----------------------------------------------------------------------------
-- ÍNDICES PARA CONSULTA C3 (listar_radar_por_categoria)
-- Consulta para exibir os cotados, indicados e vencedores por categoria.
-- ----------------------------------------------------------------------------

-- Busca das candidaturas ativas filtradas por categoria e status competitivo
CREATE INDEX idx_candidatura_cat_status 
    ON candidatura (id_categoria, status);

-- ----------------------------------------------------------------------------
-- ÍNDICES PARA ROTINAS DE CARGA E TRANSAÇÕES (A5, A6, A7, A8)
-- ----------------------------------------------------------------------------

-- Otimização do join e busca durante a atualização de avaliações da OMDb
CREATE INDEX idx_filme_imdb_id 
    ON filme (imdb_id) 
    WHERE imdb_id IS NOT NULL;
