"""Frame — the top-level orchestration engine for kenal."""

from __future__ import annotations

import logging

from kenal.block import Block
from kenal.exceptions import FrameError
from kenal.plate import Plate
from kenal.road import Road
from kenal.rules import Rule, normalize_rules
from kenal.types import Payload, Result

logger = logging.getLogger(__name__)


class Frame:
    """Orchestrates plates, blocks, and roads into a runnable pipeline.

    A Frame is the entry-point for executing a kenal pipeline.  You can
    register components declaratively at construction time or imperatively
    via ``add_*`` helpers.

    Execution strategy:
        * **Roads present** — data is streamed through each road in
          registration order.
        * **No roads** — standalone blocks run first, then every plate
          fans out to its blocks.

    Args:
        name: Human-readable name for this frame.
        plates: Initial plates to register.
        blocks: Standalone blocks (not inside a plate).
        roads: Roads that wire blocks and plates together.
        rules: Frame-level rules inherited by all roads.
    """

    def __init__(
        self,
        name: str = "default",
        *,
        plates: list[Plate] | None = None,
        blocks: list[Block] | None = None,
        roads: list[Road] | None = None,
        rules: list[str | Rule] | None = None,
    ) -> None:
        self.name = name
        self.rules: list[Rule] = normalize_rules(rules)
        self._plates: dict[str, Plate] = {}
        self._blocks: dict[str, Block] = {}
        self._roads: dict[str, Road] = {}

        for plate in plates or []:
            self.add_plate(plate)
        for block in blocks or []:
            self.add_block(block)
        for road in roads or []:
            self.add_road(road)

    # -- registration --------------------------------------------------------

    def add_plate(self, plate: Plate) -> None:
        if plate.name in self._plates:
            raise FrameError(f"Duplicate plate name '{plate.name}'")
        self._plates[plate.name] = plate

    def add_block(self, block: Block) -> None:
        if block.name in self._blocks:
            raise FrameError(f"Duplicate block name '{block.name}'")
        self._blocks[block.name] = block

    def add_road(self, road: Road) -> None:
        if road.name in self._roads:
            raise FrameError(f"Duplicate road name '{road.name}'")
        self._roads[road.name] = road

    # -- lookups -------------------------------------------------------------

    def get_plate(self, name: str) -> Plate:
        try:
            return self._plates[name]
        except KeyError:
            raise FrameError(f"Plate '{name}' not found in frame '{self.name}'") from None

    def get_block(self, name: str) -> Block:
        try:
            return self._blocks[name]
        except KeyError:
            raise FrameError(f"Block '{name}' not found in frame '{self.name}'") from None

    def get_road(self, name: str) -> Road:
        try:
            return self._roads[name]
        except KeyError:
            raise FrameError(f"Road '{name}' not found in frame '{self.name}'") from None

    # -- properties ----------------------------------------------------------

    @property
    def plates(self) -> list[Plate]:
        return list(self._plates.values())

    @property
    def blocks(self) -> list[Block]:
        return list(self._blocks.values())

    @property
    def roads(self) -> list[Road]:
        return list(self._roads.values())

    # -- execution -----------------------------------------------------------

    def run(self, data: Payload) -> list[Result]:
        """Execute the full pipeline on *data*.

        Returns:
            Ordered list of :class:`Result` objects.

        Raises:
            FrameError: If no components are registered.
        """
        logger.info("frame.run name=%s", self.name)
        results: list[Result] = []

        if self._roads:
            for road in self._roads.values():
                road_results = road.run(data, plate_rules=self.rules)
                results.extend(road_results)
        else:
            for block in self._blocks.values():
                result = block.run(data, plate_rules=self.rules)
                results.append(result)
            for plate in self._plates.values():
                plate_results = plate.run_all(data)
                results.extend(plate_results)

        if not results:
            raise FrameError(
                f"Frame '{self.name}' produced no results. "
                "Add blocks, plates, or roads before running."
            )
        return results

    def run_road(self, road_name: str, data: Payload) -> list[Result]:
        """Run a single road by name."""
        road = self.get_road(road_name)
        return road.run(data, plate_rules=self.rules)

    def __repr__(self) -> str:
        return (
            f"Frame(name={self.name!r}, "
            f"plates={list(self._plates.keys())}, "
            f"blocks={list(self._blocks.keys())}, "
            f"roads={list(self._roads.keys())})"
        )
