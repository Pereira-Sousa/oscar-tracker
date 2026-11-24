# Oscar Tracker 🎬🏆

> **Monitor Analítico e Rastreador de Filmes para a Temporada do Oscar**  
> Projeto desenvolvido para a disciplina de Banco de Dados (IMD0401) — Bacharelado em Tecnologia da Informação (IMD / UFRN).

---

## 📌 Visão Geral

O **Oscar Tracker** é uma solução centralizada que resolve a dispersão de informações durante a temporada de premiações cinematográficas. O sistema cataloga longas-metragens elegíveis ao Oscar a partir de dados públicos (TMDB e OMDb), acompanha onde cada obra está disponível no mercado brasileiro (streaming, aluguel e compra) e consolida a probabilidade competitiva de cada produção por meio de uma métrica proprietária: o **Oscar Buzz Score**.

### Principais Funcionalidades Implementadas
* **Linha do Tempo da Temporada (C1):** Exibição cronológica dos filmes elegíveis mês a mês, separando obras já lançadas de estreias futuras, com filtros combinados por plataforma de streaming, gênero, faixa de nota e ordenações via índice.
* **Ficha Técnica & Curadoria (C2):** Modal interativo exibindo sinopse, notas consolidadas (IMDb e Metascore), decomposição do Oscar Buzz Score, elenco principal (Top 10), direção e catálogo onde assistir no Brasil.
* **Radar de Premiações (C3):** Acompanhamento em tempo real das categorias do Oscar (filme e individuais), exibindo profissionais e títulos cotados, indicados oficiais e vencedores.
* **Opções de Filtro Dinâmicas (C4):** Listas consolidadas diretamente do banco com edições, gêneros, plataformas e categorias.
* **Ingestão Automatizada de Dados (A5/A6/A7):** Sincronização e cruzamento periódico entre a API do TMDB e da OMDb com garantias transacionais e tolerância a falhas.

---

## 🛠️ Stack Tecnológica

