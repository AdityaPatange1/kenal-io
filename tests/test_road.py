"""Tests for kenal.road."""

from __future__ import annotations

import pytest

from kenal.block import Block
from kenal.exceptions import RoadError
from kenal.plate import Plate
from kenal.road import Road


class TestRoadInit:
    def test_empty_name_raises(self) -> None:
        with pytest.raises(RoadError, match="cannot be empty"):
            Road(name="")

    def test_basic_creation(self) -> None:
        r = Road(name="test")
        assert r.name == "test"
        assert r.stops == []


class TestRoadAddStop:
    def test_chaining(self, echo_block: Block, upper_block: Block) -> None:
        r = Road(name="pipe").add_stop(echo_block).add_stop(upper_block)
        assert len(r.stops) == 2


class TestRoadRun:
    def test_no_stops_raises(self) -> None:
        r = Road(name="empty")
        with pytest.raises(RoadError, match="no stops"):
            r.run("data")

    def test_sequential_blocks(self, upper_block: Block, exclaim_block: Block) -> None:
        r = Road(name="pipe", stops=[upper_block, exclaim_block])
        results = r.run("hello")
        assert len(results) == 2
        assert results[0].output == "HELLO"
        assert results[1].output == "HELLO!"

    def test_plate_as_stop(self, echo_block: Block, upper_block: Block) -> None:
        plate = Plate(name="p", blocks=[echo_block, upper_block])
        r = Road(name="pipe", stops=[plate])
        results = r.run("hello")
        assert len(results) == 2

    def test_mixed_stops(self, reverse_block: Block, echo_block: Block, upper_block: Block) -> None:
        plate = Plate(name="p", blocks=[echo_block, upper_block])
        r = Road(name="pipe", stops=[reverse_block, plate])
        results = r.run("hello")
        assert results[0].output == "olleh"
        assert results[1].output == "olleh"
        assert results[2].output == "OLLEH"

    def test_data_flows_through(self) -> None:
        add_a = Block(name="add_a", process=lambda d: f"{d}A")
        add_b = Block(name="add_b", process=lambda d: f"{d}B")
        add_c = Block(name="add_c", process=lambda d: f"{d}C")
        r = Road(name="chain", stops=[add_a, add_b, add_c])
        results = r.run("start-")
        assert results[-1].output == "start-ABC"


class TestRoadRepr:
    def test_repr(self, echo_block: Block) -> None:
        r = Road(name="test", stops=[echo_block])
        assert "test" in repr(r)
        assert "echo" in repr(r)
