"""Modelos SQLModel. Fonte única do schema, compartilhada por bot e api."""

from datetime import UTC, date, datetime, time
from typing import Any

from sqlalchemy import DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(UTC)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int = Field(unique=True, index=True)
    name: str = ""
    timezone: str = "America/Sao_Paulo"
    # Metas de água/treino e preferências gerais
    settings: dict[str, Any] = Field(default_factory=dict, sa_type=JSONB)
    created_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))


class WorkoutSession(SQLModel, table=True):
    __tablename__ = "workout_sessions"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    performed_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))
    raw_input: str = ""
    source: str = "text"  # text | audio
    # [{name, sets, reps, weight_kg}]
    exercises: list[dict[str, Any]] = Field(default_factory=list, sa_type=JSONB)
    notes: str | None = None
    created_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))


class WorkoutPhoto(SQLModel, table=True):
    __tablename__ = "workout_photos"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    file_path: str  # relativo ao volume media/
    caption: str | None = None
    taken_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))
    created_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))


class WaterLog(SQLModel, table=True):
    __tablename__ = "water_logs"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    amount_ml: int
    source: str = "manual"  # manual | reminder
    logged_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))


class MealLog(SQLModel, table=True):
    __tablename__ = "meal_logs"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    meal_type: str = "other"  # breakfast | lunch | snack | dinner | other
    description: str
    logged_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    title: str
    recurrence: str = "none"  # none | daily | weekly
    recurrence_days: list[int] = Field(default_factory=list, sa_type=JSONB)  # 0=segunda
    scheduled_date: date | None = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))


class TaskCompletion(SQLModel, table=True):
    __tablename__ = "task_completions"

    id: int | None = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="tasks.id", index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    completed_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))


class NotificationSetting(SQLModel, table=True):
    __tablename__ = "notification_settings"
    __table_args__ = (UniqueConstraint("user_id", "type", name="uq_notification_user_type"),)

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    type: str  # morning_summary | water | workout | task_reminder | night_summary
    time_of_day: time | None = None
    interval_minutes: int | None = None
    enabled: bool = True
    updated_at: datetime = Field(default_factory=utcnow, sa_type=DateTime(timezone=True))
