"""Example: call ``kenal.engine.generate`` directly (system + user messages)."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from llm_support import banner, should_skip_llm_example  # noqa: E402

from kenal.engine import generate  # noqa: E402


def main() -> None:
    if should_skip_llm_example():
        return

    banner("engine.generate (direct)")

    system = "You are a tiny test harness. Reply with the single word OK and nothing else."
    prompt = "Acknowledge."
    text = generate(system=system, prompt=prompt)

    print(f"  prompt: {prompt!r}")
    print(f"  reply:  {text!r}")
    print()
    if "ok" in text.strip().lower():
        print("  Check: reply contains OK — OK.")
    else:
        print("  Note: model did not return only OK; acceptable for smoke test.")
    print()


if __name__ == "__main__":
    main()
