"""Core type definitions for kenal."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

Payload = str | dict[str, Any]


@dataclass(frozen=True, slots=True)
class Result:
    """Immutable output produced by a Block execution."""

    output: Payload
    source_block: str
    source_plate: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
