from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional, List
import datetime
import psycopg

from app.database import get_db_cursor, is_postgres_available
from app.config import settings
from scripts.executar_carga import AMOSTRA_FILMES_DEMO
from scripts.buzz_score import calcular_oscar_buzz_score

app = FastAPI(
    title="Oscar Tracker API",
    description="Monitor Analítico e Rastreador de Filmes para a Temporada do Oscar - IMD0401 (UFRN)",
    version="1.0.0"
)

BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# ============================================================================
# MOCK DEMO FALLBACK (Para execucao imediata quando o PostgreSQL local nao estiver ativo)
# ============================================================================
def fallback_opcoes_filtro(ano_edicao: int):
    generos_set = set()
    plataformas_dict = {}
    for f in AMOSTRA_FILMES_DEMO:
        for g in f["generos"]:
            generos_set.add(g)
        for st in f["streamings"]:
            plataformas_dict[st["provider_id"]] = {"provider_id": st["provider_id"], "nome": st["nome"], "logo_path": st["logo"]}
            
    return {
        "edicoes": [{"ano_edicao": 2026, "data_cerimonia": "2026-03-08"}, {"ano_edicao": 2025, "data_cerimonia": "2025-03-02"}],
        "generos": [{"id_genero": i+1, "nome": g} for i, g in enumerate(sorted(generos_set))],
        "plataformas": list(plataformas_dict.values()),
        "categorias": [
            {"id_categoria": 1, "nome": "Melhor Filme", "escopo": "FILME"},
            {"id_categoria": 2, "nome": "Melhor Direção", "escopo": "INDIVIDUAL"},
            {"id_categoria": 3, "nome": "Melhor Ator", "escopo": "INDIVIDUAL"},
            {"id_categoria": 4, "nome": "Melhor Atriz", "escopo": "INDIVIDUAL"},
            {"id_categoria": 5, "nome": "Melhor Ator Coadjuvante", "escopo": "INDIVIDUAL"},
            {"id_categoria": 6, "nome": "Melhor Atriz Coadjuvante", "escopo": "INDIVIDUAL"},
            {"id_categoria": 7, "nome": "Melhor Roteiro Original", "escopo": "INDIVIDUAL"},
            {"id_categoria": 8, "nome": "Melhor Roteiro Adaptado", "escopo": "INDIVIDUAL"},
            {"id_categoria": 9, "nome": "Melhor Animação", "escopo": "FILME"},
            {"id_categoria": 10, "nome": "Melhor Fotografia", "escopo": "INDIVIDUAL"}
        ],
        "modalidades": ["ASSINATURA", "ALUGUEL", "COMPRA"]
    }

def fallback_consultar_linha_do_tempo(ano_edicao=2026, status_filme="TODOS", id_genero=None, provider_id=None, modalidade=None, busca=None, ordem="BUZZ_SCORE_DESC", pagina=1, tamanho_pagina=24):
    filmes_processados = []
    hoje = datetime.date.today().isoformat()
    
    for f in AMOSTRA_FILMES_DEMO:
        status_deriv = "LANCADO" if f["release_date"] <= hoje else "FUTURO"
        if status_filme == "LANCADO" and status_deriv != "LANCADO":
            continue
        if status_filme == "FUTURO" and status_deriv != "FUTURO":
            continue
        if busca and busca.lower() not in f["titulo"].lower() and busca.lower() not in f["titulo_original"].lower():
            continue
        if provider_id:
            if not any(st["provider_id"] == provider_id for st in f["streamings"]):
                continue
        if modalidade:
            if not any(st["modalidade"] == modalidade for st in f["streamings"]):
                continue

        score = calcular_oscar_buzz_score(
            popularity=f["popularidade"],
            generos_pesos=[0.60] * len(f["generos"]),
            imdb_rating=f["imdb_rating"],
            metascore=f["metascore"],
            awards_text=f["premios_texto"]
        )

        filmes_processados.append({
            "tmdb_id": f["tmdb_id"],
            "imdb_id": f["imdb_id"],
            "titulo": f["titulo"],
            "titulo_original": f["titulo_original"],
            "poster_path": f["poster_path"],
            "release_date": f["release_date"],
            "duracao_min": f["duracao_min"],
            "popularidade": f["popularidade"],
            "imdb_rating": f["imdb_rating"],
            "metascore": f["metascore"],
            "oscar_buzz_score": score,
            "status_derivado": status_deriv,
            "generos": [{"id_genero": i, "nome": g} for i, g in enumerate(f["generos"])],
            "streamings": [{"provider_id": st["provider_id"], "nome": st["nome"], "modalidade": st["modalidade"], "logo_path": st["logo"]} for st in f["streamings"]],
            "total_candidaturas": len(f.get("candidaturas", []))
        })

    if ordem == "BUZZ_SCORE_DESC":
        filmes_processados.sort(key=lambda x: x["oscar_buzz_score"], reverse=True)
    elif ordem == "DATA_ASC":
        filmes_processados.sort(key=lambda x: x["release_date"])
    elif ordem == "POPULARIDADE_DESC":
        filmes_processados.sort(key=lambda x: x["popularidade"], reverse=True)

    return {
        "filmes": filmes_processados,
        "total": len(filmes_processados),
        "pagina": pagina,
        "tamanho_pagina": tamanho_pagina,
        "total_paginas": 1
    }

