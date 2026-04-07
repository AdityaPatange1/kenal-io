"""Block — the fundamental processing unit in kenal."""

from __future__ import annotations

import logging
from collections.abc import Callable

from kenal.exceptions import BlockError
from kenal.rules import Rule, compile_rules, normalize_rules
from kenal.types import Payload, Result

logger = logging.getLogger(__name__)


class Block:
    """An individual processing component.

    A Block receives an input :pydata:`Payload`, applies its logic, and
    returns a :class:`Result`.  Processing is handled either by a caller-
    supplied function or, when none is given, by the built-in LLM engine
    guided by natural-language :class:`Rule` instances.

    Args:
        name: Unique identifier for this block.
        rules: Natural-language rules that govern processing behaviour.
        process: Optional pure-Python callable ``(Payload) -> Payload``.
            When provided the LLM engine is bypassed entirely.
    """

    def __init__(
        self,
        name: str,
        rules: list[str | Rule] | None = None,
        process: Callable[[Payload], Payload] | None = None,
    ) -> None:
        if not name:
            raise BlockError("Block name cannot be empty.")
        self.name = name
        self.rules: list[Rule] = normalize_rules(rules)
        self._process = process

    def run(self, data: Payload, *, plate_rules: list[Rule] | None = None) -> Result:
        """Execute this block on *data*.

        Args:
            data: The input payload.
            plate_rules: Additional rules inherited from the enclosing Plate.

        Returns:
            A :class:`Result` containing the processed output.

        Raises:
            BlockError: If processing fails for any reason.
        """
        logger.info("block.run name=%s", self.name)
        try:
            if self._process is not None:
                output = self._process(data)
            else:
                output = self._llm_process(data, plate_rules or [])
        except BlockError:
            raise
        except Exception as exc:
            raise BlockError(f"Block '{self.name}' failed: {exc}") from exc
        return Result(output=output, source_block=self.name)

    def _llm_process(self, data: Payload, extra_rules: list[Rule]) -> Payload:
        from kenal.engine import generate

        all_rules = extra_rules + self.rules
        system = compile_rules(all_rules) if all_rules else "You are a helpful assistant."
        prompt = data if isinstance(data, str) else str(data)
        return generate(system=system, prompt=prompt)

    def __repr__(self) -> str:
        return f"Block(name={self.name!r}, rules={len(self.rules)})"
