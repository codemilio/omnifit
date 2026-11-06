# Especificação técnica — Omnifit

Como o sistema é construído. Produto em [prd.md](prd.md); execução em [tasks.md](tasks.md).

## 1. Stack

| Camada | Escolha | Versão |
| --- | --- | --- |
| Runtime | Python | 3.12 |
| Bot | aiogram | 3.31.x |
| API + dashboard | FastAPI + Jinja2 + HTMX | FastAPI 0.162.x |
| Banco | PostgreSQL | 17-alpine |
| ORM | SQLModel | 0.0.48.x |
| Migrações | Alembic | 1.20.x |
| Driver async | asyncpg | 0.32.x |
| Agendamento | APScheduler (`>=3.11,<4`) | 3.11.x |
| IA | SDK `groq` (Whisper + Llama) | 1.7.x |
| Config | pydantic-settings | 2.16.x |
| Proxy / TLS / Auth | Caddy 2 | 2-alpine |
| Pacotes | uv | 0.13.x |
| Lint / teste | ruff + pytest | — |

## 2. Arquitetura

```
Telegram ──polling──► bot (aiogram + APScheduler) ──┐
                                                    ├──► PostgreSQL
Navegador ──HTTPS──► Caddy ──► api (FastAPI+Jinja) ─┘
```

- `bot` faz **polling**. Não expõe porta; não depende de webhook, domínio ou secret token.
- `api` serve dashboard e futuras rotas de leitura/escrita.
- `caddy` é o único ponto público: TLS automático e Basic Auth.
- `db` é interno à rede do compose.

Containers: `bot`, `api`, `db`, `caddy`. Consumo estimado em repouso: 350–450 MB.

## 3. Estrutura

```
/
├── bot/
│   ├── main.py               entrypoint (polling)
│   ├── handlers/             um módulo por domínio
│   └── scheduler/jobs.py     jobs do APScheduler
├── api/
│   ├── main.py               app FastAPI
│   ├── templates/            Jinja2
│   └── static/               CSS, JS (htmx e Chart.js via CDN)
├── shared/
│   ├── config.py             Settings (pydantic-settings)
│   ├── db.py                 engine e sessão async
│   ├── models.py             modelos SQLModel
│   └── ai.py                 Groq: transcribe() e parse_workout()
├── migrations/               Alembic
├── tests/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── Caddyfile
└── pyproject.toml / uv.lock
```

## 4. Modelo de dados

Todas as tabelas usam `id` inteiro autoincremento e timestamps `timestamptz` em UTC. Conversão para o fuso do usuário acontece na borda (bot/dashboard).

| Tabela | Campos | Notas |
| --- | --- | --- |
| `users` | `telegram_id` (unique), `name`, `timezone`, `settings` (JSONB), `created_at` | `settings` guarda metas de água e treino |
| `workout_sessions` | `user_id`, `performed_at`, `raw_input`, `source`, `exercises` (JSONB), `notes` | `source`: `text` \| `audio` |
| `workout_photos` | `user_id`, `file_path`, `caption`, `taken_at` | `file_path` relativo ao volume `media/` |
| `water_logs` | `user_id`, `amount_ml`, `source`, `logged_at` | `source`: `manual` \| `reminder` |
| `meal_logs` | `user_id`, `meal_type`, `description`, `logged_at` | `meal_type`: breakfast \| lunch \| snack \| dinner \| other |
| `tasks` | `user_id`, `title`, `recurrence`, `recurrence_days` (JSONB), `scheduled_date`, `is_active` | `recurrence`: none \| daily \| weekly |
| `task_completions` | `task_id`, `user_id`, `completed_at` | uma linha por conclusão |
| `notification_settings` | `user_id`, `type`, `time_of_day`, `interval_minutes`, `enabled`, `updated_at` | unique (`user_id`, `type`) |

**Regras:**

- `exercises` é JSONB: `[{"name": str, "sets": int|null, "reps": int|null, "weight_kg": float|null}]`.
- Áudios não são persistidos; só transcrição e JSON.
- `users.settings` evita dezenas de colunas nulas. Normalizar só se necessário.
- `user_id` existe em todas as tabelas de domínio desde o MVP (isolamento da Fase 2 sem refatoração).

## 5. Contrato do bot (MVP)