def fallback_obter_ficha_tecnica(tmdb_id: int):
    for f in AMOSTRA_FILMES_DEMO:
        if f["tmdb_id"] == tmdb_id:
            score = calcular_oscar_buzz_score(
                popularity=f["popularidade"],
                generos_pesos=[0.60] * len(f["generos"]),
                imdb_rating=f["imdb_rating"],
                metascore=f["metascore"],
                awards_text=f["premios_texto"]
            )
            return {
                "tmdb_id": f["tmdb_id"],
                "imdb_id": f["imdb_id"],
                "titulo": f["titulo"],
                "titulo_original": f["titulo_original"],
                "sinopse": f["sinopse"],
                "poster_path": f["poster_path"],
                "release_date": f["release_date"],
                "duracao_min": f["duracao_min"],
                "popularidade": f["popularidade"],
                "imdb_rating": f["imdb_rating"],
                "metascore": f["metascore"],
                "oscar_buzz_score": score,
                "ano_edicao": 2026,
                "data_cerimonia": "2026-03-08",
                "status_derivado": "LANCADO" if f["release_date"] <= datetime.date.today().isoformat() else "FUTURO",
                "paises": f["paises"],
                "generos": [{"id_genero": i, "nome": g, "peso_academia": 0.60} for i, g in enumerate(f["generos"])],
                "streamings": [{"provider_id": st["provider_id"], "nome": st["nome"], "modalidade": st["modalidade"], "logo_path": st["logo"]} for st in f["streamings"]],
                "elenco": [{"tmdb_person_id": at["person_id"], "nome": at["nome"], "character_name": at["char"], "ordem_elenco": at["ordem"], "profile_path": None} for at in f["elenco"]],
                "equipe": [{"tmdb_person_id": eq["person_id"], "nome": eq["nome"], "funcao": eq["funcao"], "profile_path": None} for eq in f["equipe"]],
                "candidaturas": [{"categoria_nome": cand["categoria"], "status": cand["status"], "profissional_nome": None} for cand in f["candidaturas"]]
            }
    raise HTTPException(status_code=404, detail="Filme não encontrado.")

def fallback_radar_categoria(ano_edicao=2026, id_categoria=None, status=None):
    radar_map = {}
    for f in AMOSTRA_FILMES_DEMO:
        score = calcular_oscar_buzz_score(
            popularity=f["popularidade"],
            generos_pesos=[0.60] * len(f["generos"]),
            imdb_rating=f["imdb_rating"],
            metascore=f["metascore"],
            awards_text=f["premios_texto"]
        )
        for cand in f["candidaturas"]:
            cat_nome = cand["categoria"]
            if cat_nome not in radar_map:
                radar_map[cat_nome] = {
                    "id_categoria": len(radar_map) + 1,
                    "nome": cat_nome,
                    "escopo": "FILME" if "Filme" in cat_nome or "Animação" in cat_nome else "INDIVIDUAL",
                    "funcao_exigida": "DIRETOR" if "Direção" in cat_nome else ("ELENCO" if "Ator" in cat_nome or "Atriz" in cat_nome else None),
                    "candidaturas": []
                }
            radar_map[cat_nome]["candidaturas"].append({
                "tmdb_id": f["tmdb_id"],
                "titulo": f["titulo"],
                "titulo_original": f["titulo_original"],
                "poster_path": f["poster_path"],
                "oscar_buzz_score": score,
                "status": cand["status"],
                "profissional_nome": next((eq["nome"] for eq in f["equipe"] if eq.get("person_id") == cand.get("person_id")), None)
            })

    for cat in radar_map.values():
        cat["total"] = len(cat["candidaturas"])
        cat["candidaturas"].sort(key=lambda x: (0 if x["status"] == "VENCEDOR" else (1 if x["status"] == "INDICADO" else 2), -x["oscar_buzz_score"]))

    return list(radar_map.values())

