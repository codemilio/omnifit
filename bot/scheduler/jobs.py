"""Agendamento de lembretes proativos."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from shared.config import get_settings


def build_scheduler() -> AsyncIOScheduler:
    """Scheduler em memória no fuso do usuário. Jobs entram nas tarefas de módulo."""
    return AsyncIOScheduler(timezone=get_settings().timezone)
