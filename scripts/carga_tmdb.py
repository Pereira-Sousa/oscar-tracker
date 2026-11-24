import httpx
from typing import Dict, List, Any, Optional
from scripts.buzz_score import calcular_oscar_buzz_score

TMDB_BASE_URL = "https://api.themoviedb.org/3"

def obter_headers(api_key: str) -> Dict[str, str]:
    if api_key.startswith("ey"): # Token JWT v4
        return {"Authorization": f"Bearer {api_key}", "accept": "application/json"}
    return {"accept": "application/json"}

def obter_params(api_key: str, extras: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    params = extras.copy() if extras else {}
    if not api_key.startswith("ey"):
        params["api_key"] = api_key
    return params

def carregar_plataformas_tmdb(cur, api_key: str) -> int:
    """
    Funcao A3: carregar_plataformas
    Busca todas as plataformas ativas no Brasil no endpoint da TMDB e realiza upsert.
    """
    url = f"{TMDB_BASE_URL}/watch/providers/movie"
    params = obter_params(api_key, {"watch_region": "BR"})
    headers = obter_headers(api_key)

    with httpx.Client(timeout=15.0) as client:
        resp = client.get(url, params=params, headers=headers)
        resp.raise_for_status()
        dados = resp.json()

    provedores = dados.get("results", [])
    total_upsert = 0
    for prov in provedores:
        p_id = prov.get("provider_id")
        nome = prov.get("provider_name")
        logo = prov.get("logo_path")
        if p_id and nome:
            cur.execute("""
                INSERT INTO plataforma (provider_id, nome, logo_path)
                VALUES (%s, %s, %s)
                ON CONFLICT (provider_id) DO UPDATE
                SET nome = EXCLUDED.nome,
                    logo_path = EXCLUDED.logo_path;
            """, (p_id, nome, logo))
            total_upsert += 1

    return total_upsert

def obter_estreia_comercial_eua(client: httpx.Client, movie_id: int, api_key: str, release_principal: str) -> str:
    """
    Obtem a data de estreia comercial nos EUA (tipo 2 ou 3) conforme RN1.
    Fallback para a data de lancamento principal se ausente.
    """
    url = f"{TMDB_BASE_URL}/movie/{movie_id}/release_dates"
    params = obter_params(api_key)
    headers = obter_headers(api_key)

    try:
        resp = client.get(url, params=params, headers=headers)
        if resp.status_code == 200:
            dados = resp.json()
            for item in dados.get("results", []):
                if item.get("iso_3166_1") == "US":
                    # Procura tipos 2 (Limited) ou 3 (Theatrical)
                    datas_cinema = [
                        rd.get("release_date")[:10]
                        for rd in item.get("release_dates", [])
                        if rd.get("type") in (2, 3) and rd.get("release_date")
                    ]
                    if datas_cinema:
                        return min(datas_cinema)
    except Exception:
        pass

    return release_principal

def sincronizar_filme_tmdb(cur, client: httpx.Client, movie_id: int, ano_edicao: int, api_key: str, generos_map: Dict[int, tuple[int, float]]):
    """
    Funcao A5 (Unidade Transacional por filme):
    Sincroniza metadados, release_date, creditos (top 10 cast + crew chave) e disponibilidade no Brasil.
    """
    # 1. Metadados do filme
    url_movie = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = obter_params(api_key, {"language": "pt-BR", "append_to_response": "credits,watch/providers"})
    headers = obter_headers(api_key)

    resp = client.get(url_movie, params=params, headers=headers)
    if resp.status_code != 200:
        return None

    filme = resp.json()
    
    # Ignora filmes de televisao (Cinema TV)
    gen_ids = [g["id"] for g in filme.get("genres", [])]
    if 10770 in gen_ids:
        return None

    titulo = filme.get("title") or filme.get("original_title")
    titulo_original = filme.get("original_title")
    sinopse = filme.get("overview") or None
    poster_path = filme.get("poster_path") or None
    duracao_min = filme.get("runtime") or None
    popularidade = float(filme.get("popularity") or 0.0)
    imdb_id = filme.get("imdb_id") or None
    if imdb_id and imdb_id.strip() == "":
        imdb_id = None

    release_principal = (filme.get("release_date") or "")[:10]
    if not release_principal:
        return None

    release_date = obter_estreia_comercial_eua(client, movie_id, api_key, release_principal)

    # Coleta pesos dos generos para calculo inicial do score
    pesos_generos = []
    ids_generos_db = []
    for g_id in gen_ids:
        if g_id in generos_map:
            db_id, peso = generos_map[g_id]
            pesos_generos.append(peso)
            ids_generos_db.append(db_id)

    # Calculo inicial do Buzz Score
    score_inicial = calcular_oscar_buzz_score(
        popularity=popularidade,
        generos_pesos=pesos_generos
    )

    # Upsert em FILME
    cur.execute("""
        INSERT INTO filme (
            tmdb_id, imdb_id, titulo, titulo_original, sinopse, poster_path,
            release_date, duracao_min, popularidade, oscar_buzz_score, ano_edicao
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (tmdb_id) DO UPDATE SET
            imdb_id = COALESCE(EXCLUDED.imdb_id, filme.imdb_id),
            titulo = EXCLUDED.titulo,
            titulo_original = EXCLUDED.titulo_original,
            sinopse = COALESCE(EXCLUDED.sinopse, filme.sinopse),
            poster_path = COALESCE(EXCLUDED.poster_path, filme.poster_path),
            release_date = EXCLUDED.release_date,
            duracao_min = COALESCE(EXCLUDED.duracao_min, filme.duracao_min),
            popularidade = EXCLUDED.popularidade,
            ano_edicao = EXCLUDED.ano_edicao;
    """, (
        movie_id, imdb_id, titulo, titulo_original, sinopse, poster_path,
        release_date, duracao_min, popularidade, score_inicial, ano_edicao
    ))

    # Paises de Origem (1FN)
    paises = filme.get("origin_country") or [p.get("iso_3166_1") for p in filme.get("production_countries", [])]
    cur.execute("DELETE FROM filme_pais_origem WHERE tmdb_id = %s;", (movie_id,))
    for p in set(filter(None, paises)):
        cur.execute("""
            INSERT INTO filme_pais_origem (tmdb_id, codigo_pais)
            VALUES (%s, %s) ON CONFLICT DO NOTHING;
        """, (movie_id, p[:10]))

    # Generos N:M
    cur.execute("DELETE FROM filme_genero WHERE tmdb_id = %s;", (movie_id,))
    for db_id in set(ids_generos_db):
        cur.execute("""
            INSERT INTO filme_genero (tmdb_id, id_genero)
            VALUES (%s, %s) ON CONFLICT DO NOTHING;
        """, (movie_id, db_id))

    # Creditos: Top 10 Cast + Crew Chave
    credits = filme.get("credits", {})
    cast_list = sorted(credits.get("cast", []), key=lambda x: x.get("order", 999))[:10]
    
    crew_jobs_map = {
        "Director": "DIRETOR",
        "Screenplay": "ROTEIRISTA",
        "Writer": "ROTEIRISTA",
        "Producer": "PRODUTOR",
        "Original Music Composer": "COMPOSITOR",
        "Director of Photography": "DIRETOR_FOTOGRAFIA",
        "Editor": "MONTADOR"
    }

    # Salva profissionais e creditos de elenco
    for cast in cast_list:
        person_id = cast.get("id")
        nome = cast.get("name")
        if not person_id or not nome:
            continue
        cur.execute("""
            INSERT INTO profissional (tmdb_person_id, nome, profile_path, known_for_department)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (tmdb_person_id) DO UPDATE SET
                nome = EXCLUDED.nome,
                profile_path = COALESCE(EXCLUDED.profile_path, profissional.profile_path);
        """, (person_id, nome, cast.get("profile_path"), cast.get("known_for_department") or "Acting"))

        char_name = (cast.get("character") or "Não informado").strip() or "Não informado"
        cur.execute("""
            INSERT INTO credito (tmdb_id, tmdb_person_id, funcao, character_name, credit_id, ordem_elenco)
            VALUES (%s, %s, 'ELENCO', %s, %s, %s)
            ON CONFLICT (tmdb_id, tmdb_person_id, funcao) DO UPDATE SET
                character_name = EXCLUDED.character_name,
                ordem_elenco = EXCLUDED.ordem_elenco;
        """, (movie_id, person_id, char_name, cast.get("credit_id"), cast.get("order")))

    # Salva profissionais e creditos de equipe tecnica
    for crew in credits.get("crew", []):
        job = crew.get("job")
        if job in crew_jobs_map:
            funcao_db = crew_jobs_map[job]
            person_id = crew.get("id")
            nome = crew.get("name")
            if not person_id or not nome:
                continue

            cur.execute("""
                INSERT INTO profissional (tmdb_person_id, nome, profile_path, known_for_department)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (tmdb_person_id) DO UPDATE SET
                    nome = EXCLUDED.nome,
                    profile_path = COALESCE(EXCLUDED.profile_path, profissional.profile_path);
            """, (person_id, nome, crew.get("profile_path"), crew.get("department")))

            cur.execute("""
                INSERT INTO credito (tmdb_id, tmdb_person_id, funcao, character_name, credit_id, ordem_elenco)
                VALUES (%s, %s, %s, NULL, %s, NULL)
                ON CONFLICT (tmdb_id, tmdb_person_id, funcao) DO NOTHING;
            """, (movie_id, person_id, funcao_db, crew.get("credit_id")))

    # Disponibilidade de Streaming (Brasil - watch/providers)
    wp = filme.get("watch/providers", {}).get("results", {}).get("BR", {})
    modalidades_map = {
        "flatrate": "ASSINATURA",
        "rent": "ALUGUEL",
        "buy": "COMPRA"
    }

    # Atualizacao de ofertas: remove anteriores e insere vigentes na mesma transacao (RN4)
    cur.execute("DELETE FROM disponibilidade WHERE tmdb_id = %s;", (movie_id,))
    for mod_key, mod_db in modalidades_map.items():
        for prov in wp.get(mod_key, []):
            prov_id = prov.get("provider_id")
            prov_nome = prov.get("provider_name")
            prov_logo = prov.get("logo_path")
            if prov_id:
                # Garante existencia na tabela plataforma
                cur.execute("""
                    INSERT INTO plataforma (provider_id, nome, logo_path)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (provider_id) DO UPDATE SET
                        nome = EXCLUDED.nome,
                        logo_path = COALESCE(EXCLUDED.logo_path, plataforma.logo_path);
                """, (prov_id, prov_nome, prov_logo))

                cur.execute("""
                    INSERT INTO disponibilidade (tmdb_id, provider_id, modalidade, data_coleta)
                    VALUES (%s, %s, %s, CURRENT_DATE)
                    ON CONFLICT (tmdb_id, provider_id, modalidade) DO UPDATE SET
                        data_coleta = CURRENT_DATE;
                """, (movie_id, prov_id, mod_db))

    return titulo
