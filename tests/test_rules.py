"""Tests for kenal.rules."""

from __future__ import annotations

import pytest

from kenal.rules import Rule, compile_rules, normalize_rules


class TestRule:
    def test_str_enforced(self) -> None:
        r = Rule(text="Be polite", enforce=True)
        assert str(r) == "[MUST] Be polite"

    def test_str_advisory(self) -> None:
        r = Rule(text="Be concise", enforce=False)
        assert str(r) == "[SHOULD] Be concise"

    def test_immutability(self) -> None:
        r = Rule(text="test")
        with pytest.raises(AttributeError):
            r.text = "other"  # type: ignore[misc]


class TestNormalizeRules:
    def test_none_input(self) -> None:
        assert normalize_rules(None) == []

    def test_empty_list(self) -> None:
        assert normalize_rules([]) == []

    def test_strings_converted(self) -> None:
        result = normalize_rules(["rule1", "rule2"])
        assert len(result) == 2
        assert all(isinstance(r, Rule) for r in result)
        assert result[0].text == "rule1"
        assert result[0].enforce is True

    def test_mixed_input(self) -> None:
        advisory = Rule(text="advisory", enforce=False)
        result = normalize_rules(["strict", advisory])
        assert result[0].enforce is True
        assert result[1].enforce is False


class TestCompileRules:
    def test_empty(self) -> None:
        assert compile_rules([]) == ""

    def test_single_rule(self) -> None:
        compiled = compile_rules([Rule(text="Be helpful")])
        assert "Be helpful" in compiled
        assert "1." in compiled

    def test_multiple_rules(self) -> None:
        rules = [Rule(text="First"), Rule(text="Second", enforce=False)]
        compiled = compile_rules(rules)
        assert "1." in compiled
        assert "2." in compiled
        assert "[MUST] First" in compiled
        assert "[SHOULD] Second" in compiled
