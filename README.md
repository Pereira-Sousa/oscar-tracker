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

* **Banco de Dados:** [PostgreSQL 16](https://www.postgresql.org/) (Modelagem relacional em 3FN, transações ACID e índices otimizados).
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
│   ├── ddl.sql           # Esquema relacional DDL (3FN) e restrições
│   ├── indices.sql       # Definição dos índices de performance
│   └── seed.sql          # Carga inicial de categorias, pesos e edições
├── scripts/
│   ├── carga_tmdb.py     # Ingestão de filmes, créditos e provedores
│   ├── carga_omdb.py     # Coleta de notas críticas e prêmios
│   └── buzz_score.py     # Algoritmo de cálculo do Oscar Buzz Score
├── docker-compose.yml    # Orquestração do PostgreSQL e serviços
├── requirements.txt      # Dependências Python
├── .env.example          # Modelo de variáveis de ambiente
└── README.md             # Documentação do projeto
```

---

## 🚀 Como Executar

### 1. Pré-requisitos
* Git
* Python 3.11+
* Docker & Docker Compose (ou instância PostgreSQL local)

### 2. Configuração do Ambiente
Clone o repositório e crie o arquivo de variáveis de ambiente:
```bash
cp .env.example .env
```
Preencha no `.env` suas credenciais do PostgreSQL e as chaves de API da **TMDB** e **OMDb**.

### 3. Inicialização com Docker Compose
```bash
# Sobe o banco de dados PostgreSQL
docker compose up -d

# Executa as migrações/DDL inicial e scripts de carga
# (Instruções detalhadas serão adicionadas a cada etapa)
```

---

## 🌿 Política de Versionamento (Git Flow)

Este repositório adota um fluxo de trabalho baseado em branches de funcionalidade para garantir rastreabilidade e integridade do código:
* `main`: Branch de produção / código estável e auditado.
* `feature/<nome-da-etapa>`: Cópias temporárias derivadas de `main` onde o desenvolvimento de cada entrega/módulo é realizado.
* **Regra de Integração:** Nenhuma alteração é comitada diretamente na `main`. Todo novo recurso é desenvolvido em uma branch de funcionalidade e integrado à `main` via merge formal.

---

## 👥 Equipe do Projeto

* Clécio Gabriel de Oliveira Felix
* Lucas Emanuel da Paz Ribeiro
* Lucas Pereira de Sousa
* Vitor Fraifer Palhano dos Anjos

*Universidade Federal do Rio Grande do Norte (UFRN) — Instituto Metrópole Digital (IMD)*
