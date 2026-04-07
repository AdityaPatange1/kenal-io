"""kenal-io — A simple agent framework with Plates, Roads, Blocks, and Frames."""

from kenal._version import __version__
from kenal.block import Block
from kenal.exceptions import (
    BlockError,
    EngineError,
    FrameError,
    KenalError,
    PlateError,
    RoadError,
    RuleError,
)
from kenal.frame import Frame
from kenal.plate import Plate
from kenal.road import Road
from kenal.rules import Rule
from kenal.types import Payload, Result

__all__ = [
    "Block",
    "BlockError",
    "EngineError",
    "Frame",
    "FrameError",
    "KenalError",
    "Payload",
    "Plate",
    "PlateError",
    "Result",
    "Road",
    "RoadError",
    "Rule",
    "RuleError",
    "__version__",
]
