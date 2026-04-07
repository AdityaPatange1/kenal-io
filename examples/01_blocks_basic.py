"""Example: blocks with pure-Python processors and Result objects."""

from __future__ import annotations

from kenal import Block


def main() -> None:
    print()
    print("  Blocks apply a callable or the default LLM path; here we use callables.")
    print()

    echo = Block(name="echo", process=lambda x: x)
    upper = Block(name="upper", process=lambda x: x.upper() if isinstance(x, str) else x)

    payload = "kenal-io"
    r1 = echo.run(payload)
    r2 = upper.run(payload)

    print(f"  echo:  {r1.output!r}  (from {r1.source_block})")
    print(f"  upper: {r2.output!r}  (from {r2.source_block})")
    print()


if __name__ == "__main__":
    main()
