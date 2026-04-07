"""Example: plates group blocks; run_all fans out the same input."""

from __future__ import annotations

from kenal import Block, Plate


def main() -> None:
    print()

    double = Block(name="double", process=lambda x: f"{x}{x}" if isinstance(x, str) else x)
    upper = Block(
        name="upper",
        process=lambda x: x.upper() if isinstance(x, str) else x,
    )

    plate = Plate(
        name="text_ops",
        blocks=[double, upper],
        rules=["Keep outputs on one line where possible."],
    )

    data = "hi-"
    results = plate.run_all(data)
    print(f"  Input: {data!r}")
    print("  Plate fan-out (same input to each block):")
    for r in results:
        label = f"{r.source_plate}/{r.source_block}"
        print(f"    [{label}] -> {r.output!r}")
    print()


if __name__ == "__main__":
    main()
