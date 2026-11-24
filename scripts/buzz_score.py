import math
import re
from typing import List, Optional

def extrair_vitorias_indicacoes(awards_text: Optional[str]) -> tuple[int, int]:
    """
    Extrai quantidade de vitorias e indicacoes do texto livre da OMDb.
    Exemplo: 'Won 3 Oscars. Another 45 wins & 62 nominations.' -> (48, 62)
    """
    if not awards_text or awards_text.strip().upper() in ("N/A", ""):
        return 0, 0

    vitorias = 0
    indicacoes = 0

    # Contagem de Oscars ganhos
    match_oscar_won = re.search(r'Won\s+(\d+)\s+Oscar', awards_text, re.IGNORECASE)
    if match_oscar_won:
        vitorias += int(match_oscar_won.group(1))

    # Outras vitorias
    match_wins = re.search(r'(\d+)\s+win', awards_text, re.IGNORECASE)
    if match_wins:
        vitorias += int(match_wins.group(1))

    # Indicacoes ao Oscar
    match_oscar_nom = re.search(r'Nominated for\s+(\d+)\s+Oscar', awards_text, re.IGNORECASE)
    if match_oscar_nom:
        indicacoes += int(match_oscar_nom.group(1))

    # Outras indicacoes
    match_noms = re.search(r'(\d+)\s+nomination', awards_text, re.IGNORECASE)
    if match_noms:
        indicacoes += int(match_noms.group(1))

    return vitorias, indicacoes

def calcular_oscar_buzz_score(
    popularity: float,
    generos_pesos: List[float],
    imdb_rating: Optional[float] = None,
    metascore: Optional[int] = None,
    awards_text: Optional[str] = None
) -> float:
    """
    Calcula o indice Oscar Buzz Score (0.00 a 100.00) conforme especificado
    na Secao 4.3.1 (pagina 32) do documento do projeto.
    
    Formula geral com redistribuicao proporcional de pesos:
    score = sum(peso_i * valor_i) / sum(peso_i) para componentes nao-nulos.
    
    Componentes e pesos base:
      C (Critica / Metascore): 0.35
      F (Premios preliminares): 0.20 -> min(100, 10 * V + 3 * I)
      G (Genero): 0.20 -> media(pesos dos generos) * 100
      A (Publico / IMDb): 0.15 -> imdb_rating * 10
      P (Popularidade): 0.10 -> min(100, ln(1 + pop) / ln(1 + 500) * 100)
    """
    valores = {}
    pesos_base = {
        'C': 0.35,
        'F': 0.20,
        'G': 0.20,
        'A': 0.15,
        'P': 0.10
    }

    # 1. G - Genero (Sempre existe, RN2)
    if generos_pesos:
        media_genero = sum(generos_pesos) / len(generos_pesos)
    else:
        media_genero = 0.50 # Peso neutro
    valores['G'] = max(0.0, min(100.0, media_genero * 100.0))

    # 2. P - Popularidade (Sempre existe, RN1)
    pop = max(0.0, float(popularity or 0.0))
    val_p = (math.log(1.0 + pop) / math.log(1.0 + 500.0)) * 100.0
    valores['P'] = max(0.0, min(100.0, val_p))

    # 3. C - Critica / Metascore (Opcional)
    if metascore is not None and metascore >= 0:
        valores['C'] = max(0.0, min(100.0, float(metascore)))

    # 4. A - Publico / IMDb (Opcional)
    if imdb_rating is not None and imdb_rating >= 0:
        valores['A'] = max(0.0, min(100.0, float(imdb_rating) * 10.0))

    # 5. F - Premios preliminares (Opcional, se awards_text estiver presente)
    if awards_text and awards_text.strip().upper() not in ("N/A", ""):
        vitorias, indicacoes = extrair_vitorias_indicacoes(awards_text)
        val_f = min(100.0, (10.0 * vitorias) + (3.0 * indicacoes))
        valores['F'] = val_f

    # Calculo ponderado com soma dos pesos dos componentes disponiveis
    soma_ponderada = sum(pesos_base[comp] * valores[comp] for comp in valores)
    soma_pesos = sum(pesos_base[comp] for comp in valores)

    if soma_pesos == 0:
        return 0.0

    score = soma_ponderada / soma_pesos
    return round(max(0.0, min(100.0, score)), 2)
