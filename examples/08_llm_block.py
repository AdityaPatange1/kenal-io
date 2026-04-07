"""Example: Block without ``process=`` — uses the Ollama-backed engine and rules."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from llm_support import banner, should_skip_llm_example  # noqa: E402

from kenal import Block  # noqa: E402


def main() -> None:
    if should_skip_llm_example():
        return

    banner("LLM Block (rules + natural-language input)")

    block = Block(
        name="responder",
        rules=[
            "Reply with a single word only, no punctuation.",
            "The word must be the color blue in English.",
        ],
    )

    result = block.run("What color is the sky on a clear day? One word.")
    out = result.output
    out_stripped = (
        out.strip().lower() if isinstance(out, str) else str(out).strip().lower()
    )

    print(f"  Block: {result.source_block!r}")
    print(f"  Output: {result.output!r}")
    print()

    if "blue" in out_stripped:
        print("  Check: response mentions 'blue' — OK.")
    else:
        print("  Warning: expected something containing 'blue'; model output may vary.")
    print()


if __name__ == "__main__":
    main()
