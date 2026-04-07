"""Example: roads chain blocks; output feeds the next stop."""

from __future__ import annotations

from kenal import Block, Road


def main() -> None:
    print()

    add_prefix = Block(
        name="prefix",
        process=lambda x: f"[start]{x}" if isinstance(x, str) else x,
    )
    add_suffix = Block(
        name="suffix",
        process=lambda x: f"{x}[end]" if isinstance(x, str) else x,
    )

    road = Road(name="chain", stops=[add_prefix, add_suffix])
    out = road.run("payload")
    print("  Road stops:", [s.name for s in road.stops])
    print("  Results along the road:")
    for r in out:
        print(f"    [{r.source_block}] -> {r.output!r}")
    print(f"  Final: {out[-1].output!r}")
    print()


if __name__ == "__main__":
    main()
