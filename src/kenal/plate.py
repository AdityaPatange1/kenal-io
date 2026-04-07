"""Plate — the execution plane on which blocks operate."""

from __future__ import annotations

import logging

from kenal.block import Block
from kenal.exceptions import PlateError
from kenal.rules import Rule, normalize_rules
from kenal.types import Payload, Result

logger = logging.getLogger(__name__)


class Plate:
    """A logical execution plane that groups blocks under shared rules.

    Plates define *context*: every block that runs on a plate inherits the
    plate's rules in addition to its own.  This makes it easy to enforce
    cross-cutting concerns (language, tone, safety, etc.) across a group
    of blocks.

    Args:
        name: Unique identifier for this plate.
        blocks: Optional initial list of blocks to attach.
        rules: Plate-level rules applied to every block on the plate.
    """

    def __init__(
        self,
        name: str,
        *,
        blocks: list[Block] | None = None,
        rules: list[str | Rule] | None = None,
    ) -> None:
        if not name:
            raise PlateError("Plate name cannot be empty")
        self.name = name
        self.rules: list[Rule] = normalize_rules(rules)
        self._blocks: dict[str, Block] = {}
        for block in blocks or []:
            self.add_block(block)

    def add_block(self, block: Block) -> None:
        """Attach a block to this plate.

        Raises:
            PlateError: If a block with the same name already exists.
        """
        if block.name in self._blocks:
            raise PlateError(f"Duplicate block name '{block.name}' on plate '{self.name}'")
        self._blocks[block.name] = block

    def get_block(self, name: str) -> Block:
        """Retrieve a block by name.

        Raises:
            PlateError: If the block is not found.
        """
        try:
            return self._blocks[name]
        except KeyError:
            raise PlateError(f"Block '{name}' not found on plate '{self.name}'") from None

    @property
    def blocks(self) -> list[Block]:
        """All blocks attached to this plate."""
        return list(self._blocks.values())

    @property
    def block_names(self) -> list[str]:
        """Names of all blocks on this plate."""
        return list(self._blocks.keys())

    def run_block(self, block_name: str, data: Payload) -> Result:
        """Run a single block by name, injecting plate-level rules."""
        block = self.get_block(block_name)
        logger.info("plate.run_block plate=%s block=%s", self.name, block_name)
        result = block.run(data, plate_rules=self.rules)
        return Result(
            output=result.output,
            source_block=result.source_block,
            source_plate=self.name,
            metadata=result.metadata,
        )

    def run_all(self, data: Payload) -> list[Result]:
        """Fan-out: run every block on this plate with the same input."""
        results: list[Result] = []
        for block in self._blocks.values():
            result = block.run(data, plate_rules=self.rules)
            results.append(
                Result(
                    output=result.output,
                    source_block=result.source_block,
                    source_plate=self.name,
                    metadata=result.metadata,
                )
            )
        return results

    def __repr__(self) -> str:
        return f"Plate(name={self.name!r}, blocks={self.block_names})"