# ============================================================================
# FUNÇÃO C4: listar_opcoes_de_filtro
# ============================================================================
def obter_opcoes_filtro(ano_edicao: int):
    try:
        with get_db_cursor(commit=False) as cur:
            cur.execute("SELECT ano_edicao, data_cerimonia FROM edicao ORDER BY ano_edicao DESC;")
            edicoes = cur.fetchall()

            cur.execute("""
                SELECT DISTINCT g.id_genero, g.nome
                FROM genero g
                JOIN filme_genero fg ON g.id_genero = fg.id_genero
                JOIN filme f ON fg.tmdb_id = f.tmdb_id
                WHERE f.ano_edicao = %s
                ORDER BY g.nome;
            """, (ano_edicao,))
            generos = cur.fetchall()

            cur.execute("""
                SELECT DISTINCT p.provider_id, p.nome, p.logo_path
                FROM plataforma p
                JOIN disponibilidade d ON p.provider_id = d.provider_id
                JOIN filme f ON d.tmdb_id = f.tmdb_id
                WHERE f.ano_edicao = %s
                ORDER BY p.nome;
            """, (ano_edicao,))
            plataformas = cur.fetchall()

            cur.execute("SELECT id_categoria, nome, escopo FROM categoria ORDER BY escopo, nome;")
            categorias = cur.fetchall()

            return {
                "edicoes": edicoes,
                "generos": generos,
                "plataformas": plataformas,
                "categorias": categorias,
                "modalidades": ["ASSINATURA", "ALUGUEL", "COMPRA"]
            }
    except Exception:
        return fallback_opcoes_filtro(ano_edicao)

