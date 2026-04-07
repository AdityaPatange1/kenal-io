"""LLM engine backed by ollama — no model selection, auto-detect."""

from __future__ import annotations

import logging
import os
from typing import Any

import ollama as _ollama
from dotenv import load_dotenv

from kenal.exceptions import EngineError

load_dotenv()

logger = logging.getLogger(__name__)

_DEFAULT_HOST = "http://localhost:11434"


def _get_host() -> str:
    return os.getenv("KENAL_OLLAMA_HOST", _DEFAULT_HOST)


def _resolve_model() -> str:
    """Return the model to use: env override, or first model available on the host."""
    explicit = os.getenv("KENAL_MODEL")
    if explicit:
        return explicit
    try:
        client = _ollama.Client(host=_get_host())
        listing = client.list()
        if listing and listing.models:
            return str(listing.models[0].model)
    except Exception:
        logger.debug("Could not auto-detect model, falling back to default")
    return "llama3.2"


def generate(system: str, prompt: str, **kwargs: Any) -> str:
    """Run a single chat-style generation through ollama.

    Args:
        system: System-level instruction (compiled rules).
        prompt: User-level input payload.
        **kwargs: Extra arguments forwarded to ``ollama.Client.chat``.

    Returns:
        The assistant's reply as a plain string.

    Raises:
        EngineError: If the generation request fails.
    """
    host = _get_host()
    model = _resolve_model()
    logger.debug("engine.generate model=%s host=%s", model, host)
    try:
        client = _ollama.Client(host=host)
        response = client.chat(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            **kwargs,
        )
        content: str = response.message.content or ""
        return content
    except Exception as exc:
        raise EngineError(f"LLM generation failed: {exc}") from exc
