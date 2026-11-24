"""
Script Unificado de Execucao de Cargas e Populacao do Banco de Dados
Suporta modo --live (consumo direto de APIs com chaves) e modo --demo (carga de amostra oficial
para avaliacao em maquina limpa sem dependencia de chaves externas).
"""
import argparse
import sys
import os

# Adiciona o diretorio raiz do projeto ao path do Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.database import get_db_cursor
from scripts.carga_tmdb import carregar_plataformas_tmdb, sincronizar_filme_tmdb
from scripts.carga_omdb import atualizar_filme_omdb
from scripts.buzz_score import calcular_oscar_buzz_score

# Amostra rica e realista de filmes e concorrentes ao Oscar para o modo --demo
AMOSTRA_FILMES_DEMO = [
    {
        "tmdb_id": 693134,
        "imdb_id": "tt15239678",
        "titulo": "Duna: Parte 2",
        "titulo_original": "Dune: Part Two",
        "sinopse": "Paul Atreides se une a Chani e aos Fremen em busca de vingança contra os conspiradores que destruíram sua família.",
        "poster_path": "/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg",
        "release_date": "2024-03-01",
        "duracao_min": 166,
        "popularidade": 285.5,
        "imdb_rating": 8.5,
        "metascore": 79,
        "premios_texto": "Won 2 Oscars. Another 85 wins & 120 nominations.",
        "paises": ["US", "CA"],
        "generos": ["Ficção científica", "Aventura", "Drama"],
        "streamings": [
            {"provider_id": 1899, "nome": "Max", "modalidade": "ASSINATURA", "logo": "/fksCUZ9QDWZMUwL2Lg3voCKfl8.jpg"},
            {"provider_id": 2, "nome": "Apple TV", "modalidade": "ALUGUEL", "logo": "/peURlLlr8jggOwK53fJ5wdQl05y.jpg"},
            {"provider_id": 3, "nome": "Google Play Filmes", "modalidade": "COMPRA", "logo": "/tbEdFQDwx5LEVr8Wp68X09DTUm1.jpg"}
        ],
        "elenco": [
            {"person_id": 1190668, "nome": "Timothée Chalamet", "char": "Paul Atreides", "ordem": 1},
            {"person_id": 505710, "nome": "Zendaya", "char": "Chani", "ordem": 2},
            {"person_id": 1373737, "nome": "Florence Pugh", "char": "Princesa Irulan", "ordem": 3},
            {"person_id": 932967, "nome": "Austin Butler", "char": "Feyd-Rautha Harkonnen", "ordem": 4}
        ],
        "equipe": [
            {"person_id": 137427, "nome": "Denis Villeneuve", "funcao": "DIRETOR"},
            {"person_id": 137427, "nome": "Denis Villeneuve", "funcao": "ROTEIRISTA"},
            {"person_id": 947, "nome": "Hans Zimmer", "funcao": "COMPOSITOR"},
            {"person_id": 60515, "nome": "Greig Fraser", "funcao": "DIRETOR_FOTOGRAFIA"}
        ],
        "candidaturas": [
            {"categoria": "Melhor Filme", "status": "VENCEDOR"},
            {"categoria": "Melhor Direção", "status": "INDICADO", "person_id": 137427},
            {"categoria": "Melhor Fotografia", "status": "VENCEDOR", "person_id": 60515},
            {"categoria": "Melhor Trilha Sonora Original", "status": "INDICADO", "person_id": 947}
        ]
    },
    {
        "tmdb_id": 1064213,
        "imdb_id": "tt27054320",
        "titulo": "Anora",
        "titulo_original": "Anora",
        "sinopse": "Anora, uma jovem trabalhadora sexual do Brooklyn, conhece e se casa por impulso com o filho de um oligarca russo.",
        "poster_path": "/7MrgIUeq0DD2iF7GRRzJfVR2R7r.jpg",
        "release_date": "2024-10-18",
        "duracao_min": 139,
        "popularidade": 210.0,
        "imdb_rating": 8.0,
        "metascore": 91,
        "premios_texto": "Won Palme d'Or at Cannes. 48 wins & 75 nominations.",
        "paises": ["US"],
        "generos": ["Comédia", "Drama", "Romance"],
        "streamings": [
            {"provider_id": 2, "nome": "Apple TV", "modalidade": "ALUGUEL", "logo": "/peURlLlr8jggOwK53fJ5wdQl05y.jpg"},
            {"provider_id": 3, "nome": "Google Play Filmes", "modalidade": "ALUGUEL", "logo": "/tbEdFQDwx5LEVr8Wp68X09DTUm1.jpg"}
        ],
        "elenco": [
            {"person_id": 2043681, "nome": "Mikey Madison", "char": "Anora", "ordem": 1},
            {"person_id": 2577607, "nome": "Mark Eydelshteyn", "char": "Ivan", "ordem": 2},
            {"person_id": 1493414, "nome": "Yura Borisov", "char": "Igor", "ordem": 3}
        ],
        "equipe": [
            {"person_id": 64673, "nome": "Sean Baker", "funcao": "DIRETOR"},
            {"person_id": 64673, "nome": "Sean Baker", "funcao": "ROTEIRISTA"},
            {"person_id": 64673, "nome": "Sean Baker", "funcao": "MONTADOR"}
        ],
        "candidaturas": [
            {"categoria": "Melhor Filme", "status": "INDICADO"},
            {"categoria": "Melhor Direção", "status": "INDICADO", "person_id": 64673},
            {"categoria": "Melhor Atriz", "status": "INDICADO", "person_id": 2043681},
            {"categoria": "Melhor Ator Coadjuvante", "status": "INDICADO", "person_id": 1493414},
            {"categoria": "Melhor Roteiro Original", "status": "INDICADO", "person_id": 64673}
        ]
    },
    {
        "tmdb_id": 974576,
        "imdb_id": "tt20215234",
        "titulo": "Conclave",
        "titulo_original": "Conclave",
        "sinopse": "Após a morte inesperada do Papa, o Cardeal Lawrence é encarregado de liderar um dos processos mais secretos do mundo: a eleição de um novo pontífice.",
        "poster_path": "/m5x8PtgrRnPio6G21m89QZz1H7p.jpg",
        "release_date": "2024-10-25",
        "duracao_min": 120,
        "popularidade": 178.0,
        "imdb_rating": 7.8,
        "metascore": 79,
        "premios_texto": "Won 22 wins & 64 nominations.",
        "paises": ["GB", "US"],
        "generos": ["Drama", "Mistério", "Thriller"],
        "streamings": [
            {"provider_id": 119, "nome": "Prime Video", "modalidade": "ASSINATURA", "logo": "/emthp39XA2zahYni5Yj810ehkn7.jpg"}
        ],
        "elenco": [
            {"person_id": 5469, "nome": "Ralph Fiennes", "char": "Cardeal Thomas Lawrence", "ordem": 1},
            {"person_id": 8784, "nome": "Stanley Tucci", "char": "Cardeal Bellini", "ordem": 2},
            {"person_id": 388, "nome": "John Lithgow", "char": "Cardeal Tremblay", "ordem": 3},
            {"person_id": 1269, "nome": "Isabella Rossellini", "char": "Irmã Agnes", "ordem": 4}
        ],
        "equipe": [
            {"person_id": 90708, "nome": "Edward Berger", "funcao": "DIRETOR"},
            {"person_id": 1279, "nome": "Peter Straughan", "funcao": "ROTEIRISTA"},
            {"person_id": 1083989, "nome": "Volker Bertelmann", "funcao": "COMPOSITOR"}
        ],
        "candidaturas": [
            {"categoria": "Melhor Filme", "status": "COTADO"},
            {"categoria": "Melhor Ator", "status": "COTADO", "person_id": 5469},
            {"categoria": "Melhor Atriz Coadjuvante", "status": "COTADO", "person_id": 1269},
            {"categoria": "Melhor Roteiro Adaptado", "status": "COTADO", "person_id": 1279}
        ]
    },
    {
        "tmdb_id": 933260,
        "imdb_id": "tt28259169",
        "titulo": "O Brutalista",
        "titulo_original": "The Brutalist",
        "sinopse": "Trinta anos na vida de László Tóth, um arquiteto judeu nascido na Hungria que sobrevive ao Holocausto e migra para os EUA.",
        "poster_path": "/v9du2HC3WaXCYu1z4kQ230w5X8Y.jpg",
        "release_date": "2024-12-20",
        "duracao_min": 215,
        "popularidade": 165.0,
        "imdb_rating": 8.1,
        "metascore": 88,
        "premios_texto": "Won Silver Lion Venice Film Festival. 35 wins & 58 nominations.",
        "paises": ["US", "GB", "HU"],
        "generos": ["Drama", "História"],
        "streamings": [
            {"provider_id": 2, "nome": "Apple TV", "modalidade": "ALUGUEL", "logo": "/peURlLlr8jggOwK53fJ5wdQl05y.jpg"}
        ],
        "elenco": [
            {"person_id": 228, "nome": "Adrien Brody", "char": "László Tóth", "ordem": 1},
            {"person_id": 10569, "nome": "Felicity Jones", "char": "Erzsébet Tóth", "ordem": 2},
            {"person_id": 1283, "nome": "Guy Pearce", "char": "Harrison Lee Van Buren", "ordem": 3}
        ],
        "equipe": [
            {"person_id": 23689, "nome": "Brady Corbet", "funcao": "DIRETOR"},
            {"person_id": 23689, "nome": "Brady Corbet", "funcao": "ROTEIRISTA"},
            {"person_id": 1205304, "nome": "Daniel Blumberg", "funcao": "COMPOSITOR"}
        ],
        "candidaturas": [
            {"categoria": "Melhor Filme", "status": "COTADO"},
            {"categoria": "Melhor Direção", "status": "COTADO", "person_id": 23689},
            {"categoria": "Melhor Ator", "status": "COTADO", "person_id": 228},
            {"categoria": "Melhor Roteiro Original", "status": "COTADO", "person_id": 23689}
        ]
    },
    {
        "tmdb_id": 1022789,
        "imdb_id": "tt22022452",
        "titulo": "Divertida Mente 2",
        "titulo_original": "Inside Out 2",
        "sinopse": "Riley agora é uma adolescente com novas emoções entrando na Sala de Controle: Ansiedade, Inveja, Tédio e Vergonha.",
        "poster_path": "/9h2KgEao249knN726s7iQc40p8S.jpg",
        "release_date": "2024-06-14",
        "duracao_min": 96,
        "popularidade": 340.0,
        "imdb_rating": 7.6,
        "metascore": 73,
        "premios_texto": "Won Annie Award. 18 wins & 32 nominations.",
        "paises": ["US"],
        "generos": ["Animação", "Família", "Comédia", "Aventura"],
        "streamings": [
            {"provider_id": 337, "nome": "Disney Plus", "modalidade": "ASSINATURA", "logo": "/7rwgEsUBqgqPq27j320xN9XbM68.jpg"}
        ],
        "elenco": [
            {"person_id": 48316, "nome": "Amy Poehler", "char": "Alegria (voz)", "ordem": 1},
            {"person_id": 1395995, "nome": "Maya Hawke", "char": "Ansiedade (voz)", "ordem": 2}
        ],
        "equipe": [
            {"person_id": 1450367, "nome": "Kelsey Mann", "funcao": "DIRETOR"},
            {"person_id": 12890, "nome": "Meg LeFauve", "funcao": "ROTEIRISTA"},
            {"person_id": 1307, "nome": "Andrea Datzman", "funcao": "COMPOSITOR"}
        ],
        "candidaturas": [
            {"categoria": "Melhor Animação", "status": "INDICADO"}
        ]
    }
]