# ============================================================================
# FUNÇÃO C1: consultar_linha_do_tempo
# ============================================================================
def consultar_linha_do_tempo(
    ano_edicao: int = 2026,
    mes: Optional[int] = None,
    status_filme: str = "TODOS",
    id_genero: Optional[int] = None,
    provider_id: Optional[int] = None,
    modalidade: Optional[str] = None,
    id_categoria: Optional[int] = None,
    nota_min: Optional[float] = None,
    nota_max: Optional[float] = None,
    busca: Optional[str] = None,
    ordem: str = "BUZZ_SCORE_DESC",
    pagina: int = 1,
    tamanho_pagina: int = 24
):
    try:
        filtros = ["f.ano_edicao = %(ano_edicao)s"]
        params = {"ano_edicao": ano_edicao}

        hoje = datetime.date.today()
        if status_filme == "LANCADO":
            filtros.append("f.release_date <= %(hoje)s")
            params["hoje"] = hoje
        elif status_filme == "FUTURO":
            filtros.append("f.release_date > %(hoje)s")
            params["hoje"] = hoje

        if mes and 1 <= mes <= 12:
            filtros.append("EXTRACT(MONTH FROM f.release_date) = %(mes)s")
            params["mes"] = mes

        if id_genero:
            filtros.append("EXISTS (SELECT 1 FROM filme_genero fg WHERE fg.tmdb_id = f.tmdb_id AND fg.id_genero = %(id_genero)s)")
            params["id_genero"] = id_genero

        if provider_id:
            if modalidade:
                filtros.append("EXISTS (SELECT 1 FROM disponibilidade d WHERE d.tmdb_id = f.tmdb_id AND d.provider_id = %(provider_id)s AND d.modalidade = %(modalidade)s)")
                params["modalidade"] = modalidade
            else:
                filtros.append("EXISTS (SELECT 1 FROM disponibilidade d WHERE d.tmdb_id = f.tmdb_id AND d.provider_id = %(provider_id)s)")
            params["provider_id"] = provider_id
        elif modalidade:
            filtros.append("EXISTS (SELECT 1 FROM disponibilidade d WHERE d.tmdb_id = f.tmdb_id AND d.modalidade = %(modalidade)s)")
            params["modalidade"] = modalidade

        if id_categoria:
            filtros.append("EXISTS (SELECT 1 FROM candidatura c WHERE c.tmdb_id = f.tmdb_id AND c.id_categoria = %(id_categoria)s)")
            params["id_categoria"] = id_categoria

        if nota_min is not None:
            filtros.append("f.imdb_rating >= %(nota_min)s")
            params["nota_min"] = nota_min
        if nota_max is not None:
            filtros.append("f.imdb_rating <= %(nota_max)s")
            params["nota_max"] = nota_max

        if busca and busca.strip():
            filtros.append("(f.titulo ILIKE %(busca)s OR f.titulo_original ILIKE %(busca)s)")
            params["busca"] = f"%{busca.strip()}%"

        order_clause = "f.oscar_buzz_score DESC, f.popularidade DESC"
        if ordem == "DATA_ASC":
            order_clause = "f.release_date ASC, f.oscar_buzz_score DESC"
        elif ordem == "POPULARIDADE_DESC":
            order_clause = "f.popularidade DESC, f.oscar_buzz_score DESC"

        offset = (pagina - 1) * tamanho_pagina
        params["limit"] = tamanho_pagina
        params["offset"] = offset

        where_str = " AND ".join(filtros)

        with get_db_cursor(commit=False) as cur:
            cur.execute(f"SELECT COUNT(*) as total FROM filme f WHERE {where_str};", params)
            total = cur.fetchone()["total"]

            query = f"""
                SELECT 
                    f.tmdb_id,
                    f.imdb_id,
                    f.titulo,
                    f.titulo_original,
                    f.poster_path,
                    f.release_date,
                    f.duracao_min,
                    f.popularidade,
                    f.imdb_rating,
                    f.metascore,
                    f.oscar_buzz_score,
                    CASE WHEN f.release_date <= CURRENT_DATE THEN 'LANCADO' ELSE 'FUTURO' END as status_derivado,
                    COALESCE(
                        (SELECT JSON_AGG(JSON_BUILD_OBJECT('id_genero', g.id_genero, 'nome', g.nome))
                         FROM filme_genero fg JOIN genero g ON fg.id_genero = g.id_genero
                         WHERE fg.tmdb_id = f.tmdb_id), '[]'::json
                    ) as generos,
                    COALESCE(
                        (SELECT JSON_AGG(JSON_BUILD_OBJECT('provider_id', p.provider_id, 'nome', p.nome, 'modalidade', d.modalidade, 'logo_path', p.logo_path))
                         FROM disponibilidade d JOIN plataforma p ON d.provider_id = p.provider_id
                         WHERE d.tmdb_id = f.tmdb_id), '[]'::json
                    ) as streamings,
                    COALESCE(
                        (SELECT COUNT(*) FROM candidatura c WHERE c.tmdb_id = f.tmdb_id), 0
                    ) as total_candidaturas
                FROM filme f
                WHERE {where_str}
                ORDER BY {order_clause}
                LIMIT %(limit)s OFFSET %(offset)s;
            """
            cur.execute(query, params)
            filmes = cur.fetchall()

            return {
                "filmes": filmes,
                "total": total,
                "pagina": pagina,
                "tamanho_pagina": tamanho_pagina,
                "total_paginas": (total + tamanho_pagina - 1) // tamanho_pagina if total > 0 else 1
            }
    except Exception:
        return fallback_consultar_linha_do_tempo(
            ano_edicao=ano_edicao,
            status_filme=status_filme,
            id_genero=id_genero,
            provider_id=provider_id,
            modalidade=modalidade,
            busca=busca,
            ordem=ordem,
            pagina=pagina,
            tamanho_pagina=tamanho_pagina
        )

