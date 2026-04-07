"""Tests for kenal.block."""

from __future__ import annotations

import pytest

from kenal.block import Block
from kenal.exceptions import BlockError
from kenal.rules import Rule


class TestBlockInit:
    def test_empty_name_raises(self) -> None:
        with pytest.raises(BlockError, match="cannot be empty"):
            Block(name="")

    def test_basic_creation(self) -> None:
        b = Block(name="test")
        assert b.name == "test"
        assert b.rules == []

    def test_rules_normalised(self) -> None:
        b = Block(name="test", rules=["rule1", Rule(text="rule2", enforce=False)])
        assert len(b.rules) == 2
        assert b.rules[0].text == "rule1"
        assert b.rules[1].enforce is False


class TestBlockRun:
    def test_custom_processor(self, echo_block: Block) -> None:
        result = echo_block.run("hello")
        assert result.output == "hello"
        assert result.source_block == "echo"

    def test_transform(self, upper_block: Block) -> None:
        result = upper_block.run("hello")
        assert result.output == "HELLO"

    def test_dict_payload(self) -> None:
        b = Block(name="passthrough", process=lambda d: d)
        result = b.run({"key": "value"})
        assert result.output == {"key": "value"}

    def test_processor_exception_wrapped(self) -> None:
        def bad_processor(data: object) -> object:
            raise ValueError("boom")

        b = Block(name="bad", process=bad_processor)
        with pytest.raises(BlockError, match="boom"):
            b.run("input")

    def test_plate_rules_passed(self) -> None:
        b = Block(name="spy", process=lambda data: data)
        plate_rules = [Rule(text="plate rule")]
        result = b.run("x", plate_rules=plate_rules)
        assert result.output == "x"


class TestBlockRepr:
    def test_repr(self) -> None:
        b = Block(name="test", rules=["r1", "r2"])
        assert "test" in repr(b)
        assert "2" in repr(b)
