"""Command-line interface for kenal."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from kenal._version import __version__


def main() -> int:
    parser = argparse.ArgumentParser(prog="kenal", description="kenal-io agent framework")
    parser.add_argument("--version", action="version", version=f"kenal {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="Run a kenal frame from a JSON config")
    run_parser.add_argument("config", help="Path to a kenal JSON config file")
    run_parser.add_argument("input", help="Input data to process")

    subparsers.add_parser("info", help="Show kenal framework info")

    args = parser.parse_args()

    if args.command == "info":
        _print_info()
        return 0

    if args.command == "run":
        return _run_config(args.config, args.input)

    parser.print_help()
    return 0


def _print_info() -> None:
    print(f"kenal {__version__}")
    print("A simple agent framework with Plates, Roads, Blocks, and Frames.")
    print()
    print("Components:")
    print("  Block  — individual processing unit")
    print("  Plate  — execution plane grouping blocks with shared rules")
    print("  Road   — pipe that streams data through stops")
    print("  Frame  — top-level orchestration engine")


def _run_config(config_path: str, input_data: str) -> int:
    from kenal.block import Block
    from kenal.frame import Frame
    from kenal.plate import Plate
    from kenal.road import Road

    try:
        with open(config_path) as fh:
            config: dict[str, Any] = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Error loading config: {exc}", file=sys.stderr)
        return 1

    blocks_map: dict[str, Block] = {}
    plates_map: dict[str, Plate] = {}

    for block_cfg in config.get("blocks", []):
        blk = Block(name=block_cfg["name"], rules=block_cfg.get("rules"))
        blocks_map[blk.name] = blk

    for plate_cfg in config.get("plates", []):
        plate_blocks = [blocks_map[bn] for bn in plate_cfg.get("blocks", []) if bn in blocks_map]
        plate = Plate(
            name=plate_cfg["name"],
            blocks=plate_blocks,
            rules=plate_cfg.get("rules"),
        )
        plates_map[plate.name] = plate

    roads: list[Road] = []
    for road_cfg in config.get("roads", []):
        stops: list[Block | Plate] = []
        for stop_name in road_cfg.get("stops", []):
            if stop_name in blocks_map:
                stops.append(blocks_map[stop_name])
            elif stop_name in plates_map:
                stops.append(plates_map[stop_name])
        roads.append(Road(name=road_cfg["name"], stops=stops))

    standalone = [
        b
        for name, b in blocks_map.items()
        if not any(name in p.block_names for p in plates_map.values())
    ]

    frame_cfg: dict[str, Any] = config.get("frame", {})
    frame = Frame(
        name=frame_cfg.get("name", "cli"),
        plates=list(plates_map.values()),
        blocks=standalone,
        roads=roads,
        rules=frame_cfg.get("rules"),
    )

    results = frame.run(input_data)
    for result in results:
        source = result.source_block
        if result.source_plate:
            source = f"{result.source_plate}/{result.source_block}"
        print(f"[{source}] {result.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
