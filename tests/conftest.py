"""Shared fixtures for kenal tests."""

from __future__ import annotations

import pytest

from kenal.block import Block
from kenal.rules import Rule


@pytest.fixture()
def echo_block() -> Block:
    return Block(name="echo", process=lambda data: data)


@pytest.fixture()
def upper_block() -> Block:
    return Block(name="upper", process=lambda data: data.upper() if isinstance(data, str) else data)


@pytest.fixture()
def reverse_block() -> Block:
    return Block(name="reverse", process=lambda data: data[::-1] if isinstance(data, str) else data)


@pytest.fixture()
def exclaim_block() -> Block:
    return Block(name="exclaim", process=lambda data: f"{data}!" if isinstance(data, str) else data)


@pytest.fixture()
def ruled_block() -> Block:
    return Block(
        name="ruled",
        rules=[
            Rule(text="Always respond in uppercase", enforce=True),
            Rule(text="Be concise", enforce=False),
        ],
        process=lambda data: data.upper() if isinstance(data, str) else data,
    )