* **Banco de Dados:** [PostgreSQL 16](https://www.postgresql.org/) (Modelagem relacional normalizada em 3FN, transações ACID e índices otimizados).
* **Backend:** [Python 3.11+](https://www.python.org/) com [FastAPI](https://fastapi.tiangolo.com/) e driver nativo `psycopg` para execução direta de consultas SQL (sem ORM ocultando a lógica).
* **Frontend:** Interface Web leve renderizada pelo servidor com HTML5, Jinja2 e estilização moderna via [Tailwind CSS](https://tailwindcss.com/) e [Lucide Icons](https://lucide.dev/).
* **Infraestrutura:** Containerização completa via [Docker Compose](https://docs.docker.com/compose/).

---

## 📁 Estrutura do Projeto

```text
oscar-tracker/
├── app/
│   ├── static/           # Arquivos estáticos (CSS customizado, JS assíncrono para o modal C2)
│   ├── templates/        # Templates Jinja2 (base.html, index.html, radar.html)
│   ├── config.py         # Configurações e variáveis de ambiente
│   ├── database.py       # Conexão e pool de sessões PostgreSQL (psycopg3)
│   └── main.py           # Aplicação FastAPI com consultas SQL nativas (C1, C2, C3, C4)
├── database/
│   ├── ddl.sql           # Esquema relacional DDL (3FN), chaves e restrições CHECK
│   ├── indices.sql       # Índices B-Tree e parciais para otimização de C1 a C4
│   └── seed.sql          # Carga inicial de edições, categorias e gêneros com pesos
├── scripts/
│   ├── buzz_score.py     # Algoritmo matemático de cálculo do Oscar Buzz Score
│   ├── carga_tmdb.py     # Ingestão de filmes, créditos, datas e provedores BR
│   ├── carga_omdb.py     # Coleta de notas críticas, prêmios e recálculo
│   └── executar_carga.py # Script unificado de carga (suporta --live e --demo)
├── docker-compose.yml    # Orquestração do PostgreSQL e volumes
├── requirements.txt      # Dependências Python
├── .env.example          # Modelo de variáveis de ambiente
└── README.md             # Documentação do projeto
```

---

## 🚀 Como Executar em Máquina Limpa (Passo a Passo)

### 1. Clonar o Repositório e Configurar Ambiente
```bash
git clone https://github.com/Pereira-Sousa/oscar-tracker.git
cd oscar-tracker

# Copiar arquivo de variáveis de ambiente
cp .env.example .env
```

---

### 2. Inicializar o Banco de Dados (PostgreSQL 16)

#### Opção A: Via Docker Compose (Mais Recomendado)
O `docker-compose.yml` inicializa automaticamente o PostgreSQL 16 e executa na primeira inicialização o DDL (`01_ddl.sql`), os índices (`02_indices.sql`) e a carga inicial de referência (`03_seed.sql`):
```bash
docker compose up -d
```

#### Opção B: Via PostgreSQL Local
Caso possua PostgreSQL local instalado:
```bash
createdb -U postgres oscar_tracker
psql -U postgres -d oscar_tracker -f database/ddl.sql
psql -U postgres -d oscar_tracker -f database/indices.sql
psql -U postgres -d oscar_tracker -f database/seed.sql
```

---

### 3. Instalar Dependências Python
```bash
python -m venv venv

# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# Instalar pacotes
pip install -r requirements.txt
```

---

### 4. Popular o Banco de Dados

#### A. Carga Imediata de Avaliação (`--demo`)
> **Recomendado para correção imediata do trabalho:** Popula o banco com obras reais da temporada 2026 (Duna: Parte 2, Anora, Conclave, O Brutalista, Divertida Mente 2) com notas, streamings no Brasil, elenco e candidaturas:
```bash
python scripts/executar_carga.py --demo
```

#### B. Carga em Tempo Real via APIs (`--live`)
Caso informe suas chaves no `.env` (`TMDB_API_KEY` e `OMDB_API_KEY`):
```bash
python scripts/executar_carga.py --ano 2026
```

---

### 5. Iniciar a Aplicação Web
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Acesse no seu navegador:  
👉 **`http://localhost:8000`**

* **`/`** — Painel Linha do Tempo da Temporada (Função C1 e filtros C4) e Modal da Ficha Técnica (Função C2).
* **`/radar`** — Radar Oficial de Premiações por Categoria (Função C3).
* **`/api/filmes/{tmdb_id}`** — Retorno em JSON estruturado da ficha técnica completa.

---

## 🧮 Algoritmo do Oscar Buzz Score

Implementado em `scripts/buzz_score.py`, o índice consolidado varia de `0.00` a `100.00` e pondera 5 componentes de acordo com a proximidade histórica com as escolhas da Academia:

$$\text{Score} = \frac{\sum (Peso_i \times Valor_i)}{\sum Peso_i}$$

| Componente | Métrica Utilizada | Peso Base | Normalização (0 a 100) |
| :--- | :--- | :---: | :--- |
| **C (Crítica)** | Metascore | 0.35 | Valor nominal do Metascore (0 a 100) |
| **F (Prêmios)** | Histórico OMDb | 0.20 | $\min(100, 10 \times \text{Vitórias} + 3 \times \text{Indicações})$ |
| **G (Gênero)** | Afinidade Histórica | 0.20 | Média dos pesos dos gêneros da obra $\times 100$ |
| **A (Público)** | Nota IMDb | 0.15 | $\text{imdb\_rating} \times 10$ |
| **P (Popularidade)**| TMDB Popularity | 0.10 | $\min\left(100, \frac{\ln(1 + \text{pop})}{\ln(1 + 500)} \times 100\right)$ |

---

## 📐 Projeto de Dados & Normalização (3FN)

O esquema relacional implementado em `database/ddl.sql` segue rigorosamente a **Terceira Forma Normal (3FN)**:
1. **1FN:** Todos os atributos são atômicos. O atributo multivalorado de países de origem de um filme foi decomposto na relação `filme_pais_origem (tmdb_id, codigo_pais)`.
2. **2FN:** Está em 1FN e nenhum atributo não-chave depende de parte de uma chave primária composta (como em `candidatura` e `disponibilidade`).
3. **3FN:** Está em 2FN e todos os atributos não-chave dependem exclusivamente e diretamente da chave primária (sem dependências transitivas).

---

## 🌿 Política de Versionamento (Git Flow)

Este repositório adota um fluxo de trabalho baseado em branches de funcionalidade para garantir rastreabilidade e integridade do código:
* `main`: Branch de produção / código estável e auditado.
* `feature/<nome-da-etapa>`: Cópias temporárias derivadas de `main` onde o desenvolvimento de cada entrega/módulo é realizado.
* **Regra de Integração:** Nenhuma alteração é comitada diretamente na `main`. Todo novo recurso é desenvolvido em uma branch de funcionalidade e integrado à `main` via merge formal (`git merge --no-ff`).

---

## 👥 Equipe do Projeto

* Clécio Gabriel de Oliveira Felix
* Lucas Emanuel da Paz Ribeiro
* Lucas Pereira de Sousa
* Vitor Fraifer Palhano dos Anjos

*Universidade Federal do Rio Grande do Norte (UFRN) — Instituto Metrópole Digital (IMD)*