# ============================================================================
# FUNÇÃO C2: obter_ficha_tecnica_filme
# ============================================================================
def obter_ficha_tecnica_filme(tmdb_id: int):
    try:
        with get_db_cursor(commit=False) as cur:
            cur.execute("""
                SELECT 
                    f.*,
                    e.ano_edicao,
                    e.data_cerimonia,
                    CASE WHEN f.release_date <= CURRENT_DATE THEN 'LANCADO' ELSE 'FUTURO' END as status_derivado
                FROM filme f
                JOIN edicao e ON f.ano_edicao = e.ano_edicao
                WHERE f.tmdb_id = %s;
            """, (tmdb_id,))
            filme = cur.fetchone()

            if not filme:
                return fallback_obter_ficha_tecnica(tmdb_id)

            cur.execute("SELECT codigo_pais FROM filme_pais_origem WHERE tmdb_id = %s ORDER BY codigo_pais;", (tmdb_id,))
            paises = [r["codigo_pais"] for r in cur.fetchall()]

            cur.execute("""
                SELECT g.id_genero, g.nome, g.peso_academia
                FROM genero g
                JOIN filme_genero fg ON g.id_genero = fg.id_genero
                WHERE fg.tmdb_id = %s
                ORDER BY g.nome;
            """, (tmdb_id,))
            generos = cur.fetchall()

            cur.execute("""
                SELECT p.provider_id, p.nome, p.logo_path, d.modalidade, d.data_coleta
                FROM disponibilidade d
                JOIN plataforma p ON d.provider_id = p.provider_id
                WHERE d.tmdb_id = %s
                ORDER BY d.modalidade, p.nome;
            """, (tmdb_id,))
            streamings = cur.fetchall()

            cur.execute("""
                SELECT p.tmdb_person_id, p.nome, p.profile_path, c.character_name, c.ordem_elenco
                FROM credito c
                JOIN profissional p ON c.tmdb_person_id = p.tmdb_person_id
                WHERE c.tmdb_id = %s AND c.funcao = 'ELENCO'
                ORDER BY c.ordem_elenco ASC NULLS LAST;
            """, (tmdb_id,))
            elenco = cur.fetchall()

            cur.execute("""
                SELECT p.tmdb_person_id, p.nome, p.profile_path, c.funcao
                FROM credito c
                JOIN profissional p ON c.tmdb_person_id = p.tmdb_person_id
                WHERE c.tmdb_id = %s AND c.funcao <> 'ELENCO'
                ORDER BY c.funcao, p.nome;
            """, (tmdb_id,))
            equipe = cur.fetchall()

            cur.execute("""
                SELECT 
                    c.seq_candidatura,
                    c.status,
                    cat.id_categoria,
                    cat.nome as categoria_nome,
                    cat.escopo,
                    p.nome as profissional_nome
                FROM candidatura c
                JOIN categoria cat ON c.id_categoria = cat.id_categoria
                LEFT JOIN profissional p ON c.tmdb_person_id = p.tmdb_person_id
                WHERE c.tmdb_id = %s
                ORDER BY 
                    CASE c.status 
                        WHEN 'VENCEDOR' THEN 1 
                        WHEN 'INDICADO' THEN 2 
                        ELSE 3 
                    END,
                    cat.nome;
            """, (tmdb_id,))
            candidaturas = cur.fetchall()

            return {
                **filme,
                "paises": paises,
                "generos": generos,
                "streamings": streamings,
                "elenco": elenco,
                "equipe": equipe,
                "candidaturas": candidaturas
            }
    except Exception:
        return fallback_obter_ficha_tecnica(tmdb_id)

