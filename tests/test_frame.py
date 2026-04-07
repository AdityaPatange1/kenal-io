"""Tests for kenal.frame."""

from __future__ import annotations

import pytest

from kenal.block import Block
from kenal.exceptions import FrameError
from kenal.frame import Frame
from kenal.plate import Plate
from kenal.road import Road


class TestFrameInit:
    def test_defaults(self) -> None:
        f = Frame()
        assert f.name == "default"
        assert f.plates == []
        assert f.blocks == []
        assert f.roads == []

    def test_custom_name(self) -> None:
        f = Frame(name="my-frame")
        assert f.name == "my-frame"

    def test_components_registered(self, echo_block: Block, upper_block: Block) -> None:
        plate = Plate(name="p", blocks=[echo_block])
        road = Road(name="r", stops=[upper_block])
        standalone = Block(name="standalone", process=lambda d: d)
        f = Frame(plates=[plate], blocks=[standalone], roads=[road])
        assert len(f.plates) == 1
        assert len(f.blocks) == 1
        assert len(f.roads) == 1


class TestFrameDuplicates:
    def test_duplicate_plate(self) -> None:
        p1 = Plate(name="dup")
        p2 = Plate(name="dup")
        with pytest.raises(FrameError, match="Duplicate plate"):
            Frame(plates=[p1, p2])

    def test_duplicate_block(self) -> None:
        b1 = Block(name="dup", process=lambda d: d)
        b2 = Block(name="dup", process=lambda d: d)
        with pytest.raises(FrameError, match="Duplicate block"):
            Frame(blocks=[b1, b2])

    def test_duplicate_road(self, echo_block: Block) -> None:
        r1 = Road(name="dup", stops=[echo_block])
        r2 = Road(name="dup", stops=[echo_block])
        with pytest.raises(FrameError, match="Duplicate road"):
            Frame(roads=[r1, r2])


class TestFrameLookups:
    def test_get_plate(self) -> None:
        p = Plate(name="p1")
        f = Frame(plates=[p])
        assert f.get_plate("p1") is p

    def test_get_plate_missing(self) -> None:
        f = Frame()
        with pytest.raises(FrameError, match="not found"):
            f.get_plate("nope")

    def test_get_block(self, echo_block: Block) -> None:
        f = Frame(blocks=[echo_block])
        assert f.get_block("echo") is echo_block

    def test_get_road(self, echo_block: Block) -> None:
        r = Road(name="r1", stops=[echo_block])
        f = Frame(roads=[r])
        assert f.get_road("r1") is r


class TestFrameRun:
    def test_empty_frame_raises(self) -> None:
        f = Frame()
        with pytest.raises(FrameError, match="no results"):
            f.run("data")

    def test_standalone_blocks(self, echo_block: Block, upper_block: Block) -> None:
        f = Frame(blocks=[echo_block, upper_block])
        results = f.run("hello")
        assert len(results) == 2
        outputs = [r.output for r in results]
        assert "hello" in outputs
        assert "HELLO" in outputs

    def test_plates_without_roads(self, echo_block: Block, upper_block: Block) -> None:
        plate = Plate(name="p1", blocks=[echo_block, upper_block])
        f = Frame(plates=[plate])
        results = f.run("hello")
        assert len(results) == 2

    def test_roads_take_precedence(self) -> None:
        add_x = Block(name="add_x", process=lambda d: f"{d}X")
        standalone = Block(name="standalone", process=lambda d: f"{d}Y")
        road = Road(name="main", stops=[add_x])
        f = Frame(blocks=[standalone], roads=[road])
        results = f.run("start-")
        assert len(results) == 1
        assert results[0].output == "start-X"

    def test_run_road_by_name(self) -> None:
        add_a = Block(name="a", process=lambda d: f"{d}A")
        add_b = Block(name="b", process=lambda d: f"{d}B")
        r1 = Road(name="first", stops=[add_a])
        r2 = Road(name="second", stops=[add_b])
        f = Frame(roads=[r1, r2])
        results = f.run_road("second", "start-")
        assert len(results) == 1
        assert results[0].output == "start-B"

    def test_full_pipeline(self) -> None:
        upper = Block(name="upper", process=lambda d: d.upper() if isinstance(d, str) else d)
        exclaim = Block(name="exclaim", process=lambda d: f"{d}!" if isinstance(d, str) else d)
        plate = Plate(
            name="transform",
            blocks=[upper],
            rules=["Always be enthusiastic"],
        )
        road = Road(name="pipeline", stops=[plate, exclaim])
        f = Frame(name="demo", roads=[road])
        results = f.run("hello world")
        assert results[-1].output == "HELLO WORLD!"


class TestFrameRepr:
    def test_repr(self) -> None:
        f = Frame(name="test")
        assert "test" in repr(f)
