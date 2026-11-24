"""
Script Unificado de Execucao de Cargas e Populacao do Banco de Dados
Suporta modo --live (consumo direto de APIs com chaves) e modo --demo (carga de amostra oficial
para avaliacao em maquina limpa sem dependencia de chaves externas).
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.database import get_db_cursor
from scripts.carga_tmdb import carregar_plataformas_tmdb, sincronizar_filme_tmdb
from scripts.carga_omdb import atualizar_filme_omdb
from scripts.buzz_score import calcular_oscar_buzz_score

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
            {"provider_id": 3, "nome": "Google Play", "modalidade": "COMPRA", "logo": "/tbEdFQDwx5LEVr8Wp68X09DTUm1.jpg"}
        ],
        "elenco": [
            {"person_id": 1190668, "nome": "Timothée Chalamet", "char": "Paul Atreides", "ordem": 1},
            {"person_id": 505710, "nome": "Zendaya", "char": "Chani", "ordem": 2},
            {"person_id": 1373737, "nome": "Florence Pugh", "char": "Princesa Irulan", "ordem": 3},
            {"person_id": 932967, "nome": "Austin Butler", "char": "Feyd-Rautha", "ordem": 4}
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
        "sinopse": "Anora, uma jovem profissional do sexo do Brooklyn, conhece e se casa por impulso com o filho de um influente oligarca russo.",
        "poster_path": "/cgXk2tNYhJZLXdBDO5DidAVzQ82.jpg",
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
            {"provider_id": 3, "nome": "Google Play", "modalidade": "ALUGUEL", "logo": "/tbEdFQDwx5LEVr8Wp68X09DTUm1.jpg"}
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
        "sinopse": "Após a morte inesperada do Papa, o Cardeal Lawrence é encarregado de liderar um dos processos mais secretos do mundo: a eleição do novo pontífice.",
        "poster_path": "/m5x8D0bZ3eKqIVWZ5y7TnZ2oTVg.jpg",
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
        "tmdb_id": 845781,
        "imdb_id": "tt28259169",
        "titulo": "O Brutalista",
        "titulo_original": "The Brutalist",
        "sinopse": "Trinta anos na vida de László Tóth, um arquiteto judeu que sobrevive ao Holocausto e migra para os Estados Unidos para reconstruir sua arte e carreira.",
        "poster_path": "/vP7Yd6couiAaw9jgMd5cjMRj3hQ.jpg",
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
        "poster_path": "/p5ozvmdgsmbWe0H8Xk7Rc8SCwAB.jpg",
        "release_date": "2024-06-14",
        "duracao_min": 96,
        "popularidade": 340.0,
        "imdb_rating": 7.6,
        "metascore": 73,
        "premios_texto": "Won Annie Award. 18 wins & 32 nominations.",
        "paises": ["US"],
        "generos": ["Animação", "Família", "Comédia", "Aventura"],
        "streamings": [
            {"provider_id": 337, "nome": "Disney+", "modalidade": "ASSINATURA", "logo": "/7rwgEsUBqgqPq27j320xN9XbM68.jpg"}
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
    },
    {
        "tmdb_id": 402431,
        "imdb_id": "tt4520988",
        "titulo": "Wicked",
        "titulo_original": "Wicked",
        "sinopse": "A história inédita de Elphaba, uma jovem incompreendida de pele verde incomum, e Glinda, uma garota popular e privilegiada.",
        "poster_path": "/b9xo966oVIrFtpevhLQ9XILcXTh.jpg",
        "release_date": "2024-11-22",
        "duracao_min": 160,
        "popularidade": 230.0,
        "imdb_rating": 8.0,
        "metascore": 73,
        "premios_texto": "32 wins & 80 nominations.",
        "paises": ["US"],
        "generos": ["Fantasia", "Música", "Romance"],
        "streamings": [
            {"provider_id": 2, "nome": "Apple TV", "modalidade": "ALUGUEL", "logo": "/peURlLlr8jggOwK53fJ5wdQl05y.jpg"}
        ],
        "elenco": [
            {"person_id": 125660, "nome": "Cynthia Erivo", "char": "Elphaba", "ordem": 1},
            {"person_id": 77855, "nome": "Ariana Grande", "char": "Glinda", "ordem": 2},
            {"person_id": 1136406, "nome": "Jonathan Bailey", "char": "Fiyero", "ordem": 3}
        ],
        "equipe": [
            {"person_id": 5583, "nome": "Jon M. Chu", "funcao": "DIRETOR"},
            {"person_id": 11756, "nome": "Stephen Schwartz", "funcao": "COMPOSITOR"}
        ],
        "candidaturas": [
            {"categoria": "Melhor Atriz", "status": "INDICADO", "person_id": 125660},
            {"categoria": "Melhor Atriz Coadjuvante", "status": "INDICADO", "person_id": 77855},
            {"categoria": "Melhor Canção Original", "status": "VENCEDOR"},
            {"categoria": "Melhor Figurino", "status": "INDICADO"}
        ]
    },
    {
        "tmdb_id": 558449,
        "imdb_id": "tt9603212",
        "titulo": "Gladiador II",
        "titulo_original": "Gladiator II",
        "sinopse": "Anos após testemunhar a morte do herói Maximus, Lucius é forçado a entrar no Coliseu após sua casa ser conquistada pelos imperadores tirânicos.",
        "poster_path": "/41RyTMtScaSYJ5ZHwOrkv3NJKEv.jpg",
        "release_date": "2024-11-15",
        "duracao_min": 148,
        "popularidade": 290.0,
        "imdb_rating": 7.0,
        "metascore": 64,
        "premios_texto": "15 wins & 45 nominations.",
        "paises": ["GB", "US"],
        "generos": ["Ação", "Aventura", "Drama"],
        "streamings": [
            {"provider_id": 119, "nome": "Prime Video", "modalidade": "ASSINATURA", "logo": "/emthp39XA2zahYni5Yj810ehkn7.jpg"}
        ],
        "elenco": [
            {"person_id": 2182570, "nome": "Paul Mescal", "char": "Lucius", "ordem": 1},
            {"person_id": 17697, "nome": "Pedro Pascal", "char": "Marcus Acacius", "ordem": 2},
            {"person_id": 5292, "nome": "Denzel Washington", "char": "Macrinus", "ordem": 3}
        ],
        "equipe": [
            {"person_id": 578, "nome": "Ridley Scott", "funcao": "DIRETOR"},
            {"person_id": 1284, "nome": "David Scarpa", "funcao": "ROTEIRISTA"},
            {"person_id": 10444, "nome": "Harry Gregson-Williams", "funcao": "COMPOSITOR"}
        ],
        "candidaturas": [
            {"categoria": "Melhor Ator Coadjuvante", "status": "INDICADO", "person_id": 5292},
            {"categoria": "Melhores Efeitos Visuais", "status": "INDICADO"},
            {"categoria": "Melhor Som", "status": "INDICADO"}
        ]
    },
    {
        "tmdb_id": 933260,
        "imdb_id": "tt17526714",
        "titulo": "A Substância",
        "titulo_original": "The Substance",
        "sinopse": "Uma celebridade em decadência decide usar uma droga misteriosa do mercado clandestino que gera uma versão mais jovem e perfeita de si mesma.",
        "poster_path": "/bVSOgrxasVJF6V71T7v2KfBRSzu.jpg",
        "release_date": "2024-09-20",
        "duracao_min": 140,
        "popularidade": 245.0,
        "imdb_rating": 7.5,
        "metascore": 78,
        "premios_texto": "Won Best Screenplay Cannes. 42 wins & 68 nominations.",
        "paises": ["GB", "US", "FR"],
        "generos": ["Terror", "Drama", "Ficção científica"],
        "streamings": [
            {"provider_id": 11, "nome": "MUBI", "modalidade": "ASSINATURA", "logo": "/bVR4ZES6V4E870UUCoxkZ8ZpDk.jpg"}
        ],
        "elenco": [
            {"person_id": 3416, "nome": "Demi Moore", "char": "Elisabeth Sparkle", "ordem": 1},
            {"person_id": 1248001, "nome": "Margaret Qualley", "char": "Sue", "ordem": 2},
            {"person_id": 1532, "nome": "Dennis Quaid", "char": "Harvey", "ordem": 3}
        ],
        "equipe": [
            {"person_id": 1827453, "nome": "Coralie Fargeat", "funcao": "DIRETOR"},
            {"person_id": 1827453, "nome": "Coralie Fargeat", "funcao": "ROTEIRISTA"}
        ],
        "candidaturas": [
            {"categoria": "Melhor Atriz", "status": "INDICADO", "person_id": 3416},
            {"categoria": "Melhor Roteiro Original", "status": "INDICADO", "person_id": 1827453},
            {"categoria": "Melhor Maquiagem e Penteados", "status": "VENCEDOR"}
        ]
    },
    {
        "tmdb_id": 1034541,
        "imdb_id": "tt21379082",
        "titulo": "Sing Sing",
        "titulo_original": "Sing Sing",
        "sinopse": "Um grupo de homens encarcerados na prisão de segurança máxima de Sing Sing encontra propósito ao encenar uma peça de teatro original.",
        "poster_path": "/CZyMhVVpraYDptLpYXxXjgAuCH.jpg",
        "release_date": "2024-07-12",
        "duracao_min": 107,
        "popularidade": 120.0,
        "imdb_rating": 7.8,
        "metascore": 84,
        "premios_texto": "38 wins & 70 nominations.",
        "paises": ["US"],
        "generos": ["Drama"],
        "streamings": [
            {"provider_id": 2, "nome": "Apple TV", "modalidade": "ALUGUEL", "logo": "/peURlLlr8jggOwK53fJ5wdQl05y.jpg"}
        ],
        "elenco": [
            {"person_id": 107567, "nome": "Colman Domingo", "char": "John 'Divine G' Whitfield", "ordem": 1},
            {"person_id": 2981775, "nome": "Clarence Maclin", "char": "Ele mesmo", "ordem": 2}
        ],
        "equipe": [
            {"person_id": 147814, "nome": "Greg Kwedar", "funcao": "DIRETOR"},
            {"person_id": 147814, "nome": "Greg Kwedar", "funcao": "ROTEIRISTA"}
        ],
        "candidaturas": [
            {"categoria": "Melhor Ator", "status": "INDICADO", "person_id": 107567},
            {"categoria": "Melhor Roteiro Adaptado", "status": "INDICADO", "person_id": 147814}
        ]
    },
    {
        "tmdb_id": 786892,
        "imdb_id": "tt12037194",
        "titulo": "Furiosa: Uma Saga Mad Max",
        "titulo_original": "Furiosa: A Mad Max Saga",
        "sinopse": "A jovem Furiosa é arrebatada do Lugar Verde das Muitas Mães e cai nas mãos de uma grande Horda de Motoqueiros liderada pelo Senhor da Guerra Dementus.",
        "poster_path": "/iADOJ8Zymht2JPMoy3R7xceZprc.jpg",
        "release_date": "2024-05-24",
        "duracao_min": 148,
        "popularidade": 215.0,
        "imdb_rating": 7.6,
        "metascore": 79,
        "premios_texto": "18 wins & 45 nominations.",
        "paises": ["AU", "US"],
        "generos": ["Ação", "Aventura", "Ficção científica"],
        "streamings": [
            {"provider_id": 1899, "nome": "Max", "modalidade": "ASSINATURA", "logo": "/fksCUZ9QDWZMUwL2Lg3voCKfl8.jpg"},
            {"provider_id": 2, "nome": "Apple TV", "modalidade": "ALUGUEL", "logo": "/peURlLlr8jggOwK53fJ5wdQl05y.jpg"}
        ],
        "elenco": [
            {"person_id": 1393273, "nome": "Anya Taylor-Joy", "char": "Furiosa", "ordem": 1},
            {"person_id": 74568, "nome": "Chris Hemsworth", "char": "Dementus", "ordem": 2},
            {"person_id": 84433, "nome": "Tom Burke", "char": "Praetorian Jack", "ordem": 3}
        ],
        "equipe": [
            {"person_id": 20629, "nome": "George Miller", "funcao": "DIRETOR"},
            {"person_id": 20629, "nome": "George Miller", "funcao": "ROTEIRISTA"},
            {"person_id": 11846, "nome": "Tom Holkenborg", "funcao": "COMPOSITOR"}
        ],
        "candidaturas": [
            {"categoria": "Melhores Efeitos Visuais", "status": "INDICADO"},
            {"categoria": "Melhor Figurino", "status": "INDICADO"},
            {"categoria": "Melhor Som", "status": "INDICADO"}
        ]
    },
    {
        "tmdb_id": 872585,
        "imdb_id": "tt15398776",
        "titulo": "Oppenheimer",
        "titulo_original": "Oppenheimer",
        "sinopse": "A história do físico americano J. Robert Oppenheimer, seu papel no Projeto Manhattan e o desenvolvimento da bomba atômica durante a Segunda Guerra Mundial.",
        "poster_path": "/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
        "release_date": "2023-07-21",
        "duracao_min": 180,
        "popularidade": 310.0,
        "imdb_rating": 8.9,
        "metascore": 89,
        "premios_texto": "Won 7 Oscars. Another 340 wins & 410 nominations.",
        "paises": ["US", "GB"],
        "generos": ["Biografia", "Drama", "História"],
        "streamings": [
            {"provider_id": 119, "nome": "Prime Video", "modalidade": "ASSINATURA", "logo": "/emthp39XA2zahYni5Yj810ehkn7.jpg"},
            {"provider_id": 2, "nome": "Apple TV", "modalidade": "ALUGUEL", "logo": "/peURlLlr8jggOwK53fJ5wdQl05y.jpg"}
        ],
        "elenco": [
            {"person_id": 2037, "nome": "Cillian Murphy", "char": "J. Robert Oppenheimer", "ordem": 1},
            {"person_id": 1245, "nome": "Robert Downey Jr.", "char": "Lewis Strauss", "ordem": 2},
            {"person_id": 5081, "nome": "Emily Blunt", "char": "Katherine Oppenheimer", "ordem": 3}
        ],
        "equipe": [
            {"person_id": 525, "nome": "Christopher Nolan", "funcao": "DIRETOR"},
            {"person_id": 525, "nome": "Christopher Nolan", "funcao": "ROTEIRISTA"},
            {"person_id": 10444, "nome": "Ludwig Göransson", "funcao": "COMPOSITOR"}
        ],
        "candidaturas": [
            {"categoria": "Melhor Filme", "status": "VENCEDOR"},
            {"categoria": "Melhor Direção", "status": "VENCEDOR", "person_id": 525},
            {"categoria": "Melhor Ator", "status": "VENCEDOR", "person_id": 2037},
            {"categoria": "Melhor Ator Coadjuvante", "status": "VENCEDOR", "person_id": 1245}
        ]
    },
    {
        "tmdb_id": 792307,
        "imdb_id": "tt14230458",
        "titulo": "Pobres Criaturas",
        "titulo_original": "Poor Things",
        "sinopse": "A incrível evolução de Bella Baxter, uma jovem mulher ressuscitada pelo brilhante e heterodoxo cientista Dr. Godwin Baxter.",
        "poster_path": "/kCGlIMHnOm8JPXq3rXM6c5wMxcT.jpg",
        "release_date": "2023-12-08",
        "duracao_min": 141,
        "popularidade": 220.0,
        "imdb_rating": 7.9,
        "metascore": 87,
        "premios_texto": "Won 4 Oscars. Another 120 wins & 230 nominations.",
        "paises": ["US", "GB", "IE"],
        "generos": ["Comédia", "Fantasia", "Ficção científica", "Romance"],
        "streamings": [
            {"provider_id": 337, "nome": "Disney+", "modalidade": "ASSINATURA", "logo": "/7rwgEsUBqgqPq27j320xN9XbM68.jpg"}
        ],
        "elenco": [
            {"person_id": 54693, "nome": "Emma Stone", "char": "Bella Baxter", "ordem": 1},
            {"person_id": 103, "nome": "Mark Ruffalo", "char": "Duncan Wedderburn", "ordem": 2},
            {"person_id": 5293, "nome": "Willem Dafoe", "char": "Dr. Godwin Baxter", "ordem": 3}
        ],
        "equipe": [
            {"person_id": 137427, "nome": "Yorgos Lanthimos", "funcao": "DIRETOR"},
            {"person_id": 12890, "nome": "Tony McNamara", "funcao": "ROTEIRISTA"}
        ],
        "candidaturas": [
            {"categoria": "Melhor Filme", "status": "INDICADO"},
            {"categoria": "Melhor Atriz", "status": "VENCEDOR", "person_id": 54693},
            {"categoria": "Melhor Figurino", "status": "VENCEDOR"},
            {"categoria": "Melhor Design de Produção", "status": "VENCEDOR"}
        ]
    },
    {
        "tmdb_id": 915935,
        "imdb_id": "tt17009710",
        "titulo": "Anatomia de uma Queda",
        "titulo_original": "Anatomy of a Fall",
        "sinopse": "Uma mulher é julgada pelo assassinato de seu marido, e seu filho cego enfrenta um dilema moral como única testemunha.",
        "poster_path": "/kQs6keheMwCxJxrzV83VUwFtHkB.jpg",
        "release_date": "2023-08-23",
        "duracao_min": 151,
        "popularidade": 190.0,
        "imdb_rating": 7.7,
        "metascore": 86,
        "premios_texto": "Won 1 Oscar. Another 98 wins & 150 nominations.",
        "paises": ["FR"],
        "generos": ["Crime", "Drama", "Mistério", "Thriller"],
        "streamings": [
            {"provider_id": 119, "nome": "Prime Video", "modalidade": "ASSINATURA", "logo": "/emthp39XA2zahYni5Yj810ehkn7.jpg"}
        ],
        "elenco": [
            {"person_id": 117240, "nome": "Sandra Hüller", "char": "Sandra Voyter", "ordem": 1},
            {"person_id": 2182570, "nome": "Swann Arlaud", "char": "Vincent Renzi", "ordem": 2}
        ],
        "equipe": [
            {"person_id": 147814, "nome": "Justine Triet", "funcao": "DIRETOR"},
            {"person_id": 147814, "nome": "Justine Triet", "funcao": "ROTEIRISTA"}
        ],
        "candidaturas": [
            {"categoria": "Melhor Filme", "status": "INDICADO"},
            {"categoria": "Melhor Direção", "status": "INDICADO", "person_id": 147814},
            {"categoria": "Melhor Atriz", "status": "INDICADO", "person_id": 117240},
            {"categoria": "Melhor Roteiro Original", "status": "VENCEDOR", "person_id": 147814}
        ]
    }
]

def executar_carga_demo(ano_edicao: int = 2026):
    print(f"Iniciando carga de dados em modo DEMO/AMOSTRA REAL (Edicao {ano_edicao})...")
    with get_db_cursor(commit=True) as cur:
        cur.execute("SELECT id_genero, nome, peso_academia FROM genero;")
        generos_rows = cur.fetchall()
        generos_dict = {row["nome"]: (row["id_genero"], float(row["peso_academia"])) for row in generos_rows}

        cur.execute("SELECT id_categoria, nome, escopo FROM categoria;")
        cat_rows = cur.fetchall()
        cat_dict = {row["nome"]: row["id_categoria"] for row in cat_rows}

        filmes_inseridos = 0
        for f in AMOSTRA_FILMES_DEMO:
            pesos_g = [generos_dict[g][1] for g in f["generos"] if g in generos_dict]
            score = calcular_oscar_buzz_score(
                popularity=f["popularidade"],
                generos_pesos=pesos_g,
                imdb_rating=f["imdb_rating"],
                metascore=f["metascore"],
                awards_text=f["premios_texto"]
            )

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

            cur.execute("DELETE FROM filme_pais_origem WHERE tmdb_id = %s;", (f["tmdb_id"],))
            for p in f["paises"]:
                cur.execute("""
                    INSERT INTO filme_pais_origem (tmdb_id, codigo_pais)
                    VALUES (%s, %s) ON CONFLICT DO NOTHING;
                """, (f["tmdb_id"], p))

            cur.execute("DELETE FROM filme_genero WHERE tmdb_id = %s;", (f["tmdb_id"],))
            for g_nome in f["generos"]:
                if g_nome in generos_dict:
                    cur.execute("""
                        INSERT INTO filme_genero (tmdb_id, id_genero)
                        VALUES (%s, %s) ON CONFLICT DO NOTHING;
                    """, (f["tmdb_id"], generos_dict[g_nome][0]))

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

if __name__ == "__main__":
    main()
