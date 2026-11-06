"""Testes de fumaça da API e do metadata dos modelos."""

from fastapi.testclient import TestClient

from api.main import app
from shared.models import SQLModel

EXPECTED_TABLES = {
    "users",
    "workout_sessions",
    "workout_photos",
    "water_logs",
    "meal_logs",
    "tasks",
    "task_completions",
    "notification_settings",
}


def test_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_renders() -> None:
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "Omnifit" in response.text


def test_models_registered() -> None:
    assert EXPECTED_TABLES.issubset(SQLModel.metadata.tables)