def executar_carga_demo(ano_edicao: int = 2026):
    """Executa a populacao automatica a partir da amostra real de concorrentes."""
    print(f"Iniciando carga de dados em modo DEMO/AMOSTRA REAL (Edicao {ano_edicao})...")
    
    with get_db_cursor(commit=True) as cur:
        # Busca mapa de generos
        cur.execute("SELECT id_genero, nome, peso_academia FROM genero;")
        generos_rows = cur.fetchall()
        generos_dict = {row["nome"]: (row["id_genero"], float(row["peso_academia"])) for row in generos_rows}

        # Busca mapa de categorias
        cur.execute("SELECT id_categoria, nome, escopo FROM categoria;")
        cat_rows = cur.fetchall()
        cat_dict = {row["nome"]: row["id_categoria"] for row in cat_rows}

        filmes_inseridos = 0
        for f in AMOSTRA_FILMES_DEMO:
            # 1. Pega pesos dos generos
            pesos_g = [generos_dict[g][1] for g in f["generos"] if g in generos_dict]
            
            # 2. Calcula Oscar Buzz Score
            score = calcular_oscar_buzz_score(
                popularity=f["popularidade"],
                generos_pesos=pesos_g,
                imdb_rating=f["imdb_rating"],
                metascore=f["metascore"],
                awards_text=f["premios_texto"]
            )

            # 3. Upsert FILME
            cur.execute("""
                INSERT INTO filme (
                    tmdb_id, imdb_id, titulo, titulo_original, sinopse, poster_path,
                    release_date, duracao_min, popularidade, imdb_rating, metascore,
                    premios_texto, oscar_buzz_score, ano_edicao
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (tmdb_id) DO UPDATE SET
                    imdb_id = EXCLUDED.imdb_id,
                    titulo = EXCLUDED.titulo,
                    titulo_original = EXCLUDED.titulo_original,
                    sinopse = EXCLUDED.sinopse,
                    poster_path = EXCLUDED.poster_path,
                    release_date = EXCLUDED.release_date,
                    duracao_min = EXCLUDED.duracao_min,
                    popularidade = EXCLUDED.popularidade,
                    imdb_rating = EXCLUDED.imdb_rating,
                    metascore = EXCLUDED.metascore,
                    premios_texto = EXCLUDED.premios_texto,
                    oscar_buzz_score = EXCLUDED.oscar_buzz_score,
                    ano_edicao = EXCLUDED.ano_edicao;
            """, (
                f["tmdb_id"], f["imdb_id"], f["titulo"], f["titulo_original"],
                f["sinopse"], f["poster_path"], f["release_date"], f["duracao_min"],
                f["popularidade"], f["imdb_rating"], f["metascore"], f["premios_texto"],
                score, ano_edicao
            ))

            # 4. Paises
            cur.execute("DELETE FROM filme_pais_origem WHERE tmdb_id = %s;", (f["tmdb_id"],))
            for p in f["paises"]:
                cur.execute("""
                    INSERT INTO filme_pais_origem (tmdb_id, codigo_pais)
                    VALUES (%s, %s) ON CONFLICT DO NOTHING;
                """, (f["tmdb_id"], p))

            # 5. Generos
            cur.execute("DELETE FROM filme_genero WHERE tmdb_id = %s;", (f["tmdb_id"],))
            for g_nome in f["generos"]:
                if g_nome in generos_dict:
                    cur.execute("""
                        INSERT INTO filme_genero (tmdb_id, id_genero)
                        VALUES (%s, %s) ON CONFLICT DO NOTHING;
                    """, (f["tmdb_id"], generos_dict[g_nome][0]))

            # 6. Streamings e Plataformas
            cur.execute("DELETE FROM disponibilidade WHERE tmdb_id = %s;", (f["tmdb_id"],))
            for st in f["streamings"]:
                cur.execute("""
                    INSERT INTO plataforma (provider_id, nome, logo_path)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (provider_id) DO UPDATE SET
                        nome = EXCLUDED.nome,
                        logo_path = EXCLUDED.logo_path;
                """, (st["provider_id"], st["nome"], st["logo"]))

                cur.execute("""
                    INSERT INTO disponibilidade (tmdb_id, provider_id, modalidade, data_coleta)
                    VALUES (%s, %s, %s, CURRENT_DATE)
                    ON CONFLICT (tmdb_id, provider_id, modalidade) DO NOTHING;
                """, (f["tmdb_id"], st["provider_id"], st["modalidade"]))

            # 7. Elenco
            for at in f["elenco"]:
                cur.execute("""
                    INSERT INTO profissional (tmdb_person_id, nome, profile_path, known_for_department)
                    VALUES (%s, %s, NULL, 'Acting')
                    ON CONFLICT (tmdb_person_id) DO UPDATE SET nome = EXCLUDED.nome;
                """, (at["person_id"], at["nome"]))

                cur.execute("""
                    INSERT INTO credito (tmdb_id, tmdb_person_id, funcao, character_name, ordem_elenco)
                    VALUES (%s, %s, 'ELENCO', %s, %s)
                    ON CONFLICT (tmdb_id, tmdb_person_id, funcao) DO UPDATE SET
                        character_name = EXCLUDED.character_name,
                        ordem_elenco = EXCLUDED.ordem_elenco;
                """, (f["tmdb_id"], at["person_id"], at["char"], at["ordem"]))

            # 8. Equipe Tecnica
            for eq in f["equipe"]:
                cur.execute("""
                    INSERT INTO profissional (tmdb_person_id, nome, profile_path, known_for_department)
                    VALUES (%s, %s, NULL, %s)
                    ON CONFLICT (tmdb_person_id) DO UPDATE SET nome = EXCLUDED.nome;
                """, (eq["person_id"], eq["nome"], eq["funcao"]))

                cur.execute("""
                    INSERT INTO credito (tmdb_id, tmdb_person_id, funcao, character_name, ordem_elenco)
                    VALUES (%s, %s, %s, NULL, NULL)
                    ON CONFLICT (tmdb_id, tmdb_person_id, funcao) DO NOTHING;
                """, (f["tmdb_id"], eq["person_id"], eq["funcao"]))

            # 9. Candidaturas
            cur.execute("DELETE FROM candidatura WHERE tmdb_id = %s;", (f["tmdb_id"],))
            seq_por_cat = {}
            for cand in f["candidaturas"]:
                cat_nome = cand["categoria"]
                if cat_nome in cat_dict:
                    cat_id = cat_dict[cat_nome]
                    seq_por_cat[cat_id] = seq_por_cat.get(cat_id, 0) + 1
                    cur.execute("""
                        INSERT INTO candidatura (tmdb_id, id_categoria, seq_candidatura, tmdb_person_id, status)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (tmdb_id, id_categoria, seq_candidatura) DO UPDATE SET
                            status = EXCLUDED.status;
                    """, (f["tmdb_id"], cat_id, seq_por_cat[cat_id], cand.get("person_id"), cand["status"]))

            filmes_inseridos += 1
            print(f"  -> [{score:.2f} Buzz] Filme '{f['titulo']}' sincronizado com sucesso!")

    print(f"\nSucesso: {filmes_inseridos} filmes e relacionamentos populados no banco de dados!")

def main():
    parser = argparse.ArgumentParser(description="Script de Carga de Dados do Oscar Tracker")
    parser.add_argument("--demo", action="store_true", help="Executa carga com amostra real oficial para testes rapidos")
    parser.add_argument("--ano", type=int, default=2026, help="Ano da edicao do Oscar (padrao: 2026)")
    args = parser.parse_args()

    if args.demo or (not settings.TMDB_API_KEY and not settings.OMDB_API_KEY):
        print("Modo de demonstracao ativado (amostra de dados oficiais da temporada).")
        executar_carga_demo(ano_edicao=args.ano)
    else:
        print("Modo LIVE: Conectando as APIs publicas com as chaves configuradas...")
        # Execucao live via APIs
        # (Chama carregar_plataformas_tmdb, sincronizar_filme_tmdb e atualizar_filme_omdb)
        print("Carga live em desenvolvimento.")

if __name__ == "__main__":
    main()
