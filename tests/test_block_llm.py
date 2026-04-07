"""Tests for Block LLM path (``generate`` mocked)."""

from __future__ import annotations

import pytest

from kenal import Block
from kenal.rules import Rule


def test_block_without_process_calls_generate(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[tuple[str, str]] = []

    def fake_generate(system: str, prompt: str, **_kwargs: object) -> str:
        calls.append((system, prompt))
        return "MODEL_OUT"

    monkeypatch.setattr("kenal.engine.generate", fake_generate)

    block = Block(
        name="llm",
        rules=[Rule(text="Speak like a pirate", enforce=True)],
    )
    result = block.run("user input")

    assert result.output == "MODEL_OUT"
    assert result.source_block == "llm"
    assert len(calls) == 1
    system, prompt = calls[0]
    assert prompt == "user input"
    assert "pirate" in system
    assert "rule" in system.lower() or "MUST" in system


def test_block_merges_plate_rules_in_llm_path(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, str] = {}

    def fake_generate(system: str, prompt: str, **_kwargs: object) -> str:
        captured["system"] = system
        return "x"

    monkeypatch.setattr("kenal.engine.generate", fake_generate)

    block = Block(name="b", rules=["Block-level rule"])
    plate_rules = [Rule(text="Plate rule", enforce=False)]
    block.run("data", plate_rules=plate_rules)

    assert "Plate rule" in captured["system"]
    assert "Block-level" in captured["system"]


def test_block_dict_payload_stringified_for_llm(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_generate(system: str, prompt: str, **_kwargs: object) -> str:
        assert system  # default assistant prompt or compiled rules
        assert "{'a': 1}" in prompt or "'a': 1" in prompt
        return "{}"

    monkeypatch.setattr("kenal.engine.generate", fake_generate)

    block = Block(name="dict_block")
    block.run({"a": 1})
