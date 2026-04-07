"""Tests for kenal.types."""

from __future__ import annotations

import pytest

from kenal.types import Result


class TestResult:
    def test_creation_with_defaults(self) -> None:
        r = Result(output="hello", source_block="b1")
        assert r.output == "hello"
        assert r.source_block == "b1"
        assert r.source_plate is None
        assert r.metadata == {}

    def test_creation_with_all_fields(self) -> None:
        r = Result(output={"key": "val"}, source_block="b1", source_plate="p1", metadata={"k": 1})
        assert r.output == {"key": "val"}
        assert r.source_plate == "p1"
        assert r.metadata == {"k": 1}

    def test_immutability(self) -> None:
        r = Result(output="x", source_block="b1")
        with pytest.raises(AttributeError):
            r.output = "y"  # type: ignore[misc]
