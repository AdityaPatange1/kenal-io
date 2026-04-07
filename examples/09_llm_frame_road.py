"""Example: Frame + Road with multiple LLM blocks (sequential pipeline)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from llm_support import banner, should_skip_llm_example  # noqa: E402

from kenal import Block, Frame, Road  # noqa: E402


def main() -> None:
    if should_skip_llm_example():
        return

    banner("Frame with a Road of two LLM blocks")

    first = Block(
        name="expand",
        rules=["Output exactly one short sentence, nothing else."],
    )
    second = Block(
        name="count",
        rules=[
            "Count how many words are in the user's message.",
            "Reply with only an integer (digits only).",
        ],
    )

    road = Road(name="llm_chain", stops=[first, second])
    frame = Frame(name="llm_demo", roads=[road], rules=["Be concise."])

    seed = "The quick brown fox."
    results = frame.run(seed)

    print(f"  Input: {seed!r}")
    for r in results:
        print(f"  [{r.source_block}] -> {r.output!r}")
    print()


if __name__ == "__main__":
    main()
