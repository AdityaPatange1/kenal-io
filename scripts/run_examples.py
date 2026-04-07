#!/usr/bin/env python3
"""Run all numbered examples under examples/ sequentially with colored banners."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import console as C  # noqa: E402


def discover_examples() -> list[Path]:
    ex_dir = ROOT / "examples"
    paths = sorted(ex_dir.glob("[0-9][0-9]_*.py"))
    return paths


def run_one(path: Path, index: int, total: int) -> int:
    label = f"[{index}/{total}] {path.name}"
    C.section(f"Example {label}")
    C.banner(f"Running {path.relative_to(ROOT)}")
    sys.stdout.flush()

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    env["PYTHONUNBUFFERED"] = "1"

    proc = subprocess.Popen(
        [sys.executable, str(path)],
        cwd=ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert proc.stdout is not None
    prefix = C.dim("  │ ")
    for line in proc.stdout:
        print(prefix + line.rstrip())
    proc.wait()
    code = proc.returncode or 0
    print()
    if code == 0:
        C.success_banner(f"Finished {path.name}")
    else:
        C.failure_banner(f"Failed {path.name} (exit {code})")
    C.rule()
    return code


def main() -> int:
    examples = discover_examples()
    if not examples:
        C.failure_banner(f"No examples found under {ROOT / 'examples'}")
        return 1

    C.section("kenal-io — examples suite")
    C.log_line("●", f"Project root: {ROOT}", color=C.C.BRIGHT_BLUE)
    C.log_line("●", f"Python: {sys.executable}", color=C.C.BRIGHT_BLUE)
    C.log_line("●", f"Examples: {len(examples)}", color=C.C.BRIGHT_BLUE)
    print()
    sys.stdout.flush()

    failed: list[str] = []
    for i, path in enumerate(examples, start=1):
        code = run_one(path, i, len(examples))
        if code != 0:
            failed.append(path.name)

    C.section("Summary")
    if not failed:
        C.success_banner(f"All {len(examples)} example(s) completed successfully.")
        return 0

    C.failure_banner(f"{len(failed)} example(s) failed: {', '.join(failed)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
