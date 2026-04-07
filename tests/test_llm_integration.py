"""Optional live Ollama tests — run only when enabled and a server is reachable."""

from __future__ import annotations

import os

import pytest
import requests

from kenal import Block, Frame, Road
from kenal.engine import generate


def _ollama_tags_url() -> str:
    base = os.environ.get("KENAL_OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    return f"{base}/api/tags"


def ollama_is_live() -> bool:
    try:
        r = requests.get(_ollama_tags_url(), timeout=3)
        return r.ok
    except requests.RequestException:
        return False


def _integration_enabled() -> bool:
    return os.environ.get("KENAL_RUN_LLM_INTEGRATION", "").lower() in (
        "1",
        "true",
        "yes",
    )


pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def require_live_ollama() -> None:
    if not _integration_enabled():
        pytest.skip("Set KENAL_RUN_LLM_INTEGRATION=1 to run live Ollama integration tests.")
    if not ollama_is_live():
        pytest.skip(f"Ollama not reachable at {_ollama_tags_url()}")


def test_live_generate_smoke(require_live_ollama: None) -> None:
    out = generate(
        system="Reply with the single word PONG and nothing else.",
        prompt="ping",
    )
    assert isinstance(out, str)
    assert len(out.strip()) > 0
    assert "PONG" in out.upper()


def test_live_block_without_process(require_live_ollama: None) -> None:
    block = Block(
        name="live",
        rules=["Reply with exactly one word: PARIS"],
    )
    result = block.run("Capital of France?")
    text = str(result.output).lower()
    assert "paris" in text


def test_live_frame_road(require_live_ollama: None) -> None:
    a = Block(name="a", rules=["Reply with only: ALPHA"])
    b = Block(name="b", rules=["Reply with only: BRAVO"])
    road = Road(name="r", stops=[a, b])
    frame = Frame(name="f", roads=[road])
    results = frame.run("seed")
    assert len(results) == 2
    for r in results:
        assert len(str(r.output).strip()) > 0
