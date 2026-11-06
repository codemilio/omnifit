# Tarefas — Omnifit

Regra: **uma tarefa = um commit**. Toda alteração de código referencia o ID da tarefa na mensagem: `tipo(escopo): descrição (T-000)`.

**Definição de pronto:** código funcionando · migração Alembic se houver mudança de schema · teste executável se a lógica for não trivial · esta tabela atualizada · commit com o ID.

## Fase 0 — Scaffolding (concluída)

| ID | Tarefa | Aceite | Commit |
| --- | --- | --- | --- |
| T-001 | Bootstrap do repositório | `.gitignore` protegendo `.env`; scaffold TypeScript anterior removido; `git init` em `main` | `chore(repo): bootstrap do repositorio e remocao do scaffold TypeScript (T-001)` |
| T-002 | Documentação base | `prd.md`, `spec.md`, `tasks.md`, README e `.gitattributes` | `docs: PRD, especificacao tecnica e backlog (T-002)` |
| T-003 | Projeto Python com uv | `pyproject.toml`, `uv.lock`, `.python-version`, Ruff e pytest configurados; `uv sync` funciona | `build: projeto Python, dependencias e ferramentas (T-003)` |
| T-004 | Camada compartilhada | `config.py`, `db.py`, `models.py` com as 8 tabelas, `ai.py` com Groq; Alembic configurado | `feat(shared): config, banco, modelos e cliente Groq (T-004)` |
| T-005 | Bot mínimo | `/start` com teclado, `/ajuda`, fallback de texto, polling e scheduler instanciado | `feat(bot): entrypoint aiogram e menu inicial (T-005)` |
| T-006 | API e dashboard base | `/health`, `/health/db`, página inicial renderizada por Jinja; teste de fumaça | `feat(api): FastAPI, healthcheck e layout base (T-006)` |
| T-007 | Infraestrutura | Dockerfile multiestágio, compose com `db`/`bot`/`api`/`caddy`, Caddyfile com TLS e Basic Auth | `build(infra): Dockerfile, compose e Caddy (T-007)` |

## Fase 1 — MVP solo

Ordem por risco: scheduler e confirmação primeiro, áudio por último (reusa o parser do texto).

| ID | Tarefa | Escopo | Aceite | Commit |
| --- | --- | --- | --- | --- |
| T-101 | Água | Registro manual (`agua 250`, `bebi 2 copos`) + lembrete com botões inline e total do dia | Total correto após reinício; job dispara na janela configurada | `feat(water): registro manual e lembrete de agua (T-101)` |
| T-102 | Refeições | Log por texto com tipo inferido pelo horário | Refeição aparece com tipo e horário corretos | `feat(meals): registro de refeicoes por texto (T-102)` |
| T-103 | Tarefas | CRUD, recorrência diária/semanal, `/tarefas` e cobrança às 21h com check | Recorrente reaparece no dia certo; conclusão não duplica | `feat(tasks): tarefas, recorrencia e cobranca noturna (T-103)` |
| T-104 | Treino por texto | Parser Groq + confirmação inline + edição | JSON válido salvo; falha cai para texto bruto | `feat(workout): treino por texto com confirmacao (T-104)` |
| T-105 | Treino por áudio | Transcrição Groq + fluxo do T-104 | Áudio OGG do Telegram transcrito e salvo como `audio` | `feat(workout): treino por audio com transcricao (T-105)` |
| T-106 | Fotos de evolução | Download do arquivo, storage em `media/`, legenda | Foto listada com data após restart (volume persistente) | `feat(photos): fotos de evolucao fisica (T-106)` |
| T-107 | Dashboard read-only | Histórico de treino, refeições, água vs meta, tarefas, galeria | 5 telas com dados reais; Basic Auth ativo | `feat(dashboard): historico somente leitura (T-107)` |
| T-108 | Notificações e `/configurar` | Resumo da manhã, resumo noturno, lembrete de treino, edição de horários | Horários persistem e respeitam `America/Sao_Paulo` | `feat(notifications): resumos e configuracao de horarios (T-108)` |
| T-109 | CI/CD | GitHub Actions: lint + teste a cada push; deploy por SSH na `main` | Pipeline verde; deploy documentado linha a linha | `build(ci): pipeline de testes e deploy (T-109)` |

**Saída da Fase 1:** 2 semanas de uso diário, 6 módulos funcionando, dashboard no ar.

## Fase 2 — Multi-usuário

| ID | Tarefa | Aceite |
| --- | --- | --- |
| T-201 | Auth e isolamento | Login, sessão e todas as queries filtradas por `user_id` |
| T-202 | Onboarding conversacional | Novo usuário configurando metas pelo bot |
| T-203 | Plano de treino | Periodização simples por dia da semana |
| T-204 | Plano alimentar | Metas por refeição |
| T-205 | Exportação CSV | Treinos, água, refeições e tarefas |
| T-206 | Edição pelo dashboard | Escrita nas telas de água, refeições e tarefas |

## Fase 3 — Expansão

| ID | Tarefa |
| --- | --- |
| T-301 | Integração com wearables (Garmin / Apple Health) |
| T-302 | Macros e calorias (TACO / Open Food Facts) |
| T-303 | Gamificação: streaks e conquistas |
| T-304 | Relatórios em PDF |
| T-305 | Análise de evolução por IA |

## Backlog sem tarefa

Ideias ainda não comprometidas. Não geram commit até virarem tarefa numerada.

- Backup automatizado (`pg_dump` + `restic` para `media/`)
- Migrar `MemoryStorage` para storage persistente
- Webhook no lugar de polling (só se houver mais de uma instância)
- Modo IA local (`shared/ai.py` → Whisper/Ollama) se privacidade virar requisito
