"""Único ponto de acesso à IA.

Trocar Groq por modelo local (Whisper/Ollama) significa editar apenas este arquivo.
"""

import json
from typing import Any

from groq import AsyncGroq

from shared.config import get_settings

TRANSCRIBE_MODEL = "whisper-large-v3"
PARSE_MODEL = "llama-3.1-8b-instant"

PARSE_SYSTEM = (
    "Você extrai treinos de mensagens em português.\n"
    'Responda APENAS um objeto JSON válido: {"exercises": [{"name": string, '
    '"sets": int|null, "reps": int|null, "weight_kg": number|null}], '
    '"notes": string|null}\n'
    "Não invente exercícios que não estejam no texto. "
    'Se nada for identificável, retorne {"exercises": [], "notes": null}.'
)

_client: AsyncGroq | None = None


def _client() -> AsyncGroq:
    global _client
    if _client is None:
        _client = AsyncGroq(api_key=get_settings().groq_api_key)
    return _client


async def transcribe(audio: bytes, filename: str = "audio.ogg") -> str:
    """Transcreve áudio do Telegram (OGG/Opus) via Whisper."""
    result = await _client().audio.transcriptions.create(
        file=(filename, audio),
        model=TRANSCRIBE_MODEL,
        language="pt",
    )
    return result.text.strip()


async def parse_workout(text: str) -> dict[str, Any]:
    """Extrai exercícios estruturados de um texto livre."""
    result = await _client().chat.completions.create(
        model=PARSE_MODEL,
        messages=[
            {"role": "system", "content": PARSE_SYSTEM},
            {"role": "user", "content": text},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(result.choices[0].message.content or "{}")
