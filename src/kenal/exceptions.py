"""Exception hierarchy for kenal."""

from __future__ import annotations


class KenalError(Exception):
    """Base exception for all kenal errors."""


class BlockError(KenalError):
    """Raised when a block fails during execution."""


class PlateError(KenalError):
    """Raised when a plate encounters an error."""


class RoadError(KenalError):
    """Raised when routing or piping fails."""


class FrameError(KenalError):
    """Raised when the frame orchestrator encounters an error."""


class EngineError(KenalError):
    """Raised when the LLM engine fails."""


class RuleError(KenalError):
    """Raised when rule validation or compilation fails."""
