"""Tests for kenal.plate."""

from __future__ import annotations

import pytest

from kenal.block import Block
from kenal.exceptions import PlateError
from kenal.plate import Plate


class TestPlateInit:
    def test_empty_name_raises(self) -> None:
        with pytest.raises(PlateError, match="cannot be empty"):
            Plate(name="")

    def test_basic_creation(self) -> None:
        p = Plate(name="test")
        assert p.name == "test"
        assert p.blocks == []
        assert p.rules == []

    def test_creation_with_blocks(self, echo_block: Block, upper_block: Block) -> None:
        p = Plate(name="test", blocks=[echo_block, upper_block])
        assert len(p.blocks) == 2
        assert p.block_names == ["echo", "upper"]


class TestPlateAddBlock:
    def test_add_block(self, echo_block: Block) -> None:
        p = Plate(name="test")
        p.add_block(echo_block)
        assert "echo" in p.block_names

    def test_duplicate_raises(self, echo_block: Block) -> None:
        p = Plate(name="test", blocks=[echo_block])
        dup = Block(name="echo", process=lambda d: d)
        with pytest.raises(PlateError, match="Duplicate"):
            p.add_block(dup)


class TestPlateGetBlock:
    def test_found(self, echo_block: Block) -> None:
        p = Plate(name="test", blocks=[echo_block])
        assert p.get_block("echo") is echo_block

    def test_not_found(self) -> None:
        p = Plate(name="test")
        with pytest.raises(PlateError, match="not found"):
            p.get_block("missing")


class TestPlateRunBlock:
    def test_run_single(self, upper_block: Block) -> None:
        p = Plate(name="test", blocks=[upper_block])
        result = p.run_block("upper", "hello")
        assert result.output == "HELLO"
        assert result.source_block == "upper"
        assert result.source_plate == "test"


class TestPlateRunAll:
    def test_fan_out(self, echo_block: Block, upper_block: Block) -> None:
        p = Plate(name="test", blocks=[echo_block, upper_block])
        results = p.run_all("hello")
        assert len(results) == 2
        outputs = [r.output for r in results]
        assert "hello" in outputs
        assert "HELLO" in outputs

    def test_empty_plate(self) -> None:
        p = Plate(name="empty")
        assert p.run_all("data") == []

    def test_plate_rules_inherited(self) -> None:
        received_rules: list[object] = []

        class SpyBlock(Block):
            def run(self, data: object, *, plate_rules: list[object] | None = None) -> object:  # type: ignore[override]
                received_rules.extend(plate_rules or [])
                return super().run(data, plate_rules=plate_rules)  # type: ignore[arg-type]

        spy = SpyBlock(name="spy", process=lambda d: d)
        p = Plate(name="ruled", blocks=[spy], rules=["be nice"])
        p.run_all("x")
        assert len(received_rules) == 1


class TestPlateRepr:
    def test_repr(self, echo_block: Block) -> None:
        p = Plate(name="test", blocks=[echo_block])
        assert "test" in repr(p)
        assert "echo" in repr(p)
