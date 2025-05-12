import base64
import io
import os

from openai import OpenAI

DEFAULT_MODEL = "gpt-4o-transcribe"  # For cheaper model, use "gpt-4o-mini-transcribe" for half the price


def _make_client() -> OpenAI:
    return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _bytes_from_b64(audio_b64: str) -> bytes:
    """Strip any data‑URL header and return raw bytes."""
    if audio_b64.startswith("data:"):
        audio_b64 = audio_b64.split(",", 1)[1]
    return base64.b64decode(audio_b64)


def transcribe_audio(audio_b64: str, model: str = DEFAULT_MODEL) -> str:
    if audio_b64.startswith("data:"):
        audio_b64 = audio_b64.split(",", 1)[1]
    buf = io.BytesIO(base64.b64decode(audio_b64))
    buf.name = "upload.mp3"
    resp = _make_client().audio.transcriptions.create(
        model=model,
        file=buf,
        response_format="text"
    )
    return resp.strip()
