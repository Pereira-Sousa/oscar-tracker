# Oscar Tracker 🎬🏆

> **Monitor Analítico e Rastreador de Filmes para a Temporada do Oscar**  
> Projeto desenvolvido para a disciplina de Banco de Dados (IMD0401) — Bacharelado em Tecnologia da Informação (IMD / UFRN).

---

## 📌 Visão Geral

O **Oscar Tracker** é uma solução centralizada que resolve a dispersão de informações durante a temporada de premiações cinematográficas. O sistema cataloga longas-metragens elegíveis ao Oscar a partir de dados públicos (TMDB e OMDb), acompanha onde cada obra está disponível no mercado brasileiro (streaming, aluguel e compra) e consolida a probabilidade competitiva de cada produção por meio de uma métrica proprietária: o **Oscar Buzz Score**.

### Principais Funcionalidades
* **Linha do Tempo da Temporada (C1):** Exibição cronológica dos filmes elegíveis mês a mês, separando obras já lançadas de estreias futuras, com filtros combinados por plataforma de streaming, gênero e faixa de nota.
* **Ficha Técnica & Curadoria (C2):** Visão detalhada de cada título com sinopse, notas consolidadas (IMDb e Metascore), algoritmo do Oscar Buzz Score, elenco principal, direção e plataformas disponíveis no Brasil.
* **Radar de Premiações (C3):** Acompanhamento em tempo real das categorias do Oscar (filme e individuais), exibindo profissionais e títulos cotados, indicados oficiais e vencedores.
* **Ingestão Automatizada de Dados (A5/A6/A7):** Sincronização e cruzamento periódico entre a API do TMDB e da OMDb com garantias transacionais e tolerância a falhas.

---

## 🛠️ Stack Tecnológica

* **Banco de Dados:** [PostgreSQL 16](https://www.postgresql.org/) (Modelagem relacional normalizada em 3FN, transações ACID e índices otimizados).
* **Backend:** [Python 3.11+](https://www.python.org/) com [FastAPI](https://fastapi.tiangolo.com/) e driver nativo `psycopg` para execução direta de consultas SQL.
* **Frontend:** Interface Web leve renderizada pelo servidor com HTML5, Jinja2 e estilização via [Tailwind CSS](https://tailwindcss.com/).
* **Infraestrutura:** Containerização completa via [Docker Compose](https://docs.docker.com/compose/).

---

## 📁 Estrutura do Projeto

```text
oscar-tracker/
├── app/
│   ├── static/           # Arquivos estáticos (CSS customizado, imagens)
│   ├── templates/        # Templates Jinja2 (HTML + Tailwind CSS)
│   ├── config.py         # Configurações e variáveis de ambiente
│   ├── database.py       # Conexão e pool de sessões PostgreSQL
│   └── main.py           # Aplicação principal FastAPI e rotas web
├── database/
│   ├── ddl.sql           # Esquema relacional DDL (3FN), chaves e restrições CHECK
│   ├── indices.sql       # Índices B-Tree e parciais para otimização de C1 a C4
│   └── seed.sql          # Carga inicial de edições, categorias e gêneros com pesos
├── scripts/
│   ├── carga_tmdb.py     # Ingestão de filmes, créditos e provedores
│   ├── carga_omdb.py     # Coleta de notas críticas e prêmios
│   └── buzz_score.py     # Algoritmo de cálculo do Oscar Buzz Score
├── docker-compose.yml    # Orquestração do PostgreSQL e volumes
├── requirements.txt      # Dependências Python
├── .env.example          # Modelo de variáveis de ambiente
└── README.md             # Documentação do projeto
```

---

## 🚀 Como Inicializar o Projeto (Passo a Passo)

### 1. Pré-requisitos
* Git instalado
* Docker e Docker Compose instalados (Recomendado) **OU** PostgreSQL 16 instalado localmente
* Python 3.11+ (para execução da aplicação e scripts)

---

### 2. Configuração das Variáveis de Ambiente
Copie o arquivo de exemplo `.env.example` para `.env`:
```bash
cp .env.example .env
```
Abra o arquivo `.env` e configure suas variáveis:
```ini
# Configurações do Banco de Dados
POSTGRES_USER=oscar_user
POSTGRES_PASSWORD=oscar_secret
POSTGRES_DB=oscar_tracker
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Chaves das APIs Públicas (TMDB e OMDb)
TMDB_API_KEY=sua_chave_aqui
OMDB_API_KEY=sua_chave_aqui
```

---

### 3. Inicialização do Banco de Dados

#### Opção A: Via Docker Compose (Mais Rápido e Isolado)
O `docker-compose.yml` já está configurado para inicializar automaticamente o PostgreSQL 16 e executar todos os scripts na ordem correta (`01_ddl.sql`, `02_indices.sql` e `03_seed.sql`):
```bash
docker compose up -d
```
Para verificar se o container está rodando:
```bash
docker compose ps
```
Para conferir os logs do banco:
```bash
docker compose logs -f db
```

#### Opção B: Via PostgreSQL Local (psql)
Caso prefira usar o PostgreSQL instalado na sua máquina:
1. Crie o banco de dados:
   ```sql
   CREATE DATABASE oscar_tracker;
   ```
2. Execute os scripts na ordem:
   ```bash
   psql -U oscar_user -d oscar_tracker -f database/ddl.sql
   psql -U oscar_user -d oscar_tracker -f database/indices.sql
   psql -U oscar_user -d oscar_tracker -f database/seed.sql
   ```

---

### 4. Instalação das Dependências Python
Crie um ambiente virtual e instale os pacotes:
```bash
# Criar e ativar o ambiente virtual
python -m venv venv

# No Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# No Linux/macOS:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

---

## 📐 Projeto de Dados & Normalização (3FN)

O esquema relacional implementado em `database/ddl.sql` segue rigorosamente a **Terceira Forma Normal (3FN)**:
1. **Primeira Forma Normal (1FN):**
   * Todos os atributos são atômicos.
   * O atributo multivalorado de países de origem de um filme foi decomposto na tabela associativa `filme_pais_origem (tmdb_id, codigo_pais)`.
2. **Segunda Forma Normal (2FN):**
   * O esquema está em 1FN e nenhum atributo não-chave depende de parte de uma chave primária composta.
   * Em entidades fracas e associativas como `candidatura (tmdb_id, id_categoria, seq_candidatura)`, o atributo `status` depende da totalidade da chave composta.
3. **Terceira Forma Normal (3FN):**
   * O esquema está em 2FN e não existem dependências transitivas entre atributos não-chave.
   * Todos os atributos não-chave dependem direta e exclusivamente da chave primária (ex.: na tabela `filme`, `sinopse`, `popularidade` e `release_date` dependem de `tmdb_id`; dados de gênero e streaming foram normalizados em relações próprias).

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
