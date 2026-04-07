"""Road — the piping system that streams data through blocks and plates."""

from __future__ import annotations

import logging

from kenal.block import Block
from kenal.exceptions import RoadError
from kenal.plate import Plate
from kenal.rules import Rule
from kenal.types import Payload, Result

logger = logging.getLogger(__name__)

Stop = Block | Plate


class Road:
    """Routes and streams data between blocks and plates.

    A Road is an ordered sequence of *stops*.  Data enters the first stop,
    and each stop's output feeds into the next.  When a stop is a
    :class:`Plate`, all blocks on that plate run in fan-out; the last
    block's output is forwarded down the road.

    Args:
        name: Unique identifier for this road.
        stops: Ordered sequence of blocks and/or plates.
    """

    def __init__(
        self,
        name: str,
        *,
        stops: list[Stop] | None = None,
    ) -> None:
        if not name:
            raise RoadError("Road name cannot be empty")
        self.name = name
        self._stops: list[Stop] = list(stops or [])

    def add_stop(self, stop: Stop) -> Road:
        """Append a stop to the road and return self for chaining."""
        self._stops.append(stop)
        return self

    @property
    def stops(self) -> list[Stop]:
        """All stops on this road in execution order."""
        return list(self._stops)

    def run(self, data: Payload, *, plate_rules: list[Rule] | None = None) -> list[Result]:
        """Stream *data* through every stop, collecting results.

        Each stop receives the output of the previous stop.  All
        intermediate and final results are returned.

        Raises:
            RoadError: If the road has no stops or encounters an invalid stop.
        """
        if not self._stops:
            raise RoadError(f"Road '{self.name}' has no stops")

        logger.info("road.run name=%s stops=%d", self.name, len(self._stops))
        results: list[Result] = []
        current: Payload = data

        for stop in self._stops:
            if isinstance(stop, Plate):
                plate_results = stop.run_all(current)
                results.extend(plate_results)
                if plate_results:
                    current = plate_results[-1].output
            elif isinstance(stop, Block):
                result = stop.run(current, plate_rules=plate_rules or [])
                results.append(result)
                current = result.output
            else:
                raise RoadError(f"Invalid stop type: {type(stop)}")

        return results

    def __repr__(self) -> str:
        labels = [s.name for s in self._stops]
        return f"Road(name={self.name!r}, stops={labels})"