# ============================================================================
# FUNÇÃO C3: listar_radar_por_categoria
# ============================================================================
def listar_radar_por_categoria(ano_edicao: int = 2026, id_categoria: Optional[int] = None, status: Optional[str] = None):
    try:
        with get_db_cursor(commit=False) as cur:
            cat_filter = "WHERE 1=1"
            params = [ano_edicao]
            if id_categoria:
                cat_filter += " AND c.id_categoria = %s"
                params.append(id_categoria)

            cur.execute(f"SELECT c.id_categoria, c.nome, c.escopo, c.funcao_exigida FROM categoria c {cat_filter} ORDER BY c.escopo, c.nome;", params[1:])
            categorias = cur.fetchall()

            status_clause = ""
            cand_params = [ano_edicao]
            if status:
                status_clause = "AND cand.status = %s"
                cand_params.append(status)

            query = f"""
                SELECT 
                    cand.id_categoria,
                    cand.seq_candidatura,
                    cand.status,
                    f.tmdb_id,
                    f.titulo,
                    f.titulo_original,
                    f.poster_path,
                    f.oscar_buzz_score,
                    p.tmdb_person_id,
                    p.nome as profissional_nome
                FROM candidatura cand
                JOIN filme f ON cand.tmdb_id = f.tmdb_id
                LEFT JOIN profissional p ON cand.tmdb_person_id = p.tmdb_person_id
                WHERE f.ano_edicao = %s {status_clause}
                ORDER BY 
                    cand.id_categoria,
                    CASE cand.status 
                        WHEN 'VENCEDOR' THEN 1 
                        WHEN 'INDICADO' THEN 2 
                        ELSE 3 
                    END,
                    f.oscar_buzz_score DESC;
            """
            cur.execute(query, cand_params)
            candidaturas_raw = cur.fetchall()

            cand_por_cat = {}
            for r in candidaturas_raw:
                cid = r["id_categoria"]
                if cid not in cand_por_cat:
                    cand_por_cat[cid] = []
                cand_por_cat[cid].append(r)

            resultado = []
            for cat in categorias:
                cands = cand_por_cat.get(cat["id_categoria"], [])
                resultado.append({
                    "id_categoria": cat["id_categoria"],
                    "nome": cat["nome"],
                    "escopo": cat["escopo"],
                    "funcao_exigida": cat["funcao_exigida"],
                    "candidaturas": cands,
                    "total": len(cands)
                })

            return resultado
    except Exception:
        return fallback_radar_categoria(ano_edicao=ano_edicao, id_categoria=id_categoria, status=status)

# ============================================================================
# ROTAS DA APLICAÇÃO WEB
# ============================================================================

@app.get("/", response_class=HTMLResponse)
def index_page(
    request: Request,
    ano: int = 2026,
    mes: Optional[int] = None,
    status: str = "TODOS",
    genero: Optional[int] = None,
    plataforma: Optional[int] = None,
    modalidade: Optional[str] = None,
    categoria: Optional[int] = None,
    busca: Optional[str] = None,
    ordem: str = "BUZZ_SCORE_DESC",
    pagina: int = 1
):
    filtros_opcoes = obter_opcoes_filtro(ano)
    resultado = consultar_linha_do_tempo(
        ano_edicao=ano,
        mes=mes,
        status_filme=status,
        id_genero=genero,
        provider_id=plataforma,
        modalidade=modalidade,
        id_categoria=categoria,
        busca=busca,
        ordem=ordem,
        pagina=pagina
    )

    return templates.TemplateResponse(request=request, name="index.html", context={
        "filmes": resultado["filmes"],
        "total": resultado["total"],
        "pagina_atual": resultado["pagina"],
        "total_paginas": resultado["total_paginas"],
        "opcoes": filtros_opcoes,
        "ano_selecionado": ano,
        "mes_selecionado": mes,
        "status_selecionado": status,
        "genero_selecionado": genero,
        "plataforma_selecionada": plataforma,
        "modalidade_selecionada": modalidade,
        "categoria_selecionada": categoria,
        "busca_selecionada": busca or "",
        "ordem_selecionada": ordem
    })

@app.get("/radar", response_class=HTMLResponse)
def radar_page(
    request: Request,
    ano: int = 2026,
    categoria: Optional[int] = None,
    status: Optional[str] = None
):
    filtros_opcoes = obter_opcoes_filtro(ano)
    radar_dados = listar_radar_por_categoria(ano_edicao=ano, id_categoria=categoria, status=status)

    return templates.TemplateResponse(request=request, name="radar.html", context={
        "categorias_radar": radar_dados,
        "opcoes": filtros_opcoes,
        "ano_selecionado": ano,
        "categoria_selecionada": categoria,
        "status_selecionado": status
    })

@app.get("/api/filmes/{tmdb_id}", response_class=JSONResponse)
def api_detalhe_filme(tmdb_id: int):
    return obter_ficha_tecnica_filme(tmdb_id)

@app.get("/api/linha-do-tempo", response_class=JSONResponse)
def api_linha_do_tempo(
    ano: int = 2026,
    status: str = "TODOS",
    genero: Optional[int] = None,
    ordem: str = "BUZZ_SCORE_DESC"
):
    return consultar_linha_do_tempo(ano_edicao=ano, status_filme=status, id_genero=genero, ordem=ordem)
