"""Example: invoke the ``kenal`` CLI for ``info`` / ``--version`` (no LLM required)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    exe = shutil.which("kenal")
    if exe:
        cmd_base = [exe]
    else:
        cmd_base = [sys.executable, "-m", "kenal.cli"]

    env = {**__import__("os").environ, "PYTHONPATH": str(root / "src")}

    print()
    for args in (["--version"], ["info"]):
        cmd = cmd_base + args
        print(f"  $ {' '.join(cmd)}")
        proc = subprocess.run(
            cmd,
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
        )
        if proc.stdout:
            for line in proc.stdout.splitlines():
                print(f"    {line}")
        if proc.stderr:
            for line in proc.stderr.splitlines():
                print(f"    (stderr) {line}")
        if proc.returncode != 0:
            print(f"    exit {proc.returncode}")
    print()


if __name__ == "__main__":
    main()
