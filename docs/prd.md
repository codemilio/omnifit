# PRD — Omnifit

Versão 1.0 · 05/11/2026 · Carlos

Documento de produto: o quê e por quê. Decisões técnicas ficam em [spec.md](spec.md); execução em [tasks.md](tasks.md).

## 1. Visão

Omnifit é um sistema pessoal de rotina com o Telegram como interface de entrada e um dashboard web para acompanhamento. O usuário registra treino, água, refeições e tarefas por texto ou áudio, envia fotos de evolução e recebe lembretes proativos nos horários que definir.

**Problema:** manter consistência de hábitos sem depender de memória ou de apps que ninguém abre. O Telegram já está aberto o dia todo — o registro acontece onde o usuário já está.

**Público inicial:** uma pessoa com rotina irregular, retomando o treino, que quer centralizar o registro em uma única interface conversacional.

## 2. Objetivos e métricas

| Objetivo | Métrica | Meta (MVP) |
| --- | --- | --- |
| Uso consistente | Dias com ao menos 1 registro na semana | ≥ 5 |
| Cobertura de hábitos | Módulos usados por dia | Treino + água + refeição + 1 tarefa |
| Latência de texto | Resposta do bot | < 2 s |
| Latência de áudio | Resposta do bot | < 10 s |
| Retenção de dados | Uptime do servidor | ≥ 99 % |
| Histórico | Registros visíveis no dashboard | 100 % |

**Critério de saída do MVP:** 2 semanas de uso diário pessoal sem queda crítica, todos os módulos funcionando pelo bot e dashboard somente leitura no ar.

## 3. Personas

**Fase 1 — uso solo.** Desenvolvedor e estudante, trabalho das 6h às 20h com alguma flexibilidade. Registra em texto rápido, manda áudio do treino logo depois de terminar, confirma água quando lembrado, adiciona tarefas pela manhã e consulta o dashboard à noite no PC.

**Fase 2 — multi-usuário.** Perfil semelhante, não necessariamente desenvolvedor. Exige onboarding auto-explicativo e isolamento de dados. A modelagem já nasce com `user_id` em todas as tabelas.

## 4. Escopo do MVP

### 4.1 Treino (texto e áudio)

O usuário descreve o treino. Áudio é transcrito, o texto passa por um LLM que extrai exercícios, séries, repetições e carga em JSON. Antes de salvar, o bot mostra o resultado e pede confirmação (`✅ Confirmar` / `✏️ Editar`). Se o parsing falhar, salva o texto bruto e pede confirmação manual.

`input → (Whisper se áudio) → parser → confirmação inline → banco`

Campos salvos: data/hora, exercícios, texto original, origem (`text`/`audio`), notas.

### 4.2 Fotos de evolução

O usuário envia uma foto com legenda opcional. O arquivo é salvo localmente na VPS, registrado no banco com data e legenda, e aparece em galeria cronológica no dashboard.

### 4.3 Água

- **Lembrete:** o bot envia uma mensagem a cada intervalo configurado (padrão 1h, entre 08h e 20h) com `✅ Bebi` / `⏭️ Pular`. Confirmar registra a quantidade padrão (padrão 300 ml).
- **Manual:** `agua 250` ou `bebi 2 copos` a qualquer momento.

O bot responde com o total do dia contra a meta configurada.

### 4.4 Refeições

Log por texto, sem parsing nutricional no MVP. O tipo (café, almoço, lanche, jantar, ceia) é inferido pelo horário ou explicitado pelo usuário.

`almoço: arroz, feijão, frango grelhado, salada`

### 4.5 Tarefas

- **Criação:** `tarefa: ligar para a faculdade` ou `tarefa toda segunda: relatório semanal`
- **Recorrência:** nenhuma, diária ou semanal (dias específicos)
- **Cobrança:** às 21h (configurável) o bot envia as pendentes com botão de check
- **Consulta:** `/tarefas` lista as de hoje

### 4.6 Notificações proativas

| Tipo | Padrão | Configurável |
| --- | --- | --- |
| Resumo da manhã | 07:00 | sim |
| Lembrete de água | 1h, 08h–20h | sim |
| Lembrete de treino | horário do usuário | sim |
| Cobrança de tarefas | 21:00 | sim |
| Resumo noturno | 22:00 | sim (opcional) |

## 5. Fora de escopo

| Item | Fase | Motivo |
| --- | --- | --- |
| Plano de treino periodizado | 2 | Exige modelagem própria; MVP é treino livre |
| Plano alimentar e macros | 2 | Depende de base nutricional |
| Contagem de calorias | 2 | Complexidade de entrada alta |
| Multi-usuário com auth | 2 | Isolamento, onboarding e suporte |
| Exportação CSV | 2 | Útil, não crítico |
| Wearables | 3 | Depende de APIs de terceiros |
| Gamificação (streaks) | 3 | Não muda o valor central |
| App nativo | 3 | Telegram resolve o mobile |

## 6. Jornadas principais

**Áudio do treino.** Envia áudio → bot transcreve → parser devolve JSON → bot mostra resumo e botões → confirma → salvo → resposta com resumo compacto.

**Água.** Scheduler dispara → bot pergunta com botões → confirma/pula/outra quantidade → bot mostra total do dia.

**Tarefa noturna.** 21h → bot lista pendentes com check por item → usuário marca → conclusão registrada.

**Resumo da manhã.** 07h → bot agrega tarefas do dia, meta de água e horário do treino → mensagem única.

## 7. Requisitos não funcionais

| Categoria | Requisito |
| --- | --- |
| Performance | Texto < 2 s; áudio < 10 s; dashboard < 3 s na primeira carga |
| Disponibilidade | Containers com restart automático |
| Backup | `pg_dump` diário, retenção 30 dias; diretório de fotos com backup separado |
| Privacidade | Áudio e texto processados pela Groq no MVP; troca para IA local prevista |
| Segurança | HTTPS obrigatório no dashboard; Basic Auth; segredos fora do git |
| Fuso horário | Todo cálculo no timezone do usuário (`America/Sao_Paulo`), nunca no da VPS |
| Observabilidade | Logs estruturados no stdout, coletados pelo Docker |
| Manutenção | Uma migração Alembic por mudança de schema |

## 8. Roadmap

| Fase | Entrega |
| --- | --- |
| 0 | Scaffolding, docs, infra, bot e API mínimos |
| 1 | Água → refeições → tarefas → treino texto → áudio → fotos → dashboard |
| 2 | Multi-usuário, auth, planos configuráveis, CSV, onboarding |
| 3 | Wearables, macros, gamificação, PDF, análise por IA |

Ordem da Fase 1 é por risco, não por importância: scheduler e fluxo de confirmação primeiro; áudio depois de o fluxo de texto estar estável (reusa o mesmo parser).

## 9. Riscos

| Risco | Mitigação |
| --- | --- |
| Parser LLM devolve JSON inválido | `response_format=json_object` + fallback para texto bruto |
| VPS pequena sem RAM | Sem modelo local no MVP; Groq via HTTP |
| Fuso horário errado em lembretes | `zoneinfo` do usuário em todo agendamento; nunca `datetime.now()` ingênuo |
| Escopo crescer antes do uso real | Fase 1 só entrega os 6 módulos; resto é Fase 2+ |
| Dependência de biblioteca sem manutenção | Versões pinadas; ver critérios em spec.md |
