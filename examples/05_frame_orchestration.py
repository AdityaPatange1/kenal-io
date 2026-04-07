"""Example: Frame wires roads and inherits frame-level rules."""

from __future__ import annotations

from kenal import Block, Frame, Plate, Road


def main() -> None:
    print()

    upper = Block(
        name="upper",
        process=lambda x: x.upper() if isinstance(x, str) else x,
    )
    exclaim = Block(
        name="exclaim",
        process=lambda x: f"{x}!" if isinstance(x, str) else x,
    )

    plate = Plate(name="transform", blocks=[upper], rules=["Be concise."])
    road = Road(name="main", stops=[plate, exclaim])

    frame = Frame(
        name="demo",
        roads=[road],
        rules=["Use plain ASCII in examples."],
    )

    results = frame.run("hello")
    print("  Frame:", frame.name)
    print("  Results:")
    for r in results:
        src = r.source_block
        if r.source_plate:
            src = f"{r.source_plate}/{r.source_block}"
        print(f"    [{src}] -> {r.output!r}")
    print()


if __name__ == "__main__":
    main()
