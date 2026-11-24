import httpx
from typing import Dict, Any, Optional
from scripts.buzz_score import calcular_oscar_buzz_score

OMDB_BASE_URL = "https://www.omdbapi.com/"

def atualizar_filme_omdb(cur, client: httpx.Client, tmdb_id: int, imdb_id: str, api_key: str) -> Optional[Dict[str, Any]]:
    """
    Funcao A6: atualizar_avaliacoes_criticas
    Consulta a OMDb API pelo imdb_id, atualiza imdb_rating, metascore, premios_texto,
    vincula o genero 'Biografia' caso presente no retorno, e recalcula o Oscar Buzz Score.
    """
    if not imdb_id or not api_key:
        return None

    params = {"apikey": api_key, "i": imdb_id}
    try:
        resp = client.get(OMDB_BASE_URL, params=params, timeout=12.0)
        if resp.status_code != 200:
            return None
        dados = resp.json()
        if dados.get("Response") != "True":
            return None
    except Exception:
        return None

    # Parsing das metricas
    raw_rating = dados.get("imdbRating")
    imdb_rating = None
    if raw_rating and raw_rating.strip().upper() != "N/A":
        try:
            val = float(raw_rating)
            if 0.0 <= val <= 10.0:
                imdb_rating = val
        except ValueError:
            pass

    raw_metascore = dados.get("Metascore")
    metascore = None
    if raw_metascore and raw_metascore.strip().upper() != "N/A":
        try:
            val = int(raw_metascore)
            if 0 <= val <= 100:
                metascore = val
        except ValueError:
            pass

    awards_text = dados.get("Awards")
    if awards_text and awards_text.strip().upper() == "N/A":
        awards_text = None

    # Se a OMDb contem o genero 'Biography', vincula ao genero Biografia (RN2)
    generos_texto = dados.get("Genre") or ""
    if "Biography" in generos_texto:
        cur.execute("""
            INSERT INTO filme_genero (tmdb_id, id_genero)
            SELECT %s, id_genero FROM genero WHERE nome = 'Biografia'
            ON CONFLICT DO NOTHING;
        """, (tmdb_id,))

    # Busca popularidade e pesos dos generos atualizados para recalcular o Buzz Score
    cur.execute("""
        SELECT f.popularidade, ARRAY_AGG(g.peso_academia) as pesos
        FROM filme f
        LEFT JOIN filme_genero fg ON f.tmdb_id = fg.tmdb_id
        LEFT JOIN genero g ON fg.id_genero = g.id_genero
        WHERE f.tmdb_id = %s
        GROUP BY f.tmdb_id, f.popularidade;
    """, (tmdb_id,))
    row = cur.fetchone()
    
    popularidade = float(row["popularidade"]) if row and row["popularidade"] is not None else 0.0
    pesos = [float(p) for p in (row["pesos"] or []) if p is not None]

    # Recalcula o Oscar Buzz Score com todas as metricas consolidadas
    novo_score = calcular_oscar_buzz_score(
        popularity=popularidade,
        generos_pesos=pesos,
        imdb_rating=imdb_rating,
        metascore=metascore,
        awards_text=awards_text
    )

    # Gravacao das notas e do score recalculado na mesma transacao (Secao 4.3.3)
    cur.execute("""
        UPDATE filme
        SET imdb_rating = %s,
            metascore = %s,
            premios_texto = %s,
            oscar_buzz_score = %s
        WHERE tmdb_id = %s;
    """, (imdb_rating, metascore, awards_text, novo_score, tmdb_id))

    return {
        "tmdb_id": tmdb_id,
        "imdb_rating": imdb_rating,
        "metascore": metascore,
        "buzz_score": novo_score
    }