| Entrada | Comportamento |
| --- | --- |
| `/start` | Saudação + teclado persistente (Treino, Dieta, Água, Tarefas) |
| `/ajuda` | Lista de comandos |
| `/tarefas` | Tarefas de hoje |
| `/configurar` | Menu de horários e metas |
| `agua 250` / `bebi 2 copos` | Registra água |
| `tarefa: ...` / `tarefa toda segunda: ...` | Cria tarefa |
| `almoço: ...` | Registra refeição |
| texto livre | Fluxo de treino (parser + confirmação) |
| áudio/voz | Transcrição → fluxo de treino |
| foto | Salva em `media/`, confirma |

Botões inline: `✅ Confirmar` / `✏️ Editar`; `✅ Bebi` / `⏭️ Pular`; check por tarefa.

## 6. Decisões técnicas

| ID | Decisão | Alternativa descartada | Motivo |
| --- | --- | --- | --- |
| D-01 | Python 3.12 + aiogram | Node/TypeScript + grammY | Fluência do autor domina o custo de manutenção em 3 fases |
| D-02 | Polling | Webhook + secret token | Dispensa domínio, nginx e validação de header; um processo menos exposto |
| D-03 | Caddy | nginx + Certbot | TLS automático e `basic_auth` em 3 linhas; sem cron de renovação |
| D-04 | Jinja2 + HTMX + Chart.js CDN | Next.js + shadcn + Recharts | Dashboard read-only não justifica segundo runtime nem build step |
| D-05 | Um módulo `shared/ai.py` | Abstração `Transcriber`/`Parser` + implementações local/Groq | A troca é editar um arquivo; 5 arquivos para uma troca hipotética é custo sem retorno |
| D-06 | PostgreSQL desde o dia 1 | SQLite e migrar depois | JSONB, concorrência bot/api e multi-tenant na Fase 2 |
| D-07 | APScheduler 3 | 4.x | 4.x é reescrita ainda instável; 3.11 tem jobstore e cron estáveis |
| D-08 | `MemoryStorage` no FSM | Redis | Estado de confirmação dura segundos; Redis é um serviço a mais para um usuário |
| D-09 | `uv` | pip + requirements.txt | Lockfile determinístico e resolução rápida |

## 7. Configuração

Variáveis em `.env` (ver `.env.example`): `BOT_TOKEN`, `DATABASE_URL`, `POSTGRES_*`, `GROQ_API_KEY`, `TZ`, `DOMAIN`, `BASIC_AUTH_USER`, `BASIC_AUTH_HASH`.

`shared/config.py` expõe `get_settings()` (cacheado). `BOT_TOKEN` é opcional na carga para permitir subir a API sem bot; `bot/main.py` aborta se estiver vazio.

## 8. Comandos

```bash
uv sync                                  # instala dependências
uv run ruff check .                      # lint
uv run pytest                            # testes
uv run alembic upgrade head              # aplica migrações
uv run alembic revision --autogenerate -m "descricao"
uv run uvicorn api.main:app --reload     # dashboard local
uv run python -m bot.main                # bot local
docker compose up --build                # stack completa
```

## 9. Convenções

- **Timezone:** `ZoneInfo(settings.timezone)` em todo agendamento e formatação. Nunca `datetime.now()` sem fuso.
- **Async:** handlers e rotas não bloqueiam; acesso ao banco via `AsyncSession` (`shared.db.get_session`).
- **Migrações:** autogenerate sempre revisado à mão (SQLModel/JSONB não é detectado por completo).
- **Teste:** toda lógica não trivial deixa um teste executável em `tests/`. Sem framework além de pytest.
- **Commit:** `tipo(escopo): descrição (T-000)`; um commit por tarefa de `docs/tasks.md`.

## 10. Limitações conhecidas

| Limitação | Efeito | Quando revisar |
| --- | --- | --- |
| `MemoryStorage` | Confirmação pendente se perde em restart | multi-usuário (Fase 2) |
| Groq na nuvem | áudio/texto saem da VPS | se privacidade virar requisito rígido: reescrever `shared/ai.py` |
| Polling | um único processo consome updates | múltiplas instâncias / escala |
| SQLModel 0.0.x | API pode mudar em minor | versão travada no `uv.lock` |
| Sem fila de jobs | uma instância de scheduler | múltiplos usuários com lembretes independentes |
