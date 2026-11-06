# Omnifit

Sistema pessoal de rotina: bot de Telegram para registro rápido (treino, água, refeições, tarefas, fotos) e dashboard web somente leitura.

- Produto: [docs/prd.md](docs/prd.md)
- Especificação técnica: [docs/spec.md](docs/spec.md)
- Backlog e convenção de commits: [docs/tasks.md](docs/tasks.md)

## Stack

Python 3.12 · aiogram 3 · FastAPI + Jinja2 + HTMX · SQLModel + Alembic · PostgreSQL · APScheduler 3 · Groq (Whisper + Llama) · Caddy · Docker Compose.

## Desenvolvimento local

```bash
uv sync                       # cria .venv e instala dependências
cp .env.example .env          # preencher BOT_TOKEN e GROQ_API_KEY

docker compose up -d db       # apenas o Postgres
uv run alembic upgrade head   # depois que existir a primeira migração
uv run uvicorn api.main:app --reload   # dashboard em http://localhost:8000
uv run python -m bot.main     # bot em polling
```

## Verificações

```bash
uv run ruff check .
uv run pytest
```

## Docker (stack completa)

```bash
docker compose up --build
```

Sobe `db`, `bot`, `api` e `caddy`. O Caddy expõe apenas a API/dashboard, com TLS automático e Basic Auth. Preencha `DOMAIN` e `BASIC_AUTH_HASH` no `.env` antes de subir.

## Estrutura

```
bot/        aiogram: handlers e scheduler
api/        FastAPI: routers, templates (Jinja), static
shared/     config, banco, modelos SQLModel, cliente Groq
migrations/ Alembic
docs/       prd.md, spec.md, tasks.md
```

## Convenção

Toda alteração pertence a uma tarefa de `docs/tasks.md` (ex.: `T-101`) e cada tarefa gera um commit:

```
tipo(escopo): descrição (T-000)
```

Tipos: `feat`, `fix`, `docs`, `build`, `chore`, `test`, `refactor`.

## Segurança

O arquivo `.env` nunca é versionado. Se um token vazar, revogue em @BotFather antes de qualquer `git push`.
