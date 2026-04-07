"""Example: load examples/config/pipeline.json and bind Block callables in code.

The CLI ``kenal run`` builds blocks without custom ``process`` functions (LLM path).
This example shows the same *shape* of config with explicit Python implementations.
"""

from __future__ import annotations

import json
from pathlib import Path

from kenal import Block, Frame, Road


def main() -> None:
    root = Path(__file__).resolve().parent
    path = root / "config" / "pipeline.json"
    print()
    print(f"  Config: {path.relative_to(root.parent)}")
    with path.open() as fh:
        cfg = json.load(fh)

    impl = {
        "rev": lambda x: x[::-1] if isinstance(x, str) else x,
        "tag": lambda x: f"<out>{x}</out>" if isinstance(x, str) else x,
    }

    blocks: dict[str, Block] = {}
    for b in cfg.get("blocks", []):
        name = b["name"]
        blocks[name] = Block(name=name, rules=b.get("rules"), process=impl[name])

    roads: list[Road] = []
    for r in cfg.get("roads", []):
        stops = [blocks[s] for s in r["stops"]]
        roads.append(Road(name=r["name"], stops=stops))

    frame_cfg = cfg.get("frame", {})
    frame = Frame(
        name=frame_cfg.get("name", "cfg"),
        roads=roads,
        rules=frame_cfg.get("rules"),
    )

    out = frame.run("kenal")
    print("  Wired roads:", [rd.name for rd in frame.roads])
    for r in out:
        print(f"    [{r.source_block}] -> {r.output!r}")
    print()


if __name__ == "__main__":
    main()
