"""Unit tests for kenal.engine (mocked Ollama client)."""

from __future__ import annotations

import pytest

from kenal.exceptions import EngineError


def test_generate_returns_message_content(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeMsg:
        content = "assistant reply"

    class FakeResponse:
        message = FakeMsg()

    class FakeClient:
        def __init__(self, host: str = "") -> None:
            self.host = host

        def chat(self, **_kwargs: object) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr("kenal.engine._ollama.Client", FakeClient)
    monkeypatch.setenv("KENAL_MODEL", "fixed-model")

    from kenal.engine import generate

    out = generate("system text", "user text")
    assert out == "assistant reply"


def test_generate_empty_content_becomes_empty_string(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeMsg:
        content = None

    class FakeResponse:
        message = FakeMsg()

    class FakeClient:
        def __init__(self, host: str = "") -> None:
            pass

        def chat(self, **_kwargs: object) -> FakeResponse:
            return FakeResponse()

    monkeypatch.setattr("kenal.engine._ollama.Client", FakeClient)
    monkeypatch.setenv("KENAL_MODEL", "m")

    from kenal.engine import generate

    assert generate("s", "u") == ""


def test_generate_raises_engine_error_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeClient:
        def __init__(self, host: str = "") -> None:
            pass

        def chat(self, **_kwargs: object) -> None:
            raise RuntimeError("network down")

    monkeypatch.setattr("kenal.engine._ollama.Client", FakeClient)
    monkeypatch.setenv("KENAL_MODEL", "m")

    from kenal.engine import generate

    with pytest.raises(EngineError, match="LLM generation failed"):
        generate("s", "u")


def test_resolve_model_prefers_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KENAL_MODEL", "my-model")

    # Ensure client.list is not consulted when env is set — generate uses _resolve_model internally
    class BoomClient:
        def __init__(self, host: str = "") -> None:
            pass

        def list(self) -> None:
            raise AssertionError("list should not be called when KENAL_MODEL is set")

        def chat(self, **_kwargs: object) -> object:
            class Msg:
                content = "ok"

            class Resp:
                message = Msg()

            return Resp()

    monkeypatch.setattr("kenal.engine._ollama.Client", BoomClient)

    from kenal.engine import generate

    assert generate("s", "u") == "ok"
