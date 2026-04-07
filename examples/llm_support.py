"""Shared helpers for LLM examples (Ollama reachability, skip / fail policy)."""

from __future__ import annotations

import os
import sys
from typing import Final

import requests

_DEFAULT_HOST: Final = "http://localhost:11434"


def ollama_base_url() -> str:
    return os.environ.get("KENAL_OLLAMA_HOST", _DEFAULT_HOST).rstrip("/")


def is_ollama_reachable(timeout: float = 3.0) -> bool:
    """Return True if the Ollama HTTP API responds at ``/api/tags``."""
    url = f"{ollama_base_url()}/api/tags"
    try:
        r = requests.get(url, timeout=timeout)
        return r.ok
    except requests.RequestException:
        return False


def should_skip_llm_example() -> bool:
    """Return True if this run should skip LLM work (caller prints and exits 0)."""
    if os.environ.get("KENAL_SKIP_LLM", "").lower() in ("1", "true", "yes"):
        print()
        print("  KENAL_SKIP_LLM is set — skipping this LLM example.")
        print()
        return True
    if not is_ollama_reachable():
        print()
        print(f"  Ollama does not appear reachable at {ollama_base_url()!r}.")
        print("  Start Ollama or set KENAL_OLLAMA_HOST. To force failure instead of skip,")
        print("  set KENAL_REQUIRE_LLM=1.")
        print()
        if os.environ.get("KENAL_REQUIRE_LLM", "").lower() in ("1", "true", "yes"):
            sys.exit(1)
        return True
    return False


def banner(title: str) -> None:
    print()
    print(f"  --- {title} ---")
    print()
