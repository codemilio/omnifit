"""Configuração carregada do ambiente (`.env` em desenvolvimento)."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Telegram — obrigatório apenas para o bot
    bot_token: str = ""

    # Postgres
    database_url: str = "postgresql+asyncpg://omnifit:omnifit@localhost:5432/omnifit"

    # IA
    groq_api_key: str = ""

    # Aplicação
    timezone: str = "America/Sao_Paulo"

    # Dashboard / Caddy (lidos pelo compose, não pelo Python)
    domain: str = ""
    basic_auth_user: str = ""
    basic_auth_hash: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()
